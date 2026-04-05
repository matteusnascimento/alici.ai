from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StudioGeneration(Base):
    __tablename__ = "studio_generations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("studio_projects.id", ondelete="SET NULL"), nullable=True, index=True)
    generation_type: Mapped[str] = mapped_column(String(60), index=True)
    prompt: Mapped[str] = mapped_column(Text())
    input_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    output_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="completed", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
