from __future__ import annotations

import json
from datetime import datetime

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

        stamp = int(datetime.utcnow().timestamp())
        file_url = f"/exports/studio/{project_id}_{stamp}.{export_type}"

        item = StudioExport(
            user_id=user.id,
            project_id=project_id,
            export_type=export_type,
            file_url=file_url,
            status="ready",
            metadata_json=json.dumps(options or {}, ensure_ascii=True),
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list_exports(self, user: User, project_id: int | None = None) -> list[StudioExport]:
        query = self.db.query(StudioExport).filter(StudioExport.user_id == user.id)
        if project_id is not None:
            query = query.filter(StudioExport.project_id == project_id)
        return query.order_by(StudioExport.created_at.desc()).all()
