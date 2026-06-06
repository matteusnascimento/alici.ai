from datetime import date
import hashlib
import uuid

from fastapi import HTTPException, status
from sqlalchemy import and_, or_
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

    @staticmethod
    def _clean(value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @staticmethod
    def _clean_lower(value: str | None) -> str:
        return (value or "").strip().lower()

    def _identity_hash(self, payload: ReservationCreate, total_price: float) -> str:
        parts = [
            self._clean_lower(payload.external_reservation_id or payload.reservation_id),
            self._clean_lower(payload.reservation_number),
            self._clean_lower(payload.guest_document),
            self._clean_lower(payload.guest_email),
            payload.check_in.isoformat(),
            payload.check_out.isoformat(),
            f"{float(total_price):.2f}",
            self._clean_lower(payload.source_provider or payload.channel or payload.source),
        ]
        return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()

    def _find_duplicate(self, payload: ReservationCreate, total_price: float, identity_hash: str) -> Reservation | None:
        external_ids = [
            self._clean(payload.external_reservation_id),
            self._clean(payload.reservation_id),
            self._clean(payload.reservation_number),
        ]
        external_ids = [item for item in external_ids if item]
        duplicate = self.db.query(Reservation).filter(Reservation.reservation_identity_hash == identity_hash).first()
        if duplicate:
            return duplicate
        if external_ids:
            duplicate = (
                self.db.query(Reservation)
                .filter(
                    or_(
                        Reservation.external_reservation_id.in_(external_ids),
                        Reservation.reservation_id.in_(external_ids),
                        Reservation.reservation_number.in_(external_ids),
                    )
                )
                .first()
            )
            if duplicate:
                return duplicate

        document = self._clean(payload.guest_document)
        email = self._clean(payload.guest_email)
        source_provider = self._clean(payload.source_provider or payload.channel)
        guest_conditions = []
        if document:
            guest_conditions.append(Reservation.guest_document == document)
        if email:
            guest_conditions.append(Reservation.guest_email == email)
        if guest_conditions and source_provider:
            return (
                self.db.query(Reservation)
                .filter(
                    and_(
                        or_(*guest_conditions),
                        Reservation.check_in == payload.check_in,
                        Reservation.check_out == payload.check_out,
                        Reservation.total_price == total_price,
                        or_(Reservation.source_provider == source_provider, Reservation.channel == source_provider),
                    )
                )
                .first()
            )
        return None

    def _merge_duplicate(self, reservation: Reservation, payload: ReservationCreate, total_price: float, identity_hash: str) -> ReservationRead:
        update_data = payload.model_dump(exclude_unset=True, exclude={"total_amount"})
        update_data["total_price"] = total_price
        update_data["reservation_identity_hash"] = identity_hash
        if payload.external_reservation_id and not reservation.external_reservation_id:
            reservation.external_reservation_id = payload.external_reservation_id
        if payload.reservation_id and reservation.reservation_id.startswith("RES-"):
            reservation.reservation_id = payload.reservation_id
        for field, value in update_data.items():
            if field == "reservation_id" and not value:
                continue
            if value is not None:
                setattr(reservation, field, value)
        self.db.commit()
        self.db.refresh(reservation)
        return ReservationRead.model_validate(reservation)

    def create_reservation(self, reservation_data: ReservationCreate) -> ReservationRead:
        if reservation_data.check_in >= reservation_data.check_out:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data de check-out deve ser posterior a data de check-in",
            )

        total_price = reservation_data.total_amount if reservation_data.total_amount is not None else reservation_data.total_price
        total_price = total_price if total_price is not None else self._calculate_price(
            reservation_data.room_type,
            reservation_data.check_in,
            reservation_data.check_out,
        )
        identity_hash = self._identity_hash(reservation_data, total_price)
        duplicate = self._find_duplicate(reservation_data, total_price, identity_hash)
        if duplicate:
            return self._merge_duplicate(duplicate, reservation_data, total_price, identity_hash)

        payload = reservation_data.model_dump(exclude={"reservation_id", "total_price", "total_amount"})

        reservation = Reservation(
            reservation_id=reservation_data.reservation_id or reservation_data.external_reservation_id or self._generate_reservation_id(),
            **payload,
            total_price=total_price,
            reservation_identity_hash=identity_hash,
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
        if "total_amount" in update_data:
            update_data["total_price"] = update_data.pop("total_amount")

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
