from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(tags=["health"])

BASE_DIR = Path(__file__).resolve().parents[3]
FRONTEND_DIST = BASE_DIR / "frontend_dist"
INDEX_FILE = FRONTEND_DIST / "index.html"


@router.get("/", include_in_schema=False)
def root():
    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)
    return {"status": "ok", "service": "alici-ai", "docs": "/docs"}


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
