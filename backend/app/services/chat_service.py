from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.models.usage_log import UsageLog
from app.models.user import User
from app.schemas.chat import ChatSendRequest
from app.services.ai_service import AIService, AIServiceError


# ---------------------------------------------------------------------------
# ChatService – handles persistence and delegates generation to orchestrator
# ---------------------------------------------------------------------------

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIService()

    @staticmethod
    def _fallback_response() -> str:
        return (
            "A integracao de IA esta indisponivel no momento. "
            "Seu chat continua operacional em modo seguro enquanto a configuracao e concluida."
        )

    def send(self, user: User, payload: ChatSendRequest) -> tuple[Conversation, Message, Message]:
        conversation = self._resolve_conversation(user.id, payload)
        user_message = Message(conversation_id=conversation.id, role="user", text=payload.text)
        self.db.add(user_message)
        if not self.ai.is_configured():
            assistant_text = self._fallback_response()
        else:
            try:
                assistant_text = self.ai.generate_text(
                    system_prompt=(
                        "Voce e a assistente AXI da plataforma Alici. "
                        "Responda em pt-BR, com objetividade, clareza e foco em execucao."
                    ),
                    user_prompt=payload.text,
                    temperature=0.3,
                    function_name="chat",
                )
            except AIServiceError:
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