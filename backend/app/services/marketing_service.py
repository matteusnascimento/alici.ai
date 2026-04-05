from datetime import UTC
import json

from sqlalchemy.orm import Session

from app.models.marketing_project import MarketingProject
from app.models.user import User
from app.schemas.marketing import (
    MarketingCampaignRequest,
    MarketingCampaignResponse,
    MarketingCopyResponse,
    MarketingImagePromptResponse,
    MarketingProjectCreate,
    MarketingProjectRead,
    MarketingTool,
)
from app.services.ai_service import AIService
from app.services.model_router import AIFunction


class MarketingService:
    def __init__(self, db: Session):
        self.db = db
        self.ai = AIService()

    def list_tools(self) -> list[MarketingTool]:
        return [
            MarketingTool(id="copy", name="Copy Generator", description="Gera copy orientada a conversao."),
            MarketingTool(id="image_prompt", name="Image Prompt", description="Cria prompt para geracao de imagem."),
            MarketingTool(id="campaign", name="Campaign Planner", description="Estrutura campanha completa em texto."),
        ]

    def generate(self, payload: MarketingCampaignRequest) -> MarketingCampaignResponse:
        schema = {
            "type": "object",
            "properties": {
                "campaign": {"type": "string"},
                "copy_text": {"type": "string"},
                "cta": {"type": "string"},
                "ad_structure": {"type": "string"},
                "creative_suggestion": {"type": "string"},
            },
            "required": ["campaign", "copy_text", "cta", "ad_structure", "creative_suggestion"],
            "additionalProperties": False,
        }
        result = self.ai.generate_structured_output(
            prompt=(
                f"Empresa: {payload.company_name}\n"
                f"Publico: {payload.audience}\n"
                f"Objetivo: {payload.objective}\n"
                f"Oferta: {payload.offer}\n"
                f"Tom: {payload.tone}"
            ),
            schema=schema,
            system_prompt=(
                "Gere uma campanha de marketing completa em pt-BR. "
                "Retorne somente JSON valido com campanha, copy_text, cta, ad_structure e creative_suggestion."
            ),
            function_name=AIFunction.MARKETING_COPY,
        )
        return MarketingCampaignResponse(**result)

    def generate_copy(self, prompt: str) -> MarketingCopyResponse:
        copy_text = self.ai.generate_text(
            system_prompt="Gere uma copy comercial em pt-BR, direta, com proposta de valor clara e CTA final.",
            user_prompt=f"Contexto: {prompt.strip()}",
            temperature=0.5,
            function_name=AIFunction.MARKETING_COPY,
        )
        return MarketingCopyResponse(copy_text=copy_text)

    def generate_image_prompt(self, prompt: str) -> MarketingImagePromptResponse:
        prompt_text = self.ai.generate_text(
            system_prompt="You write premium prompts for image generation models. Return only one concise prompt in English.",
            user_prompt=f"Create a premium ad image prompt for this context: {prompt.strip() or 'high-conversion SaaS campaign'}",
            temperature=0.5,
            function_name=AIFunction.MARKETING_COPY,
        )
        return MarketingImagePromptResponse(prompt=prompt_text)

    def _parse_campaign_block(self, text: str) -> dict | None:
        sections = {
            "campaign": "",
            "copy": "",
            "cta": "",
            "ad_structure": "",
            "creative_suggestion": "",
        }
        for line in text.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            normalized_key = key.strip().lower()
            if normalized_key in sections:
                sections[normalized_key] = value.strip()

        if all(sections.values()):
            return {
                "campaign": sections["campaign"],
                "copy_text": sections["copy"],
                "cta": sections["cta"],
                "ad_structure": sections["ad_structure"],
                "creative_suggestion": sections["creative_suggestion"],
            }
        return None

    def create_project(self, user: User, payload: MarketingProjectCreate) -> MarketingProjectRead:
        project = MarketingProject(user_id=user.id, **payload.model_dump())
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return MarketingProjectRead(
            id=project.id,
            name=project.name,
            audience=project.audience,
            objective=project.objective,
            offer=project.offer,
            tone=project.tone,
            notes=project.notes,
            created_at=project.created_at.astimezone(UTC).isoformat() if project.created_at else "",
        )

    def list_projects(self, user: User) -> list[MarketingProjectRead]:
        projects = (
            self.db.query(MarketingProject)
            .filter(MarketingProject.user_id == user.id)
            .order_by(MarketingProject.created_at.desc())
            .all()
        )
        return [
            MarketingProjectRead(
                id=item.id,
                name=item.name,
                audience=item.audience,
                objective=item.objective,
                offer=item.offer,
                tone=item.tone,
                notes=item.notes,
                created_at=item.created_at.astimezone(UTC).isoformat() if item.created_at else "",
            )
            for item in projects
        ]
