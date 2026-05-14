from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ToolExecution(Base):
    __tablename__ = "tool_executions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tool_name: Mapped[str] = mapped_column(String(100), index=True)
    tool_args: Mapped[str] = mapped_column(Text())  # JSON string dos argumentos
    success: Mapped[bool] = mapped_column(default=True)
    result: Mapped[str | None] = mapped_column(Text(), nullable=True)  # JSON string do resultado
    error: Mapped[str | None] = mapped_column(Text(), nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    agent_id: Mapped[int | None] = mapped_column(Integer(), nullable=True)  # Se executado por um agent
    user_id: Mapped[int | None] = mapped_column(Integer(), nullable=True)  # Usuário que iniciou
    conversation_id: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())