from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AgentCreate(BaseModel):
    organization_id: UUID
    name: str
    system_prompt: str
    model: str
    tools: dict = {}


class AgentUpdate(BaseModel):
    name: str | None = None
    system_prompt: str | None = None
    model: str | None = None
    tools: dict | None = None


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    system_prompt: str
    model: str
    tools: dict