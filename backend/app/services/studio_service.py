from __future__ import annotations

from pathlib import PurePosixPath

from sqlalchemy.orm import Session

from app.models.studio_export import StudioExport
from app.models.studio_project import StudioProject
from app.models.user import User
from app.schemas.studio import (
    StudioOverviewResponse,
    StudioRecentExportItem,
    StudioRecentProjectItem,
)
from app.services.brand_library_service import BrandLibraryService


class StudioService:
    def __init__(self, db: Session):
        self.db = db
        self.brand_library = BrandLibraryService(db)

    def list_recent_projects(self, user: User, limit: int = 6) -> list[StudioRecentProjectItem]:
        rows = (
            self.db.query(StudioProject)
            .filter(StudioProject.user_id == user.id)
            .order_by(StudioProject.updated_at.desc())
            .limit(limit)
            .all()
        )
        return [
            StudioRecentProjectItem(
                id=item.id,
                title=item.title,
                project_type=item.project_type,
                status=item.status,
                updated_at=item.updated_at,
                thumbnail_url=item.preview_thumbnail_url,
            )
            for item in rows
        ]

    def list_recent_exports(self, user: User, limit: int = 6) -> list[StudioRecentExportItem]:
        rows = (
            self.db.query(StudioExport, StudioProject)
            .join(StudioProject, StudioProject.id == StudioExport.project_id)
            .filter(StudioExport.user_id == user.id)
            .order_by(StudioExport.created_at.desc())
            .limit(limit)
            .all()
        )
        result: list[StudioRecentExportItem] = []
        for export_item, project in rows:
            file_name = PurePosixPath(export_item.file_url).name or f"export-{export_item.id}.{export_item.export_type}"
            result.append(
                StudioRecentExportItem(
                    id=export_item.id,
                    project_id=project.id,
                    project_title=project.title,
                    file_name=file_name,
                    export_type=export_item.export_type,
                    source=project.project_type,
                    file_url=export_item.file_url,
                    created_at=export_item.created_at,
                )
            )
        return result

    def get_overview(self, user: User) -> StudioOverviewResponse:
        return StudioOverviewResponse(
            recent_projects=self.list_recent_projects(user),
            recent_exports=self.list_recent_exports(user),
            brand_summary=self.brand_library.summary(user),
            suggested_actions=[
                {
                    "id": "poster-launch",
                    "label": "Criar poster de lancamento",
                    "description": "Abra o wizard de poster e gere 3 variacoes.",
                    "route": "/app/studio/poster",
                },
                {
                    "id": "caption-campaign",
                    "label": "Gerar legenda com CTA",
                    "description": "Crie legenda, CTA e hashtags para campanha ativa.",
                    "route": "/app/studio/caption-generator",
                },
                {
                    "id": "brand-library",
                    "label": "Atualizar biblioteca da marca",
                    "description": "Suba logos, templates e assets de marca.",
                    "route": "/app/studio/brand-kit",
                },
            ],
        )
