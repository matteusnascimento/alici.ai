"""fix_subscriptions_missing_columns

Revision ID: e93293cb2ab8
Revises: e51abfb3c70f
Create Date: 2026-04-07 21:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "e93293cb2ab8"
down_revision: Union[str, None] = "e51abfb3c70f"
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


def upgrade() -> None:
    if not _table_exists("subscriptions"):
        return

    if not _column_exists("subscriptions", "created_at"):
        op.add_column(
            "subscriptions",
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )

    if not _column_exists("subscriptions", "updated_at"):
        op.add_column(
            "subscriptions",
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )


def downgrade() -> None:
    if _column_exists("subscriptions", "updated_at"):
        op.drop_column("subscriptions", "updated_at")

    if _column_exists("subscriptions", "created_at"):
        op.drop_column("subscriptions", "created_at")