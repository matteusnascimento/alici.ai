"""add_stripe_billing_fields

Revision ID: b9f1c2d3e4f5
Revises: 83fa077000f9
Create Date: 2026-04-12 17:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b9f1c2d3e4f5"
down_revision: Union[str, None] = "83fa077000f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _tables() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def _columns(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {col["name"] for col in inspector.get_columns(table_name)}


def _indexes(table_name: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return set()
    return {idx["name"] for idx in inspector.get_indexes(table_name)}


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if table_name not in _tables():
        return
    if column.name not in _columns(table_name):
        op.add_column(table_name, column)


def _create_index_if_missing(index_name: str, table_name: str, columns: list[str], *, unique: bool = False) -> None:
    if table_name not in _tables():
        return
    if index_name not in _indexes(table_name):
        op.create_index(index_name, table_name, columns, unique=unique)


def _drop_index_if_exists(index_name: str, table_name: str) -> None:
    if index_name in _indexes(table_name):
        op.drop_index(index_name, table_name=table_name)


def _drop_column_if_exists(table_name: str, column_name: str) -> None:
    if column_name in _columns(table_name):
        op.drop_column(table_name, column_name)


def upgrade() -> None:
    if "subscriptions" in _tables():
        _add_column_if_missing("subscriptions", sa.Column("currency", sa.String(length=10), nullable=False, server_default="BRL"))
        _add_column_if_missing("subscriptions", sa.Column("provider", sa.String(length=40), nullable=True))
        _add_column_if_missing("subscriptions", sa.Column("stripe_customer_id", sa.String(length=100), nullable=True))
        _add_column_if_missing("subscriptions", sa.Column("stripe_subscription_id", sa.String(length=100), nullable=True))
        _add_column_if_missing("subscriptions", sa.Column("stripe_price_id", sa.String(length=100), nullable=True))
        _add_column_if_missing("subscriptions", sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False, server_default=sa.false()))
        _add_column_if_missing("subscriptions", sa.Column("last_checkout_session_id", sa.String(length=100), nullable=True))
        _add_column_if_missing("subscriptions", sa.Column("last_invoice_id", sa.String(length=100), nullable=True))
        _add_column_if_missing("subscriptions", sa.Column("external_status", sa.String(length=40), nullable=True))
        _add_column_if_missing("subscriptions", sa.Column("metadata_json", sa.Text(), nullable=True))
        _create_index_if_missing("ix_subscriptions_stripe_customer_id", "subscriptions", ["stripe_customer_id"])
        _create_index_if_missing("ix_subscriptions_stripe_subscription_id", "subscriptions", ["stripe_subscription_id"])

    if "billing_events" in _tables():
        _add_column_if_missing("billing_events", sa.Column("stripe_event_id", sa.String(length=100), nullable=True))
        _add_column_if_missing("billing_events", sa.Column("status", sa.String(length=30), nullable=True))
        _add_column_if_missing("billing_events", sa.Column("payload_json", sa.Text(), nullable=True))
        _create_index_if_missing("ix_billing_events_stripe_event_id", "billing_events", ["stripe_event_id"], unique=True)


def downgrade() -> None:
    _drop_index_if_exists("ix_billing_events_stripe_event_id", "billing_events")
    _drop_column_if_exists("billing_events", "payload_json")
    _drop_column_if_exists("billing_events", "status")
    _drop_column_if_exists("billing_events", "stripe_event_id")

    _drop_index_if_exists("ix_subscriptions_stripe_subscription_id", "subscriptions")
    _drop_index_if_exists("ix_subscriptions_stripe_customer_id", "subscriptions")
    _drop_column_if_exists("subscriptions", "metadata_json")
    _drop_column_if_exists("subscriptions", "external_status")
    _drop_column_if_exists("subscriptions", "last_invoice_id")
    _drop_column_if_exists("subscriptions", "last_checkout_session_id")
    _drop_column_if_exists("subscriptions", "cancel_at_period_end")
    _drop_column_if_exists("subscriptions", "stripe_price_id")
    _drop_column_if_exists("subscriptions", "stripe_subscription_id")
    _drop_column_if_exists("subscriptions", "stripe_customer_id")
    _drop_column_if_exists("subscriptions", "provider")
    _drop_column_if_exists("subscriptions", "currency")
