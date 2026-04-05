from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AgentTestSession(Base):
    __tablename__ = "agent_test_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), index=True)
    scenario: Mapped[str] = mapped_column(String(120))
    input_text: Mapped[str] = mapped_column(Text())
    output_text: Mapped[str] = mapped_column(Text())
    action_trace_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    context_used: Mapped[str | None] = mapped_column(Text(), nullable=True)
    confidence_note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="ok")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
