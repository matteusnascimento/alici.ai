import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def conectar():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def criar_tabelas():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS memoria (
        id SERIAL PRIMARY KEY,
        pergunta TEXT NOT NULL,
        resposta TEXT NOT NULL,
        confianca INT DEFAULT 1,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Índice para acelerar buscas
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_memoria_pergunta
        ON memoria (pergunta);
    """)

    conn.commit()
    cur.close()
    conn.close()


def buscar_memoria(pergunta):
    try:
        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT resposta
            FROM memoria
            WHERE pergunta = %s
            ORDER BY confianca DESC
            LIMIT 1
        """, (pergunta.lower(),))

        r = cur.fetchone()
        return r[0] if r else None

    except Exception as e:
        print("Erro ao buscar memória:", e)
        return None

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()


def aprender(pergunta, resposta):
    try:
        conn = conectar()
        cur = conn.cursor()

        cur.execute("""
            SELECT id FROM memoria
            WHERE pergunta = %s AND resposta = %s
        """, (pergunta.lower(), resposta))

        existe = cur.fetchone()

        if existe:
            cur.execute("""
                UPDATE memoria
                SET confianca = confianca + 1
                WHERE id = %s
            """, (existe[0],))
        else:
            cur.execute("""
                INSERT INTO memoria (pergunta, resposta)
                VALUES (%s, %s)
            """, (pergunta.lower(), resposta))

        conn.commit()

    except Exception as e:
        print("Erro ao aprender:", e)

    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()


def salvar_interacao(pergunta, resposta):
    """
    Salva qualquer interação, mesmo quando não há aprendizado.
    """
    aprender(pergunta, resposta)