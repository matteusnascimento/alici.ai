"""add reservation identity hash

Revision ID: f4a5b6c7d8e9
Revises: e3f4a5b6c7d8
Create Date: 2026-06-03 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "f4a5b6c7d8e9"
down_revision = "e3f4a5b6c7d8"
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
    if table not in _tables():
        return
    if column.name not in _columns(table):
        op.add_column(table, column)


def _create_index_if_missing(name: str, table: str, columns: list[str], unique: bool = False) -> None:
    if table not in _tables():
        return
    if name not in _indexes(table):
        op.create_index(name, table, columns, unique=unique)


def upgrade() -> None:
    if "reservations" not in _tables():
        return

    _add_column_if_missing("reservations", sa.Column("external_reservation_id", sa.String(length=120), nullable=True))
    _add_column_if_missing("reservations", sa.Column("guest_email", sa.String(length=255), nullable=True))
    _add_column_if_missing("reservations", sa.Column("source_provider", sa.String(length=80), nullable=True))
    _add_column_if_missing("reservations", sa.Column("reservation_identity_hash", sa.String(length=64), nullable=True))

    for name, (column, unique) in {
        "ix_reservations_external_reservation_id": ("external_reservation_id", False),
        "ix_reservations_guest_email": ("guest_email", False),
        "ix_reservations_source_provider": ("source_provider", False),
        "ix_reservations_reservation_identity_hash": ("reservation_identity_hash", True),
    }.items():
        _create_index_if_missing(name, "reservations", [column], unique=unique)


def downgrade() -> None:
    pass
