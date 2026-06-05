"""add_channel_status_and_agent_preferred_model

Revision ID: a1b2c3d4e5f6
Revises: e93293cb2ab8
Create Date: 2026-04-08 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "e93293cb2ab8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return column_name in {col["name"] for col in inspector.get_columns(table_name)}


def _add_column(table_name: str, column: sa.Column) -> None:
    if _column_exists(table_name, column.name):
        return
    op.add_column(table_name, column)


def upgrade() -> None:
    # --- agent_channels ---
    _add_column(
        "agent_channels",
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text("'disconnected'"),
        ),
    )
    _add_column("agent_channels", sa.Column("access_token", sa.Text(), nullable=True))
    _add_column("agent_channels", sa.Column("refresh_token", sa.Text(), nullable=True))
    _add_column("agent_channels", sa.Column("webhook_url", sa.String(length=512), nullable=True))

    bind = op.get_bind()
    timestamp_type = sa.DateTime(timezone=True) if bind.dialect.name != "sqlite" else sa.DateTime()
    default_now = sa.text("now()") if bind.dialect.name != "sqlite" else sa.text("CURRENT_TIMESTAMP")
    _add_column(
        "agent_channels",
        sa.Column(
            "last_sync_at",
            timestamp_type,
            nullable=True,
            server_default=default_now,
        ),
    )
    _add_column("agent_channels", sa.Column("last_error", sa.Text(), nullable=True))

    # --- agents ---
    _add_column("agents", sa.Column("preferred_model", sa.String(length=80), nullable=True))


def downgrade() -> None:
    if _column_exists("agent_channels", "last_error"):
        op.drop_column("agent_channels", "last_error")
    if _column_exists("agent_channels", "last_sync_at"):
        op.drop_column("agent_channels", "last_sync_at")
    if _column_exists("agent_channels", "webhook_url"):
        op.drop_column("agent_channels", "webhook_url")
    if _column_exists("agent_channels", "refresh_token"):
        op.drop_column("agent_channels", "refresh_token")
    if _column_exists("agent_channels", "access_token"):
        op.drop_column("agent_channels", "access_token")
    if _column_exists("agent_channels", "status"):
        op.drop_column("agent_channels", "status")
    if _column_exists("agents", "preferred_model"):
        op.drop_column("agents", "preferred_model")
