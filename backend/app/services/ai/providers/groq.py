from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.services.ai.providers.base import HTTPAIProvider, ProviderError


class GroqProvider(HTTPAIProvider):
    name = "groq"

    def __init__(self) -> None:
        super().__init__(timeout_seconds=settings.ai_provider_timeout_seconds)
        self.api_key = settings.groq_api_key
        self.default_model = settings.groq_model

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat(self, *, messages: list[dict[str, Any]], model: str | None = None, temperature: float = 0.3, max_tokens: int | None = None) -> dict[str, Any]:
        if not self.is_configured():
            raise ProviderError("Groq is not configured", provider=self.name, code="not_configured")
        selected_model = model or self.default_model
        self._log_attempt(model=selected_model, input_chars=sum(len(str(item.get("content") or "")) for item in messages))
        data, latency_ms = self._safe_request(
            "POST",
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={"model": selected_model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens},
        )
        content = str((((data.get("choices") or [{}])[0].get("message") or {}).get("content")) or "").strip()
        if not content:
            raise ProviderError("Groq returned empty content", provider=self.name, status_code=502, code="empty_response")
        self._log_success(model=selected_model, latency_ms=latency_ms)
        return {"content": content, "model": data.get("model") or selected_model, "usage": data.get("usage") or {}, "latency_ms": latency_ms}
