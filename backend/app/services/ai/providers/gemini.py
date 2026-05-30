from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.services.ai.providers.base import HTTPAIProvider, ProviderError


class GeminiProvider(HTTPAIProvider):
    name = "gemini"

    def __init__(self) -> None:
        super().__init__(timeout_seconds=settings.ai_provider_timeout_seconds)
        self.api_key = settings.gemini_api_key
        self.default_model = settings.gemini_model

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat(self, *, messages: list[dict[str, Any]], model: str | None = None, temperature: float = 0.3, max_tokens: int | None = None) -> dict[str, Any]:
        if not self.is_configured():
            raise ProviderError("Gemini is not configured", provider=self.name, code="not_configured")
        selected_model = model or self.default_model
        prompt = "\n".join(f"{item.get('role', 'user')}: {item.get('content', '')}" for item in messages)
        self._log_attempt(model=selected_model, input_chars=len(prompt))
        data, latency_ms = self._safe_request(
            "POST",
            f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:generateContent?key={self.api_key}",
            json={
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": temperature, **({"maxOutputTokens": max_tokens} if max_tokens else {})},
            },
        )
        parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
        content = "".join(str(part.get("text") or "") for part in parts).strip()
        if not content:
            raise ProviderError("Gemini returned empty content", provider=self.name, status_code=502, code="empty_response")
        self._log_success(model=selected_model, latency_ms=latency_ms)
        return {"content": content, "model": selected_model, "usage": data.get("usageMetadata") or {}, "latency_ms": latency_ms}
