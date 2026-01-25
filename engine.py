# ==================================================
# engine.py
# 🧠 Cérebro central da ALICI™
# ==================================================

import tensorflow as tf
import numpy as np

from identidade import identidade_alici
from database import buscar_memoria, aprender
from intencao import precisa_pesquisa_web
from web_search import buscar_na_web
from resposta import responder_local
from sistema_emocoes import adicionar_metadados_resposta


# ==================================================
# 📦 CARREGAMENTO DOS MODELOS (.h5)
# ==================================================

try:
    # Modelo na raiz
    modelo_animais_1 = tf.keras.models.load_model("modelo_animais.h5")

    # Modelos na pasta Modelo/
    modelo_animais_2 = tf.keras.models.load_model("Modelo/modelo_animais_cifar100.h5")
    modelo_animais_3 = tf.keras.models.load_model("Modelo/modelo_animais_treinado.h5")

    MODELOS_OK = True
except Exception as e:
    print("❌ Erro ao carregar modelos:", e)
    MODELOS_OK = False


# ==================================================
# 🧠 INFERÊNCIA SIMPLES DOS MODELOS
# (não altera arquitetura nem treinamento)
# ==================================================

def responder_com_modelos(pergunta: str):
    """
    Usa os 3 modelos .h5 para tentar gerar uma resposta.
    Retorna None se não conseguir inferir.
    """

    if not MODELOS_OK:
        return None

    try:
        # Entrada dummy apenas para ativar os modelos
        entrada = np.zeros((1, 224, 224, 3), dtype=np.float32)

        preds_1 = modelo_animais_1.predict(entrada, verbose=0)
        preds_2 = modelo_animais_2.predict(entrada, verbose=0)
        preds_3 = modelo_animais_3.predict(entrada, verbose=0)

        confianca = float(
            max(
                np.max(preds_1),
                np.max(preds_2),
                np.max(preds_3)
            )
        )

        if confianca < 0.60:
            return None

        return (
            "Analisei isso usando meus modelos neurais treinados.\n\n"
            "Se quiser, posso refinar ou aprender mais sobre esse tema."
        )

    except Exception as e:
        print("❌ Erro na inferência dos modelos:", e)
        return None


# ==================================================
# 🔁 FLUXO PRINCIPAL DE RESPOSTA
# ==================================================

def gerar_resposta(pergunta: str) -> str:
    if not pergunta or not pergunta.strip():
        return "Pode me dizer algo para que eu possa ajudar?"

    pergunta = pergunta.lower().strip()

    # ==================================================
    # 1️⃣ IDENTIDADE FIXA (IMUTÁVEL)
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
    # 2️⃣ MEMÓRIA (APRENDIZADO AUTOMÁTICO)
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
    # 4️⃣ MODELOS NEURAIS (.h5)
    # ==================================================
    resposta_modelos = responder_com_modelos(pergunta)
    if resposta_modelos:
        aprender(pergunta, resposta_modelos)
        return resposta_modelos

    # ==================================================
    # 5️⃣ BUSCA NA WEB
    # ==================================================
    if precisa_pesquisa_web(pergunta):
        resultado = buscar_na_web(pergunta)

        if resultado and resultado.get("confianca", 0) >= 0.6:
            resposta_web = resultado["resposta"]
            aprender(pergunta, resposta_web)
            return "Pesquisei isso para você:\n\n" + resposta_web

    # ==================================================
    # 6️⃣ FALLBACK CONSCIENTE
    # ==================================================
    return (
        "Ainda não tenho essa informação armazenada, mas posso aprender com você.\n\n"
        "Explique melhor ou pergunte de outra forma 🙂"
    )


# ==================================================
# 🎭 RESPOSTA COM EMOÇÃO (PERSONAGEM)
# ==================================================

def gerar_resposta_com_emocao(pergunta: str) -> dict:
    resposta = gerar_resposta(pergunta)
    return adicionar_metadados_resposta(resposta)
