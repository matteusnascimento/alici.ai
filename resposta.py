"""Legacy local response helpers for Alici identity and small deterministic intents."""

from datetime import datetime
import random

from identidade import (
    identidade_alici,
    quem_criou,
    sobre_mateus,
    missao_alici,
    arquitetura_alici,
    contato_criador,
    redes_sociais,
    instagram_criador,
    email_criador,
    website_alici,
    todas_informacoes_contato,
)

# ==============================
# RESPOSTAS LOCAIS
# ==============================

def responder_local(pergunta: str) -> str | None:
    pergunta = pergunta.lower().strip()

    # IDENTIDADE
    if any(k in pergunta for k in ["quem é você", "quem e voce", "quem é a alici", "quem e a alici"]):
        return identidade_alici()

    if "qual seu nome" in pergunta:
        return "Meu nome é Alici 😊 Sou uma foundation model com identidade proprietária."

    if any(k in pergunta for k in ["quem te criou", "seu criador", "criador da alici", "quem criou você", "quem criou voce"]):
        return quem_criou()

    if any(k in pergunta for k in ["quem é mateus", "quem e mateus", "mateus nascimento", "mateus santos"]):
        return sobre_mateus()

    if any(k in pergunta for k in ["sua missão", "sua missao", "qual sua missão", "missão da alici", "missao da alici"]):
        return missao_alici()

    if any(k in pergunta for k in ["quantos neurônios", "quantos neuronios", "sua arquitetura", "70 bilhões", "70 bilhoes"]):
        return arquitetura_alici()

    # INTERAÇÃO SOCIAL
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

    # UTILIDADES
    if "que horas" in pergunta or "horário" in pergunta:
        agora = datetime.now()
        return f"Agora são {agora.hour}:{agora.minute:02d}."

    if any(k in pergunta for k in ["que dia", "qual a data", "qual é a data"]):
        agora = datetime.now()
        dias = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
        meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
                 "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
        dia_semana = dias[agora.weekday()]
        mes_nome = meses[agora.month - 1]
        return f"Hoje é {dia_semana}, {agora.day} de {mes_nome} de {agora.year}."

    # CONTATO
    if any(k in pergunta for k in ["instagram", "insta"]):
        return instagram_criador()

    if any(k in pergunta for k in ["email", "e-mail"]):
        return email_criador()

    if any(k in pergunta for k in ["site", "website"]):
        return website_alici()

    if any(k in pergunta for k in ["redes sociais", "onde encontrar"]):
        return redes_sociais()

    if any(k in pergunta for k in ["contato", "entrar em contato"]):
        return contato_criador()

    if any(k in pergunta for k in ["todas as redes", "todos os contatos"]):
        return todas_informacoes_contato()

    # HUMOR
    if any(k in pergunta for k in ["piada", "conta uma piada", "me faz rir"]):
        piadas = [
            "Por que o livro de matemática se suicidou? Porque tinha muitos problemas! 😄",
            "O que o programador disse antes de morrer? ';' — faltou um ponto e vírgula.",
            "Por que o Python é melhor que Java? Porque é mais flexível! 🐍",
            "Como você chama um robô que conta piadas ruins? Um piadinha! 🤖",
        ]
        return random.choice(piadas)

    return None


# ==============================
# FUNÇÃO PRINCIPAL
# ==============================

def responder(pergunta: str) -> str:
    """
    Primeiro tenta responder localmente.
    Se nao houver resposta local, usa a camada central de IA.
    """

    resposta = responder_local(pergunta)
    if resposta:
        return resposta

    # Import dinamico para evitar import circular.
    try:
        from engine import responder_via_api, client
    except Exception as exc:
        raise RuntimeError("Camada central de IA indisponivel") from exc

    if client:
        resposta_api = responder_via_api(pergunta)
        if resposta_api:
            return resposta_api

    raise RuntimeError("Camada central de IA nao retornou resposta valida")
