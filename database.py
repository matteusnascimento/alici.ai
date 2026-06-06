"""
database.py
Conexão com PostgreSQL (Neon) ou SQLite
VERSÃO PRODUÇÃO PROFISSIONAL
"""

import os
import json
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
            criado_em {timestamp_field}
        )
        """)

        if USE_SQLITE:
            cur.execute("PRAGMA table_info(users)")
            columns = [row[1] for row in cur.fetchall()]
            if "mensagens_hoje" not in columns:
                cur.execute("ALTER TABLE users ADD COLUMN mensagens_hoje INTEGER DEFAULT 0")
        else:
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS mensagens_hoje INTEGER DEFAULT 0")

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

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS ai_logs (
            id {id_field},
            pergunta TEXT NOT NULL,
            resposta TEXT NOT NULL,
            provider TEXT NOT NULL,
            modelo TEXT NOT NULL,
            tempo_resposta_ms INTEGER DEFAULT 0,
            tokens_estimados INTEGER DEFAULT 0,
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


def salvar_ai_log(pergunta, resposta, provider, modelo, tempo_resposta_ms=0, tokens_estimados=0):
    if not DATABASE_ENABLED:
        logger_db.warning("Banco indisponivel - log de IA nao salvo")
        return

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"

            cur.execute(f"""
                INSERT INTO ai_logs (
                    pergunta,
                    resposta,
                    provider,
                    modelo,
                    tempo_resposta_ms,
                    tokens_estimados
                )
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            """, (
                pergunta,
                resposta,
                provider,
                modelo,
                int(tempo_resposta_ms or 0),
                int(tokens_estimados or 0),
            ))

            cur.close()

    except Exception as e:
        logger_db.error(f"Erro ao salvar log de IA: {e}")


def _placeholder():
    return "?" if USE_SQLITE else "%s"


def _json_db_value(value):
    payload = value or {}
    if USE_POSTGRES:
        from psycopg2.extras import Json

        return Json(payload)
    return json.dumps(payload, ensure_ascii=False)


def _row_to_dict(cur, row):
    if not row:
        return None
    if hasattr(row, "keys"):
        return dict(row)
    columns = [desc[0] for desc in cur.description]
    return dict(zip(columns, row))


def iniciar_evento_stripe(event_id, event_type, payload):
    """Return True when this process owns the event, False for duplicate/in-flight."""
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco indisponivel para idempotencia Stripe")

    with get_db_connection() as conn:
        cur = conn.cursor()
        placeholder = _placeholder()
        payload_value = _json_db_value(payload)

        if USE_POSTGRES:
            cur.execute(
                f"""
                INSERT INTO stripe_events (id, type, status, payload)
                VALUES ({placeholder}, {placeholder}, 'processing', {placeholder})
                ON CONFLICT (id) DO NOTHING
                RETURNING id
                """,
                (event_id, event_type, payload_value),
            )
            inserted = cur.fetchone()
        else:
            cur.execute(
                f"""
                INSERT OR IGNORE INTO stripe_events (id, type, status, payload)
                VALUES ({placeholder}, {placeholder}, 'processing', {placeholder})
                """,
                (event_id, event_type, payload_value),
            )
            inserted = cur.rowcount == 1

        if inserted:
            cur.close()
            return True

        cur.execute(f"SELECT status FROM stripe_events WHERE id = {placeholder}", (event_id,))
        row = cur.fetchone()
        status = row["status"] if hasattr(row, "keys") else row[0]
        if status in {"processed", "processing", "ignored"}:
            cur.close()
            return False

        if USE_POSTGRES:
            cur.execute(
                f"""
                UPDATE stripe_events
                SET status = 'processing',
                    attempts = attempts + 1,
                    type = {placeholder},
                    payload = {placeholder},
                    error_message = NULL,
                    updated_at = NOW()
                WHERE id = {placeholder}
                """,
                (event_type, payload_value, event_id),
            )
        else:
            cur.execute(
                f"""
                UPDATE stripe_events
                SET status = 'processing',
                    attempts = attempts + 1,
                    type = {placeholder},
                    payload = {placeholder},
                    error_message = NULL,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = {placeholder}
                """,
                (event_type, payload_value, event_id),
            )
        cur.close()
        return True


def marcar_evento_stripe_processado(event_id, status="processed"):
    if not DATABASE_ENABLED:
        return
    with get_db_connection() as conn:
        cur = conn.cursor()
        placeholder = _placeholder()
        if USE_POSTGRES:
            cur.execute(
                f"""
                UPDATE stripe_events
                SET status = {placeholder}, updated_at = NOW(), processed_at = NOW(), error_message = NULL
                WHERE id = {placeholder}
                """,
                (status, event_id),
            )
        else:
            cur.execute(
                f"""
                UPDATE stripe_events
                SET status = {placeholder}, updated_at = CURRENT_TIMESTAMP, processed_at = CURRENT_TIMESTAMP, error_message = NULL
                WHERE id = {placeholder}
                """,
                (status, event_id),
            )
        cur.close()


def marcar_evento_stripe_falhou(event_id, error_message):
    if not DATABASE_ENABLED:
        return
    with get_db_connection() as conn:
        cur = conn.cursor()
        placeholder = _placeholder()
        if USE_POSTGRES:
            cur.execute(
                f"""
                UPDATE stripe_events
                SET status = 'failed', error_message = {placeholder}, updated_at = NOW()
                WHERE id = {placeholder}
                """,
                (str(error_message)[:2000], event_id),
            )
        else:
            cur.execute(
                f"""
                UPDATE stripe_events
                SET status = 'failed', error_message = {placeholder}, updated_at = CURRENT_TIMESTAMP
                WHERE id = {placeholder}
                """,
                (str(error_message)[:2000], event_id),
            )
        cur.close()


def buscar_assinatura_usuario(user_id):
    if not DATABASE_ENABLED:
        return None
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = _placeholder()
            cur.execute(
                f"""
                SELECT id, user_id, stripe_id, stripe_customer_id, stripe_subscription_id,
                       stripe_price_id, status, plano, renovacao, current_period_end,
                       criado_em, updated_at
                FROM subscriptions
                WHERE user_id = {placeholder}
                ORDER BY updated_at DESC, id DESC
                LIMIT 1
                """,
                (user_id,),
            )
            row = cur.fetchone()
            result = _row_to_dict(cur, row)
            cur.close()
            return result
    except Exception as e:
        logger_db.error(f"Erro ao buscar assinatura do usuario: {e}")
        return None


def salvar_assinatura_usuario(
    user_id,
    *,
    stripe_customer_id=None,
    stripe_subscription_id=None,
    stripe_price_id=None,
    status="inactive",
    plano="free",
    current_period_end=None,
):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco indisponivel para salvar assinatura")

    placeholder = _placeholder()
    period_value = current_period_end
    if USE_SQLITE and isinstance(current_period_end, datetime):
        period_value = current_period_end.isoformat()

    with get_db_connection() as conn:
        cur = conn.cursor()

        row = None
        if stripe_subscription_id:
            cur.execute(
                f"SELECT id FROM subscriptions WHERE stripe_subscription_id = {placeholder} LIMIT 1",
                (stripe_subscription_id,),
            )
            row = cur.fetchone()

        if not row:
            cur.execute(
                f"SELECT id FROM subscriptions WHERE user_id = {placeholder} ORDER BY id DESC LIMIT 1",
                (user_id,),
            )
            row = cur.fetchone()

        if row:
            subscription_id = row[0]
            if USE_POSTGRES:
                cur.execute(
                    f"""
                    UPDATE subscriptions
                    SET stripe_id = {placeholder},
                        stripe_customer_id = {placeholder},
                        stripe_subscription_id = {placeholder},
                        stripe_price_id = {placeholder},
                        status = {placeholder},
                        plano = {placeholder},
                        renovacao = COALESCE({placeholder}, renovacao),
                        current_period_end = {placeholder},
                        updated_at = NOW()
                    WHERE id = {placeholder}
                    """,
                    (
                        stripe_subscription_id,
                        stripe_customer_id,
                        stripe_subscription_id,
                        stripe_price_id,
                        status,
                        plano,
                        period_value,
                        period_value,
                        subscription_id,
                    ),
                )
            else:
                cur.execute(
                    f"""
                    UPDATE subscriptions
                    SET stripe_id = {placeholder},
                        stripe_customer_id = {placeholder},
                        stripe_subscription_id = {placeholder},
                        stripe_price_id = {placeholder},
                        status = {placeholder},
                        plano = {placeholder},
                        renovacao = COALESCE({placeholder}, renovacao),
                        current_period_end = {placeholder},
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = {placeholder}
                    """,
                    (
                        stripe_subscription_id,
                        stripe_customer_id,
                        stripe_subscription_id,
                        stripe_price_id,
                        status,
                        plano,
                        period_value,
                        period_value,
                        subscription_id,
                    ),
                )
        else:
            cur.execute(
                f"""
                INSERT INTO subscriptions (
                    user_id, stripe_id, stripe_customer_id, stripe_subscription_id,
                    stripe_price_id, status, plano, renovacao, current_period_end
                )
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """,
                (
                    user_id,
                    stripe_subscription_id,
                    stripe_customer_id,
                    stripe_subscription_id,
                    stripe_price_id,
                    status,
                    plano,
                    period_value,
                    period_value,
                ),
            )

        cur.execute(
            f"UPDATE users SET plano = {placeholder} WHERE id = {placeholder}",
            (plano, user_id),
        )
        cur.close()


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
