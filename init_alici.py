#!/usr/bin/env python3
"""
🎯 ALICI™ - SCRIPT DE INICIALIZAÇÃO INTEGRADA
Concatena modelo + engine + database + memória
Tudo funciona junto, pronto para produção

Criador: Mateus Nascimento dos Santos
Data: 2026-01-24
"""

import os
import sys
from pathlib import Path

def verificar_arquivos():
    """Verifica se todos os arquivos essenciais existem"""
    print("=" * 70)
    print("✅ VERIFICANDO ARQUIVOS ALICI™")
    print("=" * 70)
    print()
    
    arquivos_essenciais = {
        "Engine": [
            "engine.py",
            "resposta.py",
            "intencao.py",
            "identidade.py",
            "web_search.py",
            "sistema_emocoes.py",
        ],
        "Database": [
            "database.py",
            "init_db.py",
        ],
        "Web": [
            "main.py",
        ],
        "Modelo": [
            "model/modelo_animais_cifar100.h5",
            "model/tokenizer.json",
            "colab_finetuning.py",
            "teste_modelo.py",
        ],
        "Dataset": [
            "dataset_expandido.json",
            "gerar_dataset.py",
        ],
        "Config": [
            ".env.example",
            "requirements.txt",
            "Procfile",
            "runtime.txt",
        ],
        "Docs": [
            "README.md",
            "SETUP.md",
            "TRAINING_GUIDE.md",
        ]
    }
    
    status_ok = True
    
    for categoria, arquivos in arquivos_essenciais.items():
        print(f"📁 {categoria}:")
        for arquivo in arquivos:
            existe = Path(arquivo).exists()
            emoji = "✅" if existe else "❌"
            status = "OK" if existe else "FALTA"
            print(f"   {emoji} {arquivo}: {status}")
            if not existe and arquivo not in ["model/modelo_animais_cifar100.h5"]:  # Model é grande
                status_ok = False
        print()
    
    return status_ok

def gerar_env():
    """Gera .env a partir de .env.example se não existir"""
    print("🔧 Configurando variáveis de ambiente...")
    
    if Path(".env").exists():
        print("   ✅ .env já existe")
    else:
        print("   ⚠️  .env não encontrado")
        print("   📋 Copie de .env.example:")
        print()
        print("   cp .env.example .env")
        print("   # Depois edite com sua DATABASE_URL do Neon")
        print()

def testar_imports():
    """Testa se todos os módulos podem ser importados"""
    print("🧪 Testando imports...")
    print()
    
    modulos = {
        "Flask": "flask",
        "TensorFlow": "tensorflow",
        "Psycopg2": "psycopg2",
        "Requests": "requests",
        "Dotenv": "dotenv",
    }
    
    todos_ok = True
    for nome, modulo in modulos.items():
        try:
            __import__(modulo)
            print(f"   ✅ {nome}")
        except ImportError:
            print(f"   ❌ {nome} - Execute: pip install -r requirements.txt")
            todos_ok = False
    
    print()
    return todos_ok

def testar_engine():
    """Testa se engine funciona"""
    print("🧠 Testando engine ALICI™...")
    print()
    
    try:
        from engine import gerar_resposta
        
        resposta = gerar_resposta("quem é você")
        print(f"   ✅ Engine OK")
        print(f"   Teste: 'quem é você'")
        print(f"   Resposta: {resposta[:80]}...")
        
        return True
    except Exception as e:
        print(f"   ❌ Erro no engine: {e}")
        return False
    
    print()

def criar_startup_script():
    """Cria script de startup para Render"""
    print("📝 Criando startup script...")
    
    startup = """#!/bin/bash
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
"""
    
    with open("startup.sh", "w", encoding="utf-8") as f:
        f.write(startup)
    
    print("   ✅ startup.sh criado")
    print()

def criar_deployment_config():
    """Cria configurações para deployment"""
    print("Configurando deployment...")
    
    # Procfile para Render
    procfile = """web: gunicorn main:app --workers 2 --threads 4 --timeout 60
"""
    
    with open("Procfile", "w", encoding="utf-8") as f:
        f.write(procfile)
    
    # .gitignore para evitar arquivos grandes
    gitignore = """
# Virtual Environment
.venv/
venv/
ENV/

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local
.env.*.local

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Modelo (sera feito download em CI/CD)
# model/*.h5 - Descomentar se usar Git LFS
"""
    
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore)
    
    print("   ✅ Procfile e .gitignore configurados")
    print()

def main():
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "🎯 ALICI™ - INICIALIZAÇÃO INTEGRADA" + " " * 19 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    # 1. Verificar arquivos
    arquivos_ok = verificar_arquivos()
    
    # 2. Gerar .env
    gerar_env()
    
    # 3. Testar imports
    imports_ok = testar_imports()
    
    # 4. Testar engine
    engine_ok = testar_engine()
    
    # 5. Criar startup script
    criar_startup_script()
    
    # 6. Criar deployment config
    criar_deployment_config()
    
    # Resumo final
    print("=" * 70)
    print("✅ INICIALIZAÇÃO COMPLETA")
    print("=" * 70)
    print()
    
    if arquivos_ok and imports_ok and engine_ok:
        print("🎉 ALICI™ está pronta para usar!")
        print()
        print("📝 Próximos passos:")
        print("   1. Editar .env com DATABASE_URL do Neon")
        print("   2. Executar: python init_db.py")
        print("   3. Iniciar: python main.py")
        print("   4. Acessar: http://localhost:5000")
        print()
        print("🚀 Para deploy em Render.com:")
        print("   1. Push do repositório: git push")
        print("   2. Conectar em Render.com")
        print("   3. Definir DATABASE_URL como env var")
        print("   4. Deploy automático!")
        print()
        return True
    else:
        print("⚠️  Alguns problemas foram encontrados")
        print("   Revise as mensagens acima")
        print()
        return False

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)
