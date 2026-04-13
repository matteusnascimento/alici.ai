from fastapi import APIRouter, Depends, HTTPException
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
    MarketingProjectUpdate,
    MarketingTool,
)
from app.services.ai_service import AIServiceError
from app.services.marketing_service import MarketingService

router = APIRouter(prefix="/marketing", tags=["marketing"])


@router.post("/campaign", response_model=MarketingCampaignResponse)
def generate_campaign(
    payload: MarketingCampaignRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingCampaignResponse:
    try:
        return MarketingService(db).generate(payload)
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc


@router.get("/tools", response_model=list[MarketingTool])
def list_tools(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[MarketingTool]:
    return MarketingService(db).list_tools()


@router.post("/generate-copy", response_model=MarketingCopyResponse)
def generate_copy(
    payload: MarketingCopyRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingCopyResponse:
    try:
        return MarketingService(db).generate_copy(payload.prompt)
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc


@router.post("/generate-image-prompt", response_model=MarketingImagePromptResponse)
def generate_image_prompt(
    payload: MarketingCopyRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingImagePromptResponse:
    try:
        return MarketingService(db).generate_image_prompt(payload.prompt)
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc


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


@router.get("/projects/{project_id}", response_model=MarketingProjectRead)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingProjectRead:
    return MarketingService(db).get_project(current_user, project_id)


@router.patch("/projects/{project_id}", response_model=MarketingProjectRead)
def update_project(
    project_id: int,
    payload: MarketingProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingProjectRead:
    return MarketingService(db).update_project(current_user, project_id, payload)


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    MarketingService(db).delete_project(current_user, project_id)


@router.post("/projects/{project_id}/generate", response_model=MarketingCampaignResponse)
def generate_for_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingCampaignResponse:
    try:
        return MarketingService(db).generate_for_project(current_user, project_id)
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc



@router.post("/campaign", response_model=MarketingCampaignResponse)
def generate_campaign(
    payload: MarketingCampaignRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingCampaignResponse:
    try:
        return MarketingService(db).generate(payload)
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc


@router.get("/tools", response_model=list[MarketingTool])
def list_tools(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[MarketingTool]:
    return MarketingService(db).list_tools()


@router.post("/generate-copy", response_model=MarketingCopyResponse)
def generate_copy(
    payload: MarketingCopyRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingCopyResponse:
    try:
        return MarketingService(db).generate_copy(payload.prompt)
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc


@router.post("/generate-image-prompt", response_model=MarketingImagePromptResponse)
def generate_image_prompt(
    payload: MarketingCopyRequest,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingImagePromptResponse:
    try:
        return MarketingService(db).generate_image_prompt(payload.prompt)
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc


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
