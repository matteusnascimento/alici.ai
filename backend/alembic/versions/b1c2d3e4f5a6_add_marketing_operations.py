"""add marketing operations

Revision ID: b1c2d3e4f5a6
Revises: a9b8c7d6e5f4
Create Date: 2026-06-03 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "b1c2d3e4f5a6"
down_revision = "a9b8c7d6e5f4"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    inspector = inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _index_exists(table_name: str, index_name: str) -> bool:
    if not _table_exists(table_name):
        return False
    inspector = inspect(op.get_bind())
    return index_name in {index["name"] for index in inspector.get_indexes(table_name)}


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str]) -> None:
    if not _index_exists(table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    if not _table_exists("marketing_audiences"):
        op.create_table(
            "marketing_audiences",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("city", sa.String(length=120), nullable=True),
            sa.Column("state", sa.String(length=80), nullable=True),
            sa.Column("country", sa.String(length=80), nullable=True),
            sa.Column("ticket", sa.String(length=80), nullable=True),
            sa.Column("source", sa.String(length=120), nullable=True),
            sa.Column("reservations", sa.String(length=120), nullable=True),
            sa.Column("behavior", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing("ix_marketing_audiences_id", "marketing_audiences", ["id"])
    _create_index_if_missing("ix_marketing_audiences_user_id", "marketing_audiences", ["user_id"])

    if not _table_exists("marketing_calendar_events"):
        op.create_table(
            "marketing_calendar_events",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=140), nullable=False),
            sa.Column("date", sa.Date(), nullable=False),
            sa.Column("channel", sa.String(length=80), nullable=True),
            sa.Column("status", sa.String(length=40), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
    _create_index_if_missing("ix_marketing_calendar_events_date", "marketing_calendar_events", ["date"])
    _create_index_if_missing("ix_marketing_calendar_events_id", "marketing_calendar_events", ["id"])
    _create_index_if_missing("ix_marketing_calendar_events_user_id", "marketing_calendar_events", ["user_id"])


def downgrade() -> None:
    for index_name in (
        "ix_marketing_calendar_events_user_id",
        "ix_marketing_calendar_events_id",
        "ix_marketing_calendar_events_date",
    ):
        if _index_exists("marketing_calendar_events", index_name):
            op.drop_index(index_name, table_name="marketing_calendar_events")
    if _table_exists("marketing_calendar_events"):
        op.drop_table("marketing_calendar_events")

    for index_name in ("ix_marketing_audiences_user_id", "ix_marketing_audiences_id"):
        if _index_exists("marketing_audiences", index_name):
            op.drop_index(index_name, table_name="marketing_audiences")
    if _table_exists("marketing_audiences"):
        op.drop_table("marketing_audiences")
