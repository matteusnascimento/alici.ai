"""FastAPI application factory and setup."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from alici_api.config import get_settings
from alici_api.middleware.base import setup_middlewares
from alici_api.monitoring import capture_critical_event, init_monitoring
from alici_api.responses import Codes, error_payload
from alici_api.routes.auth import router as auth_router
from alici_api.routes.billing import router as billing_router
from alici_api.routes.chat import router as chat_router
from alici_api.routes.health import router as health_router
from alici_api.routes.history import router as history_router
from alici_api.routes.jobs import router as jobs_router
from alici_api.routes.media import router as media_router
from alici_api.routes.pages import router as pages_router
from alici_api.routes.webhooks import router as webhooks_router
from alici_api.services.ai import AIManager, IA_DISPONIVEL, VISAO_DISPONIVEL
from database import criar_tabelas
from logger import get_logger

load_dotenv()
load_dotenv("backend/.env", override=False)
settings = get_settings()
logger_app = get_logger("api")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Inteligencia Artificial com Memoria Persistente",
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs" if settings.api_docs_enabled else None,
        redoc_url="/redoc" if settings.api_docs_enabled else None,
        openapi_url="/openapi.json" if settings.api_openapi_enabled else None,
    )

    init_monitoring(app, settings)
    setup_middlewares(app, settings)

    if os.path.isdir("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    if (FRONTEND_DIST / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="frontend_assets")
    app.include_router(auth_router)
    app.include_router(billing_router)
    app.include_router(chat_router)
    app.include_router(media_router)
    app.include_router(jobs_router)
    app.include_router(webhooks_router)
    app.include_router(history_router)
    app.include_router(pages_router)
    app.include_router(health_router)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        request_id = getattr(request.state, "request_id", None)
        detail = exc.detail
        if isinstance(detail, dict) and "code" in detail:
            payload = error_payload(
                detail.get("code", f"ERR-HTTP-{exc.status_code}"),
                detail.get("message", "Erro na requisicao"),
                **{k: v for k, v in detail.items() if k not in {"code", "message"}},
            )
        else:
            message = str(detail) if detail else "Erro na requisicao"
            payload = error_payload(f"ERR-HTTP-{exc.status_code}", message)
        if request_id:
            payload["request_id"] = request_id
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        payload = error_payload(
            Codes.VALIDATION,
            "Erro de validacao na requisicao",
            details=exc.errors(),
        )
        request_id = getattr(request.state, "request_id", None)
        if request_id:
            payload["request_id"] = request_id
        return JSONResponse(status_code=422, content=payload)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger_app.exception("Erro interno nao tratado", exc_info=exc)
        capture_critical_event(
            "unhandled_exception",
            tags={"path": request.url.path, "method": request.method},
            extra={"request_id": getattr(request.state, "request_id", None), "error": str(exc)},
        )
        payload = error_payload(Codes.INTERNAL, "Erro interno do servidor")
        request_id = getattr(request.state, "request_id", None)
        if request_id:
            payload["request_id"] = request_id
        return JSONResponse(status_code=500, content=payload)

    @app.on_event("startup")
    async def startup_event():
        logger_app.info("Inicializando ALICI API")

        try:
            criar_tabelas()
            logger_app.info("Banco de dados pronto")
        except Exception as exc:
            logger_app.warning(f"Aviso ao preparar banco: {exc}")

        logger_app.info(f"IA textual disponivel: {IA_DISPONIVEL}")
        logger_app.info(f"AI providers disponiveis: {AIManager().available_providers()}")
        logger_app.info(f"IA visao disponivel: {VISAO_DISPONIVEL}")
        logger_app.info("Modelos R2/HuggingFace em lazy-load; nao serao carregados no startup")
        logger_app.info("ALICI pronta para receber requisicoes")

    return app


app = create_app()
