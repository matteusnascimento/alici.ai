from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status

from app.core.config import settings
from app.services.ai_service import AIService


class StudioVideoService:
    _ai = AIService()

    @staticmethod
    def _unavailable(operation: str) -> None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Operacao real de video '{operation}' ainda nao esta configurada.",
        )

    @staticmethod
    def _provider_not_configured(provider: str) -> None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Provider {provider} não configurado.",
        )

    @staticmethod
    def generate(prompt: str, options: dict[str, Any]) -> dict[str, Any]:
        if not (settings.shotstack_api_key or settings.creatomate_api_key):
            StudioVideoService._provider_not_configured("Shotstack ou Creatomate")
        StudioVideoService._unavailable("video-generate")

    @staticmethod
    def captions(prompt: str, options: dict[str, Any]) -> dict[str, Any]:
        generated = StudioVideoService._ai.generate_structured_output(
            prompt=f"Briefing: {prompt}\nEstilo: {options.get('style', 'bold-modern')}",
            schema={
                "type": "object",
                "properties": {
                    "captions": {
                        "type": "array",
                        "minItems": 3,
                        "maxItems": 3,
                        "items": {"type": "string"},
                    }
                },
                "required": ["captions"],
                "additionalProperties": False,
            },
            system_prompt="Gere 3 legendas de video em pt-BR com gancho, beneficio e CTA. Retorne apenas JSON valido.",
            function_name="caption_generator",
        )
        return {
            "operation": "video-captions",
            "status": "completed",
            "captions": generated.get("captions", []),
            "style": options.get("style", "bold-modern"),
            "source": prompt,
        }

    @staticmethod
    def cut(prompt: str, options: dict[str, Any]) -> dict[str, Any]:
        if not (settings.shotstack_api_key or settings.creatomate_api_key):
            StudioVideoService._provider_not_configured("Shotstack ou Creatomate")
        StudioVideoService._unavailable("video-cut")

    @staticmethod
    def voiceover(prompt: str, options: dict[str, Any]) -> dict[str, Any]:
        if not settings.elevenlabs_api_key:
            StudioVideoService._provider_not_configured("ElevenLabs")
        StudioVideoService._unavailable("video-voiceover")

    @staticmethod
    def export(prompt: str, options: dict[str, Any]) -> dict[str, Any]:
        if not (settings.shotstack_api_key or settings.creatomate_api_key):
            StudioVideoService._provider_not_configured("Shotstack ou Creatomate")
        StudioVideoService._unavailable("video-export")

    @staticmethod
    def thumbnail(prompt: str, options: dict[str, Any]) -> dict[str, Any]:
        if not (settings.effective_openai_api_key or settings.flux_api_key):
            StudioVideoService._provider_not_configured("OpenAI Images ou Flux")
        StudioVideoService._unavailable("video-thumbnail")
