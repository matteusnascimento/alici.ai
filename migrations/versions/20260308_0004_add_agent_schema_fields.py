"""add agent schema fields

Revision ID: 20260308_0004
Revises: 20260308_0003
Create Date: 2026-03-08
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260308_0004"
down_revision = "20260308_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("platform_agents", sa.Column("instructions", sa.Text(), nullable=True))
    op.add_column("platform_agents", sa.Column("tools", sa.Text(), nullable=True))
    op.add_column("platform_agents", sa.Column("knowledge", sa.Text(), nullable=True))
    op.add_column("platform_agents", sa.Column("memory", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("platform_agents", "memory")
    op.drop_column("platform_agents", "knowledge")
    op.drop_column("platform_agents", "tools")
    op.drop_column("platform_agents", "instructions")
