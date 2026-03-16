from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Organization(TimestampMixin, Base):
    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    users = relationship("User", back_populates="organization", cascade="all, delete")
    agents = relationship("Agent", back_populates="organization", cascade="all, delete")
    conversations = relationship("Conversation", back_populates="organization", cascade="all, delete")
    workflows = relationship("Workflow", back_populates="organization", cascade="all, delete")
    knowledge_documents = relationship("KnowledgeDocument", back_populates="organization", cascade="all, delete")
    integrations = relationship("Integration", back_populates="organization", cascade="all, delete")
    usage_logs = relationship("UsageLog", back_populates="organization", cascade="all, delete")
    subscriptions = relationship("Subscription", back_populates="organization", cascade="all, delete")