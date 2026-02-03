import requests
from urllib.parse import quote
from logger import get_logger

logger_web = get_logger("web_search")

def buscar_na_web(pergunta):
    """
    Busca na web usando DuckDuckGo API
    Retorna dict com resposta e confianca (compatível com engine.py)
    """
    try:
        url = f"https://api.duckduckgo.com/?q={quote(pergunta)}&format=json"
        # Aumentado de 5 para 30 segundos para melhor confiabilidade
        r = requests.get(url, timeout=30)
        data = r.json()

        resposta = None
        confianca = 0.0
        
        if data.get("AbstractText"):
            resposta = data["AbstractText"]
            confianca = 0.8
        elif data.get("RelatedTopics") and len(data["RelatedTopics"]) > 0:
            resposta = data["RelatedTopics"][0].get("Text", "")
            confianca = 0.6
        
        if resposta:
            return {
                "resposta": resposta,
                "confianca": confianca
            }
        
        return {
            "resposta": None,
            "confianca": 0.0
        }
    except Exception as e:
        logger_web.error(f"Erro ao buscar na web: {e}")
        return {
            "resposta": None,
            "confianca": 0.0
        }