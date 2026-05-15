"""Persistent upload staging for media jobs.

Web and worker processes cannot rely on the same local filesystem in
production. Uploaded media is therefore staged in Cloudflare R2 and referenced
by URL/key in generation_jobs metadata.
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, UploadFile

from alici_api.config import get_settings
from alici_api.responses import Codes
from alici_api.services.media_storage import MediaStorageError, R2MediaStorage


@dataclass(frozen=True)
class SavedUpload:
    path: str
    url: str
    key: str
    filename: str
    content_type: str
    size_bytes: int


def _extension_for_content_type(content_type: str | None) -> str:
    return {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/gif": ".gif",
        "image/bmp": ".bmp",
        "image/webp": ".webp",
    }.get(content_type or "", ".bin")


async def save_upload_for_job(
    upload: UploadFile,
    *,
    job_id: str,
    allowed_types: set[str],
    max_bytes: int | None = None,
) -> SavedUpload:
    settings = get_settings()
    limit = int(max_bytes or settings.media_upload_max_bytes)
    content_type = upload.content_type or "application/octet-stream"

    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Tipo de arquivo nao suportado"},
        )

    storage = R2MediaStorage()
    if settings.media_storage_required and not storage.is_configured():
        raise HTTPException(
            status_code=503,
            detail={
                "code": Codes.SERVICE_UNAVAILABLE,
                "message": "Storage persistente de midia nao configurado. Configure Cloudflare R2.",
                "missing": storage.missing_config(),
                "charged": False,
            },
        )

    total = 0
    chunks: list[bytes] = []
    while True:
        chunk = await upload.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > limit:
            raise HTTPException(
                status_code=413,
                detail={
                    "code": Codes.BAD_REQUEST,
                    "message": f"Arquivo excede o limite de {limit} bytes",
                    "charged": False,
                },
            )
        chunks.append(chunk)

    if total == 0:
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Arquivo vazio", "charged": False},
        )

    filename = upload.filename or f"{job_id}{_extension_for_content_type(content_type)}"
    try:
        stored = storage.upload_bytes(
            content=b"".join(chunks),
            filename=filename,
            content_type=content_type,
            folder=f"media/uploads/{job_id}",
        )
    except MediaStorageError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": Codes.SERVICE_UNAVAILABLE,
                "message": str(exc),
                "charged": False,
            },
        ) from exc

    return SavedUpload(
        path=stored.url,
        url=stored.url,
        key=stored.key,
        filename=filename,
        content_type=content_type,
        size_bytes=stored.size_bytes,
    )
