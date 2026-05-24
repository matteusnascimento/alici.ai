from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StudioVersion(Base):
    __tablename__ = "studio_versions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("studio_projects.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(120))
    canvas_data_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    layers_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    timeline_data_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
