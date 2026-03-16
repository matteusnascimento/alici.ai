from uuid import UUID
from pydantic import BaseModel, ConfigDict


class KnowledgeCreate(BaseModel):
    organization_id: UUID
    title: str
    source: str
    content: str


class KnowledgeUpdate(BaseModel):
    title: str | None = None
    source: str | None = None
    content: str | None = None


class KnowledgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    title: str
    source: str
    content: str