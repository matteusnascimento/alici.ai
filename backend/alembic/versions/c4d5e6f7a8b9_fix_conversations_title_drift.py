"""fix conversations title drift

Revision ID: c4d5e6f7a8b9
Revises: 83fa077000f9
Create Date: 2026-04-12 21:22:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4d5e6f7a8b9'
down_revision: Union[str, Sequence[str], None] = '83fa077000f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    tables = set(inspector.get_table_names())
    if 'conversations' not in tables:
        return

    columns = {col['name'] for col in inspector.get_columns('conversations')}
    if 'title' in columns:
        return

    op.add_column('conversations', sa.Column('title', sa.String(length=140), nullable=True))
    op.execute(sa.text("UPDATE conversations SET title = 'Nova conversa' WHERE title IS NULL"))
    op.alter_column('conversations', 'title', existing_type=sa.String(length=140), nullable=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    tables = set(inspector.get_table_names())
    if 'conversations' not in tables:
        return

    columns = {col['name'] for col in inspector.get_columns('conversations')}
    if 'title' in columns:
        op.drop_column('conversations', 'title')
