"""initial platform schema

Revision ID: 20260308_0001
Revises:
Create Date: 2026-03-08 00:01:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260308_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_organizations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("plan", sa.String(), nullable=True, server_default="free"),
        sa.Column("stripe_customer_id", sa.String(), nullable=True),
        sa.Column("monthly_request_limit", sa.Integer(), nullable=True, server_default="1000"),
        sa.Column("current_month_requests", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column("allow_public_api", sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("stripe_customer_id"),
    )
    op.create_index(op.f("ix_platform_organizations_id"), "platform_organizations", ["id"], unique=False)
    op.create_index(op.f("ix_platform_organizations_slug"), "platform_organizations", ["slug"], unique=True)

    op.create_table(
        "platform_users",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column("is_superuser", sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["platform_organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_platform_users_email"), "platform_users", ["email"], unique=True)
    op.create_index(op.f("ix_platform_users_id"), "platform_users", ["id"], unique=False)

    op.create_table(
        "platform_agents",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("model", sa.String(), nullable=True, server_default="gpt-3.5-turbo"),
        sa.Column("temperature", sa.Integer(), nullable=True, server_default="70"),
        sa.Column("max_tokens", sa.Integer(), nullable=True, server_default="1000"),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column("is_public", sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column("total_requests", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("monthly_requests", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["platform_organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_platform_agents_id"), "platform_agents", ["id"], unique=False)

    op.create_table(
        "platform_api_keys",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("key", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("can_chat", sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column("can_generate", sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column("total_requests", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("monthly_requests", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["platform_organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_platform_api_keys_id"), "platform_api_keys", ["id"], unique=False)
    op.create_index(op.f("ix_platform_api_keys_key"), "platform_api_keys", ["key"], unique=True)

    op.create_table(
        "platform_usage_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("api_key_id", sa.String(), nullable=True),
        sa.Column("endpoint", sa.String(), nullable=False),
        sa.Column("method", sa.String(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("agent_id", sa.String(), nullable=True),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("cost", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("request_size", sa.Integer(), nullable=True),
        sa.Column("response_size", sa.Integer(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["agent_id"], ["platform_agents.id"]),
        sa.ForeignKeyConstraint(["api_key_id"], ["platform_api_keys.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["platform_organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["platform_users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_platform_usage_logs_id"), "platform_usage_logs", ["id"], unique=False)

    op.create_table(
        "platform_conversations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("agent_id", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["platform_agents.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["platform_organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["platform_users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_platform_conversations_id"), "platform_conversations", ["id"], unique=False)

    op.create_table(
        "platform_messages",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("conversation_id", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("finish_reason", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["conversation_id"], ["platform_conversations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_platform_messages_id"), "platform_messages", ["id"], unique=False)

    op.create_table(
        "platform_integrations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("credentials", sa.Text(), nullable=True, server_default="{}"),
        sa.Column("status", sa.String(), nullable=True, server_default="disconnected"),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["platform_organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["platform_users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_platform_integrations_id"), "platform_integrations", ["id"], unique=False)
    op.create_index(op.f("ix_platform_integrations_organization_id"), "platform_integrations", ["organization_id"], unique=False)
    op.create_index(op.f("ix_platform_integrations_type"), "platform_integrations", ["type"], unique=False)
    op.create_index(op.f("ix_platform_integrations_user_id"), "platform_integrations", ["user_id"], unique=False)

    op.create_table(
        "platform_subscriptions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("initiated_by_user_id", sa.String(), nullable=False),
        sa.Column("plan", sa.String(), nullable=False, server_default="free"),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("stripe_customer_id", sa.String(), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(), nullable=True),
        sa.Column("checkout_id", sa.String(), nullable=True),
        sa.Column("cancel_at_period_end", sa.Boolean(), nullable=True, server_default=sa.false()),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["initiated_by_user_id"], ["platform_users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["platform_organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_platform_subscriptions_id"), "platform_subscriptions", ["id"], unique=False)
    op.create_index(op.f("ix_platform_subscriptions_initiated_by_user_id"), "platform_subscriptions", ["initiated_by_user_id"], unique=False)
    op.create_index(op.f("ix_platform_subscriptions_organization_id"), "platform_subscriptions", ["organization_id"], unique=False)

    op.create_table(
        "platform_user_settings",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("language", sa.String(), nullable=True, server_default="pt-BR"),
        sa.Column("theme", sa.String(), nullable=True, server_default="dark"),
        sa.Column("notifications_enabled", sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column("api_key_alias", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["platform_users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_platform_user_settings_id"), "platform_user_settings", ["id"], unique=False)
    op.create_index(op.f("ix_platform_user_settings_user_id"), "platform_user_settings", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_platform_user_settings_user_id"), table_name="platform_user_settings")
    op.drop_index(op.f("ix_platform_user_settings_id"), table_name="platform_user_settings")
    op.drop_table("platform_user_settings")

    op.drop_index(op.f("ix_platform_subscriptions_organization_id"), table_name="platform_subscriptions")
    op.drop_index(op.f("ix_platform_subscriptions_initiated_by_user_id"), table_name="platform_subscriptions")
    op.drop_index(op.f("ix_platform_subscriptions_id"), table_name="platform_subscriptions")
    op.drop_table("platform_subscriptions")

    op.drop_index(op.f("ix_platform_integrations_user_id"), table_name="platform_integrations")
    op.drop_index(op.f("ix_platform_integrations_type"), table_name="platform_integrations")
    op.drop_index(op.f("ix_platform_integrations_organization_id"), table_name="platform_integrations")
    op.drop_index(op.f("ix_platform_integrations_id"), table_name="platform_integrations")
    op.drop_table("platform_integrations")

    op.drop_index(op.f("ix_platform_messages_id"), table_name="platform_messages")
    op.drop_table("platform_messages")

    op.drop_index(op.f("ix_platform_conversations_id"), table_name="platform_conversations")
    op.drop_table("platform_conversations")

    op.drop_index(op.f("ix_platform_usage_logs_id"), table_name="platform_usage_logs")
    op.drop_table("platform_usage_logs")

    op.drop_index(op.f("ix_platform_api_keys_key"), table_name="platform_api_keys")
    op.drop_index(op.f("ix_platform_api_keys_id"), table_name="platform_api_keys")
    op.drop_table("platform_api_keys")

    op.drop_index(op.f("ix_platform_agents_id"), table_name="platform_agents")
    op.drop_table("platform_agents")

    op.drop_index(op.f("ix_platform_users_id"), table_name="platform_users")
    op.drop_index(op.f("ix_platform_users_email"), table_name="platform_users")
    op.drop_table("platform_users")

    op.drop_index(op.f("ix_platform_organizations_slug"), table_name="platform_organizations")
    op.drop_index(op.f("ix_platform_organizations_id"), table_name="platform_organizations")
    op.drop_table("platform_organizations")
