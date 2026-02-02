#!/usr/bin/env python3
"""
teste_pesquisa_web.py - Teste de Pesquisa Web e Detecção de Intenção
Valida o sistema de web search e detecção de intenção
"""

import sys

print("=" * 70)
print("🔍 TESTE DE PESQUISA WEB E DETECÇÃO DE INTENÇÃO")
print("=" * 70)

# Importar módulos
try:
    from intencao import precisa_pesquisa_web
    from web_search import buscar_na_web
    print("\n✅ Módulos importados com sucesso")
except Exception as e:
    print(f"\n❌ Erro ao importar módulos: {e}")
    sys.exit(1)

# ==================================================
# TESTE 1: DETECÇÃO DE INTENÇÃO
# ==================================================
print("\n" + "=" * 70)
print("1️⃣  TESTE DE DETECÇÃO DE INTENÇÃO")
print("=" * 70)

# Perguntas que devem acionar pesquisa web
perguntas_web = [
    "como fazer um bolo de chocolate",
    "qual é a previsão do tempo hoje",
    "quem ganhou o jogo ontem",
    "preço do bitcoin agora",
    "receita de lasanha",
    "como consertar torneira",
    "melhor celular 2026",
    "o que aconteceu hoje no mundo",
]

# Perguntas que NÃO devem acionar pesquisa web
perguntas_local = [
    "quem é você",
    "como você está",
    "olá",
    "qual seu nome",
    "você pode me ajudar",
]

print("\n📝 Testando perguntas que DEVEM acionar pesquisa web:")
acertos_web = 0
for pergunta in perguntas_web:
    precisa = precisa_pesquisa_web(pergunta)
    status = "✅" if precisa else "❌"
    print(f"   {status} '{pergunta}' → {'WEB ✓' if precisa else 'LOCAL ✗'}")
    if precisa:
        acertos_web += 1

print(f"\n📊 Acurácia: {acertos_web}/{len(perguntas_web)} ({acertos_web/len(perguntas_web)*100:.1f}%)")

print("\n📝 Testando perguntas que NÃO devem acionar pesquisa web:")
acertos_local = 0
for pergunta in perguntas_local:
    precisa = precisa_pesquisa_web(pergunta)
    status = "✅" if not precisa else "❌"
    print(f"   {status} '{pergunta}' → {'LOCAL ✓' if not precisa else 'WEB ✗'}")
    if not precisa:
        acertos_local += 1

print(f"\n📊 Acurácia: {acertos_local}/{len(perguntas_local)} ({acertos_local/len(perguntas_local)*100:.1f}%)")

# Acurácia geral
total = len(perguntas_web) + len(perguntas_local)
acertos = acertos_web + acertos_local
acuracia_geral = (acertos / total * 100)

print(f"\n{'='*70}")
print(f"📊 ACURÁCIA GERAL: {acertos}/{total} ({acuracia_geral:.1f}%)")
print(f"{'='*70}")

# ==================================================
# TESTE 2: BUSCA WEB (OPCIONAL)
# ==================================================
print("\n" + "=" * 70)
print("2️⃣  TESTE DE BUSCA WEB (OPCIONAL)")
print("=" * 70)

print("\n⚠️  Teste de busca web requer conexão com internet")
print("   e pode falhar se DuckDuckGo estiver indisponível\n")

resposta = input("Deseja testar busca web real? (s/n): ").strip().lower()

if resposta in ['s', 'sim', 'y', 'yes']:
    print("\n🔍 Testando busca na web...")
    
    pergunta_teste = "capital da França"
    print(f"\n📝 Pergunta: '{pergunta_teste}'")
    
    try:
        resultado = buscar_na_web(pergunta_teste)
        
        if resultado:
            print("\n✅ Busca realizada com sucesso!")
            print(f"\n📊 Resultado:")
            print(f"   Resposta: {resultado.get('resposta', 'N/A')[:150]}...")
            print(f"   Confiança: {resultado.get('confianca', 0):.2f}")
            print(f"   Fonte: {resultado.get('fonte', 'N/A')}")
        else:
            print("\n⚠️  Busca não retornou resultado")
            print("   Isso pode ser normal se não houver resultados")
            
    except Exception as e:
        print(f"\n❌ Erro na busca: {e}")
        print("   Isso pode acontecer se:")
        print("     • Não há conexão com internet")
        print("     • DuckDuckGo está indisponível")
        print("     • Rate limit atingido")
else:
    print("\n⏭️  Pulando teste de busca web real")

# ==================================================
# TESTE 3: INTEGRAÇÃO COM ENGINE
# ==================================================
print("\n" + "=" * 70)
print("3️⃣  TESTE DE INTEGRAÇÃO COM ENGINE")
print("=" * 70)

try:
    from engine import gerar_resposta
    
    print("\n📝 Testando resposta via engine...")
    print("   Pergunta que pode acionar web search:")
    
    pergunta = "como fazer um bolo"
    print(f"\n   '{pergunta}'")
    
    resposta = gerar_resposta(pergunta)
    
    if resposta:
        print("\n✅ Engine respondeu com sucesso")
        preview = resposta[:200] + "..." if len(resposta) > 200 else resposta
        print(f"\n   Resposta: {preview}")
    else:
        print("\n⚠️  Engine não retornou resposta")
        
except Exception as e:
    print(f"\n❌ Erro ao testar engine: {e}")

# ==================================================
# RESUMO
# ==================================================
print("\n" + "=" * 70)
print("📊 RESUMO DOS TESTES")
print("=" * 70)

print(f"""
✅ Detecção de Intenção:
   • Acurácia geral: {acuracia_geral:.1f}%
   • Perguntas web: {acertos_web}/{len(perguntas_web)} corretas
   • Perguntas locais: {acertos_local}/{len(perguntas_local)} corretas

📋 Status:
""")

if acuracia_geral >= 90:
    print("   ✅ EXCELENTE - Sistema de intenção funcionando muito bem")
elif acuracia_geral >= 70:
    print("   ✅ BOM - Sistema de intenção funcionando adequadamente")
elif acuracia_geral >= 50:
    print("   ⚠️  REGULAR - Sistema pode precisar de ajustes")
else:
    print("   ❌ RUIM - Sistema precisa de revisão")

print("\n💡 Dicas:")
print("   • Ajuste palavras-chave em intencao.py se necessário")
print("   • Teste busca web real para validar integração completa")
print("   • Monitore logs para identificar falsos positivos/negativos")

print("\n" + "=" * 70)
print("🔍 Teste de Pesquisa Web Finalizado")
print("=" * 70)
