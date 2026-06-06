"""Safe local staging for uploaded media before background processing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException, UploadFile

from alici_api.config import get_settings
from alici_api.responses import Codes


BASE_DIR = Path(__file__).resolve().parents[2]
UPLOADS_DIR = BASE_DIR / "generated" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class SavedUpload:
    path: str
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

    extension = _extension_for_content_type(content_type)
    safe_name = f"{job_id}{extension}"
    target_path = UPLOADS_DIR / safe_name
    total = 0

    with target_path.open("wb") as output:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                try:
                    target_path.unlink(missing_ok=True)
                finally:
                    raise HTTPException(
                        status_code=413,
                        detail={
                            "code": Codes.BAD_REQUEST,
                            "message": f"Arquivo excede o limite de {limit} bytes",
                        },
                    )
            output.write(chunk)

    if total == 0:
        target_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail={"code": Codes.BAD_REQUEST, "message": "Arquivo vazio"},
        )

    return SavedUpload(
        path=str(target_path),
        filename=upload.filename or safe_name,
        content_type=content_type,
        size_bytes=total,
    )
