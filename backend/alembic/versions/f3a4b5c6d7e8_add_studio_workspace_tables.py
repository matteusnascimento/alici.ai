"""add_studio_workspace_tables

Revision ID: f3a4b5c6d7e8
Revises: a1b2c3d4e5f6
Create Date: 2026-04-08 00:30:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect


revision: str = "f3a4b5c6d7e8"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    inspector = inspect(op.get_bind())
    return table_name in inspector.get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    inspector = inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return False
    return column_name in {column["name"] for column in inspector.get_columns(table_name)}


def _index_exists(table_name: str, index_name: str) -> bool:
    inspector = inspect(op.get_bind())
    if table_name not in inspector.get_table_names():
        return False
    return index_name in {idx["name"] for idx in inspector.get_indexes(table_name)}


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if not _table_exists(table_name):
        return

    if not _column_exists(table_name, column.name):
        op.add_column(table_name, column)


def _drop_index_if_exists(table_name: str, index_name: str) -> None:
    if _index_exists(table_name, index_name):
        op.drop_index(index_name, table_name=table_name)


def _drop_table_if_exists(table_name: str) -> None:
    if _table_exists(table_name):
        op.drop_table(table_name)


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

    _add_column_if_missing(
        "studio_projects",
        sa.Column("thumbnail_url", sa.String(length=500), nullable=True),
    )
    _add_column_if_missing(
        "studio_projects",
        sa.Column("metadata_json", sa.Text(), nullable=True),
    )

    if not _index_exists("studio_projects", "ix_studio_projects_user_id"):
        op.create_index("ix_studio_projects_user_id", "studio_projects", ["user_id"])

    if not _index_exists("studio_projects", "ix_studio_projects_project_type"):
        op.create_index(
            "ix_studio_projects_project_type",
            "studio_projects",
            ["project_type"],
        )

    if not _table_exists("studio_exports"):
        op.create_table(
            "studio_exports",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "project_id",
                sa.Integer(),
                sa.ForeignKey("studio_projects.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("file_name", sa.String(length=255), nullable=False),
            sa.Column("file_type", sa.String(length=40), nullable=False),
            sa.Column("file_url", sa.String(length=500), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )

    _add_column_if_missing(
        "studio_exports",
        sa.Column("file_name", sa.String(length=255), nullable=True),
    )
    _add_column_if_missing(
        "studio_exports",
        sa.Column("file_type", sa.String(length=40), nullable=True),
    )

    if not _index_exists("studio_exports", "ix_studio_exports_user_id"):
        op.create_index("ix_studio_exports_user_id", "studio_exports", ["user_id"])

    if not _index_exists("studio_exports", "ix_studio_exports_project_id"):
        op.create_index("ix_studio_exports_project_id", "studio_exports", ["project_id"])

    if not _table_exists("brand_assets"):
        op.create_table(
            "brand_assets",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("asset_type", sa.String(length=60), nullable=False),
            sa.Column("title", sa.String(length=180), nullable=False),
            sa.Column("file_url", sa.String(length=500), nullable=False),
            sa.Column("metadata_json", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )

    if not _index_exists("brand_assets", "ix_brand_assets_user_id"):
        op.create_index("ix_brand_assets_user_id", "brand_assets", ["user_id"])

    if not _index_exists("brand_assets", "ix_brand_assets_asset_type"):
        op.create_index("ix_brand_assets_asset_type", "brand_assets", ["asset_type"])

    if not _table_exists("creative_generations"):
        op.create_table(
            "creative_generations",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("tool_type", sa.String(length=60), nullable=False),
            sa.Column("prompt", sa.Text(), nullable=False),
            sa.Column("output_json", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )

    if not _index_exists("creative_generations", "ix_creative_generations_user_id"):
        op.create_index(
            "ix_creative_generations_user_id",
            "creative_generations",
            ["user_id"],
        )

    if not _index_exists("creative_generations", "ix_creative_generations_tool_type"):
        op.create_index(
            "ix_creative_generations_tool_type",
            "creative_generations",
            ["tool_type"],
        )


def downgrade() -> None:
    _drop_index_if_exists("creative_generations", "ix_creative_generations_tool_type")
    _drop_index_if_exists("creative_generations", "ix_creative_generations_user_id")
    _drop_table_if_exists("creative_generations")

    _drop_index_if_exists("brand_assets", "ix_brand_assets_asset_type")
    _drop_index_if_exists("brand_assets", "ix_brand_assets_user_id")
    _drop_table_if_exists("brand_assets")

    _drop_index_if_exists("studio_exports", "ix_studio_exports_project_id")
    _drop_index_if_exists("studio_exports", "ix_studio_exports_user_id")
    _drop_table_if_exists("studio_exports")

    _drop_index_if_exists("studio_projects", "ix_studio_projects_project_type")
    _drop_index_if_exists("studio_projects", "ix_studio_projects_user_id")
    _drop_table_if_exists("studio_projects")