"""Email provider adapter."""
from __future__ import annotations

from typing import Any

from app.integrations.providers.base import BaseProvider, ProviderResult


class EmailProvider(BaseProvider):
    REQUIRED_CONFIG_FIELDS = ("smtp_host", "smtp_port", "smtp_user", "smtp_password")

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
        # TODO: Testar conexão SMTP real
        return ProviderResult.fail(
            "Integração Email requer configuração SMTP ativa. "
            "Informe smtp_host, smtp_port, smtp_user e smtp_password.",
            provider="email",
            next_step="configure_smtp",
        )

    def disconnect(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult.ok("Email desconectado com sucesso")

    def sync(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return ProviderResult.fail(
            "Sincronização Email requer servidor SMTP configurado e acessível.",
            provider="email",
        )

    def test_connection(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return ProviderResult.fail(
            "Teste de conexão Email requer configuração SMTP válida.",
            provider="email",
        )
