#!/bin/bash
# Startup script para Render.com
# Executado automaticamente ao iniciar

echo "Iniciando ALICI..."

# 1. Instalar dependencias
echo "Verificando dependencias..."
pip install -r requirements.txt --quiet

# 2. Criar banco de dados (se necessario)
echo "Inicializando banco de dados..."
python init_db.py || echo "Banco ja existe"

# 3. Iniciar servidor Flask
echo "Iniciando servidor Flask..."
exec gunicorn main:app --workers 2 --threads 4 --timeout 60 --bind 0.0.0.0:${PORT:-5000}
