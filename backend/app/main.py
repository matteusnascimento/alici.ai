from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import (
    ai,
    account,
    agents,
    auth,
    billing,
    chat,
    dashboard,
    health,
    integrations,
    marketing,
    media,
    settings as settings_routes,
    studio,
    subscriptions,
    usage,
    users,
    webhooks,
)
from app import models as _models  # noqa: F401
from app.core.config import settings
from app.core import database as db_core
from app.services.dev_seed_service import DevSeedService
from app.services.schema_sync_service import SchemaSyncService


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    db_core.ensure_database_connection()
    backend_name = db_core.engine.url.get_backend_name()

    # Em SQLite local, aplicamos sync de compatibilidade sempre.
    # Em produção (PostgreSQL), mudanças de schema devem vir de migrations.
    if backend_name == "sqlite" or settings.app_env.lower() != "production":
        db_core.Base.metadata.create_all(bind=db_core.engine)
        SchemaSyncService(db_core.engine).apply_startup_fixes()

    db = db_core.SessionLocal()
    try:
        if settings.should_seed_dev_user:
            DevSeedService(db).ensure_local_dev_user()
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    logger.exception("Erro interno em %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocorreu um erro interno. Tente novamente em instantes."},
    )

# backend/app/main.py -> parents[1] aponta para a pasta backend
BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIST = BASE_DIR / "frontend_dist"
ASSETS_DIR = FRONTEND_DIST / "assets"
UPLOADS_DIR = BASE_DIR / "uploads"
EXPORTS_DIR = BASE_DIR / "exports"

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.mount("/exports", StaticFiles(directory=EXPORTS_DIR), name="exports")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(account.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(marketing.router, prefix="/api")
app.include_router(media.router, prefix="/api")
app.include_router(settings_routes.router, prefix="/api")
app.include_router(billing.router, prefix="/api")
app.include_router(subscriptions.router, prefix="/api")
app.include_router(usage.router, prefix="/api")
app.include_router(integrations.router, prefix="/api")
app.include_router(studio.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")
app.include_router(health.router)


@app.get("/{full_path:path}", include_in_schema=False)
async def frontend_fallback(full_path: str):
    if full_path.startswith("api") or full_path in {"docs", "openapi.json", "health"}:
        raise HTTPException(status_code=404, detail="Not found")

    frontend_root = FRONTEND_DIST.resolve()
    requested_file = (FRONTEND_DIST / full_path).resolve()
    try:
        requested_file.relative_to(frontend_root)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Not found") from exc

    if requested_file.exists() and requested_file.is_file():
        return FileResponse(requested_file)

    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)

    raise HTTPException(status_code=404, detail="Frontend not built")
