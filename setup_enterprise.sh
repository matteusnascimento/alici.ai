#!/bin/bash
# ALICI Enterprise Setup Script

echo "🚀 Configurando ALICI Enterprise Platform..."

# Verificar Python
if ! command -v python &> /dev/null; then
    echo "❌ Python não encontrado. Instale Python 3.11+ primeiro."
    exit 1
fi

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Falha na instalação das dependências."
    exit 1
fi

# Configurar .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Arquivo .env criado. Configure suas chaves API."
fi

# Criar tabelas
echo "🗄️ Criando tabelas do banco..."
python -c "from app.core.database import create_tables; create_tables()"

if [ $? -ne 0 ]; then
    echo "⚠️ Aviso: Configure DATABASE_URL no .env para usar PostgreSQL"
    echo "   Usando SQLite por enquanto..."
fi

# Inicializar Alembic
if [ ! -d migrations/versions ]; then
    echo "🔄 Inicializando Alembic..."
    alembic init migrations
fi

echo "🎉 Setup completo!"
echo ""
echo "Para desenvolvimento:"
echo "  python main.py"
echo ""
echo "Para produção:"
echo "  docker-compose up"
echo ""
echo "📚 Acesse:"
echo "  Landing: http://localhost:8000"
echo "  Chat: http://localhost:8000/chat"
echo "  Platform: http://localhost:8000/platform"
echo "  API Docs: http://localhost:8000/docs"
echo "  Public API: http://localhost:8000/v1"