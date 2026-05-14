"""Credit business service."""

from __future__ import annotations

from typing import Any

from alici_api.config import get_settings
from alici_api.repositories.credit_repository import CreditRepository, InsufficientCreditsError
from logger import get_logger


logger_credit = get_logger("credit_service")


class CreditService:
    def __init__(self, repository: CreditRepository | None = None):
        self.repository = repository or CreditRepository()
        self.settings = get_settings()

    def get_balance(self, user_id: int) -> int:
        return self.repository.get_balance(user_id)

    def spend_credits(
        self,
        user_id: int,
        amount: int,
        reason: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        job_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        new_balance = self.repository.spend_credits(
            user_id=user_id,
            amount=amount,
            reason=reason,
            provider=provider,
            model=model,
            job_id=job_id,
            metadata=metadata,
        )
        logger_credit.info(
            "credit_spend",
            extra={
                "user_id": user_id,
                "amount": amount,
                "reason": reason,
                "provider": provider,
                "model": model,
                "job_id": job_id,
                "new_balance": new_balance,
            },
        )
        return new_balance

    def add_credits(
        self,
        user_id: int,
        amount: int,
        reason: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        job_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        new_balance = self.repository.add_credits(
            user_id=user_id,
            amount=amount,
            reason=reason,
            provider=provider,
            model=model,
            job_id=job_id,
            metadata=metadata,
        )
        logger_credit.info(
            "credit_add",
            extra={
                "user_id": user_id,
                "amount": amount,
                "reason": reason,
                "provider": provider,
                "model": model,
                "job_id": job_id,
                "new_balance": new_balance,
            },
        )
        return new_balance

    def refund_credits(
        self,
        user_id: int,
        amount: int,
        reason: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        job_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        refund_metadata = {"refund": True, **(metadata or {})}
        return self.add_credits(
            user_id=user_id,
            amount=amount,
            reason=reason,
            provider=provider,
            model=model,
            job_id=job_id,
            metadata=refund_metadata,
        )

    def get_history(self, user_id: int, limit: int = 50) -> list[dict[str, Any]]:
        return self.repository.get_transaction_history(user_id=user_id, limit=limit)

    def calculate_cost(
        self,
        *,
        job_type: str,
        model: str,
        provider: str | None = None,
        resolution: str | None = None,
        duration_seconds: int | None = None,
    ) -> int:
        configured_price = self.repository.get_price(
            job_type=job_type,
            provider=provider,
            model=model,
            resolution=resolution,
            duration_seconds=duration_seconds,
        )
        if configured_price is not None:
            return configured_price

        defaults = {
            "chat": self.settings.credits_chat_default_cost,
            "code": self.settings.credits_chat_default_cost,
            "image": self.settings.credits_image_default_cost,
            "audio": self.settings.credits_audio_default_cost,
            "video": self.settings.credits_video_default_cost,
        }
        fallback_cost = int(defaults.get(job_type, self.settings.credits_chat_default_cost))
        logger_credit.info(
            "credit_price_fallback",
            extra={
                "job_type": job_type,
                "provider": provider,
                "model": model,
                "resolution": resolution,
                "duration_seconds": duration_seconds,
                "fallback_cost": fallback_cost,
            },
        )
        return fallback_cost


__all__ = ["CreditService", "InsufficientCreditsError"]
