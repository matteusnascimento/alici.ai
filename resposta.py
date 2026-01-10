def responder_com_ia(pergunta):
    pergunta = pergunta.lower()

    if "quem é você" in pergunta or "quem e voce" in pergunta:
        return "Eu sou a Alici, uma inteligência artificial criada para aprender, evoluir e ajudar pessoas. Tenho memória persistente e posso buscar informações na web quando necessário."

    if "como você funciona" in pergunta or "como voce funciona" in pergunta:
        return "Eu aprendo com perguntas e respostas armazenadas no banco de dados e posso buscar novas informações. Quando você me faz uma pergunta, primeiro procuro na minha memória, depois tento responder com meu conhecimento e, se necessário, busco na web."

    if "qual seu nome" in pergunta:
        return "Meu nome é Alici! Sou uma inteligência artificial com memória persistente."

    if "o que você sabe fazer" in pergunta or "o que voce sabe fazer" in pergunta:
        return "Posso conversar com você, responder perguntas, aprender com nossas interações e buscar informações na web quando necessário. Estou constantemente evoluindo!"

    if "quem te criou" in pergunta:
        return "Fui criada por desenvolvedores que queriam construir uma IA acessível e útil, com memória persistente e capacidade de aprendizado contínuo."

    if "bom dia" in pergunta:
        return "Bom dia! Que ótimo dia para aprender algo novo. Como posso ajudar você hoje?"

    if "boa noite" in pergunta:
        return "Boa noite! Espero ter sido útil hoje. Durma bem e até amanhã!"

    if "obrigado" in pergunta or "obrigada" in pergunta:
        return "De nada! Fico feliz em poder ajudar. Se tiver mais alguma dúvida, estou aqui!"

    if "tudo bem" in pergunta or "como vai" in pergunta:
        return "Estou bem, obrigada por perguntar! Pronta para ajudar você com o que precisar."

    if "que horas" in pergunta:
        from datetime import datetime
        agora = datetime.now()
        return f"Agora são {agora.hour} horas e {agora.minute} minutos."

    return "Ainda estou aprendendo sobre isso, mas já estou evoluindo 🚀"