"""API provider adapter (integração via REST API externa)."""
from __future__ import annotations

from typing import Any

from app.integrations.providers.base import BaseProvider, ProviderResult


class APIProvider(BaseProvider):
    REQUIRED_CONFIG_FIELDS = ("api_url",)

    def validate_config(self, config: dict[str, Any]) -> ProviderResult:
        missing = [f for f in self.REQUIRED_CONFIG_FIELDS if not config.get(f)]
        if missing:
            return ProviderResult.fail(
                f"Campos obrigatórios ausentes: {', '.join(missing)}",
                missing_fields=missing,
            )
        api_url = str(config.get("api_url", ""))
        if not api_url.startswith(("http://", "https://")):
            return ProviderResult.fail("api_url deve começar com http:// ou https://")
        return ProviderResult.ok("Configuração válida")

    def connect(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return ProviderResult.ok(
            "Integração API configurada. O agente enviará e receberá chamadas no endpoint informado.",
            provider="api",
            api_url=config.get("api_url"),
        )

    def disconnect(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult.ok("Integração API desconectada")

    def sync(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return ProviderResult.ok("API sincronizada", provider="api")

    def test_connection(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        # TODO: Fazer HEAD/GET no api_url para testar disponibilidade
        return ProviderResult.ok(
            "Endpoint de API configurado corretamente.",
            provider="api",
            api_url=config.get("api_url"),
        )
