import requests
from urllib.parse import quote


def buscar_na_web(pergunta: str) -> dict:
    """
    Realiza busca na web usando DuckDuckGo.
    Retorna um dicionário padronizado para a Alici.
    """

    try:
        url = f"https://api.duckduckgo.com/?q={quote(pergunta)}&format=json&no_html=1"
        response = requests.get(url, timeout=6)

        if response.status_code != 200:
            return _resposta_falha(pergunta)

        data = response.json()

        # 1️⃣ Resultado direto
        if data.get("AbstractText"):
            return {
                "origem": "web",
                "confianca": 0.85,
                "resposta": data["AbstractText"]
            }

        # 2️⃣ Resultados relacionados
        related = data.get("RelatedTopics", [])
        for item in related:
            if isinstance(item, dict) and item.get("Text"):
                return {
                    "origem": "web",
                    "confianca": 0.65,
                    "resposta": item["Text"]
                }

        # 3️⃣ Nada encontrado
        return {
            "origem": "web",
            "confianca": 0.2,
            "resposta": (
                f"Pesquisei sobre '{pergunta}', mas encontrei poucas informações claras. "
                "Se quiser, você pode me explicar melhor para que eu aprenda."
            )
        }

    except Exception:
        return _resposta_falha(pergunta)


def _resposta_falha(pergunta: str) -> dict:
    return {
        "origem": "web",
        "confianca": 0.0,
        "resposta": (
            f"Tentei pesquisar sobre '{pergunta}', mas tive um problema técnico no momento. "
            "Podemos tentar novamente ou você pode me explicar?"
        )
    }
