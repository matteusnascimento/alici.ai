"""Persistent storage for generated media.

Cloudflare R2 exposes an S3-compatible API, so boto3 is imported lazily only
when a real media provider needs to persist generated assets.
"""

from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from pathlib import Path
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

    def status(self, include_probe: bool = False) -> dict:
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
        result = {"configured": not missing, "missing": missing}
        if include_probe and result["configured"] and hasattr(self, "probe"):
            result["probe"] = self.probe()
        return result

    def _require_config(self) -> None:
        missing = self.status()["missing"]
        if missing:
            raise MediaStorageError(f"Storage R2 incompleto. Configure: {', '.join(missing)}")

    def _client(self):
        self._require_config()
        import boto3

        return boto3.client(
            "s3",
            endpoint_url=self.settings.r2_endpoint_url,
            aws_access_key_id=self.settings.r2_access_key_id,
            aws_secret_access_key=self.settings.r2_secret_access_key.get_secret_value(),
            region_name="auto",
        )

    def _public_url(self, key: str) -> str:
        base_url = str(self.settings.r2_public_base_url or "").rstrip("/")
        return f"{base_url}/{key.lstrip('/')}"

    def _key(self, *, folder: str, filename: str) -> str:
        safe_folder = "/".join(part.strip("/").replace("..", "") for part in folder.split("/") if part.strip("/"))
        suffix = Path(filename).suffix.lower()
        stem = Path(filename).stem[:80] or "media"
        safe_stem = "".join(ch.lower() if ch.isalnum() else "-" for ch in stem).strip("-") or "media"
        return f"{safe_folder or 'generated'}/{uuid4().hex}-{safe_stem}{suffix}"

    def upload_bytes(
        self,
        *,
        content: bytes,
        filename: str,
        content_type: str | None = None,
        folder: str = "generated",
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

    async def upload_from_url(
        self,
        *,
        source_url: str,
        filename: str,
        content_type: str | None = None,
        folder: str = "generated",
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

