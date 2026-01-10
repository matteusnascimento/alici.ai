#!/bin/bash

# Script de inicialização da Alici AI
echo "🤖 Iniciando Alici AI..."
echo "========================"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.8+"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Verificar se pip está instalado
if ! command -v pip &> /dev/null; then
    echo "❌ pip não encontrado. Por favor, instale pip"
    exit 1
fi

# Criar ambiente virtual (opcional)
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Ativar ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado"
    echo "📝 Copiando .env.example para .env"
    cp .env.example .env
    echo "❗ Por favor, edite o arquivo .env e adicione sua DATABASE_URL do Neon"
    echo "🔗 Acesse https://neon.tech para criar sua conta e obter a URL"
    exit 1
fi

# Inicializar banco de dados
echo "🔧 Inicializando banco de dados..."
python init_db.py

# Iniciar aplicação
echo "🚀 Iniciando aplicação..."
echo "🌍 Acesse: http://localhost:5000"
echo "⏹  Para parar: Ctrl+C"

python main.py