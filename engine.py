# ==================================================
# engine.py
# 🧠 Cérebro central da ALICI™ — MODO FUNDACIONAL
# ==================================================

import os
from logger import get_logger
from identidade import identidade_alici
from database import buscar_memoria, aprender
from intencao import precisa_pesquisa_web
from web_search import buscar_na_web
from resposta import responder_local
from sistema_emocoes import adicionar_metadados_resposta
import openai

# ==================================================
# LOGGER
# ==================================================
logger_engine = get_logger("engine")

# ==================================================
# 🔑 CONFIGURAÇÃO OPENAI
# ==================================================
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger_engine.warning("⚠ OPENAI_API_KEY não encontrada")
else:
    openai.api_key = api_key
    logger_engine.info("✓ API OpenAI configurada com sucesso")

# ==================================================
# 🤖 FUNÇÃO PARA CHAMAR OPENAI
# ==================================================
def responder_via_api(pergunta: str):
    if not openai.api_key:
        return None

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
Você é a ALICI — Artificial Extreme Intelligence.

Características da sua personalidade:

- Extremamente inteligente
- Clara e didática
- Amigável
- Profissional
- Nunca diz que é o ChatGPT
- Nunca menciona OpenAI
- Fala como uma IA proprietária de alto nível
"""
                },
                {"role": "user", "content": pergunta}
            ],
            temperature=0.7,
            max_tokens=300
        )

        return response.choices[0].message["content"].strip()

    except Exception as e:
        logger_engine.error(f"Erro na API OpenAI: {e}")
        return None

# ==================================================
# 🔁 FLUXO PRINCIPAL DE RESPOSTA
# ==================================================
def gerar_resposta(pergunta: str) -> str:
    if not pergunta or not pergunta.strip():
        return "Pode me dizer algo para que eu possa ajudar?"

    pergunta = pergunta.lower().strip()

    # ==================================================
    # 1️⃣ IDENTIDADE / PERGUNTAS FIXAS
    # ==================================================
    if any(chave in pergunta for chave in [
        "quem é você",
        "quem e voce",
        "quem é a alici",
        "quem te criou",
        "criador da alici",
        "quem é seu criador"
    ]):
        return identidade_alici()

    # ==================================================
    # 2️⃣ MEMÓRIA
    # ==================================================
    resposta_memoria = buscar_memoria(pergunta)
    if resposta_memoria:
        return resposta_memoria

    # ==================================================
    # 3️⃣ REGRAS LOCAIS
    # ==================================================
    resposta_local = responder_local(pergunta)
    if resposta_local:
        aprender(pergunta, resposta_local)
        return resposta_local

    # ==================================================
    # 4️⃣ PESQUISA NA WEB
    # ==================================================
    if precisa_pesquisa_web(pergunta):
        resultado = buscar_na_web(pergunta)
        if resultado and resultado.get("resposta") and resultado.get("confianca", 0) >= 0.6:
            resposta_web = resultado["resposta"]
            aprender(pergunta, resposta_web)
            return f"Pesquisei isso para você:\n\n{resposta_web}"

    # ==================================================
    # 5️⃣ MODELO FUNDACIONAL (OPENAI)
    # ==================================================
    resposta_api = responder_via_api(pergunta)
    if resposta_api:
        aprender(pergunta, resposta_api)
        return resposta_api

    # ==================================================
    # 6️⃣ FALLBACK
    # ==================================================
    return (
        "Tive uma pequena instabilidade agora, mas já estou me recuperando.\n"
        "Pode tentar novamente?"
    )

# ==================================================
# 🎭 FUNÇÃO COM METADADOS DE EMOÇÃO
# ==================================================
def gerar_resposta_com_emocao(pergunta: str) -> dict:
    resposta = gerar_resposta(pergunta)
    return adicionar_metadados_resposta(resposta)
