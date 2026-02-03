"""
🤖 ALICI - PONTO DE ENTRADA PRINCIPAL
main.py - Entrypoint unificado para a aplicação ALICI™
"""

import os
import sys
from dotenv import load_dotenv

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Carregar variáveis de ambiente
load_dotenv()

# Importar app FastAPI
from alici_api.app import app

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    env = os.getenv("ENV", "development")
    
    print(f"\n{'='*60}")
    print(f"🚀 Iniciando ALICI na porta {port}...")
    print(f"📍 Acesse: http://localhost:{port}")
    print(f"🔧 Ambiente: {env}")
    print(f"{'='*60}\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=(env == "development")
    )
