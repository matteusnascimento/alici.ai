from datetime import UTC, datetime

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

        timeline_data = {
            "tracks": [
                {
                    "id": "track-video-1",
                    "type": "video",
                    "clips": [
                        {
                            "id": "clip-generated-1",
                            "type": "video",
                            "startTime": 0,
                            "duration": payload.duration,
                            "source": payload.source_link or f"prompt:{payload.prompt or ''}",
                            "effects": [],
                            "transformations": [],
                            "text": None,
                        }
                    ],
                }
            ],
            "zoom": 1,
            "duration": payload.duration,
        }

        project = MediaProject(
            user_id=user.id,
            name=payload.project_name,
            timeline_json=timeline_data,
            duration=payload.duration,
        )
        self.db.add(project)
        self.db.flush()

        job = MediaJob(
            user_id=user.id,
            project_id=project.id,
            job_type="generate",
            status="processing",
            progress=5,
            prompt=payload.prompt,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        return MediaGenerateResponse(job_id=job.id, project_id=project.id, status=job.status)

    def get_job_status(self, user: User, job_id: int) -> MediaJobStatusResponse:
        job = self._get_job_for_user(user, job_id)
        self._update_job_progress(job)
        self.db.commit()
        self.db.refresh(job)

        return MediaJobStatusResponse(
            id=job.id,
            status=job.status,
            progress=job.progress,
            result_url=job.result_url,
            project_id=job.project_id,
        )

    def export_video(self, user: User, payload: MediaExportRequest) -> MediaExportResponse:
        project = self._get_project_for_user(user, payload.project_id)
        project.updated_at = datetime.now(UTC)

        job = MediaJob(
            user_id=user.id,
            project_id=project.id,
            job_type="export",
            status="completed",
            progress=100,
            result_url=f"https://cdn.axi.local/exports/project-{project.id}-{payload.resolution}.{payload.format}",
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)

        return MediaExportResponse(job_id=job.id, status=job.status, download_url=job.result_url or "")

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

    def _update_job_progress(self, job: MediaJob) -> None:
        if job.status == "completed":
            return

        elapsed_seconds = max(int((datetime.now(UTC) - self._as_utc(job.created_at)).total_seconds()), 0)
        progress = min(100, 10 + elapsed_seconds * 25)
        job.progress = progress

        if progress >= 100:
            job.status = "completed"
            if job.job_type == "generate":
                job.result_url = f"https://cdn.axi.local/generated/job-{job.id}.mp4"
            elif job.job_type == "export":
                job.result_url = job.result_url or f"https://cdn.axi.local/exports/job-{job.id}.mp4"
        else:
            job.status = "processing"

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
