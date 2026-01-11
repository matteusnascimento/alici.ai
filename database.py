import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    return psycopg2.connect(DATABASE_URL)

def criar_tabelas():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS memoria (
        id SERIAL PRIMARY KEY,
        pergunta TEXT,
        resposta TEXT,
        confianca INT DEFAULT 1,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    cur.close()
    conn.close()

def buscar_memoria(pergunta):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT resposta FROM memoria
        WHERE pergunta=%s
        ORDER BY confianca DESC LIMIT 1
    """, (pergunta.lower(),))

    r = cur.fetchone()
    cur.close()
    conn.close()
    return r[0] if r else None

def aprender(pergunta, resposta):
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        SELECT id FROM memoria
        WHERE pergunta=%s AND resposta=%s
    """, (pergunta.lower(), resposta))

    existe = cur.fetchone()

    if existe:
        cur.execute("UPDATE memoria SET confianca = confianca + 1 WHERE id=%s", (existe[0],))
    else:
        cur.execute("""
            INSERT INTO memoria (pergunta, resposta)
            VALUES (%s, %s)
        """, (pergunta.lower(), resposta))

    conn.commit()
    cur.close()
    conn.close()