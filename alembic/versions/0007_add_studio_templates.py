"""add studio templates

Revision ID: 0007_add_studio_templates
Revises: 0006_add_business_modules
Create Date: 2026-05-28
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0007_add_studio_templates"
down_revision = "0006_add_business_modules"
branch_labels = None
depends_on = None


json_type = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.create_table(
        "templates",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("thumbnail_url", sa.Text(), nullable=True),
        sa.Column("preview_video_url", sa.Text(), nullable=True),
        sa.Column("template_json", json_type, nullable=False),
        sa.Column("premium", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_table(
        "template_assets",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("template_id", sa.Text(), nullable=False),
        sa.Column("asset_type", sa.Text(), nullable=False),
        sa.Column("asset_url", sa.Text(), nullable=False),
        sa.Column("metadata", json_type, nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["template_id"], ["templates.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_templates_category_type", "templates", ["category", "type", "is_active"])
    op.create_index("idx_template_assets_template", "template_assets", ["template_id", "asset_type"])

    templates_table = sa.table(
        "templates",
        sa.column("id", sa.Text()),
        sa.column("name", sa.Text()),
        sa.column("category", sa.Text()),
        sa.column("type", sa.Text()),
        sa.column("thumbnail_url", sa.Text()),
        sa.column("preview_video_url", sa.Text()),
        sa.column("template_json", json_type),
        sa.column("premium", sa.Boolean()),
        sa.column("is_active", sa.Boolean()),
    )
    op.bulk_insert(
        templates_table,
        [
            {
                "id": "hotel-story-offer",
                "name": "Story Pousada Premium",
                "category": "Hotelaria",
                "type": "social",
                "thumbnail_url": None,
                "preview_video_url": None,
                "premium": False,
                "is_active": True,
                "template_json": {
                    "canvas": {"width": 1080, "height": 1920, "background": "#06111f"},
                    "prompt": "Story vertical para pousada tropical com oferta, prova social e CTA para WhatsApp.",
                    "duration": 15,
                    "mode": "video",
                    "layers": [
                        {"id": "hotel-bg", "name": "Fundo visual", "kind": "shape", "visible": True, "locked": False, "opacity": 1, "blendMode": "normal", "x": 70, "y": 48, "width": 580, "height": 445, "rotation": 0, "color": "#124055", "start": 0, "duration": 15, "editable": True, "effects": ["cinematic", "warm"]},
                        {"id": "hotel-title", "name": "Titulo da oferta", "kind": "text", "visible": True, "locked": False, "opacity": 1, "blendMode": "normal", "x": 115, "y": 140, "width": 500, "height": 80, "rotation": 0, "text": "Fim de semana perfeito", "color": "#FFFFFF", "fontSize": 46, "fontFamily": "Inter", "start": 0, "duration": 12, "editable": True},
                        {"id": "hotel-cta", "name": "CTA WhatsApp", "kind": "text", "visible": True, "locked": False, "opacity": 1, "blendMode": "normal", "x": 168, "y": 405, "width": 390, "height": 58, "rotation": 0, "text": "Chamar no WhatsApp", "color": "#FF6A00", "fontSize": 30, "fontFamily": "Inter", "start": 10, "duration": 5, "editable": True},
                    ],
                    "clips": [
                        {"id": "hotel-clip-bg", "layerId": "hotel-bg", "track": "video", "label": "Cena principal", "start": 0, "duration": 15},
                        {"id": "hotel-clip-title", "layerId": "hotel-title", "track": "text", "label": "Hook", "start": 0, "duration": 12},
                        {"id": "hotel-clip-cta", "layerId": "hotel-cta", "track": "overlay", "label": "CTA final", "start": 10, "duration": 5},
                    ],
                    "assets": [],
                    "animations": [{"layer_id": "hotel-title", "property": "y", "keyframes": [{"time": 0, "value": 170}, {"time": 0.8, "value": 140}]}],
                    "fonts": [{"family": "Inter", "weight": 800}],
                    "audio": [{"id": "hotel-beat", "label": "Beat leve tropical", "start": 0, "duration": 15, "role": "background"}],
                    "editable_regions": [
                        {"layer_id": "hotel-title", "label": "Titulo", "kind": "text"},
                        {"layer_id": "hotel-cta", "label": "CTA", "kind": "cta"},
                        {"layer_id": "hotel-bg", "label": "Cor ou imagem de fundo", "kind": "color"},
                    ],
                },
            },
            {
                "id": "product-launch-reel",
                "name": "Reels Lancamento",
                "category": "Marketing",
                "type": "video",
                "thumbnail_url": None,
                "preview_video_url": None,
                "premium": False,
                "is_active": True,
                "template_json": {
                    "canvas": {"width": 1080, "height": 1920, "background": "#050816"},
                    "prompt": "Video curto de lancamento com hook forte, tres beneficios e CTA direto.",
                    "duration": 15,
                    "mode": "video",
                    "layers": [
                        {"id": "reel-bg", "name": "Fundo campanha", "kind": "shape", "visible": True, "locked": False, "opacity": 1, "blendMode": "normal", "x": 78, "y": 58, "width": 560, "height": 430, "rotation": 0, "color": "#111827", "start": 0, "duration": 15, "editable": True, "effects": ["neon", "contrast"]},
                        {"id": "reel-hook", "name": "Hook", "kind": "text", "visible": True, "locked": False, "opacity": 1, "blendMode": "normal", "x": 112, "y": 105, "width": 500, "height": 96, "rotation": 0, "text": "Pare de perder clientes", "color": "#00F0FF", "fontSize": 42, "fontFamily": "Inter", "start": 0, "duration": 4, "editable": True},
                        {"id": "reel-cta", "name": "CTA", "kind": "text", "visible": True, "locked": False, "opacity": 1, "blendMode": "normal", "x": 162, "y": 410, "width": 400, "height": 58, "rotation": 0, "text": "Teste a AXI agora", "color": "#FF6A00", "fontSize": 31, "fontFamily": "Inter", "start": 11, "duration": 4, "editable": True},
                    ],
                    "clips": [
                        {"id": "reel-bg-clip", "layerId": "reel-bg", "track": "video", "label": "Base", "start": 0, "duration": 15},
                        {"id": "reel-hook-clip", "layerId": "reel-hook", "track": "text", "label": "Hook", "start": 0, "duration": 4},
                        {"id": "reel-cta-clip", "layerId": "reel-cta", "track": "overlay", "label": "CTA", "start": 11, "duration": 4},
                    ],
                    "assets": [],
                    "animations": [{"layer_id": "reel-cta", "property": "scale", "keyframes": [{"time": 11, "value": 0.92}, {"time": 11.4, "value": 1}]}],
                    "fonts": [{"family": "Inter", "weight": 900}],
                    "audio": [{"id": "reel-impact", "label": "Beat impacto", "start": 0, "duration": 15, "role": "background"}],
                    "editable_regions": [
                        {"layer_id": "reel-hook", "label": "Hook", "kind": "text"},
                        {"layer_id": "reel-cta", "label": "CTA", "kind": "cta"},
                    ],
                },
            },
        ],
    )


def downgrade() -> None:
    op.drop_index("idx_template_assets_template", table_name="template_assets")
    op.drop_index("idx_templates_category_type", table_name="templates")
    op.drop_table("template_assets")
    op.drop_table("templates")
