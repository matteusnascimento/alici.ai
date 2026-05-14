from datetime import datetime
from typing import Any

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
    archived: bool = False


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
    archived: bool
    created_at: datetime
    updated_at: datetime


class AgentToggleResponse(BaseModel):
    id: int
    ativo: bool


class AgentChannelCreate(BaseModel):
    channel_type: str = Field(pattern="^(website|whatsapp|instagram|api|email|facebook|custom)$")
    provider_name: str = "internal"
    external_account_id: str | None = None
    channel_id: str
    credential_ref: str | None = None
    enabled: bool = True
    test_mode: bool = True
    config: dict[str, Any] = Field(default_factory=dict)
    api_key: str | None = None


class AgentChannelUpdate(BaseModel):
    provider_name: str | None = None
    external_account_id: str | None = None
    credential_ref: str | None = None
    enabled: bool | None = None
    test_mode: bool | None = None
    config: dict[str, Any] | None = None
    api_key: str | None = None


class AgentChannelRead(BaseModel):
    id: int
    agent_id: int
    channel_type: str
    provider_name: str
    external_account_id: str | None = None
    channel_id: str
    credential_ref: str | None = None
    enabled: bool
    test_mode: bool
    config: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class AgentKnowledgeCreate(BaseModel):
    title: str
    kind: str = "note"
    content: str
    tags: str | None = None
    enabled: bool = True


class AgentKnowledgeUpdate(BaseModel):
    title: str | None = None
    kind: str | None = None
    content: str | None = None
    tags: str | None = None
    enabled: bool | None = None


class AgentKnowledgeRead(BaseModel):
    id: int
    agent_id: int
    title: str
    kind: str
    content: str
    tags: str | None = None
    enabled: bool
    created_at: datetime
    updated_at: datetime


class AgentActionCreate(BaseModel):
    name: str
    action_type: str = Field(pattern="^(save_lead|qualify_lead|transfer_human|webhook_call|send_email|create_task|schedule_callback|crm_event|custom)$")
    trigger_keywords: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class AgentActionUpdate(BaseModel):
    name: str | None = None
    action_type: str | None = None
    trigger_keywords: str | None = None
    config: dict[str, Any] | None = None
    enabled: bool | None = None


class AgentActionRead(BaseModel):
    id: int
    agent_id: int
    name: str
    action_type: str
    trigger_keywords: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    enabled: bool
    created_at: datetime
    updated_at: datetime


class AgentTestRequest(BaseModel):
    text: str
    channel_type: str = "api"


class AgentTestResponse(BaseModel):
    conversation_id: int
    status: str
    response: str
    actions: list[dict[str, Any]] = Field(default_factory=list)


class AgentLogRead(BaseModel):
    id: int
    agent_id: int
    conversation_id: int | None = None
    event_type: str
    status: str
    summary: str
    input_text: str | None = None
    output_text: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class AgentAnalyticsRead(BaseModel):
    agent_id: int
    total_inbound_messages: int
    total_outbound_messages: int
    total_conversations: int
    active_conversations: int
    human_handoffs: int
    actions_executed: int
    failed_responses: int
    average_response_time_ms: int
    channel_distribution: dict[str, int]
    leads_captured: int


class WidgetSessionCreateRequest(BaseModel):
    agent_id: int
    visitor_id: str


class WidgetSessionCreateResponse(BaseModel):
    session_token: str
    conversation_id: int
    greeting: str


class WidgetMessageRequest(BaseModel):
    session_token: str
    text: str


class WidgetMessageResponse(BaseModel):
    conversation_id: int
    response: str
    status: str


class WidgetConversationResponse(BaseModel):
    conversation_id: int
    status: str
    messages: list[dict[str, Any]]


class ChannelApiInboundRequest(BaseModel):
    channel_id: str
    external_user_id: str
    external_conversation_id: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChannelApiInboundResponse(BaseModel):
    conversation_id: int
    response: str
    status: str


class InboundWebhookResponse(BaseModel):
    ok: bool
    detail: str
