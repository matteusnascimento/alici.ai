from datetime import UTC

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


class MarketingService:
    def __init__(self, db: Session):
        self.db = db

    def list_tools(self) -> list[MarketingTool]:
        return [
            MarketingTool(id="copy", name="Copy Generator", description="Gera copy orientada a conversao."),
            MarketingTool(id="image_prompt", name="Image Prompt", description="Cria prompt para geracao de imagem."),
            MarketingTool(id="campaign", name="Campaign Planner", description="Estrutura campanha completa em texto."),
        ]

    def generate(self, payload: MarketingCampaignRequest) -> MarketingCampaignResponse:
        campaign = (
            f"Campanha {payload.objective} para {payload.company_name}: posicionar a oferta '{payload.offer}' "
            f"para o público {payload.audience} com tom {payload.tone}."
        )
        copy = (
            f"{payload.company_name} entrega uma forma mais rápida de {payload.objective.lower()} para {payload.audience}. "
            f"A oferta central é {payload.offer}, com comunicação {payload.tone} e foco em clareza, urgência e prova."
        )
        cta = f"Quero ativar {payload.offer} agora"
        ad_structure = (
            "Hook de dor -> prova social -> mecanismo único -> oferta -> urgência -> CTA. "
            f"Abra com uma promessa curta sobre {payload.objective.lower()} e feche convidando o lead a falar com a AXI."
        )
        creative_suggestion = (
            f"Use visual limpo, contraste alto e demonstração do resultado final para {payload.audience}. "
            "Combine screenshot do painel com headline curta e selo de automação inteligente."
        )
        return MarketingCampaignResponse(
            campaign=campaign,
            copy_text=copy,
            cta=cta,
            ad_structure=ad_structure,
            creative_suggestion=creative_suggestion,
        )

    def generate_copy(self, prompt: str) -> MarketingCopyResponse:
        return MarketingCopyResponse(
            copy_text=(
                "Oferta AXI para acelerar resultado comercial:\n"
                f"{prompt.strip()}\n"
                "Mensagem principal: clareza de proposta, prova de resultado e CTA unico para conversa."
            )
        )

    def generate_image_prompt(self, prompt: str) -> MarketingImagePromptResponse:
        normalized = prompt.strip() or "campanha de alta conversao para SaaS"
        return MarketingImagePromptResponse(
            prompt=(
                "Create a premium ad visual, cinematic light, modern SaaS dashboard,"
                f" focus on {normalized}, high contrast, realistic, 4k, clean typography"
            )
        )

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
