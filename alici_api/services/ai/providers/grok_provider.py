"""Grok/xAI provider using the OpenAI-compatible API."""

from __future__ import annotations

import httpx
from openai import AsyncOpenAI

from alici_api.config import get_settings

from ..base import AIResponse, BaseAIProvider


class GrokProvider(BaseAIProvider):
    provider_name = "grok"

    def __init__(self):
        settings = get_settings()
        api_key = settings.resolved_grok_api_key
        if not api_key:
            raise RuntimeError("GROK_API_KEY ou XAI_API_KEY nao configurada")

        self.model_chat = settings.grok_model_chat
        self.model_agent = settings.grok_model_agent
        self.model_code = settings.grok_model_code
        self.client = AsyncOpenAI(
            api_key=api_key.get_secret_value(),
            base_url=settings.grok_base_url.rstrip("/"),
            timeout=httpx.Timeout(float(settings.grok_timeout_seconds)),
        )

    async def chat(self, prompt: str, system_prompt: str = "") -> AIResponse:
        response = await self.client.chat.completions.create(
            model=self.model_chat,
            messages=[
                {"role": "system", "content": system_prompt or "Voce e a ALICI, uma IA clara, objetiva e util."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
            max_tokens=900,
        )
        content = (response.choices[0].message.content or "").strip()
        tokens = response.usage.total_tokens if response.usage else 0
        return AIResponse(content=content, provider=self.provider_name, model=self.model_chat, estimated_tokens=tokens)

    async def summarize(self, text: str) -> AIResponse:
        return await self.chat(f"Resuma o texto abaixo de forma clara e objetiva:\n\n{text}")

    async def generate_code(self, prompt: str) -> AIResponse:
        response = await self.client.chat.completions.create(
            model=self.model_code,
            messages=[
                {"role": "system", "content": "Voce e um engenheiro senior. Gere codigo correto, direto e seguro."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1600,
        )
        content = (response.choices[0].message.content or "").strip()
        tokens = response.usage.total_tokens if response.usage else 0
        return AIResponse(content=content, provider=self.provider_name, model=self.model_code, estimated_tokens=tokens)
