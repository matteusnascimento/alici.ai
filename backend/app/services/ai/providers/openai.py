from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.services.ai.providers.base import HTTPAIProvider, ProviderError
from app.services.openai_service import OpenAIService, OpenAIServiceError


class OpenAIProvider(HTTPAIProvider):
    name = "openai"

    def __init__(self) -> None:
        super().__init__(timeout_seconds=settings.openai_timeout_seconds)
        self.default_model = settings.effective_openai_chat_model
        self.service = OpenAIService()

    def is_configured(self) -> bool:
        return bool(settings.effective_openai_api_key)

    def chat(self, *, messages: list[dict[str, Any]], model: str | None = None, temperature: float = 0.3, max_tokens: int | None = None) -> dict[str, Any]:
        if not self.is_configured():
            raise ProviderError("OpenAI is not configured", provider=self.name, code="not_configured")
        try:
            return self.service.send_chat_message(messages=messages, model=model or self.default_model, temperature=temperature, max_tokens=max_tokens)
        except OpenAIServiceError as exc:
            raise ProviderError(str(exc), provider=self.name, status_code=exc.status_code, code=exc.error_type) from exc
