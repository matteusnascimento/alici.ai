from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime


class ReservationBase(BaseModel):
    guest_name: str
    check_in: date
    check_out: date
    room_type: str
    guests: int
    total_price: float
    total_amount: Optional[float] = None
    status: str = "confirmed"
    external_reservation_id: Optional[str] = None
    reservation_number: Optional[str] = None
    guest_document: Optional[str] = None
    guest_email: Optional[str] = None
    channel: Optional[str] = None
    source: Optional[str] = None
    source_provider: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    reservation_identity_hash: Optional[str] = None


class ReservationCreate(BaseModel):
    reservation_id: Optional[str] = None
    external_reservation_id: Optional[str] = None
    reservation_number: Optional[str] = None
    guest_name: str
    guest_document: Optional[str] = None
    guest_email: Optional[str] = None
    check_in: date
    check_out: date
    room_type: str
    guests: int
    total_price: Optional[float] = None
    total_amount: Optional[float] = None
    channel: Optional[str] = None
    source: Optional[str] = None
    source_provider: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    status: str = "confirmed"


class ReservationRead(ReservationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reservation_id: str
    created_at: datetime
    updated_at: datetime


class ReservationUpdate(BaseModel):
    external_reservation_id: Optional[str] = None
    reservation_number: Optional[str] = None
    guest_name: Optional[str] = None
    guest_document: Optional[str] = None
    guest_email: Optional[str] = None
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    room_type: Optional[str] = None
    guests: Optional[int] = None
    total_price: Optional[float] = None
    total_amount: Optional[float] = None
    channel: Optional[str] = None
    source: Optional[str] = None
    source_provider: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    status: Optional[str] = None
