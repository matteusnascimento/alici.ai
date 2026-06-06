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
    inspector = inspect(op.get_bind())

    if table_name not in inspector.get_table_names():
        return False

    return index_name in {idx["name"] for idx in inspector.get_indexes(table_name)}


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
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _index_exists("marketing_audiences", "ix_marketing_audiences_id"):
        op.create_index(
            op.f("ix_marketing_audiences_id"),
            "marketing_audiences",
            ["id"],
            unique=False,
        )

    if not _index_exists("marketing_audiences", "ix_marketing_audiences_user_id"):
        op.create_index(
            op.f("ix_marketing_audiences_user_id"),
            "marketing_audiences",
            ["user_id"],
            unique=False,
        )

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
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _index_exists("marketing_calendar_events", "ix_marketing_calendar_events_date"):
        op.create_index(
            op.f("ix_marketing_calendar_events_date"),
            "marketing_calendar_events",
            ["date"],
            unique=False,
        )

    if not _index_exists("marketing_calendar_events", "ix_marketing_calendar_events_id"):
        op.create_index(
            op.f("ix_marketing_calendar_events_id"),
            "marketing_calendar_events",
            ["id"],
            unique=False,
        )

    if not _index_exists("marketing_calendar_events", "ix_marketing_calendar_events_user_id"):
        op.create_index(
            op.f("ix_marketing_calendar_events_user_id"),
            "marketing_calendar_events",
            ["user_id"],
            unique=False,
        )


def downgrade() -> None:
    if _index_exists("marketing_calendar_events", "ix_marketing_calendar_events_user_id"):
        op.drop_index(
            op.f("ix_marketing_calendar_events_user_id"),
            table_name="marketing_calendar_events",
        )

    if _index_exists("marketing_calendar_events", "ix_marketing_calendar_events_id"):
        op.drop_index(
            op.f("ix_marketing_calendar_events_id"),
            table_name="marketing_calendar_events",
        )

    if _index_exists("marketing_calendar_events", "ix_marketing_calendar_events_date"):
        op.drop_index(
            op.f("ix_marketing_calendar_events_date"),
            table_name="marketing_calendar_events",
        )

    if _table_exists("marketing_calendar_events"):
        op.drop_table("marketing_calendar_events")

    if _index_exists("marketing_audiences", "ix_marketing_audiences_user_id"):
        op.drop_index(
            op.f("ix_marketing_audiences_user_id"),
            table_name="marketing_audiences",
        )

    if _index_exists("marketing_audiences", "ix_marketing_audiences_id"):
        op.drop_index(
            op.f("ix_marketing_audiences_id"),
            table_name="marketing_audiences",
        )

    if _table_exists("marketing_audiences"):
        op.drop_table("marketing_audiences")
