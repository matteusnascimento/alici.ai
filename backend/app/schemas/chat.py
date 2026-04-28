from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatSendRequest(BaseModel):
    text: str
    conversation_id: int | None = None
    agent_name: str | None = None
    use_responses_api: bool | None = None


class ChatUploadResponse(BaseModel):
    filename: str
    size: int
    content_type: str | None = None
    file_url: str | None = None
    message: str


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
