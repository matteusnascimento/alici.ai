"""FastAPI application factory and setup."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from alici_api.config import get_settings
from alici_api.middleware.rate_limit import RateLimitMiddleware
from alici_api.middleware.request_id import RequestIDMiddleware
from alici_api.responses import Codes, error_payload
from alici_api.routes.auth import router as auth_router
from alici_api.routes.billing import router as billing_router
from alici_api.routes.chat import router as chat_router
from alici_api.routes.conversations import router as conversations_router
from alici_api.routes.health import router as health_router
from alici_api.routes.history import router as history_router
from alici_api.routes.media import router as media_router
from alici_api.routes.pages import router as pages_router
from alici_api.routes.profile import router as profile_router
from alici_api.services.ai import IA_DISPONIVEL, VISAO_DISPONIVEL
from alici_api.services.text_model_hf import get_hf_model_status, initialize_text_model_from_hf
from alici_api.services.text_model_r2 import get_text_model_status, initialize_text_model_from_r2
from database import criar_tabelas
from logger import get_logger

load_dotenv()
settings = get_settings()
logger_app = get_logger("api")


def create_app() -> FastAPI:
    app = FastAPI(
        title="ALICI™ API",
        description="Inteligência Artificial com Memória Persistente",
        version="2.2",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestIDMiddleware)

    if settings.rate_limit_enabled:
        app.add_middleware(
            RateLimitMiddleware,
            max_requests=settings.rate_limit_max_requests,
            window_seconds=settings.rate_limit_window_seconds,
        )

    if os.path.isdir("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    if os.path.isdir("Static"):
        app.mount("/Static", StaticFiles(directory="Static"), name="Static")
    os.makedirs("generated", exist_ok=True)
    app.mount("/generated", StaticFiles(directory="generated"), name="generated")

    app.include_router(auth_router)
    app.include_router(billing_router)
    app.include_router(chat_router)
    app.include_router(conversations_router)
    app.include_router(media_router)
    app.include_router(history_router)
    app.include_router(pages_router)
    app.include_router(profile_router)
    app.include_router(health_router)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        request_id = getattr(request.state, "request_id", None)
        detail = exc.detail
        if isinstance(detail, dict) and "code" in detail:
            payload = error_payload(
                detail.get("code", f"ERR-HTTP-{exc.status_code}"),
                detail.get("message", "Erro na requisição"),
                **{k: v for k, v in detail.items() if k not in {"code", "message"}},
            )
        else:
            message = str(detail) if detail else "Erro na requisição"
            payload = error_payload(f"ERR-HTTP-{exc.status_code}", message)
        if request_id:
            payload["request_id"] = request_id
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        payload = error_payload(
            Codes.VALIDATION,
            "Erro de validação na requisição",
            details=exc.errors(),
        )
        request_id = getattr(request.state, "request_id", None)
        if request_id:
            payload["request_id"] = request_id
        return JSONResponse(
            status_code=422,
            content=payload,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger_app.exception("Erro interno não tratado", exc_info=exc)
        payload = error_payload(Codes.INTERNAL, "Erro interno do servidor")
        request_id = getattr(request.state, "request_id", None)
        if request_id:
            payload["request_id"] = request_id
        return JSONResponse(
            status_code=500,
            content=payload,
        )

    @app.on_event("startup")
    async def startup_event():
        logger_app.info("Inicializando ALICI API")
        if settings.env == "production" and settings.cors_allowed_origins == ["*"]:
            logger_app.warning("CORS_ALLOWED_ORIGINS não configurado corretamente em produção")

        try:
            criar_tabelas()
            logger_app.info("Banco de dados pronto")
        except Exception as exc:
            logger_app.warning(f"Aviso ao preparar banco: {exc}")

        logger_app.info(f"IA textual disponível: {IA_DISPONIVEL}")
        logger_app.info(f"IA visão disponível: {VISAO_DISPONIVEL}")

        initialized = initialize_text_model_from_r2()
        text_model_status = get_text_model_status()
        logger_app.info(f"Modelo textual R2 disponível: {initialized}")
        if not initialized:
            logger_app.warning(
                f"Modelo textual R2 indisponível: {text_model_status.get('erro', 'erro desconhecido')}"
            )
            logger_app.info("Tentando carregar modelo textual do HuggingFace como alternativa...")
            hf_initialized = initialize_text_model_from_hf()
            hf_model_status = get_hf_model_status()
            logger_app.info(f"Modelo textual HuggingFace disponível: {hf_initialized}")
            if not hf_initialized:
                logger_app.warning(
                    f"Modelo textual HuggingFace indisponível: {hf_model_status.get('erro', 'erro desconhecido')}"
                )

        logger_app.info("ALICI pronta para receber requisições")

    return app


app = create_app()
