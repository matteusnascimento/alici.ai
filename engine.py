# engine.py
# Cérebro central da Alici

from identidade import identidade_alici
from responder_com_ia import responder_com_ia
from intencao import precisa_pesquisa_web
from web_search import buscar_na_web


def gerar_resposta(pergunta: str) -> str:
    """
    Função principal responsável por gerar respostas da Alici.
    Ordem de decisão:
    1. Identidade fixa
    2. Respostas locais (intenção / regras)
    3. Busca na web
    4. Fallback consciente
    """

    if not pergunta:
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
        "quem e seu criador"
    ]):
        return identidade_alici()

    # ==================================================
    # 2️⃣ RESPOSTAS INTERNAS (BASE LOCAL)
    # ==================================================

    resposta_local = responder_com_ia(pergunta)

    if resposta_local and "Ainda estou aprendendo" not in resposta_local:
        return resposta_local

    # ==================================================
    # 3️⃣ BUSCA NA WEB (QUANDO NECESSÁRIO)
    # ==================================================

    if precisa_pesquisa_web(pergunta):
        resultado = buscar_na_web(pergunta)

        if resultado.get("confianca", 0) >= 0.6:
            return (
                "Pesquisei isso para você na web:\n\n"
                f"{resultado['resposta']}"
            )

        return resultado.get(
            "resposta",
            "Pesquisei, mas não encontrei informações confiáveis no momento."
        )

    # ==================================================
    # 4️⃣ FALLBACK CONSCIENTE
    # ==================================================

    return (
        "Ainda não tenho essa informação armazenada, mas posso aprender com você.\n\n"
        "Se quiser, explique melhor ou faça a pergunta de outra forma 🙂"
    )