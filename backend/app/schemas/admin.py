from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.billing import BillingHistoryItem, BillingUsageItem, CurrentSubscriptionResponse, PlanLimit


AdminPermissionLevel = Literal["none", "read", "write", "admin"]

ADMIN_PERMISSION_MODULES = {
    "revenue": "Revenue",
    "chats": "Chats",
    "assistant": "AXI Assistant",
    "marketing": "Marketing",
    "studio": "Studio",
    "integrations": "Integrations",
    "admin": "Administracao",
}


class AdminMetric(BaseModel):
    label: str
    value: int


class AdminUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: str
    plan: str
    job_title: str | None = None
    phone: str | None = None
    company: str | None = None
    status: Literal["active", "inactive", "pending"]
    last_login_at: datetime | None = None
    created_at: datetime | None = None
    disabled_at: datetime | None = None
    email_verified: bool = False
    permissions: dict[str, AdminPermissionLevel] = Field(default_factory=dict)


class AdminCompanyRead(BaseModel):
    name: str
    email: str | None = None
    plan: str
    status: str
    users_count: int
    created_at: str | None = None


class AdminCompanyCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=140)
    razao_social: str | None = Field(default=None, max_length=180)
    cnpj: str | None = Field(default=None, max_length=32)
    email: EmailStr
    telefone: str | None = Field(default=None, max_length=30)
    plano: str = Field(default="basic", pattern="^(basic|pro|enterprise)$")
    modules: list[str] = Field(default_factory=list)


class AdminOverviewResponse(BaseModel):
    empresas: list[AdminCompanyRead]
    usuarios: list[AdminUserRead]
    permissoes: list[str]
    billing: list[AdminMetric]
    seguranca: list[AdminMetric]
    auditoria: list[AdminMetric]


class AdminUserInviteRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    job_title: str | None = Field(default=None, max_length=140)
    phone: str | None = Field(default=None, max_length=30)
    permissions: dict[str, AdminPermissionLevel] = Field(default_factory=dict)


class AdminUserInviteResponse(BaseModel):
    user: AdminUserRead
    email_delivery: Literal["sent", "unavailable"] = "unavailable"
    message: str
    invite_token: str | None = None


class AdminUserUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    email: EmailStr | None = None
    job_title: str | None = Field(default=None, max_length=140)
    phone: str | None = Field(default=None, max_length=30)
    plan: str | None = Field(default=None, max_length=50)


class AdminUserActionResponse(BaseModel):
    message: str
    user: AdminUserRead | None = None
    reset_token: str | None = None


class AdminPermissionsResponse(BaseModel):
    user_id: int
    permissions: dict[str, AdminPermissionLevel]


class AdminPermissionsUpdateRequest(BaseModel):
    permissions: dict[str, AdminPermissionLevel]

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, value: dict[str, AdminPermissionLevel]) -> dict[str, AdminPermissionLevel]:
        unknown = sorted(set(value) - set(ADMIN_PERMISSION_MODULES))
        if unknown:
            raise ValueError(f"Modulo de permissao invalido: {', '.join(unknown)}")
        return value


class AdminSecurityEvent(BaseModel):
    id: int
    user_id: int | None = None
    user_name: str | None = None
    user_email: str | None = None
    event_type: str
    status: str
    created_at: datetime | None = None
    expires_at: datetime | None = None
    revoked_at: datetime | None = None


class AdminSecurityResponse(BaseModel):
    last_logins: list[AdminSecurityEvent]
    active_sessions: list[AdminSecurityEvent]
    open_sessions: list[AdminSecurityEvent]
    login_attempts: list[AdminSecurityEvent]
    revoked_tokens: list[AdminSecurityEvent]


class AdminAuditEventRead(BaseModel):
    id: int
    data: datetime | None = None
    usuario: str | None = None
    acao: str
    origem: str
    detalhes: dict | None = None


class AdminAuditResponse(BaseModel):
    events: list[AdminAuditEventRead]


class AdminBillingResponse(BaseModel):
    current: CurrentSubscriptionResponse
    usage: list[BillingUsageItem]
    limits: list[PlanLimit]
    events: list[BillingHistoryItem]
    stripe_configured: bool
    message: str | None = None
