"""AI Manager - Centralized provider orchestration and fallback handling."""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import settings
from app.services.ai.providers.groq_provider import GroqProvider
from app.services.ai.providers.gemini_provider import GeminiProvider
from app.services.ai.providers.ollama_provider import OllamaProvider
from app.services.ai.providers.openai_provider import OpenAIProvider

logger = logging.getLogger(__name__)


class AIManager:
    """Manages AI provider selection, fallback, and standardized responses."""

    def __init__(self, provider: str | None = None):
        self.preferred_provider = (provider or settings.default_ai_provider or "groq").strip().lower()
        self.fallback_chain = self._get_fallback_chain()
        self.providers = {
            "groq": GroqProvider(),
            "gemini": GeminiProvider(),
            "ollama": OllamaProvider(),
            "openai": OpenAIProvider(),
        }

    def _get_fallback_chain(self) -> list[str]:
        """Return ordered list of providers to try (preferred first)."""
        all_providers = ["groq", "gemini", "ollama", "openai"]
        if self.preferred_provider in all_providers:
            all_providers.remove(self.preferred_provider)
            return [self.preferred_provider] + all_providers
        return all_providers

    def get_active_provider(self) -> str:
        """Return first configured provider in fallback chain."""
        for provider_name in self.fallback_chain:
            provider = self.providers.get(provider_name)
            if provider and provider.is_configured():
                logger.debug(f"Using AI provider: {provider_name}")
                return provider_name
        return None

    def get_provider_instance(self, provider_name: str | None = None):
        """Get provider instance, using preferred or first available."""
        name = provider_name or self.get_active_provider()
        if not name:
            raise RuntimeError("No AI provider is configured")
        provider = self.providers.get(name)
        if not provider:
            raise RuntimeError(f"Unknown AI provider: {name}")
        return provider

    async def chat(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int | None = None,
        provider: str | None = None,
    ) -> dict[str, Any]:
        """
        Send chat message using best available provider.

        Returns:
            Standard response with keys: content, model, provider, latency_ms, usage
        """
        provider_instance = self.get_provider_instance(provider)
        result = await provider_instance.chat(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        result["provider"] = provider_instance.__class__.__name__.replace("Provider", "").lower()
        return result

    async def summarize(
        self,
        text: str,
        max_length: int | None = None,
        provider: str | None = None,
    ) -> dict[str, Any]:
        """Summarize text using best available provider."""
        provider_instance = self.get_provider_instance(provider)
        result = await provider_instance.summarize(text=text, max_length=max_length)
        result["provider"] = provider_instance.__class__.__name__.replace("Provider", "").lower()
        return result

    async def generate_code(
        self,
        prompt: str,
        language: str = "python",
        provider: str | None = None,
    ) -> dict[str, Any]:
        """Generate code using best available provider."""
        provider_instance = self.get_provider_instance(provider)
        result = await provider_instance.generate_code(prompt=prompt, language=language)
        result["provider"] = provider_instance.__class__.__name__.replace("Provider", "").lower()
        return result
