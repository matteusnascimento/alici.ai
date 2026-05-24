from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.studio_asset import StudioAsset
from app.models.user import User


class StudioAssetService:
    MAX_UPLOAD_BYTES = 25 * 1024 * 1024
    ALLOWED_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".mp4",
        ".mov",
        ".mp3",
        ".wav",
        ".pdf",
        ".txt",
        ".csv",
        ".json",
    }
    ALLOWED_CONTENT_TYPES = {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "video/mp4",
        "video/quicktime",
        "audio/mpeg",
        "audio/wav",
        "application/pdf",
        "text/plain",
        "text/csv",
        "application/json",
        "application/octet-stream",
    }

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
        name = Path(filename or "asset").name.strip() or "asset"
        stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", Path(name).stem).strip("._-") or "asset"
        ext = Path(name).suffix.lower()
        return f"{stem}{ext}"

    @classmethod
    def _build_local_asset_url(cls, filename: str) -> str:
        stamp = int(datetime.utcnow().timestamp())
        safe = cls._safe_name(filename)
        return f"/uploads/studio/{stamp}_{uuid4().hex}_{safe}"

    @classmethod
    def _validate_upload(cls, *, name: str, content: bytes, content_type: str | None) -> None:
        ext = Path(name or "").suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de asset nao permitido")
        if content_type and content_type not in cls.ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Content-Type de asset nao permitido")
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo vazio")
        if len(content) > cls.MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Asset excede 25MB")

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
        self._validate_upload(name=name, content=content, content_type=content_type)
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
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Criacao de asset sem upload real nao esta disponivel.",
        )

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
            storage_dir = self._storage_dir().resolve()
            file_path = (storage_dir / asset.file_url.replace("/uploads/studio/", "")).resolve()
            try:
                file_path.relative_to(storage_dir)
            except ValueError as exc:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Asset path invalido") from exc
            if file_path.exists() and file_path.is_file():
                file_path.unlink(missing_ok=True)

        self.db.delete(asset)
        self.db.commit()
        return True
