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
from openai import OpenAI
from alici_api.services.text_model_r2 import predict_intent_from_text
from alici_api.services.text_model_hf import predict_intent_from_text_hf

# ==================================================
# LOGGER
# ==================================================
logger_engine = get_logger("engine")

# ==================================================
# 🔑 CONFIGURAÇÃO OPENAI (SDK 1.x)
# ==================================================

api_key = os.getenv("OPENAI_API_KEY")

client = None

if not api_key:
    logger_engine.warning("⚠ OPENAI_API_KEY não encontrada")
else:
    try:
        client = OpenAI()  # Lê automaticamente da variável de ambiente
        logger_engine.info("✓ Cliente OpenAI inicializado com sucesso")
    except Exception as e:
        logger_engine.error(f"Erro ao inicializar OpenAI: {e}")
        client = None


# ==================================================
# 🤖 CHAMADA AO MODELO FUNDACIONAL
# ==================================================
def responder_via_api(pergunta: str) -> str | None:

    if not client:
        logger_engine.warning("⚠ Cliente OpenAI indisponível")
        return None

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é a ALICI — Artificial Extreme Intelligence.\n\n"
                        "Características:\n"
                        "- Extremamente inteligente\n"
                        "- Clara e didática\n"
                        "- Amigável\n"
                        "- Profissional\n"
                        "- Nunca diz que é ChatGPT\n"
                        "- Nunca menciona OpenAI\n"
                        "- Fala como IA proprietária de alto nível"
                    )
                },
                {
                    "role": "user",
                    "content": pergunta
                }
            ],
            temperature=0.7,
            max_tokens=400,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        logger_engine.error(f"Erro na API OpenAI: {e}")
        return None


# ==================================================
# 🔁 FLUXO PRINCIPAL
# ==================================================
def gerar_resposta(pergunta: str) -> str:

    if not pergunta or not pergunta.strip():
        return "Pode me dizer algo para que eu possa ajudar?"

    pergunta_original = pergunta.strip()
    pergunta_normalizada = pergunta_original.lower()

    # ==================================================
    # 1️⃣ IDENTIDADE
    # ==================================================
    if any(chave in pergunta_normalizada for chave in [
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
    resposta_memoria = buscar_memoria(pergunta_original)
    if resposta_memoria:
        return resposta_memoria

    # ==================================================
    # 3️⃣ RESPOSTAS LOCAIS
    # ==================================================
    resposta_local = responder_local(pergunta_original)
    if resposta_local:
        aprender(pergunta_original, resposta_local)
        return resposta_local

    # ==================================================
    # 3.1️⃣ CLASSIFICADOR DE INTENÇÃO (MODELO R2 ou HuggingFace)
    # ==================================================
    intent_prediction = predict_intent_from_text(pergunta_original)
    min_confidence = float(os.getenv("ALICI_INTENT_MIN_CONFIDENCE", "0.55"))

    if not intent_prediction:
        intent_prediction = predict_intent_from_text_hf(pergunta_original)
        if intent_prediction:
            logger_engine.info("Predição via modelo HuggingFace (fallback)")

    if intent_prediction:
        confidence = float(intent_prediction.get("confidence", 0.0))
        predicted_tag = intent_prediction.get("tag")
        predicted_response = intent_prediction.get("response")

        logger_engine.info(
            f"Predição intent -> tag={predicted_tag} confidence={confidence:.4f}"
        )

        if predicted_response and confidence >= min_confidence:
            aprender(pergunta_original, predicted_response)
            return predicted_response

    # ==================================================
    # 4️⃣ PESQUISA NA WEB
    # ==================================================
    if precisa_pesquisa_web(pergunta_original):
        resultado = buscar_na_web(pergunta_original)

        if (
            resultado
            and resultado.get("resposta")
            and resultado.get("confianca", 0) >= 0.6
        ):
            resposta_web = resultado["resposta"]
            aprender(pergunta_original, resposta_web)
            return f"Pesquisei isso para você:\n\n{resposta_web}"

    # ==================================================
    # 5️⃣ MODELO FUNDACIONAL
    # ==================================================
    resposta_api = responder_via_api(pergunta_original)

    if resposta_api:
        aprender(pergunta_original, resposta_api)
        return resposta_api

    # ==================================================
    # 6️⃣ FALLBACK
    # ==================================================
    logger_engine.warning("⚠ Todas as camadas falharam, acionando fallback")

    return (
        "Tive uma pequena instabilidade agora, mas já estou me recuperando.\n"
        "Pode tentar novamente?"
    )


# ==================================================
# 🎭 RESPOSTA COM EMOÇÃO
# ==================================================
def gerar_resposta_com_emocao(pergunta: str) -> dict:
    resposta = gerar_resposta(pergunta)
    return adicionar_metadados_resposta(resposta)
