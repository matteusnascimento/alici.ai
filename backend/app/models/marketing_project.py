from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MarketingProject(Base):
    __tablename__ = "marketing_projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    objective: Mapped[str] = mapped_column(String(160))
    audience: Mapped[str] = mapped_column(String(160))
    offer: Mapped[str] = mapped_column(String(200))
    tone: Mapped[str] = mapped_column(String(60), default="premium")
    channels: Mapped[str | None] = mapped_column(String(240), nullable=True)
    budget: Mapped[float | None] = mapped_column(Float(), nullable=True)
    creative_project_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_publish_error: Mapped[str | None] = mapped_column(Text(), nullable=True)
    metrics_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="marketing_projects")
