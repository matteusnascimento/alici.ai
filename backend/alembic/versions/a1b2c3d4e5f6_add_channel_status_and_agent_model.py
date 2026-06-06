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


def upgrade() -> None:
    # --- agent_channels ---
    op.execute("""
        ALTER TABLE agent_channels
        ADD COLUMN IF NOT EXISTS status VARCHAR(30) DEFAULT 'disconnected' NOT NULL;
    """)
    op.execute("""
        ALTER TABLE agent_channels
        ADD COLUMN IF NOT EXISTS access_token TEXT;
    """)
    op.execute("""
        ALTER TABLE agent_channels
        ADD COLUMN IF NOT EXISTS refresh_token TEXT;
    """)
    op.execute("""
        ALTER TABLE agent_channels
        ADD COLUMN IF NOT EXISTS webhook_url VARCHAR(512);
    """)
    op.execute("""
        ALTER TABLE agent_channels
        ADD COLUMN IF NOT EXISTS last_sync_at TIMESTAMP WITH TIME ZONE;
    """)
    op.execute("""
        ALTER TABLE agent_channels
        ADD COLUMN IF NOT EXISTS last_error TEXT;
    """)

    # --- agents ---
    op.execute("""
        ALTER TABLE agents
        ADD COLUMN IF NOT EXISTS preferred_model VARCHAR(80);
    """)


def downgrade() -> None:
    op.drop_column("agent_channels", "last_error")
    op.drop_column("agent_channels", "last_sync_at")
    op.drop_column("agent_channels", "webhook_url")
    op.drop_column("agent_channels", "refresh_token")
    op.drop_column("agent_channels", "access_token")
    op.drop_column("agent_channels", "status")
    op.drop_column("agents", "preferred_model")
