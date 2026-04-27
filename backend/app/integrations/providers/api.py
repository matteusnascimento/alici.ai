"""API provider adapter."""
from __future__ import annotations

import urllib.error
import urllib.request
from typing import Any

from app.integrations.providers.base import BaseProvider, ProviderResult


class APIProvider(BaseProvider):
    REQUIRED_CONFIG_FIELDS = ("api_url",)

    def validate_config(self, config: dict[str, Any]) -> ProviderResult:
        missing = [field for field in self.REQUIRED_CONFIG_FIELDS if not config.get(field)]
        if missing:
            return ProviderResult.fail(
                f"Campos obrigatorios ausentes: {', '.join(missing)}",
                missing_fields=missing,
            )
        api_url = str(config.get("api_url", ""))
        if not api_url.startswith(("http://", "https://")):
            return ProviderResult.fail("api_url deve comecar com http:// ou https://")
        return ProviderResult.ok("Configuracao valida")

    def connect(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return self.test_connection(config)

    def disconnect(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult.ok("Integracao API desconectada")

    def sync(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return self.test_connection(config)

    def test_connection(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation

        api_url = str(config.get("api_url"))
        headers = self._build_headers(config)
        try:
            status_code = self._request(api_url, headers=headers, method="HEAD")
        except urllib.error.HTTPError as exc:
            if exc.code in {405, 501}:
                try:
                    status_code = self._request(api_url, headers=headers, method="GET")
                except Exception as retry_exc:
                    return ProviderResult.fail(
                        f"Falha ao validar endpoint de API: {retry_exc}",
                        provider="api",
                        api_url=api_url,
                    )
            else:
                return ProviderResult.fail(
                    f"Endpoint de API respondeu HTTP {exc.code}",
                    provider="api",
                    api_url=api_url,
                    status_code=exc.code,
                )
        except Exception as exc:
            return ProviderResult.fail(
                f"Falha ao validar endpoint de API: {exc}",
                provider="api",
                api_url=api_url,
            )

        return ProviderResult.ok(
            "Endpoint de API validado com chamada real.",
            provider="api",
            api_url=api_url,
            status_code=status_code,
        )

    def _build_headers(self, config: dict[str, Any]) -> dict[str, str]:
        headers = {"User-Agent": "alici-ai/1.0"}
        extra_headers = config.get("headers")
        if isinstance(extra_headers, dict):
            headers.update({str(key): str(value) for key, value in extra_headers.items()})
        api_key = config.get("api_key") or config.get("token")
        if api_key and "Authorization" not in headers:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def _request(self, url: str, *, headers: dict[str, str], method: str) -> int:
        request = urllib.request.Request(url, headers=headers, method=method)
        with urllib.request.urlopen(request, timeout=10) as response:
            return int(response.status)
