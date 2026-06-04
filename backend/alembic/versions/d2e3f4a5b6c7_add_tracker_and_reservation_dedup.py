"""add tracker and reservation dedup fields

Revision ID: d2e3f4a5b6c7
Revises: c6d7e8f9a0b1
Create Date: 2026-06-03 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "d2e3f4a5b6c7"
down_revision = "c6d7e8f9a0b1"
branch_labels = None
depends_on = None


def _columns(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def _add_column_if_missing(table: str, column: sa.Column) -> None:
    if column.name not in _columns(table):
        op.add_column(table, column)


def upgrade() -> None:
    _add_column_if_missing("reservations", sa.Column("user_id", sa.Integer(), nullable=True))
    _add_column_if_missing("reservations", sa.Column("reservation_number", sa.String(length=80), nullable=True))
    _add_column_if_missing("reservations", sa.Column("guest_document", sa.String(length=80), nullable=True))
    _add_column_if_missing("reservations", sa.Column("channel", sa.String(length=80), nullable=True))
    _add_column_if_missing("reservations", sa.Column("source", sa.String(length=120), nullable=True))
    _add_column_if_missing("reservations", sa.Column("city", sa.String(length=120), nullable=True))
    _add_column_if_missing("reservations", sa.Column("state", sa.String(length=80), nullable=True))
    _add_column_if_missing("reservations", sa.Column("country", sa.String(length=80), nullable=True))

    existing_indexes = {idx["name"] for idx in sa.inspect(op.get_bind()).get_indexes("reservations")}
    for name, column in {
        "ix_reservations_user_id": "user_id",
        "ix_reservations_reservation_number": "reservation_number",
        "ix_reservations_guest_document": "guest_document",
        "ix_reservations_channel": "channel",
        "ix_reservations_city": "city",
        "ix_reservations_state": "state",
        "ix_reservations_country": "country",
    }.items():
        if name not in existing_indexes:
            op.create_index(name, "reservations", [column], unique=False)

    if "website_events" not in sa.inspect(op.get_bind()).get_table_names():
        op.create_table(
            "website_events",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("site_id", sa.String(length=120), nullable=True),
            sa.Column("session_id", sa.String(length=120), nullable=False),
            sa.Column("event_type", sa.String(length=60), nullable=False),
            sa.Column("city", sa.String(length=120), nullable=True),
            sa.Column("state", sa.String(length=80), nullable=True),
            sa.Column("country", sa.String(length=80), nullable=True),
            sa.Column("traffic_source", sa.String(length=160), nullable=True),
            sa.Column("device", sa.String(length=80), nullable=True),
            sa.Column("utm_source", sa.String(length=120), nullable=True),
            sa.Column("utm_medium", sa.String(length=120), nullable=True),
            sa.Column("utm_campaign", sa.String(length=160), nullable=True),
            sa.Column("page_url", sa.String(length=1024), nullable=True),
            sa.Column("referrer", sa.String(length=1024), nullable=True),
            sa.Column("duration_seconds", sa.Integer(), nullable=True),
            sa.Column("pages_visited", sa.Integer(), nullable=True),
            sa.Column("click_target", sa.String(length=255), nullable=True),
            sa.Column("quote_value", sa.Float(), nullable=True),
            sa.Column("reservation_value", sa.Float(), nullable=True),
            sa.Column("payload_json", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        for column in ["id", "site_id", "session_id", "event_type", "city", "state", "country", "traffic_source", "utm_source", "utm_campaign", "created_at"]:
            op.create_index(op.f(f"ix_website_events_{column}"), "website_events", [column], unique=False)


def downgrade() -> None:
    if "website_events" in sa.inspect(op.get_bind()).get_table_names():
        op.drop_table("website_events")
