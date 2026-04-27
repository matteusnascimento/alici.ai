"""CRM provider adapter."""
from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from app.integrations.providers.base import BaseProvider, ProviderResult

SUPPORTED_CRMS = ("hubspot", "salesforce", "pipedrive", "rd_station", "custom")


class CRMProvider(BaseProvider):
    REQUIRED_CONFIG_FIELDS = ("crm_type", "api_key")

    def validate_config(self, config: dict[str, Any]) -> ProviderResult:
        missing = [field for field in self.REQUIRED_CONFIG_FIELDS if not config.get(field)]
        if missing:
            return ProviderResult.fail(
                f"Campos obrigatorios ausentes: {', '.join(missing)}",
                missing_fields=missing,
            )
        crm_type = str(config.get("crm_type", "")).lower()
        if crm_type not in SUPPORTED_CRMS:
            return ProviderResult.fail(
                f"CRM '{crm_type}' nao suportado. Opcoes: {', '.join(SUPPORTED_CRMS)}",
                supported=list(SUPPORTED_CRMS),
            )
        if crm_type in {"salesforce", "custom"} and not config.get("api_url"):
            return ProviderResult.fail(
                f"CRM '{crm_type}' exige api_url para teste real",
                missing_fields=["api_url"],
            )
        return ProviderResult.ok("Configuracao valida")

    def connect(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return self.test_connection(config)

    def disconnect(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult.ok("CRM desconectado com sucesso")

    def sync(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return self.test_connection(config)

    def test_connection(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation

        crm_type = str(config["crm_type"]).lower()
        api_key = str(config["api_key"])
        url, headers = self._build_healthcheck(crm_type, api_key, config)

        try:
            status_code = self._get(url, headers=headers)
        except urllib.error.HTTPError as exc:
            return ProviderResult.fail(
                f"CRM {crm_type} respondeu HTTP {exc.code}",
                provider="crm",
                crm_type=crm_type,
                status_code=exc.code,
            )
        except Exception as exc:
            return ProviderResult.fail(
                f"Falha ao validar CRM {crm_type}: {exc}",
                provider="crm",
                crm_type=crm_type,
            )

        return ProviderResult.ok(
            f"CRM {crm_type} validado com chamada real.",
            provider="crm",
            crm_type=crm_type,
            status_code=status_code,
        )

    def _build_healthcheck(self, crm_type: str, api_key: str, config: dict[str, Any]) -> tuple[str, dict[str, str]]:
        headers = {"User-Agent": "alici-ai/1.0"}
        if crm_type == "hubspot":
            headers["Authorization"] = f"Bearer {api_key}"
            return "https://api.hubapi.com/crm/v3/objects/contacts?limit=1", headers
        if crm_type == "pipedrive":
            params = urllib.parse.urlencode({"api_token": api_key})
            return f"https://api.pipedrive.com/v1/users/me?{params}", headers
        if crm_type == "rd_station":
            headers["Authorization"] = f"Bearer {api_key}"
            return "https://api.rd.services/platform/contacts/fields", headers

        api_url = str(config["api_url"]).rstrip("/")
        headers["Authorization"] = f"Bearer {api_key}"
        if crm_type == "salesforce":
            return f"{api_url}/services/data/", headers
        return api_url, headers

    def _get(self, url: str, *, headers: dict[str, str]) -> int:
        request = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(request, timeout=10) as response:
            return int(response.status)
