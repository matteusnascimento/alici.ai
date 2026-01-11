from identidade import identidade_alici
from database import buscar_memoria, aprender
from intencao import precisa_pesquisa_web
from web_search import buscar_na_web
from responder_local import responder_local


def gerar_resposta(pergunta: str) -> str:
    if not pergunta or not pergunta.strip():
        return "Pode me dizer algo para que eu possa ajudar?"

    pergunta = pergunta.lower().strip()

    # 1️⃣ IDENTIDADE FIXA
    if any(chave in pergunta for chave in [
        "quem é você", "quem e voce", "quem é a alici",
        "quem te criou", "criador da alici"
    ]):
        return identidade_alici()

    # 2️⃣ MEMÓRIA
    resposta = buscar_memoria(pergunta)
    if resposta:
        return resposta

    # 3️⃣ REGRAS LOCAIS
    resposta = responder_local(pergunta)
    if resposta:
        aprender(pergunta, resposta)
        return resposta

    # 4️⃣ WEB
    if precisa_pesquisa_web(pergunta):
        resultado = buscar_na_web(pergunta)
        if resultado and resultado.get("confianca", 0) >= 0.6:
            aprender(pergunta, resultado["resposta"])
            return "Pesquisei isso para você:\n\n" + resultado["resposta"]

    # 5️⃣ FALLBACK
    return (
        "Ainda não tenho essa informação armazenada, mas posso aprender com você.\n"
        "Explique melhor ou pergunte de outra forma 🙂"
    )