# engine.py
# Cérebro central da Alici

from identidade import identidade_alici
from database import buscar_memoria, aprender
from intencao import precisa_pesquisa_web
from web_search import buscar_na_web
from resposta import responder_local


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
    # 3️⃣ REGRAS LOCAIS (resposta.py)
    # ==================================================
    resposta_local = responder_local(pergunta)
    if resposta_local:
        aprender(pergunta, resposta_local)
        return resposta_local

    # ==================================================
    # 4️⃣ BUSCA NA WEB
    # ==================================================
    if precisa_pesquisa_web(pergunta):
        resultado = buscar_na_web(pergunta)

        if resultado and resultado.get("confianca", 0) >= 0.6:
            resposta_web = resultado["resposta"]
            aprender(pergunta, resposta_web)
            return "Pesquisei isso para você:\n\n" + resposta_web

    # ==================================================
    # 5️⃣ FALLBACK CONSCIENTE
    # ==================================================
    return (
        "Ainda não tenho essa informação armazenada, mas posso aprender com você.\n\n"
        "Explique melhor ou pergunte de outra forma 🙂"
    )