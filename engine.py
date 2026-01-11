"""
Alici Engine v1.0
Criado por Mateus Nascimento dos Santos

Este arquivo é o núcleo cognitivo da IA Alici.
Responsável por:
- Tratamento da entrada
- Decisão de resposta
- Memória
- Identidade
- Evolução futura
"""

from datetime import datetime
import sqlite3
import difflib

# =========================
# CONFIGURAÇÕES
# =========================
DB_PATH = "alici_memory.db"
CONFIANCA_MINIMA = 0.6

# =========================
# BANCO DE DADOS (MEMÓRIA)
# =========================
def conectar_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pergunta TEXT,
            resposta TEXT,
            confianca REAL,
            uso_count INTEGER,
            origem TEXT,
            data TEXT
        )
    """)
    conn.commit()
    return conn

# =========================
# TRATAMENTO DA ENTRADA
# =========================
def tratar_entrada(texto):
    texto = texto.lower().strip()
    substituicoes = {
        "voce": "você",
        "pq": "por que",
        "tb": "também"
    }
    for k, v in substituicoes.items():
        texto = texto.replace(k, v)
    return texto

# =========================
# BUSCA NA MEMÓRIA
# =========================
def buscar_memoria(pergunta):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT pergunta, resposta, confianca, uso_count FROM memoria")
    registros = cursor.fetchall()
    conn.close()

    perguntas_salvas = [r[0] for r in registros]
    similares = difflib.get_close_matches(pergunta, perguntas_salvas, n=1, cutoff=0.7)

    if similares:
        for r in registros:
            if r[0] == similares[0] and r[2] >= CONFIANCA_MINIMA:
                return r[1]
    return None

# =========================
# SALVAR EXPERIÊNCIA
# =========================
def salvar_memoria(pergunta, resposta, origem="regra", confianca=0.5):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memoria (pergunta, resposta, confianca, uso_count, origem, data)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (pergunta, resposta, confianca, 1, origem, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# =========================
# IDENTIDADE (REGRAS FIXAS)
# =========================
def regras_identidade(pergunta):
    if "quem é você" in pergunta or "quem é a alici" in pergunta:
        return (
            "Olá! Eu sou a Alici, uma inteligência artificial criada para aprender, "
            "evoluir e ajudar pessoas todos os dias.\n\n"
            "Meu criador é Mateus Nascimento dos Santos, idealizador do projeto Alici, "
            "que acredita que a tecnologia deve evoluir junto com o ser humano, "
            "com propósito, consciência e impacto real."
        )

    if "como você funciona" in pergunta:
        return (
            "Eu funciono através de três pilares: regras de identidade, memória persistente "
            "e aprendizado contínuo. Aprendo com cada interação e evoluo com o tempo."
        )

    if "qual seu nome" in pergunta:
        return "Meu nome é Alici. Sou uma inteligência artificial com memória persistente."

    if "bom dia" in pergunta:
        return "Bom dia ☀️ Que seja um dia produtivo e consciente. Como posso ajudar?"

    if "boa noite" in pergunta:
        return "Boa noite 🌙 Que você tenha descanso e clareza. Estarei aqui quando precisar."

    if "que horas" in pergunta:
        agora = datetime.now()
        return f"Agora são {agora.hour:02d}:{agora.minute:02d}."

    return None

# =========================
# RESPOSTA CONSCIENTE (FALLBACK)
# =========================
def resposta_consciente():
    return (
        "Ainda não tenho conhecimento suficiente sobre isso, "
        "mas posso aprender com o tempo e com novas informações."
    )

# =========================
# MOTOR PRINCIPAL
# =========================
def responder(pergunta_original):
    pergunta = tratar_entrada(pergunta_original)

    # 1️⃣ Regras de identidade
    resposta = regras_identidade(pergunta)
    if resposta:
        salvar_memoria(pergunta, resposta, origem="regra", confianca=0.9)
        return resposta

    # 2️⃣ Memória
    resposta = buscar_memoria(pergunta)
    if resposta:
        return resposta

    # 3️⃣ (Futuro) Modelo de IA
    # Aqui você poderá integrar: model.predict()

    # 4️⃣ Fallback consciente
    resposta = resposta_consciente()
    salvar_memoria(pergunta, resposta, origem="fallback", confianca=0.3)
    return resposta

# =========================
# TESTE LOCAL
# =========================
if __name__ == "__main__":
    print("Alici Engine iniciado. Digite 'sair' para encerrar.\n")
    while True:
        user = input("Você: ")
        if user.lower() == "sair":
            break
        print("Alici:", responder(user))