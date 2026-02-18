"""
🤖 ALICI - PONTO DE ENTRADA PRINCIPAL
main.py - Entrypoint unificado para a aplicação ALICI™
"""

import os
import sys
from dotenv import load_dotenv
from logger import get_logger

# ==================================================
# LOGGER
# ==================================================
logger_main = get_logger("main")

# ==================================================
# PATHS
# ==================================================
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ==================================================
# CARREGAR VARIÁVEIS DE AMBIENTE
# ==================================================
load_dotenv()

# ==================================================
# TENTAR IMPORTAR APP PRINCIPAL
# ==================================================
try:
    from alici_api import app
    logger_main.info("✅ App FastAPI importado com sucesso.")
except ImportError as e:
    logger_main.error(f"Erro ao importar app: {e}")
    logger_main.warning("⚠️ Criando app FastAPI de fallback...")
    from fastapi import FastAPI
    app = FastAPI(title="ALICI - App Fallback")

    @app.get("/")
    def root():
        return {"message": "⚠️ App fallback ativado - alici_api.app não encontrado"}

# ==================================================
# TENTAR IMPORTAR CRIAR TABELAS
# ==================================================
try:
    from database import criar_tabelas
    logger_main.info("✅ Função criar_tabelas importada.")
except ImportError as e:
    logger_main.warning(f"Função criar_tabelas não encontrada: {e}")
    # Criar função dummy para não travar o app
    def criar_tabelas():
        logger_main.warning("⚠️ criar_tabelas não implementada, ignorando...")

# ==================================================
# ENDPOINT /chat
# ==================================================
try:
    from fastapi import FastAPI
    from pydantic import BaseModel
    from engine import gerar_resposta_com_emocao

    class Mensagem(BaseModel):
        mensagem: str

    @app.post("/chat")
    async def chat(payload: Mensagem):
        pergunta = payload.mensagem
        resposta = gerar_resposta_com_emocao(pergunta)
        return {"resposta": resposta}

    logger_main.info("✅ Endpoint /chat configurado com sucesso.")

except Exception as e:
    logger_main.error(f"Erro ao configurar endpoint /chat: {e}")

# ==================================================
# EXECUÇÃO DIRETA (UVICORN)
# ==================================================
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    env = os.getenv("ENV", "development")

    logger_main.info(f"\n{'='*60}")
    logger_main.info(f"🚀 Iniciando ALICI na porta {port}...")
    logger_main.info(f"📍 Acesse: http://localhost:{port}")
    logger_main.info(f"🔧 Ambiente: {env}")
    logger_main.info(f"{'='*60}\n")

    # 🔹 Criar tabelas ao iniciar
    try:
        criar_tabelas()
        logger_main.info("✅ Tabelas criadas ou verificadas com sucesso.")
    except Exception as e:
        logger_main.error(f"Erro ao criar tabelas: {e}")

    uvicorn.run(
        "main:app",  # Agora o app sempre existe
        host="0.0.0.0",
        port=port,
        reload=(env == "development")
    )
