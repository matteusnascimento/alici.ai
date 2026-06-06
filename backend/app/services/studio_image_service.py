from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status

from app.core.config import settings


class StudioImageService:
    @staticmethod
    def _unavailable(operation: str) -> None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Operacao real de imagem '{operation}' ainda nao esta configurada.",
        )

    @staticmethod
    def _provider_not_configured(provider: str) -> None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Provider {provider} não configurado.",
        )

    @staticmethod
    def remove_background(asset_url: str | None, options: dict[str, Any]) -> dict[str, Any]:
        if not settings.removebg_api_key:
            StudioImageService._provider_not_configured("Remove.bg")
        StudioImageService._unavailable("remove-background")

    @staticmethod
    def retouch(asset_url: str | None, options: dict[str, Any]) -> dict[str, Any]:
        if not (settings.effective_openai_api_key or settings.flux_api_key):
            StudioImageService._provider_not_configured("OpenAI Images ou Flux")
        StudioImageService._unavailable("retouch")

    @staticmethod
    def enhance(asset_url: str | None, options: dict[str, Any]) -> dict[str, Any]:
        if not (settings.effective_openai_api_key or settings.flux_api_key):
            StudioImageService._provider_not_configured("OpenAI Images ou Flux")
        StudioImageService._unavailable("enhance")

    @staticmethod
    def resize(asset_url: str | None, options: dict[str, Any]) -> dict[str, Any]:
        if not (settings.effective_openai_api_key or settings.flux_api_key):
            StudioImageService._provider_not_configured("OpenAI Images ou Flux")
        StudioImageService._unavailable("resize")

    @staticmethod
    def filter_image(asset_url: str | None, options: dict[str, Any]) -> dict[str, Any]:
        if not (settings.effective_openai_api_key or settings.flux_api_key):
            StudioImageService._provider_not_configured("OpenAI Images ou Flux")
        StudioImageService._unavailable("filter")

    @staticmethod
    def upscale(asset_url: str | None, options: dict[str, Any]) -> dict[str, Any]:
        if not (settings.effective_openai_api_key or settings.flux_api_key):
            StudioImageService._provider_not_configured("OpenAI Images ou Flux")
        StudioImageService._unavailable("upscale")
