from pydantic import BaseModel, ConfigDict, EmailStr


class ProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    username: str
    email: EmailStr
    phone: str | None
    plan: str


class ProfileUpdate(BaseModel):
    name: str
    username: str
    email: EmailStr
    phone: str | None = None
    plan: str


class SettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    background_conversation: bool
    autocomplete: bool
    trending: bool
    sequence: bool
    split_mode: bool
    language: str
    voice: str


class SettingsUpdate(BaseModel):
    background_conversation: bool
    autocomplete: bool
    trending: bool
    sequence: bool
    split_mode: bool
    language: str
    voice: str


class AccountResponse(BaseModel):
    profile: ProfileRead
    settings: SettingsRead
