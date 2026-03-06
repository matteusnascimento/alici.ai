"""
Organization model for multi-tenant architecture
"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Organization(Base):
    __tablename__ = "platform_organizations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)

    # Billing
    plan = Column(String, default="free")  # free, pro, enterprise
    stripe_customer_id = Column(String, unique=True)

    # Limits
    monthly_request_limit = Column(Integer, default=1000)
    current_month_requests = Column(Integer, default=0)

    # Settings
    is_active = Column(Boolean, default=True)
    allow_public_api = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="organization")
    agents = relationship("Agent", back_populates="organization")
    api_keys = relationship("APIKey", back_populates="organization")
    usage_logs = relationship("UsageLog", back_populates="organization")

    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name}, plan={self.plan})>"