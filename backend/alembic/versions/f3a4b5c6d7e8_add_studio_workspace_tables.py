"""add_studio_workspace_tables

Revision ID: f3a4b5c6d7e8
Revises: a1b2c3d4e5f6
Create Date: 2026-04-08 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "f3a4b5c6d7e8"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS studio_projects (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(180) NOT NULL,
            project_type VARCHAR(60) NOT NULL,
            status VARCHAR(40) NOT NULL DEFAULT 'draft',
            thumbnail_url VARCHAR(500),
            metadata_json TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
        );
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_studio_projects_user_id ON studio_projects (user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_studio_projects_project_type ON studio_projects (project_type);")
    op.execute("ALTER TABLE studio_projects ADD COLUMN IF NOT EXISTS thumbnail_url VARCHAR(500);")
    op.execute("ALTER TABLE studio_projects ADD COLUMN IF NOT EXISTS metadata_json TEXT;")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS studio_exports (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            project_id INTEGER NOT NULL REFERENCES studio_projects(id) ON DELETE CASCADE,
            file_name VARCHAR(255) NOT NULL,
            file_type VARCHAR(40) NOT NULL,
            file_url VARCHAR(500) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
        );
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_studio_exports_user_id ON studio_exports (user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_studio_exports_project_id ON studio_exports (project_id);")
    op.execute("ALTER TABLE studio_exports ADD COLUMN IF NOT EXISTS file_name VARCHAR(255);")
    op.execute("ALTER TABLE studio_exports ADD COLUMN IF NOT EXISTS file_type VARCHAR(40);")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS brand_assets (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            asset_type VARCHAR(60) NOT NULL,
            title VARCHAR(180) NOT NULL,
            file_url VARCHAR(500) NOT NULL,
            metadata_json TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
        );
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_brand_assets_user_id ON brand_assets (user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_brand_assets_asset_type ON brand_assets (asset_type);")

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS creative_generations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            tool_type VARCHAR(60) NOT NULL,
            prompt TEXT NOT NULL,
            output_json TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
        );
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_creative_generations_user_id ON creative_generations (user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_creative_generations_tool_type ON creative_generations (tool_type);")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS creative_generations;")
    op.execute("DROP TABLE IF EXISTS brand_assets;")
    op.execute("DROP TABLE IF EXISTS studio_exports;")
    op.execute("DROP TABLE IF EXISTS studio_projects;")
