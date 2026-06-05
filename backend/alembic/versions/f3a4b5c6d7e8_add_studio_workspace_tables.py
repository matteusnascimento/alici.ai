"""add_studio_workspace_tables

Revision ID: f3a4b5c6d7e8
Revises: a1b2c3d4e5f6
Create Date: 2026-04-08 00:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f3a4b5c6d7e8"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return column_name in {col["name"] for col in inspector.get_columns(table_name)}


def _timestamp_column(name: str, nullable: bool = False) -> sa.Column:
    bind = op.get_bind()
    dialect = bind.dialect.name
    column_type = sa.DateTime(timezone=True) if dialect != "sqlite" else sa.DateTime()
    server_default = sa.text("now()") if dialect != "sqlite" else sa.text("CURRENT_TIMESTAMP")
    return sa.Column(name, column_type, nullable=nullable, server_default=server_default)


def _add_column_if_missing(table_name: str, column: sa.Column) -> None:
    if _column_exists(table_name, column.name):
        return
    op.add_column(table_name, column)


def _create_studio_projects() -> None:
    if _table_exists("studio_projects"):
        _add_column_if_missing("studio_projects", sa.Column("thumbnail_url", sa.String(length=500), nullable=True))
        _add_column_if_missing("studio_projects", sa.Column("metadata_json", sa.Text(), nullable=True))
        return

    op.create_table(
        "studio_projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("project_type", sa.String(length=60), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'draft'")),
        sa.Column("thumbnail_url", sa.String(length=500), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        _timestamp_column("created_at", nullable=False),
        _timestamp_column("updated_at", nullable=False),
    )
    op.create_index("ix_studio_projects_user_id", "studio_projects", ["user_id"])
    op.create_index("ix_studio_projects_project_type", "studio_projects", ["project_type"])


def _create_studio_exports() -> None:
    if _table_exists("studio_exports"):
        _add_column_if_missing("studio_exports", sa.Column("file_name", sa.String(length=255), nullable=True))
        _add_column_if_missing("studio_exports", sa.Column("file_type", sa.String(length=40), nullable=True))
        return

    op.create_table(
        "studio_exports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("studio_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=40), nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=False),
        _timestamp_column("created_at", nullable=False),
    )
    op.create_index("ix_studio_exports_user_id", "studio_exports", ["user_id"])
    op.create_index("ix_studio_exports_project_id", "studio_exports", ["project_id"])


def _create_brand_assets() -> None:
    if _table_exists("brand_assets"):
        return

    op.create_table(
        "brand_assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("asset_type", sa.String(length=60), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        _timestamp_column("created_at", nullable=False),
    )
    op.create_index("ix_brand_assets_user_id", "brand_assets", ["user_id"])
    op.create_index("ix_brand_assets_asset_type", "brand_assets", ["asset_type"])


def _create_creative_generations() -> None:
    if _table_exists("creative_generations"):
        return

    op.create_table(
        "creative_generations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tool_type", sa.String(length=60), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("output_json", sa.Text(), nullable=True),
        _timestamp_column("created_at", nullable=False),
    )
    op.create_index("ix_creative_generations_user_id", "creative_generations", ["user_id"])
    op.create_index("ix_creative_generations_tool_type", "creative_generations", ["tool_type"])


def upgrade() -> None:
    _create_studio_projects()
    _create_studio_exports()
    _create_brand_assets()
    _create_creative_generations()


def downgrade() -> None:
    op.drop_table("creative_generations")
    op.drop_table("brand_assets")
    op.drop_table("studio_exports")
    op.drop_table("studio_projects")
