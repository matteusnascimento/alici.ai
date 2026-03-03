"""Pydantic schemas used by the API."""

from typing import Optional

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    nome: str
    email: EmailStr
    senha: str


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ChatRequest(BaseModel):
    pergunta: str
    incluir_emocao: bool = False


class PredictRequest(BaseModel):
    imagem_base64: str


class ImageRequest(BaseModel):
    prompt: str


class AudioRequest(BaseModel):
    texto: str


class VideoRequest(BaseModel):
    prompt: str


class BillingCheckoutRequest(BaseModel):
    plano: str


class UpdateProfileRequest(BaseModel):
    nome: Optional[str] = None
    senha_atual: Optional[str] = None
    nova_senha: Optional[str] = None
    tema: Optional[str] = None


class CreateConversationRequest(BaseModel):
    titulo: Optional[str] = None


class ConversationChatRequest(BaseModel):
    content: str
    incluir_emocao: bool = False
