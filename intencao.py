def precisa_pesquisa_web(pergunta: str) -> bool:
    gatilhos = [
        "quem é",
        "o que é",
        "notícia",
        "últimas",
        "hoje",
        "atual",
        "valor",
        "preço",
        "onde fica",
        "como fazer"
    ]

    pergunta = pergunta.lower()
    return any(gatilho in pergunta for gatilho in gatilhos)
