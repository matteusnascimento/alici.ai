from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class IntegrationAccount(Base):
    __tablename__ = "integration_accounts"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", "external_account_id", name="uq_integration_account_provider_external"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(40), index=True)
    external_account_id: Mapped[str | None] = mapped_column(String(180), nullable=True)
    external_account_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    access_token_encrypted: Mapped[str | None] = mapped_column(Text(), nullable=True)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text(), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="disconnected", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", back_populates="integration_accounts")
    endpoints = relationship("ChannelEndpoint", back_populates="integration_account", cascade="all, delete-orphan")