from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ChannelEndpoint(Base):
    __tablename__ = "channel_endpoints"
    __table_args__ = (
        UniqueConstraint("integration_account_id", "provider", "external_channel_id", name="uq_channel_endpoint_external"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    integration_account_id: Mapped[int] = mapped_column(
        ForeignKey("integration_accounts.id", ondelete="CASCADE"),
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(40), index=True)
    external_channel_id: Mapped[str | None] = mapped_column(String(180), nullable=True)
    channel_name: Mapped[str] = mapped_column(String(180))
    phone_number_or_handle: Mapped[str | None] = mapped_column(String(180), nullable=True)
    webhook_status: Mapped[str] = mapped_column(String(30), default="pending_setup")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    integration_account = relationship("IntegrationAccount", back_populates="endpoints")
    bindings = relationship("AgentChannelBinding", back_populates="channel_endpoint", cascade="all, delete-orphan")
    webhook_events = relationship("ChannelWebhookEvent", back_populates="channel_endpoint")