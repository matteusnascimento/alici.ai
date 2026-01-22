#!/bin/bash

# setup-alici-production.sh
# Script para migrar a ALICI™ de Flask para FastAPI + Autenticação + Memória

set -e

echo "🚀 SETUP ALICI™ - SISTEMA COMPLETO"
echo "===================================="

# 1. Atualizar requirements
echo "1️⃣  Atualizando dependências..."
pip install -r requirements_new.txt

# 2. Inicializar banco de dados
echo "2️⃣  Inicializando banco de dados..."
python -c "
from database_models import init_db
import os
init_db(os.getenv('DATABASE_URL'))
"

# 3. Teste de conexão
echo "3️⃣  Testando conexões..."
python -c "
from auth import create_access_token, verify_token
token, _ = create_access_token('test-user-id')
print(f'✅ JWT funcionando: {token[:20]}...')
"

# 4. Teste de embeddings
echo "4️⃣  Carregando modelo de embeddings..."
python -c "
from embeddings import init_embeddings, embed_text
init_embeddings()
embedding = embed_text('teste')
print(f'✅ Embedding gerado com dimensão: {len(embedding)}')
"

# 5. Pronto!
echo ""
echo "✅ Setup completo!"
echo ""
echo "Para rodar o servidor FastAPI:"
echo "  uvicorn main_fastapi:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Para produção no Render:"
echo "  - Build: pip install -r requirements_new.txt"
echo "  - Start: gunicorn main_fastapi:app -w 4"
