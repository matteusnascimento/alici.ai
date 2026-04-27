from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class ReservationBase(BaseModel):
    guest_name: str
    check_in: date
    check_out: date
    room_type: str
    guests: int
    total_price: float
    status: str = "confirmed"


class ReservationCreate(BaseModel):
    guest_name: str
    check_in: date
    check_out: date
    room_type: str
    guests: int
    status: str = "confirmed"


class ReservationRead(ReservationBase):
    id: int
    reservation_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReservationUpdate(BaseModel):
    guest_name: Optional[str] = None
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    room_type: Optional[str] = None
    guests: Optional[int] = None
    total_price: Optional[float] = None
    status: Optional[str] = None
