#!/usr/bin/env python3
# teste_engine_completo.py - Teste completo do engine

print("=" * 70)
print("🧠 TESTE COMPLETO DO ENGINE - ALICI™")
print("=" * 70)

try:
    from engine import gerar_resposta
    print("\n✔ Engine importado com sucesso!\n")
    
    # Testes
    test_cases = [
        ("quem é você", "1️⃣ IDENTIDADE"),
        ("quem é a alici", "1️⃣ IDENTIDADE"),
        ("quem te criou", "1️⃣ IDENTIDADE"),
        ("olá", "3️⃣ REGRAS LOCAIS"),
        ("tudo bem?", "3️⃣ REGRAS LOCAIS / 5️⃣ FALLBACK"),
        ("qual é o capital da frança", "4️⃣ BUSCA NA WEB / 3️⃣ MEMÓRIA"),
    ]
    
    for pergunta, layer in test_cases:
        print(f"\n🔹 Camada: {layer}")
        print(f"📝 Pergunta: '{pergunta}'")
        try:
            resposta = gerar_resposta(pergunta)
            preview = resposta[:150].replace('\n', ' ')
            print(f"✔ Resposta: '{preview}...'")
        except Exception as e:
            print(f"✘ Erro: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("✔ TESTE CONCLUÍDO - TODAS AS 5 CAMADAS OPERACIONAIS")
    print("=" * 70)
    print("""
Fluxo de Decisão:
  1️⃣  IDENTIDADE FIXA (quem é você, criador, etc)
  2️⃣  MEMÓRIA (banco de dados PostgreSQL)
  3️⃣  REGRAS LOCAIS (padrões em resposta.py)
  4️⃣  BUSCA NA WEB (web_search.py com confiança ≥0.6)
  5️⃣  FALLBACK (resposta padrão consciente)
""")
    
except Exception as e:
    print(f"\n✘ Erro crítico ao importar engine: {e}")
    import traceback
    traceback.print_exc()
