"""CRM provider adapter."""
from __future__ import annotations

from typing import Any

from app.integrations.providers.base import BaseProvider, ProviderResult

SUPPORTED_CRMS = ("hubspot", "salesforce", "pipedrive", "rd_station", "custom")


class CRMProvider(BaseProvider):
    REQUIRED_CONFIG_FIELDS = ("crm_type", "api_key")

    def validate_config(self, config: dict[str, Any]) -> ProviderResult:
        missing = [f for f in self.REQUIRED_CONFIG_FIELDS if not config.get(f)]
        if missing:
            return ProviderResult.fail(
                f"Campos obrigatórios ausentes: {', '.join(missing)}",
                missing_fields=missing,
            )
        crm_type = str(config.get("crm_type", "")).lower()
        if crm_type not in SUPPORTED_CRMS:
            return ProviderResult.fail(
                f"CRM '{crm_type}' não suportado. Opções: {', '.join(SUPPORTED_CRMS)}",
                supported=list(SUPPORTED_CRMS),
            )
        return ProviderResult.ok("Configuração válida")

    def connect(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        # TODO: Integrar com APIs CRM (HubSpot, Salesforce, etc.)
        return ProviderResult.fail(
            f"Integração CRM ({config.get('crm_type')}) pendente de implementação. "
            "Configure crm_type e api_key válidos.",
            provider="crm",
            crm_type=config.get("crm_type"),
            next_step="configure_crm_credentials",
        )

    def disconnect(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult.ok("CRM desconectado com sucesso")

    def sync(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return ProviderResult.fail(
            "Sincronização CRM requer credenciais ativas.",
            provider="crm",
        )

    def test_connection(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return ProviderResult.fail(
            "Teste de conexão CRM requer API key válida.",
            provider="crm",
        )
