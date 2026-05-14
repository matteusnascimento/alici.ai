"""Gemini provider."""

from __future__ import annotations

import asyncio
import os

import google.generativeai as genai

from ..base import AIResponse, BaseAIProvider


class GeminiProvider(BaseAIProvider):
    provider_name = "gemini"

    def __init__(self):
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(self.model_name)

    async def _generate(self, prompt: str) -> AIResponse:
        response = await asyncio.to_thread(self.model.generate_content, prompt)
        content = (getattr(response, "text", "") or "").strip()
        return AIResponse(content=content, provider=self.provider_name, model=self.model_name)

    async def chat(self, prompt: str, system_prompt: str = "") -> AIResponse:
        full_prompt = f"{system_prompt.strip()}\n\n{prompt}" if system_prompt else prompt
        return await self._generate(full_prompt)

    async def summarize(self, text: str) -> AIResponse:
        return await self._generate(f"Resuma o texto abaixo de forma clara e objetiva:\n\n{text}")

    async def generate_code(self, prompt: str) -> AIResponse:
        return await self._generate(f"Voce e um assistente senior de programacao. Gere codigo correto e direto.\n\n{prompt}")
