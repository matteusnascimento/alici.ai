"""add omnichannel social connections

Revision ID: 0005_add_omnichannel_connections
Revises: 0004_add_stripe_invoice_credit_idempotency
Create Date: 2026-05-24
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0005_add_omnichannel_connections"
down_revision = "0004_add_stripe_invoice_credit_idempotency"
branch_labels = None
depends_on = None


json_type = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.create_table(
        "user_social_connections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("external_account_id", sa.Text(), nullable=False),
        sa.Column("external_account_name", sa.Text(), nullable=True),
        sa.Column("access_token", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False, server_default="connected"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("metadata", json_type, nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_user_social_connections_user", "user_social_connections", ["user_id"])
    op.create_index("idx_user_social_connections_provider", "user_social_connections", ["provider", "external_account_id"])

    op.create_table(
        "omnichannel_conversations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("external_account_id", sa.Text(), nullable=False),
        sa.Column("external_contact_id", sa.Text(), nullable=False),
        sa.Column("contact_name", sa.Text(), nullable=True),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("last_message_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "idx_omnichannel_conversations_lookup",
        "omnichannel_conversations",
        ["provider", "external_account_id", "external_contact_id"],
    )

    op.create_table(
        "omnichannel_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("connection_id", sa.Integer(), nullable=False),
        sa.Column("omnichannel_conversation_id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("direction", sa.Text(), nullable=False),
        sa.Column("external_message_id", sa.Text(), nullable=True),
        sa.Column("external_contact_id", sa.Text(), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("raw_payload", json_type, nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("idx_omnichannel_messages_user", "omnichannel_messages", ["user_id", "provider"])


def downgrade() -> None:
    op.drop_index("idx_omnichannel_messages_user", table_name="omnichannel_messages")
    op.drop_table("omnichannel_messages")
    op.drop_index("idx_omnichannel_conversations_lookup", table_name="omnichannel_conversations")
    op.drop_table("omnichannel_conversations")
    op.drop_index("idx_user_social_connections_provider", table_name="user_social_connections")
    op.drop_index("idx_user_social_connections_user", table_name="user_social_connections")
    op.drop_table("user_social_connections")
