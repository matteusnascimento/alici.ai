from __future__ import annotations

import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.studio_project import StudioProject
from app.models.studio_template import StudioTemplate
from app.models.user import User


class StudioTemplateService:
    def __init__(self, db: Session):
        self.db = db

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
        return (
            self.db.query(StudioTemplate)
            .filter((StudioTemplate.user_id == user.id) | (StudioTemplate.is_public.is_(True)))
            .order_by(StudioTemplate.created_at.desc())
            .all()
        )

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
