from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.marketing import (
    MarketingCampaignRequest,
    MarketingCampaignResponse,
    MarketingCopyRequest,
    MarketingCopyResponse,
    MarketingImagePromptResponse,
    MarketingProjectCreate,
    MarketingProjectRead,
    MarketingTool,
)
from app.services.marketing_service import MarketingService

router = APIRouter(prefix="/marketing", tags=["marketing"])


@router.post("/campaign", response_model=MarketingCampaignResponse)
def generate_campaign(
    payload: MarketingCampaignRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingCampaignResponse:
    return MarketingService(db).generate(payload)


@router.get("/tools", response_model=list[MarketingTool])
def list_tools(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[MarketingTool]:
    return MarketingService(db).list_tools()


@router.post("/generate-copy", response_model=MarketingCopyResponse)
def generate_copy(
    payload: MarketingCopyRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingCopyResponse:
    return MarketingService(db).generate_copy(payload.prompt)


@router.post("/generate-image-prompt", response_model=MarketingImagePromptResponse)
def generate_image_prompt(
    payload: MarketingCopyRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingImagePromptResponse:
    return MarketingService(db).generate_image_prompt(payload.prompt)


@router.post("/projects", response_model=MarketingProjectRead)
def create_project(
    payload: MarketingProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingProjectRead:
    return MarketingService(db).create_project(current_user, payload)


@router.get("/projects", response_model=list[MarketingProjectRead])
def list_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[MarketingProjectRead]:
    return MarketingService(db).list_projects(current_user)
