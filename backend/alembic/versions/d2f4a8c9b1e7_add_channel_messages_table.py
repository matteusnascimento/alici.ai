"""add_channel_messages_table

Revision ID: d2f4a8c9b1e7
Revises: c4d5e6f7a8b9
Create Date: 2026-04-12 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "d2f4a8c9b1e7"
down_revision: Union[str, None] = "c4d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    """Check if a table exists in the current database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def _index_exists(table_name: str, index_name: str) -> bool:
    """Check if an index exists in the current database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    
    if table_name not in inspector.get_table_names():
        return False
    
    return index_name in {idx["name"] for idx in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if not _table_exists("channel_messages"):
        op.create_table(
            "channel_messages",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="SET NULL"), nullable=True),
            sa.Column("provider", sa.String(length=40), nullable=False),
            sa.Column("direction", sa.String(length=30), nullable=False),
            sa.Column("external_message_id", sa.String(length=180), nullable=True),
            sa.Column("endpoint_id", sa.Integer(), sa.ForeignKey("channel_endpoints.id", ondelete="SET NULL"), nullable=True),
            sa.Column("binding_id", sa.Integer(), sa.ForeignKey("agent_channel_bindings.id", ondelete="SET NULL"), nullable=True),
            sa.Column("payload_summary", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=30), nullable=False, server_default="processing"),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
    
    if not _index_exists("channel_messages", "ix_channel_messages_id"):
        op.create_index("ix_channel_messages_id", "channel_messages", ["id"])
    
    if not _index_exists("channel_messages", "ix_channel_messages_user_id"):
        op.create_index("ix_channel_messages_user_id", "channel_messages", ["user_id"])
    
    if not _index_exists("channel_messages", "ix_channel_messages_agent_id"):
        op.create_index("ix_channel_messages_agent_id", "channel_messages", ["agent_id"])
    
    if not _index_exists("channel_messages", "ix_channel_messages_provider"):
        op.create_index("ix_channel_messages_provider", "channel_messages", ["provider"])
    
    if not _index_exists("channel_messages", "ix_channel_messages_direction"):
        op.create_index("ix_channel_messages_direction", "channel_messages", ["direction"])
    
    if not _index_exists("channel_messages", "ix_channel_messages_external_message_id"):
        op.create_index("ix_channel_messages_external_message_id", "channel_messages", ["external_message_id"])
    
    if not _index_exists("channel_messages", "ix_channel_messages_endpoint_id"):
        op.create_index("ix_channel_messages_endpoint_id", "channel_messages", ["endpoint_id"])
    
    if not _index_exists("channel_messages", "ix_channel_messages_binding_id"):
        op.create_index("ix_channel_messages_binding_id", "channel_messages", ["binding_id"])
    
    if not _index_exists("channel_messages", "ix_channel_messages_status"):
        op.create_index("ix_channel_messages_status", "channel_messages", ["status"])


def downgrade() -> None:
    if _index_exists("channel_messages", "ix_channel_messages_status"):
        op.drop_index("ix_channel_messages_status", table_name="channel_messages")
    
    if _index_exists("channel_messages", "ix_channel_messages_binding_id"):
        op.drop_index("ix_channel_messages_binding_id", table_name="channel_messages")
    
    if _index_exists("channel_messages", "ix_channel_messages_endpoint_id"):
        op.drop_index("ix_channel_messages_endpoint_id", table_name="channel_messages")
    
    if _index_exists("channel_messages", "ix_channel_messages_external_message_id"):
        op.drop_index("ix_channel_messages_external_message_id", table_name="channel_messages")
    
    if _index_exists("channel_messages", "ix_channel_messages_direction"):
        op.drop_index("ix_channel_messages_direction", table_name="channel_messages")
    
    if _index_exists("channel_messages", "ix_channel_messages_provider"):
        op.drop_index("ix_channel_messages_provider", table_name="channel_messages")
    
    if _index_exists("channel_messages", "ix_channel_messages_agent_id"):
        op.drop_index("ix_channel_messages_agent_id", table_name="channel_messages")
    
    if _index_exists("channel_messages", "ix_channel_messages_user_id"):
        op.drop_index("ix_channel_messages_user_id", table_name="channel_messages")
    
    if _index_exists("channel_messages", "ix_channel_messages_id"):
        op.drop_index("ix_channel_messages_id", table_name="channel_messages")
    
    if _table_exists("channel_messages"):
        op.drop_table("channel_messages")
