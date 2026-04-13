from datetime import datetime

from pydantic import BaseModel


class PlanLimit(BaseModel):
    key: str
    value: int


class PlanRead(BaseModel):
    id: str
    name: str
    monthly_price: float
    yearly_price: float | None = None
    features: list[str]
    limits: list[PlanLimit]
    active: bool = True


class CurrentSubscriptionResponse(BaseModel):
    plan_id: str
    plan_name: str
    status: str
    billing_cycle: str
    monthly_price: float
    yearly_price: float | None = None
    auto_renew: bool
    cancel_at_period_end: bool = False
    started_at: datetime | None = None
    next_renewal_at: datetime | None = None
    provider: str | None = None
    stripe_customer_id: str | None = None


class UpgradeRequest(BaseModel):
    """Mantido para compatibilidade interna/administrativa. Fluxo principal usa /billing/checkout."""
    plan_id: str
    billing_cycle: str = "monthly"


class UpgradeResponse(BaseModel):
    message: str
    subscription: CurrentSubscriptionResponse


# ── Checkout Stripe ─────────────────────────────────────────
class CheckoutRequest(BaseModel):
    plan_id: str
    billing_cycle: str = "monthly"


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


# ── Portal Stripe ────────────────────────────────────────────
class PortalResponse(BaseModel):
    portal_url: str


# ── Cancel / Resume ──────────────────────────────────────────
class SubscriptionActionResponse(BaseModel):
    message: str
    subscription: CurrentSubscriptionResponse


# ── Usage ────────────────────────────────────────────────────
class BillingUsageItem(BaseModel):
    metric: str
    used: int
    limit: int


class BillingUsageResponse(BaseModel):
    items: list[BillingUsageItem]


# ── History ──────────────────────────────────────────────────
class BillingHistoryItem(BaseModel):
    id: int
    event_type: str
    amount: float
    currency: str
    description: str | None = None
    stripe_event_id: str | None = None
    status: str | None = None
    created_at: datetime


class BillingHistoryResponse(BaseModel):
    events: list[BillingHistoryItem]
