from datetime import datetime

from pydantic import BaseModel


class IntegrationRead(BaseModel):
    id: int
    provider: str
    name: str
    is_active: bool
    created_at: datetime


class IntegrationTestRequest(BaseModel):
    api_key: str | None = None
    token: str | None = None
    endpoint: str | None = None


class IntegrationTestResponse(BaseModel):
    provider: str
    status: str
    message: str
    model: str | None = None
