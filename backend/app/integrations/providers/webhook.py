"""Webhook provider adapter."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from app.integrations.providers.base import BaseProvider, ProviderResult
from app.integrations.providers.http_security import UnsafeProviderURL, assert_public_http_url


class WebhookProvider(BaseProvider):
    REQUIRED_CONFIG_FIELDS = ("webhook_url",)

    def validate_config(self, config: dict[str, Any]) -> ProviderResult:
        webhook_url = str(config.get("webhook_url") or "")
        if not webhook_url:
            return ProviderResult.fail(
                "Campo obrigatorio ausente: webhook_url",
                missing_fields=["webhook_url"],
            )
        if not webhook_url.startswith(("http://", "https://")):
            return ProviderResult.fail("webhook_url deve comecar com http:// ou https://")
        try:
            assert_public_http_url(webhook_url)
        except UnsafeProviderURL as exc:
            return ProviderResult.fail(str(exc))
        return ProviderResult.ok("Configuracao valida")

    def connect(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return self.test_connection(config)

    def disconnect(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult.ok("Webhook desconectado")

    def sync(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return self.test_connection(config)

    def test_connection(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation

        webhook_url = str(config.get("webhook_url"))
        payload = {
            "event": "axi.connection_test",
            "provider": "webhook",
            "test": True,
        }
        headers = self._build_headers(config)

        try:
            status_code = self._post_json(webhook_url, payload=payload, headers=headers)
        except urllib.error.HTTPError as exc:
            return ProviderResult.fail(
                f"Webhook respondeu HTTP {exc.code}",
                provider="webhook",
                webhook_url=webhook_url,
                status_code=exc.code,
            )
        except Exception as exc:
            return ProviderResult.fail(
                f"Falha ao validar webhook com POST real: {exc}",
                provider="webhook",
                webhook_url=webhook_url,
            )

        return ProviderResult.ok(
            "Webhook validado com POST real.",
            provider="webhook",
            webhook_url=webhook_url,
            status_code=status_code,
        )

    def _build_headers(self, config: dict[str, Any]) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "alici-ai/1.0",
        }
        extra_headers = config.get("headers")
        if isinstance(extra_headers, dict):
            headers.update({str(key): str(value) for key, value in extra_headers.items()})
        secret = config.get("secret")
        if secret and "X-AXI-Webhook-Secret" not in headers:
            headers["X-AXI-Webhook-Secret"] = str(secret)
        return headers

    def _post_json(self, url: str, *, payload: dict[str, Any], headers: dict[str, str]) -> int:
        body = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=10) as response:
            return int(response.status)
