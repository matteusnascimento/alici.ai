from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.studio_project import StudioProject
from app.models.studio_version import StudioVersion
from app.models.user import User
from app.schemas.studio import StudioProjectCreate, StudioProjectUpdate, StudioVersionCreate


class StudioProjectService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _loads_dict(value: str | None) -> dict[str, Any]:
        if not value:
            return {}
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
            return {}
        except Exception:
            return {}

    @staticmethod
    def _loads_list(value: str | None) -> list[dict[str, Any]]:
        if not value:
            return []
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [item for item in parsed if isinstance(item, dict)]
            return []
        except Exception:
            return []

    def list_projects(self, user: User) -> list[StudioProject]:
        return (
            self.db.query(StudioProject)
            .filter(StudioProject.user_id == user.id)
            .order_by(StudioProject.updated_at.desc())
            .all()
        )

    def create_project(self, user: User, payload: StudioProjectCreate) -> StudioProject:
        project = StudioProject(
            user_id=user.id,
            project_type=payload.project_type,
            title=payload.title,
            status="draft",
            metadata_json=json.dumps(payload.metadata, ensure_ascii=True),
            canvas_data_json=json.dumps(payload.canvas_data, ensure_ascii=True),
            layers_json=json.dumps(payload.layers, ensure_ascii=True),
            timeline_data_json=json.dumps(payload.timeline_data, ensure_ascii=True),
            export_settings_json=json.dumps(payload.export_settings, ensure_ascii=True),
            preview_thumbnail_url=payload.preview_thumbnail_url,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_project(self, user: User, project_id: int) -> StudioProject:
        item = self.db.query(StudioProject).filter(StudioProject.id == project_id, StudioProject.user_id == user.id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Studio project not found")
        return item

    def update_project(self, user: User, project_id: int, payload: StudioProjectUpdate) -> StudioProject:
        item = self.get_project(user, project_id)
        data = payload.model_dump(exclude_unset=True)

        if "metadata" in data:
            item.metadata_json = json.dumps(data.pop("metadata") or {}, ensure_ascii=True)
        if "canvas_data" in data:
            item.canvas_data_json = json.dumps(data.pop("canvas_data") or {}, ensure_ascii=True)
        if "layers" in data:
            item.layers_json = json.dumps(data.pop("layers") or [], ensure_ascii=True)
        if "timeline_data" in data:
            item.timeline_data_json = json.dumps(data.pop("timeline_data") or {}, ensure_ascii=True)
        if "export_settings" in data:
            item.export_settings_json = json.dumps(data.pop("export_settings") or {}, ensure_ascii=True)

        for key, value in data.items():
            setattr(item, key, value)

        self.db.commit()
        self.db.refresh(item)
        return item

    def duplicate_project(self, user: User, project_id: int) -> StudioProject:
        base = self.get_project(user, project_id)
        copy = StudioProject(
            user_id=user.id,
            project_type=base.project_type,
            title=f"{base.title} (copia)",
            status="draft",
            metadata_json=base.metadata_json,
            canvas_data_json=base.canvas_data_json,
            layers_json=base.layers_json,
            timeline_data_json=base.timeline_data_json,
            export_settings_json=base.export_settings_json,
            preview_thumbnail_url=base.preview_thumbnail_url,
        )
        self.db.add(copy)
        self.db.commit()
        self.db.refresh(copy)
        return copy

    def save_project(self, user: User, project_id: int, payload: StudioProjectUpdate | None = None) -> StudioProject:
        if payload is None:
            payload = StudioProjectUpdate(status="saved")
        item = self.update_project(user, project_id, payload)
        if item.status == "draft":
            item.status = "saved"
            self.db.commit()
            self.db.refresh(item)
        return item

    def create_version(self, user: User, project_id: int, payload: StudioVersionCreate) -> StudioVersion:
        self.get_project(user, project_id)
        version = StudioVersion(
            user_id=user.id,
            project_id=project_id,
            label=payload.label,
            canvas_data_json=json.dumps(payload.canvas_data, ensure_ascii=True),
            layers_json=json.dumps(payload.layers, ensure_ascii=True),
            timeline_data_json=json.dumps(payload.timeline_data, ensure_ascii=True),
        )
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def list_versions(self, user: User, project_id: int) -> list[StudioVersion]:
        self.get_project(user, project_id)
        return (
            self.db.query(StudioVersion)
            .filter(StudioVersion.user_id == user.id, StudioVersion.project_id == project_id)
            .order_by(StudioVersion.created_at.desc())
            .all()
        )
