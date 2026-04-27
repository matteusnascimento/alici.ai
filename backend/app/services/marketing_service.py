from datetime import UTC
import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.marketing_project import MarketingProject
from app.models.user import User
from app.schemas.marketing import (
    MarketingCampaignRequest,
    MarketingCampaignResponse,
    MarketingContentRequest,
    MarketingContentResponse,
    MarketingCopyResponse,
    MarketingImagePromptResponse,
    MarketingProjectCreate,
    MarketingProjectRead,
    MarketingProjectUpdate,
    MarketingTool,
)
from app.services.ai_service import AIService, AIServiceError


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
    def _normalize_content_response(result: dict) -> MarketingContentResponse:
        raw_copies = result.get("copies")
        if isinstance(raw_copies, list):
            copies = [str(item).strip() for item in raw_copies if str(item).strip()]
        elif isinstance(raw_copies, str) and raw_copies.strip():
            copies = [raw_copies.strip()]
        else:
            copies = []

        raw_hashtags = result.get("hashtags")
        if isinstance(raw_hashtags, list):
            hashtags = [str(item).strip() for item in raw_hashtags if str(item).strip()]
        elif isinstance(raw_hashtags, str) and raw_hashtags.strip():
            hashtags = [item.strip() for item in raw_hashtags.split() if item.strip()]
        else:
            hashtags = []

        cta = str(result.get("cta") or "").strip()
        hook = str(result.get("hook") or "").strip()
        if not copies or not cta or not hook:
            raise AIServiceError(
                "Invalid marketing AI response",
                user_message="A IA retornou uma resposta incompleta para marketing.",
                status_code=502,
                code="invalid_ai_response",
            )

        return MarketingContentResponse(
            copies=copies[:3],
            cta=cta,
            hook=hook,
            hashtags=hashtags[:8],
        )

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
            function_name="ad_copy_generator",
        )
        return MarketingCampaignResponse(**result)

    def generate_copy(self, prompt: str) -> MarketingCopyResponse:
        copy_text = self.ai.generate_text(
            system_prompt="Gere uma copy comercial em pt-BR, direta, com proposta de valor clara e CTA final.",
            user_prompt=f"Contexto: {prompt.strip()}",
            temperature=0.5,
            function_name="ad_copy_generator",
        )
        return MarketingCopyResponse(copy_text=copy_text)

    def generate_image_prompt(self, prompt: str) -> MarketingImagePromptResponse:
        prompt_text = self.ai.generate_text(
            system_prompt="You write premium prompts for image generation models. Return only one concise prompt in English.",
            user_prompt=f"Create a premium ad image prompt for this context: {prompt.strip() or 'high-conversion SaaS campaign'}",
            temperature=0.5,
            function_name="social_post_generator",
        )
        return MarketingImagePromptResponse(prompt=prompt_text)

    def generate_content(self, user: User, payload: MarketingContentRequest) -> MarketingContentResponse:
        project = self.db.query(MarketingProject).filter(
            MarketingProject.id == payload.project_id, MarketingProject.user_id == user.id
        ).first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projeto nao encontrado")

        schema = {
            "type": "object",
            "properties": {
                "copies": {"type": "array", "items": {"type": "string"}},
                "cta": {"type": "string"},
                "hook": {"type": "string"},
                "hashtags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["copies", "cta", "hook", "hashtags"],
            "additionalProperties": False,
        }
        result = self.ai.generate_structured_output(
            prompt=(
                f"Projeto: {project.name}\n"
                f"Publico: {project.audience}\n"
                f"Objetivo: {project.objective}\n"
                f"Oferta: {project.offer}\n"
                f"Tom: {project.tone}\n"
                f"Tipo: {payload.type.strip() or 'social_post'}\n"
                f"Contexto: {payload.context.strip()}"
            ),
            schema=schema,
            system_prompt=(
                "Gere conteudo de marketing em pt-BR. "
                "Retorne JSON valido com ate 3 copies, cta, hook e hashtags."
            ),
            function_name="ad_copy_generator",
        )
        return self._normalize_content_response(result)

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
