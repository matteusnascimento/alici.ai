"""WhatsApp provider adapter."""
from __future__ import annotations

from typing import Any

from app.integrations.providers.base import BaseProvider, ProviderResult


class WhatsAppProvider(BaseProvider):
    REQUIRED_CONFIG_FIELDS = ("phone_number_id", "access_token", "business_account_id")

    def validate_config(self, config: dict[str, Any]) -> ProviderResult:
        missing = [f for f in self.REQUIRED_CONFIG_FIELDS if not config.get(f)]
        if missing:
            return ProviderResult.fail(
                f"Campos obrigatórios ausentes: {', '.join(missing)}",
                missing_fields=missing,
            )
        return ProviderResult.ok("Configuração válida")

    def connect(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        # TODO: Integrar com WhatsApp Business API (Meta Graph API)
        # Endpoint: POST https://graph.facebook.com/v19.0/{phone_number_id}/register
        return ProviderResult.fail(
            "Integração WhatsApp pendente de configuração na Meta. "
            "Configure o phone_number_id, access_token e business_account_id no painel Meta Business.",
            provider="whatsapp",
            next_step="configure_meta_business",
        )

    def disconnect(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult.ok("WhatsApp desconectado com sucesso")

    def sync(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return ProviderResult.fail(
            "Sincronização WhatsApp requer configuração ativa da Meta Business API.",
            provider="whatsapp",
        )

    def test_connection(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return ProviderResult.fail(
            "Teste de conexão WhatsApp requer credenciais Meta ativas.",
            provider="whatsapp",
        )
