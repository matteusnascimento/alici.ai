from datetime import datetime

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
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="user", cascade="all, delete-orphan")
    integration_accounts = relationship("IntegrationAccount", back_populates="user", cascade="all, delete-orphan")
    marketing_projects = relationship("MarketingProject", back_populates="user", cascade="all, delete-orphan")
    media_projects = relationship("MediaProject", back_populates="user", cascade="all, delete-orphan")
    media_jobs = relationship("MediaJob", back_populates="user", cascade="all, delete-orphan")
    agent_channels = relationship("AgentChannel", back_populates="user", cascade="all, delete-orphan")
    agent_knowledge_items = relationship("AgentKnowledge", back_populates="user", cascade="all, delete-orphan")
    agent_actions = relationship("AgentAction", back_populates="user", cascade="all, delete-orphan")
