from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ChannelMessage(Base):
    __tablename__ = "channel_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    agent_id: Mapped[int | None] = mapped_column(ForeignKey("agents.id", ondelete="SET NULL"), index=True, nullable=True)
    provider: Mapped[str] = mapped_column(String(40), index=True)
    direction: Mapped[str] = mapped_column(String(30), index=True)
    external_message_id: Mapped[str | None] = mapped_column(String(180), nullable=True, index=True)
    endpoint_id: Mapped[int | None] = mapped_column(ForeignKey("channel_endpoints.id", ondelete="SET NULL"), index=True, nullable=True)
    binding_id: Mapped[int | None] = mapped_column(ForeignKey("agent_channel_bindings.id", ondelete="SET NULL"), index=True, nullable=True)
    payload_summary: Mapped[str] = mapped_column(Text())
    status: Mapped[str] = mapped_column(String(30), default="processing", index=True)
    error_message: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
