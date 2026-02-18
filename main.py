"""
🤖 ALICI - PONTO DE ENTRADA PRINCIPAL
main.py - Entrypoint unificado para a aplicação ALICI™
"""

import os
import sys
from dotenv import load_dotenv
from logger import get_logger

# Configurar logger
logger_main = get_logger("main")

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Carregar variáveis de ambiente
load_dotenv()

# 🔹 Importar app FastAPI com fallback
try:
    from alici_api.app import app
    logger_main.info("✅ App FastAPI importado com sucesso.")
except ImportError as e:
    logger_main.error(f"Erro ao importar app: {e}")
    logger_main.warning("⚠️ Criando app FastAPI de fallback...")
    from fastapi import FastAPI
    app = FastAPI(title="ALICI - App Fallback")

    @app.get("/")
    def root():
        return {"message": "⚠️ App fallback ativado - alici_api.app não encontrado"}

# 🔹 Importar função criar_tabelas com fallback
try:
    from database import criar_tabelas
    logger_main.info("✅ Função criar_tabelas importada.")
except ImportError as e:
    logger_main.warning(f"Função criar_tabelas não encontrada: {e}")
    # Criar função dummy para não travar o app
    def criar_tabelas():
        logger_main.warning("⚠️ criar_tabelas não implementada, ignorando...")


# 🔹 Execução direta (uvicorn) para desenvolvimento local
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    env = os.getenv("ENV", "development")

    logger_main.info(f"\n{'='*60}")
    logger_main.info(f"🚀 Iniciando ALICI na porta {port}...")
    logger_main.info(f"📍 Acesse: http://localhost:{port}")
    logger_main.info(f"🔧 Ambiente: {env}")
    logger_main.info(f"{'='*60}\n")

    # 🔥 Criar tabelas automaticamente ao iniciar
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
