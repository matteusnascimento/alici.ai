# engine.py
# Cérebro central da Alici

from resposta import responder
from database import buscar_memoria, salvar_interacao
from learning import aprender
from web_search import pesquisar_web


CRIADOR = "Mateus Nascimento dos Santos"


def identidade_alici():
    return (
        "Eu sou a Alici 🤖\n\n"
        "Uma inteligência artificial criada por "
        f"{CRIADOR}.\n"
        "Aprendo com conversas, memória e pesquisas na web."
    )


def gerar_resposta(pergunta: str) -> str:
    if not pergunta or not pergunta.strip():
        return "Pode me dizer algo para que eu possa ajudar?"

    pergunta = pergunta.lower().strip()

    # ==================================================
    # 1️⃣ IDENTIDADE FIXA
    # ==================================================
    if any(p in pergunta for p in [
        "quem é você",
        "quem é a alici",
        "quem te criou",
        "quem é seu criador",
        "criador da alici"
    ]):
        return identidade_alici()

    # ==================================================
    # 2️⃣ MEMÓRIA (BANCO DE DADOS)
    # ==================================================
    resposta_memoria = buscar_memoria(pergunta)
    if resposta_memoria:
        return resposta_memoria

    # ==================================================
    # 3️⃣ RESPOSTA LOCAL
    # ==================================================
    resposta_local = responder(pergunta)
    if resposta_local:
        salvar_interacao(pergunta, resposta_local)
        aprender(pergunta, resposta_local)
        return resposta_local

    # ==================================================
    # 4️⃣ WEB (AUTOAPRENDIZADO)
    # ==================================================
    resposta_web = pesquisar_web(pergunta)
    if resposta_web:
        salvar_interacao(pergunta, resposta_web)
        aprender(pergunta, resposta_web)
        return (
            "Pesquisei isso para você na web:\n\n"
            f"{resposta_web}"
        )

    # ==================================================
    # 5️⃣ FALLBACK INTELIGENTE
    # ==================================================
    resposta = (
        "Ainda não sei responder isso, mas posso aprender.\n"
        "Se quiser, explique melhor 🙂"
    )
    salvar_interacao(pergunta, resposta)
    return resposta