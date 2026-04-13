from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AIRequestLog(Base):
    __tablename__ = "ai_request_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    agent_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    endpoint: Mapped[str | None] = mapped_column(String(120), nullable=True)
    task_name: Mapped[str] = mapped_column(String(60), index=True)
    provider: Mapped[str] = mapped_column(String(30), default="openai")
    model: Mapped[str] = mapped_column(String(80), default="gpt-4o-mini")
    status: Mapped[str] = mapped_column(String(30), default="success")
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    error_summary: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
