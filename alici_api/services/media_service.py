"""Media provider boundary.

The public media endpoints must never return locally fabricated assets as if
they were paid AI generations. Until real providers are configured, the service
fails explicitly before credits are charged. Future integrations for Flux,
ElevenLabs, Kling, Runway, Luma, etc. should live behind this module.
"""

from __future__ import annotations

from alici_api.services.media_storage import R2MediaStorage, StoredMedia


class MediaProviderUnavailableError(RuntimeError):
    """Raised when a paid media capability has no real provider configured."""

    def __init__(self, media_type: str, message: str):
        self.media_type = media_type
        super().__init__(message)


_UNAVAILABLE_MESSAGES = {
    "image": "Em breve - geracao de imagem com provider real (Flux/Stability/OpenAI Images) ainda nao esta ativa.",
    "audio": "Em breve - geracao de audio com provider real ainda nao esta ativa.",
    "video": "Em breve - integracao com Kling/Runway/Luma ainda nao esta ativa.",
    "image_analysis": "Em breve - analise de imagem com modelo de visao real ainda nao esta ativa.",
    "chat_image_analysis": "Em breve - analise de imagem no chat com modelo de visao real ainda nao esta ativa.",
}


def unavailable_message(media_type: str) -> str:
    return _UNAVAILABLE_MESSAGES.get(
        media_type,
        "Em breve - este recurso de midia ainda nao possui provider real ativo.",
    )


def ensure_media_provider_available(media_type: str) -> None:
    """Block paid media work when no real provider implementation exists."""
    raise MediaProviderUnavailableError(media_type, unavailable_message(media_type))


def store_generated_media_bytes(
    *,
    content: bytes,
    filename: str,
    content_type: str,
    folder: str = "generated",
) -> StoredMedia:
    """Persist real provider output in R2.

    Provider integrations should call this after receiving bytes from the
    upstream AI service. It intentionally does not create local fallback files.
    """
    return R2MediaStorage().upload_bytes(
        content=content,
        filename=filename,
        content_type=content_type,
        folder=folder,
    )


async def store_generated_media_url(
    *,
    source_url: str,
    filename: str,
    content_type: str | None = None,
    folder: str = "generated",
) -> StoredMedia:
    """Download real provider output and persist it in R2."""
    return await R2MediaStorage().upload_from_url(
        source_url=source_url,
        filename=filename,
        content_type=content_type,
        folder=folder,
    )


def generate_image(prompt: str) -> str:
    ensure_media_provider_available("image")
    raise AssertionError("unreachable")


def generate_audio(text: str) -> str:
    ensure_media_provider_available("audio")
    raise AssertionError("unreachable")


def generate_video(prompt: str) -> dict:
    ensure_media_provider_available("video")
    raise AssertionError("unreachable")


def analyze_image_bytes(content: bytes, filename: str, content_type: str) -> dict:
    ensure_media_provider_available("image_analysis")
    raise AssertionError("unreachable")
