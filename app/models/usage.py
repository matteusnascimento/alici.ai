"""
Usage tracking models
"""
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(String, primary_key=True, index=True)

    # Multi-tenant
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"))
    api_key_id = Column(String, ForeignKey("api_keys.id"))

    # Request details
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer)

    # AI usage
    agent_id = Column(String, ForeignKey("agents.id"))
    model = Column(String)
    tokens_used = Column(Integer)
    cost = Column(Float, default=0.0)

    # Request/Response
    request_size = Column(Integer)  # bytes
    response_size = Column(Integer)  # bytes
    user_agent = Column(String)
    ip_address = Column(String)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    organization = relationship("Organization", back_populates="usage_logs")

    def __repr__(self):
        return f"<UsageLog(id={self.id}, endpoint={self.endpoint}, cost={self.cost})>"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)

    # Multi-tenant
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)

    # Settings
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_message_at = Column(DateTime(timezone=True))

    # Relationships
    organization = relationship("Organization")
    agent = relationship("Agent", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", order_by="Message.created_at")

    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title})>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, index=True)

    # Conversation
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)

    # Content
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # AI metadata
    model = Column(String)
    tokens_used = Column(Integer)
    finish_reason = Column(String)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, tokens={self.tokens_used})>"