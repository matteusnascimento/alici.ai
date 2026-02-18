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

# Importar app FastAPI e funções do database
try:
    from alici_api.app import app
except ImportError as e:
    logger_main.error(f"Erro ao importar app: {e}")
    raise

try:
    from database import criar_tabelas
except ImportError as e:
    logger_main.error(f"Erro ao importar criar_tabelas: {e}")
    # Criar função dummy para não travar o app
    def criar_tabelas():
        logger_main.warning("⚠️ criar_tabelas não implementada, ignorando...")


if __name__ == "__main__":
    import uvicorn

    # Porta e ambiente
    port = int(os.getenv("PORT", 8000))
    env = os.getenv("ENV", "development")

    # Logs de inicialização
    logger_main.info(f"\n{'='*60}")
    logger_main.info(f"🚀 Iniciando ALICI na porta {port}...")
    logger_main.info(f"📍 Acesse: http://localhost:{port}")
    logger_main.info(f"🔧 Ambiente: {env}")
    logger_main.info(f"{'='*60}\n")

    # 🔥 Criar tabelas automaticamente ao iniciar
    try:
        criar_tabelas()
    except Exception as e:
        logger_main.error(f"Erro ao criar tabelas: {e}")

    # Iniciar servidor Uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=(env == "development")
    )
