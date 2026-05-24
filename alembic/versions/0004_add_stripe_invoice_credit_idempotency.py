"""add stripe invoice credit idempotency"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op


revision: str = "0004_add_stripe_invoice_credit_idempotency"
down_revision: Union[str, None] = "0003_extend_generation_jobs_for_arq"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_credit_stripe_invoice_grant
        ON credit_transactions (job_id, reason, type)
        WHERE job_id IS NOT NULL
          AND type = 'grant'
          AND reason = 'stripe_invoice_payment_succeeded'
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_credit_stripe_invoice_grant")

