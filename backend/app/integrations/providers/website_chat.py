"""Website Chat provider adapter (widget embeddável)."""
from __future__ import annotations

from typing import Any

from app.integrations.providers.base import BaseProvider, ProviderResult


class WebsiteChatProvider(BaseProvider):
    def validate_config(self, config: dict[str, Any]) -> ProviderResult:
        # Website chat não requer credenciais externas — usa widget com agent_id
        return ProviderResult.ok("Configuração válida")

    def connect(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult.ok(
            "Widget de chat ativo. Incorpore o script no seu site.",
            provider="website_chat",
            widget_script_ready=True,
        )

    def disconnect(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult.ok("Widget de chat desabilitado")

    def sync(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult.ok("Widget de chat sincronizado com sucesso")

    def test_connection(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult.ok(
            "Widget de chat funcionando corretamente",
            provider="website_chat",
            latency_ms=0,
        )
