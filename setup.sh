#!/bin/bash
# ALICI Setup Script
# Facilita a configuração inicial do projeto

echo "🚀 Configurando ALICI..."

# Verificar se Python está instalado
if ! command -v python &> /dev/null; then
    echo "❌ Python não encontrado. Instale Python 3.11+ primeiro."
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip &> /dev/null; then
    echo "❌ pip não encontrado. Instale pip primeiro."
    exit 1
fi

echo "📦 Instalando dependências..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Falha na instalação das dependências."
    exit 1
fi

echo "📄 Configurando .env..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Arquivo .env criado. Edite-o com suas chaves API."
else
    echo "ℹ️ Arquivo .env já existe."
fi

echo "🗄️ Criando tabelas do banco..."
python -c "from database import criar_tabelas; criar_tabelas()"

if [ $? -ne 0 ]; then
    echo "⚠️ Aviso: Não foi possível criar tabelas. Configure DATABASE_URL no .env"
else
    echo "✅ Tabelas criadas com sucesso."
fi

echo "🎉 Setup completo!"
echo ""
echo "Para rodar localmente:"
echo "  python main.py"
echo ""
echo "Acesse: http://localhost:8000"
echo ""
echo "Para deploy no Render:"
echo "1. Fork este repositório"
echo "2. Conecte no Render.com"
echo "3. Configure as variáveis de ambiente"
echo ""
echo "📚 Documentação: https://github.com/matteusnascimento/alici.ai"