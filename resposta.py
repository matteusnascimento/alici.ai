# responder_com_ia.py
# Respostas locais e comportamentais da Alici

from datetime import datetime


def responder_com_ia(pergunta: str) -> str | None:
    pergunta = pergunta.lower().strip()

    # ==============================
    # IDENTIDADE / CONSCIÊNCIA
    # ==============================

    if any(k in pergunta for k in ["quem é você", "quem e voce"]):
        return (
            "Olá! Eu sou a Alici, uma inteligência artificial desenvolvida para aprender, "
            "evoluir e ajudar pessoas todos os dias. Tenho memória persistente, aprendo com "
            "cada interação e posso buscar informações na web sempre que preciso.\n\n"
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
            "Quando você pergunta algo, primeiro consulto o que já aprendi. "
            "Se não souber, posso pesquisar e aprender com a resposta."
        )

    if any(k in pergunta for k in ["como você aprende", "como voce aprende"]):
        return (
            "Eu aprendo armazenando perguntas e respostas em um banco de dados. "
            "Quanto mais uma resposta é usada, mais forte ela se torna na minha memória."
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
        return "Bom dia! ☀️ Que ótimo dia para aprender algo novo. Como posso ajudar?"

    if "boa noite" in pergunta:
        return "Boa noite! 🌙 Espero ter sido útil hoje. Até mais!"

    if any(k in pergunta for k in ["obrigado", "obrigada"]):
        return "De nada! Fico feliz em poder ajudar 😊"

    if any(k in pergunta for k in ["tudo bem", "como vai", "como você está"]):
        return "Estou bem e pronta para ajudar você no que precisar!"

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