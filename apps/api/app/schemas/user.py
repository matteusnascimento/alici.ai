from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    organization_id: UUID
    email: EmailStr
    full_name: str
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    email: EmailStr
    full_name: str
    is_active: bool