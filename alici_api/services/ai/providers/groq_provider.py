"""Groq provider using its OpenAI-compatible API."""

from __future__ import annotations

import os

from openai import AsyncOpenAI

from ..base import AIResponse, BaseAIProvider


class GroqProvider(BaseAIProvider):
    provider_name = "groq"

    def __init__(self):
        self.model_chat = os.getenv("GROQ_MODEL_CHAT", "llama-3.1-8b-instant")
        self.model_agent = os.getenv("GROQ_MODEL_AGENT", "llama-3.1-8b-instant")
        self.model_code = os.getenv("GROQ_MODEL_CODE", "qwen/qwen3-coder")
        self.client = AsyncOpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )

    async def chat(self, prompt: str, system_prompt: str = "") -> AIResponse:
        response = await self.client.chat.completions.create(
            model=self.model_chat,
            messages=[
                {"role": "system", "content": system_prompt or "Voce e a AXI, uma IA clara, objetiva e util."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=800,
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
                {"role": "system", "content": "Voce e um assistente senior de programacao. Gere codigo correto e direto."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=1400,
        )
        content = (response.choices[0].message.content or "").strip()
        tokens = response.usage.total_tokens if response.usage else 0
        return AIResponse(content=content, provider=self.provider_name, model=self.model_code, estimated_tokens=tokens)
