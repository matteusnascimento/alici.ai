from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class WidgetSession(Base):
    __tablename__ = "widget_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), index=True)
    channel_id: Mapped[str] = mapped_column(String(180), index=True)
    visitor_id: Mapped[str] = mapped_column(String(180), index=True)
    session_token: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    external_conversation_id: Mapped[str] = mapped_column(String(180), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    agent = relationship("Agent", back_populates="widget_sessions")
