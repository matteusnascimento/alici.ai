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

        if USE_SQLITE:
            bool_field = "INTEGER DEFAULT 1"
            json_field = "TEXT"
        else:
            bool_field = "BOOLEAN DEFAULT TRUE"
            json_field = "JSONB"

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS user_social_connections (
            id {id_field},
            user_id INTEGER NOT NULL,
            provider TEXT NOT NULL,
            external_account_id TEXT NOT NULL,
            external_account_name TEXT,
            access_token TEXT,
            status TEXT DEFAULT 'connected',
            enabled {bool_field},
            metadata {json_field},
            created_at {timestamp_field},
            updated_at {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS omnichannel_conversations (
            id {id_field},
            user_id INTEGER NOT NULL,
            connection_id INTEGER NOT NULL,
            provider TEXT NOT NULL,
            external_account_id TEXT NOT NULL,
            external_contact_id TEXT NOT NULL,
            contact_name TEXT,
            conversation_id INTEGER NOT NULL,
            created_at {timestamp_field},
            last_message_at {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS omnichannel_messages (
            id {id_field},
            user_id INTEGER NOT NULL,
            connection_id INTEGER NOT NULL,
            omnichannel_conversation_id INTEGER NOT NULL,
            conversation_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            provider TEXT NOT NULL,
            direction TEXT NOT NULL,
            external_message_id TEXT,
            external_contact_id TEXT NOT NULL,
            content TEXT NOT NULL,
            raw_payload {json_field},
            created_at {timestamp_field}
        )
        """)

        cur.execute("CREATE INDEX IF NOT EXISTS idx_user_social_connections_user ON user_social_connections (user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_user_social_connections_provider ON user_social_connections (provider, external_account_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_omnichannel_conversations_lookup ON omnichannel_conversations (provider, external_account_id, external_contact_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_omnichannel_messages_user ON omnichannel_messages (user_id, provider)")

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS business_pipelines (
            id {id_field},
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            stages {json_field},
            is_default {bool_field},
            created_at {timestamp_field},
            updated_at {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS business_contacts (
            id {id_field},
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            company TEXT,
            status TEXT DEFAULT 'prospect',
            source TEXT DEFAULT 'manual',
            last_interaction_at {timestamp_field},
            created_at {timestamp_field},
            updated_at {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS business_deals (
            id {id_field},
            user_id INTEGER NOT NULL,
            pipeline_id INTEGER,
            contact_id INTEGER,
            title TEXT NOT NULL,
            value_cents INTEGER DEFAULT 0,
            currency TEXT DEFAULT 'BRL',
            stage TEXT DEFAULT 'novo',
            status TEXT DEFAULT 'open',
            probability INTEGER DEFAULT 10,
            expected_close_date TEXT,
            created_at {timestamp_field},
            updated_at {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS business_products (
            id {id_field},
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price_cents INTEGER DEFAULT 0,
            currency TEXT DEFAULT 'BRL',
            status TEXT DEFAULT 'active',
            created_at {timestamp_field},
            updated_at {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS business_calls (
            id {id_field},
            user_id INTEGER NOT NULL,
            contact_id INTEGER,
            phone TEXT NOT NULL,
            direction TEXT DEFAULT 'outbound',
            outcome TEXT DEFAULT 'pending',
            duration_seconds INTEGER DEFAULT 0,
            notes TEXT,
            created_at {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS business_groups (
            id {id_field},
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            created_at {timestamp_field},
            updated_at {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS business_meetings (
            id {id_field},
            user_id INTEGER NOT NULL,
            contact_id INTEGER,
            title TEXT NOT NULL,
            scheduled_at TEXT,
            status TEXT DEFAULT 'scheduled',
            notes TEXT,
            created_at {timestamp_field},
            updated_at {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS business_contracts (
            id {id_field},
            user_id INTEGER NOT NULL,
            contact_id INTEGER,
            deal_id INTEGER,
            title TEXT NOT NULL,
            value_cents INTEGER DEFAULT 0,
            status TEXT DEFAULT 'draft',
            signed_at TEXT,
            created_at {timestamp_field},
            updated_at {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS business_tasks (
            id {id_field},
            user_id INTEGER NOT NULL,
            contact_id INTEGER,
            title TEXT NOT NULL,
            due_at TEXT,
            status TEXT DEFAULT 'open',
            priority TEXT DEFAULT 'medium',
            created_at {timestamp_field},
            updated_at {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS business_quick_messages (
            id {id_field},
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            category TEXT DEFAULT 'atendimento',
            status TEXT DEFAULT 'active',
            created_at {timestamp_field},
            updated_at {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS business_logistics (
            id {id_field},
            user_id INTEGER NOT NULL,
            contact_id INTEGER,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            tracking_code TEXT,
            notes TEXT,
            created_at {timestamp_field},
            updated_at {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS business_revenue_goals (
            id {id_field},
            user_id INTEGER NOT NULL,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            target_cents INTEGER DEFAULT 0,
            created_at {timestamp_field},
            updated_at {timestamp_field}
        )
        """)

        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS marketing_projects (
            id {id_field},
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            audience TEXT NOT NULL,
            objective TEXT NOT NULL,
            offer TEXT NOT NULL,
            tone TEXT DEFAULT 'premium',
            notes TEXT,
            created_at {timestamp_field},
            updated_at {timestamp_field}
        )
        """)

        cur.execute("CREATE INDEX IF NOT EXISTS idx_business_contacts_user ON business_contacts (user_id, status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_business_deals_user ON business_deals (user_id, status, stage)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_business_products_user ON business_products (user_id, status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_business_calls_user ON business_calls (user_id, created_at)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_business_groups_user ON business_groups (user_id, status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_business_meetings_user ON business_meetings (user_id, status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_business_contracts_user ON business_contracts (user_id, status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_business_tasks_user ON business_tasks (user_id, status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_business_quick_messages_user ON business_quick_messages (user_id, status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_business_logistics_user ON business_logistics (user_id, status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_business_revenue_goals_user ON business_revenue_goals (user_id, year, month)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_marketing_projects_user ON marketing_projects (user_id, created_at)")

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
        logger_db.error(f"Erro ao revogar tokens do usuario: {e}")
        return False


def _json_or_dict(value):
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return {}
    return {}


def _social_connection_from_row(row):
    if not row:
        return None
    keys = [
        "id", "user_id", "provider", "external_account_id", "external_account_name",
        "access_token", "status", "enabled", "metadata", "created_at", "updated_at",
    ]
    data = dict(zip(keys, row))
    data["enabled"] = bool(data.get("enabled"))
    data["metadata"] = _json_or_dict(data.get("metadata"))
    return data


def criar_conexao_social(user_id, provider, external_account_id, external_account_name=None, access_token=None, metadata=None, enabled=True):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")

    p = "?" if USE_SQLITE else "%s"
    enabled_value = 1 if USE_SQLITE and enabled else 0 if USE_SQLITE else enabled
    metadata_payload = json.dumps(metadata or {}, ensure_ascii=False)
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            INSERT INTO user_social_connections
                (user_id, provider, external_account_id, external_account_name, access_token, status, enabled, metadata)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
            """,
            (user_id, provider, external_account_id, external_account_name, access_token, "connected", enabled_value, metadata_payload),
        )
        if USE_SQLITE:
            connection_id = cur.lastrowid
        else:
            cur.execute("SELECT LASTVAL()")
            connection_id = cur.fetchone()[0]
        cur.close()
    return buscar_conexao_social_por_id(user_id, connection_id)


def buscar_conexao_social_por_id(user_id, connection_id):
    if not DATABASE_ENABLED:
        return None
    try:
        p = "?" if USE_SQLITE else "%s"
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT id, user_id, provider, external_account_id, external_account_name,
                       access_token, status, enabled, metadata, created_at, updated_at
                FROM user_social_connections
                WHERE user_id = {p} AND id = {p}
                LIMIT 1
                """,
                (user_id, connection_id),
            )
            row = cur.fetchone()
            cur.close()
            return _social_connection_from_row(row)
    except Exception as e:
        logger_db.error(f"Erro ao buscar conexao social: {e}")
        return None


def listar_conexoes_sociais(user_id):
    if not DATABASE_ENABLED:
        return []
    try:
        p = "?" if USE_SQLITE else "%s"
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT id, user_id, provider, external_account_id, external_account_name,
                       access_token, status, enabled, metadata, created_at, updated_at
                FROM user_social_connections
                WHERE user_id = {p}
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            rows = cur.fetchall()
            cur.close()
            return [_social_connection_from_row(row) for row in rows]
    except Exception as e:
        logger_db.error(f"Erro ao listar conexoes sociais: {e}")
        return []


def atualizar_conexao_social(user_id, connection_id, enabled=None, status=None):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")

    p = "?" if USE_SQLITE else "%s"
    updates = []
    values = []
    if enabled is not None:
        updates.append(f"enabled = {p}")
        values.append(1 if USE_SQLITE and enabled else 0 if USE_SQLITE else enabled)
    if status is not None:
        updates.append(f"status = {p}")
        values.append(status)
    if not updates:
        return buscar_conexao_social_por_id(user_id, connection_id)

    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.extend([user_id, connection_id])
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            UPDATE user_social_connections
            SET {", ".join(updates)}
            WHERE user_id = {p} AND id = {p}
            """,
            tuple(values),
        )
        cur.close()
    return buscar_conexao_social_por_id(user_id, connection_id)


def desconectar_conexoes_sociais_por_provider(user_id, provider):
    if not DATABASE_ENABLED:
        return {"provider": provider, "updated": 0}
    try:
        p = "?" if USE_SQLITE else "%s"
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                UPDATE user_social_connections
                SET enabled = {p}, status = {p}, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = {p} AND provider = {p}
                """,
                (0 if USE_SQLITE else False, "disconnected", user_id, provider),
            )
            updated = cur.rowcount
            cur.close()
            return {"provider": provider, "updated": updated}
    except Exception as e:
        logger_db.error(f"Erro ao desconectar provider social: {e}")
        return {"provider": provider, "updated": 0}


def buscar_conexao_social_por_canal(provider, external_account_id):
    if not DATABASE_ENABLED:
        return None
    try:
        p = "?" if USE_SQLITE else "%s"
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT id, user_id, provider, external_account_id, external_account_name,
                       access_token, status, enabled, metadata, created_at, updated_at
                FROM user_social_connections
                WHERE provider = {p}
                  AND external_account_id = {p}
                  AND status IN ('connected', 'active')
                  AND enabled = {p}
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (provider, external_account_id, 1 if USE_SQLITE else True),
            )
            row = cur.fetchone()
            cur.close()
            return _social_connection_from_row(row)
    except Exception as e:
        logger_db.error(f"Erro ao localizar conexao social por canal: {e}")
        return None


def salvar_mensagem_omnichannel(connection, external_contact_id, content, direction="inbound", contact_name=None, external_message_id=None, raw_payload=None):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")

    p = "?" if USE_SQLITE else "%s"
    raw_json = json.dumps(raw_payload or {}, ensure_ascii=False)
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT id, conversation_id
            FROM omnichannel_conversations
            WHERE user_id = {p} AND provider = {p} AND external_account_id = {p} AND external_contact_id = {p}
            LIMIT 1
            """,
            (connection["user_id"], connection["provider"], connection["external_account_id"], external_contact_id),
        )
        existing = cur.fetchone()
        if existing:
            omni_conversation_id = existing[0]
            conversation_id = existing[1]
        else:
            title = contact_name or f"{connection['provider']}:{external_contact_id}"
            cur.execute(f"INSERT INTO conversations (user_id, title) VALUES ({p}, {p})", (connection["user_id"], title))
            if USE_SQLITE:
                conversation_id = cur.lastrowid
            else:
                cur.execute("SELECT LASTVAL()")
                conversation_id = cur.fetchone()[0]
            cur.execute(
                f"""
                INSERT INTO omnichannel_conversations
                    (user_id, connection_id, provider, external_account_id, external_contact_id, contact_name, conversation_id)
                VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p})
                """,
                (connection["user_id"], connection["id"], connection["provider"], connection["external_account_id"], external_contact_id, contact_name, conversation_id),
            )
            if USE_SQLITE:
                omni_conversation_id = cur.lastrowid
            else:
                cur.execute("SELECT LASTVAL()")
                omni_conversation_id = cur.fetchone()[0]

        role = "user" if direction == "inbound" else "assistant"
        cur.execute(f"INSERT INTO messages (conversation_id, role, content) VALUES ({p}, {p}, {p})", (conversation_id, role, content))
        if USE_SQLITE:
            message_id = cur.lastrowid
        else:
            cur.execute("SELECT LASTVAL()")
            message_id = cur.fetchone()[0]

        cur.execute(
            f"""
            INSERT INTO omnichannel_messages
                (user_id, connection_id, omnichannel_conversation_id, conversation_id, message_id,
                 provider, direction, external_message_id, external_contact_id, content, raw_payload)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
            """,
            (connection["user_id"], connection["id"], omni_conversation_id, conversation_id, message_id, connection["provider"], direction, external_message_id, external_contact_id, content, raw_json),
        )
        if USE_SQLITE:
            omni_message_id = cur.lastrowid
        else:
            cur.execute("SELECT LASTVAL()")
            omni_message_id = cur.fetchone()[0]

        cur.execute(f"UPDATE omnichannel_conversations SET last_message_at = CURRENT_TIMESTAMP WHERE id = {p}", (omni_conversation_id,))
        cur.close()
        return {"conversation_id": conversation_id, "message_id": message_id, "omnichannel_message_id": omni_message_id}


def _fetch_business_rows(table, user_id, *, limit=100, search=None, status=None):
    if not DATABASE_ENABLED:
        return []
    allowed_tables = {
        "business_pipelines",
        "business_contacts",
        "business_deals",
        "business_products",
        "business_calls",
        "business_groups",
        "business_meetings",
        "business_contracts",
        "business_tasks",
        "business_quick_messages",
        "business_logistics",
        "business_revenue_goals",
    }
    if table not in allowed_tables:
        raise ValueError("Tabela de negocio invalida")

    p = _placeholder()
    filters = [f"user_id = {p}"]
    values = [user_id]

    if status:
        filters.append(f"status = {p}")
        values.append(status)

    if search and table in {
        "business_contacts",
        "business_deals",
        "business_products",
        "business_pipelines",
        "business_groups",
        "business_meetings",
        "business_contracts",
        "business_tasks",
        "business_quick_messages",
        "business_logistics",
    }:
        like = f"%{search.strip()}%"
        op = "LIKE" if USE_SQLITE else "ILIKE"
        if table == "business_contacts":
            filters.append(f"(name {op} {p} OR COALESCE(email, '') {op} {p} OR COALESCE(phone, '') {op} {p})")
            values.extend([like, like, like])
        elif table == "business_deals":
            filters.append(f"title {op} {p}")
            values.append(like)
        elif table in {"business_quick_messages"}:
            filters.append(f"(title {op} {p} OR body {op} {p})")
            values.extend([like, like])
        elif table in {"business_meetings", "business_contracts", "business_tasks", "business_logistics"}:
            filters.append(f"title {op} {p}")
            values.append(like)
        else:
            filters.append(f"name {op} {p}")
            values.append(like)

    order_col = "last_interaction_at" if table == "business_contacts" else "created_at"
    query = f"""
        SELECT *
        FROM {table}
        WHERE {' AND '.join(filters)}
        ORDER BY {order_col} DESC, id DESC
        LIMIT {int(limit)}
    """
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, tuple(values))
        rows = cur.fetchall()
        result = [_row_to_dict(cur, row) for row in rows]
        cur.close()
    for item in result:
        if "stages" in item:
            item["stages"] = _json_or_dict(item.get("stages"))
    return result


def listar_business_pipelines(user_id):
    return _fetch_business_rows("business_pipelines", user_id, limit=100)


def listar_business_contacts(user_id, search=None, status=None, limit=100):
    return _fetch_business_rows("business_contacts", user_id, search=search, status=status, limit=limit)


def listar_business_deals(user_id, search=None, status=None, limit=100):
    return _fetch_business_rows("business_deals", user_id, search=search, status=status, limit=limit)


def listar_business_products(user_id, search=None, status=None, limit=100):
    return _fetch_business_rows("business_products", user_id, search=search, status=status, limit=limit)


def listar_business_calls(user_id, limit=100):
    return _fetch_business_rows("business_calls", user_id, limit=limit)


def listar_business_groups(user_id, search=None, status=None, limit=100):
    return _fetch_business_rows("business_groups", user_id, search=search, status=status, limit=limit)


def listar_business_meetings(user_id, search=None, status=None, limit=100):
    return _fetch_business_rows("business_meetings", user_id, search=search, status=status, limit=limit)


def listar_business_contracts(user_id, search=None, status=None, limit=100):
    return _fetch_business_rows("business_contracts", user_id, search=search, status=status, limit=limit)


def listar_business_tasks(user_id, search=None, status=None, limit=100):
    return _fetch_business_rows("business_tasks", user_id, search=search, status=status, limit=limit)


def listar_business_quick_messages(user_id, search=None, status=None, limit=100):
    return _fetch_business_rows("business_quick_messages", user_id, search=search, status=status, limit=limit)


def listar_business_logistics(user_id, search=None, status=None, limit=100):
    return _fetch_business_rows("business_logistics", user_id, search=search, status=status, limit=limit)


def listar_business_revenue_goals(user_id, limit=24):
    return _fetch_business_rows("business_revenue_goals", user_id, limit=limit)


def buscar_business_item(table, user_id, item_id):
    if not DATABASE_ENABLED:
        return None
    allowed_tables = {
        "business_pipelines",
        "business_contacts",
        "business_deals",
        "business_products",
        "business_calls",
        "business_groups",
        "business_meetings",
        "business_contracts",
        "business_tasks",
        "business_quick_messages",
        "business_logistics",
        "business_revenue_goals",
    }
    if table not in allowed_tables:
        raise ValueError("Tabela de negocio invalida")
    p = _placeholder()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table} WHERE user_id = {p} AND id = {p} LIMIT 1", (user_id, item_id))
        row = cur.fetchone()
        item = _row_to_dict(cur, row)
        cur.close()
    if item and "stages" in item:
        item["stages"] = _json_or_dict(item.get("stages"))
    return item


def criar_business_pipeline(user_id, name, description=None, stages=None, is_default=False):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")
    p = _placeholder()
    stages_payload = stages or ["novo", "qualificado", "proposta", "negociacao", "ganho"]
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            INSERT INTO business_pipelines (user_id, name, description, stages, is_default)
            VALUES ({p}, {p}, {p}, {p}, {p})
            """,
            (user_id, name, description, _json_db_value(stages_payload), 1 if USE_SQLITE and is_default else 0 if USE_SQLITE else is_default),
        )
        new_id = cur.lastrowid if USE_SQLITE else None
        if not USE_SQLITE:
            cur.execute("SELECT LASTVAL()")
            new_id = cur.fetchone()[0]
        cur.close()
    return buscar_business_item("business_pipelines", user_id, new_id)


def criar_business_contact(user_id, name, email=None, phone=None, company=None, status="prospect", source="manual"):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")
    p = _placeholder()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            INSERT INTO business_contacts (user_id, name, email, phone, company, status, source)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p})
            """,
            (user_id, name, email, phone, company, status, source),
        )
        new_id = cur.lastrowid if USE_SQLITE else None
        if not USE_SQLITE:
            cur.execute("SELECT LASTVAL()")
            new_id = cur.fetchone()[0]
        cur.close()
    return buscar_business_item("business_contacts", user_id, new_id)


def upsert_business_contact_from_channel(user_id, provider, external_contact_id, contact_name=None):
    if not DATABASE_ENABLED:
        return None
    p = _placeholder()
    phone = external_contact_id if provider in {"whatsapp", "messenger"} else None
    lookup_value = phone or external_contact_id
    name = (contact_name or lookup_value or f"Contato {provider}").strip()
    with get_db_connection() as conn:
        cur = conn.cursor()
        if phone:
            cur.execute(
                f"SELECT id FROM business_contacts WHERE user_id = {p} AND phone = {p} LIMIT 1",
                (user_id, phone),
            )
        else:
            cur.execute(
                f"SELECT id FROM business_contacts WHERE user_id = {p} AND name = {p} AND source = {p} LIMIT 1",
                (user_id, name, provider),
            )
        existing = cur.fetchone()
        if existing:
            contact_id = existing[0]
            cur.execute(
                f"""
                UPDATE business_contacts
                SET name = COALESCE({p}, name),
                    last_interaction_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = {p}
                """,
                (name, contact_id),
            )
        else:
            cur.execute(
                f"""
                INSERT INTO business_contacts (user_id, name, phone, status, source)
                VALUES ({p}, {p}, {p}, {p}, {p})
                """,
                (user_id, name, phone, "prospect", provider),
            )
            contact_id = cur.lastrowid if USE_SQLITE else None
            if not USE_SQLITE:
                cur.execute("SELECT LASTVAL()")
                contact_id = cur.fetchone()[0]
        cur.close()
    return buscar_business_item("business_contacts", user_id, contact_id)


def criar_business_deal(user_id, title, value_cents=0, pipeline_id=None, contact_id=None, stage="novo", status="open", probability=10, expected_close_date=None):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")
    p = _placeholder()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            INSERT INTO business_deals (
                user_id, pipeline_id, contact_id, title, value_cents, stage, status, probability, expected_close_date
            )
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
            """,
            (user_id, pipeline_id, contact_id, title, int(value_cents or 0), stage, status, int(probability or 10), expected_close_date),
        )
        new_id = cur.lastrowid if USE_SQLITE else None
        if not USE_SQLITE:
            cur.execute("SELECT LASTVAL()")
            new_id = cur.fetchone()[0]
        cur.close()
    return buscar_business_item("business_deals", user_id, new_id)


def criar_business_product(user_id, name, description=None, price_cents=0, status="active"):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")
    p = _placeholder()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            INSERT INTO business_products (user_id, name, description, price_cents, status)
            VALUES ({p}, {p}, {p}, {p}, {p})
            """,
            (user_id, name, description, int(price_cents or 0), status),
        )
        new_id = cur.lastrowid if USE_SQLITE else None
        if not USE_SQLITE:
            cur.execute("SELECT LASTVAL()")
            new_id = cur.fetchone()[0]
        cur.close()
    return buscar_business_item("business_products", user_id, new_id)


def criar_business_call(user_id, phone, contact_id=None, direction="outbound", outcome="pending", duration_seconds=0, notes=None):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")
    p = _placeholder()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            INSERT INTO business_calls (user_id, contact_id, phone, direction, outcome, duration_seconds, notes)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p})
            """,
            (user_id, contact_id, phone, direction, outcome, int(duration_seconds or 0), notes),
        )
        new_id = cur.lastrowid if USE_SQLITE else None
        if not USE_SQLITE:
            cur.execute("SELECT LASTVAL()")
            new_id = cur.fetchone()[0]
        cur.close()
    return buscar_business_item("business_calls", user_id, new_id)


def criar_business_group(user_id, name, description=None, status="active"):
    return _create_simple_business_item(
        "business_groups",
        user_id,
        {"name": name, "description": description, "status": status},
    )


def criar_business_meeting(user_id, title, contact_id=None, scheduled_at=None, status="scheduled", notes=None):
    return _create_simple_business_item(
        "business_meetings",
        user_id,
        {"contact_id": contact_id, "title": title, "scheduled_at": scheduled_at, "status": status, "notes": notes},
    )


def criar_business_contract(user_id, title, contact_id=None, deal_id=None, value_cents=0, status="draft", signed_at=None):
    return _create_simple_business_item(
        "business_contracts",
        user_id,
        {"contact_id": contact_id, "deal_id": deal_id, "title": title, "value_cents": int(value_cents or 0), "status": status, "signed_at": signed_at},
    )


def criar_business_task(user_id, title, contact_id=None, due_at=None, status="open", priority="medium"):
    return _create_simple_business_item(
        "business_tasks",
        user_id,
        {"contact_id": contact_id, "title": title, "due_at": due_at, "status": status, "priority": priority},
    )


def criar_business_quick_message(user_id, title, body, category="atendimento", status="active"):
    return _create_simple_business_item(
        "business_quick_messages",
        user_id,
        {"title": title, "body": body, "category": category, "status": status},
    )


def criar_business_logistic(user_id, title, contact_id=None, status="pending", tracking_code=None, notes=None):
    return _create_simple_business_item(
        "business_logistics",
        user_id,
        {"contact_id": contact_id, "title": title, "status": status, "tracking_code": tracking_code, "notes": notes},
    )


def salvar_business_revenue_goal(user_id, year, month, target_cents):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")
    p = _placeholder()
    with get_db_connection() as conn:
        cur = conn.cursor()
        if USE_POSTGRES:
            cur.execute(
                f"""
                INSERT INTO business_revenue_goals (user_id, year, month, target_cents)
                VALUES ({p}, {p}, {p}, {p})
                ON CONFLICT DO NOTHING
                """,
                (user_id, int(year), int(month), int(target_cents or 0)),
            )
            cur.execute(
                f"""
                UPDATE business_revenue_goals
                SET target_cents = {p}, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = {p} AND year = {p} AND month = {p}
                """,
                (int(target_cents or 0), user_id, int(year), int(month)),
            )
        else:
            cur.execute(
                f"SELECT id FROM business_revenue_goals WHERE user_id = {p} AND year = {p} AND month = {p} LIMIT 1",
                (user_id, int(year), int(month)),
            )
            existing = cur.fetchone()
            if existing:
                cur.execute(
                    f"UPDATE business_revenue_goals SET target_cents = {p}, updated_at = CURRENT_TIMESTAMP WHERE id = {p}",
                    (int(target_cents or 0), existing[0]),
                )
                item_id = existing[0]
            else:
                cur.execute(
                    f"INSERT INTO business_revenue_goals (user_id, year, month, target_cents) VALUES ({p}, {p}, {p}, {p})",
                    (user_id, int(year), int(month), int(target_cents or 0)),
                )
                item_id = cur.lastrowid
        if USE_POSTGRES:
            cur.execute(
                f"SELECT id FROM business_revenue_goals WHERE user_id = {p} AND year = {p} AND month = {p} LIMIT 1",
                (user_id, int(year), int(month)),
            )
            item_id = cur.fetchone()[0]
        cur.close()
    return buscar_business_item("business_revenue_goals", user_id, item_id)


def _create_simple_business_item(table, user_id, values):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")
    allowed_tables = {
        "business_groups",
        "business_meetings",
        "business_contracts",
        "business_tasks",
        "business_quick_messages",
        "business_logistics",
    }
    if table not in allowed_tables:
        raise ValueError("Tabela de negocio invalida")
    p = _placeholder()
    columns = ["user_id", *values.keys()]
    placeholders = ", ".join([p] * len(columns))
    params = [user_id, *values.values()]
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
            tuple(params),
        )
        new_id = cur.lastrowid if USE_SQLITE else None
        if not USE_SQLITE:
            cur.execute("SELECT LASTVAL()")
            new_id = cur.fetchone()[0]
        cur.close()
    return buscar_business_item(table, user_id, new_id)


def atualizar_business_status(table, user_id, item_id, status):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")
    allowed_tables = {
        "business_contacts",
        "business_deals",
        "business_products",
        "business_groups",
        "business_meetings",
        "business_contracts",
        "business_tasks",
        "business_quick_messages",
        "business_logistics",
    }
    if table not in allowed_tables:
        raise ValueError("Tabela de negocio invalida")
    p = _placeholder()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE {table} SET status = {p}, updated_at = CURRENT_TIMESTAMP WHERE user_id = {p} AND id = {p}",
            (status, user_id, item_id),
        )
        cur.close()
    return buscar_business_item(table, user_id, item_id)


def business_summary(user_id):
    if not DATABASE_ENABLED:
        return {
            "contacts": 0,
            "deals": 0,
            "open_deals": 0,
            "pipeline_value_cents": 0,
            "won_value_cents": 0,
            "products": 0,
            "calls_today": 0,
        }
    p = _placeholder()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM business_contacts WHERE user_id = {p}", (user_id,))
        contacts = int(cur.fetchone()[0] or 0)
        cur.execute(f"SELECT COUNT(*) FROM business_deals WHERE user_id = {p}", (user_id,))
        deals = int(cur.fetchone()[0] or 0)
        cur.execute(f"SELECT COUNT(*), COALESCE(SUM(value_cents), 0) FROM business_deals WHERE user_id = {p} AND status = {p}", (user_id, "open"))
        row = cur.fetchone()
        open_deals = int(row[0] or 0)
        pipeline_value = int(row[1] or 0)
        cur.execute(f"SELECT COALESCE(SUM(value_cents), 0) FROM business_deals WHERE user_id = {p} AND status = {p}", (user_id, "won"))
        won_value = int(cur.fetchone()[0] or 0)
        cur.execute(f"SELECT COUNT(*) FROM business_products WHERE user_id = {p} AND status = {p}", (user_id, "active"))
        products = int(cur.fetchone()[0] or 0)
        if USE_SQLITE:
            cur.execute(f"SELECT COUNT(*) FROM business_calls WHERE user_id = {p} AND date(created_at) = date('now')", (user_id,))
        else:
            cur.execute(f"SELECT COUNT(*) FROM business_calls WHERE user_id = {p} AND DATE(created_at) = CURRENT_DATE", (user_id,))
        calls_today = int(cur.fetchone()[0] or 0)
        cur.close()
    return {
        "contacts": contacts,
        "deals": deals,
        "open_deals": open_deals,
        "pipeline_value_cents": pipeline_value,
        "won_value_cents": won_value,
        "products": products,
        "calls_today": calls_today,
    }


def listar_marketing_projects(user_id, limit=100):
    if not DATABASE_ENABLED:
        return []
    p = _placeholder()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT *
            FROM marketing_projects
            WHERE user_id = {p}
            ORDER BY created_at DESC, id DESC
            LIMIT {int(limit)}
            """,
            (user_id,),
        )
        rows = cur.fetchall()
        result = [_row_to_dict(cur, row) for row in rows]
        cur.close()
    return result


def buscar_marketing_project(user_id, project_id):
    if not DATABASE_ENABLED:
        return None
    p = _placeholder()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"SELECT * FROM marketing_projects WHERE user_id = {p} AND id = {p} LIMIT 1",
            (user_id, project_id),
        )
        row = cur.fetchone()
        item = _row_to_dict(cur, row)
        cur.close()
    return item


def criar_marketing_project(user_id, name, audience, objective, offer, tone="premium", notes=None):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")
    p = _placeholder()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            INSERT INTO marketing_projects (user_id, name, audience, objective, offer, tone, notes)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p})
            """,
            (user_id, name, audience, objective, offer, tone or "premium", notes),
        )
        new_id = cur.lastrowid if USE_SQLITE else None
        if not USE_SQLITE:
            cur.execute("SELECT LASTVAL()")
            new_id = cur.fetchone()[0]
        cur.close()
    return buscar_marketing_project(user_id, new_id)


def atualizar_marketing_project(user_id, project_id, **fields):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")
    allowed = {"name", "audience", "objective", "offer", "tone", "notes"}
    updates = []
    values = []
    p = _placeholder()
    for key, value in fields.items():
        if key in allowed and value is not None:
            updates.append(f"{key} = {p}")
            values.append(value)
    if not updates:
        return buscar_marketing_project(user_id, project_id)
    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.extend([user_id, project_id])
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE marketing_projects SET {', '.join(updates)} WHERE user_id = {p} AND id = {p}",
            tuple(values),
        )
        cur.close()
    return buscar_marketing_project(user_id, project_id)


def deletar_marketing_project(user_id, project_id):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")
    p = _placeholder()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM marketing_projects WHERE user_id = {p} AND id = {p}", (user_id, project_id))
        deleted = cur.rowcount
        cur.close()
    return deleted > 0


def listar_studio_templates(category=None, template_type=None, include_premium=True, limit=100):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")
    p = _placeholder()
    filters = ["is_active = " + p]
    values = [1 if USE_SQLITE else True]
    if category:
        filters.append(f"category = {p}")
        values.append(category)
    if template_type:
        filters.append(f"type = {p}")
        values.append(template_type)
    if not include_premium:
        filters.append("premium = " + p)
        values.append(0 if USE_SQLITE else False)
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT id, name, category, type, thumbnail_url, preview_video_url, template_json, premium
            FROM templates
            WHERE {' AND '.join(filters)}
            ORDER BY premium ASC, category ASC, name ASC
            LIMIT {int(limit)}
            """,
            tuple(values),
        )
        rows = cur.fetchall()
        result = []
        for row in rows:
            item = _row_to_dict(cur, row)
            if isinstance(item.get("template_json"), str):
                item["template_json"] = json.loads(item["template_json"])
            item["premium"] = bool(item.get("premium"))
            result.append(item)
        cur.close()
    return result


def buscar_studio_template(template_id):
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco nao configurado")
    p = _placeholder()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT id, name, category, type, thumbnail_url, preview_video_url, template_json, premium
            FROM templates
            WHERE id = {p} AND is_active = {p}
            LIMIT 1
            """,
            (template_id, 1 if USE_SQLITE else True),
        )
        row = cur.fetchone()
        item = _row_to_dict(cur, row)
        if item and isinstance(item.get("template_json"), str):
            item["template_json"] = json.loads(item["template_json"])
        if item:
            item["premium"] = bool(item.get("premium"))
        cur.close()
    return item


def marketing_performance_summary(user_id):
    """Return marketing KPIs from real internal records and connected accounts only."""
    connections = listar_conexoes_sociais(user_id)
    connected_sources = [
        {
            "provider": item.get("provider"),
            "name": item.get("external_account_name") or item.get("external_account_id"),
            "enabled": bool(item.get("enabled")),
            "status": item.get("status"),
        }
        for item in connections
        if item.get("status") == "connected" and item.get("enabled")
    ]
    summary = business_summary(user_id)
    deals = listar_business_deals(user_id, limit=500)
    won_deals = [deal for deal in deals if str(deal.get("status", "")).lower() == "won"]
    open_deals = [deal for deal in deals if str(deal.get("status", "")).lower() == "open"]
    omnichannel_contacts = listar_business_contacts(user_id, limit=500)
    channel_counts = {}
    for contact in omnichannel_contacts:
        source = contact.get("source") or "manual"
        channel_counts[source] = channel_counts.get(source, 0) + 1

    ads_connected = any(source["provider"] in {"google_ads", "meta_ads"} for source in connected_sources)
    return {
        "views": 0,
        "clicks": 0,
        "reservations": len(won_deals),
        "open_opportunities": len(open_deals),
        "pipeline_value_cents": summary.get("pipeline_value_cents", 0),
        "won_value_cents": summary.get("won_value_cents", 0),
        "leads": summary.get("contacts", 0),
        "connected_sources": connected_sources,
        "channel_counts": channel_counts,
        "ads_connected": ads_connected,
        "message": None if ads_connected else "Conecte Google Ads ou Meta Ads para importar visualizacoes, cliques e custo real.",
    }
