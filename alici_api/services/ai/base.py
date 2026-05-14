"""Base interfaces for AI providers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AIResponse:
    content: str
    provider: str
    model: str
    response_time_ms: int = 0
    estimated_tokens: int = 0
    cached: bool = False


class BaseAIProvider:
    provider_name = "base"

    async def chat(self, prompt: str, system_prompt: str = "") -> AIResponse:
        raise NotImplementedError

    async def summarize(self, text: str) -> AIResponse:
        raise NotImplementedError

    async def generate_code(self, prompt: str) -> AIResponse:
        raise NotImplementedError
