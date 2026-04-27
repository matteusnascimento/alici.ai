from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.studio import (
    StudioAdCreateRequest,
    StudioCreativeCreateRequest,
    StudioGenerateResponse,
    StudioProjectCreate,
    StudioProjectRead,
    StudioToolActionResponse,
)
from app.services.ai_service import AIServiceError
from app.services.studio_generation_service import StudioGenerationService
from app.services.studio_project_service import StudioProjectService


class CreativeGenerationService:
    def __init__(self, db: Session):
        self.db = db
        self.projects = StudioProjectService(db)
        self.generation = StudioGenerationService(db)

    def _project_to_read(self, project) -> StudioProjectRead:
        from app.api.routes.studio import _project_read

        return _project_read(project)

    def _create_base_project(self, user: User, project_type: str, title: str, metadata: dict[str, Any]) -> Any:
        return self.projects.create_project(
            user,
            StudioProjectCreate(
                project_type=project_type,
                title=title,
                metadata=metadata,
                canvas_data={},
                layers=[],
                timeline_data={},
                export_settings={"format": "png"},
            ),
        )

    def create_poster(self, user: User, payload: StudioCreativeCreateRequest) -> StudioToolActionResponse:
        project = self._create_base_project(
            user,
            "poster",
            payload.title or "Novo Poster",
            {
                **payload.metadata,
                "prompt": payload.prompt,
                "template_id": payload.template_id,
                "upload_urls": payload.upload_urls,
            },
        )
        generation_response: StudioGenerateResponse | None = None
        if payload.prompt:
            result = self.generation.generate_poster_variations(payload.prompt, {"style": "poster"})
            generated = self.generation.create_generation(
                user_id=user.id,
                project_id=project.id,
                generation_type="poster",
                prompt=payload.prompt,
                input_payload=payload.model_dump(),
                result_payload=result,
            )
            generation_response = StudioGenerateResponse(
                generation_id=generated.id,
                status=generated.status,
                result=result,
            )
        return StudioToolActionResponse(project=self._project_to_read(project), generation=generation_response, message="Projeto de poster criado com sucesso.")

    def create_story(self, user: User, payload: StudioCreativeCreateRequest) -> StudioToolActionResponse:
        project = self._create_base_project(
            user,
            "story",
            payload.title or "Novo Story 9:16",
            {
                **payload.metadata,
                "ratio": "9:16",
                "prompt": payload.prompt,
                "template_id": payload.template_id,
            },
        )
        generation_response: StudioGenerateResponse | None = None
        if payload.prompt:
            result = self.generation.generate_poster_variations(payload.prompt, {"style": "story", "ratio": "9:16"})
            generated = self.generation.create_generation(
                user_id=user.id,
                project_id=project.id,
                generation_type="story",
                prompt=payload.prompt,
                input_payload=payload.model_dump(),
                result_payload=result,
            )
            generation_response = StudioGenerateResponse(
                generation_id=generated.id,
                status=generated.status,
                result=result,
            )
        return StudioToolActionResponse(project=self._project_to_read(project), generation=generation_response, message="Story criado com canvas vertical pronto para edicao.")

    def create_ad(self, user: User, payload: StudioAdCreateRequest) -> StudioToolActionResponse:
        prompt = payload.prompt or (
            f"Produto: {payload.product}; Oferta: {payload.offer}; Publico: {payload.audience}; Canal: {payload.channel}"
        )
        project = self._create_base_project(
            user,
            "ad",
            payload.title or f"Anuncio {payload.product}",
            {
                **payload.metadata,
                "product": payload.product,
                "offer": payload.offer,
                "audience": payload.audience,
                "channel": payload.channel,
            },
        )
        copy_result = self.generation.generate_copy(prompt, "ad-copy")
        visual_result = self.generation.generate_poster_variations(prompt, {"style": "ad", "channel": payload.channel})
        merged_result = {"copy": copy_result, "visual": visual_result}
        generated = self.generation.create_generation(
            user_id=user.id,
            project_id=project.id,
            generation_type="ad",
            prompt=prompt,
            input_payload=payload.model_dump(),
            result_payload=merged_result,
        )
        generation_response = StudioGenerateResponse(
            generation_id=generated.id,
            status=generated.status,
            result=merged_result,
        )
        return StudioToolActionResponse(project=self._project_to_read(project), generation=generation_response, message="Campanha base criada com copy e visual inicial por IA.")

    def create_video(self, user: User, payload: StudioCreativeCreateRequest) -> StudioToolActionResponse:
        project = self._create_base_project(
            user,
            "video",
            payload.title or "Novo Video",
            {
                **payload.metadata,
                "prompt": payload.prompt,
                "template_id": payload.template_id,
                "upload_urls": payload.upload_urls,
            },
        )
        return StudioToolActionResponse(
            project=self._project_to_read(project),
            generation=None,
            message="Workspace de video criado. A geracao/renderizacao real ainda precisa ser configurada.",
        )

    def generate_caption(
        self,
        user: User,
        *,
        project_id: int | None,
        campaign_context: str,
        channel: str,
        tone: str,
        include_cta: bool,
        include_hashtags: bool,
        variations: int,
    ) -> StudioGenerateResponse:
        mode = f"caption-{channel}-{tone}-v{variations}"
        prompt = (
            f"Contexto: {campaign_context}\n"
            f"Canal: {channel}\nTom: {tone}\n"
            f"Incluir CTA: {'sim' if include_cta else 'nao'}\n"
            f"Incluir hashtags: {'sim' if include_hashtags else 'nao'}\n"
            f"Variacoes: {variations}"
        )
        try:
            result = self.generation.generate_copy(prompt, mode)
        except AIServiceError:
            raise

        enriched = {
            "captions": result.get("result", []),
            "cta": "Comente 'QUERO' para receber o plano completo." if include_cta else "",
            "hashtags": ["#marketingdigital", "#criativos", "#axi"] if include_hashtags else [],
            "channel": channel,
            "tone": tone,
        }

        created = self.generation.create_generation(
            user_id=user.id,
            project_id=project_id,
            generation_type="caption",
            prompt=campaign_context,
            input_payload={
                "campaign_context": campaign_context,
                "channel": channel,
                "tone": tone,
                "include_cta": include_cta,
                "include_hashtags": include_hashtags,
                "variations": variations,
            },
            result_payload=enriched,
        )
        return StudioGenerateResponse(generation_id=created.id, status=created.status, result=enriched)

    def generate_cta(
        self,
        user: User,
        *,
        project_id: int | None,
        campaign_context: str,
        channel: str,
        tone: str,
        variations: int,
    ) -> StudioGenerateResponse:
        mode = f"cta-{channel}-{tone}-v{variations}"
        prompt = (
            f"Contexto: {campaign_context}\n"
            f"Canal: {channel}\nTom: {tone}\n"
            f"Gerar apenas CTAs orientados para conversao com {variations} variacoes"
        )
        result = self.generation.generate_copy(prompt, mode)
        items = result.get("result", []) if isinstance(result, dict) else []
        enriched = {
            "captions": [],
            "cta": items[0] if items else "Clique para receber sua proposta personalizada.",
            "hashtags": [],
            "variations": items,
            "channel": channel,
            "tone": tone,
        }
        created = self.generation.create_generation(
            user_id=user.id,
            project_id=project_id,
            generation_type="cta",
            prompt=campaign_context,
            input_payload={
                "campaign_context": campaign_context,
                "channel": channel,
                "tone": tone,
                "variations": variations,
            },
            result_payload=enriched,
        )
        return StudioGenerateResponse(generation_id=created.id, status=created.status, result=enriched)

    def generate_promo_copy(
        self,
        user: User,
        *,
        project_id: int | None,
        campaign_context: str,
        channel: str,
        tone: str,
        variations: int,
    ) -> StudioGenerateResponse:
        mode = f"promo-copy-{channel}-{tone}-v{variations}"
        prompt = (
            f"Contexto: {campaign_context}\n"
            f"Canal: {channel}\nTom: {tone}\n"
            f"Crie texto promocional com promessa, beneficio e CTA em {variations} variacoes"
        )
        result = self.generation.generate_copy(prompt, mode)
        items = result.get("result", []) if isinstance(result, dict) else []
        enriched = {
            "captions": items,
            "cta": "Fale com nosso time e ative sua campanha hoje.",
            "hashtags": ["#promocao", "#marketing", "#axi"],
            "channel": channel,
            "tone": tone,
        }
        created = self.generation.create_generation(
            user_id=user.id,
            project_id=project_id,
            generation_type="promo-copy",
            prompt=campaign_context,
            input_payload={
                "campaign_context": campaign_context,
                "channel": channel,
                "tone": tone,
                "variations": variations,
            },
            result_payload=enriched,
        )
        return StudioGenerateResponse(generation_id=created.id, status=created.status, result=enriched)

    def ai_creative_assistant(
        self,
        user: User,
        *,
        project_id: int | None,
        action: str,
        briefing: str,
    ) -> StudioGenerateResponse:
        prompt = (
            f"Acao solicitada: {action}\n"
            f"Briefing: {briefing}\n"
            "Retorne estrutura pratica com ideia central, headline, CTA, copy curta e formato de criativo recomendado."
        )
        result = self.generation.generate_copy(prompt, f"ai-creative-{action.lower().replace(' ', '-')}")
        items = result.get("result", []) if isinstance(result, dict) else []
        enriched = {
            "action": action,
            "briefing": briefing,
            "ideas": items,
            "recommended_formats": ["Poster", "Story", "Video curto"],
        }
        created = self.generation.create_generation(
            user_id=user.id,
            project_id=project_id,
            generation_type="ai-creative",
            prompt=briefing,
            input_payload={"action": action, "briefing": briefing},
            result_payload=enriched,
        )
        return StudioGenerateResponse(generation_id=created.id, status=created.status, result=enriched)
