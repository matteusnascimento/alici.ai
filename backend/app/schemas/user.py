from pydantic import BaseModel, EmailStr


class UserUpdateRequest(BaseModel):
    name: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class UserMeResponse(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    phone: str | None
    plan: str
