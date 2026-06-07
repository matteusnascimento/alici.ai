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


def _tables() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _table_exists(table_name: str) -> bool:
    return table_name in _tables()


def _columns(table_name: str) -> set[str]:
    if not _table_exists(table_name):
        return set()
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table_name)}


def _indexes(table_name: str) -> set[str]:
    if not _table_exists(table_name):
        return set()
    return {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def _add_column_if_missing(table: str, column: sa.Column) -> None:
    if not _table_exists(table):
        print(f"Table '{table}' does not exist. Skipping column '{column.name}'.")
        return
    if column.name not in _columns(table):
        op.add_column(table, column)


def _create_index_if_missing(name: str, table: str, columns: list[str], unique: bool = False) -> None:
    if not _table_exists(table):
        print(f"Table '{table}' does not exist. Skipping index '{name}'.")
        return
    if name not in _indexes(table):
        op.create_index(name, table, columns, unique=unique)


def upgrade() -> None:
    if _table_exists("reservations"):
        _add_column_if_missing("reservations", sa.Column("user_id", sa.Integer(), nullable=True))
        _add_column_if_missing("reservations", sa.Column("reservation_number", sa.String(length=80), nullable=True))
        _add_column_if_missing("reservations", sa.Column("guest_document", sa.String(length=80), nullable=True))
        _add_column_if_missing("reservations", sa.Column("channel", sa.String(length=80), nullable=True))
        _add_column_if_missing("reservations", sa.Column("source", sa.String(length=120), nullable=True))
        _add_column_if_missing("reservations", sa.Column("city", sa.String(length=120), nullable=True))
        _add_column_if_missing("reservations", sa.Column("state", sa.String(length=80), nullable=True))
        _add_column_if_missing("reservations", sa.Column("country", sa.String(length=80), nullable=True))

        for name, column in {
            "ix_reservations_user_id": "user_id",
            "ix_reservations_reservation_number": "reservation_number",
            "ix_reservations_guest_document": "guest_document",
            "ix_reservations_channel": "channel",
            "ix_reservations_city": "city",
            "ix_reservations_state": "state",
            "ix_reservations_country": "country",
        }.items():
            _create_index_if_missing(name, "reservations", [column])
    else:
        print("Table 'reservations' does not exist. Skipping reservation dedup fields.")

    if not _table_exists("website_events"):
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

    for column in [
        "id",
        "site_id",
        "session_id",
        "event_type",
        "city",
        "state",
        "country",
        "traffic_source",
        "utm_source",
        "utm_campaign",
        "created_at",
    ]:
        _create_index_if_missing(op.f(f"ix_website_events_{column}"), "website_events", [column])


def downgrade() -> None:
    if _table_exists("website_events"):
        op.drop_table("website_events")
