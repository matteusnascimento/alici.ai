"""Real media provider integrations.

Paid media features must either call a real upstream provider or fail before
credits are charged. Generated assets are copied to Cloudflare R2 so web and
worker processes can serve stable URLs without relying on local disk.
"""

from __future__ import annotations

import mimetypes
import base64
from dataclasses import dataclass, field
from pathlib import Path
from time import monotonic, sleep
from typing import Any
from urllib.parse import urlparse

import httpx
from pydantic import SecretStr

from alici_api.config import get_settings
from alici_api.services.media_storage import MediaStorageError, R2MediaStorage, StoredMedia
from logger import get_logger


logger_media_provider = get_logger("media_provider")


class MediaProviderUnavailableError(RuntimeError):
    """Raised when no real paid provider is configured for a media feature."""

    def __init__(self, media_type: str, message: str):
        self.media_type = media_type
        super().__init__(message)


class MediaProviderError(RuntimeError):
    """Raised when a configured upstream provider fails."""


@dataclass(frozen=True)
class ConfiguredMediaProvider:
    media_type: str
    provider_name: str
    model_name: str


@dataclass(frozen=True)
class MediaGenerationResult:
    url: str
    provider: str
    model: str
    r2_key: str
    source_url: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_payload(self, field_name: str = "url") -> dict[str, Any]:
        payload = {
            field_name: self.url,
            "provider": self.provider,
            "model": self.model,
            "r2_key": self.r2_key,
        }
        if self.source_url:
            payload["source_provider_url"] = self.source_url
        payload.update(self.metadata)
        return payload


def _secret_value(value: SecretStr | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, SecretStr):
        resolved = value.get_secret_value()
    else:
        resolved = str(value)
    resolved = resolved.strip()
    return resolved or None


def _runway_secret() -> str | None:
    settings = get_settings()
    return _secret_value(settings.runway_api_secret) or _secret_value(getattr(settings, "runwayml_api_secret", None))


def _poll_interval() -> float:
    return max(1.0, float(get_settings().media_generation_poll_interval_seconds or 3.0))


def _timeout_seconds() -> float:
    return max(30.0, float(get_settings().media_generation_timeout_seconds or 600))


def _client_timeout() -> httpx.Timeout:
    timeout = _timeout_seconds()
    return httpx.Timeout(timeout=timeout, connect=20.0, write=30.0, pool=30.0)


def _raise_response(provider: str, response: httpx.Response) -> None:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        body = response.text[:800] if response.text else ""
        raise MediaProviderError(f"{provider} respondeu HTTP {response.status_code}: {body}") from exc


def _first_url(value: Any) -> str | None:
    if isinstance(value, str):
        return value if value.startswith(("http://", "https://")) else None
    if isinstance(value, list):
        for item in value:
            found = _first_url(item)
            if found:
                return found
    if isinstance(value, dict):
        for key in ("url", "video", "image", "audio", "uri"):
            found = _first_url(value.get(key))
            if found:
                return found
        for item in value.values():
            found = _first_url(item)
            if found:
                return found
    return None


def _filename_from_url(source_url: str, fallback: str) -> str:
    parsed = urlparse(source_url)
    suffix = Path(parsed.path).suffix
    if suffix:
        return Path(parsed.path).name or fallback
    return fallback


def _store_remote_url(
    *,
    provider: str,
    source_url: str,
    fallback_filename: str,
    folder: str,
    max_bytes: int,
) -> StoredMedia:
    storage = R2MediaStorage()
    with httpx.Client(timeout=_client_timeout(), follow_redirects=True) as client:
        response = client.get(source_url)
        _raise_response(provider, response)
        content = response.content
        if len(content) > max_bytes:
            raise MediaProviderError(f"{provider} retornou arquivo maior que o limite permitido")
        content_type = response.headers.get("content-type") or mimetypes.guess_type(source_url)[0]
        filename = _filename_from_url(source_url, fallback_filename)
        return storage.upload_bytes(
            content=content,
            filename=filename,
            content_type=content_type,
            folder=folder,
        )


def _store_bytes(
    *,
    content: bytes,
    filename: str,
    content_type: str,
    folder: str,
) -> StoredMedia:
    return R2MediaStorage().upload_bytes(
        content=content,
        filename=filename,
        content_type=content_type,
        folder=folder,
    )


def _require_r2(media_type: str) -> None:
    storage = R2MediaStorage()
    missing = storage.missing_config()
    if missing:
        raise MediaProviderUnavailableError(
            media_type,
            f"Storage persistente R2 obrigatorio para midia paga. Configure: {', '.join(missing)}",
        )


def available_media_providers(media_type: str) -> list[ConfiguredMediaProvider]:
    settings = get_settings()
    providers: list[ConfiguredMediaProvider] = []

    if media_type == "image":
        if _secret_value(settings.replicate_api_token):
            providers.append(ConfiguredMediaProvider(media_type, "replicate", settings.replicate_image_model))
        if _runway_secret():
            providers.append(ConfiguredMediaProvider(media_type, "runway", settings.runway_image_model))
    elif media_type == "audio":
        if _secret_value(settings.elevenlabs_api_key):
            providers.append(ConfiguredMediaProvider(media_type, "elevenlabs", settings.elevenlabs_model))
    elif media_type == "video":
        if _secret_value(settings.luma_api_key):
            providers.append(ConfiguredMediaProvider(media_type, "luma", settings.luma_video_model))
        if _runway_secret():
            providers.append(ConfiguredMediaProvider(media_type, "runway", settings.runway_video_model))
    elif media_type in {"image_analysis", "chat_image_analysis"}:
        if _secret_value(settings.gemini_api_key):
            providers.append(ConfiguredMediaProvider(media_type, "gemini", settings.gemini_model))
        if _secret_value(settings.openai_api_key):
            providers.append(ConfiguredMediaProvider(media_type, "openai", settings.openai_model_chat_general))

    if providers and media_type in {"image", "audio", "video"}:
        _require_r2(media_type)
    return providers


def ensure_media_provider_available(media_type: str) -> ConfiguredMediaProvider:
    providers = available_media_providers(media_type)
    if providers:
        return providers[0]

    required = {
        "image": "REPLICATE_API_TOKEN ou RUNWAY_API_SECRET",
        "audio": "ELEVENLABS_API_KEY",
        "video": "LUMA_API_KEY ou RUNWAY_API_SECRET",
        "image_analysis": "GEMINI_API_KEY ou OPENAI_API_KEY",
        "chat_image_analysis": "GEMINI_API_KEY ou OPENAI_API_KEY",
    }.get(media_type, "provider real correspondente")
    raise MediaProviderUnavailableError(
        media_type,
        f"Nenhum provider real configurado para {media_type}. Configure {required}; nenhum credito foi cobrado.",
    )


def _poll_prediction(
    *,
    client: httpx.Client,
    provider: str,
    url: str,
    headers: dict[str, str],
    done_statuses: set[str],
    failed_statuses: set[str],
) -> dict[str, Any]:
    deadline = monotonic() + _timeout_seconds()
    payload: dict[str, Any] = {}

    while monotonic() < deadline:
        response = client.get(url, headers=headers)
        _raise_response(provider, response)
        payload = response.json()
        status = str(payload.get("status") or payload.get("state") or "").lower()
        if status in done_statuses:
            return payload
        if status in failed_statuses:
            raise MediaProviderError(f"{provider} falhou: {payload.get('failure_reason') or payload.get('error') or status}")
        sleep(_poll_interval())

    raise MediaProviderError(f"{provider} excedeu timeout de geracao")


def _replicate_image(prompt: str, provider: ConfiguredMediaProvider) -> MediaGenerationResult:
    token = _secret_value(get_settings().replicate_api_token)
    if not token:
        raise MediaProviderUnavailableError("image", "REPLICATE_API_TOKEN ausente")

    try:
        owner, model = provider.model_name.split("/", 1)
    except ValueError as exc:
        raise MediaProviderUnavailableError("image", "REPLICATE_IMAGE_MODEL deve usar owner/model") from exc

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Prefer": "wait=60",
    }
    create_url = f"https://api.replicate.com/v1/models/{owner}/{model}/predictions"
    with httpx.Client(timeout=_client_timeout(), follow_redirects=True) as client:
        response = client.post(create_url, headers=headers, json={"input": {"prompt": prompt}})
        _raise_response("replicate", response)
        payload = response.json()
        status = str(payload.get("status") or "").lower()
        if status not in {"succeeded", "failed", "canceled"}:
            poll_url = (payload.get("urls") or {}).get("get") or f"https://api.replicate.com/v1/predictions/{payload.get('id')}"
            payload = _poll_prediction(
                client=client,
                provider="replicate",
                url=poll_url,
                headers=headers,
                done_statuses={"succeeded"},
                failed_statuses={"failed", "canceled"},
            )
        if str(payload.get("status") or "").lower() != "succeeded":
            raise MediaProviderError(f"replicate falhou: {payload.get('error') or payload.get('status')}")

    source_url = _first_url(payload.get("output"))
    if not source_url:
        raise MediaProviderError("replicate concluiu sem URL de imagem")
    stored = _store_remote_url(
        provider="replicate",
        source_url=source_url,
        fallback_filename="flux-image.png",
        folder="media/results/images",
        max_bytes=30 * 1024 * 1024,
    )
    return MediaGenerationResult(
        url=stored.url,
        provider=provider.provider_name,
        model=provider.model_name,
        r2_key=stored.key,
        source_url=source_url,
        metadata={"provider_prediction_id": payload.get("id"), "content_type": stored.content_type},
    )


def _runway_headers() -> dict[str, str]:
    secret = _runway_secret()
    if not secret:
        raise MediaProviderUnavailableError("runway", "RUNWAY_API_SECRET ausente")
    return {
        "Authorization": f"Bearer {secret}",
        "Content-Type": "application/json",
        "X-Runway-Version": get_settings().runway_api_version,
    }


def _runway_task(endpoint: str, body: dict[str, Any]) -> dict[str, Any]:
    headers = _runway_headers()
    with httpx.Client(timeout=_client_timeout(), follow_redirects=True) as client:
        response = client.post(f"https://api.dev.runwayml.com/v1/{endpoint}", headers=headers, json=body)
        _raise_response("runway", response)
        payload = response.json()
        task_id = payload.get("id")
        if not task_id:
            raise MediaProviderError(f"runway nao retornou task id: {payload}")
        return _poll_prediction(
            client=client,
            provider="runway",
            url=f"https://api.dev.runwayml.com/v1/tasks/{task_id}",
            headers=headers,
            done_statuses={"succeeded", "completed"},
            failed_statuses={"failed", "cancelled", "canceled"},
        )


def _runway_image(prompt: str, provider: ConfiguredMediaProvider) -> MediaGenerationResult:
    payload = _runway_task(
        "text_to_image",
        {
            "model": provider.model_name,
            "promptText": prompt,
            "ratio": "1920:1080",
        },
    )
    source_url = _first_url(payload.get("output"))
    if not source_url:
        raise MediaProviderError("runway concluiu sem URL de imagem")
    stored = _store_remote_url(
        provider="runway",
        source_url=source_url,
        fallback_filename="runway-image.png",
        folder="media/results/images",
        max_bytes=40 * 1024 * 1024,
    )
    return MediaGenerationResult(
        url=stored.url,
        provider=provider.provider_name,
        model=provider.model_name,
        r2_key=stored.key,
        source_url=source_url,
        metadata={"provider_task_id": payload.get("id"), "content_type": stored.content_type},
    )


def _luma_video(prompt: str, provider: ConfiguredMediaProvider) -> MediaGenerationResult:
    token = _secret_value(get_settings().luma_api_key)
    if not token:
        raise MediaProviderUnavailableError("video", "LUMA_API_KEY ausente")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    create_url = "https://api.lumalabs.ai/dream-machine/v1/generations"
    with httpx.Client(timeout=_client_timeout(), follow_redirects=True) as client:
        response = client.post(
            create_url,
            headers=headers,
            json={"prompt": prompt, "model": provider.model_name, "aspect_ratio": "16:9"},
        )
        _raise_response("luma", response)
        payload = response.json()
        generation_id = payload.get("id")
        if not generation_id:
            raise MediaProviderError(f"luma nao retornou generation id: {payload}")
        payload = _poll_prediction(
            client=client,
            provider="luma",
            url=f"{create_url}/{generation_id}",
            headers=headers,
            done_statuses={"completed", "succeeded"},
            failed_statuses={"failed", "canceled", "cancelled"},
        )

    source_url = _first_url((payload.get("assets") or {}).get("video")) or _first_url(payload.get("video")) or _first_url(payload)
    if not source_url:
        raise MediaProviderError("luma concluiu sem URL de video")
    stored = _store_remote_url(
        provider="luma",
        source_url=source_url,
        fallback_filename="luma-video.mp4",
        folder="media/results/videos",
        max_bytes=300 * 1024 * 1024,
    )
    return MediaGenerationResult(
        url=stored.url,
        provider=provider.provider_name,
        model=provider.model_name,
        r2_key=stored.key,
        source_url=source_url,
        metadata={"provider_generation_id": payload.get("id"), "content_type": stored.content_type},
    )


def _runway_video(prompt: str, provider: ConfiguredMediaProvider) -> MediaGenerationResult:
    payload = _runway_task(
        "image_to_video",
        {
            "model": provider.model_name,
            "promptText": prompt,
            "ratio": "1280:720",
            "duration": 5,
        },
    )
    source_url = _first_url(payload.get("output"))
    if not source_url:
        raise MediaProviderError("runway concluiu sem URL de video")
    stored = _store_remote_url(
        provider="runway",
        source_url=source_url,
        fallback_filename="runway-video.mp4",
        folder="media/results/videos",
        max_bytes=300 * 1024 * 1024,
    )
    return MediaGenerationResult(
        url=stored.url,
        provider=provider.provider_name,
        model=provider.model_name,
        r2_key=stored.key,
        source_url=source_url,
        metadata={"provider_task_id": payload.get("id"), "content_type": stored.content_type},
    )


def _elevenlabs_audio(text: str, provider: ConfiguredMediaProvider) -> MediaGenerationResult:
    settings = get_settings()
    token = _secret_value(settings.elevenlabs_api_key)
    if not token:
        raise MediaProviderUnavailableError("audio", "ELEVENLABS_API_KEY ausente")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}"
    headers = {
        "xi-api-key": token,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    with httpx.Client(timeout=_client_timeout(), follow_redirects=True) as client:
        response = client.post(
            url,
            headers=headers,
            params={"output_format": "mp3_44100_128"},
            json={"text": text, "model_id": provider.model_name},
        )
        _raise_response("elevenlabs", response)
        content = response.content

    stored = _store_bytes(
        content=content,
        filename="elevenlabs-audio.mp3",
        content_type=response.headers.get("content-type") or "audio/mpeg",
        folder="media/results/audio",
    )
    return MediaGenerationResult(
        url=stored.url,
        provider=provider.provider_name,
        model=provider.model_name,
        r2_key=stored.key,
        metadata={"content_type": stored.content_type, "voice_id": settings.elevenlabs_voice_id},
    )


def _run_with_fallback(media_type: str, prompt: str) -> MediaGenerationResult:
    providers = available_media_providers(media_type)
    if not providers:
        ensure_media_provider_available(media_type)

    errors: list[str] = []
    for provider in providers:
        try:
            if provider.provider_name == "replicate" and media_type == "image":
                return _replicate_image(prompt, provider)
            if provider.provider_name == "runway" and media_type == "image":
                return _runway_image(prompt, provider)
            if provider.provider_name == "luma" and media_type == "video":
                return _luma_video(prompt, provider)
            if provider.provider_name == "runway" and media_type == "video":
                return _runway_video(prompt, provider)
            if provider.provider_name == "elevenlabs" and media_type == "audio":
                return _elevenlabs_audio(prompt, provider)
        except MediaProviderUnavailableError:
            raise
        except (MediaStorageError, MediaProviderError, httpx.HTTPError) as exc:
            errors.append(f"{provider.provider_name}:{provider.model_name}: {exc}")
            logger_media_provider.warning(
                "media_provider_failed",
                extra={"media_type": media_type, "provider": provider.provider_name, "model": provider.model_name},
            )
            continue

    raise MediaProviderError(f"Todos os providers reais falharam para {media_type}: {' | '.join(errors)}")


def store_generated_media_bytes(
    *,
    content: bytes,
    filename: str,
    content_type: str,
    folder: str = "media/results",
) -> StoredMedia:
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
    folder: str = "media/results",
) -> StoredMedia:
    return await R2MediaStorage().upload_from_url(
        source_url=source_url,
        filename=filename,
        content_type=content_type,
        folder=folder,
    )


def generate_image(prompt: str) -> str:
    result = _run_with_fallback("image", prompt)
    return result.url


def generate_audio(text: str) -> str:
    result = _run_with_fallback("audio", text)
    return result.url


def generate_video(prompt: str) -> dict[str, Any]:
    result = _run_with_fallback("video", prompt)
    return result.as_payload("video_url")


def _gemini_analyze_image(content: bytes, filename: str, content_type: str, provider: ConfiguredMediaProvider) -> dict[str, Any]:
    token = _secret_value(get_settings().gemini_api_key)
    if not token:
        raise MediaProviderUnavailableError("image_analysis", "GEMINI_API_KEY ausente")

    import google.generativeai as genai

    genai.configure(api_key=token)
    model = genai.GenerativeModel(provider.model_name)
    response = model.generate_content(
        [
            (
                "Analise a imagem para um usuario do alici.ai. Responda em portugues, "
                "com descricao objetiva, possiveis problemas visuais e sugestoes praticas."
            ),
            {"mime_type": content_type or "image/png", "data": content},
        ]
    )
    text = getattr(response, "text", "") or ""
    if not text.strip():
        raise MediaProviderError("gemini concluiu sem texto de analise")
    return {
        "provider": provider.provider_name,
        "model": provider.model_name,
        "filename": filename,
        "analysis": text.strip(),
        "resposta": text.strip(),
    }


def _openai_analyze_image(content: bytes, filename: str, content_type: str, provider: ConfiguredMediaProvider) -> dict[str, Any]:
    token = _secret_value(get_settings().openai_api_key)
    if not token:
        raise MediaProviderUnavailableError("image_analysis", "OPENAI_API_KEY ausente")

    from openai import OpenAI

    data_uri = f"data:{content_type or 'image/png'};base64,{base64.b64encode(content).decode('ascii')}"
    client = OpenAI(api_key=token)
    response = client.chat.completions.create(
        model=provider.model_name,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analise a imagem para um usuario do alici.ai. Responda em portugues, "
                            "com descricao objetiva, possiveis problemas visuais e sugestoes praticas."
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ],
            }
        ],
        max_tokens=600,
    )
    text = (response.choices[0].message.content or "").strip()
    if not text:
        raise MediaProviderError("openai concluiu sem texto de analise")
    return {
        "provider": provider.provider_name,
        "model": provider.model_name,
        "filename": filename,
        "analysis": text,
        "resposta": text,
    }


def analyze_image_bytes(content: bytes, filename: str, content_type: str) -> dict[str, Any]:
    providers = available_media_providers("image_analysis")
    if not providers:
        ensure_media_provider_available("image_analysis")

    errors: list[str] = []
    for provider in providers:
        try:
            if provider.provider_name == "gemini":
                return _gemini_analyze_image(content, filename, content_type, provider)
            if provider.provider_name == "openai":
                return _openai_analyze_image(content, filename, content_type, provider)
        except (MediaProviderError, httpx.HTTPError, Exception) as exc:
            errors.append(f"{provider.provider_name}:{provider.model_name}: {exc}")
            logger_media_provider.warning(
                "image_analysis_provider_failed",
                extra={"provider": provider.provider_name, "model": provider.model_name},
            )
            continue
    raise MediaProviderError(f"Todos os providers reais falharam para analise de imagem: {' | '.join(errors)}")
