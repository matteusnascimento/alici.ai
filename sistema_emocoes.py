# sistema_emocoes.py
# Sistema de detecção automática de emoções para Alici

import re

def detectar_emocao(resposta: str) -> dict:
    """
    Analisa a resposta e retorna emoção + estado animação
    
    Retorna:
    {
        "emocao": "happy|neutral|serious|mysterious|thinking",
        "intensidade": 0.0-1.0,
        "cor_aura": "#00ffaa",
        "velocidade_animacao": 1.0
    }
    """
    
    resposta_lower = resposta.lower()
    
    # 🔥 MYSTERIOUS (Espiritual, profundo, enigmático)
    mysterious_keywords = [
        "mistério", "enigma", "segredo", "oculto", "além",
        "dimensão", "energia", "aura", "essência", "transcend",
        "cósmico", "infinito", "conhecimento antigo", "verdade absoluta",
        "ainda não tenho", "aprender com você"
    ]
    
    # 😊 HAPPY (Positivo, entusiasmado, confiante)
    happy_keywords = [
        "claro", "com prazer", "adorei", "fantástico", "excelente",
        "perfeito", "ótimo", "maravilhoso", "incrível", "feliz",
        "ajudar", "sucesso", "consegui", "vou te", "pronta",
        "estou bem", "tudo certo", "✔", "🎉", "!"
    ]
    
    # 🤔 THINKING (Reflexivo, questionador)
    thinking_keywords = [
        "talvez", "pode ser", "acredito", "tenho certeza",
        "não tenho certeza", "depende", "é complicado",
        "pensando", "refletindo", "considerando"
    ]
    
    # 😐 SERIOUS (Sério, aviso, atenção)
    serious_keywords = [
        "atenção", "perigo", "cuidado", "aviso", "erro",
        "problema", "falha", "infelizmente", "não posso",
        "impossível", "não é possível", "urgente"
    ]
    
    # Contar ocorrências
    mysterious_score = sum(1 for k in mysterious_keywords if k in resposta_lower)
    happy_score = sum(1 for k in happy_keywords if k in resposta_lower)
    thinking_score = sum(1 for k in thinking_keywords if k in resposta_lower)
    serious_score = sum(1 for k in serious_keywords if k in resposta_lower)
    
    # Pontuação por caracteres especiais
    if "?" in resposta:
        thinking_score += 2
    if "!" in resposta:
        happy_score += 1.5
    if "..." in resposta:
        mysterious_score += 1
    
    # Emoji direto
    emojis = resposta.count("✨") + resposta.count("🌟") + resposta.count("💫")
    mysterious_score += emojis
    
    # Determinar emoção dominante
    scores = {
        "mysterious": mysterious_score,
        "happy": happy_score,
        "thinking": thinking_score,
        "serious": serious_score,
        "neutral": 1  # default
    }
    
    emocao = max(scores, key=scores.get)
    intensidade = min(1.0, max(scores.values()) / 10.0)
    
    # Mapeamento de cores de aura (mystical vibes)
    cores_aura = {
        "mysterious": "#8b5cf6",  # Roxo místico
        "happy": "#00ffaa",       # Ciano energético
        "thinking": "#fbbf24",    # Âmbar contemplativo
        "serious": "#ef4444",     # Vermelho alertador
        "neutral": "#06b6d4"      # Cyan neutro
    }
    
    # Velocidade de animação baseada em intensidade
    velocidade = 0.5 + intensidade
    
    return {
        "emocao": emocao,
        "intensidade": round(intensidade, 2),
        "cor_aura": cores_aura[emocao],
        "velocidade_animacao": round(velocidade, 2),
        "scores": scores  # Debug
    }


def adicionar_metadados_resposta(resposta: str) -> dict:
    """
    Versão expandida que retorna a resposta + metadados
    para integração com engine.py
    """
    emocao = detectar_emocao(resposta)
    
    # Determinar estado visual
    estados_map = {
        "mysterious": "mystical",
        "happy": "happy",
        "thinking": "thinking",
        "serious": "serious",
        "neutral": "neutral"
    }
    
    return {
        "resposta": resposta,
        "emocao": emocao["emocao"],
        "intensidade": emocao["intensidade"],
        "cor_aura": emocao["cor_aura"],
        "velocidade_animacao": emocao["velocidade_animacao"],
        "estado_visual": estados_map[emocao["emocao"]]
    }


# Testes
if __name__ == "__main__":
    testes = [
        "Olá! Eu sou a Alici, uma inteligência artificial desenvolvida para aprender.",
        "Claro, com prazer! Vou te ajudar com isso! 🎉",
        "Hmm, talvez isso seja mais complicado do que parece...",
        "⚠️ ATENÇÃO: há um perigo aqui! Tome cuidado!",
        "Ainda não tenho essa informação, mas posso aprender com você... ✨"
    ]
    
    for teste in testes:
        resultado = detectar_emocao(teste)
        print(f"\nResposta: {teste[:50]}...")
        print(f"Emoção: {resultado['emocao']} (intensidade: {resultado['intensidade']})")
        print(f"Cor: {resultado['cor_aura']} | Velocidade: {resultado['velocidade_animacao']}x")
