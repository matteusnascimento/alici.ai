"""Pydantic schemas used by the API."""

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    nome: str = Field(min_length=2, max_length=120, validation_alias=AliasChoices("nome", "name"))
    email: EmailStr
    senha: str = Field(min_length=8, max_length=72, validation_alias=AliasChoices("senha", "password"))


class LoginRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: EmailStr
    senha: str = Field(min_length=1, max_length=72, validation_alias=AliasChoices("senha", "password"))


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=20, max_length=4096)


class ChatRequest(BaseModel):
    pergunta: str = Field(min_length=1, max_length=8_000)
    incluir_emocao: bool = False


class PredictRequest(BaseModel):
    imagem_base64: str = Field(min_length=1, max_length=15_000_000)


class ImageRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2_000)


class AudioRequest(BaseModel):
    texto: str = Field(min_length=1, max_length=5_000)


class VideoRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2_000)


class BillingCheckoutRequest(BaseModel):
    plano: str = Field(min_length=2, max_length=32)
