#!/usr/bin/env python3
"""
teste_interativo_alici.py - Teste Interativo da ALICI
Interface de linha de comando para conversar com a ALICI
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Verificar DATABASE_URL
if not os.getenv("DATABASE_URL"):
    print("❌ ERRO: DATABASE_URL não configurado no .env")
    print("   Configure DATABASE_URL antes de usar a ALICI")
    sys.exit(1)

# Importar engine
try:
    from engine import gerar_resposta
except Exception as e:
    print(f"❌ Erro ao importar engine: {e}")
    sys.exit(1)

print("=" * 70)
print("🤖 ALICI™ - MODO INTERATIVO")
print("=" * 70)
print("""
Bem-vindo ao teste interativo da ALICI!

Comandos especiais:
  • 'sair', 'exit', 'quit' - Encerrar
  • 'limpar', 'clear' - Limpar tela
  • 'ajuda', 'help' - Mostrar ajuda

Digite suas perguntas e a ALICI responderá!
""")
print("=" * 70)

# Contador de interações
contador = 0

def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_ajuda():
    """Mostra informações de ajuda"""
    print("\n" + "=" * 70)
    print("📚 AJUDA - ALICI™")
    print("=" * 70)
    print("""
A ALICI possui 5 camadas de decisão:

1️⃣  IDENTIDADE - Perguntas sobre quem ela é
   Exemplo: "quem é você", "quem te criou"

2️⃣  MEMÓRIA - Recupera informações já aprendidas
   A ALICI lembra de conversas anteriores

3️⃣  REGRAS LOCAIS - Padrões pré-programados
   Exemplo: "olá", "como você está"

4️⃣  MODELOS NEURAIS - Inferência com ML (se disponível)
   Usa modelos .h5 treinados

5️⃣  BUSCA WEB - DuckDuckGo para info externa
   Exemplo: "como fazer bolo", "preço bitcoin"

6️⃣  FALLBACK - Resposta honesta quando não sabe
   "Ainda não tenho essa informação..."

💡 Dicas:
• Seja claro e específico nas perguntas
• A ALICI aprende com cada interação
• Perguntas repetidas ficam mais rápidas
""")
    print("=" * 70)

# Loop principal
while True:
    try:
        # Prompt
        print(f"\n{'─' * 70}")
        pergunta = input("Você: ").strip()
        
        # Verificar se está vazio
        if not pergunta:
            continue
        
        # Comandos especiais
        if pergunta.lower() in ['sair', 'exit', 'quit']:
            print("\n👋 Até logo! Foi um prazer conversar com você!")
            print(f"📊 Total de interações: {contador}")
            break
        
        if pergunta.lower() in ['limpar', 'clear']:
            limpar_tela()
            print("=" * 70)
            print("🤖 ALICI™ - MODO INTERATIVO")
            print("=" * 70)
            continue
        
        if pergunta.lower() in ['ajuda', 'help']:
            mostrar_ajuda()
            continue
        
        # Processar pergunta
        contador += 1
        print(f"\n{'─' * 70}")
        print("🤖 ALICI:", end=" ")
        
        # Gerar resposta
        resposta = gerar_resposta(pergunta)
        print(resposta)
        
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário. Até logo!")
        print(f"📊 Total de interações: {contador}")
        break
    
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        print("Tente novamente ou digite 'sair' para encerrar.")

print("\n" + "=" * 70)
print("🤖 ALICI™ - Sessão Encerrada")
print("=" * 70)
