from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status


class StudioImageService:
    @staticmethod
    def _unavailable(operation: str) -> None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Operacao real de imagem '{operation}' ainda nao esta configurada.",
        )

    @staticmethod
    def remove_background(asset_url: str | None, options: dict[str, Any]) -> dict[str, Any]:
        StudioImageService._unavailable("remove-background")

    @staticmethod
    def retouch(asset_url: str | None, options: dict[str, Any]) -> dict[str, Any]:
        StudioImageService._unavailable("retouch")

    @staticmethod
    def enhance(asset_url: str | None, options: dict[str, Any]) -> dict[str, Any]:
        StudioImageService._unavailable("enhance")

    @staticmethod
    def resize(asset_url: str | None, options: dict[str, Any]) -> dict[str, Any]:
        StudioImageService._unavailable("resize")

    @staticmethod
    def filter_image(asset_url: str | None, options: dict[str, Any]) -> dict[str, Any]:
        StudioImageService._unavailable("filter")

    @staticmethod
    def upscale(asset_url: str | None, options: dict[str, Any]) -> dict[str, Any]:
        StudioImageService._unavailable("upscale")
