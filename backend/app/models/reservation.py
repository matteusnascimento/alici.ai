from datetime import datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reservation_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # RES-2026-001
    external_reservation_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    reservation_number: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    guest_name: Mapped[str] = mapped_column(String(120))
    guest_document: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    guest_email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    check_in: Mapped[datetime] = mapped_column(Date())
    check_out: Mapped[datetime] = mapped_column(Date())
    room_type: Mapped[str] = mapped_column(String(50))
    guests: Mapped[int] = mapped_column(Integer())
    total_price: Mapped[float] = mapped_column(Float())
    channel: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    source: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_provider: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    reservation_identity_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True, index=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    state: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    country: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(50), default="confirmed")  # confirmed, cancelled, checked_in, checked_out
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
