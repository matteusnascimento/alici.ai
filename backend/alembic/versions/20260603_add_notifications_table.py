"""add_notifications_table

Revision ID: 20260603notif
Revises: a9b8c7d6e5f4, f0e1d2c3b4a5
Create Date: 2026-06-03 19:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260603notif"
down_revision: Union[str, tuple[str, str], None] = ("a9b8c7d6e5f4", "f0e1d2c3b4a5")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    if _table_exists("notifications"):
        return

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=60), nullable=False),
        sa.Column("titulo", sa.String(length=140), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("destino", sa.String(length=255), nullable=False),
        sa.Column("lida", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("horario", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)
    op.create_index(op.f("ix_notifications_tipo"), "notifications", ["tipo"], unique=False)
    op.create_index(op.f("ix_notifications_lida"), "notifications", ["lida"], unique=False)
    op.create_index(op.f("ix_notifications_horario"), "notifications", ["horario"], unique=False)


def downgrade() -> None:
    if _table_exists("notifications"):
        op.drop_index(op.f("ix_notifications_horario"), table_name="notifications")
        op.drop_index(op.f("ix_notifications_lida"), table_name="notifications")
        op.drop_index(op.f("ix_notifications_tipo"), table_name="notifications")
        op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
        op.drop_index(op.f("ix_notifications_id"), table_name="notifications")
        op.drop_table("notifications")
