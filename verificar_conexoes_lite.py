#!/usr/bin/env python3
# verificar_conexoes_lite.py - Verifica integridade sem TensorFlow

import os
import json
import sys

print("=" * 60)
print("🔍 VERIFICAÇÃO ALICI™ (MODO LITE)")
print("=" * 60)

# 1. Arquivos do modelo
print("\n1. ARQUIVOS DO MODELO")
print("-" * 60)
model_files = {
    'alici_blindado.h5': 'model/alici_blindado.h5',
    'tokenizer.json': 'model/tokenizer.json',
    'ALICI_LICENSE.txt': 'model/ALICI_LICENSE.txt'
}

for name, path in model_files.items():
    exists = os.path.exists(path)
    size = f" ({os.path.getsize(path) / (1024**2):.1f}MB)" if exists else ""
    status = "✔" if exists else "✘"
    print(f"  {status} {path}{size}")

# 2. Módulos Python
print("\n2. MÓDULOS PRINCIPAIS")
print("-" * 60)
modules = ['engine.py', 'database.py', 'identidade.py', 'resposta.py', 
           'intencao.py', 'web_search.py', 'main.py']

for module in modules:
    exists = os.path.exists(module)
    status = "✔" if exists else "✘"
    size = f" ({os.path.getsize(module)/1024:.1f}KB)" if exists else ""
    print(f"  {status} {module}{size}")

# 3. Imports (sem TensorFlow)
print("\n3. IMPORTAÇÕES PYTHON")
print("-" * 60)

try:
    from identidade import identidade_alici
    print("  ✔ identidade_alici()")
except Exception as e:
    print(f"  ✘ identidade_alici(): {e}")

try:
    from resposta import responder_local
    print("  ✔ responder_local()")
except Exception as e:
    print(f"  ✘ responder_local(): {e}")

try:
    from intencao import precisa_pesquisa_web
    print("  ✔ precisa_pesquisa_web()")
except Exception as e:
    print(f"  ✘ precisa_pesquisa_web(): {e}")

try:
    from database import buscar_memoria, aprender
    print("  ✔ database.py (buscar_memoria, aprender)")
except Exception as e:
    print(f"  ✘ database.py: {e}")

try:
    from web_search import buscar_na_web
    print("  ✔ web_search.py (buscar_na_web)")
except Exception as e:
    print(f"  ✘ web_search.py: {e}")

# 4. Teste das funções
print("\n4. TESTE DAS FUNÇÕES")
print("-" * 60)

try:
    from identidade import identidade_alici
    resposta = identidade_alici()
    print(f"  ✔ identidade_alici():")
    print(f"     → '{resposta[:80]}...'")
except Exception as e:
    print(f"  ✘ identidade_alici(): {e}")

try:
    from resposta import responder_local
    test_qs = ["olá", "quem é você", "qual seu nome"]
    for q in test_qs:
        resp = responder_local(q)
        if resp:
            print(f"  ✔ responder_local('{q}'):")
            print(f"     → '{resp[:60]}...'")
            break
    else:
        print(f"  ℹ responder_local() - sem correspondência para testes simples")
except Exception as e:
    print(f"  ✘ responder_local(): {e}")

# 5. Verificar database
print("\n5. BANCO DE DADOS")
print("-" * 60)

try:
    from database import testar_conexao
    testar_conexao()
except:
    try:
        import os
        db_env = os.environ.get('DATABASE_URL')
        if db_env:
            print(f"  ℹ DATABASE_URL configurada: {db_env[:50]}...")
        else:
            print("  ⚠ DATABASE_URL não encontrada (.env?)")
    except Exception as e:
        print(f"  ✘ Erro ao verificar database: {e}")

print("\n" + "=" * 60)
print("✔ VERIFICAÇÃO CONCLUÍDA")
print("=" * 60)
