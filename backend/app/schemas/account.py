from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AccountProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    username: str
    email: EmailStr
    phone: str | None
    avatar_url: str | None = None
    bio: str | None = None
    company: str | None = None
    job_title: str | None = None
    timezone: str | None = None
    language: str
    email_verified: bool
    phone_verified: bool
    status: str
    plan: str
    created_at: datetime
    updated_at: datetime | None = None
    last_login_at: datetime | None = None


class AccountProfileUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    phone: str | None = None
    avatar_url: str | None = None
    bio: str | None = Field(default=None, max_length=500)
    company: str | None = Field(default=None, max_length=140)
    job_title: str | None = Field(default=None, max_length=140)
    timezone: str | None = Field(default=None, max_length=60)
    language: str | None = Field(default=None, max_length=20)


class AccountPreferencesRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    language: str
    voice: str
    theme_mode: str
    accent_color: str
    haptic_feedback: bool
    background_conversation: bool
    autocomplete: bool
    trending: bool
    sequence: bool
    split_mode: bool


class AccountPreferencesUpdate(BaseModel):
    language: str
    voice: str
    theme_mode: str
    accent_color: str
    haptic_feedback: bool
    background_conversation: bool
    autocomplete: bool
    trending: bool
    sequence: bool
    split_mode: bool


class AccountNotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    notifications_enabled: bool
    email_notifications: bool
    push_notifications: bool
    product_updates: bool
    marketing_notifications: bool
    security_alerts: bool


class AccountNotificationUpdate(BaseModel):
    notifications_enabled: bool
    email_notifications: bool
    push_notifications: bool
    product_updates: bool
    marketing_notifications: bool
    security_alerts: bool


class AccountIntegrationRead(BaseModel):
    id: int
    provider: str
    name: str
    enabled: bool
    status: str
    updated_at: datetime | None = None


class AccountIntegrationUpdate(BaseModel):
    enabled: bool


class AccountSecurityChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)


class AccountSecuritySummary(BaseModel):
    password_last_changed: datetime | None = None
    session_count: int
    security_alerts: bool


class AccountActionResponse(BaseModel):
    message: str


class AccountVerificationChallenge(BaseModel):
    channel: str
    destination: str
    expires_at: datetime
    message: str
    preview_code: str | None = None


class AccountVerificationConfirm(BaseModel):
    code: str = Field(min_length=4, max_length=12)


class AccountSubscriptionView(BaseModel):
    plan_id: str
    plan_name: str
    status: str
    billing_cycle: str
    monthly_price: float
    yearly_price: float | None = None
    auto_renew: bool
    started_at: datetime | None = None


class AccountArchivedChatItem(BaseModel):
    id: int
    title: str
    archived_at: datetime | None = None


class AccountArchivedChatList(BaseModel):
    items: list[AccountArchivedChatItem]


class AccountPrivacyRead(BaseModel):
    archived_chat_visibility: bool
    data_portability_supported: bool = True
    account_deletion_supported: bool = True
    notes: list[str]


class AccountHelpInfo(BaseModel):
    app_version: str
    help_center_url: str
    report_bug_url: str


class AccountLegalInfo(BaseModel):
    terms_url: str
    privacy_url: str
