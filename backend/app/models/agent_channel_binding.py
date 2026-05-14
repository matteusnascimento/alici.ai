from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AgentChannelBinding(Base):
    __tablename__ = "agent_channel_bindings"
    __table_args__ = (
        UniqueConstraint("agent_id", "channel_endpoint_id", name="uq_agent_channel_binding_endpoint"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), index=True)
    channel_endpoint_id: Mapped[int] = mapped_column(ForeignKey("channel_endpoints.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(40), index=True)
    status: Mapped[str] = mapped_column(String(30), default="disconnected", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    fallback_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    last_test_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_test_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    last_test_message: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    agent = relationship("Agent", back_populates="channel_bindings")
    channel_endpoint = relationship("ChannelEndpoint", back_populates="bindings")