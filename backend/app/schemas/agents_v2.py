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


class AgentKnowledgeManualRequest(BaseModel):
    title: str
    content: str
    tags: str | None = None
    enabled: bool = True


class AgentKnowledgeFaqRequest(BaseModel):
    question: str
    answer: str
    tags: str | None = None
    enabled: bool = True


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


# --- Connections / Integrations ---

class AgentConnectionRead(BaseModel):
    id: int
    agent_id: int
    channel_type: str
    provider_name: str
    status: str
    is_enabled: bool
    enabled: bool
    external_account_id: str | None
    webhook_url: str | None
    last_sync_at: datetime | None
    last_error: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj: Any) -> "AgentConnectionRead":
        return cls(
            id=obj.id,
            agent_id=obj.agent_id,
            channel_type=obj.channel_type,
            provider_name=obj.provider_name or "internal",
            status=obj.status or "disconnected",
            is_enabled=bool(obj.enabled),
            enabled=bool(obj.enabled),
            external_account_id=obj.external_account_id,
            webhook_url=obj.webhook_url,
            last_sync_at=obj.last_sync_at,
            last_error=obj.last_error,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )


class AgentConnectionConnectRequest(BaseModel):
    config: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class AgentConnectionUpdateRequest(BaseModel):
    config: dict[str, Any] | None = None
    enabled: bool | None = None
    webhook_url: str | None = None
    external_account_id: str | None = None


class AgentConnectionActionResponse(BaseModel):
    success: bool
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    channel_type: str


class AgentChannelIntegrationPayload(BaseModel):
    external_account_id: str | None = None
    external_account_name: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentChannelEndpointPayload(BaseModel):
    external_channel_id: str | None = None
    channel_name: str | None = None
    phone_number_or_handle: str | None = None


class AgentChannelBindingConnectRequest(BaseModel):
    provider: str
    integration: AgentChannelIntegrationPayload
    endpoint: AgentChannelEndpointPayload
    fallback_enabled: bool = False


class AgentChannelBindingDisconnectRequest(BaseModel):
    binding_id: int


class AgentChannelBindingTestRequest(BaseModel):
    binding_id: int
    message: str | None = None


class AgentChannelBindingRead(BaseModel):
    binding_id: int
    agent_id: int
    channel_endpoint_id: int
    provider: str
    status: str
    is_active: bool
    fallback_enabled: bool
    external_account_id: str | None
    external_account_name: str | None
    channel_name: str
    external_channel_id: str | None
    phone_number_or_handle: str | None
    webhook_status: str
    last_test_at: datetime | None
    last_test_status: str | None
    last_test_message: str | None
    created_at: datetime
    updated_at: datetime


class AgentChannelBindingActionResponse(BaseModel):
    success: bool
    message: str
    provider: str
    channel_binding_id: int
    data: dict[str, Any] = Field(default_factory=dict)
