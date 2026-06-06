from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IntegrationRead(BaseModel):
    id: int
    provider: str
    name: str
    is_active: bool
    created_at: datetime


class IntegrationTestRequest(BaseModel):
    api_key: str | None = None
    token: str | None = None
    endpoint: str | None = None


class IntegrationTestResponse(BaseModel):
    provider: str
    status: str
    message: str
    model: str | None = None
    model_used: str | None = None
    latency_ms: float | None = None
    error_type: str | None = None
    status_code: int | None = None


class IntegrationProviderRead(BaseModel):
    provider: str
    title: str
    description: str
    status: str
    helper_text: str
    connected_accounts: int
    active_bindings: int
    supports_activation: bool
    account_name: str | None = None
    last_sync_at: datetime | None = None
    last_error: str | None = None
    data_received: int | None = None
    scopes: list[str] = Field(default_factory=list)


class IntegrationAccountCreateRequest(BaseModel):
    provider: str
    external_account_id: str | None = None
    external_account_name: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class IntegrationAccountRead(BaseModel):
    id: int
    provider: str
    external_account_id: str | None
    external_account_name: str | None
    status: str
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class IntegrationProviderStatusRead(BaseModel):
    provider: str
    status: str
    connected_accounts: int
    active_endpoints: int
    active_bindings: int
    helper_text: str
    account_name: str | None = None
    last_sync_at: datetime | None = None
    last_error: str | None = None
    data_received: int | None = None
    scopes: list[str] = Field(default_factory=list)


class IntegrationOAuthStartRequest(BaseModel):
    redirect_path: str | None = None


class IntegrationOAuthStartResponse(BaseModel):
    provider: str
    authorization_url: str


class IntegrationQrStartRequest(BaseModel):
    redirect_path: str | None = None


class IntegrationQrStartResponse(BaseModel):
    provider: str
    qr_code_url: str
    pairing_code: str
    expires_at: datetime


class WebsiteChatScriptResponse(BaseModel):
    provider: str = "website_chat"
    company_id: str
    script: str
