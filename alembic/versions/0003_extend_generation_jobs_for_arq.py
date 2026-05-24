"""extend generation jobs for arq"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "0003_extend_generation_jobs_for_arq"
down_revision: Union[str, None] = "0002_add_stripe_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def _sqlite_columns(table_name: str) -> set[str]:
    rows = op.get_bind().exec_driver_sql(f"PRAGMA table_info({table_name})").fetchall()
    return {row[1] for row in rows}


def _sqlite_add_column_if_missing(table_name: str, column_name: str, ddl: str) -> None:
    if column_name not in _sqlite_columns(table_name):
        op.execute(f"ALTER TABLE {table_name} ADD COLUMN {ddl}")


def upgrade() -> None:
    if _is_postgres():
        op.execute("ALTER TABLE generation_jobs ADD COLUMN IF NOT EXISTS queue_name TEXT")
        op.execute("ALTER TABLE generation_jobs ADD COLUMN IF NOT EXISTS priority INTEGER NOT NULL DEFAULT 50")
        op.execute("ALTER TABLE generation_jobs ADD COLUMN IF NOT EXISTS arq_job_id TEXT")
        op.execute("ALTER TABLE generation_jobs ADD COLUMN IF NOT EXISTS input_path TEXT")
        op.execute("ALTER TABLE generation_jobs ADD COLUMN IF NOT EXISTS result_payload JSONB NOT NULL DEFAULT '{}'::jsonb")
        op.execute("ALTER TABLE generation_jobs ADD COLUMN IF NOT EXISTS attempts INTEGER NOT NULL DEFAULT 0")
        op.execute("ALTER TABLE generation_jobs ADD COLUMN IF NOT EXISTS max_retries INTEGER NOT NULL DEFAULT 3")
        op.execute("ALTER TABLE generation_jobs ADD COLUMN IF NOT EXISTS started_at TIMESTAMPTZ")
        op.execute("ALTER TABLE generation_jobs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")
        op.execute("ALTER TABLE generation_jobs ADD COLUMN IF NOT EXISTS refunded_at TIMESTAMPTZ")
        op.execute("CREATE INDEX IF NOT EXISTS idx_generation_jobs_arq_job_id ON generation_jobs (arq_job_id)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_generation_jobs_user_status_created ON generation_jobs (user_id, status, created_at DESC)")
        op.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_credit_refund_job_reason
            ON credit_transactions (job_id, reason, type)
            WHERE job_id IS NOT NULL
              AND type = 'grant'
              AND reason = 'generation_failed_refund'
            """
        )
    else:
        op.execute("PRAGMA foreign_keys=ON")
        _sqlite_add_column_if_missing("generation_jobs", "queue_name", "queue_name TEXT")
        _sqlite_add_column_if_missing("generation_jobs", "priority", "priority INTEGER NOT NULL DEFAULT 50")
        _sqlite_add_column_if_missing("generation_jobs", "arq_job_id", "arq_job_id TEXT")
        _sqlite_add_column_if_missing("generation_jobs", "input_path", "input_path TEXT")
        _sqlite_add_column_if_missing("generation_jobs", "result_payload", "result_payload TEXT NOT NULL DEFAULT '{}'")
        _sqlite_add_column_if_missing("generation_jobs", "attempts", "attempts INTEGER NOT NULL DEFAULT 0")
        _sqlite_add_column_if_missing("generation_jobs", "max_retries", "max_retries INTEGER NOT NULL DEFAULT 3")
        _sqlite_add_column_if_missing("generation_jobs", "started_at", "started_at TEXT")
        _sqlite_add_column_if_missing("generation_jobs", "updated_at", "updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP")
        _sqlite_add_column_if_missing("generation_jobs", "refunded_at", "refunded_at TEXT")
        op.execute("CREATE INDEX IF NOT EXISTS idx_generation_jobs_arq_job_id ON generation_jobs (arq_job_id)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_generation_jobs_user_status_created ON generation_jobs (user_id, status, created_at DESC)")
        op.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS uq_credit_refund_job_reason
            ON credit_transactions (job_id, reason, type)
            WHERE job_id IS NOT NULL
              AND type = 'grant'
              AND reason = 'generation_failed_refund'
            """
        )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_credit_refund_job_reason")
    op.execute("DROP INDEX IF EXISTS idx_generation_jobs_user_status_created")
    op.execute("DROP INDEX IF EXISTS idx_generation_jobs_arq_job_id")
