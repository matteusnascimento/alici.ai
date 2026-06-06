"""Centralized AI provider orchestration and fallback handling."""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import settings
from app.services.ai import providers
from app.services.ai.providers.base import ProviderError

logger = logging.getLogger(__name__)

FALLBACK_ORDER = ["groq", "gemini", "ollama", "openai"]


class AIManager:
    def __init__(self, provider: str | None = None):
        self.preferred_provider = (provider or settings.default_ai_provider or "groq").strip().lower()
        self.providers = self._load_providers()
        self.fallback_chain = self._get_fallback_chain()

    def _load_providers(self) -> dict[str, Any]:
        loaded: dict[str, Any] = {}
        registry = {
            "groq": "GroqProvider",
            "gemini": "GeminiProvider",
            "ollama": "OllamaProvider",
            "openai": "OpenAIProvider",
        }
        for provider_name in FALLBACK_ORDER:
            class_name = registry[provider_name]
            provider_class = getattr(providers, class_name, None)
            if provider_class is None:
                logger.warning("ai.provider.missing provider=%s", provider_name)
                continue
            loaded[provider_name] = provider_class()
        return loaded

    def _get_fallback_chain(self) -> list[str]:
        order = list(FALLBACK_ORDER)
        if self.preferred_provider in order:
            order.remove(self.preferred_provider)
            return [self.preferred_provider] + order
        return order

    def configured_providers(self) -> list[str]:
        return [name for name in self.fallback_chain if name in self.providers and self.providers[name].is_configured()]

    def get_active_provider(self) -> str | None:
        configured = self.configured_providers()
        return configured[0] if configured else None

    def chat(
        self,
        *,
        messages: list[dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int | None = None,
        model: str | None = None,
        provider: str | None = None,
    ) -> dict[str, Any]:
        provider_names = [provider] if provider else self.fallback_chain
        errors: list[ProviderError] = []

        for provider_name in provider_names:
            if not provider_name:
                continue
            instance = self.providers.get(provider_name)
            if not instance or not instance.is_configured():
                continue
            try:
                provider_model = model
                if provider_name != "openai" and model and model.startswith(("gpt-", "text-", "o")):
                    provider_model = None
                result = instance.chat(messages=messages, model=provider_model, temperature=temperature, max_tokens=max_tokens)
                result["provider"] = provider_name
                result["fallback_chain"] = self.fallback_chain
                return result
            except ProviderError as exc:
                errors.append(exc)
                logger.warning(
                    "ai.provider.failed provider=%s code=%s status_code=%s",
                    exc.provider,
                    exc.code,
                    exc.status_code,
                )

        if errors:
            last = errors[-1]
            raise ProviderError(str(last), provider=last.provider, status_code=last.status_code, code=last.code)
        raise ProviderError("No AI provider is configured", provider="none", status_code=503, code="not_configured")

    def summarize(self, text: str, max_length: int | None = None, provider: str | None = None) -> dict[str, Any]:
        prompt = f"Resuma o texto abaixo em ate {max_length or 800} caracteres:\n\n{text}"
        return self.chat(messages=[{"role": "user", "content": prompt}], provider=provider)

    def generate_code(self, prompt: str, language: str = "python", provider: str | None = None) -> dict[str, Any]:
        messages = [{"role": "user", "content": f"Gere codigo {language} para: {prompt}"}]
        return self.chat(messages=messages, provider=provider)
