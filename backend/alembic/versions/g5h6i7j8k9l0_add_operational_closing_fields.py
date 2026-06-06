"""add operational closing fields

Revision ID: g5h6i7j8k9l0
Revises: f4a5b6c7d8e9
Create Date: 2026-06-04 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "g5h6i7j8k9l0"
down_revision = "f4a5b6c7d8e9"
branch_labels = None
depends_on = None


def _tables() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def _indexes(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {index["name"] for index in inspector.get_indexes(table_name)}


def _add_column_if_missing(table: str, column: sa.Column) -> None:
    if column.name not in _columns(table):
        op.add_column(table, column)


def _create_index_if_missing(name: str, table: str, columns: list[str], unique: bool = False) -> None:
    if name not in _indexes(table):
        op.create_index(name, table, columns, unique=unique)


def upgrade() -> None:
    if "website_events" in _tables():
        _add_column_if_missing("website_events", sa.Column("visitor_id", sa.String(length=120), nullable=True))
        _add_column_if_missing("website_events", sa.Column("utm_term", sa.String(length=160), nullable=True))
        _add_column_if_missing("website_events", sa.Column("utm_content", sa.String(length=160), nullable=True))
        _add_column_if_missing("website_events", sa.Column("search_query", sa.String(length=255), nullable=True))
        _create_index_if_missing("ix_website_events_visitor_id", "website_events", ["visitor_id"])

    if "leads" in _tables():
        _add_column_if_missing("leads", sa.Column("lead_identity_hash", sa.String(length=64), nullable=True))
        _create_index_if_missing("ix_leads_lead_identity_hash", "leads", ["lead_identity_hash"], unique=True)

    if "marketing_projects" in _tables():
        _add_column_if_missing("marketing_projects", sa.Column("channels", sa.String(length=240), nullable=True))
        _add_column_if_missing("marketing_projects", sa.Column("budget", sa.Float(), nullable=True))
        _add_column_if_missing("marketing_projects", sa.Column("creative_project_id", sa.String(length=80), nullable=True))
        _add_column_if_missing("marketing_projects", sa.Column("status", sa.String(length=40), nullable=True, server_default="draft"))
        _add_column_if_missing("marketing_projects", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))
        _add_column_if_missing("marketing_projects", sa.Column("last_publish_error", sa.Text(), nullable=True))
        _add_column_if_missing("marketing_projects", sa.Column("metrics_json", sa.Text(), nullable=True))
        _create_index_if_missing("ix_marketing_projects_status", "marketing_projects", ["status"])

    if "chat_quotes" not in _tables():
        op.create_table(
            "chat_quotes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("conversation_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=160), nullable=False),
            sa.Column("amount", sa.Float(), nullable=True),
            sa.Column("currency", sa.String(length=10), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=40), nullable=False),
            sa.Column("delivery_status", sa.String(length=40), nullable=False),
            sa.Column("provider", sa.String(length=60), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["conversation_id"], ["agent_conversations.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        for column in ["id", "conversation_id", "user_id", "status", "delivery_status", "provider", "created_at"]:
            op.create_index(op.f(f"ix_chat_quotes_{column}"), "chat_quotes", [column], unique=False)

    if "chat_tasks" not in _tables():
        op.create_table(
            "chat_tasks",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("conversation_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=160), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("task_type", sa.String(length=40), nullable=False),
            sa.Column("status", sa.String(length=40), nullable=False),
            sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["conversation_id"], ["agent_conversations.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        for column in ["id", "conversation_id", "user_id", "task_type", "status", "created_at"]:
            op.create_index(op.f(f"ix_chat_tasks_{column}"), "chat_tasks", [column], unique=False)

    if "chat_tags" not in _tables():
        op.create_table(
            "chat_tags",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("conversation_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("tag", sa.String(length=80), nullable=False),
            sa.Column("color", sa.String(length=30), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["conversation_id"], ["agent_conversations.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("conversation_id", "tag", name="uq_chat_tags_conversation_tag"),
        )
        for column in ["id", "conversation_id", "user_id", "tag", "created_at"]:
            op.create_index(op.f(f"ix_chat_tags_{column}"), "chat_tags", [column], unique=False)


def downgrade() -> None:
    pass
