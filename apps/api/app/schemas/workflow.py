from uuid import UUID
from pydantic import BaseModel, ConfigDict


class WorkflowCreate(BaseModel):
    organization_id: UUID
    name: str
    graph: dict
    is_active: bool = True


class WorkflowUpdate(BaseModel):
    name: str | None = None
    graph: dict | None = None
    is_active: bool | None = None


class WorkflowResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    graph: dict
    is_active: bool