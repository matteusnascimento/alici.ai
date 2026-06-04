"""add premium preferences

Revision ID: d1e2f3a4b5c6
Revises: c6d7e8f9a0b1
Create Date: 2026-06-03 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "d1e2f3a4b5c6"
down_revision = "c6d7e8f9a0b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("user_settings") as batch_op:
        batch_op.add_column(sa.Column("interface_animations", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column("advanced_visual_effects", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column("compact_menus", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column("contextual_tips", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column("confirm_critical_actions", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column("open_last_module", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column("autosave_filters", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column("keyboard_shortcuts", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column("show_quick_metrics", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column("assistant_mode", sa.String(length=30), nullable=False, server_default="automatico"))
        batch_op.add_column(sa.Column("assistant_response_detail", sa.String(length=30), nullable=False, server_default="normais"))
        batch_op.add_column(sa.Column("assistant_tone", sa.String(length=30), nullable=False, server_default="profissional"))


def downgrade() -> None:
    with op.batch_alter_table("user_settings") as batch_op:
        batch_op.drop_column("assistant_tone")
        batch_op.drop_column("assistant_response_detail")
        batch_op.drop_column("assistant_mode")
        batch_op.drop_column("show_quick_metrics")
        batch_op.drop_column("keyboard_shortcuts")
        batch_op.drop_column("autosave_filters")
        batch_op.drop_column("open_last_module")
        batch_op.drop_column("confirm_critical_actions")
        batch_op.drop_column("contextual_tips")
        batch_op.drop_column("compact_menus")
        batch_op.drop_column("advanced_visual_effects")
        batch_op.drop_column("interface_animations")
