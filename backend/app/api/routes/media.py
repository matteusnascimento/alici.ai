from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.media import (
    MediaExportRequest,
    MediaExportResponse,
    MediaGenerateRequest,
    MediaGenerateResponse,
    MediaJobStatusResponse,
    MediaProjectCreate,
    MediaProjectRead,
    MediaProjectUpdate,
)
from app.services.media_service import MediaService

router = APIRouter(prefix="/media", tags=["media"])


@router.post("/generate", response_model=MediaGenerateResponse)
def generate_video(
    payload: MediaGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MediaGenerateResponse:
    service = MediaService(db)
    try:
        return service.generate_video(current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/status/{job_id}", response_model=MediaJobStatusResponse)
def get_generation_status(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MediaJobStatusResponse:
    service = MediaService(db)
    try:
        return service.get_job_status(current_user, job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/export", response_model=MediaExportResponse)
def export_video(
    payload: MediaExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MediaExportResponse:
    service = MediaService(db)
    try:
        return service.export_video(current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/projects", response_model=list[MediaProjectRead])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MediaProjectRead]:
    return MediaService(db).list_projects(current_user)


@router.post("/projects", response_model=MediaProjectRead)
def create_project(
    payload: MediaProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MediaProjectRead:
    return MediaService(db).create_project(current_user, payload)


@router.get("/project/{project_id}", response_model=MediaProjectRead)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MediaProjectRead:
    service = MediaService(db)
    try:
        return service.get_project(current_user, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/project/{project_id}", response_model=MediaProjectRead)
def update_project(
    project_id: int,
    payload: MediaProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MediaProjectRead:
    service = MediaService(db)
    try:
        return service.update_project(current_user, project_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/project/{project_id}/duplicate", response_model=MediaProjectRead)
def duplicate_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MediaProjectRead:
    service = MediaService(db)
    try:
        return service.duplicate_project(current_user, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
