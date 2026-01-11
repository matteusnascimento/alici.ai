"""
Alici Engine v2.0
Criado por Mateus Nascimento dos Santos

Sistema cognitivo avançado com:
- Memória persistente
- Confiança dinâmica
- Avaliação do usuário
- Detecção de intenção
- Proteção contra aprendizado tóxico
- Diagnóstico interno
"""

from datetime import datetime
import sqlite3
import difflib
import re

# =========================
# CONFIGURAÇÕES
# =========================
DB_PATH = "alici_memory.db"
CONFIANCA_MINIMA = 0.6
CONTEXTO_MAX = 5

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
            avaliacao INTEGER,
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
# DETECÇÃO DE INTENÇÃO
# =========================
def detectar_intencao(texto):
    if any(p in texto for p in ["como", "por que", "o que", "qual"]):
        return "pergunta"
    if any(p in texto for p in ["triste", "cansado", "mal", "desanimado"]):
        return "emocional"
    if texto.startswith(("faça", "crie", "execute")):
        return "comando"
    return "conversa"

# =========================
# FILTRO DE APRENDIZADO TÓXICO
# =========================
def conteudo_permitido(texto):
    bloqueios = ["ódio", "matar", "crime", "racismo"]
    return not any(p in texto for p in bloqueios)

# =========================
# MEMÓRIA DE CURTO PRAZO
# =========================
contexto_usuario = []

def atualizar_contexto(pergunta):
    contexto_usuario.append(pergunta)
    if len(contexto_usuario) > CONTEXTO_MAX:
        contexto_usuario.pop(0)

# =========================
# BUSCA NA MEMÓRIA
# =========================
def buscar_memoria(pergunta):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT pergunta, resposta, confianca FROM memoria
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
def salvar_memoria(pergunta, resposta, origem, confianca=0.5, avaliacao=0):
    if not conteudo_permitido(pergunta):
        return

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memoria
        (pergunta, resposta, confianca, uso_count, avaliacao, origem, data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        pergunta,
        resposta,
        confianca,
        1,
        avaliacao,
        origem,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

# =========================
# IDENTIDADE
# =========================
def regras_identidade(pergunta):
    if "quem é você" in pergunta or "quem é a alici" in pergunta:
        return (
            "Eu sou a Alici, uma inteligência artificial criada para aprender, evoluir "
            "e ajudar pessoas com consciência e propósito.\n\n"
            "Fui idealizada por Mateus Nascimento dos Santos."
        )

    if "como você funciona" in pergunta:
        return (
            "Eu funciono por regras de identidade, memória persistente e aprendizado contínuo. "
            "Cada interação contribui para minha evolução."
        )

    return None

# =========================
# RESPOSTA EMOCIONAL
# =========================
def resposta_emocional():
    return (
        "Sinto muito que você esteja se sentindo assim. "
        "Se quiser conversar, estou aqui para te ouvir."
    )

# =========================
# DIAGNÓSTICO
# =========================
def diagnostico():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM memoria")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM memoria WHERE confianca >= 0.8")
    boas = cursor.fetchone()[0]

    conn.close()

    return {
        "total_memorias": total,
        "memorias_confiaveis": boas,
        "nivel": "iniciante" if total < 500 else "intermediário"
    }

# =========================
# MOTOR PRINCIPAL
# =========================
def responder(pergunta_original):
    pergunta = tratar_entrada(pergunta_original)
    atualizar_contexto(pergunta)

    intencao = detectar_intencao(pergunta)

    # Identidade
    resposta = regras_identidade(pergunta)
    if resposta:
        salvar_memoria(pergunta, resposta, "regra", 0.9)
        return resposta

    # Emocional
    if intencao == "emocional":
        resposta = resposta_emocional()
        salvar_memoria(pergunta, resposta, "emocional", 0.7)
        return resposta

    # Memória
    resposta = buscar_memoria(pergunta)
    if resposta:
        return resposta

    # Fallback consciente
    resposta = (
        "Ainda não tenho conhecimento suficiente sobre isso, "
        "mas posso aprender com novas interações."
    )
    salvar_memoria(pergunta, resposta, "fallback", 0.3)
    return resposta

# =========================
# TESTE LOCAL
# =========================
if __name__ == "__main__":
    print("Alici Engine v2.0 ativa. Digite 'sair' para encerrar.\n")
    while True:
        user = input("Você: ")
        if user.lower() == "sair":
            print("Diagnóstico:", diagnostico())
            break
        print("Alici:", responder(user))