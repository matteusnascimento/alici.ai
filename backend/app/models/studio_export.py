from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StudioExport(Base):
    __tablename__ = "studio_exports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("studio_projects.id", ondelete="CASCADE"), index=True)
    export_type: Mapped[str] = mapped_column(String(40), index=True)
    file_url: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(40), default="ready")
    metadata_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
