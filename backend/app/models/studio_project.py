from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StudioProject(Base):
    __tablename__ = "studio_projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    project_type: Mapped[str] = mapped_column(String(60), index=True)
    title: Mapped[str] = mapped_column(String(180))
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    metadata_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    canvas_data_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    layers_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    timeline_data_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    export_settings_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    preview_thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
