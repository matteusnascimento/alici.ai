"""add_channel_status_and_agent_preferred_model

Revision ID: a1b2c3d4e5f6
Revises: e93293cb2ab8
Create Date: 2026-04-08 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "e93293cb2ab8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    inspector = inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    inspector = inspect(op.get_bind())

    if table_name not in inspector.get_table_names():
        return False

    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if not _table_exists(table_name):
        return

    if not _column_exists(table_name, column.name):
        op.add_column(table_name, column)


def _drop_column_if_exists(table_name: str, column_name: str) -> None:
    if not _table_exists(table_name):
        return

    if _column_exists(table_name, column_name):
        op.drop_column(table_name, column_name)


def upgrade() -> None:
    _add_column_if_missing(
        "agent_channels",
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default="disconnected",
        ),
    )

    _add_column_if_missing(
        "agent_channels",
        sa.Column("access_token", sa.Text(), nullable=True),
    )

    _add_column_if_missing(
        "agent_channels",
        sa.Column("refresh_token", sa.Text(), nullable=True),
    )

    _add_column_if_missing(
        "agent_channels",
        sa.Column("webhook_url", sa.String(length=512), nullable=True),
    )

    _add_column_if_missing(
        "agent_channels",
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
    )

    _add_column_if_missing(
        "agent_channels",
        sa.Column("last_error", sa.Text(), nullable=True),
    )

    _add_column_if_missing(
        "agents",
        sa.Column("preferred_model", sa.String(length=80), nullable=True),
    )


def downgrade() -> None:
    _drop_column_if_exists("agent_channels", "last_error")
    _drop_column_if_exists("agent_channels", "last_sync_at")
    _drop_column_if_exists("agent_channels", "webhook_url")
    _drop_column_if_exists("agent_channels", "refresh_token")
    _drop_column_if_exists("agent_channels", "access_token")
    _drop_column_if_exists("agent_channels", "status")
    _drop_column_if_exists("agents", "preferred_model")