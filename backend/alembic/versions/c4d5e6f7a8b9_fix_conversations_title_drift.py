"""fix conversations title drift

Revision ID: c4d5e6f7a8b9
Revises: 83fa077000f9
Create Date: 2026-04-12 21:22:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, Sequence[str], None] = "83fa077000f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    if not _table_exists("conversations"):
        return

    if "title" in _columns("conversations"):
        return

    op.add_column("conversations", sa.Column("title", sa.String(length=140), nullable=True))
    op.execute(sa.text("UPDATE conversations SET title = 'Nova conversa' WHERE title IS NULL"))

    if op.get_bind().dialect.name == "sqlite":
        return

    op.alter_column("conversations", "title", existing_type=sa.String(length=140), nullable=False)


def downgrade() -> None:
    if not _table_exists("conversations"):
        return

    if "title" in _columns("conversations"):
        op.drop_column("conversations", "title")
