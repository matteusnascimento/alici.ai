from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.studio_export import StudioExport
from app.models.studio_project import StudioProject
from app.models.user import User


class StudioExportService:
    def __init__(self, db: Session):
        self.db = db

    def create_export(self, user: User, project_id: int, export_type: str, options: dict) -> StudioExport:
        project = self.db.query(StudioProject).filter(StudioProject.id == project_id, StudioProject.user_id == user.id).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=(
                "Exportacao real ainda nao esta configurada para o Studio. "
                "Nenhum arquivo foi gerado."
            ),
        )

    def list_exports(self, user: User, project_id: int | None = None) -> list[StudioExport]:
        query = self.db.query(StudioExport).filter(StudioExport.user_id == user.id)
        if project_id is not None:
            query = query.filter(StudioExport.project_id == project_id)
        return query.order_by(StudioExport.created_at.desc()).all()
