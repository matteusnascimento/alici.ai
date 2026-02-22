"""
🤖 ALICI - PONTO DE ENTRADA PRINCIPAL
main.py - Entrypoint unificado para a aplicação ALICI™
"""

import os
import sys
import traceback
from dotenv import load_dotenv

# ==================================================
# CONFIGURAR PATH PRIMEIRO (ANTES DE QUALQUER IMPORT)
# ==================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ==================================================
# CARREGAR VARIÁVEIS DE AMBIENTE
# ==================================================
load_dotenv()

# ==================================================
# IMPORTAR LOGGER
# ==================================================
try:
    from logger import get_logger
    logger_main = get_logger("main")
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger_main = logging.getLogger("main")
    logger_main.warning("⚠️ Logger customizado não encontrado, usando padrão.")

# ==================================================
# IMPORTAR APP PRINCIPAL
# ==================================================
try:
    from alici_api.app import app
    logger_main.info("✅ App FastAPI importado com sucesso.")

except Exception as e:
    logger_main.error(f"❌ Erro ao importar alici_api.app: {e}")
    logger_main.debug(traceback.format_exc())

    from fastapi import FastAPI
    app = FastAPI(title="ALICI - App Fallback")

    @app.get("/")
    def root():
        return {
            "message": "⚠️ App fallback ativado - erro ao carregar alici_api.app"
        }

# ==================================================
# IMPORTAR CRIAR TABELAS
# ==================================================
try:
    from database import criar_tabelas
    logger_main.info("✅ Função criar_tabelas importada com sucesso.")
except Exception as e:
    logger_main.warning(f"⚠️ criar_tabelas não encontrada: {e}")

    def criar_tabelas():
        logger_main.warning("⚠️ criar_tabelas não implementada.")

# ==================================================
# INICIALIZAÇÃO
# ==================================================
try:
    criar_tabelas()
    logger_main.info("✅ Tabelas criadas/verificadas ao iniciar aplicação.")
except Exception as e:
    logger_main.error(f"❌ Erro ao criar tabelas: {e}")

# ==================================================
# EXECUÇÃO LOCAL (somente desenvolvimento)
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

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=(env == "development")
    )
