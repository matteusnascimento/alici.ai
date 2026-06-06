"""add_channel_integration_foundation

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-04-11 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
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
    # Create integration_accounts table
    if not _table_exists("integration_accounts"):
        op.create_table(
            "integration_accounts",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("provider", sa.String(length=40), nullable=False),
            sa.Column("external_account_id", sa.String(length=180), nullable=True),
            sa.Column("external_account_name", sa.String(length=180), nullable=True),
            sa.Column("access_token_encrypted", sa.Text(), nullable=True),
            sa.Column("refresh_token_encrypted", sa.Text(), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=30), nullable=False, server_default="disconnected"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint("user_id", "provider", "external_account_id", name="uq_integration_account_provider_external"),
        )
    
    if not _index_exists("integration_accounts", "ix_integration_accounts_id"):
        op.create_index("ix_integration_accounts_id", "integration_accounts", ["id"])
    
    if not _index_exists("integration_accounts", "ix_integration_accounts_user_id"):
        op.create_index("ix_integration_accounts_user_id", "integration_accounts", ["user_id"])
    
    if not _index_exists("integration_accounts", "ix_integration_accounts_provider"):
        op.create_index("ix_integration_accounts_provider", "integration_accounts", ["provider"])

    # Create channel_endpoints table
    if not _table_exists("channel_endpoints"):
        op.create_table(
            "channel_endpoints",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("integration_account_id", sa.Integer(), sa.ForeignKey("integration_accounts.id", ondelete="CASCADE"), nullable=False),
            sa.Column("provider", sa.String(length=40), nullable=False),
            sa.Column("external_channel_id", sa.String(length=180), nullable=True),
            sa.Column("channel_name", sa.String(length=180), nullable=False),
            sa.Column("phone_number_or_handle", sa.String(length=180), nullable=True),
            sa.Column("webhook_status", sa.String(length=30), nullable=False, server_default="pending_setup"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint("integration_account_id", "provider", "external_channel_id", name="uq_channel_endpoint_external"),
        )
    
    if not _index_exists("channel_endpoints", "ix_channel_endpoints_id"):
        op.create_index("ix_channel_endpoints_id", "channel_endpoints", ["id"])
    
    if not _index_exists("channel_endpoints", "ix_channel_endpoints_provider"):
        op.create_index("ix_channel_endpoints_provider", "channel_endpoints", ["provider"])
    
    if not _index_exists("channel_endpoints", "ix_channel_endpoints_integration_account_id"):
        op.create_index("ix_channel_endpoints_integration_account_id", "channel_endpoints", ["integration_account_id"])

    # Create agent_channel_bindings table
    if not _table_exists("agent_channel_bindings"):
        op.create_table(
            "agent_channel_bindings",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("agent_id", sa.Integer(), sa.ForeignKey("agents.id", ondelete="CASCADE"), nullable=False),
            sa.Column("channel_endpoint_id", sa.Integer(), sa.ForeignKey("channel_endpoints.id", ondelete="CASCADE"), nullable=False),
            sa.Column("provider", sa.String(length=40), nullable=False),
            sa.Column("status", sa.String(length=30), nullable=False, server_default="disconnected"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("fallback_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("last_test_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("last_test_status", sa.String(length=30), nullable=True),
            sa.Column("last_test_message", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.UniqueConstraint("agent_id", "channel_endpoint_id", name="uq_agent_channel_binding_endpoint"),
        )
    
    if not _index_exists("agent_channel_bindings", "ix_agent_channel_bindings_id"):
        op.create_index("ix_agent_channel_bindings_id", "agent_channel_bindings", ["id"])
    
    if not _index_exists("agent_channel_bindings", "ix_agent_channel_bindings_agent_id"):
        op.create_index("ix_agent_channel_bindings_agent_id", "agent_channel_bindings", ["agent_id"])
    
    if not _index_exists("agent_channel_bindings", "ix_agent_channel_bindings_channel_endpoint_id"):
        op.create_index("ix_agent_channel_bindings_channel_endpoint_id", "agent_channel_bindings", ["channel_endpoint_id"])
    
    if not _index_exists("agent_channel_bindings", "ix_agent_channel_bindings_provider"):
        op.create_index("ix_agent_channel_bindings_provider", "agent_channel_bindings", ["provider"])
    
    if not _index_exists("agent_channel_bindings", "ix_agent_channel_bindings_status"):
        op.create_index("ix_agent_channel_bindings_status", "agent_channel_bindings", ["status"])

    # Create channel_webhook_events table
    if not _table_exists("channel_webhook_events"):
        op.create_table(
            "channel_webhook_events",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("channel_endpoint_id", sa.Integer(), sa.ForeignKey("channel_endpoints.id", ondelete="SET NULL"), nullable=True),
            sa.Column("provider", sa.String(length=40), nullable=False),
            sa.Column("event_type", sa.String(length=80), nullable=False),
            sa.Column("payload_json", sa.Text(), nullable=False),
            sa.Column("processed", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
    
    if not _index_exists("channel_webhook_events", "ix_channel_webhook_events_id"):
        op.create_index("ix_channel_webhook_events_id", "channel_webhook_events", ["id"])
    
    if not _index_exists("channel_webhook_events", "ix_channel_webhook_events_channel_endpoint_id"):
        op.create_index("ix_channel_webhook_events_channel_endpoint_id", "channel_webhook_events", ["channel_endpoint_id"])
    
    if not _index_exists("channel_webhook_events", "ix_channel_webhook_events_provider"):
        op.create_index("ix_channel_webhook_events_provider", "channel_webhook_events", ["provider"])
    
    if not _index_exists("channel_webhook_events", "ix_channel_webhook_events_event_type"):
        op.create_index("ix_channel_webhook_events_event_type", "channel_webhook_events", ["event_type"])


def downgrade() -> None:
    # Drop channel_webhook_events table and indexes
    if _index_exists("channel_webhook_events", "ix_channel_webhook_events_event_type"):
        op.drop_index("ix_channel_webhook_events_event_type", table_name="channel_webhook_events")
    
    if _index_exists("channel_webhook_events", "ix_channel_webhook_events_provider"):
        op.drop_index("ix_channel_webhook_events_provider", table_name="channel_webhook_events")
    
    if _index_exists("channel_webhook_events", "ix_channel_webhook_events_channel_endpoint_id"):
        op.drop_index("ix_channel_webhook_events_channel_endpoint_id", table_name="channel_webhook_events")
    
    if _index_exists("channel_webhook_events", "ix_channel_webhook_events_id"):
        op.drop_index("ix_channel_webhook_events_id", table_name="channel_webhook_events")
    
    if _table_exists("channel_webhook_events"):
        op.drop_table("channel_webhook_events")

    # Drop agent_channel_bindings table and indexes
    if _index_exists("agent_channel_bindings", "ix_agent_channel_bindings_status"):
        op.drop_index("ix_agent_channel_bindings_status", table_name="agent_channel_bindings")
    
    if _index_exists("agent_channel_bindings", "ix_agent_channel_bindings_provider"):
        op.drop_index("ix_agent_channel_bindings_provider", table_name="agent_channel_bindings")
    
    if _index_exists("agent_channel_bindings", "ix_agent_channel_bindings_channel_endpoint_id"):
        op.drop_index("ix_agent_channel_bindings_channel_endpoint_id", table_name="agent_channel_bindings")
    
    if _index_exists("agent_channel_bindings", "ix_agent_channel_bindings_agent_id"):
        op.drop_index("ix_agent_channel_bindings_agent_id", table_name="agent_channel_bindings")
    
    if _index_exists("agent_channel_bindings", "ix_agent_channel_bindings_id"):
        op.drop_index("ix_agent_channel_bindings_id", table_name="agent_channel_bindings")
    
    if _table_exists("agent_channel_bindings"):
        op.drop_table("agent_channel_bindings")

    # Drop channel_endpoints table and indexes
    if _index_exists("channel_endpoints", "ix_channel_endpoints_integration_account_id"):
        op.drop_index("ix_channel_endpoints_integration_account_id", table_name="channel_endpoints")
    
    if _index_exists("channel_endpoints", "ix_channel_endpoints_provider"):
        op.drop_index("ix_channel_endpoints_provider", table_name="channel_endpoints")
    
    if _index_exists("channel_endpoints", "ix_channel_endpoints_id"):
        op.drop_index("ix_channel_endpoints_id", table_name="channel_endpoints")
    
    if _table_exists("channel_endpoints"):
        op.drop_table("channel_endpoints")

    # Drop integration_accounts table and indexes
    if _index_exists("integration_accounts", "ix_integration_accounts_provider"):
        op.drop_index("ix_integration_accounts_provider", table_name="integration_accounts")
    
    if _index_exists("integration_accounts", "ix_integration_accounts_user_id"):
        op.drop_index("ix_integration_accounts_user_id", table_name="integration_accounts")
    
    if _index_exists("integration_accounts", "ix_integration_accounts_id"):
        op.drop_index("ix_integration_accounts_id", table_name="integration_accounts")
    
    if _table_exists("integration_accounts"):
        op.drop_table("integration_accounts")
