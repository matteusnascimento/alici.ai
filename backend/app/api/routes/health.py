from pathlib import Path
import socket
from urllib.parse import urlparse

from fastapi import APIRouter
from fastapi.responses import FileResponse, Response
from sqlalchemy import inspect, text

from app.core.config import settings
from app.core.database import engine
from app.services.ai.manager import AIManager

router = APIRouter(tags=["health"])

BASE_DIR = Path(__file__).resolve().parents[3]
FRONTEND_DIST = BASE_DIR / "frontend_dist"
INDEX_FILE = FRONTEND_DIST / "index.html"


@router.get("/", include_in_schema=False)
def root():
    if INDEX_FILE.exists():
        return FileResponse(INDEX_FILE)
    return {"status": "ok", "service": "alici-ai", "docs": "/docs"}


@router.head("/", include_in_schema=False)
def root_head():
    return Response(status_code=200)


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


def _check_db() -> dict:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "detail": exc.__class__.__name__}


def _check_migrations() -> dict:
    try:
        inspector = inspect(engine)
        if not inspector.has_table("alembic_version"):
            return {"status": "warning", "detail": "alembic_version ausente"}
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "detail": exc.__class__.__name__}


def _check_redis() -> dict:
    if not settings.redis_required and not settings.redis_url:
        return {"status": "skipped"}
    if not settings.redis_url:
        return {"status": "error", "detail": "REDIS_URL ausente"}
    parsed = urlparse(settings.redis_url)
    try:
        with socket.create_connection((parsed.hostname or "localhost", parsed.port or 6379), timeout=2):
            return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "detail": exc.__class__.__name__}


def _check_ai() -> dict:
    manager = AIManager()
    active = manager.get_active_provider()
    if not active:
        return {"status": "error", "default_provider": settings.default_ai_provider, "configured": []}
    return {"status": "ok", "default_provider": settings.default_ai_provider, "active_provider": active, "configured": manager.configured_providers()}


def _check_stripe() -> dict:
    has_prices = any([settings.stripe_price_pro_monthly, settings.stripe_price_pro_yearly, settings.stripe_price_business_monthly, settings.stripe_price_business_yearly])
    if not settings.stripe_secret_key:
        return {"status": "warning", "configured": False, "prices": has_prices}
    return {"status": "ok", "configured": True, "prices": has_prices, "webhook": bool(settings.stripe_webhook_secret)}


@router.get("/ready")
def readiness() -> dict:
    checks = {
        "db": _check_db(),
        "migrations": _check_migrations(),
        "redis": _check_redis(),
        "ai": _check_ai(),
        "stripe": _check_stripe(),
        "storage": {"status": "skipped" if not settings.storage_external_required else "error", "detail": "storage externo nao configurado" if settings.storage_external_required else None},
    }
    failed = [name for name, item in checks.items() if item.get("status") == "error"]
    return {"status": "error" if failed else "ok", "checks": checks}
