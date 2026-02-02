#!/usr/bin/env python3
"""
init_alici.py - Verificador Completo do Sistema ALICI™
Verifica todas as dependências, configurações e componentes
"""

import os
import sys
from dotenv import load_dotenv

print("=" * 70)
print("🤖 VERIFICADOR COMPLETO DO SISTEMA ALICI™")
print("=" * 70)

# Carregar variáveis de ambiente
load_dotenv()

# Contadores
total_verificacoes = 0
verificacoes_ok = 0
avisos = []
erros = []

def verificar(nome, teste, critico=True):
    """Helper para verificações"""
    global total_verificacoes, verificacoes_ok, avisos, erros
    total_verificacoes += 1
    
    print(f"\n📝 Verificando: {nome}")
    
    try:
        resultado = teste()
        if resultado:
            verificacoes_ok += 1
            print(f"   ✅ OK")
            return True
        else:
            if critico:
                erros.append(nome)
                print(f"   ❌ FALHOU (CRÍTICO)")
            else:
                avisos.append(nome)
                print(f"   ⚠️  AVISO")
            return False
    except Exception as e:
        if critico:
            erros.append(f"{nome}: {e}")
            print(f"   ❌ ERRO: {e}")
        else:
            avisos.append(f"{nome}: {e}")
            print(f"   ⚠️  AVISO: {e}")
        return False


# ==================================================
# 1️⃣ VERIFICAÇÃO DE VARIÁVEIS DE AMBIENTE
# ==================================================
print("\n" + "=" * 70)
print("1️⃣  VARIÁVEIS DE AMBIENTE")
print("=" * 70)

verificar(
    "DATABASE_URL configurado",
    lambda: bool(os.getenv("DATABASE_URL")),
    critico=True
)


# ==================================================
# 2️⃣ VERIFICAÇÃO DE DEPENDÊNCIAS
# ==================================================
print("\n" + "=" * 70)
print("2️⃣  DEPENDÊNCIAS PYTHON")
print("=" * 70)

dependencias = [
    ("flask", "Flask"),
    ("fastapi", "FastAPI"),
    ("psycopg2", "PostgreSQL Driver"),
    ("tensorflow", "TensorFlow"),
    ("dotenv", "Python-dotenv"),
    ("requests", "Requests"),
]

for modulo, nome in dependencias:
    try:
        __import__(modulo)
        verificar(nome, lambda: True, critico=False)
    except ImportError:
        verificar(nome, lambda: False, critico=False)


# ==================================================
# 3️⃣ VERIFICAÇÃO DE ARQUIVOS ESSENCIAIS
# ==================================================
print("\n" + "=" * 70)
print("3️⃣  ARQUIVOS ESSENCIAIS")
print("=" * 70)

arquivos_essenciais = [
    "main.py",
    "engine.py",
    "database.py",
    "identidade.py",
    "resposta.py",
    "intencao.py",
    "web_search.py",
    "sistema_emocoes.py",
    "requirements.txt",
    ".env",
]

for arquivo in arquivos_essenciais:
    verificar(
        arquivo,
        lambda a=arquivo: os.path.exists(a),
        critico=True
    )


# ==================================================
# 4️⃣ VERIFICAÇÃO DE CONEXÃO COM BANCO
# ==================================================
print("\n" + "=" * 70)
print("4️⃣  CONEXÃO COM BANCO DE DADOS")
print("=" * 70)

if os.getenv("DATABASE_URL"):
    try:
        from database import conectar
        
        verificar(
            "Conectar ao PostgreSQL",
            lambda: bool(conectar()),
            critico=True
        )
        
        # Verificar se tabela existe
        try:
            from database import buscar_memoria
            buscar_memoria("teste")
            verificar("Tabela 'memoria' existe", lambda: True, critico=True)
        except Exception as e:
            if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                verificar("Tabela 'memoria' existe", lambda: False, critico=True)
                print("\n   💡 Execute: python init_db.py")
            else:
                raise e
                
    except Exception as e:
        verificar(f"Conexão com banco", lambda: False, critico=True)
else:
    print("   ⏭️  Pulando (DATABASE_URL não configurado)")


# ==================================================
# 5️⃣ VERIFICAÇÃO DE MÓDULOS CORE
# ==================================================
print("\n" + "=" * 70)
print("5️⃣  MÓDULOS CORE DA ALICI")
print("=" * 70)

try:
    from identidade import identidade_alici
    verificar("identidade.py", lambda: bool(identidade_alici()), critico=True)
except:
    verificar("identidade.py", lambda: False, critico=True)

try:
    from resposta import responder_local
    verificar("resposta.py", lambda: bool(responder_local("olá")), critico=True)
except:
    verificar("resposta.py", lambda: False, critico=True)

try:
    from intencao import precisa_pesquisa_web
    verificar("intencao.py", lambda: callable(precisa_pesquisa_web), critico=True)
except:
    verificar("intencao.py", lambda: False, critico=True)

try:
    from engine import gerar_resposta
    verificar("engine.py", lambda: callable(gerar_resposta), critico=True)
except:
    verificar("engine.py", lambda: False, critico=True)


# ==================================================
# 6️⃣ VERIFICAÇÃO DE MODELOS (OPCIONAL)
# ==================================================
print("\n" + "=" * 70)
print("6️⃣  MODELOS DE MACHINE LEARNING (OPCIONAL)")
print("=" * 70)

modelos_paths = [
    "modelo_animais.h5",
    "model/modelo_animais_cifar100.h5",
    "model/modelo_animais_treinado.h5",
]

for modelo_path in modelos_paths:
    verificar(
        modelo_path,
        lambda m=modelo_path: os.path.exists(m),
        critico=False
    )


# ==================================================
# RESUMO FINAL
# ==================================================
print("\n" + "=" * 70)
print("📊 RESUMO DA VERIFICAÇÃO")
print("=" * 70)

percentual = (verificacoes_ok / total_verificacoes * 100) if total_verificacoes > 0 else 0

print(f"\n✅ Verificações OK: {verificacoes_ok}/{total_verificacoes} ({percentual:.1f}%)")

if avisos:
    print(f"\n⚠️  Avisos ({len(avisos)}):")
    for aviso in avisos:
        print(f"   • {aviso}")

if erros:
    print(f"\n❌ Erros CRÍTICOS ({len(erros)}):")
    for erro in erros:
        print(f"   • {erro}")
    
    print("\n" + "=" * 70)
    print("❌ SISTEMA NÃO ESTÁ PRONTO")
    print("=" * 70)
    print("\n🔧 Ações necessárias:")
    
    if not os.getenv("DATABASE_URL"):
        print("   1. Configure DATABASE_URL no arquivo .env")
    
    if any("memoria" in str(e).lower() for e in erros):
        print("   2. Execute: python init_db.py")
    
    if any("pip" in str(e).lower() or any(dep[1] in str(e) for dep in dependencias)):
        print("   3. Instale dependências: pip install -r requirements.txt")
    
    sys.exit(1)
    
elif avisos:
    print("\n" + "=" * 70)
    print("⚠️  SISTEMA FUNCIONAL (com avisos)")
    print("=" * 70)
    print("\n✓ ALICI está pronta para uso básico")
    print("⚠️ Alguns recursos opcionais podem não estar disponíveis")
    print("\n🚀 Execute: python main.py")
    
else:
    print("\n" + "=" * 70)
    print("✅ SISTEMA TOTALMENTE OPERACIONAL")
    print("=" * 70)
    print("\n🎉 ALICI está 100% pronta para uso!")
    print("\n📝 Próximos passos:")
    print("   1. Execute: python main.py")
    print("   2. Acesse: http://localhost:8000")
    print("   3. Ou teste: python teste_engine_completo.py")
    print("\n" + "=" * 70)
