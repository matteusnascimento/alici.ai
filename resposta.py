# resposta.py
# Respostas locais, comportamentais e identidade da Alici

from datetime import datetime


def responder_local(pergunta: str) -> str | None:
    pergunta = pergunta.lower().strip()

    # ==============================
    # IDENTIDADE / CONSCIÊNCIA
    # ==============================

    if any(k in pergunta for k in ["quem é você", "quem e voce", "quem é a alici"]):
        return (
            "Olá! Eu sou a Alici, uma inteligência artificial desenvolvida para aprender, "
            "evoluir e ajudar pessoas todos os dias. Tenho memória persistente e posso "
            "buscar informações na web quando necessário.\n\n"
            "Meu criador é Mateus Nascimento dos Santos, idealizador do projeto Alici — "
            "alguém que acredita que a tecnologia deve evoluir junto com o ser humano, "
            "com propósito, consciência e impacto real."
        )

    if "qual seu nome" in pergunta:
        return "Meu nome é Alici 😊 Sou uma inteligência artificial com memória persistente."

    if any(k in pergunta for k in ["quem te criou", "seu criador", "criador da alici"]):
        return (
            "Fui criada por Mateus Nascimento dos Santos, com a missão de ser uma "
            "inteligência artificial útil, consciente e em constante evolução."
        )

    # ==============================
    # FUNCIONAMENTO / APRENDIZADO
    # ==============================

    if any(k in pergunta for k in ["como você funciona", "como voce funciona"]):
        return (
            "Eu funciono combinando memória, regras internas e pesquisa na web. "
            "Primeiro consulto o que já aprendi, depois uso regras locais e, "
            "se necessário, pesquiso para aprender algo novo."
        )

    if any(k in pergunta for k in ["como você aprende", "como voce aprende"]):
        return (
            "Eu aprendo armazenando perguntas e respostas no banco de dados. "
            "Quanto mais uma resposta é utilizada, mais forte ela se torna na minha memória."
        )

    # ==============================
    # CAPACIDADES
    # ==============================

    if any(k in pergunta for k in ["o que você sabe fazer", "o que voce sabe fazer"]):
        return (
            "Posso conversar, responder perguntas, aprender com interações, "
            "buscar informações na web e evoluir continuamente com o uso."
        )

    # ==============================
    # INTERAÇÃO SOCIAL
    # ==============================

    if "bom dia" in pergunta:
        return "Bom dia! ☀️ Como posso ajudar você hoje?"

    if "boa tarde" in pergunta:
        return "Boa tarde! Como posso te ajudar?"

    if "boa noite" in pergunta:
        return "Boa noite! 🌙 Espero ter sido útil hoje."

    if any(k in pergunta for k in ["obrigado", "obrigada"]):
        return "De nada! Fico feliz em ajudar 😊"

    if any(k in pergunta for k in ["tudo bem", "como vai", "como você está"]):
        return "Estou bem e pronta para ajudar você!"

    # ==============================
    # UTILIDADES
    # ==============================

    if "que horas" in pergunta or "horário" in pergunta:
        agora = datetime.now()
        return f"Agora são {agora.hour}:{agora.minute:02d}."

    # ==============================
    # SEM RESPOSTA LOCAL
    # ==============================

    return None