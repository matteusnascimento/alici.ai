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
                logger_db.warning(
                    f"Tentativa {attempt+1}/{retries} falhou ao conectar no Neon..."
                )
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

        db_path = DATABASE_URL.replace("sqlite:///", "")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        try:
            yield conn
            conn.commit()
        except:
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

def buscar_usuario_por_email(email):

    if not DATABASE_ENABLED:
        return None

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()

            placeholder = "?" if USE_SQLITE else "%s"

            cur.execute(f"""
                SELECT id, nome, email, senha_hash, plano
                FROM users
                WHERE email = {placeholder}
            """, (email,))

            user = cur.fetchone()
            cur.close()

            return user

    except Exception as e:
        logger_db.error(f"Erro ao buscar usuário: {e}")
        return None


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
                WHERE pergunta = {placeholder}
                AND resposta = {placeholder}
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
