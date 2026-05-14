"""merge multiple heads

Revision ID: f0e1d2c3b4a5
Revises: c1a2b3d4e5f6, d2f4a8c9b1e7
Create Date: 2026-04-13 03:28:29.891000

"""
from typing import Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0e1d2c3b4a5'
down_revision: Union[str, tuple] = ('c1a2b3d4e5f6', 'd2f4a8c9b1e7')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
