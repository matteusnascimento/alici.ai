"""Persistent user memory model."""

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class UserMemory(Base):
    __tablename__ = "platform_user_memory"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("platform_users.id"), nullable=False, index=True)
    organization_id = Column(String, ForeignKey("platform_organizations.id"), nullable=False, index=True)

    key = Column(String, nullable=False, index=True)
    value = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<UserMemory(user_id={self.user_id}, key={self.key})>"
