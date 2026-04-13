from __future__ import annotations

import json
from typing import Any

from app.core.config import settings
from app.services.ai.model_router import get_model_for_task, normalize_task
from app.services.openai_service import OpenAIService


def get_default_ai_provider() -> str:
    return (settings.default_ai_provider or "openai").strip().lower()


def get_default_chat_model() -> str:
    return settings.openai_model or "gpt-4o-mini"


def get_model_for_task_name(task_name: str | None) -> str:
    return get_model_for_task(task_name)


class ProviderService:
    def __init__(self, provider: str | None = None) -> None:
        self.provider = (provider or get_default_ai_provider()).strip().lower()
        self._openai = OpenAIService()

    def is_configured(self) -> bool:
        return self.provider == "openai" and bool(settings.effective_openai_api_key)

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
        if self.provider != "openai":
            raise RuntimeError(f"Unsupported provider for now: {self.provider}")
        try:
            return self._openai.send_chat_message(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                model=model or get_model_for_task(normalized_task),
            )
        except Exception as exc:
            # Em dev/teste, evita quebrar fluxos por indisponibilidade/autenticacao externa.
            if settings.app_env.lower() != "production":
                return {
                    "content": "Resposta de teste da IA",
                    "model": model or get_model_for_task(normalized_task),
                    "usage": {"total_tokens": 0},
                    "latency_ms": 0,
                    "raw": {"fallback": True, "reason": str(exc)},
                }
            raise

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
        if self.provider != "openai":
            raise RuntimeError(f"Unsupported provider for now: {self.provider}")
        full_prompt = f"{system_prompt}\n\n{user_prompt}".strip()
        try:
            result = self._openai.structured_extract(full_prompt, schema)
        except Exception as exc:
            if settings.app_env.lower() != "production":
                return {
                    "content": "{}",
                    "model": model or get_model_for_task(normalized_task),
                    "usage": {"total_tokens": 0},
                    "latency_ms": 0,
                    "structured_data": {},
                    "raw": {"fallback": True, "reason": str(exc)},
                }
            raise
        text = str(result.get("text") or "{}").strip()
        try:
            parsed = json.loads(text) if text else {}
        except json.JSONDecodeError:
            parsed = {}
        return {
            "content": text,
            "model": result.get("model") or model or get_model_for_task(normalized_task),
            "usage": {},
            "latency_ms": None,
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
        if self.provider != "openai":
            raise RuntimeError(f"Unsupported provider for now: {self.provider}")
        try:
            result = self._openai.analyze_image_bytes(
                image_bytes=image_bytes,
                prompt=prompt,
            )
        except Exception as exc:
            if settings.app_env.lower() != "production":
                return {
                    "content": "Analise indisponivel no momento.",
                    "model": model or get_model_for_task(normalized_task),
                    "usage": {"total_tokens": 0},
                    "latency_ms": 0,
                    "raw": {"fallback": True, "reason": str(exc)},
                }
            raise
        return {
            "content": result.get("text", ""),
            "model": result.get("model") or model or get_model_for_task(normalized_task),
            "usage": {},
            "latency_ms": None,
            "raw": result.get("raw", {}),
        }
