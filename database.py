"""
database.py
Conexão com PostgreSQL (Neon) e operações de banco de dados
"""

import os
import psycopg2
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL não configurado em .env")


def conectar():
    return psycopg2.connect(DATABASE_URL, sslmode="require")


@contextmanager
def get_db_connection():
    """
    Context manager para conexão com banco de dados
    """
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def criar_tabelas():
    """
    Cria as tabelas necessárias no banco de dados
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Tabela de memória
            cur.execute("""
                CREATE TABLE IF NOT EXISTS memoria (
                    id SERIAL PRIMARY KEY,
                    pergunta TEXT NOT NULL,
                    resposta TEXT NOT NULL,
                    confianca INT DEFAULT 1,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabela de usuários
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    senha_hash TEXT NOT NULL,
                    plano TEXT DEFAULT 'free',
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabela de histórico
            cur.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id SERIAL PRIMARY KEY,
                    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    pergunta TEXT NOT NULL,
                    resposta TEXT NOT NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Índices
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_memoria_pergunta
                ON memoria (pergunta)
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_user_id ON history(user_id)
            """)


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


# ============================================================================
# OPERAÇÕES DE USUÁRIO
# ============================================================================

def criar_usuario(nome: str, email: str, senha_hash: str, plano: str = "free") -> dict:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO users (nome, email, senha_hash, plano)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, nome, email, plano, criado_em
                    """,
                    (nome, email, senha_hash, plano)
                )
                resultado = cur.fetchone()

                if resultado:
                    return {
                        "id": resultado[0],
                        "nome": resultado[1],
                        "email": resultado[2],
                        "plano": resultado[3],
                        "criado_em": resultado[4]
                    }
            except psycopg2.IntegrityError:
                raise ValueError("Email já está registrado")
            except Exception as e:
                raise Exception(f"Erro ao criar usuário: {str(e)}")


def buscar_usuario_por_email(email: str) -> dict:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, email, senha_hash, plano FROM users WHERE email = %s",
                (email,)
            )
            resultado = cur.fetchone()

            if resultado:
                return {
                    "id": resultado[0],
                    "nome": resultado[1],
                    "email": resultado[2],
                    "senha_hash": resultado[3],
                    "plano": resultado[4]
                }
            return None


def buscar_usuario_por_id(user_id: int) -> dict:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, email, plano FROM users WHERE id = %s",
                (user_id,)
            )
            resultado = cur.fetchone()

            if resultado:
                return {
                    "id": resultado[0],
                    "nome": resultado[1],
                    "email": resultado[2],
                    "plano": resultado[3]
                }
            return None


# ============================================================================
# OPERAÇÕES DE HISTÓRICO
# ============================================================================

def salvar_historico(user_id: int, pergunta: str, resposta: str) -> dict:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO history (user_id, pergunta, resposta)
                VALUES (%s, %s, %s)
                RETURNING id, user_id, pergunta, resposta, criado_em
                """,
                (user_id, pergunta, resposta)
            )
            resultado = cur.fetchone()

            if resultado:
                return {
                    "id": resultado[0],
                    "user_id": resultado[1],
                    "pergunta": resultado[2],
                    "resposta": resultado[3],
                    "criado_em": resultado[4]
                }


def buscar_historico(user_id: int, limite: int = 50) -> list:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, pergunta, resposta, criado_em
                FROM history
                WHERE user_id = %s
                ORDER BY criado_em DESC
                LIMIT %s
                """,
                (user_id, limite)
            )
            resultados = cur.fetchall()

            return [
                {
                    "id": r[0],
                    "pergunta": r[1],
                    "resposta": r[2],
                    "criado_em": r[3]
                }
                for r in resultados
            ]


def limpar_historico(user_id: int) -> bool:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM history WHERE user_id = %s", (user_id,))
            return True