from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.models.usage_log import UsageLog
from app.models.user import User
from app.schemas.chat import ChatSendRequest
from app.schemas.openai_responses import AIToolRegistry, ConversationMessage
from app.services.ai.model_router import get_model_for_task
from app.services.ai_service import AIService, AIServiceError
from app.services.openai_responses_service import OpenAIResponsesService, OpenAIResponsesError
from app.services.tool_executor import ToolExecutor


# ---------------------------------------------------------------------------
# ChatService – handles persistence and delegates generation to orchestrator
# ---------------------------------------------------------------------------

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIService()
        self.openai_responses = OpenAIResponsesService()
        self.tool_executor = ToolExecutor()

    @staticmethod
    def _fallback_response(reason: str | None = None) -> str:
        if reason == "rate_limit":
            return (
                "A IA atingiu o limite temporario de uso. Seu chat continua operacional em modo seguro. "
                "Tente novamente em instantes para receber resposta completa."
            )
        if reason == "ai_not_configured":
            return (
                "A integracao de IA ainda nao esta configurada por completo. "
                "Seu chat continua operacional em modo seguro enquanto a configuracao e concluida."
            )
        return (
            "A integracao de IA esta indisponivel no momento. "
            "Seu chat continua operacional em modo seguro enquanto a plataforma se recupera."
        )

    @staticmethod
    def _resolve_reason_from_status(status_code: int | None) -> str:
        if status_code == 429:
            return "rate_limit"
        if status_code == 401:
            return "ai_not_configured"
        return "ai_unavailable"

    @staticmethod
    def _resolve_task(agent_name: str | None) -> str:
        if not agent_name:
            return "chat"
        normalized = agent_name.strip().lower()
        if normalized == "support":
            return "chat_support"
        if normalized in {"sales", "operations"}:
            return "agent_runtime"
        return "chat"

    def _resolve_instructions(self, agent_name: str | None = None) -> str:
        base = (
            "Voce e a assistente AXI da plataforma Alici. "
            "Responda em pt-BR, com objetividade, clareza e foco em execucao."
        )
        if not agent_name:
            return base

        normalized = agent_name.strip().lower()
        specializations = {
            "sales": "Voce e especialista em vendas, proposta e conversao.",
            "support": "Voce e especialista em suporte ao cliente e resolucao de incidentes.",
            "operations": "Voce e especialista em operacoes, processos e metricas.",
        }
        return f"{base} {specializations.get(normalized, '')}".strip()

    @staticmethod
    def _build_tools_schema() -> list[dict]:
        return [tool.to_json_schema() for tool in AIToolRegistry.list_all_tools()]

    def send(self, user: User, payload: ChatSendRequest, use_responses_api: bool = True, agent_name: str | None = None) -> tuple[Conversation, Message, Message]:
        """
        Envia uma mensagem de chat.
        
        Args:
            user: Usuário que envia a mensagem
            payload: Dados da mensagem (text, conversation_id)
            use_responses_api: Se deve usar OpenAI Responses API (padrão True)
            agent_name: Nome do agente (para especialização)
        
        Returns:
            Tupla (conversa, mensagem_usuario, mensagem_assistente)
        """
        conversation = self._resolve_conversation(user.id, payload)
        user_message = Message(conversation_id=conversation.id, role="user", text=payload.text)
        self.db.add(user_message)

        selected_agent = payload.agent_name or agent_name
        selected_task = self._resolve_task(selected_agent)
        selected_model = get_model_for_task(selected_task)
        selected_instructions = self._resolve_instructions(selected_agent)
        should_use_responses_api = payload.use_responses_api if payload.use_responses_api is not None else use_responses_api

        # Tenta Responses API se disponível e habilitado
        assistant_text = None
        if should_use_responses_api and self.openai_responses.is_configured():
            try:
                # Constrói histórico da conversa
                history = self._build_conversation_history(conversation.id)

                # Gera resposta via Responses API
                response = self.openai_responses.generate_response(
                    user_message=payload.text,
                    instructions=selected_instructions,
                    conversation_history=history,
                    tools=self._build_tools_schema(),
                )
                
                assistant_text = response.output_text
                
                # Se houve tool calls, executa-as
                if response.tool_calls:
                    for tool_call in response.tool_calls:
                        tool_result = self.tool_executor.execute(tool_call.tool_name, tool_call.tool_args)
                        # Log de ferramenta executada (opcional)
                        self.db.add(
                            UsageLog(
                                user_id=user.id,
                                metric=f"tool_{tool_call.tool_name}",
                                quantity=1,
                                source="chat",
                            )
                        )
            except OpenAIResponsesError as exc:
                # Fall back para AIService em caso de erro
                if exc.status_code in (401, 429, 503, 504):
                    assistant_text = self._fallback_response(self._resolve_reason_from_status(exc.status_code))
                else:
                    raise AIServiceError(
                        str(exc),
                        user_message="Servico de IA temporariamente indisponivel.",
                        status_code=exc.status_code,
                    ) from exc

        # Fall back para AIService se necessário
        if assistant_text is None:
            if not self.ai.is_configured():
                assistant_text = self._fallback_response()
            else:
                try:
                    assistant_text = self.ai.generate_text(
                        system_prompt=selected_instructions,
                        user_prompt=payload.text,
                        temperature=0.3,
                        model=selected_model,
                        function_name=selected_task,
                    )
                except AIServiceError as exc:
                    if exc.is_retryable_platform_issue:
                        assistant_text = self._fallback_response(exc.code)
                    else:
                        raise
                except Exception as exc:
                    raise AIServiceError(
                        str(exc),
                        user_message="Servico de IA temporariamente indisponivel. Tente novamente.",
                        status_code=503,
                    ) from exc

        assistant_message = Message(conversation_id=conversation.id, role="assistant", text=assistant_text)
        self.db.add(assistant_message)
        self.db.add(UsageLog(user_id=user.id, metric="messages", quantity=2, source="chat"))
        self.db.commit()
        self.db.refresh(conversation)
        self.db.refresh(user_message)
        self.db.refresh(assistant_message)
        return conversation, user_message, assistant_message

    def history(self, user: User) -> list[dict]:
        conversations = self.list_conversations(user)
        return [
            {
                "conversation_id": item.id,
                "title": item.title,
                "created_at": item.created_at,
                "message_count": len(item.messages),
            }
            for item in conversations
        ]

    def list_conversations(self, user: User) -> list[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user.id)
            .order_by(Conversation.created_at.desc())
            .all()
        )

    def list_messages(self, user: User, conversation_id: int) -> list[Message]:
        conversation = (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user.id, Conversation.id == conversation_id)
            .first()
        )
        if not conversation:
            return []
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )

    def _resolve_conversation(self, user_id: int, payload: ChatSendRequest) -> Conversation:
        conversation = None
        if payload.conversation_id:
            conversation = (
                self.db.query(Conversation)
                .filter(Conversation.id == payload.conversation_id, Conversation.user_id == user_id)
                .first()
            )
        if conversation:
            return conversation
        title = payload.text.strip()[:60] or "Nova conversa"
        conversation = Conversation(user_id=user_id, title=title)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def _build_conversation_history(self, conversation_id: int) -> list[ConversationMessage]:
        """Constrói o histórico da conversa para context injection."""
        messages = (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )
        return [
            ConversationMessage(role=msg.role, content=msg.text)
            for msg in messages[-10:]  # Últimas 10 mensagens para evitar token bloat
        ]

    @staticmethod
    def _build_instructions(agent_name: str | None = None) -> str:
        """Compatibilidade com chamadas legadas."""
        base_instructions = (
            "Voce e a assistente AXI da plataforma Alici. "
            "Responda em pt-BR, com objetividade, clareza e foco em execucao."
        )

        if agent_name == "sales":
            return base_instructions + " Voce e especialista em vendas e propostas comerciais."
        if agent_name == "support":
            return base_instructions + " Voce e especialista em suporte ao cliente."
        if agent_name == "operations":
            return base_instructions + " Voce e especialista em operacoes e metricas."

        return base_instructions