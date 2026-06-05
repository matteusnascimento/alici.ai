"""add admin operations

Revision ID: h6i7j8k9l0m1
Revises: g5h6i7j8k9l0
Create Date: 2026-06-04 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "h6i7j8k9l0m1"
down_revision = "g5h6i7j8k9l0"
branch_labels = None
depends_on = None


def _tables() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    if "users" in _tables() and "disabled_at" not in _columns("users"):
        op.add_column("users", sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True))

    if "admin_permissions" not in _tables():
        op.create_table(
            "admin_permissions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("permissions_json", sa.Text(), nullable=False),
            sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["updated_by_user_id"], ["users.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id"),
        )
        op.create_index(op.f("ix_admin_permissions_id"), "admin_permissions", ["id"], unique=False)
        op.create_index(op.f("ix_admin_permissions_user_id"), "admin_permissions", ["user_id"], unique=True)

    if "admin_audit_events" not in _tables():
        op.create_table(
            "admin_audit_events",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("actor_user_id", sa.Integer(), nullable=True),
            sa.Column("target_user_id", sa.Integer(), nullable=True),
            sa.Column("action", sa.String(length=80), nullable=False),
            sa.Column("origin", sa.String(length=80), nullable=False),
            sa.Column("details_json", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["target_user_id"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_admin_audit_events_id"), "admin_audit_events", ["id"], unique=False)
        op.create_index(op.f("ix_admin_audit_events_actor_user_id"), "admin_audit_events", ["actor_user_id"], unique=False)
        op.create_index(op.f("ix_admin_audit_events_target_user_id"), "admin_audit_events", ["target_user_id"], unique=False)
        op.create_index(op.f("ix_admin_audit_events_action"), "admin_audit_events", ["action"], unique=False)
        op.create_index(op.f("ix_admin_audit_events_created_at"), "admin_audit_events", ["created_at"], unique=False)


def downgrade() -> None:
    pass
