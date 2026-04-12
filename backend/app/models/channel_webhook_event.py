from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ChannelWebhookEvent(Base):
    __tablename__ = "channel_webhook_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    channel_endpoint_id: Mapped[int | None] = mapped_column(
        ForeignKey("channel_endpoints.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    provider: Mapped[str] = mapped_column(String(40), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    payload_json: Mapped[str] = mapped_column(Text())
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    error_message: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    channel_endpoint = relationship("ChannelEndpoint", back_populates="webhook_events")