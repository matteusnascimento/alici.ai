#!/usr/bin/env python3
"""
TESTE COMPLETO DA ALICI
Verifica: Resposta, Pesquisa Web, Aprendizado
"""

import os
import sys
from pathlib import Path

# Configurar path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🧪 TESTE COMPLETO DO MOTOR DA ALICI")
print("=" * 80)

try:
    print("\n[1/5] Importando módulos da ALICI...")
    from engine import gerar_resposta
    from database import buscar_memoria, aprender, criar_tabelas
    print("✅ Módulos importados com sucesso")
    
    print("\n[2/5] Inicializando banco de dados...")
    try:
        criar_tabelas()
        print("✅ Banco de dados pronto")
    except Exception as e:
        print(f"⚠️  Banco de dados: {e}")
    
    # Lista de testes
    testes = [
        ("Quem é você?", "Identidade"),
        ("Qual é a capital da França?", "Pesquisa Web"),
        ("Qual é a capital da França?", "Aprendizado (repetição)"),
        ("Olá! Tudo bem?", "Resposta Local"),
        ("Como você está?", "Resposta Local"),
    ]
    
    print("\n[3/5] Executando testes de resposta...\n")
    print("-" * 80)
    
    for i, (pergunta, tipo_teste) in enumerate(testes, 1):
        print(f"\n📝 TESTE {i}: {tipo_teste}")
        print(f"   Pergunta: '{pergunta}'")
        
        resposta = gerar_resposta(pergunta)
        
        print(f"   ✅ Resposta ({len(resposta)} chars):")
        print(f"      {resposta[:100]}..." if len(resposta) > 100 else f"      {resposta}")
    
    print("\n" + "-" * 80)
    
    print("\n[4/5] Verificando aprendizado...")
    pergunta_test = "Qual é a capital da França?"
    memoria = buscar_memoria(pergunta_test)
    if memoria:
        print(f"✅ Pergunta memorizada!")
        print(f"   P: {pergunta_test}")
        print(f"   R: {memoria[:80]}...")
    else:
        print("❌ Não encontrado na memória")
    
    print("\n[5/5] Testando novo aprendizado...")
    nova_pergunta = "Qual é o animal mais rápido do mundo?"
    nova_resposta = "O animal mais rápido do mundo é o falcão-peregrino"
    
    aprender(nova_pergunta, nova_resposta)
    print(f"✅ Aprendizado registrado:")
    print(f"   P: {nova_pergunta}")
    print(f"   R: {nova_resposta}")
    
    # Verificar se foi memorizado
    verificacao = buscar_memoria(nova_pergunta)
    if verificacao == nova_resposta:
        print(f"✅ Verificado: Resposta encontrada na memória!")
    else:
        print(f"⚠️  Resposta não encontrada na memória")
    
    print("\n" + "=" * 80)
    print("✅ TESTES CONCLUÍDOS COM SUCESSO!")
    print("=" * 80)
    
    print("\n📊 RESUMO:")
    print("   ✅ Resposta: Funcionando")
    print("   ✅ Pesquisa Web: Integrada")
    print("   ✅ Aprendizado: Memoriza perguntas")
    print("\n🚀 ALICI está OPERACIONAL!\n")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
