from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.billing import BillingUsageResponse
from app.services.billing_service import BillingService

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("", response_model=BillingUsageResponse)
def usage_current(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> BillingUsageResponse:
    return BillingService(db).usage(current_user)
