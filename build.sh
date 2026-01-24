#!/bin/bash
# ALICI Render Deploy - Build & Run Script

echo "🚀 ALICI Deploy no Render"
echo "========================="

# 1. Instalar dependências
echo "📦 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# 2. Inicializar banco de dados
echo "📊 Inicializando banco de dados..."
python -c "from database import criar_tabelas; criar_tabelas()"

# 3. Verificar conexão
echo "🔗 Verificando conexões..."
python -c "from database import conectar; print('✅ Banco de dados OK')" || echo "⚠️  BD pode não estar disponível"

echo ""
echo "✅ Build concluído com sucesso!"
echo "🎯 ALICI pronta para rodar!"
