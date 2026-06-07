"""merge channel and studio heads

Revision ID: 83fa077000f9
Revises: b7c8d9e0f1a2, f3a4b5c6d7e8
Create Date: 2026-04-11 22:47:02.096366
"""

from typing import Sequence, Union


revision: str = "83fa077000f9"
down_revision: Union[str, tuple[str, str], None] = (
    "b7c8d9e0f1a2",
    "f3a4b5c6d7e8",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass