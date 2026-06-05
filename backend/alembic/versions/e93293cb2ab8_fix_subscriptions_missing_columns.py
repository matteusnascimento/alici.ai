"""fix_subscriptions_missing_columns

Revision ID: e93293cb2ab8
Revises: e51abfb3c70f
Create Date: 2026-04-07 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e93293cb2ab8'
down_revision: Union[str, None] = 'e51abfb3c70f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return column_name in {col["name"] for col in inspector.get_columns(table_name)}


def _add_timestamp_column(table_name: str, column_name: str) -> None:
    if _column_exists(table_name, column_name):
        return

    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "sqlite":
        op.add_column(
            table_name,
            sa.Column(
                column_name,
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )
    else:
        op.add_column(
            table_name,
            sa.Column(
                column_name,
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
        )


def upgrade() -> None:
    """Upgrade schema - add missing columns to subscriptions table."""
    _add_timestamp_column("subscriptions", "created_at")
    _add_timestamp_column("subscriptions", "updated_at")


def downgrade() -> None:
    """Downgrade schema."""
    if _column_exists("subscriptions", "updated_at"):
        op.drop_column("subscriptions", "updated_at")
    if _column_exists("subscriptions", "created_at"):
        op.drop_column("subscriptions", "created_at")
