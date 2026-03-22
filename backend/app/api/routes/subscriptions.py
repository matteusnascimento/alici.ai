from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.billing import CurrentSubscriptionResponse
from app.services.billing_service import BillingService

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/current", response_model=CurrentSubscriptionResponse)
def subscription_current(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CurrentSubscriptionResponse:
    return BillingService(db).current_subscription(current_user)
