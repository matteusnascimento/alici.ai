from datetime import UTC
import json

from fastapi import HTTPException, status
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
    MarketingProjectUpdate,
    MarketingTool,
)
from app.services.ai_service import AIService
from app.services.ai_service import AIServiceError


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

    @staticmethod
    def _can_fallback(exc: AIServiceError) -> bool:
        return exc.is_retryable_platform_issue

    @staticmethod
    def _campaign_fallback(payload: MarketingCampaignRequest) -> MarketingCampaignResponse:
        return MarketingCampaignResponse(
            campaign=f"Campanha base para {payload.company_name}",
            copy_text=(
                f"{payload.offer} para {payload.audience}. Destaque a proposta principal e convide o lead a falar com o time."
            ),
            cta="Fale com nossa equipe e receba sua proposta personalizada.",
            ad_structure="Gancho inicial, beneficio central, prova rapida e CTA final.",
            creative_suggestion=f"Visual limpo com foco em {payload.offer} e linguagem {payload.tone}.",
        )

    @staticmethod
    def _copy_fallback(prompt: str) -> MarketingCopyResponse:
        return MarketingCopyResponse(copy_text=f"Mensagem base: {prompt.strip() or 'Apresente a oferta com clareza e CTA final.'}")

    @staticmethod
    def _image_prompt_fallback(prompt: str) -> MarketingImagePromptResponse:
        return MarketingImagePromptResponse(prompt=f"Premium marketing visual, clean layout, strong offer focus, context: {prompt.strip() or 'campaign creative'}")

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
        try:
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
                function_name="ad_copy_generator",
            )
        except AIServiceError as exc:
            if self._can_fallback(exc):
                return self._campaign_fallback(payload)
            raise
        return MarketingCampaignResponse(**result)

    def generate_copy(self, prompt: str) -> MarketingCopyResponse:
        try:
            copy_text = self.ai.generate_text(
                system_prompt="Gere uma copy comercial em pt-BR, direta, com proposta de valor clara e CTA final.",
                user_prompt=f"Contexto: {prompt.strip()}",
                temperature=0.5,
                function_name="ad_copy_generator",
            )
        except AIServiceError as exc:
            if self._can_fallback(exc):
                return self._copy_fallback(prompt)
            raise
        return MarketingCopyResponse(copy_text=copy_text)

    def generate_image_prompt(self, prompt: str) -> MarketingImagePromptResponse:
        try:
            prompt_text = self.ai.generate_text(
                system_prompt="You write premium prompts for image generation models. Return only one concise prompt in English.",
                user_prompt=f"Create a premium ad image prompt for this context: {prompt.strip() or 'high-conversion SaaS campaign'}",
                temperature=0.5,
                function_name="social_post_generator",
            )
        except AIServiceError as exc:
            if self._can_fallback(exc):
                return self._image_prompt_fallback(prompt)
            raise
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

    def get_project(self, user: User, project_id: int) -> MarketingProjectRead:
        project = self.db.query(MarketingProject).filter(
            MarketingProject.id == project_id, MarketingProject.user_id == user.id
        ).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto nao encontrado")
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

    def update_project(self, user: User, project_id: int, payload: MarketingProjectUpdate) -> MarketingProjectRead:
        project = self.db.query(MarketingProject).filter(
            MarketingProject.id == project_id, MarketingProject.user_id == user.id
        ).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto nao encontrado")
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(project, field, value)
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

    def delete_project(self, user: User, project_id: int) -> None:
        project = self.db.query(MarketingProject).filter(
            MarketingProject.id == project_id, MarketingProject.user_id == user.id
        ).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto nao encontrado")
        self.db.delete(project)
        self.db.commit()

    def generate_for_project(self, user: User, project_id: int) -> MarketingCampaignResponse:
        project = self.db.query(MarketingProject).filter(
            MarketingProject.id == project_id, MarketingProject.user_id == user.id
        ).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto nao encontrado")
        req = MarketingCampaignRequest(
            company_name=project.name,
            audience=project.audience,
            objective=project.objective,
            offer=project.offer,
            tone=project.tone,
        )
        return self.generate(req)
