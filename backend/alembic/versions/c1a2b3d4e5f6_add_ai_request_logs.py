"""add_ai_request_logs

Revision ID: c1a2b3d4e5f6
Revises: b9f1c2d3e4f5
Create Date: 2026-04-12 22:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c1a2b3d4e5f6"
down_revision: Union[str, None] = "b9f1c2d3e4f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ai_request_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("agent_id", sa.Integer(), nullable=True),
        sa.Column("endpoint", sa.String(length=120), nullable=True),
        sa.Column("task_name", sa.String(length=60), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("model", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=False),
        sa.Column("output_tokens", sa.Integer(), nullable=False),
        sa.Column("total_tokens", sa.Integer(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("error_summary", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_request_logs_id", "ai_request_logs", ["id"], unique=False)
    op.create_index("ix_ai_request_logs_user_id", "ai_request_logs", ["user_id"], unique=False)
    op.create_index("ix_ai_request_logs_agent_id", "ai_request_logs", ["agent_id"], unique=False)
    op.create_index("ix_ai_request_logs_task_name", "ai_request_logs", ["task_name"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ai_request_logs_task_name", table_name="ai_request_logs")
    op.drop_index("ix_ai_request_logs_agent_id", table_name="ai_request_logs")
    op.drop_index("ix_ai_request_logs_user_id", table_name="ai_request_logs")
    op.drop_index("ix_ai_request_logs_id", table_name="ai_request_logs")
    op.drop_table("ai_request_logs")
