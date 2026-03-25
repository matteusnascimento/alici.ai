from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.conversation import Conversation, Message
from app.models.usage_log import UsageLog
from app.models.user import User
from app.schemas.chat import ChatSendRequest
from app.services.openai_service import OpenAIService, OpenAIServiceError


# ---------------------------------------------------------------------------
# Mock provider – fallback used while real AI is not yet connected
# ---------------------------------------------------------------------------

class _MockProvider:
    """Keyword-based fallback provider. Returns canned responses."""

    def generate(self, prompt: str) -> str:
        normalized = prompt.lower()
        if "campanha" in normalized or "marketing" in normalized:
            return "Posso estruturar uma campanha com oferta, objeções e CTA. Abra Marketing Studio para gerar a versão completa."
        if "agente" in normalized:
            return "Seus agentes podem ser ativados por canal. Use a aba Agents para configurar função, linguagem e conexões."
        if "dashboard" in normalized or "métrica" in normalized:
            return "O dashboard resume mensagens, agentes e indicadores operacionais em tempo real a partir do banco."
        return "Entendi. Posso ajudar a transformar essa demanda em ação dentro da AXI com chat, agentes, marketing e métricas conectadas."


class _OpenAIProvider:
    """Provider real usando OpenAI Chat Completions."""

    def __init__(self) -> None:
        self._service = OpenAIService()

    def generate(self, prompt: str) -> str:
        response = self._service.send_chat_message(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é a assistente AXI da plataforma Alici. "
                        "Responda em pt-BR, com objetividade, clareza e foco em execução."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        content = response.get("content", "").strip()
        if not content:
            raise OpenAIServiceError("OpenAI returned empty content")
        return content


# ---------------------------------------------------------------------------
# Orchestrator – selects the active provider
# ---------------------------------------------------------------------------

class _ChatOrchestrator:
    """
    Routes chat requests to the appropriate AI provider.

    Uses OpenAI when configured and healthy, with automatic fallback
    to local mock provider for resilience.
    """

    def __init__(self) -> None:
        self._fallback_provider = _MockProvider()
        self._provider = _OpenAIProvider() if settings.openai_api_key else self._fallback_provider

    def reply(self, prompt: str) -> str:
        try:
            return self._provider.generate(prompt)
        except Exception:
            # Never fail chat generation hard because of provider outage.
            return self._fallback_provider.generate(prompt)


_orchestrator = _ChatOrchestrator()


# ---------------------------------------------------------------------------
# ChatService – handles persistence and delegates generation to orchestrator
# ---------------------------------------------------------------------------

class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def send(self, user: User, payload: ChatSendRequest) -> tuple[Conversation, Message, Message]:
        conversation = self._resolve_conversation(user.id, payload)
        user_message = Message(conversation_id=conversation.id, role="user", text=payload.text)
        self.db.add(user_message)
        assistant_text = _orchestrator.reply(payload.text)
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