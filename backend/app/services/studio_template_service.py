from __future__ import annotations

import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.studio_project import StudioProject
from app.models.studio_template import StudioTemplate
from app.models.user import User
from app.services.envato_template_provider import EnvatoTemplateProvider, EnvatoTemplateProviderError


class StudioTemplateService:
    def __init__(self, db: Session):
        self.db = db
        self.envato_provider = EnvatoTemplateProvider()

    def ensure_seed_templates(self) -> None:
        count = self.db.query(StudioTemplate).count()
        if count > 0:
            return

        seeds = [
            StudioTemplate(
                user_id=None,
                name="Poster Neon Conversao",
                category="poster",
                style_tag="neon",
                template_data_json=json.dumps({"layout": "hero-left", "ratio": "1:1"}, ensure_ascii=True),
                preview_url=None,
                is_public=True,
            ),
            StudioTemplate(
                user_id=None,
                name="Story Premium Motion",
                category="story",
                style_tag="cinematic",
                template_data_json=json.dumps({"layout": "vertical-stack", "ratio": "9:16"}, ensure_ascii=True),
                preview_url=None,
                is_public=True,
            ),
            StudioTemplate(
                user_id=None,
                name="Banner Performance",
                category="banner",
                style_tag="clean",
                template_data_json=json.dumps({"layout": "horizontal-split", "ratio": "16:9"}, ensure_ascii=True),
                preview_url=None,
                is_public=True,
            ),
        ]
        self.db.add_all(seeds)
        self.db.commit()

    def list_templates(self, user: User) -> list[StudioTemplate]:
        self.ensure_seed_templates()
        if settings.is_studio_template_provider_configured("envato"):
            self.sync_envato_templates()
        return (
            self.db.query(StudioTemplate)
            .filter((StudioTemplate.user_id == user.id) | (StudioTemplate.is_public.is_(True)))
            .order_by(StudioTemplate.created_at.desc())
            .all()
        )

    def sync_envato_templates(self) -> None:
        try:
            envato_templates = self.envato_provider.search_templates()
        except EnvatoTemplateProviderError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

        changed = False
        for item in envato_templates:
            existing = self._find_envato_template(item["source_id"])
            template_data_json = json.dumps(item["template_data"], ensure_ascii=True)
            if existing:
                existing.name = item["name"]
                existing.category = item["category"]
                existing.style_tag = item["style_tag"]
                existing.preview_url = item["preview_url"]
                existing.template_data_json = template_data_json
            else:
                self.db.add(
                    StudioTemplate(
                        user_id=None,
                        name=item["name"],
                        category=item["category"],
                        style_tag=item["style_tag"],
                        template_data_json=template_data_json,
                        preview_url=item["preview_url"],
                        is_public=True,
                    )
                )
            changed = True

        if changed:
            self.db.commit()

    def _find_envato_template(self, source_id: str) -> StudioTemplate | None:
        candidates = (
            self.db.query(StudioTemplate)
            .filter(StudioTemplate.user_id.is_(None), StudioTemplate.is_public.is_(True))
            .all()
        )
        for template in candidates:
            try:
                payload = json.loads(template.template_data_json or "{}")
            except json.JSONDecodeError:
                continue
            if payload.get("source") == "envato" and str(payload.get("source_id")) == source_id:
                return template
        return None

    def apply_template(self, user: User, template_id: int, project_id: int) -> StudioProject:
        template = self.db.query(StudioTemplate).filter(StudioTemplate.id == template_id).first()
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

        project = self.db.query(StudioProject).filter(StudioProject.id == project_id, StudioProject.user_id == user.id).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        payload = json.loads(template.template_data_json)
        project.canvas_data_json = json.dumps(payload, ensure_ascii=True)
        project.metadata_json = json.dumps({"template": template.name, "style": template.style_tag}, ensure_ascii=True)
        self.db.commit()
        self.db.refresh(project)
        return project
