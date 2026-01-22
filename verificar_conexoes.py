#!/usr/bin/env python3
# verificar_conexoes.py - Verifica integridade do sistema ALICI

import os
import json
import sys
import traceback

print("=" * 60)
print("🔍 VERIFICAÇÃO DE INTEGRIDADE - ALICI™")
print("=" * 60)

# 1. Verificar arquivos do modelo
print("\n✓ 1. VERIFICANDO ARQUIVOS DO MODELO")
print("-" * 60)
model_dir = 'model'
model_path = os.path.join(model_dir, 'alici_blindado.h5')
tokenizer_path = os.path.join(model_dir, 'tokenizer.json')
license_path = os.path.join(model_dir, 'ALICI_LICENSE.txt')

files_check = {
    'Modelo H5': model_path,
    'Tokenizer JSON': tokenizer_path,
    'Licença': license_path
}

for name, path in files_check.items():
    exists = os.path.exists(path)
    size = f" ({os.path.getsize(path) / (1024**2):.1f}MB)" if exists else ""
    status = "✔" if exists else "✘"
    print(f"  {status} {name}: {path}{size}")

# 2. Carregar modelo e tokenizer
print("\n✓ 2. CARREGANDO MODELO NEURAL")
print("-" * 60)

try:
    import tensorflow as tf
    print("  ✔ TensorFlow importado")
    model = tf.keras.models.load_model(model_path)
    print("  ✔ Modelo carregado com sucesso!")
except Exception as e:
    print(f"  ✘ Erro ao carregar modelo: {e}")
    traceback.print_exc()

print("\n✓ 3. CARREGANDO TOKENIZER")
print("-" * 60)

try:
    with open(tokenizer_path, 'r') as f:
        tokenizer_json = json.load(f)
    print("  ✔ Tokenizer carregado com sucesso!")
except Exception as e:
    print(f"  ✘ Erro ao carregar tokenizer: {e}")
    traceback.print_exc()

# 3. Verificar módulos principais
print("\n✓ 4. VERIFICANDO MÓDULOS PRINCIPAIS")
print("-" * 60)

modules = [
    ('engine.py', 'from engine import gerar_resposta'),
    ('database.py', 'from database import buscar_memoria, aprender'),
    ('identidade.py', 'from identidade import identidade_alici'),
    ('resposta.py', 'from resposta import responder_local'),
    ('intencao.py', 'from intencao import precisa_pesquisa_web'),
    ('web_search.py', 'from web_search import buscar_na_web'),
]

for filename, import_stmt in modules:
    exists = os.path.exists(filename)
    status = "✔" if exists else "✘"
    print(f"  {status} {filename}")
    
    if exists:
        try:
            exec(import_stmt)
            print(f"     ✔ Importação bem-sucedida")
        except Exception as e:
            print(f"     ✘ Erro na importação: {e}")

# 4. Teste de chamada
print("\n✓ 5. TESTE DE CHAMADA - engine.gerar_resposta()")
print("-" * 60)

try:
    from engine import gerar_resposta
    
    test_questions = [
        "quem é você",
        "qual seu nome",
        "olá"
    ]
    
    for question in test_questions:
        try:
            response = gerar_resposta(question)
            print(f"  ✔ Pergunta: '{question}'")
            print(f"     Resposta: '{response[:100]}...'")
        except Exception as e:
            print(f"  ✘ Erro ao processar '{question}': {e}")
            traceback.print_exc()
            
except Exception as e:
    print(f"  ✘ Erro ao importar engine: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("✔ VERIFICAÇÃO CONCLUÍDA")
print("=" * 60)
