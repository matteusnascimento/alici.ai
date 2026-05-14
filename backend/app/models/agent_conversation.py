from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AgentConversation(Base):
    __tablename__ = "agent_conversations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), index=True)
    channel_type: Mapped[str] = mapped_column(String(40), index=True)
    channel_id: Mapped[str] = mapped_column(String(180), index=True)
    external_user_id: Mapped[str] = mapped_column(String(180), index=True)
    external_conversation_id: Mapped[str] = mapped_column(String(180), index=True)
    status: Mapped[str] = mapped_column(String(40), default="active_ai", index=True)
    sales_stage: Mapped[str] = mapped_column(String(40), default="novo_lead", index=True)
    reservation_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    lead_source: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    is_remarketing: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    assigned_to_human: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    agent = relationship("Agent", back_populates="runtime_conversations")
    messages = relationship("AgentMessage", back_populates="conversation", cascade="all, delete-orphan")
    logs = relationship("AgentLog", back_populates="conversation")
