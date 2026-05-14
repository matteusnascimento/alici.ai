"""add_stripe_billing_fields

Revision ID: b9f1c2d3e4f5
Revises: 83fa077000f9
Create Date: 2026-04-12 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b9f1c2d3e4f5"
down_revision: Union[str, None] = "83fa077000f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_names(table_name: str) -> set[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return {col["name"] for col in inspector.get_columns(table_name)}


def upgrade() -> None:
    subscription_columns = _column_names("subscriptions")
    billing_event_columns = _column_names("billing_events")

    if "currency" not in subscription_columns:
        op.add_column("subscriptions", sa.Column("currency", sa.String(length=10), nullable=False, server_default="BRL"))
    if "provider" not in subscription_columns:
        op.add_column("subscriptions", sa.Column("provider", sa.String(length=40), nullable=True))
    if "stripe_customer_id" not in subscription_columns:
        op.add_column("subscriptions", sa.Column("stripe_customer_id", sa.String(length=100), nullable=True))
    if "stripe_subscription_id" not in subscription_columns:
        op.add_column("subscriptions", sa.Column("stripe_subscription_id", sa.String(length=100), nullable=True))
    if "stripe_price_id" not in subscription_columns:
        op.add_column("subscriptions", sa.Column("stripe_price_id", sa.String(length=100), nullable=True))
    if "cancel_at_period_end" not in subscription_columns:
        op.add_column("subscriptions", sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False, server_default=sa.false()))
    if "last_checkout_session_id" not in subscription_columns:
        op.add_column("subscriptions", sa.Column("last_checkout_session_id", sa.String(length=100), nullable=True))
    if "last_invoice_id" not in subscription_columns:
        op.add_column("subscriptions", sa.Column("last_invoice_id", sa.String(length=100), nullable=True))
    if "external_status" not in subscription_columns:
        op.add_column("subscriptions", sa.Column("external_status", sa.String(length=40), nullable=True))
    if "metadata_json" not in subscription_columns:
        op.add_column("subscriptions", sa.Column("metadata_json", sa.Text(), nullable=True))

    if "stripe_event_id" not in billing_event_columns:
        op.add_column("billing_events", sa.Column("stripe_event_id", sa.String(length=100), nullable=True))
    if "status" not in billing_event_columns:
        op.add_column("billing_events", sa.Column("status", sa.String(length=30), nullable=True))
    if "payload_json" not in billing_event_columns:
        op.add_column("billing_events", sa.Column("payload_json", sa.Text(), nullable=True))

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_indexes = {idx["name"] for idx in inspector.get_indexes("subscriptions")}
    if "ix_subscriptions_stripe_customer_id" not in existing_indexes:
        op.create_index("ix_subscriptions_stripe_customer_id", "subscriptions", ["stripe_customer_id"], unique=False)
    if "ix_subscriptions_stripe_subscription_id" not in existing_indexes:
        op.create_index("ix_subscriptions_stripe_subscription_id", "subscriptions", ["stripe_subscription_id"], unique=False)

    existing_event_indexes = {idx["name"] for idx in inspector.get_indexes("billing_events")}
    if "ix_billing_events_stripe_event_id" not in existing_event_indexes:
        op.create_index("ix_billing_events_stripe_event_id", "billing_events", ["stripe_event_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_billing_events_stripe_event_id", table_name="billing_events")
    op.drop_column("billing_events", "payload_json")
    op.drop_column("billing_events", "status")
    op.drop_column("billing_events", "stripe_event_id")

    op.drop_index("ix_subscriptions_stripe_subscription_id", table_name="subscriptions")
    op.drop_index("ix_subscriptions_stripe_customer_id", table_name="subscriptions")
    op.drop_column("subscriptions", "metadata_json")
    op.drop_column("subscriptions", "external_status")
    op.drop_column("subscriptions", "last_invoice_id")
    op.drop_column("subscriptions", "last_checkout_session_id")
    op.drop_column("subscriptions", "cancel_at_period_end")
    op.drop_column("subscriptions", "stripe_price_id")
    op.drop_column("subscriptions", "stripe_subscription_id")
    op.drop_column("subscriptions", "stripe_customer_id")
    op.drop_column("subscriptions", "provider")
    op.drop_column("subscriptions", "currency")
