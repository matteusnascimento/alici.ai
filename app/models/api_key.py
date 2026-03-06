"""
API Key model for public API access
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)

    # Multi-tenant
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)

    # Permissions
    can_chat = Column(Boolean, default=True)
    can_generate = Column(Boolean, default=True)

    # Usage tracking
    total_requests = Column(Integer, default=0)
    monthly_requests = Column(Integer, default=0)

    # Settings
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True))

    # Relationships
    organization = relationship("Organization", back_populates="api_keys")

    def __repr__(self):
        return f"<APIKey(id={self.id}, name={self.name}, org={self.organization_id})>"