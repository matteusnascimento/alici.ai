from datetime import date
import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.reservation import Reservation
from app.schemas.reservation import ReservationCreate, ReservationRead, ReservationUpdate


class ReservationService:
    ROOM_INVENTORY = {
        "standard": 5,
        "deluxe": 3,
        "suite": 1,
    }
    ROOM_PRICES = {
        "standard": 150.0,
        "deluxe": 250.0,
        "suite": 400.0,
    }

    def __init__(self, db: Session):
        self.db = db

    def _reservation_or_404(self, reservation_id: int) -> Reservation:
        reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva nao encontrada")
        return reservation

    def _generate_reservation_id(self) -> str:
        return f"RES-{date.today().year}-{uuid.uuid4().hex[:3].upper()}"

    def _calculate_price(self, room_type: str, check_in: date, check_out: date) -> float:
        price_per_night = self.ROOM_PRICES.get(room_type, self.ROOM_PRICES["standard"])
        nights = (check_out - check_in).days
        return price_per_night * nights

    def create_reservation(self, reservation_data: ReservationCreate) -> ReservationRead:
        if reservation_data.check_in >= reservation_data.check_out:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data de check-out deve ser posterior a data de check-in",
            )

        total_price = self._calculate_price(
            reservation_data.room_type,
            reservation_data.check_in,
            reservation_data.check_out,
        )

        reservation = Reservation(
            reservation_id=self._generate_reservation_id(),
            **reservation_data.model_dump(),
            total_price=total_price,
        )

        self.db.add(reservation)
        try:
            self.db.commit()
            self.db.refresh(reservation)
            return ReservationRead.model_validate(reservation)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao criar reserva")

    def get_reservation(self, reservation_id: int) -> ReservationRead:
        reservation = self._reservation_or_404(reservation_id)
        return ReservationRead.model_validate(reservation)

    def update_reservation(self, reservation_id: int, reservation_data: ReservationUpdate) -> ReservationRead:
        reservation = self._reservation_or_404(reservation_id)
        update_data = reservation_data.model_dump(exclude_unset=True)

        if "check_in" in update_data or "check_out" in update_data or "room_type" in update_data:
            check_in = update_data.get("check_in", reservation.check_in)
            check_out = update_data.get("check_out", reservation.check_out)
            room_type = update_data.get("room_type", reservation.room_type)
            update_data["total_price"] = self._calculate_price(room_type, check_in, check_out)

        for field, value in update_data.items():
            setattr(reservation, field, value)

        self.db.commit()
        self.db.refresh(reservation)
        return ReservationRead.model_validate(reservation)

    def check_availability(self, check_in: date, check_out: date, room_type: str | None = None) -> dict:
        if check_in >= check_out:
            raise ValueError("check_out deve ser posterior a check_in")

        room_types = list(self.ROOM_INVENTORY)
        if room_type:
            if room_type not in self.ROOM_INVENTORY:
                raise ValueError(f"room_type deve ser um dos: {list(self.ROOM_INVENTORY)}")
            room_types = [room_type]

        available_rooms = []
        for current_room_type in room_types:
            overlapping = (
                self.db.query(Reservation)
                .filter(
                    Reservation.room_type == current_room_type,
                    Reservation.status != "cancelled",
                    Reservation.check_in < check_out,
                    Reservation.check_out > check_in,
                )
                .count()
            )
            available_rooms.append(
                {
                    "type": current_room_type,
                    "count": max(self.ROOM_INVENTORY[current_room_type] - overlapping, 0),
                    "price_per_night": self.ROOM_PRICES[current_room_type],
                }
            )

        return {
            "status": "success",
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "available_rooms": available_rooms,
        }
