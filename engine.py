from database import buscar_resposta, salvar_interacao
from resposta import responder_com_ia
from web_search import buscar_na_web

def gerar_resposta(pergunta):
    # 1. Busca no banco
    resposta = buscar_resposta(pergunta)

    if resposta:
        salvar_interacao(pergunta, resposta)
        return resposta

    # 2. IA responde
    resposta = responder_com_ia(pergunta)

    # 3. Se ainda for fraca, busca na web
    if resposta is None or len(resposta) < 10:
        resposta = buscar_na_web(pergunta)

    salvar_interacao(pergunta, resposta)
    return resposta