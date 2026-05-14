"""Local Ollama provider."""

from __future__ import annotations

import os

import httpx

from ..base import AIResponse, BaseAIProvider


class OllamaProvider(BaseAIProvider):
    provider_name = "ollama"

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "llama3")

    async def _generate(self, prompt: str) -> AIResponse:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            data = response.json()
            return AIResponse(
                content=(data.get("response") or "").strip(),
                provider=self.provider_name,
                model=self.model,
                estimated_tokens=int(data.get("eval_count") or 0),
            )

    async def chat(self, prompt: str, system_prompt: str = "") -> AIResponse:
        full_prompt = f"{system_prompt.strip()}\n\nUsuario: {prompt}\nAXI:" if system_prompt else prompt
        return await self._generate(full_prompt)

    async def summarize(self, text: str) -> AIResponse:
        return await self._generate(f"Resuma o texto abaixo de forma clara e objetiva:\n\n{text}")

    async def generate_code(self, prompt: str) -> AIResponse:
        return await self._generate(f"Voce e um assistente senior de programacao. Gere codigo correto e direto.\n\n{prompt}")
