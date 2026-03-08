"""add user memory table

Revision ID: 20260308_0002
Revises: 20260308_0001
Create Date: 2026-03-08 12:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260308_0002"
down_revision: Union[str, None] = "20260308_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_user_memory",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["platform_organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["platform_users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_platform_user_memory_id"), "platform_user_memory", ["id"], unique=False)
    op.create_index(op.f("ix_platform_user_memory_user_id"), "platform_user_memory", ["user_id"], unique=False)
    op.create_index(op.f("ix_platform_user_memory_organization_id"), "platform_user_memory", ["organization_id"], unique=False)
    op.create_index(op.f("ix_platform_user_memory_key"), "platform_user_memory", ["key"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_platform_user_memory_key"), table_name="platform_user_memory")
    op.drop_index(op.f("ix_platform_user_memory_organization_id"), table_name="platform_user_memory")
    op.drop_index(op.f("ix_platform_user_memory_user_id"), table_name="platform_user_memory")
    op.drop_index(op.f("ix_platform_user_memory_id"), table_name="platform_user_memory")
    op.drop_table("platform_user_memory")
