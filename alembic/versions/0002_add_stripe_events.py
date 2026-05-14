"""add stripe events"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "0002_add_stripe_events"
down_revision: Union[str, None] = "0001_add_credit_system"
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
        op.execute(
            """
            CREATE TABLE IF NOT EXISTS stripe_events (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'processing'
                    CHECK (status IN ('processing', 'processed', 'failed', 'ignored')),
                attempts INTEGER NOT NULL DEFAULT 1,
                payload JSONB NOT NULL DEFAULT '{}'::jsonb,
                error_message TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                processed_at TIMESTAMPTZ
            )
            """
        )
        op.execute("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT")
        op.execute("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS stripe_subscription_id TEXT")
        op.execute("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS stripe_price_id TEXT")
        op.execute("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS current_period_end TIMESTAMPTZ")
        op.execute("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW()")
        op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_subscriptions_stripe_subscription_id ON subscriptions (stripe_subscription_id) WHERE stripe_subscription_id IS NOT NULL")
        op.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions (user_id)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_customer_id ON subscriptions (stripe_customer_id)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_stripe_events_status_created ON stripe_events (status, created_at)")
    else:
        op.execute("PRAGMA foreign_keys=ON")
        op.execute(
            """
            CREATE TABLE IF NOT EXISTS stripe_events (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'processing'
                    CHECK (status IN ('processing', 'processed', 'failed', 'ignored')),
                attempts INTEGER NOT NULL DEFAULT 1,
                payload TEXT NOT NULL DEFAULT '{}',
                error_message TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                processed_at TEXT
            )
            """
        )
        _sqlite_add_column_if_missing("subscriptions", "stripe_customer_id", "stripe_customer_id TEXT")
        _sqlite_add_column_if_missing("subscriptions", "stripe_subscription_id", "stripe_subscription_id TEXT")
        _sqlite_add_column_if_missing("subscriptions", "stripe_price_id", "stripe_price_id TEXT")
        _sqlite_add_column_if_missing("subscriptions", "current_period_end", "current_period_end TEXT")
        _sqlite_add_column_if_missing("subscriptions", "updated_at", "updated_at TEXT DEFAULT CURRENT_TIMESTAMP")
        op.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_subscriptions_stripe_subscription_id ON subscriptions (stripe_subscription_id)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions (user_id)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_customer_id ON subscriptions (stripe_customer_id)")
        op.execute("CREATE INDEX IF NOT EXISTS idx_stripe_events_status_created ON stripe_events (status, created_at)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_stripe_events_status_created")
    op.execute("DROP INDEX IF EXISTS idx_subscriptions_stripe_customer_id")
    op.execute("DROP INDEX IF EXISTS idx_subscriptions_user_id")
    op.execute("DROP INDEX IF EXISTS uq_subscriptions_stripe_subscription_id")
    op.execute("DROP TABLE IF EXISTS stripe_events")
