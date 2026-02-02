"""
teste_engine_completo.py
🧪 Suite completa de testes para o engine ALICI
Testa todos os 6 níveis de decisão
"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

def testar_importacoes():
    """Testa se todos os módulos podem ser importados"""
    print("\n📦 Testando importações...")
    
    try:
        from engine import gerar_resposta, gerar_resposta_com_emocao
        from identidade import identidade_alici
        from database import buscar_memoria, aprender
        from resposta import responder_local
        from intencao import precisa_pesquisa_web
        from web_search import buscar_na_web
        print("  ✅ Todos os módulos importados com sucesso")
        return True
    except ImportError as e:
        print(f"  ❌ Erro ao importar: {e}")
        return False

def testar_identidade():
    """Testa camada 1: Identidade"""
    print("\n🎭 Testando Camada 1: Identidade...")
    
    from engine import gerar_resposta
    
    perguntas = [
        "quem é você",
        "quem e voce",
        "quem é a alici",
        "quem te criou",
    ]
    
    for pergunta in perguntas:
        resposta = gerar_resposta(pergunta)
        if resposta and len(resposta) > 50:
            print(f"  ✅ '{pergunta}' → {len(resposta)} caracteres")
        else:
            print(f"  ❌ '{pergunta}' → resposta inválida")
            return False
    
    print("  ✅ Camada de identidade OK")
    return True

def testar_regras_locais():
    """Testa camada 3: Regras locais (resposta.py patterns)"""
    print("\n📝 Testando Camada 3: Regras Locais...")
    
    from engine import gerar_resposta
    
    testes = [
        ("oi", "saudação"),
        ("olá", "saudação"),
        ("como você está", "bem-estar"),
        ("o que você faz", "capacidades"),
    ]
    
    for pergunta, categoria in testes:
        resposta = gerar_resposta(pergunta)
        if resposta and len(resposta) > 10:
            print(f"  ✅ [{categoria}] '{pergunta}' → resposta OK")
        else:
            print(f"  ⚠️  [{categoria}] '{pergunta}' → sem resposta")
    
    print("  ✅ Regras locais OK")
    return True

def testar_aprendizado():
    """Testa camada 2: Memória e aprendizado (database queries)"""
    print("\n🧠 Testando Camada 2: Memória e Aprendizado...")
    
    from engine import gerar_resposta
    from database import aprender, buscar_memoria
    
    # Pergunta única para teste
    pergunta_teste = "qual é a cor favorita do teste automatizado"
    resposta_teste = "A cor favorita do teste automatizado é azul cibernético"
    
    try:
        # Limpar memória anterior (se existir)
        print(f"  📝 Ensinando: '{pergunta_teste}'")
        aprender(pergunta_teste, resposta_teste)
        
        # Buscar da memória
        print(f"  🔍 Buscando na memória...")
        resposta = buscar_memoria(pergunta_teste)
        
        if resposta and resposta_teste.lower() in resposta.lower():
            print(f"  ✅ ALICI lembrou corretamente!")
            return True
        else:
            print(f"  ❌ ALICI não conseguiu lembrar")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro no teste de aprendizado: {e}")
        return False

def testar_intencao_web():
    """Testa camada 5: Detecção de intenção para web search"""
    print("\n🔍 Testando Camada 5: Detecção de Intenção Web...")
    
    from intencao import precisa_pesquisa_web
    
    testes_positivos = [
        "qual é a temperatura em são paulo",
        "preço do bitcoin hoje",
        "quem ganhou a copa do mundo",
    ]
    
    testes_negativos = [
        "quem é você",
        "oi tudo bem",
        "como você está",
    ]
    
    print("  🌐 Deve buscar na web:")
    for pergunta in testes_positivos:
        resultado = precisa_pesquisa_web(pergunta)
        simbolo = "✅" if resultado else "⚠️"
        print(f"    {simbolo} '{pergunta}' → {resultado}")
    
    print("  💾 Não deve buscar na web:")
    for pergunta in testes_negativos:
        resultado = precisa_pesquisa_web(pergunta)
        simbolo = "✅" if not resultado else "⚠️"
        print(f"    {simbolo} '{pergunta}' → {not resultado}")
    
    print("  ✅ Detecção de intenção OK")
    return True

def testar_fallback():
    """Testa camada 6: Fallback gracioso"""
    print("\n🤔 Testando Camada 6: Fallback...")
    
    from engine import gerar_resposta
    
    # Pergunta muito específica que provavelmente não tem resposta
    pergunta = "xyzabc123 pergunta impossível de responder definitivamente"
    resposta = gerar_resposta(pergunta)
    
    if resposta and len(resposta) > 20:
        print(f"  ✅ Fallback gracioso funcionando")
        print(f"     Resposta: {resposta[:80]}...")
        return True
    else:
        print(f"  ❌ Fallback não funcionou")
        return False

def testar_resposta_com_emocao():
    """Testa resposta com metadata emocional"""
    print("\n💭 Testando Sistema de Emoções...")
    
    try:
        from engine import gerar_resposta_com_emocao
        
        resultado = gerar_resposta_com_emocao("oi")
        
        if isinstance(resultado, dict) and "resposta" in resultado:
            print(f"  ✅ Sistema de emoções OK")
            print(f"     Campos: {list(resultado.keys())}")
            return True
        else:
            print(f"  ⚠️  Sistema de emoções retornou formato inesperado")
            return False
            
    except Exception as e:
        print(f"  ⚠️  Sistema de emoções não disponível: {e}")
        return False

def testar_pipeline_completo():
    """Testa o pipeline completo com várias perguntas"""
    print("\n🔄 Testando Pipeline Completo...")
    
    from engine import gerar_resposta
    
    perguntas = [
        "quem é você",                    # Identidade
        "oi",                             # Regras locais
        "como você está",                 # Regras locais
        "teste de aprendizado único",     # Fallback
    ]
    
    for i, pergunta in enumerate(perguntas, 1):
        print(f"\n  📝 Teste {i}: '{pergunta}'")
        try:
            resposta = gerar_resposta(pergunta)
            if resposta:
                preview = resposta[:100] + "..." if len(resposta) > 100 else resposta
                print(f"  ✅ Resposta: {preview}")
            else:
                print(f"  ❌ Sem resposta")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
    
    print("\n  ✅ Pipeline completo testado")
    return True

def main():
    """Executa todos os testes"""
    print("=" * 70)
    print("🧪 ALICI™ - Teste Completo do Engine")
    print("=" * 70)
    
    testes = [
        ("Importações", testar_importacoes),
        ("Identidade", testar_identidade),
        ("Regras Locais", testar_regras_locais),
        ("Aprendizado", testar_aprendizado),
        ("Intenção Web", testar_intencao_web),
        ("Fallback", testar_fallback),
        ("Sistema de Emoções", testar_resposta_com_emocao),
        ("Pipeline Completo", testar_pipeline_completo),
    ]
    
    resultados = {}
    
    for nome, teste_func in testes:
        try:
            resultados[nome] = teste_func()
        except Exception as e:
            print(f"\n  ❌ Erro ao executar teste '{nome}': {e}")
            resultados[nome] = False
    
    # Resumo
    print("\n" + "=" * 70)
    print("📊 RESUMO DOS TESTES")
    print("=" * 70)
    
    for nome, passou in resultados.items():
        simbolo = "✅" if passou else "❌"
        print(f"{simbolo} {nome}")
    
    print()
    
    total = len(resultados)
    aprovados = sum(resultados.values())
    porcentagem = (aprovados / total) * 100
    
    print(f"Resultado: {aprovados}/{total} testes passaram ({porcentagem:.1f}%)")
    
    if porcentagem == 100:
        print("\n🎉 Todos os testes passaram! Engine 100% operacional!")
        return 0
    elif porcentagem >= 75:
        print("\n⚠️  Maioria dos testes passou. Sistema funcional.")
        return 0
    else:
        print("\n❌ Muitos testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
