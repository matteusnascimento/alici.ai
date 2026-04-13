from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.studio_export import StudioExport
from app.models.studio_project import StudioProject
from app.models.user import User


class StudioExportService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _storage_dir() -> Path:
        base_dir = Path(__file__).resolve().parents[2]
        path = base_dir / "exports" / "studio"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def create_export(self, user: User, project_id: int, export_type: str, options: dict) -> StudioExport:
        project = self.db.query(StudioProject).filter(StudioProject.id == project_id, StudioProject.user_id == user.id).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        stamp = int(datetime.utcnow().timestamp())
        filename = f"{project_id}_{stamp}.{export_type}"
        file_url = f"/exports/studio/{filename}"
        file_path = self._storage_dir() / filename

        placeholder = {
            "project_id": project_id,
            "project_title": project.title,
            "export_type": export_type,
            "generated_at": datetime.utcnow().isoformat(),
            "options": options or {},
        }
        file_path.write_text(json.dumps(placeholder, ensure_ascii=True), encoding="utf-8")

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
