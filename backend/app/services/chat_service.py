from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.models.user import User
from app.schemas.chat import ChatSendRequest


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def send(self, user: User, payload: ChatSendRequest) -> tuple[Conversation, Message, Message]:
        conversation = self._resolve_conversation(user.id, payload)
        user_message = Message(conversation_id=conversation.id, role="user", text=payload.text)
        self.db.add(user_message)
        assistant_text = self._generate_reply(payload.text)
        assistant_message = Message(conversation_id=conversation.id, role="assistant", text=assistant_text)
        self.db.add(assistant_message)
        self.db.commit()
        self.db.refresh(conversation)
        self.db.refresh(user_message)
        self.db.refresh(assistant_message)
        return conversation, user_message, assistant_message

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

    def _generate_reply(self, prompt: str) -> str:
        normalized = prompt.lower()
        if "campanha" in normalized or "marketing" in normalized:
            return "Posso estruturar uma campanha com oferta, objeções e CTA. Abra Marketing Studio para gerar a versão completa."
        if "agente" in normalized:
            return "Seus agentes podem ser ativados por canal. Use a aba Agents para configurar função, linguagem e conexões."
        if "dashboard" in normalized or "métrica" in normalized:
            return "O dashboard resume mensagens, agentes e indicadores operacionais em tempo real a partir do banco."
        return "Entendi. Posso ajudar a transformar essa demanda em ação dentro da AXI com chat, agentes, marketing e métricas conectadas."