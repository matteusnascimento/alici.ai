"""Email provider adapter."""
from __future__ import annotations

import smtplib
import ssl
from typing import Any

from app.integrations.providers.base import BaseProvider, ProviderResult


class EmailProvider(BaseProvider):
    REQUIRED_CONFIG_FIELDS = ("smtp_host", "smtp_port", "smtp_user", "smtp_password")

    def validate_config(self, config: dict[str, Any]) -> ProviderResult:
        missing = [field for field in self.REQUIRED_CONFIG_FIELDS if not config.get(field)]
        if missing:
            return ProviderResult.fail(
                f"Campos obrigatorios ausentes: {', '.join(missing)}",
                missing_fields=missing,
            )
        try:
            int(config["smtp_port"])
        except (TypeError, ValueError):
            return ProviderResult.fail("smtp_port deve ser numerico")
        return ProviderResult.ok("Configuracao valida")

    def connect(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return self.test_connection(config)

    def disconnect(self, config: dict[str, Any]) -> ProviderResult:
        return ProviderResult.ok("Email desconectado com sucesso")

    def sync(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation
        return ProviderResult.fail(
            "SMTP nao possui sincronizacao de dados; use test_connection para validar credenciais.",
            provider="email",
        )

    def test_connection(self, config: dict[str, Any]) -> ProviderResult:
        validation = self.validate_config(config)
        if not validation.success:
            return validation

        host = str(config["smtp_host"])
        port = int(config["smtp_port"])
        user = str(config["smtp_user"])
        password = str(config["smtp_password"])
        use_ssl = self._truthy(config.get("smtp_ssl")) or port == 465
        use_tls = self._truthy(config.get("smtp_tls", True)) and not use_ssl

        try:
            if use_ssl:
                context = ssl.create_default_context()
                server: smtplib.SMTP = smtplib.SMTP_SSL(host, port, timeout=10, context=context)
            else:
                server = smtplib.SMTP(host, port, timeout=10)
                server.ehlo()
                if use_tls:
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()
            try:
                server.login(user, password)
            finally:
                server.quit()
        except Exception as exc:
            return ProviderResult.fail(
                f"Falha ao validar SMTP: {exc}",
                provider="email",
                smtp_host=host,
                smtp_port=port,
            )

        return ProviderResult.ok(
            "SMTP validado com login real.",
            provider="email",
            smtp_host=host,
            smtp_port=port,
        )

    def _truthy(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "sim", "on"}
        return bool(value)
