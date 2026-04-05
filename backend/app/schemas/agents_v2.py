from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentOverviewResponse(BaseModel):
    agent: dict[str, Any]
    kpis: dict[str, Any]
    canais_ativos: list[dict[str, Any]]
    historico_de_atividade: list[dict[str, Any]]
    setup: dict[str, Any]


class AgentSetupChecklistItem(BaseModel):
    key: str
    label: str
    completed: bool
    detail: str
    route: str
    helper_text: str | None = None


class AgentSetupRecommendedStep(BaseModel):
    key: str
    title: str
    description: str
    route: str
    cta: str


class AgentSetupStatusResponse(BaseModel):
    progress_percent: int
    completed_steps: int
    total_steps: int
    activation_ready: bool
    summary_message: str
    recommended_next_step: AgentSetupRecommendedStep
    checklist: list[AgentSetupChecklistItem]


class AgentReadinessResponse(BaseModel):
    activation_ready: bool
    status: str
    progress_percent: int
    validation_errors: list[str]


class AgentCreatedFlowResponse(BaseModel):
    agent: dict[str, Any]
    setup: AgentSetupStatusResponse


class AgentChannelConnectRequest(BaseModel):
    channel_type: str
    provider_name: str = "internal"
    channel_id: str
    external_account_id: str | None = None
    credential_ref: str | None = None
    enabled: bool = True
    test_mode: bool = True
    config: dict[str, Any] = Field(default_factory=dict)
    api_key: str | None = None


class AgentChannelStatusResponse(BaseModel):
    id: int
    channel_type: str
    channel_id: str
    status: str
    conexao_do_agente: str


class AgentKnowledgeSourceRequest(BaseModel):
    title: str
    kind: str = "note"
    content: str
    tags: str | None = None
    enabled: bool = True


class AgentKnowledgeSourceResponse(BaseModel):
    id: int
    materiais_e_informacoes_do_agente: str
    tipo: str
    status: str


class AgentActionRequest(BaseModel):
    name: str
    action_type: str
    trigger_keywords: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class AgentRunTestRequest(BaseModel):
    text: str
    scenario: str = "free"
    channel_type: str = "api"


class AgentRunTestResponse(BaseModel):
    test_id: int
    scenario: str
    response: str
    actions: list[dict[str, Any]]
    source: str
    confidence_note: str
    status: str


class AgentTestSessionMessageRead(BaseModel):
    id: int
    role: str
    content: str
    trace: dict[str, Any]
    created_at: datetime


class AgentTestSessionRead(BaseModel):
    id: int
    scenario: str
    status: str
    session_summary: str
    created_at: datetime


class AgentSettingsBasic(BaseModel):
    name: str
    role: str
    language: str
    tone: str | None = None
    working_hours: str | None = None
    active: bool
    fallback_to_human: bool


class AgentSettingsAdvanced(BaseModel):
    instrucoes_principais_do_agente: str | None = None
    modelo: str | None = None
    temperature: str | None = None
    opcoes_avancadas: dict[str, Any] = Field(default_factory=dict)


class AgentSettingsResponse(BaseModel):
    basic: AgentSettingsBasic
    advanced: AgentSettingsAdvanced


class AgentSettingsUpdateRequest(BaseModel):
    basic: AgentSettingsBasic
    advanced: AgentSettingsAdvanced


class AgentsImportConfigRequest(BaseModel):
    nome: str
    funcao: str
    tipo: str
    linguagem: str = "pt-BR"
    prompt: str
    tone: str | None = None
    objective: str | None = None
    channels: list[dict[str, Any]] = Field(default_factory=list)
    knowledge: list[dict[str, Any]] = Field(default_factory=list)
    actions: list[dict[str, Any]] = Field(default_factory=list)


class AgentsTemplateRead(BaseModel):
    id: str
    nome: str
    descricao: str
    funcao: str
    objetivos: list[str]
