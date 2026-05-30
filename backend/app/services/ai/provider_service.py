from __future__ import annotations

import json
from typing import Any

from app.core.config import settings
from app.services.ai.manager import AIManager
from app.services.ai.model_router import get_model_for_task, normalize_task
from app.services.ai.providers.base import ProviderError


def get_default_ai_provider() -> str:
    return (settings.default_ai_provider or "groq").strip().lower()


def get_default_chat_model() -> str:
    return settings.openai_model or "gpt-4o-mini"


def get_model_for_task_name(task_name: str | None) -> str:
    return get_model_for_task(task_name)


class ProviderService:
    def __init__(self, provider: str | None = None) -> None:
        self.provider = (provider or get_default_ai_provider()).strip().lower()
        self._manager = AIManager(self.provider)

    def is_configured(self) -> bool:
        return bool(self._manager.configured_providers())

    def run_text(
        self,
        *,
        task_name: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        normalized_task = normalize_task(task_name)
        return self._manager.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model or get_model_for_task(normalized_task),
        )

    def run_structured(
        self,
        *,
        task_name: str,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        normalized_task = normalize_task(task_name)
        full_prompt = f"{system_prompt}\n\n{user_prompt}".strip()
        result = self._manager.chat(
            messages=[
                {"role": "system", "content": "Responda somente JSON valido que siga o schema informado."},
                {"role": "user", "content": f"Schema: {json.dumps(schema, ensure_ascii=True)}\n\n{full_prompt}"},
            ],
            model=model or get_model_for_task(normalized_task),
        )
        text = str(result.get("content") or "{}").strip()
        try:
            parsed = json.loads(text) if text else {}
        except json.JSONDecodeError:
            parsed = {}
        return {
            "content": text,
            "model": result.get("model") or model or get_model_for_task(normalized_task),
            "usage": result.get("usage") or {},
            "latency_ms": result.get("latency_ms"),
            "structured_data": parsed,
            "raw": result.get("raw", {}),
        }

    def run_image_analysis(
        self,
        *,
        task_name: str,
        image_bytes: bytes,
        prompt: str,
        model: str | None = None,
    ) -> dict[str, Any]:
        normalized_task = normalize_task(task_name)
        result = self._manager.chat(
            messages=[{"role": "user", "content": f"Analise esta imagem com base nesta descricao/contexto: {prompt}"}],
            model=model or get_model_for_task(normalized_task),
        )
        return {
            "content": result.get("content", ""),
            "model": result.get("model") or model or get_model_for_task(normalized_task),
            "usage": result.get("usage") or {},
            "latency_ms": result.get("latency_ms"),
            "raw": result.get("raw", {}),
        }
