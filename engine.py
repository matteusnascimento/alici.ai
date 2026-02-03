# ==================================================
# engine.py
# 🧠 Cérebro central da ALICI™
# ==================================================

# Proteção para imports de TensorFlow (pode falhar em algumas configs)
try:
    import tensorflow as tf
    import numpy as np
    TF_AVAILABLE = True
except Exception as e:
    print(f"⚠️ TensorFlow não disponível: {e}")
    TF_AVAILABLE = False

from identidade import identidade_alici
from database import buscar_memoria, aprender
from intencao import precisa_pesquisa_web
from web_search import buscar_na_web
from resposta import responder_local
from sistema_emocoes import adicionar_metadados_resposta
from logger import get_logger

# Configurar logger
logger_engine = get_logger("engine")


# ==================================================
# 📦 CARREGAMENTO DOS MODELOS (.h5)
# ==================================================

import os

MODELOS_OK = False
modelo_animais_1 = None
modelo_animais_2 = None
modelo_animais_3 = None

try:
    # Tentar carregar modelos de localizações conhecidas
    modelo_paths = [
        "model/modelo_animais.h5",
        "model/modelo_animais_cifar100.h5",
        "model/modelo_animais_treinado.h5",
        "modelo_animais.h5",
    ]
    
    modelos_carregados = 0
    
    for path in modelo_paths:
        if os.path.exists(path):
            try:
                # Proteger contra TensorFlow indisponível
                if not TF_AVAILABLE:
                    continue
                    
                modelo = tf.keras.models.load_model(path)
                if modelos_carregados == 0:
                    modelo_animais_1 = modelo
                elif modelos_carregados == 1:
                    modelo_animais_2 = modelo
                elif modelos_carregados == 2:
                    modelo_animais_3 = modelo
                modelos_carregados += 1
            except Exception as e:
                print(f"⚠ Erro ao carregar {path}: {e}")
    
    if modelos_carregados > 0:
        MODELOS_OK = True
        logger_engine.info(f"✓ {modelos_carregados} modelo(s) carregado(s)")
    else:
        logger_engine.info("ℹ Nenhum modelo de IA disponível (funcionalidade reduzida)")
        MODELOS_OK = False
        
except Exception as e:
    logger_engine.warning(f"⚠ Aviso ao inicializar modelos: {e}")
    MODELOS_OK = False


# ==================================================
# 🧠 INFERÊNCIA SIMPLES DOS MODELOS
# (não altera arquitetura nem treinamento)
# ==================================================

def responder_com_modelos(pergunta: str):
    """
    Usa os modelos .h5 para tentar gerar uma resposta.
    Retorna None se não conseguir inferir ou modelos não estão carregados.
    """

    if not MODELOS_OK or modelo_animais_1 is None:
        return None

    try:
        # Entrada dummy apenas para ativar os modelos
        entrada = np.zeros((1, 224, 224, 3), dtype=np.float32)
        if not TF_AVAILABLE:
            return None

        confianca = 0.0
        
        if modelo_animais_1 is not None:
            preds_1 = modelo_animais_1.predict(entrada, verbose=0)
            confianca = max(confianca, float(np.max(preds_1)))
        
        if modelo_animais_2 is not None:
            preds_2 = modelo_animais_2.predict(entrada, verbose=0)
            confianca = max(confianca, float(np.max(preds_2)))
        
        if modelo_animais_3 is not None:
            preds_3 = modelo_animais_3.predict(entrada, verbose=0)
            confianca = max(confianca, float(np.max(preds_3)))

        if confianca < 0.60:
            return None

        return (
            "Analisei isso usando meus modelos neurais treinados.\n\n"
            "Se quiser, posso refinar ou aprender mais sobre esse tema."
        )

    except Exception as e:
        logger_engine.error(f"Erro na inferência dos modelos: {e}")
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

        if resultado and resultado.get("resposta") and resultado.get("confianca", 0) >= 0.6:
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
