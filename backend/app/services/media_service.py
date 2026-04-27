from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.media_job import MediaJob
from app.models.media_project import MediaProject
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


class MediaService:
    def __init__(self, db: Session):
        self.db = db

    def generate_video(self, user: User, payload: MediaGenerateRequest) -> MediaGenerateResponse:
        self._validate_generation_payload(payload)
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Geracao real de video ainda nao esta configurada.",
        )

    def get_job_status(self, user: User, job_id: int) -> MediaJobStatusResponse:
        job = self._get_job_for_user(user, job_id)
        return MediaJobStatusResponse(
            id=job.id,
            status=job.status,
            progress=job.progress,
            result_url=job.result_url,
            project_id=job.project_id,
        )

    def export_video(self, user: User, payload: MediaExportRequest) -> MediaExportResponse:
        self._get_project_for_user(user, payload.project_id)
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Exportacao real de video ainda nao esta configurada.",
        )

    def create_project(self, user: User, payload: MediaProjectCreate) -> MediaProjectRead:
        project = MediaProject(
            user_id=user.id,
            name=payload.name,
            timeline_json=payload.timeline_data,
            thumbnail=payload.thumbnail,
            duration=payload.duration,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return self._serialize_project(project)

    def list_projects(self, user: User) -> list[MediaProjectRead]:
        projects = (
            self.db.query(MediaProject)
            .filter(MediaProject.user_id == user.id)
            .order_by(MediaProject.updated_at.desc())
            .all()
        )
        return [self._serialize_project(item) for item in projects]

    def get_project(self, user: User, project_id: int) -> MediaProjectRead:
        project = self._get_project_for_user(user, project_id)
        return self._serialize_project(project)

    def update_project(self, user: User, project_id: int, payload: MediaProjectUpdate) -> MediaProjectRead:
        project = self._get_project_for_user(user, project_id)
        data = payload.model_dump(exclude_none=True)

        if "timeline_data" in data:
            project.timeline_json = data["timeline_data"]
        if "name" in data:
            project.name = str(data["name"])
        if "thumbnail" in data:
            project.thumbnail = data["thumbnail"]
        if "duration" in data:
            project.duration = int(data["duration"])

        project.updated_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(project)
        return self._serialize_project(project)

    def duplicate_project(self, user: User, project_id: int) -> MediaProjectRead:
        source = self._get_project_for_user(user, project_id)
        duplicate = MediaProject(
            user_id=user.id,
            name=f"{source.name} (copia)",
            timeline_json=source.timeline_json,
            thumbnail=source.thumbnail,
            duration=source.duration,
        )
        self.db.add(duplicate)
        self.db.commit()
        self.db.refresh(duplicate)
        return self._serialize_project(duplicate)

    def _serialize_project(self, project: MediaProject) -> MediaProjectRead:
        return MediaProjectRead(
            id=project.id,
            user_id=project.user_id,
            name=project.name,
            timeline_data=project.timeline_json or {},
            thumbnail=project.thumbnail,
            duration=project.duration,
            created_at=self._as_utc(project.created_at).isoformat(),
            updated_at=self._as_utc(project.updated_at).isoformat(),
        )

    def _get_job_for_user(self, user: User, job_id: int) -> MediaJob:
        job = self.db.query(MediaJob).filter(MediaJob.id == job_id, MediaJob.user_id == user.id).first()
        if not job:
            raise ValueError("Job nao encontrado")
        return job

    def _get_project_for_user(self, user: User, project_id: int) -> MediaProject:
        project = self.db.query(MediaProject).filter(MediaProject.id == project_id, MediaProject.user_id == user.id).first()
        if not project:
            raise ValueError("Projeto nao encontrado")
        return project

    def _validate_generation_payload(self, payload: MediaGenerateRequest) -> None:
        if payload.mode == "prompt" and not (payload.prompt or "").strip():
            raise ValueError("Informe um prompt para gerar o video")
        if payload.mode == "link" and not (payload.source_link or "").strip():
            raise ValueError("Informe um link de origem")
        if payload.mode == "media" and not payload.uploads:
            raise ValueError("Adicione ao menos um arquivo de midia")
        if payload.duration <= 0:
            raise ValueError("Duracao invalida")

    def _as_utc(self, value: datetime | None) -> datetime:
        if value is None:
            return datetime.now(UTC)
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
