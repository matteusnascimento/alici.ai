#!/usr/bin/env python3
"""
teste_engine_completo.py - Teste Completo do Engine de 5 Camadas
Valida todas as funcionalidades principais da ALICI™
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Verificar DATABASE_URL
if not os.getenv("DATABASE_URL"):
    print("❌ ERRO: DATABASE_URL não configurado no .env")
    exit(1)

from engine import gerar_resposta
from identidade import identidade_alici
from database import buscar_memoria, aprender
from resposta import responder_local
from intencao import precisa_pesquisa_web

print("=" * 70)
print("🤖 TESTE COMPLETO DO ENGINE ALICI™")
print("=" * 70)

# Contador de testes
total_testes = 0
testes_ok = 0

def testar(nome, funcao, esperado=True):
    """Helper para executar testes"""
    global total_testes, testes_ok
    total_testes += 1
    
    print(f"\n📝 Teste {total_testes}: {nome}")
    try:
        resultado = funcao()
        sucesso = (bool(resultado) == esperado) if esperado is not None else True
        
        if sucesso:
            testes_ok += 1
            print(f"   ✅ PASSOU")
            if resultado and isinstance(resultado, str):
                print(f"   Resposta: {resultado[:100]}..." if len(resultado) > 100 else f"   Resposta: {resultado}")
        else:
            print(f"   ❌ FALHOU - Esperado: {esperado}, Obtido: {bool(resultado)}")
            
        return resultado
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
        return None


# ==================================================
# 1️⃣ TESTE DE IDENTIDADE
# ==================================================
print("\n" + "=" * 70)
print("1️⃣  CAMADA DE IDENTIDADE")
print("=" * 70)

testar(
    "Identidade ALICI",
    lambda: gerar_resposta("quem é você"),
    esperado=True
)

testar(
    "Criador da ALICI",
    lambda: gerar_resposta("quem te criou"),
    esperado=True
)


# ==================================================
# 2️⃣ TESTE DE MEMÓRIA
# ==================================================
print("\n" + "=" * 70)
print("2️⃣  CAMADA DE MEMÓRIA (APRENDIZADO)")
print("=" * 70)

# Testar aprendizado
pergunta_teste = "qual é a cor do céu no teste"
resposta_teste = "O céu é azul devido ao espalhamento Rayleigh"

print(f"\n🧠 Ensinando ALICI: '{pergunta_teste}'")
aprender(pergunta_teste, resposta_teste)

testar(
    "Recuperar da memória",
    lambda: buscar_memoria(pergunta_teste),
    esperado=True
)

testar(
    "Resposta completa via engine",
    lambda: gerar_resposta(pergunta_teste),
    esperado=True
)


# ==================================================
# 3️⃣ TESTE DE REGRAS LOCAIS
# ==================================================
print("\n" + "=" * 70)
print("3️⃣  CAMADA DE REGRAS LOCAIS")
print("=" * 70)

testar(
    "Saudação",
    lambda: gerar_resposta("olá"),
    esperado=True
)

testar(
    "Estado/Como está",
    lambda: gerar_resposta("como você está"),
    esperado=True
)

testar(
    "Capacidades",
    lambda: gerar_resposta("o que você sabe fazer"),
    esperado=True
)


# ==================================================
# 4️⃣ TESTE DE INTENÇÃO (WEB SEARCH)
# ==================================================
print("\n" + "=" * 70)
print("4️⃣  DETECÇÃO DE INTENÇÃO (WEB SEARCH)")
print("=" * 70)

print("\n🔍 Testando detecção de perguntas que precisam busca web:")

perguntas_web = [
    "como fazer um bolo de chocolate",
    "qual é a previsão do tempo hoje",
    "quem ganhou o jogo ontem",
]

for p in perguntas_web:
    precisa = precisa_pesquisa_web(p)
    status = "✅" if precisa else "❌"
    print(f"   {status} '{p}' → {'WEB' if precisa else 'LOCAL'}")


# ==================================================
# 5️⃣ TESTE DE FALLBACK
# ==================================================
print("\n" + "=" * 70)
print("5️⃣  CAMADA DE FALLBACK")
print("=" * 70)

testar(
    "Pergunta desconhecida (fallback gracioso)",
    lambda: gerar_resposta("xyzabc123questionamento completamente aleatorio"),
    esperado=True
)


# ==================================================
# RESUMO FINAL
# ==================================================
print("\n" + "=" * 70)
print("📊 RESUMO DOS TESTES")
print("=" * 70)

percentual = (testes_ok / total_testes * 100) if total_testes > 0 else 0

print(f"\n✅ Testes passados: {testes_ok}/{total_testes} ({percentual:.1f}%)")

if testes_ok == total_testes:
    print("\n🎉 TODOS OS TESTES PASSARAM!")
    print("✅ ALICI está operacional e pronta para uso!")
else:
    print(f"\n⚠️  {total_testes - testes_ok} teste(s) falharam")
    print("🔍 Revise os erros acima")

print("\n" + "=" * 70)
print("🚀 Próximo passo: python main.py")
print("=" * 70)
