"""Base AI Provider Interface for AXI."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if provider is properly configured."""
        pass

    @abstractmethod
    async def chat(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        Send a chat message to the provider.

        Args:
            prompt: User message
            system_prompt: System instructions
            temperature: Generation temperature (0-1)
            max_tokens: Maximum tokens in response
            model: Specific model to use (optional)

        Returns:
            Dict with keys:
            - content: str (response text)
            - model: str (model used)
            - usage: dict (tokens info, if available)
            - latency_ms: float (response time)
        """
        pass

    @abstractmethod
    async def summarize(
        self,
        text: str,
        max_length: int | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        Summarize text.

        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            model: Specific model to use (optional)

        Returns:
            Dict with keys:
            - content: str (summary)
            - model: str (model used)
            - latency_ms: float
        """
        pass

    @abstractmethod
    async def generate_code(
        self,
        prompt: str,
        language: str = "python",
        model: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate code based on description.

        Args:
            prompt: Code generation request
            language: Programming language
            model: Specific model to use (optional)

        Returns:
            Dict with keys:
            - content: str (generated code)
            - model: str (model used)
            - latency_ms: float
        """
        pass
