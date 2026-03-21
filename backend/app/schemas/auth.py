from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class RegisterRequest(BaseModel):
    name: str
    username: str
    email: EmailStr
    phone: str | None = None
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    username: str
    email: EmailStr
    phone: str | None
    plan: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
