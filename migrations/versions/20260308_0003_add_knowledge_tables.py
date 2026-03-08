"""add knowledge base tables

Revision ID: 20260308_0003
Revises: 20260308_0002
Create Date: 2026-03-08 12:40:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260308_0003"
down_revision: Union[str, None] = "20260308_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_knowledge_documents",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("file_type", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("total_chunks", sa.Integer(), nullable=True, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["platform_organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["platform_users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_platform_knowledge_documents_id"),
        "platform_knowledge_documents",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_platform_knowledge_documents_user_id"),
        "platform_knowledge_documents",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_platform_knowledge_documents_organization_id"),
        "platform_knowledge_documents",
        ["organization_id"],
        unique=False,
    )

    op.create_table(
        "platform_knowledge_chunks",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("document_id", sa.String(), nullable=False),
        sa.Column("organization_id", sa.String(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["document_id"], ["platform_knowledge_documents.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["platform_organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_platform_knowledge_chunks_id"),
        "platform_knowledge_chunks",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_platform_knowledge_chunks_document_id"),
        "platform_knowledge_chunks",
        ["document_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_platform_knowledge_chunks_organization_id"),
        "platform_knowledge_chunks",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_platform_knowledge_chunks_organization_id"), table_name="platform_knowledge_chunks")
    op.drop_index(op.f("ix_platform_knowledge_chunks_document_id"), table_name="platform_knowledge_chunks")
    op.drop_index(op.f("ix_platform_knowledge_chunks_id"), table_name="platform_knowledge_chunks")
    op.drop_table("platform_knowledge_chunks")

    op.drop_index(op.f("ix_platform_knowledge_documents_organization_id"), table_name="platform_knowledge_documents")
    op.drop_index(op.f("ix_platform_knowledge_documents_user_id"), table_name="platform_knowledge_documents")
    op.drop_index(op.f("ix_platform_knowledge_documents_id"), table_name="platform_knowledge_documents")
    op.drop_table("platform_knowledge_documents")
