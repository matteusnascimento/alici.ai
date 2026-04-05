import base64
import json
from pathlib import Path
from typing import Any

import httpx

from app.core.config import settings
from app.services.model_router import AIFunction, get_model_for


class OpenAIServiceError(RuntimeError):
    pass


class OpenAIService:
    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        self.default_model = settings.openai_model
        self.timeout_seconds = settings.openai_timeout_seconds
        self.base_url = "https://api.openai.com/v1"

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _post_json(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            raise OpenAIServiceError("OPENAI_API_KEY is not configured")

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(f"{self.base_url}{endpoint}", json=payload, headers=self._headers())
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise OpenAIServiceError("OpenAI request timed out") from exc
        except httpx.HTTPError as exc:
            raise OpenAIServiceError(f"OpenAI request failed: {exc}") from exc
        return response.json()

    def _extract_output_text(self, data: dict[str, Any]) -> str:
        if data.get("output_text"):
            return str(data["output_text"])

        output = data.get("output") or []
        for item in output:
            for content in item.get("content", []):
                if content.get("type") in {"output_text", "text"} and content.get("text"):
                    return str(content["text"])
        return ""

    def chat(self, prompt: str, system: str | None = None, premium: bool = False) -> dict[str, Any]:
        model = get_model_for(AIFunction.CHAT_PREMIUM if premium else AIFunction.CHAT)
        input_items: list[dict[str, Any]] = []
        if system:
            input_items.append(
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": system}],
                }
            )
        input_items.append(
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            }
        )

        data = self._post_json("/responses", {"model": model, "input": input_items})
        return {
            "model": data.get("model", model),
            "text": self._extract_output_text(data),
            "raw": data,
        }

    def marketing_copy(self, prompt: str) -> dict[str, Any]:
        model = get_model_for(AIFunction.MARKETING_COPY)
        data = self._post_json(
            "/responses",
            {
                "model": model,
                "input": f"Crie uma copy de marketing profissional em pt-BR:\n\n{prompt}",
            },
        )
        return {
            "model": data.get("model", model),
            "text": self._extract_output_text(data),
            "raw": data,
        }

    def structured_extract(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        model = get_model_for(AIFunction.STRUCTURED_EXTRACTION)
        data = self._post_json(
            "/responses",
            {
                "model": model,
                "input": prompt,
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": "structured_output",
                        "schema": schema,
                    }
                },
            },
        )
        return {
            "model": data.get("model", model),
            "text": self._extract_output_text(data),
            "raw": data,
        }

    def analyze_image_bytes(self, image_bytes: bytes, prompt: str) -> dict[str, Any]:
        model = get_model_for(AIFunction.IMAGE_ANALYSIS)
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data = self._post_json(
            "/responses",
            {
                "model": model,
                "input": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            {"type": "input_image", "image_url": f"data:image/jpeg;base64,{b64}"},
                        ],
                    }
                ],
            },
        )
        return {
            "model": data.get("model", model),
            "text": self._extract_output_text(data),
            "raw": data,
        }

    def generate_image(self, prompt: str, size: str = "1024x1024") -> dict[str, Any]:
        model = get_model_for(AIFunction.IMAGE_GENERATION)
        data = self._post_json(
            "/images/generations",
            {
                "model": model,
                "prompt": prompt,
                "size": size,
                "response_format": "b64_json",
            },
        )
        image_b64 = (data.get("data") or [{}])[0].get("b64_json")
        return {
            "model": model,
            "b64_json": image_b64,
            "raw": data,
        }

    def transcribe_audio(self, audio_path: str, fast: bool = False) -> dict[str, Any]:
        if not self.api_key:
            raise OpenAIServiceError("OPENAI_API_KEY is not configured")

        model = get_model_for(AIFunction.AUDIO_TRANSCRIPTION_FAST if fast else AIFunction.AUDIO_TRANSCRIPTION)
        path = Path(audio_path)

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                with path.open("rb") as audio_file:
                    response = client.post(
                        f"{self.base_url}/audio/transcriptions",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        data={"model": model},
                        files={"file": (path.name, audio_file, "application/octet-stream")},
                    )
                    response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise OpenAIServiceError("OpenAI transcription timed out") from exc
        except httpx.HTTPError as exc:
            raise OpenAIServiceError(f"OpenAI request failed: {exc}") from exc

        data = response.json()
        return {
            "model": model,
            "text": data.get("text", ""),
            "raw": data,
        }

    def text_to_speech(self, text: str, voice: str = "alloy", output_path: str = "speech.mp3") -> dict[str, Any]:
        if not self.api_key:
            raise OpenAIServiceError("OPENAI_API_KEY is not configured")

        model = get_model_for(AIFunction.TEXT_TO_SPEECH)
        payload = {
            "model": model,
            "voice": voice,
            "input": text,
        }

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/audio/speech",
                    json=payload,
                    headers=self._headers(),
                )
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise OpenAIServiceError("OpenAI speech request timed out") from exc
        except httpx.HTTPError as exc:
            raise OpenAIServiceError(f"OpenAI request failed: {exc}") from exc

        Path(output_path).write_bytes(response.content)
        return {
            "model": model,
            "file_path": output_path,
        }

    def embed(self, texts: list[str], high_quality: bool = False) -> dict[str, Any]:
        model = get_model_for(AIFunction.EMBEDDING_HIGH if high_quality else AIFunction.EMBEDDING)
        data = self._post_json(
            "/embeddings",
            {
                "model": model,
                "input": texts,
            },
        )
        vectors = [item.get("embedding", []) for item in data.get("data", [])]
        return {
            "model": model,
            "vectors": vectors,
            "raw": data,
        }

    def healthcheck(self) -> dict[str, Any]:
        try:
            result = self.chat("Responda apenas: OK")
            return {
                "status": "ok",
                "model": result["model"],
                "message": result.get("text", ""),
            }
        except Exception as exc:
            return {
                "status": "error",
                "message": str(exc),
            }

    # Backward-compatible wrappers used in existing services/routes.
    def send_chat_message(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        if not messages:
            raise OpenAIServiceError("messages cannot be empty")

        payload = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        response = self._post_json("/chat/completions", payload)
        content = ""
        choices = response.get("choices") or []
        if choices:
            content = choices[0].get("message", {}).get("content", "")
        return {
            "content": content,
            "model": response.get("model", model or self.default_model),
            "usage": response.get("usage"),
            "raw": response,
        }

    def generate_marketing_copy(self, prompt: str) -> str:
        result = self.marketing_copy(prompt)
        return result.get("text", "")

    def summarize_text(self, text: str) -> str:
        result = self.chat(
            prompt=text,
            system="Summarize clearly in pt-BR.",
            premium=False,
        )
        return result.get("text", "")

    def generate_agent_system_prompt(self, config: dict[str, Any]) -> str:
        compact_config = json.dumps(config, ensure_ascii=True)
        result = self.chat(
            prompt=f"Agent config: {compact_config}",
            system="Create robust system prompts for AI agents.",
            premium=True,
        )
        return result.get("text", "")
