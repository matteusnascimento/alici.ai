import requests
from urllib.parse import quote

def buscar_na_web(pergunta):
    try:
        url = f"https://api.duckduckgo.com/?q={quote(pergunta)}&format=json"
        r = requests.get(url, timeout=5)
        data = r.json()

        if data.get("AbstractText"):
            return data["AbstractText"]

        if data.get("RelatedTopics"):
            return data["RelatedTopics"][0].get("Text", "")

        return None
    except:
        return None