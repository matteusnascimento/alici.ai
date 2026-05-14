from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AgentConfiguration(Base):
    __tablename__ = "agent_configurations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), index=True, unique=True)
    language: Mapped[str] = mapped_column(String(40), default="pt-BR")
    tone: Mapped[str | None] = mapped_column(String(80), nullable=True)
    objective: Mapped[str | None] = mapped_column(String(180), nullable=True)
    working_hours: Mapped[str | None] = mapped_column(String(120), nullable=True)
    fallback_to_human: Mapped[bool] = mapped_column(Boolean, default=True)
    system_instructions: Mapped[str | None] = mapped_column(Text(), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    temperature: Mapped[str | None] = mapped_column(String(20), nullable=True)
    advanced_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
