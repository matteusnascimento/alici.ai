"""Base interface for channel provider adapters."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderResult:
    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(cls, message: str = "OK", **kwargs: Any) -> "ProviderResult":
        return cls(success=True, message=message, data=kwargs)

    @classmethod
    def fail(cls, message: str, **kwargs: Any) -> "ProviderResult":
        return cls(success=False, message=message, data=kwargs)


class BaseProvider(ABC):
    """Contrato base que todo provider deve implementar."""

    @abstractmethod
    def validate_config(self, config: dict[str, Any]) -> ProviderResult:
        """Valida se a config tem os campos obrigatórios para este provider."""

    @abstractmethod
    def connect(self, config: dict[str, Any]) -> ProviderResult:
        """Tenta estabelecer conexão com o provider externo."""

    @abstractmethod
    def disconnect(self, config: dict[str, Any]) -> ProviderResult:
        """Remove a conexão ativa."""

    @abstractmethod
    def sync(self, config: dict[str, Any]) -> ProviderResult:
        """Sincroniza dados com o provider (webhook, contatos, etc.)."""

    @abstractmethod
    def test_connection(self, config: dict[str, Any]) -> ProviderResult:
        """Testa a conexão sem executar sincronização completa."""
