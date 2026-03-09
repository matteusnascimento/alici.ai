"""Vector store provider registry for RAG infrastructure."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VectorProvider:
    name: str
    managed: bool
    requires_endpoint: bool


class VectorStoreService:
    """Manage vector database provider selection per organization."""

    _AVAILABLE: dict[str, VectorProvider] = {
        "supabase": VectorProvider(name="supabase", managed=True, requires_endpoint=True),
        "pinecone": VectorProvider(name="pinecone", managed=True, requires_endpoint=True),
        "weaviate": VectorProvider(name="weaviate", managed=True, requires_endpoint=True),
        "pgvector": VectorProvider(name="pgvector", managed=False, requires_endpoint=False),
        "memory": VectorProvider(name="memory", managed=False, requires_endpoint=False),
    }

    _ORG_CONFIG: dict[str, dict[str, Any]] = {}

    def list_providers(self) -> list[dict[str, object]]:
        return [
            {
                "name": provider.name,
                "managed": provider.managed,
                "requires_endpoint": provider.requires_endpoint,
            }
            for provider in self._AVAILABLE.values()
        ]

    def configure_org_provider(
        self,
        organization_id: str,
        provider: str,
        *,
        endpoint: str | None = None,
        index_name: str | None = None,
    ) -> dict[str, Any]:
        normalized = (provider or "").strip().lower()
        info = self._AVAILABLE.get(normalized)
        if not info:
            raise ValueError(f"Unsupported vector provider: {provider}")

        cleaned_endpoint = (endpoint or "").strip() or None
        if info.requires_endpoint and not cleaned_endpoint:
            raise ValueError(f"Provider '{normalized}' requires endpoint")

        config = {
            "provider": normalized,
            "endpoint": cleaned_endpoint,
            "index_name": (index_name or "").strip() or None,
            "managed": info.managed,
        }
        self._ORG_CONFIG[organization_id] = config
        return config

    def get_org_config(self, organization_id: str) -> dict[str, Any] | None:
        return self._ORG_CONFIG.get(organization_id)
