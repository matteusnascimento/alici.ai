from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)

    # Plano e status local
    plan_id: Mapped[str] = mapped_column(String(40), default="free")
    status: Mapped[str] = mapped_column(String(30), default="active")
    billing_cycle: Mapped[str] = mapped_column(String(20), default="monthly")
    monthly_price: Mapped[float] = mapped_column(Float, default=0.0)
    yearly_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="BRL")

    # Campos Stripe
    provider: Mapped[str | None] = mapped_column(String(40), nullable=True)  # "stripe" quando aplicável
    stripe_customer_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    stripe_price_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, default=False)
    last_checkout_session_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_invoice_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    external_status: Mapped[str | None] = mapped_column(String(40), nullable=True)  # status vindo do Stripe
    metadata_json: Mapped[str | None] = mapped_column(Text(), nullable=True)

    # Período e trial
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Configurações
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=True)
    seats: Mapped[int] = mapped_column(Integer, default=1)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", back_populates="subscription")
