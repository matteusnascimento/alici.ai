"""Knowledge base models for document conversations."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class KnowledgeDocument(Base):
    __tablename__ = "platform_knowledge_documents"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("platform_users.id"), nullable=False, index=True)
    organization_id = Column(String, ForeignKey("platform_organizations.id"), nullable=False, index=True)

    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    title = Column(String)

    total_chunks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class KnowledgeChunk(Base):
    __tablename__ = "platform_knowledge_chunks"

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("platform_knowledge_documents.id"), nullable=False, index=True)
    organization_id = Column(String, ForeignKey("platform_organizations.id"), nullable=False, index=True)

    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
