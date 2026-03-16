from uuid import UUID
from pydantic import BaseModel, ConfigDict


class MessageCreate(BaseModel):
    conversation_id: UUID
    role: str
    content: str


class MessageUpdate(BaseModel):
    content: str | None = None


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: str
    content: str