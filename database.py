"""
database.py
Conexão com PostgreSQL (Neon) ou SQLite
VERSÃO PRODUÇÃO PROFISSIONAL
"""

import os
import sqlite3
import time
from contextlib import contextmanager
from dotenv import load_dotenv
from logger import get_logger

logger_db = get_logger("database")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
USE_SQLITE = DATABASE_URL and DATABASE_URL.startswith("sqlite")
USE_POSTGRES = DATABASE_URL and DATABASE_URL.startswith("postgresql")

pool = None
DATABASE_ENABLED = False

# ==========================================
# 🔥 CONEXÃO COM RETRY (ANTI NEON SLEEP)
# ==========================================
if not DATABASE_URL:
    logger_db.warning("⚠️ DATABASE_URL não configurado")

elif USE_POSTGRES:
    try:
        import psycopg2
        from psycopg2.pool import SimpleConnectionPool

        retries = 5
        for attempt in range(retries):
            try:
                pool = SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dsn=DATABASE_URL
                )
                DATABASE_ENABLED = True
                logger_db.info("✅ PostgreSQL/Neon conectado com pool")
                break
            except Exception as e:
                logger_db.warning(f"Tentativa {attempt+1}/{retries} falhou ao conectar no Neon: {e}")
                time.sleep(2)

        if not DATABASE_ENABLED:
            logger_db.error("❌ Não foi possível conectar ao PostgreSQL")

    except Exception as e:
        logger_db.error(f"Erro ao importar psycopg2: {e}")

elif USE_SQLITE:
    DATABASE_ENABLED = True
    logger_db.info("🗄️ Usando SQLite")

else:
    logger_db.error("❌ DATABASE_URL inválido")


# ==========================================
# CONTEXT MANAGER
# ==========================================
@contextmanager
def get_db_connection():
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco não configurado ou indisponível")

    if USE_SQLITE:
        db_path = DATABASE_URL.replace("sqlite:///", "") if DATABASE_URL else "database.db"
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        conn = None
        try:
            conn = pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger_db.error(f"Erro na conexão: {e}")
            raise
        finally:
            if conn:
                pool.putconn(conn)


# ==========================================
# 🚀 CRIAR TABELAS
# ==========================================
def criar_tabelas():
    if not DATABASE_ENABLED:
        logger_db.warning("Banco indisponível - pulando criação")
        return

    with get_db_connection() as conn:
        cur = conn.cursor()

        if USE_SQLITE:
            id_field = "INTEGER PRIMARY KEY AUTOINCREMENT"
            timestamp_field = "DATETIME DEFAULT CURRENT_TIMESTAMP"
        else:
            id_field = "SERIAL PRIMARY KEY"
            timestamp_field = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            id {id_field},
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            plano TEXT DEFAULT 'free',
            criado_em {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS memoria (
            id {id_field},
            pergunta TEXT NOT NULL,
            resposta TEXT NOT NULL,
            confianca INTEGER DEFAULT 1,
            criado_em {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS history (
            id {id_field},
            user_id INTEGER,
            pergunta TEXT NOT NULL,
            resposta TEXT NOT NULL,
            criado_em {timestamp_field}
        )
        """)

        cur.close()
        logger_db.info("✅ Tabelas verificadas/criadas")


# ==========================================
# 👤 USERS
# ==========================================
def criar_usuario(nome, email, senha_hash, plano="free"):
    """
    Recebe senha_hash já gerado no auth.py
    """
    if not DATABASE_ENABLED:
        return None

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"

            if USE_POSTGRES:
                cur.execute(f"""
                    INSERT INTO users (nome, email, senha_hash, plano)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
                    RETURNING id, nome, email, senha_hash, plano
                """, (nome, email, senha_hash, plano))
                user = cur.fetchone()
            else:
                cur.execute(f"""
                    INSERT INTO users (nome, email, senha_hash, plano)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
                """, (nome, email, senha_hash, plano))
                user_id = cur.lastrowid
                cur.execute(f"""
                    SELECT id, nome, email, senha_hash, plano
                    FROM users
                    WHERE id = {placeholder}
                """, (user_id,))
                user = cur.fetchone()

            cur.close()

            if user:
                user = dict(zip(["id", "nome", "email", "senha_hash", "plano"], user))

            return user

    except Exception as e:
        logger_db.error(f"Erro ao criar usuário: {e}")
        return None


def buscar_usuario(identificador):
    if not DATABASE_ENABLED:
        return None

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"

            if isinstance(identificador, int):
                cur.execute(f"""
                    SELECT id, nome, email, senha_hash, plano
                    FROM users
                    WHERE id = {placeholder}
                """, (identificador,))
            elif isinstance(identificador, str):
                cur.execute(f"""
                    SELECT id, nome, email, senha_hash, plano
                    FROM users
                    WHERE email = {placeholder}
                """, (identificador,))
            else:
                cur.close()
                return None

            user = cur.fetchone()
            cur.close()

            if user:
                user = dict(zip(["id", "nome", "email", "senha_hash", "plano"], user))

            return user

    except Exception as e:
        logger_db.error(f"Erro ao buscar usuário: {e}")
        return None


def buscar_usuario_por_email(email):
    return buscar_usuario(email)


def buscar_usuario_por_id(user_id):
    return buscar_usuario(user_id)


# ==========================================
# 🧠 MEMÓRIA IA
# ==========================================
def buscar_memoria(pergunta):
    if not DATABASE_ENABLED:
        return None

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"

            cur.execute(f"""
                SELECT resposta
                FROM memoria
                WHERE pergunta = {placeholder}
                ORDER BY confianca DESC
                LIMIT 1
            """, (pergunta.lower(),))

            r = cur.fetchone()
            cur.close()

            return r[0] if r else None

    except Exception as e:
        logger_db.error(f"Erro ao buscar memória: {e}")
        return None


def aprender(pergunta, resposta):
    if not DATABASE_ENABLED:
        return

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"

            cur.execute(f"""
                SELECT id
                FROM memoria
                WHERE pergunta = {placeholder} AND resposta = {placeholder}
            """, (pergunta.lower(), resposta))

            existe = cur.fetchone()

            if existe:
                cur.execute(f"""
                    UPDATE memoria
                    SET confianca = confianca + 1
                    WHERE id = {placeholder}
                """, (existe[0],))
            else:
                cur.execute(f"""
                    INSERT INTO memoria (pergunta, resposta)
                    VALUES ({placeholder}, {placeholder})
                """, (pergunta.lower(), resposta))

            cur.close()

    except Exception as e:
        logger_db.error(f"Erro ao aprender: {e}")


# ==========================================
# 📜 HISTÓRICO
# ==========================================
def salvar_historico(user_id, pergunta, resposta):
    if not DATABASE_ENABLED:
        logger_db.warning("Banco indisponível - histórico não salvo")
        return

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"

            cur.execute(f"""
                INSERT INTO history (user_id, pergunta, resposta)
                VALUES ({placeholder}, {placeholder}, {placeholder})
            """, (user_id, pergunta, resposta))

            cur.close()

    except Exception as e:
        logger_db.error(f"Erro ao salvar histórico: {e}")


def buscar_historico(user_id, limite=50):
    if not DATABASE_ENABLED:
        return []

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"

            cur.execute(f"""
                SELECT pergunta, resposta, criado_em
                FROM history
                WHERE user_id = {placeholder}
                ORDER BY criado_em DESC
                LIMIT {limite}
            """, (user_id,))

            rows = cur.fetchall()
            cur.close()

            return [
                {"pergunta": r[0], "resposta": r[1], "criado_em": r[2]}
                for r in rows
            ]

    except Exception as e:
        logger_db.error(f"Erro ao buscar histórico: {e}")
        return []


def limpar_historico(user_id):
    if not DATABASE_ENABLED:
        return

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"

            cur.execute(f"""
                DELETE FROM history
                WHERE user_id = {placeholder}
            """, (user_id,))

            cur.close()

    except Exception as e:
        logger_db.error(f"Erro ao limpar histórico: {e}")
