from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.studio_asset import StudioAsset
from app.models.user import User


class StudioAssetService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _storage_dir() -> Path:
        base_dir = Path(__file__).resolve().parents[2]
        path = base_dir / "uploads" / "studio"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _safe_name(filename: str) -> str:
        return Path(filename).name.replace(" ", "_")

    @classmethod
    def _build_local_asset_url(cls, filename: str) -> str:
        stamp = int(datetime.utcnow().timestamp())
        safe = cls._safe_name(filename)
        return f"/uploads/studio/{stamp}_{safe}"

    def create_asset_from_upload(
        self,
        user: User,
        *,
        name: str,
        content: bytes,
        content_type: str | None,
        asset_type: str,
        project_id: int | None,
        metadata: dict[str, Any] | None = None,
    ) -> StudioAsset:
        url = self._build_local_asset_url(name)
        relative = url.replace("/uploads/studio/", "")
        path = self._storage_dir() / relative
        path.write_bytes(content)

        payload = {
            **(metadata or {}),
            "storage": f"uploads/studio/{relative}",
            "content_type": content_type,
            "size_bytes": len(content),
        }

        asset = StudioAsset(
            user_id=user.id,
            project_id=project_id,
            asset_type=asset_type,
            name=name,
            file_url=url,
            metadata_json=json.dumps(payload, ensure_ascii=True),
        )
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def create_asset(self, user: User, *, name: str, asset_type: str, project_id: int | None, metadata: dict[str, Any] | None = None) -> StudioAsset:
        asset = StudioAsset(
            user_id=user.id,
            project_id=project_id,
            asset_type=asset_type,
            name=name,
            file_url=self._build_local_asset_url(name),
            metadata_json=json.dumps(metadata or {}, ensure_ascii=True),
        )
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def list_assets(self, user: User) -> list[StudioAsset]:
        return (
            self.db.query(StudioAsset)
            .filter(StudioAsset.user_id == user.id)
            .order_by(StudioAsset.created_at.desc())
            .all()
        )

    def delete_asset(self, user: User, asset_id: int) -> bool:
        asset = self.db.query(StudioAsset).filter(StudioAsset.id == asset_id, StudioAsset.user_id == user.id).first()
        if not asset:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found")

        if asset.file_url and asset.file_url.startswith("/uploads/studio/"):
            file_path = self._storage_dir() / asset.file_url.replace("/uploads/studio/", "")
            if file_path.exists() and file_path.is_file():
                file_path.unlink(missing_ok=True)

        self.db.delete(asset)
        self.db.commit()
        return True
