from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatSendRequest(BaseModel):
    text: str
    conversation_id: int | None = None


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    role: str
    text: str
    created_at: datetime


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    created_at: datetime


class ChatSendResponse(BaseModel):
    conversation: ConversationRead
    user_message: MessageRead
    assistant_message: MessageRead
