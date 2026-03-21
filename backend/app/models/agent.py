from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    nome: Mapped[str] = mapped_column(String(120))
    funcao: Mapped[str] = mapped_column(String(160))
    tipo: Mapped[str] = mapped_column(String(60))
    linguagem: Mapped[str] = mapped_column(String(40), default="pt-BR")
    prompt: Mapped[str] = mapped_column(Text())
    whatsapp: Mapped[str | None] = mapped_column(String(120), nullable=True)
    instagram: Mapped[str | None] = mapped_column(String(120), nullable=True)
    api: Mapped[str | None] = mapped_column(String(255), nullable=True)
    outros: Mapped[str | None] = mapped_column(String(255), nullable=True)
    outros_nome: Mapped[str | None] = mapped_column(String(120), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="agents")
