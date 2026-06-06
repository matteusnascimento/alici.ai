from __future__ import annotations

import logging
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class ProviderError(RuntimeError):
    def __init__(self, message: str, *, provider: str, status_code: int = 503, code: str = "provider_error") -> None:
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code
        self.code = code


class HTTPAIProvider:
    name: str = "provider"
    default_model: str = ""

    def __init__(self, *, timeout_seconds: float) -> None:
        self.timeout_seconds = timeout_seconds

    def is_configured(self) -> bool:
        return False

    def chat(
        self,
        *,
        messages: list[dict[str, Any]],
        model: str | None = None,
        temperature: float = 0.3,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    def _safe_request(self, method: str, url: str, **kwargs: Any) -> tuple[dict[str, Any], float]:
        started = time.perf_counter()
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.request(method, url, **kwargs)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ProviderError("AI provider timed out", provider=self.name, status_code=504, code="timeout") from exc
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            code = "rate_limit" if status == 429 else "auth_error" if status in {401, 403} else "http_error"
            raise ProviderError(
                f"AI provider returned HTTP {status}",
                provider=self.name,
                status_code=status if status in {401, 403, 429} else 502,
                code=code,
            ) from exc
        except httpx.HTTPError as exc:
            raise ProviderError("AI provider network error", provider=self.name, status_code=503, code="network_error") from exc

        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return response.json(), latency_ms

    def _log_attempt(self, *, model: str, input_chars: int) -> None:
        logger.info("ai.provider.request provider=%s model=%s input_chars=%s", self.name, model, input_chars)

    def _log_success(self, *, model: str, latency_ms: float) -> None:
        logger.info("ai.provider.success provider=%s model=%s latency_ms=%s", self.name, model, latency_ms)
