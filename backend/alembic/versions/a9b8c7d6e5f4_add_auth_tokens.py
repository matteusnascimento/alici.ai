"""add_auth_tokens

Revision ID: a9b8c7d6e5f4
Revises: f3a4b5c6d7e8
Create Date: 2026-05-30 08:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "a9b8c7d6e5f4"
down_revision: Union[str, None] = "f3a4b5c6d7e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    inspector = inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _index_exists(table_name: str, index_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    inspector = inspect(op.get_bind())
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if not _table_exists("auth_tokens"):
        op.create_table(
            "auth_tokens",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("token_hash", sa.String(length=128), nullable=False),
            sa.Column("token_type", sa.String(length=40), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )

    if not _index_exists("auth_tokens", "ix_auth_tokens_user_id"):
        op.create_index("ix_auth_tokens_user_id", "auth_tokens", ["user_id"])
    if not _index_exists("auth_tokens", "ix_auth_tokens_token_hash"):
        op.create_index("ix_auth_tokens_token_hash", "auth_tokens", ["token_hash"], unique=True)
    if not _index_exists("auth_tokens", "ix_auth_tokens_token_type"):
        op.create_index("ix_auth_tokens_token_type", "auth_tokens", ["token_type"])
    if not _index_exists("auth_tokens", "ix_auth_tokens_expires_at"):
        op.create_index("ix_auth_tokens_expires_at", "auth_tokens", ["expires_at"])


def downgrade() -> None:
    for index_name in (
        "ix_auth_tokens_expires_at",
        "ix_auth_tokens_token_type",
        "ix_auth_tokens_token_hash",
        "ix_auth_tokens_user_id",
    ):
        if _index_exists("auth_tokens", index_name):
            op.drop_index(index_name, table_name="auth_tokens")
    if _table_exists("auth_tokens"):
        op.drop_table("auth_tokens")
