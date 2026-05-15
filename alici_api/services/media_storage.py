"""Persistent storage for media files.

Cloudflare R2 exposes an S3-compatible API, so boto3 is imported lazily only
when media providers or upload flows need persistent assets.
"""

from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

import httpx

from alici_api.config import get_settings


class MediaStorageError(RuntimeError):
    pass


@dataclass(frozen=True)
class StoredMedia:
    key: str
    url: str
    content_type: str
    size_bytes: int


class R2MediaStorage:
    def __init__(self):
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return not self.missing_config()

    def missing_config(self) -> list[str]:
        missing = []
        if not self.settings.r2_endpoint_url:
            missing.append("R2_ENDPOINT_URL")
        if not self.settings.r2_access_key_id:
            missing.append("R2_ACCESS_KEY_ID")
        if not self.settings.r2_secret_access_key:
            missing.append("R2_SECRET_ACCESS_KEY")
        if not self.settings.r2_bucket_uploads:
            missing.append("R2_BUCKET_UPLOADS")
        if not self.settings.r2_public_base_url:
            missing.append("R2_PUBLIC_BASE_URL")
        return missing

    def _require_config(self) -> None:
        missing = self.missing_config()
        if missing:
            raise MediaStorageError(f"Storage R2 incompleto. Configure: {', '.join(missing)}")

    def _client(self):
        self._require_config()
        import boto3
        from botocore.config import Config

        return boto3.client(
            "s3",
            endpoint_url=self.settings.r2_endpoint_url,
            aws_access_key_id=self.settings.r2_access_key_id,
            aws_secret_access_key=self.settings.r2_secret_access_key.get_secret_value(),
            region_name="auto",
            config=Config(
                connect_timeout=3,
                read_timeout=10,
                retries={"max_attempts": 2, "mode": "standard"},
                signature_version="s3v4",
            ),
        )

    def status(self, *, include_probe: bool = False) -> dict[str, Any]:
        missing = self.missing_config()
        payload: dict[str, Any] = {
            "configured": not missing,
            "missing": missing,
            "bucket": self.settings.r2_bucket_uploads if not missing else None,
            "public_base_url_configured": bool(self.settings.r2_public_base_url),
            "probe_ok": None,
        }
        if include_probe and not missing:
            try:
                self._client().head_bucket(Bucket=self.settings.r2_bucket_uploads)
                payload["probe_ok"] = True
            except Exception as exc:
                payload["probe_ok"] = False
                payload["error"] = str(exc)
        return payload

    def _public_url(self, key: str) -> str:
        base_url = str(self.settings.r2_public_base_url or "").rstrip("/")
        return f"{base_url}/{key.lstrip('/')}"

    def _key(self, *, folder: str, filename: str) -> str:
        safe_folder = "/".join(part.strip("/").replace("..", "") for part in folder.split("/") if part.strip("/"))
        suffix = Path(filename).suffix.lower()
        stem = Path(filename).stem[:80] or "media"
        safe_stem = "".join(ch.lower() if ch.isalnum() else "-" for ch in stem).strip("-") or "media"
        return f"{safe_folder or 'media'}/{uuid4().hex}-{safe_stem}{suffix}"

    def upload_bytes(
        self,
        *,
        content: bytes,
        filename: str,
        content_type: str | None = None,
        folder: str = "media/results",
    ) -> StoredMedia:
        if not content:
            raise MediaStorageError("Conteudo de midia vazio")

        resolved_type = content_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        key = self._key(folder=folder, filename=filename)
        self._client().put_object(
            Bucket=self.settings.r2_bucket_uploads,
            Key=key,
            Body=content,
            ContentType=resolved_type,
        )
        return StoredMedia(
            key=key,
            url=self._public_url(key),
            content_type=resolved_type,
            size_bytes=len(content),
        )

    def download_bytes(self, *, key: str) -> bytes:
        if not key:
            raise MediaStorageError("Chave R2 vazia")

        response = self._client().get_object(
            Bucket=self.settings.r2_bucket_uploads,
            Key=key,
        )
        body = response.get("Body")
        if body is None:
            raise MediaStorageError(f"Objeto R2 sem corpo: {key}")
        content = body.read()
        if not content:
            raise MediaStorageError(f"Objeto R2 vazio: {key}")
        return content

    async def upload_from_url(
        self,
        *,
        source_url: str,
        filename: str,
        content_type: str | None = None,
        folder: str = "media/results",
        timeout_seconds: float = 60,
        max_bytes: int = 100 * 1024 * 1024,
    ) -> StoredMedia:
        async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
            response = await client.get(source_url)
            response.raise_for_status()
            content = response.content
            if len(content) > max_bytes:
                raise MediaStorageError(f"Midia excede limite de {max_bytes} bytes")
            return self.upload_bytes(
                content=content,
                filename=filename,
                content_type=content_type or response.headers.get("content-type"),
                folder=folder,
            )
