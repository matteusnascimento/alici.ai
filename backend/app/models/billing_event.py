from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BillingEvent(Base):
    __tablename__ = "billing_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    event_type: Mapped[str] = mapped_column(String(50))
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="BRL")
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # Campos Stripe — idempotência e rastreabilidade
    stripe_event_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True, unique=True)
    status: Mapped[str | None] = mapped_column(String(30), nullable=True)  # succeeded, failed, pending
    payload_json: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="billing_events")
