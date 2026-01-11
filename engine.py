from datetime import datetime
import sqlite3
import difflib
import re

DB_PATH = "alici_memory.db"
CONFIANCA_MINIMA = 0.6

# =========================
# BANCO DE DADOS
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
    texto = re.sub(r"[^\w\sáéíóúãõç]", "", texto)
    correcoes = {
        "voce": "você",
        "pq": "por que",
        "tb": "também"
    }
    for k, v in correcoes.items():
        texto = texto.replace(k, v)
    return texto

# =========================
# IDENTIDADE
# =========================
def regras_identidade(pergunta):
    if "quem é você" in pergunta or "quem é a alici" in pergunta:
        return (
            "Olá! Eu sou a Alici, uma inteligência artificial criada para aprender, "
            "evoluir e ajudar pessoas com consciência e propósito.\n\n"
            "Fui idealizada por Mateus Nascimento dos Santos."
        )

    if "como você funciona" in pergunta:
        return (
            "Eu funciono por regras de identidade, memória persistente "
            "e aprendizado contínuo."
        )

    return None

# =========================
# BUSCA NA MEMÓRIA
# =========================
def buscar_memoria(pergunta):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pergunta, resposta, confianca
        FROM memoria
        WHERE confianca >= ?
    """, (CONFIANCA_MINIMA,))
    registros = cursor.fetchall()
    conn.close()

    perguntas = [r[0] for r in registros]
    similares = difflib.get_close_matches(pergunta, perguntas, n=1, cutoff=0.75)

    if similares:
        for r in registros:
            if r[0] == similares[0]:
                return r[1]
    return None

# =========================
# SALVAR EXPERIÊNCIA
# =========================
def salvar_memoria(pergunta, resposta, origem, confianca):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memoria
        (pergunta, resposta, confianca, uso_count, origem, data)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        pergunta,
        resposta,
        confianca,
        1,
        origem,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

# =========================
# MOTOR PRINCIPAL
# =========================
def responder(pergunta_original):
    pergunta = tratar_entrada(pergunta_original)

    # 1️⃣ Identidade
    resposta = regras_identidade(pergunta)
    if resposta:
        salvar_memoria(pergunta, resposta, "regra", 0.9)
        return resposta

    # 2️⃣ Memória
    resposta = buscar_memoria(pergunta)
    if resposta:
        return resposta

    # 3️⃣ Fallback consciente
    resposta = (
        "Ainda estou aprendendo sobre isso, "
        "mas posso evoluir com novas interações."
    )
    salvar_memoria(pergunta, resposta, "fallback", 0.3)
    return resposta

# =========================
# ALIAS (IMPORTANTE PARA O RENDER)
# =========================
def gerar_resposta(pergunta):
    return responder(pergunta)