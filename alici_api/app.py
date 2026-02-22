"""FastAPI application factory and setup."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from alici_api.routes.auth import router as auth_router
from alici_api.routes.chat import router as chat_router
from alici_api.routes.health import router as health_router
from alici_api.routes.history import router as history_router
from alici_api.routes.media import router as media_router
from alici_api.routes.pages import router as pages_router
from alici_api.services.ai import IA_DISPONIVEL, VISAO_DISPONIVEL
from database import criar_tabelas
from logger import get_logger

load_dotenv()
logger_app = get_logger("api")


def create_app() -> FastAPI:
    app = FastAPI(
        title="ALICI™ API",
        description="Inteligência Artificial com Memória Persistente",
        version="2.1",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if os.path.isdir("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    if os.path.isdir("Static"):
        app.mount("/Static", StaticFiles(directory="Static"), name="Static")
    if os.path.isdir("generated"):
        app.mount("/generated", StaticFiles(directory="generated"), name="generated")

    app.include_router(auth_router)
    app.include_router(chat_router)
    app.include_router(media_router)
    app.include_router(history_router)
    app.include_router(pages_router)
    app.include_router(health_router)

    @app.on_event("startup")
    async def startup_event():
        logger_app.info("🚀 Inicializando ALICI API...")
        try:
            criar_tabelas()
            logger_app.info("✅ Banco de dados pronto")
        except Exception as exc:
            logger_app.warning(f"⚠ Aviso ao preparar banco: {exc}")

        logger_app.info(f"IA textual disponível: {IA_DISPONIVEL}")
        logger_app.info(f"IA visão disponível: {VISAO_DISPONIVEL}")
        logger_app.info("🤖 ALICI pronta para receber requisições")

    return app


app = create_app()
