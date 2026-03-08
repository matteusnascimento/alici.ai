"""Integration model for external connectors."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Integration(Base):
    __tablename__ = "platform_integrations"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("platform_users.id"), nullable=False, index=True)
    organization_id = Column(String, ForeignKey("platform_organizations.id"), nullable=False, index=True)
    type = Column(String, nullable=False, index=True)
    credentials = Column(Text, default="{}")
    status = Column(String, default="disconnected")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User")
    organization = relationship("Organization")

    def __repr__(self):
        return f"<Integration(id={self.id}, type={self.type}, user_id={self.user_id})>"
