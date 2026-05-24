from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AgentMetric(Base):
    __tablename__ = "agent_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), index=True)
    metric_key: Mapped[str] = mapped_column(String(80), index=True)
    metric_value: Mapped[str] = mapped_column(String(80))
    period: Mapped[str] = mapped_column(String(40), default="total")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
