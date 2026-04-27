from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.studio import (
    StudioBackgroundRemoveRequest,
    StudioGenerateResponse,
    StudioPhotoEditRequest,
    StudioProjectCreate,
    StudioToolActionResponse,
)
from app.services.studio_generation_service import StudioGenerationService
from app.services.studio_image_service import StudioImageService
from app.services.studio_project_service import StudioProjectService


class MediaProcessingService:
    def __init__(self, db: Session):
        self.db = db
        self.projects = StudioProjectService(db)
        self.generation = StudioGenerationService(db)

    def _ensure_project(self, user: User, project_id: int | None, project_type: str, title: str):
        if project_id:
            return self.projects.get_project(user, project_id)
        return self.projects.create_project(
            user,
            StudioProjectCreate(
                project_type=project_type,
                title=title,
                metadata={"source": "studio-action"},
                canvas_data={},
                layers=[],
                timeline_data={},
                export_settings={"format": "png"},
            ),
        )

    def _project_read(self, project):
        from app.api.routes.studio import _project_read

        return _project_read(project)

    def edit_photo(self, user: User, payload: StudioPhotoEditRequest) -> StudioToolActionResponse:
        result = StudioImageService.enhance(payload.asset_url, payload.adjustments)
        project = self._ensure_project(user, payload.project_id, "photo-edit", "Edicao de Foto")
        result["actions"] = payload.actions
        created = self.generation.create_generation(
            user_id=user.id,
            project_id=project.id,
            generation_type="photo-edit",
            prompt="photo-edit",
            input_payload=payload.model_dump(),
            result_payload=result,
        )
        generation = StudioGenerateResponse(generation_id=created.id, status=created.status, result=result)
        return StudioToolActionResponse(project=self._project_read(project), generation=generation, message="Edicao de foto processada com sucesso.")

    def remove_background(self, user: User, payload: StudioBackgroundRemoveRequest) -> StudioToolActionResponse:
        result = StudioImageService.remove_background(payload.asset_url, payload.options)
        project = self._ensure_project(user, payload.project_id, "background-remove", "Remocao de Fundo")
        result["before_after_preview"] = True
        created = self.generation.create_generation(
            user_id=user.id,
            project_id=project.id,
            generation_type="background-remove",
            prompt="background-remove",
            input_payload=payload.model_dump(),
            result_payload=result,
        )
        generation = StudioGenerateResponse(generation_id=created.id, status=created.status, result=result)
        return StudioToolActionResponse(project=self._project_read(project), generation=generation, message="Fundo removido. Preview before/after disponivel para download e salvamento.")
