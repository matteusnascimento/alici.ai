"""add studio projects

Revision ID: f3a4b5c6d7e8
Revises: e93293cb2ab8
Create Date: 2026-04-11 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect


revision: str = "f3a4b5c6d7e8"
down_revision: Union[str, None] = "e93293cb2ab8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    inspector = inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _index_exists(table_name: str, index_name: str) -> bool:
    inspector = inspect(op.get_bind())

    if table_name not in inspector.get_table_names():
        return False

    return index_name in {idx["name"] for idx in inspector.get_indexes(table_name)}


def upgrade() -> None:
    if not _table_exists("studio_projects"):
        op.create_table(
            "studio_projects",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("project_type", sa.String(length=60), nullable=False),
            sa.Column(
                "status",
                sa.String(length=40),
                nullable=False,
                server_default="draft",
            ),
            sa.Column("thumbnail_url", sa.String(length=500), nullable=True),
            sa.Column("metadata_json", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )

    if not _index_exists("studio_projects", "ix_studio_projects_user_id"):
        op.create_index(
            "ix_studio_projects_user_id",
            "studio_projects",
            ["user_id"],
        )

    if not _index_exists("studio_projects", "ix_studio_projects_project_type"):
        op.create_index(
            "ix_studio_projects_project_type",
            "studio_projects",
            ["project_type"],
        )

    if not _index_exists("studio_projects", "ix_studio_projects_status"):
        op.create_index(
            "ix_studio_projects_status",
            "studio_projects",
            ["status"],
        )


def downgrade() -> None:
    if _index_exists("studio_projects", "ix_studio_projects_status"):
        op.drop_index("ix_studio_projects_status", table_name="studio_projects")

    if _index_exists("studio_projects", "ix_studio_projects_project_type"):
        op.drop_index("ix_studio_projects_project_type", table_name="studio_projects")

    if _index_exists("studio_projects", "ix_studio_projects_user_id"):
        op.drop_index("ix_studio_projects_user_id", table_name="studio_projects")

    if _table_exists("studio_projects"):
        op.drop_table("studio_projects")