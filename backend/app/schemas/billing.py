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
    started_at: datetime | None = None


class UpgradeRequest(BaseModel):
    plan_id: str
    billing_cycle: str = "monthly"


class UpgradeResponse(BaseModel):
    message: str
    subscription: CurrentSubscriptionResponse


class BillingUsageItem(BaseModel):
    metric: str
    used: int
    limit: int


class BillingUsageResponse(BaseModel):
    items: list[BillingUsageItem]


class BillingHistoryItem(BaseModel):
    id: int
    event_type: str
    amount: float
    currency: str
    description: str | None = None
    created_at: datetime


class BillingHistoryResponse(BaseModel):
    events: list[BillingHistoryItem]
