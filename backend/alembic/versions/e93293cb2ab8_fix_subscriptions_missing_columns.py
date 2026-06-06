"""fix_subscriptions_missing_columns

Revision ID: e93293cb2ab8
Revises: e51abfb3c70f
Create Date: 2026-04-07 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e93293cb2ab8'
down_revision: Union[str, None] = 'e51abfb3c70f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add missing columns to subscriptions table."""
    # Check if columns exist before adding
    # Note: PostgreSQL doesn't have a simple IF NOT EXISTS for ALTER TABLE ADD COLUMN
    # We'll use raw SQL to handle this safely
    
    # Add created_at if it doesn't exist
    op.execute('''
        ALTER TABLE subscriptions
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL;
    ''')
    
    # Add updated_at if it doesn't exist
    op.execute('''
        ALTER TABLE subscriptions
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL;
    ''')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('subscriptions', 'updated_at')
    op.drop_column('subscriptions', 'created_at')
