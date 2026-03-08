"""User settings model for profile preferences."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class UserSetting(Base):
    __tablename__ = "platform_user_settings"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("platform_users.id"), unique=True, nullable=False, index=True)

    language = Column(String, default="pt-BR")
    theme = Column(String, default="dark")
    notifications_enabled = Column(Boolean, default=True)
    api_key_alias = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User")

    def __repr__(self):
        return f"<UserSetting(user_id={self.user_id}, language={self.language}, theme={self.theme})>"
