"""WhatsApp provider adapter."""
from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from app.integrations.providers.base import BaseProvider, ProviderResult


class WhatsAppProvider(BaseProvider):
    REQUIRED_CONFIG_FIELDS = ("phone_number_id", "access_token", "business_account_id")

    def validate_config(self, config: dict[str, Any]) -> ProviderResult:
        missing = [field for field in self.REQUIRED_CONFIG_FIELDS if not config.get(field)]
        if missing:
            return ProviderResult.fail(
                f"Campos obrigatorios ausentes: {', '.join(missing)}",
                missing_fields=missing,
            )
        return ProviderResult.ok("Configuracao valida")

    def connect(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return self.test_connection(config)

    def disconnect(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult.ok("WhatsApp desconectado com sucesso")

    def sync(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return self.test_connection(config)

    def test_connection(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation

        phone_number_id = str(config["phone_number_id"])
        access_token = str(config["access_token"])
        fields = "id,display_phone_number,verified_name"
        params = urllib.parse.urlencode({"fields": fields, "access_token": access_token})
        url = f"https://graph.facebook.com/v19.0/{urllib.parse.quote(phone_number_id)}?{params}"

        try:
            status_code = self._get(url)
        except urllib.error.HTTPError as exc:
            return ProviderResult.fail(
                f"Meta Graph respondeu HTTP {exc.code} para WhatsApp",
                provider="whatsapp",
                phone_number_id=phone_number_id,
                status_code=exc.code,
            )
        except Exception as exc:
            return ProviderResult.fail(
                f"Falha ao validar WhatsApp na Meta Graph API: {exc}",
                provider="whatsapp",
                phone_number_id=phone_number_id,
            )

        return ProviderResult.ok(
            "WhatsApp validado com chamada real na Meta Graph API.",
            provider="whatsapp",
            phone_number_id=phone_number_id,
            business_account_id=config.get("business_account_id"),
            status_code=status_code,
        )

    def _get(self, url: str) -> int:
        request = urllib.request.Request(url, headers={"User-Agent": "alici-ai/1.0"}, method="GET")
        with urllib.request.urlopen(request, timeout=10) as response:
            return int(response.status)
