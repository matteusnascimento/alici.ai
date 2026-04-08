from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentCreate(BaseModel):
    nome: str
    funcao: str
    tipo: str
    linguagem: str = "pt-BR"
    prompt: str
    tone: str | None = None
    objectives: list[str] = Field(default_factory=list)
    whatsapp: str | None = None
    instagram: str | None = None
    api: str | None = None
    outros: str | None = None
    outros_nome: str | None = None
    ativo: bool = True
    preferred_model: str | None = None


class AgentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    nome: str
    funcao: str
    tipo: str
    linguagem: str
    prompt: str
    whatsapp: str | None
    instagram: str | None
    api: str | None
    outros: str | None
    outros_nome: str | None
    ativo: bool
    created_at: datetime
    preferred_model: str | None


class AgentToggleResponse(BaseModel):
    id: int
    ativo: bool
