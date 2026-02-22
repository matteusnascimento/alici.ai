"""Pydantic schemas used by the API."""

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    nome: str
    email: EmailStr
    senha: str


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


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
