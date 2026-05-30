from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.services.ai.providers.base import HTTPAIProvider, ProviderError


class OllamaProvider(HTTPAIProvider):
    name = "ollama"

    def __init__(self) -> None:
        super().__init__(timeout_seconds=settings.ollama_timeout_seconds)
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.default_model = settings.ollama_model

    def is_configured(self) -> bool:
        return bool(settings.ollama_enabled and self.base_url and self.default_model)

    def chat(self, *, messages: list[dict[str, Any]], model: str | None = None, temperature: float = 0.3, max_tokens: int | None = None) -> dict[str, Any]:
        if not self.is_configured():
            raise ProviderError("Ollama is not configured", provider=self.name, code="not_configured")
        selected_model = model or self.default_model
        self._log_attempt(model=selected_model, input_chars=sum(len(str(item.get("content") or "")) for item in messages))
        options: dict[str, Any] = {"temperature": temperature}
        if max_tokens:
            options["num_predict"] = max_tokens
        data, latency_ms = self._safe_request(
            "POST",
            f"{self.base_url}/api/chat",
            json={"model": selected_model, "messages": messages, "stream": False, "options": options},
        )
        content = str((data.get("message") or {}).get("content") or "").strip()
        if not content:
            raise ProviderError("Ollama returned empty content", provider=self.name, status_code=502, code="empty_response")
        self._log_success(model=selected_model, latency_ms=latency_ms)
        return {"content": content, "model": selected_model, "usage": {}, "latency_ms": latency_ms}
