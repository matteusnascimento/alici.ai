"""Model router service for multi-provider AI orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ProviderCapability:
    provider: str
    default_model: str
    supports_stream: bool = True
    supports_tools: bool = True


class ModelRouterService:
    """Resolve provider from model names and tenant overrides."""

    _CAPABILITIES: dict[str, ProviderCapability] = {
        "openai": ProviderCapability(provider="openai", default_model="gpt-4o-mini"),
        "anthropic": ProviderCapability(provider="anthropic", default_model="claude-3-5-sonnet"),
        "gemini": ProviderCapability(provider="gemini", default_model="gemini-1.5-flash"),
        "mistral": ProviderCapability(provider="mistral", default_model="mistral-large-latest"),
        "huggingface": ProviderCapability(provider="huggingface", default_model="hf:meta-llama/Meta-Llama-3-8B-Instruct"),
        "local": ProviderCapability(provider="local", default_model="local:llama3"),
    }

    # Prefix map keeps default behavior deterministic even before provider setup UI.
    _MODEL_PREFIX_PROVIDER: dict[str, str] = {
        "gpt": "openai",
        "o1": "openai",
        "claude": "anthropic",
        "gemini": "gemini",
        "mistral": "mistral",
        "hf:": "huggingface",
        "local:": "local",
    }

    # In-memory org-level overrides (safe for MVP and can be replaced by DB table later).
    _ORG_DEFAULT_PROVIDER: dict[str, str] = {}

    def resolve_provider(self, model: str, organization_id: Optional[str] = None) -> Optional[str]:
        value = (model or "").strip().lower()
        if not value:
            return self._ORG_DEFAULT_PROVIDER.get(organization_id or "")

        for prefix, provider in self._MODEL_PREFIX_PROVIDER.items():
            if value.startswith(prefix):
                return provider

        return self._ORG_DEFAULT_PROVIDER.get(organization_id or "")

    def set_default_provider(self, organization_id: str, provider: str) -> None:
        provider_name = (provider or "").strip().lower()
        if provider_name not in self._CAPABILITIES:
            raise ValueError(f"Unsupported provider: {provider}")
        self._ORG_DEFAULT_PROVIDER[organization_id] = provider_name

    def list_providers(self) -> list[dict[str, object]]:
        return [
            {
                "provider": capability.provider,
                "default_model": capability.default_model,
                "supports_stream": capability.supports_stream,
                "supports_tools": capability.supports_tools,
            }
            for capability in self._CAPABILITIES.values()
        ]

    def get_default_provider(self, organization_id: str) -> Optional[str]:
        return self._ORG_DEFAULT_PROVIDER.get(organization_id)
