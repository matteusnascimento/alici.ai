"""add premium preferences

Revision ID: d1e2f3a4b5c6
Revises: c6d7e8f9a0b1
Create Date: 2026-06-03 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "d1e2f3a4b5c6"
down_revision = "c6d7e8f9a0b1"
branch_labels = None
depends_on = None


PREFERENCE_COLUMN_NAMES = [
    "interface_animations",
    "advanced_visual_effects",
    "compact_menus",
    "contextual_tips",
    "confirm_critical_actions",
    "open_last_module",
    "autosave_filters",
    "keyboard_shortcuts",
    "show_quick_metrics",
    "assistant_mode",
    "assistant_response_detail",
    "assistant_tone",
]


def _table_exists(table_name: str) -> bool:
    inspector = inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    if not _table_exists(table_name):
        return False

    inspector = inspect(op.get_bind())
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _build_column(column_name: str) -> sa.Column:
    boolean_defaults = {
        "interface_animations": sa.true(),
        "advanced_visual_effects": sa.true(),
        "compact_menus": sa.false(),
        "contextual_tips": sa.true(),
        "confirm_critical_actions": sa.true(),
        "open_last_module": sa.true(),
        "autosave_filters": sa.true(),
        "keyboard_shortcuts": sa.true(),
        "show_quick_metrics": sa.true(),
    }
    string_defaults = {
        "assistant_mode": "automatico",
        "assistant_response_detail": "normais",
        "assistant_tone": "profissional",
    }

    if column_name in boolean_defaults:
        return sa.Column(column_name, sa.Boolean(), nullable=False, server_default=boolean_defaults[column_name])
    return sa.Column(column_name, sa.String(length=30), nullable=False, server_default=string_defaults[column_name])


def upgrade() -> None:
    for column_name in PREFERENCE_COLUMN_NAMES:
        if not _column_exists("user_settings", column_name):
            with op.batch_alter_table("user_settings") as batch_op:
                batch_op.add_column(_build_column(column_name))


def downgrade() -> None:
    for column_name in reversed(PREFERENCE_COLUMN_NAMES):
        if _column_exists("user_settings", column_name):
            with op.batch_alter_table("user_settings") as batch_op:
                batch_op.drop_column(column_name)
