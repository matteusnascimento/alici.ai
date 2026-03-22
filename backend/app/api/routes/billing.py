from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.billing import (
    BillingHistoryResponse,
    BillingUsageResponse,
    CurrentSubscriptionResponse,
    PlanRead,
    UpgradeRequest,
    UpgradeResponse,
)
from app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/plans", response_model=list[PlanRead])
def billing_plans(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[PlanRead]:
    return BillingService(db).list_plans()


@router.get("/current", response_model=CurrentSubscriptionResponse)
def billing_current(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CurrentSubscriptionResponse:
    return BillingService(db).current_subscription(current_user)


@router.post("/upgrade", response_model=UpgradeResponse)
def billing_upgrade(
    payload: UpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UpgradeResponse:
    return BillingService(db).upgrade(current_user, payload)


@router.get("/usage", response_model=BillingUsageResponse)
def billing_usage(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> BillingUsageResponse:
    return BillingService(db).usage(current_user)


@router.get("/history", response_model=BillingHistoryResponse)
def billing_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> BillingHistoryResponse:
    return BillingService(db).history(current_user)
