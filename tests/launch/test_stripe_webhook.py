from __future__ import annotations

import alici_api.services.billing_service as billing_module
from alici_api.services.billing_service import BillingService


class FakeCreditService:
    def __init__(self, duplicate: bool = False):
        self.duplicate = duplicate
        self.grants = []

    def transaction_exists(self, *, job_id, reason, transaction_type="grant"):
        return self.duplicate and job_id == "in_123" and reason == "stripe_invoice_payment_succeeded"

    def add_credits(self, **kwargs):
        self.grants.append(kwargs)
        return 1000


def test_stripe_invoice_payment_grants_credits_once_per_invoice(monkeypatch):
    credit_service = FakeCreditService(duplicate=False)
    service = BillingService(credit_service=credit_service)

    monkeypatch.setattr(
        billing_module.stripe.Subscription,
        "retrieve",
        lambda subscription_id, expand=None: {
            "id": subscription_id,
            "customer": "cus_123",
            "status": "active",
            "metadata": {"user_id": "42", "plan": "pro", "price_id": "price_pro"},
            "items": {"data": [{"price": {"id": "price_pro"}}]},
            "current_period_end": 2_000_000_000,
        },
    )
    monkeypatch.setattr(billing_module, "salvar_assinatura_usuario", lambda *args, **kwargs: None)
    monkeypatch.setattr(service, "plan_credits", lambda plan: 500)

    service._handle_invoice_payment_succeeded({"id": "in_123", "subscription": "sub_123"}, "evt_1")

    assert len(credit_service.grants) == 1
    assert credit_service.grants[0]["user_id"] == 42
    assert credit_service.grants[0]["amount"] == 500
    assert credit_service.grants[0]["job_id"] == "in_123"
    assert credit_service.grants[0]["metadata"]["stripe_event_id"] == "evt_1"


def test_stripe_invoice_idempotency_skips_duplicate_grant(monkeypatch):
    credit_service = FakeCreditService(duplicate=True)
    service = BillingService(credit_service=credit_service)
    called = {"retrieve": False}

    def fail_if_called(*args, **kwargs):
        called["retrieve"] = True
        raise AssertionError("subscription retrieval should be skipped for duplicate invoice")

    monkeypatch.setattr(billing_module.stripe.Subscription, "retrieve", fail_if_called)

    service._handle_invoice_payment_succeeded({"id": "in_123", "subscription": "sub_123"}, "evt_2")

    assert credit_service.grants == []
    assert called["retrieve"] is False
