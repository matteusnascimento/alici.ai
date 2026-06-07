from datetime import datetime
import json

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text(), nullable=True)
    company: Mapped[str | None] = mapped_column(String(140), nullable=True)
    job_title: Mapped[str | None] = mapped_column(String(140), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(60), nullable=True)
    email_verified: Mapped[bool] = mapped_column(default=False)
    phone_verified: Mapped[bool] = mapped_column(default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    email_verification_code: Mapped[str | None] = mapped_column(String(12), nullable=True)
    email_verification_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    phone_verification_code: Mapped[str | None] = mapped_column(String(12), nullable=True)
    phone_verification_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    plan: Mapped[str] = mapped_column(String(50), default="free")
    disabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    billing_events = relationship("BillingEvent", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="user", cascade="all, delete-orphan")
    integration_accounts = relationship("IntegrationAccount", back_populates="user", cascade="all, delete-orphan")
    marketing_projects = relationship("MarketingProject", back_populates="user", cascade="all, delete-orphan")
    marketing_audiences = relationship("MarketingAudience", back_populates="user", cascade="all, delete-orphan")
    marketing_calendar_events = relationship("MarketingCalendarEvent", back_populates="user", cascade="all, delete-orphan")
    media_projects = relationship("MediaProject", back_populates="user", cascade="all, delete-orphan")
    media_jobs = relationship("MediaJob", back_populates="user", cascade="all, delete-orphan")
    agent_channels = relationship("AgentChannel", back_populates="user", cascade="all, delete-orphan")
    agent_knowledge_items = relationship("AgentKnowledge", back_populates="user", cascade="all, delete-orphan")
    agent_actions = relationship("AgentAction", back_populates="user", cascade="all, delete-orphan")
    auth_tokens = relationship("AuthToken", back_populates="user", cascade="all, delete-orphan")
    admin_permissions = relationship(
        "AdminPermission",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="AdminPermission.user_id",
    )

    @property
    def role(self) -> str:
        from app.core.config import settings

        email = (self.email or "").strip().lower()
        owner_emails = {item.strip().lower() for item in settings.owner_emails if item.strip()}
        admin_emails = {item.strip().lower() for item in settings.admin_emails if item.strip()}
        billing_admin_emails = {item.strip().lower() for item in settings.billing_admin_emails if item.strip()}
        if email in owner_emails:
            return "owner"
        if settings.should_seed_dev_user and email == settings.dev_seed_email.strip().lower():
            return "owner"
        if email in admin_emails or email in billing_admin_emails:
            return "admin"
        return "member"

    @property
    def permissions(self) -> dict[str, str]:
        modules = {
            "revenue",
            "chats",
            "assistant",
            "marketing",
            "studio",
            "integrations",
            "admin",
        }
        if self.role in {"owner", "admin"}:
            return {module: "admin" for module in modules}

        row = self.admin_permissions
        if not row or not row.permissions_json:
            return {}
        try:
            payload = json.loads(row.permissions_json)
        except (TypeError, ValueError):
            return {}
        if not isinstance(payload, dict):
            return {}
        return {
            str(module): str(level)
            for module, level in payload.items()
            if module in modules and level in {"none", "read", "write", "admin"}
        }
