"""add credit system"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "0001_add_credit_system"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def upgrade() -> None:
    if _is_postgres():
        op.execute(
            """
            CREATE TABLE IF NOT EXISTS credit_balances (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                balance INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        op.execute(
            """
            CREATE TABLE IF NOT EXISTS credit_transactions (
                id BIGSERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                amount INTEGER NOT NULL CHECK (amount <> 0),
                type VARCHAR(32) NOT NULL,
                reason TEXT NOT NULL,
                provider TEXT,
                model TEXT,
                job_id TEXT,
                metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                CONSTRAINT credit_transactions_type_check
                    CHECK (type IN ('grant', 'spend', 'refund', 'adjustment', 'reservation', 'release'))
            )
            """
        )
        op.execute(
            """
            CREATE TABLE IF NOT EXISTS generation_jobs (
                id VARCHAR(64) PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                status VARCHAR(32) NOT NULL DEFAULT 'queued',
                job_type VARCHAR(32) NOT NULL,
                provider TEXT,
                model TEXT,
                prompt TEXT NOT NULL,
                result_url TEXT,
                cost INTEGER NOT NULL DEFAULT 0 CHECK (cost >= 0),
                progress INTEGER NOT NULL DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
                error_message TEXT,
                metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                completed_at TIMESTAMPTZ,
                CONSTRAINT generation_jobs_status_check
                    CHECK (status IN ('queued', 'processing', 'completed', 'failed', 'cancelled', 'dead_letter'))
            )
            """
        )
        op.execute(
            """
            CREATE TABLE IF NOT EXISTS credit_pricing (
                id BIGSERIAL PRIMARY KEY,
                job_type VARCHAR(32) NOT NULL DEFAULT 'chat',
                provider TEXT,
                model TEXT NOT NULL,
                resolution TEXT,
                duration_seconds INTEGER,
                cost_credits INTEGER NOT NULL CHECK (cost_credits >= 0),
                active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        op.execute("CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_created ON credit_transactions (user_id, created_at DESC)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_credit_transactions_job_id ON credit_transactions (job_id)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_generation_jobs_user_created ON generation_jobs (user_id, created_at DESC)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_generation_jobs_status_created ON generation_jobs (status, created_at)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_credit_pricing_lookup ON credit_pricing (job_type, provider, model, resolution, duration_seconds, active)")
        op.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_credit_pricing_active_lookup
            ON credit_pricing (
                job_type,
                COALESCE(provider, ''),
                model,
                COALESCE(resolution, ''),
                COALESCE(duration_seconds, -1)
            )
            WHERE active = TRUE
            """
        )
        op.execute(
            """
            INSERT INTO credit_pricing (job_type, provider, model, resolution, duration_seconds, cost_credits)
            VALUES
                ('chat', 'groq', 'llama-3.1-8b-instant', NULL, NULL, 1),
                ('chat', 'gemini', 'gemini-1.5-flash', NULL, NULL, 1),
                ('chat', 'ollama', 'llama3', NULL, NULL, 0),
                ('chat', 'openai', 'gpt-4o-mini', NULL, NULL, 2),
                ('code', 'groq', 'qwen/qwen3-coder', NULL, NULL, 2),
                ('image', NULL, 'default-image', '1024x1024', NULL, 10),
                ('image', 'black-forest-labs', 'flux-schnell', '1024x1024', NULL, 8),
                ('image', 'black-forest-labs', 'flux-dev', '1024x1024', NULL, 15),
                ('image', 'stability', 'stable-image-core', '1024x1024', NULL, 12),
                ('image', 'openai', 'gpt-image-1', '1024x1024', NULL, 25),
                ('audio', NULL, 'default-audio', NULL, NULL, 5),
                ('video', NULL, 'default-video', '720p', 5, 100),
                ('video', 'kling', 'kling-v1.6-standard', '720p', 5, 120),
                ('video', 'kling', 'kling-v1.6-pro', '1080p', 5, 220),
                ('video', 'runway', 'gen-3-alpha-turbo', '720p', 5, 180),
                ('video', 'runway', 'gen-3-alpha', '1080p', 10, 450),
                ('video', 'luma', 'ray2', '720p', 5, 160),
                ('video', 'pika', 'pika-2.2', '720p', 5, 120)
            ON CONFLICT DO NOTHING
            """
        )
    else:
        op.execute("PRAGMA foreign_keys=ON")
        op.execute(
            """
            CREATE TABLE IF NOT EXISTS credit_balances (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0),
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        op.execute(
            """
            CREATE TABLE IF NOT EXISTS credit_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL CHECK (amount <> 0),
                type TEXT NOT NULL CHECK (type IN ('grant', 'spend', 'refund', 'adjustment', 'reservation', 'release')),
                reason TEXT NOT NULL,
                provider TEXT,
                model TEXT,
                job_id TEXT,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        op.execute(
            """
            CREATE TABLE IF NOT EXISTS generation_jobs (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'queued'
                    CHECK (status IN ('queued', 'processing', 'completed', 'failed', 'cancelled', 'dead_letter')),
                job_type TEXT NOT NULL,
                provider TEXT,
                model TEXT,
                prompt TEXT NOT NULL,
                result_url TEXT,
                cost INTEGER NOT NULL DEFAULT 0 CHECK (cost >= 0),
                progress INTEGER NOT NULL DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
                error_message TEXT,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        op.execute(
            """
            CREATE TABLE IF NOT EXISTS credit_pricing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_type TEXT NOT NULL DEFAULT 'chat',
                provider TEXT,
                model TEXT NOT NULL,
                resolution TEXT,
                duration_seconds INTEGER,
                cost_credits INTEGER NOT NULL CHECK (cost_credits >= 0),
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        op.execute("CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_created ON credit_transactions (user_id, created_at DESC)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_credit_transactions_job_id ON credit_transactions (job_id)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_generation_jobs_user_created ON generation_jobs (user_id, created_at DESC)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_generation_jobs_status_created ON generation_jobs (status, created_at)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_credit_pricing_lookup ON credit_pricing (job_type, provider, model, resolution, duration_seconds, active)")
        op.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_credit_pricing_active_lookup
            ON credit_pricing (
                job_type,
                COALESCE(provider, ''),
                model,
                COALESCE(resolution, ''),
                COALESCE(duration_seconds, -1)
            )
            WHERE active = 1
            """
        )
        op.execute(
            """
            INSERT OR IGNORE INTO credit_pricing (job_type, provider, model, resolution, duration_seconds, cost_credits)
            VALUES
                ('chat', 'groq', 'llama-3.1-8b-instant', NULL, NULL, 1),
                ('chat', 'gemini', 'gemini-1.5-flash', NULL, NULL, 1),
                ('chat', 'ollama', 'llama3', NULL, NULL, 0),
                ('chat', 'openai', 'gpt-4o-mini', NULL, NULL, 2),
                ('code', 'groq', 'qwen/qwen3-coder', NULL, NULL, 2),
                ('image', NULL, 'default-image', '1024x1024', NULL, 10),
                ('image', 'black-forest-labs', 'flux-schnell', '1024x1024', NULL, 8),
                ('image', 'black-forest-labs', 'flux-dev', '1024x1024', NULL, 15),
                ('image', 'stability', 'stable-image-core', '1024x1024', NULL, 12),
                ('image', 'openai', 'gpt-image-1', '1024x1024', NULL, 25),
                ('audio', NULL, 'default-audio', NULL, NULL, 5),
                ('video', NULL, 'default-video', '720p', 5, 100),
                ('video', 'kling', 'kling-v1.6-standard', '720p', 5, 120),
                ('video', 'kling', 'kling-v1.6-pro', '1080p', 5, 220),
                ('video', 'runway', 'gen-3-alpha-turbo', '720p', 5, 180),
                ('video', 'runway', 'gen-3-alpha', '1080p', 10, 450),
                ('video', 'luma', 'ray2', '720p', 5, 160),
                ('video', 'pika', 'pika-2.2', '720p', 5, 120)
            """
        )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_credit_pricing_active_lookup")
    op.execute("DROP INDEX IF EXISTS idx_credit_pricing_lookup")
    op.execute("DROP INDEX IF EXISTS idx_generation_jobs_status_created")
    op.execute("DROP INDEX IF EXISTS idx_generation_jobs_user_created")
    op.execute("DROP INDEX IF EXISTS idx_credit_transactions_job_id")
    op.execute("DROP INDEX IF EXISTS idx_credit_transactions_user_created")
    op.execute("DROP TABLE IF EXISTS credit_pricing")
    op.execute("DROP TABLE IF EXISTS generation_jobs")
    op.execute("DROP TABLE IF EXISTS credit_transactions")
    op.execute("DROP TABLE IF EXISTS credit_balances")
