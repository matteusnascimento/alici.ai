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
    def _build_local_asset_url(filename: str) -> str:
        stamp = int(datetime.utcnow().timestamp())
        safe = Path(filename).name.replace(" ", "_")
        return f"/uploads/studio/{stamp}_{safe}"

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
        self.db.delete(asset)
        self.db.commit()
        return True
