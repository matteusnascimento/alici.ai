from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from alici_api.repositories.credit_repository import InsufficientCreditsError
from alici_api.services.credit_service import CreditService


class ThreadSafeCreditRepository:
    def __init__(self):
        self.balance = 0
        self.transactions = []
        self.lock = threading.Lock()

    def get_balance(self, user_id: int) -> int:
        return self.balance

    def add_credits(self, **kwargs) -> int:
        with self.lock:
            amount = int(kwargs["amount"])
            self.balance += amount
            self.transactions.append({"amount": amount, "type": "grant", **kwargs})
            return self.balance

    def spend_credits(self, **kwargs) -> int:
        with self.lock:
            amount = int(kwargs["amount"])
            if self.balance < amount:
                raise InsufficientCreditsError(balance=self.balance, required=amount)
            self.balance -= amount
            self.transactions.append({"amount": -amount, "type": "spend", **kwargs})
            return self.balance

    def get_transaction_history(self, user_id: int, limit: int = 50):
        return list(reversed(self.transactions))[:limit]

    def transaction_exists(self, *, job_id: str, reason: str, transaction_type: str = "grant") -> bool:
        return any(
            item.get("job_id") == job_id and item.get("reason") == reason and item.get("type") == transaction_type
            for item in self.transactions
        )

    def get_price(self, **kwargs):
        return None


def test_credit_spend_is_atomic_enough_under_parallel_requests():
    repository = ThreadSafeCreditRepository()
    service = CreditService(repository=repository)
    service.add_credits(1, 100, "seed")

    with ThreadPoolExecutor(max_workers=10) as executor:
        balances = list(
            executor.map(
                lambda _: service.spend_credits(1, 7, "chat", provider="grok", model="grok-3-mini-fast"),
                range(10),
            )
        )

    assert sorted(balances) == [30, 37, 44, 51, 58, 65, 72, 79, 86, 93]
    assert service.get_balance(1) == 30
    assert len([item for item in repository.transactions if item["type"] == "spend"]) == 10


def test_refund_records_audit_metadata_and_restores_balance():
    repository = ThreadSafeCreditRepository()
    service = CreditService(repository=repository)
    service.add_credits(1, 20, "seed")
    service.spend_credits(1, 8, "chat", provider="grok", model="grok-3-mini-fast", job_id="chat-1")

    new_balance = service.refund_credits(
        1,
        8,
        "chat_failed_refund",
        provider="grok",
        model="grok-3-mini-fast",
        job_id="chat-1",
        metadata={"error": "timeout"},
    )

    assert new_balance == 20
    history = service.get_history(1)
    assert history[0]["reason"] == "chat_failed_refund"
    assert history[0]["metadata"]["refund"] is True
    assert history[0]["metadata"]["error"] == "timeout"


def test_spend_rejects_insufficient_credits_without_negative_balance():
    repository = ThreadSafeCreditRepository()
    service = CreditService(repository=repository)
    service.add_credits(1, 3, "seed")

    with pytest.raises(InsufficientCreditsError) as exc:
        service.spend_credits(1, 5, "video")

    assert exc.value.balance == 3
    assert exc.value.required == 5
    assert service.get_balance(1) == 3
