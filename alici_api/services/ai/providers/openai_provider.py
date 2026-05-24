"""OpenAI provider kept for future paid compatibility."""

from __future__ import annotations

import os

from openai import AsyncOpenAI

from ..base import AIResponse, BaseAIProvider


class OpenAIProvider(BaseAIProvider):
    provider_name = "openai"

    def __init__(self):
        self.model = os.getenv("OPENAI_MODEL_CHAT_GENERAL", "gpt-4o-mini")
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def chat(self, prompt: str, system_prompt: str = "") -> AIResponse:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt or "Voce e a AXI, uma IA clara, objetiva e util."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=800,
        )
        content = (response.choices[0].message.content or "").strip()
        tokens = response.usage.total_tokens if response.usage else 0
        return AIResponse(content=content, provider=self.provider_name, model=self.model, estimated_tokens=tokens)

    async def summarize(self, text: str) -> AIResponse:
        return await self.chat(f"Resuma o texto abaixo de forma clara e objetiva:\n\n{text}")

    async def generate_code(self, prompt: str) -> AIResponse:
        return await self.chat(prompt, "Voce e um assistente senior de programacao. Gere codigo correto e direto.")
