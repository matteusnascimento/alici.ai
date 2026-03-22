import json
from typing import Any

import httpx

from app.core.config import settings


class OpenAIServiceError(RuntimeError):
    pass


class OpenAIService:
    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        self.default_model = settings.openai_model
        self.timeout_seconds = settings.openai_timeout_seconds

    def send_chat_message(self, messages: list[dict], model: str | None = None, temperature: float = 0.2) -> dict[str, Any]:
        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
        }
        return self._post_chat(payload)

    def generate_marketing_copy(self, prompt: str) -> str:
        response = self.send_chat_message(
            messages=[
                {"role": "system", "content": "You are a senior direct response copywriter."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        return response["content"]

    def summarize_text(self, text: str) -> str:
        response = self.send_chat_message(
            messages=[
                {"role": "system", "content": "Summarize clearly in pt-BR."},
                {"role": "user", "content": text},
            ],
            temperature=0.1,
        )
        return response["content"]

    def generate_agent_system_prompt(self, config: dict[str, Any]) -> str:
        compact_config = json.dumps(config, ensure_ascii=True)
        response = self.send_chat_message(
            messages=[
                {"role": "system", "content": "Create robust system prompts for AI agents."},
                {"role": "user", "content": f"Agent config: {compact_config}"},
            ],
            temperature=0.3,
        )
        return response["content"]

    def _post_chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            raise OpenAIServiceError("OPENAI_API_KEY is not configured")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise OpenAIServiceError("OpenAI request timed out") from exc
        except httpx.HTTPError as exc:
            raise OpenAIServiceError(f"OpenAI request failed: {exc}") from exc

        data = response.json()
        content = ""
        if data.get("choices"):
            content = data["choices"][0].get("message", {}).get("content", "")

        return {
            "content": content,
            "model": data.get("model", payload.get("model", self.default_model)),
            "usage": data.get("usage"),
            "raw": data,
        }
