#!/usr/bin/env python3
"""
teste_alici_completo.py - Teste Completo da ALICI
Teste integrado de todas as funcionalidades principais
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Verificar DATABASE_URL
if not os.getenv("DATABASE_URL"):
    print("❌ ERRO: DATABASE_URL não configurado no .env")
    print("   Configure DATABASE_URL antes de executar os testes")
    sys.exit(1)

print("=" * 70)
print("🤖 TESTE COMPLETO DA ALICI™")
print("   Validação de Sistema End-to-End")
print("=" * 70)

# Importar módulos
try:
    from engine import gerar_resposta
    from database import buscar_memoria, aprender
    from identidade import identidade_alici
    from resposta import responder_local
    print("\n✅ Todos os módulos importados com sucesso")
except Exception as e:
    print(f"\n❌ Erro ao importar módulos: {e}")
    sys.exit(1)

# Contador
total = 0
passou = 0

def teste(nome, resultado_esperado=True):
    """Helper para testes"""
    global total, passou
    total += 1
    
    def decorador(func):
        print(f"\n{'='*70}")
        print(f"Teste {total}: {nome}")
        print('='*70)
        
        try:
            resultado = func()
            
            if resultado_esperado:
                sucesso = bool(resultado)
            else:
                sucesso = not bool(resultado)
            
            if sucesso:
                passou += 1
                print("✅ PASSOU")
                if isinstance(resultado, str) and len(resultado) > 0:
                    preview = resultado[:200] + "..." if len(resultado) > 200 else resultado
                    print(f"\nResposta: {preview}")
            else:
                print("❌ FALHOU")
                
            return resultado
            
        except Exception as e:
            print(f"❌ ERRO: {e}")
            return None
    
    return decorador


# ==================================================
# TESTES
# ==================================================

@teste("Identidade - Quem é você?")
def test_identidade_1():
    return gerar_resposta("quem é você")

@teste("Identidade - Quem te criou?")
def test_identidade_2():
    return gerar_resposta("quem te criou")

@teste("Saudação - Olá")
def test_saudacao_1():
    return gerar_resposta("olá")

@teste("Saudação - Oi")
def test_saudacao_2():
    return gerar_resposta("oi!")

@teste("Estado - Como você está?")
def test_estado():
    return gerar_resposta("como você está")

# Teste de aprendizado
print(f"\n{'='*70}")
print("Teste de Aprendizado - Múltiplos passos")
print('='*70)

pergunta_aprendizado = "teste automatizado - cor do oceano"
resposta_aprendizado = "O oceano é azul devido à absorção de luz"

print("\n1. Ensinar ALICI sobre nova informação...")
aprender(pergunta_aprendizado, resposta_aprendizado)
print("   ✅ Informação ensinada")

print("\n2. Verificar memória direta...")
memoria = buscar_memoria(pergunta_aprendizado)
if memoria:
    print(f"   ✅ Recuperado da memória: {memoria[:100]}...")
    passou += 1
else:
    print("   ❌ Não encontrado na memória")

total += 1

print("\n3. Testar resposta via engine...")
resposta_engine = gerar_resposta(pergunta_aprendizado)
if resposta_engine and resposta_aprendizado in resposta_engine:
    print(f"   ✅ Engine respondeu corretamente")
    passou += 1
else:
    print("   ❌ Engine não respondeu como esperado")

total += 1

# ==================================================
# RESUMO
# ==================================================

print("\n" + "=" * 70)
print("📊 RESUMO DOS TESTES")
print("=" * 70)

percentual = (passou / total * 100) if total > 0 else 0

print(f"\n✅ Testes aprovados: {passou}/{total} ({percentual:.1f}%)")

if passou == total:
    print("\n🎉 TODOS OS TESTES PASSARAM!")
    print("✅ ALICI está 100% operacional!")
    print("\n🚀 Sistema pronto para produção!")
elif passou >= total * 0.8:
    print("\n✅ Sistema operacional com pequenos avisos")
    print(f"⚠️  {total - passou} teste(s) falharam")
else:
    print("\n⚠️  ATENÇÃO: Alguns testes falharam")
    print(f"❌ {total - passou} teste(s) não passaram")
    print("\n🔍 Revise os erros acima")

print("\n" + "=" * 70)
print("🤖 ALICI™ - Teste Completo Finalizado")
print("=" * 70)

# Exit code baseado no resultado
sys.exit(0 if passou == total else 1)
