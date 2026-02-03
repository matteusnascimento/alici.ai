import requests
from urllib.parse import quote

def buscar_na_web(pergunta):
    """
    Busca na web usando DuckDuckGo API
    Retorna dict com resposta e confianca (compatível com engine.py)
    """
    try:
        url = f"https://api.duckduckgo.com/?q={quote(pergunta)}&format=json"
        r = requests.get(url, timeout=5)
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
        print(f"Erro ao buscar na web: {e}")
        return {
            "resposta": None,
            "confianca": 0.0
        }