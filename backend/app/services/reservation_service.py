from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import uuid

from app.models.reservation import Reservation
from app.schemas.reservation import ReservationCreate, ReservationRead, ReservationUpdate


class ReservationService:
    def __init__(self, db: Session):
        self.db = db

    def _reservation_or_404(self, reservation_id: int) -> Reservation:
        """Busca reserva por ID ou lança 404."""
        reservation = self.db.query(Reservation).filter(Reservation.id == reservation_id).first()
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva não encontrada",
            )
        return reservation

    def _generate_reservation_id(self) -> str:
        """Gera ID único para reserva."""
        return f"RES-{date.today().year}-{uuid.uuid4().hex[:3].upper()}"

    def _calculate_price(self, room_type: str, check_in: date, check_out: date) -> float:
        """Calcula preço baseado no tipo de quarto e período."""
        room_prices = {
            "standard": 150.0,
            "deluxe": 250.0,
            "suite": 400.0,
        }
        price_per_night = room_prices.get(room_type, 150.0)
        nights = (check_out - check_in).days
        return price_per_night * nights

    def create_reservation(self, reservation_data: ReservationCreate) -> ReservationRead:
        """Cria uma nova reserva."""
        # Valida datas
        if reservation_data.check_in >= reservation_data.check_out:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data de check-out deve ser posterior à data de check-in",
            )

        # Calcula preço
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao criar reserva",
            )

    def get_reservation(self, reservation_id: int) -> ReservationRead:
        """Busca reserva por ID."""
        reservation = self._reservation_or_404(reservation_id)
        return ReservationRead.model_validate(reservation)

    def update_reservation(self, reservation_id: int, reservation_data: ReservationUpdate) -> ReservationRead:
        """Atualiza reserva."""
        reservation = self._reservation_or_404(reservation_id)
        update_data = reservation_data.model_dump(exclude_unset=True)

        # Recalcula preço se datas ou tipo de quarto mudaram
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
        """Verifica disponibilidade de quartos."""
        # Por simplicidade, retorna disponibilidade mock
        # Em produção, isso consultaria o banco de reservas
        available_rooms = [
            {"type": "standard", "count": 5, "price_per_night": 150.0},
            {"type": "deluxe", "count": 3, "price_per_night": 250.0},
            {"type": "suite", "count": 1, "price_per_night": 400.0},
        ]

        if room_type:
            available_rooms = [r for r in available_rooms if r["type"] == room_type]

        return {
            "status": "success",
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "available_rooms": available_rooms,
        }