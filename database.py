"""
database.py
Conexão com PostgreSQL (Neon) ou SQLite e operações de banco de dados
VERSÃO PRODUÇÃO
"""

import os
import sqlite3
from contextlib import contextmanager
from dotenv import load_dotenv
from logger import get_logger

logger_db = get_logger("database")

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_ENABLED = bool(DATABASE_URL)

USE_SQLITE = DATABASE_URL and DATABASE_URL.startswith("sqlite")
USE_POSTGRES = DATABASE_URL and DATABASE_URL.startswith("postgresql")

pool = None


# ==========================================
# DETECÇÃO DO BANCO
# ==========================================

if not DATABASE_ENABLED:
    logger_db.warning("⚠️ DATABASE_URL não configurado")

elif USE_SQLITE:
    logger_db.info("🗄️ Usando SQLite")

elif USE_POSTGRES:
    try:
        import psycopg2
        from psycopg2.pool import SimpleConnectionPool

        pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=DATABASE_URL,
            sslmode="require",
        )

        logger_db.info("🗄️ Usando PostgreSQL/Neon com pool de conexões")

    except Exception as e:
        logger_db.error(f"❌ Erro ao conectar no PostgreSQL: {e}")
        DATABASE_ENABLED = False

else:
    logger_db.error("❌ DATABASE_URL inválido")
    DATABASE_ENABLED = False


# ==========================================
# CONTEXT MANAGER
# ==========================================

@contextmanager
def get_db_connection():

    if not DATABASE_ENABLED:
        raise RuntimeError("Banco não configurado")

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
        conn = pool.getconn()

        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            pool.putconn(conn)


# ==========================================
# 🚀 CRIAR TABELAS AUTOMATICAMENTE
# ==========================================

def criar_tabelas():

    if not DATABASE_ENABLED:
        logger_db.warning("Banco não configurado - pulando criação")
        return

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()

            if USE_SQLITE:
                id_field = "INTEGER PRIMARY KEY AUTOINCREMENT"
                timestamp_field = "DATETIME DEFAULT CURRENT_TIMESTAMP"
            else:
                id_field = "SERIAL PRIMARY KEY"
                timestamp_field = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"

            # ================= USERS (LOGIN / REGISTER) =================
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                id {id_field},
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                plano TEXT DEFAULT 'free',
                criado_em {timestamp_field},
                atualizado_em {timestamp_field}
            )
            """)

            # ================= MEMÓRIA IA =================
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS memoria (
                id {id_field},
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL,
                confianca INTEGER DEFAULT 1,
                criado_em {timestamp_field}
            )
            """)

            # ================= HISTORY =================
            cur.execute(f"""
            CREATE TABLE IF NOT EXISTS history (
                id {id_field},
                user_id INTEGER NOT NULL,
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL,
                criado_em {timestamp_field},
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """)

            # ================= ÍNDICES =================

            if USE_POSTGRES:

                cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_email
                ON users(email);
                """)

                cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_memoria_pergunta
                ON memoria(pergunta);
                """)

                cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_user
                ON history(user_id);
                """)

            else:

                cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_memoria_pergunta ON memoria(pergunta)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_history_user ON history(user_id)")

            cur.close()

            logger_db.info("✅ Tabelas verificadas/criadas com sucesso")

    except Exception as e:
        logger_db.error(f"❌ Erro ao criar tabelas: {e}")


# ==========================================
# MEMÓRIA IA
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
