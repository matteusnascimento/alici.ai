from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.marketing import MarketingCampaignRequest, MarketingCampaignResponse
from app.services.marketing_service import MarketingService

router = APIRouter(prefix="/marketing", tags=["marketing"])


@router.post("/campaign", response_model=MarketingCampaignResponse)
def generate_campaign(
    payload: MarketingCampaignRequest,
    _: User = Depends(get_current_user),
) -> MarketingCampaignResponse:
    return MarketingService().generate(payload)
