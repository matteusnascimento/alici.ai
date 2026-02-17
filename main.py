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

# Importar app FastAPI
from alici_api.app import app
from database import criar_tabelas


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
    criar_tabelas()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=(env == "development")
    )
