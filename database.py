"""
database.py
Conexão com PostgreSQL (Neon) ou SQLite
VERSÃO PRODUÇÃO PROFISSIONAL
"""

import os
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv

from logger import get_logger

logger_db = get_logger("database")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
USE_SQLITE = DATABASE_URL and DATABASE_URL.startswith("sqlite")
USE_POSTGRES = DATABASE_URL and DATABASE_URL.startswith("postgresql")

pool = None
DATABASE_ENABLED = False

if not DATABASE_URL:
    logger_db.warning("⚠️ DATABASE_URL não configurado")

elif USE_POSTGRES:
    try:
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
            mensagens_hoje INTEGER DEFAULT 0,
            foto_url TEXT,
            tema TEXT DEFAULT 'dark',
            criado_em {timestamp_field}
        )
        """)

        if USE_SQLITE:
            cur.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cur.fetchall()]
            if "mensagens_hoje" not in columns:
                cur.execute("ALTER TABLE users ADD COLUMN mensagens_hoje INTEGER DEFAULT 0")
            if "foto_url" not in columns:
                cur.execute("ALTER TABLE users ADD COLUMN foto_url TEXT")
            if "tema" not in columns:
                cur.execute("ALTER TABLE users ADD COLUMN tema TEXT DEFAULT 'dark'")
        else:
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS mensagens_hoje INTEGER DEFAULT 0")
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS foto_url TEXT")
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS tema TEXT DEFAULT 'dark'")

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

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id {id_field},
            user_id INTEGER NOT NULL,
            stripe_id TEXT,
            status TEXT DEFAULT 'inactive',
            plano TEXT DEFAULT 'free',
            renovacao {timestamp_field},
            criado_em {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS conversations (
            id {id_field},
            user_id INTEGER NOT NULL,
            titulo TEXT,
            criado_em {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS messages (
            id {id_field},
            conversation_id INTEGER,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            criado_em {timestamp_field}
        )
        """)

        if USE_SQLITE:
            refresh_token_id_field = "INTEGER PRIMARY KEY AUTOINCREMENT"
            refresh_expires_field = "TEXT NOT NULL"
            refresh_revoked_field = "INTEGER DEFAULT 0"
        else:
            refresh_token_id_field = "SERIAL PRIMARY KEY"
            refresh_expires_field = "TIMESTAMP NOT NULL"
            refresh_revoked_field = "BOOLEAN DEFAULT FALSE"

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id {refresh_token_id_field},
            user_id INTEGER NOT NULL,
            jti TEXT UNIQUE NOT NULL,
            expires_at {refresh_expires_field},
            revoked {refresh_revoked_field},
            created_ip TEXT,
            user_agent TEXT,
            criado_em {timestamp_field}
        )
        """)

        cur.close()
        logger_db.info("✅ Tabelas verificadas/criadas")


def criar_usuario(nome, email, senha_hash, plano="free"):
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
                    RETURNING id, nome, email, senha_hash, plano, foto_url, tema
                """, (nome, email, senha_hash, plano))
                user = cur.fetchone()
            else:
                cur.execute(f"""
                    INSERT INTO users (nome, email, senha_hash, plano)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
                """, (nome, email, senha_hash, plano))
                user_id = cur.lastrowid
                cur.execute(f"""
                    SELECT id, nome, email, senha_hash, plano, foto_url, tema
                    FROM users
                    WHERE id = {placeholder}
                """, (user_id,))
                user = cur.fetchone()

            cur.close()

            if user:
                user = dict(zip(["id", "nome", "email", "senha_hash", "plano", "foto_url", "tema"], user))

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
                    SELECT id, nome, email, senha_hash, plano, foto_url, tema
                    FROM users
                    WHERE id = {placeholder}
                """, (identificador,))
            elif isinstance(identificador, str):
                cur.execute(f"""
                    SELECT id, nome, email, senha_hash, plano, foto_url, tema
                    FROM users
                    WHERE email = {placeholder}
                """, (identificador,))
            else:
                cur.close()
                return None

            user = cur.fetchone()
            cur.close()

            if user:
                user = dict(zip(["id", "nome", "email", "senha_hash", "plano", "foto_url", "tema"], user))

            return user

    except Exception as e:
        logger_db.error(f"Erro ao buscar usuário: {e}")
        return None


def buscar_usuario_por_email(email):
    return buscar_usuario(email)


def buscar_usuario_por_id(user_id):
    return buscar_usuario(user_id)


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


def contar_mensagens_hoje(user_id):
    if not DATABASE_ENABLED:
        return 0

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"

            if USE_SQLITE:
                cur.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM history
                    WHERE user_id = {placeholder}
                      AND date(criado_em) = date('now')
                    """,
                    (user_id,),
                )
            else:
                cur.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM history
                    WHERE user_id = {placeholder}
                      AND DATE(criado_em) = CURRENT_DATE
                    """,
                    (user_id,),
                )

            total = cur.fetchone()[0]
            cur.close()
            return int(total or 0)

    except Exception as e:
        logger_db.error(f"Erro ao contar mensagens do dia: {e}")
        return 0


def _to_utc_datetime(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if isinstance(value, str):
        value = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(value)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except Exception:
            return None
    return None


def salvar_refresh_token(user_id, jti, expires_at, created_ip=None, user_agent=None):
    if not DATABASE_ENABLED:
        return False

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"
            parsed_exp = _to_utc_datetime(expires_at)
            expires_value = parsed_exp.isoformat() if USE_SQLITE and parsed_exp else parsed_exp

            cur.execute(
                f"""
                INSERT INTO refresh_tokens (user_id, jti, expires_at, revoked, created_ip, user_agent)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """,
                (user_id, jti, expires_value, 0 if USE_SQLITE else False, created_ip, user_agent),
            )
            cur.close()
            return True
    except Exception as e:
        logger_db.error(f"Erro ao salvar refresh token: {e}")
        return False


def buscar_refresh_token_por_jti(jti):
    if not DATABASE_ENABLED:
        return None

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"

            cur.execute(
                f"""
                SELECT id, user_id, jti, expires_at, revoked, created_ip, user_agent
                FROM refresh_tokens
                WHERE jti = {placeholder}
                LIMIT 1
                """,
                (jti,),
            )
            row = cur.fetchone()
            cur.close()

            if not row:
                return None

            data = dict(zip(["id", "user_id", "jti", "expires_at", "revoked", "created_ip", "user_agent"], row))
            data["expires_at"] = _to_utc_datetime(data.get("expires_at"))
            data["revoked"] = bool(data.get("revoked"))
            return data
    except Exception as e:
        logger_db.error(f"Erro ao buscar refresh token: {e}")
        return None


def revogar_refresh_token_por_jti(jti):
    if not DATABASE_ENABLED:
        return False

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"
            cur.execute(
                f"""
                UPDATE refresh_tokens
                SET revoked = {placeholder}
                WHERE jti = {placeholder}
                """,
                (1 if USE_SQLITE else True, jti),
            )
            cur.close()
            return True
    except Exception as e:
        logger_db.error(f"Erro ao revogar refresh token: {e}")
        return False


def revogar_refresh_tokens_usuario(user_id):
    if not DATABASE_ENABLED:
        return False

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"
            cur.execute(
                f"""
                UPDATE refresh_tokens
                SET revoked = {placeholder}
                WHERE user_id = {placeholder}
                """,
                (1 if USE_SQLITE else True, user_id),
            )
            cur.close()
            return True
    except Exception as e:
        logger_db.error(f"Erro ao revogar tokens do usuário: {e}")
        return False


def atualizar_perfil(user_id, nome=None, senha_hash=None, foto_url=None, tema=None):
    """Update user profile fields."""
    if not DATABASE_ENABLED:
        return False

    placeholder = "?" if USE_SQLITE else "%s"
    updates = []
    values = []

    if nome is not None:
        updates.append(f"nome = {placeholder}")
        values.append(nome)
    if senha_hash is not None:
        updates.append(f"senha_hash = {placeholder}")
        values.append(senha_hash)
    if foto_url is not None:
        updates.append(f"foto_url = {placeholder}")
        values.append(foto_url)
    if tema is not None:
        updates.append(f"tema = {placeholder}")
        values.append(tema)

    if not updates:
        return True

    values.append(user_id)
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE id = {placeholder}",
                values,
            )
            cur.close()
            return True
    except Exception as e:
        logger_db.error(f"Erro ao atualizar perfil: {e}")
        return False


def criar_conversa(user_id, titulo=None):
    """Create a new conversation and return it."""
    if not DATABASE_ENABLED:
        return None

    titulo = titulo or "Nova Conversa"
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"

            if USE_POSTGRES:
                cur.execute(
                    f"""
                    INSERT INTO conversations (user_id, titulo)
                    VALUES ({placeholder}, {placeholder})
                    RETURNING id, user_id, titulo, criado_em
                    """,
                    (user_id, titulo),
                )
                row = cur.fetchone()
            else:
                cur.execute(
                    f"""
                    INSERT INTO conversations (user_id, titulo)
                    VALUES ({placeholder}, {placeholder})
                    """,
                    (user_id, titulo),
                )
                conv_id = cur.lastrowid
                cur.execute(
                    f"SELECT id, user_id, titulo, criado_em FROM conversations WHERE id = {placeholder}",
                    (conv_id,),
                )
                row = cur.fetchone()

            cur.close()
            if row:
                return dict(zip(["id", "user_id", "titulo", "criado_em"], row))
            return None
    except Exception as e:
        logger_db.error(f"Erro ao criar conversa: {e}")
        return None


def listar_conversas(user_id):
    """List conversations for a user (most recent first)."""
    if not DATABASE_ENABLED:
        return []

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"
            cur.execute(
                f"""
                SELECT id, titulo, criado_em
                FROM conversations
                WHERE user_id = {placeholder}
                ORDER BY criado_em DESC
                LIMIT 50
                """,
                (user_id,),
            )
            rows = cur.fetchall()
            cur.close()
            return [{"id": r[0], "titulo": r[1], "criado_em": str(r[2])} for r in rows]
    except Exception as e:
        logger_db.error(f"Erro ao listar conversas: {e}")
        return []


def buscar_mensagens_conversa(conversation_id, user_id):
    """Get messages for a conversation with ownership check.

    Returns None if the conversation is not found or does not belong to user_id.
    """
    if not DATABASE_ENABLED:
        return []

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"

            cur.execute(
                f"SELECT id FROM conversations WHERE id = {placeholder} AND user_id = {placeholder}",
                (conversation_id, user_id),
            )
            if not cur.fetchone():
                cur.close()
                return None

            cur.execute(
                f"""
                SELECT role, content, criado_em
                FROM messages
                WHERE conversation_id = {placeholder}
                ORDER BY criado_em ASC
                """,
                (conversation_id,),
            )
            rows = cur.fetchall()
            cur.close()
            return [{"role": r[0], "content": r[1], "criado_em": str(r[2])} for r in rows]
    except Exception as e:
        logger_db.error(f"Erro ao buscar mensagens: {e}")
        return []


def salvar_mensagem_conversa(conversation_id, role, content):
    """Save a message to a conversation."""
    if not DATABASE_ENABLED:
        return False

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"
            cur.execute(
                f"""
                INSERT INTO messages (conversation_id, role, content)
                VALUES ({placeholder}, {placeholder}, {placeholder})
                """,
                (conversation_id, role, content),
            )
            cur.close()
            return True
    except Exception as e:
        logger_db.error(f"Erro ao salvar mensagem: {e}")
        return False


def atualizar_titulo_conversa(conversation_id, user_id, titulo):
    """Update the title of a conversation."""
    if not DATABASE_ENABLED:
        return False

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"
            cur.execute(
                f"""
                UPDATE conversations
                SET titulo = {placeholder}
                WHERE id = {placeholder} AND user_id = {placeholder}
                """,
                (titulo, conversation_id, user_id),
            )
            cur.close()
            return True
    except Exception as e:
        logger_db.error(f"Erro ao atualizar título: {e}")
        return False


def excluir_conversa(conversation_id, user_id):
    """Delete a conversation and all its messages (with ownership check)."""
    if not DATABASE_ENABLED:
        return False

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"

            cur.execute(
                f"SELECT id FROM conversations WHERE id = {placeholder} AND user_id = {placeholder}",
                (conversation_id, user_id),
            )
            if not cur.fetchone():
                cur.close()
                return False

            cur.execute(
                f"DELETE FROM messages WHERE conversation_id = {placeholder}",
                (conversation_id,),
            )
            cur.execute(
                f"DELETE FROM conversations WHERE id = {placeholder} AND user_id = {placeholder}",
                (conversation_id, user_id),
            )
            cur.close()
            return True
    except Exception as e:
        logger_db.error(f"Erro ao excluir conversa: {e}")
        return False
