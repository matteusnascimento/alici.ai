from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MediaProject(Base):
    __tablename__ = "media_projects"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(140))
    timeline_json: Mapped[dict] = mapped_column(JSON, default=dict)
    thumbnail: Mapped[str | None] = mapped_column(String(512), nullable=True)
    duration: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="media_projects")
    jobs = relationship("MediaJob", back_populates="project", cascade="all, delete-orphan")
