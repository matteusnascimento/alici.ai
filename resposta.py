"""
resposta.py
Respostas locais, comportamentais e identidade da Alici
Atualizado para fallback via OpenAI quando local não responde
"""

from datetime import datetime
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
    camadas_estrategicas,
    fases_evolucao,
    tracos_psicologo,
    capital_intelectual,
    diagnostico_futuro
)
from engine import responder_via_api

import random

# ==============================
# RESPOSTAS LOCAIS
# ==============================
def responder_local(pergunta: str) -> str | None:
    pergunta = pergunta.lower().strip()

    # IDENTIDADE / CONSCIÊNCIA
    if any(k in pergunta for k in ["quem é você", "quem e voce", "quem é a alici", "quem e a alici"]):
        return identidade_alici()
    if "qual seu nome" in pergunta:
        return "Meu nome é Alici 😊 Sou uma foundation model com identidade proprietária e 70 bilhões de neurônios."
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
        meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
        dia_semana = dias[agora.weekday()]
        mes_nome = meses[agora.month - 1]
        return f"Hoje é {dia_semana}, {agora.day} de {mes_nome} de {agora.year}."

    # REDES SOCIAIS E CONTATO
    if any(k in pergunta for k in ["instagram", "insta", "@matteus_nascimento_ofc", "instagram do criador", "instagram mateus"]):
        return instagram_criador()
    if any(k in pergunta for k in ["email", "e-mail", "email do criador", "email mateus", "enviar email"]):
        return email_criador()
    if any(k in pergunta for k in ["site", "website", "alici.ai", "página", "pagina"]):
        return website_alici()
    if any(k in pergunta for k in ["redes sociais", "redes do criador", "social media", "onde encontrar"]):
        return redes_sociais()
    if any(k in pergunta for k in ["contato", "como contatar", "como falar com", "falar com mateus", "entrar em contato"]):
        return contato_criador()
    if any(k in pergunta for k in ["todas as redes", "todos os contatos", "informações de contato", "informacoes de contato"]):
        return todas_informacoes_contato()
    
    # PIADAS / HUMOR
    if any(k in pergunta for k in ["piada", "conta uma piada", "me faz rir"]):
        piadas = [
            "Por que o livro de matemática se suicidou? Porque tinha muitos problemas! 😄",
            "O que o programador disse antes de morrer? '\x97(Um ponto e vírgula)",
            "Por que o Python é melhor que Java? Porque é mais indiano! 🐍",
            "Como você chama um robô que conta piadas ruins? Um piadinha! 🤖",
        ]
        return random.choice(piadas)

    # SEM RESPOSTA LOCAL
    return None

# ==============================
# FUNÇÃO PRINCIPAL DE RESPOSTA
# ==============================
def responder(pergunta: str) -> str:
    """
    Primeiro tenta responder localmente. Se não houver resposta, envia para OpenAI.
    """
    resposta_local = responder_local(pergunta)
    if resposta_local:
        return resposta_local

    # fallback via OpenAI
    from engine import client
    if client:
        resposta_api = responder_via_api(pergunta)
        if resposta_api:
            return resposta_api

    # fallback final
    return "Desculpe, não consegui entender sua pergunta. Pode reformular?"
