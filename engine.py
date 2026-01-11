# engine.py
# Cérebro central da Alici

from identidade import identidade_alici
from responder_com_ia import responder_com_ia
from intencao import precisa_pesquisa_web
from web_search import buscar_na_web
from database import buscar_memoria, aprender


def gerar_resposta(pergunta: str) -> str:
    """
    Função central de decisão da Alici.

    Ordem de prioridade:
    1️⃣ Identidade fixa (imutável)
    2️⃣ Memória aprendida (banco de dados)
    3️⃣ Respostas locais (regras / intents)
    4️⃣ Busca na web (quando necessário)
    5️⃣ Fallback consciente (aprendizado futuro)
    """

    if not pergunta or not pergunta.strip():
        return "Pode me dizer algo para que eu possa ajudar?"

    pergunta = pergunta.lower().strip()

    # ==================================================
    # 1️⃣ IDENTIDADE FIXA (NUNCA MUDA)
    # ==================================================

    if any(chave in pergunta for chave in [
        "quem é você",
        "quem e voce",
        "quem é a alici",
        "quem e a alici",
        "quem te criou",
        "quem é seu criador",
        "quem e seu criador",
        "criador da alici"
    ]):
        return identidade_alici()

    # ==================================================
    # 2️⃣ MEMÓRIA (APRENDIZADO AUTOMÁTICO)
    # ==================================================

    resposta_memoria = buscar_memoria(pergunta)
    if resposta_memoria:
        return resposta_memoria

    # ==================================================
    # 3️⃣ RESPOSTAS INTERNAS (REGRAS LOCAIS)
    # ==================================================

    resposta_local = responder_com_ia(pergunta)

    if resposta_local and "Ainda estou aprendendo" not in resposta_local:
        # Reforça aprendizado
        aprender(pergunta, resposta_local)
        return resposta_local

    # ==================================================
    # 4️⃣ BUSCA NA WEB (QUANDO NECESSÁRIO)
    # ==================================================

    if precisa_pesquisa_web(pergunta):
        resultado = buscar_na_web(pergunta)

        if resultado and resultado.get("confianca", 0) >= 0.6:
            resposta = resultado["resposta"]

            # Aprende com a web
            aprender(pergunta, resposta)

            return (
                "Pesquisei isso para você na web:\n\n"
                f"{resposta}"
            )

        return (
            resultado.get(
                "resposta",
                "Pesquisei, mas não encontrei informações confiáveis no momento."
            )
            if resultado else
            "Tentei pesquisar, mas algo deu errado no acesso à web."
        )

    # ==================================================
    # 5️⃣ FALLBACK CONSCIENTE (AUTOAPRENDIZADO FUTURO)
    # ==================================================

    return (
        "Ainda não tenho essa informação armazenada, mas posso aprender com você.\n\n"
        "Se quiser, explique melhor ou faça a pergunta de outra forma 🙂"
    )