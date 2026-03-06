"""
Agent model for AI orchestration
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Agent(Base):
    __tablename__ = "platform_agents"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    system_prompt = Column(Text, nullable=False)

    # Configuration
    model = Column(String, default="gpt-3.5-turbo")  # gpt-3.5-turbo, gpt-4, claude, etc.
    temperature = Column(Integer, default=70)  # 0-100
    max_tokens = Column(Integer, default=1000)

    # Multi-tenant
    organization_id = Column(String, ForeignKey("platform_organizations.id"), nullable=False)

    # Settings
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)  # Can be used via public API

    # Usage tracking
    total_requests = Column(Integer, default=0)
    monthly_requests = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="agents")
    conversations = relationship("Conversation", back_populates="agent")

    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, model={self.model})>"