from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    proposal_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # PROP-2026-001
    lead_id: Mapped[int] = mapped_column(Integer(), index=True)
    proposal_type: Mapped[str] = mapped_column(String(50))
    value: Mapped[float] = mapped_column(Float())
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, sent, accepted, rejected
    content: Mapped[str | None] = mapped_column(Text(), nullable=True)  # Conteúdo da proposta
    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)  # Caminho do arquivo gerado
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )