"""Instagram provider adapter."""
from __future__ import annotations

from typing import Any

from app.integrations.providers.base import BaseProvider, ProviderResult


class InstagramProvider(BaseProvider):
    REQUIRED_CONFIG_FIELDS = ("instagram_account_id", "access_token")

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
        # TODO: Integrar com Instagram Messaging API (Meta)
        return ProviderResult.fail(
            "Integração Instagram pendente de configuração na Meta. "
            "Configure o instagram_account_id e access_token com permissão instagram_manage_messages.",
            provider="instagram",
            next_step="configure_meta_instagram",
        )

    def disconnect(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult.ok("Instagram desconectado com sucesso")

    def sync(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return ProviderResult.fail(
            "Sincronização Instagram requer token ativo com permissão instagram_manage_messages.",
            provider="instagram",
        )

    def test_connection(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return ProviderResult.fail(
            "Teste de conexão Instagram requer credenciais Meta ativas.",
            provider="instagram",
        )
