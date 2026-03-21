from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    background_conversation: Mapped[bool] = mapped_column(Boolean, default=True)
    autocomplete: Mapped[bool] = mapped_column(Boolean, default=True)
    trending: Mapped[bool] = mapped_column(Boolean, default=True)
    sequence: Mapped[bool] = mapped_column(Boolean, default=False)
    split_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    language: Mapped[str] = mapped_column(String(20), default="pt-BR")
    voice: Mapped[str] = mapped_column(String(40), default="neutral")

    user = relationship("User", back_populates="settings")
