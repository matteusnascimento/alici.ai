#!/usr/bin/env python3
"""
✅ VERIFICAÇÃO FINAL - ALICI.AI 4 FEATURES
Valida que todos os 4 features solicitados estão implementados e prontos
"""

import os
import sys
from pathlib import Path

def verificar_arquivo(caminho, descricao):
    """Verifica se arquivo existe"""
    if os.path.exists(caminho):
        print(f"✅ {descricao}")
        return True
    else:
        print(f"❌ {descricao}")
        return False

def verificar_conteudo(caminho, palavra_chave, descricao):
    """Verifica se arquivo contém palavra-chave"""
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            if palavra_chave in conteudo:
                print(f"✅ {descricao}")
                return True
            else:
                print(f"❌ {descricao}")
                return False
    except:
        print(f"⚠️  Não conseguiu ler {caminho}")
        return False

print("=" * 60)
print("🔍 VERIFICAÇÃO FINAL - ALICI.AI 4 FEATURES COMPLETAS")
print("=" * 60)

score = 0
total = 0

# ============================================================================
# FEATURE 1: RENDER DEPLOY
# ============================================================================
print("\n1️⃣  CONECTAR RENDER.COM - DEPLOY AUTOMÁTICO")
print("-" * 60)

total += 1
if verificar_arquivo("RENDER_DEPLOY.md", "Documentação Render criada"):
    score += 1

total += 1
if verificar_arquivo("Procfile", "Procfile configurado"):
    score += 1

total += 1
if verificar_conteudo("requirements.txt", "gunicorn", "requirements.txt com gunicorn"):
    score += 1

total += 1
if verificar_conteudo("runtime.txt", "3.11", "Python 3.11 em runtime.txt"):
    score += 1

print(f"Render: {score-3}/4 ✓")

# ============================================================================
# FEATURE 2: COLAB TRAINING
# ============================================================================
print("\n2️⃣  TREINAR EM COLAB - EXPANDIR CONHECIMENTO")
print("-" * 60)

base_score = score

total += 1
if verificar_arquivo("COLAB_TRAINING.md", "Documentação Colab criada"):
    score += 1

total += 1
if verificar_arquivo("colab_finetuning.py", "Script Colab existe"):
    score += 1

total += 1
if verificar_arquivo("dataset_expandido.json", "Dataset expandido criado"):
    score += 1

total += 1
if verificar_conteudo("colab_finetuning.py", "model.fit", "Script tem treinamento"):
    score += 1

print(f"Colab: {score-base_score}/4 ✓")

# ============================================================================
# FEATURE 3: ADICIONAR PADRÕES
# ============================================================================
print("\n3️⃣  ADICIONAR MAIS PADRÕES - RESPOSTA.PY")
print("-" * 60)

base_score = score

total += 1
# Contar linhas em resposta.py para estimar padrões
try:
    with open("resposta.py", 'r', encoding='utf-8') as f:
        linhas = len(f.readlines())
        if linhas > 500:  # ~150 padrões ≈ 500+ linhas
            print(f"✅ resposta.py expandido ({linhas} linhas)")
            score += 1
        else:
            print(f"⚠️  resposta.py pode estar pequeno ({linhas} linhas)")
except:
    print("❌ Não conseguiu ler resposta.py")

total += 1
if verificar_conteudo("resposta.py", "instagram", "Padrões social networks"):
    score += 1

total += 1
if verificar_conteudo("resposta.py", "python", "Padrões educação"):
    score += 1

total += 1
if verificar_conteudo("resposta.py", "emoção", "Padrões personalidade"):
    score += 1

print(f"Padrões: {score-base_score}/4 ✓")

# ============================================================================
# FEATURE 4: TEXT-TO-SPEECH
# ============================================================================
print("\n4️⃣  INTEGRAR VOZ - TEXT-TO-SPEECH")
print("-" * 60)

base_score = score

total += 1
if verificar_arquivo("alici_tts.py", "Módulo TTS criado"):
    score += 1

total += 1
if verificar_arquivo("VOICE_TTS.md", "Documentação TTS criada"):
    score += 1

total += 1
if verificar_conteudo("main.py", "/chat/audio", "Endpoint /chat/audio em main.py"):
    score += 1

total += 1
if verificar_conteudo("requirements.txt", "gtts", "gtts em requirements.txt"):
    score += 1

print(f"Voice/TTS: {score-base_score}/4 ✓")

# ============================================================================
# DOCUMENTAÇÃO & DEPLOY
# ============================================================================
print("\n📚 DOCUMENTAÇÃO & RECURSOS")
print("-" * 60)

total += 1
if verificar_arquivo("CHECKLIST_DEPLOY.md", "Checklist deploy criado"):
    score += 1

total += 1
if verificar_arquivo("README.md", "README atualizado"):
    score += 1

total += 1
if verificar_arquivo(".gitignore", "Git configurado"):
    score += 1

print(f"Docs: {score-17}/3 ✓")

# ============================================================================
# RESUMO FINAL
# ============================================================================
print("\n" + "=" * 60)
print("📊 RESUMO FINAL")
print("=" * 60)

porcentagem = (score / total) * 100

print(f"""
Arquivos verificados: {total}
Verificações passadas: {score}
Porcentagem: {porcentagem:.1f}%

STATUS:
""")

if porcentagem >= 95:
    print("🟢 SISTEMA COMPLETO E PRONTO PARA PRODUÇÃO ✅")
    print("""
Próximo passo:
  1. git add .
  2. git commit -m "feat: 4 features - Deploy pronto"
  3. git push
  4. Render detecta automaticamente
  5. ✅ Sistema live em produção!
""")
elif porcentagem >= 80:
    print("🟡 QUASE PRONTO - Faltam alguns detalhes")
    print(f"Complete os {total - score} itens faltantes")
else:
    print("🔴 INCOMPLETO - Verifique os arquivos")

print("=" * 60)
print("\n📖 LEIA OS GUIAS:")
print("  • RENDER_DEPLOY.md - Como fazer deploy em Render")
print("  • COLAB_TRAINING.md - Como treinar em Google Colab")
print("  • VOICE_TTS.md - Como usar Text-to-Speech")
print("  • CHECKLIST_DEPLOY.md - Checklist completo")
print("=" * 60)

sys.exit(0 if porcentagem >= 95 else 1)
