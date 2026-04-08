"""Webhook provider adapter."""
from __future__ import annotations

from typing import Any

from app.integrations.providers.base import BaseProvider, ProviderResult


class WebhookProvider(BaseProvider):
    REQUIRED_CONFIG_FIELDS = ("webhook_url",)

    def validate_config(self, config: dict[str, Any]) -> ProviderResult:
        webhook_url = str(config.get("webhook_url") or "")
        if not webhook_url:
            return ProviderResult.fail(
                "Campo obrigatório ausente: webhook_url",
                missing_fields=["webhook_url"],
            )
        if not webhook_url.startswith(("http://", "https://")):
            return ProviderResult.fail("webhook_url deve começar com http:// ou https://")
        return ProviderResult.ok("Configuração válida")

    def connect(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return ProviderResult.ok(
            "Webhook configurado. O agente enviará eventos para a URL informada.",
            provider="webhook",
            webhook_url=config.get("webhook_url"),
        )

    def disconnect(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult.ok("Webhook desconectado")

    def sync(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return ProviderResult.ok("Webhook registrado para eventos futuros", provider="webhook")

    def test_connection(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        # TODO: Enviar POST de teste para webhook_url
        return ProviderResult.ok(
            "URL do webhook válida. Aguardando confirmação de recebimento.",
            provider="webhook",
            webhook_url=config.get("webhook_url"),
        )
