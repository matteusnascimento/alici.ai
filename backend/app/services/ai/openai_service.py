from __future__ import annotations

import base64
import json
import logging
import time
from typing import Any

from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError, OpenAI, RateLimitError

from app.core.config import settings
from app.services.ai.model_router import get_model_for_task

logger = logging.getLogger(__name__)


class OpenAIProviderError(RuntimeError):
    def __init__(self, message: str, *, status_code: int = 503, code: str = "openai_error") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code


class OpenAIProviderService:
    def __init__(self) -> None:
        self.api_key = settings.effective_openai_api_key
        self.timeout = settings.openai_timeout_seconds
        self.client = OpenAI(api_key=self.api_key, timeout=self.timeout) if self.api_key else None

    def is_configured(self) -> bool:
        return bool(self.api_key and self.client)

    def _raise_mapped_error(self, exc: Exception) -> OpenAIProviderError:
        if isinstance(exc, AuthenticationError):
            raise OpenAIProviderError("OpenAI authentication failed", status_code=401, code="invalid_api_key") from exc
        if isinstance(exc, RateLimitError):
            raise OpenAIProviderError("OpenAI rate limit reached", status_code=429, code="rate_limit") from exc
        if isinstance(exc, APITimeoutError):
            raise OpenAIProviderError("OpenAI request timed out", status_code=504, code="timeout") from exc
        if isinstance(exc, APIConnectionError):
            raise OpenAIProviderError("OpenAI connection failed", status_code=503, code="connection_error") from exc
        if isinstance(exc, APIError):
            raise OpenAIProviderError(f"OpenAI API error: {exc}", status_code=502, code="api_error") from exc
        raise OpenAIProviderError(f"OpenAI request failed: {exc}", status_code=503, code="unknown_error") from exc

    def generate_text(
        self,
        *,
        task_name: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        if not self.client:
            raise OpenAIProviderError("OPENAI_API_KEY is not configured", status_code=503, code="missing_api_key")

        selected_model = model or get_model_for_task(task_name)
        started = time.perf_counter()
        try:
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:
            self._raise_mapped_error(exc)

        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        content = ""
        if response.choices:
            content = str(response.choices[0].message.content or "").strip()

        return {
            "content": content,
            "model": response.model or selected_model,
            "usage": response.usage.model_dump() if response.usage else {},
            "latency_ms": latency_ms,
            "raw": response.model_dump(),
        }

    def generate_structured_json(
        self,
        *,
        task_name: str,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        text_response = self.generate_text(
            task_name=task_name,
            messages=[
                {"role": "system", "content": f"{system_prompt}\nRetorne somente JSON válido compatível com o schema."},
                {"role": "user", "content": user_prompt},
            ],
            model=model,
            temperature=0.2,
        )
        content = text_response.get("content") or "{}"
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = {}
        return {**text_response, "structured_data": parsed, "schema": schema}

    def analyze_image(
        self,
        *,
        task_name: str,
        image_bytes: bytes,
        prompt: str,
        model: str | None = None,
    ) -> dict[str, Any]:
        if not self.client:
            raise OpenAIProviderError("OPENAI_API_KEY is not configured", status_code=503, code="missing_api_key")

        selected_model = model or get_model_for_task(task_name)
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        started = time.perf_counter()
        try:
            response = self.client.responses.create(
                model=selected_model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            {"type": "input_image", "image_url": f"data:image/jpeg;base64,{image_b64}"},
                        ],
                    }
                ],
            )
        except Exception as exc:
            self._raise_mapped_error(exc)

        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        text = response.output_text or ""
        return {
            "content": text,
            "model": selected_model,
            "usage": {},
            "latency_ms": latency_ms,
            "raw": response.model_dump() if hasattr(response, "model_dump") else {},
        }
