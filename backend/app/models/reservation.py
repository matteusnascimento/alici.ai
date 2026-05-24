from datetime import datetime

from sqlalchemy import Date, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    reservation_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # RES-2026-001
    guest_name: Mapped[str] = mapped_column(String(120))
    check_in: Mapped[datetime] = mapped_column(Date())
    check_out: Mapped[datetime] = mapped_column(Date())
    room_type: Mapped[str] = mapped_column(String(50))
    guests: Mapped[int] = mapped_column(Integer())
    total_price: Mapped[float] = mapped_column(Float())
    status: Mapped[str] = mapped_column(String(50), default="confirmed")  # confirmed, cancelled, checked_in, checked_out
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )