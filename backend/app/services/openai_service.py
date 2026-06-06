import base64
import json
import logging
import time
from pathlib import Path
from typing import Any

import httpx
from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError, OpenAI, RateLimitError

from app.core.config import settings
from app.services.model_router import AIFunction, get_model_for


class OpenAIServiceError(RuntimeError):
    def __init__(self, message: str, *, error_type: str = "openai_error", status_code: int = 503) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.status_code = status_code


logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self) -> None:
        self.api_key = settings.effective_openai_api_key
        self.default_model = settings.effective_openai_chat_model
        self.timeout_seconds = settings.openai_timeout_seconds
        self.base_url = "https://api.openai.com/v1"
        self.client = OpenAI(api_key=self.api_key, timeout=self.timeout_seconds) if self.api_key else None

        logger.info(
            "openai.service.init api_key=%s model=%s timeout_seconds=%s",
            "set" if self.api_key else "missing",
            self.default_model,
            self.timeout_seconds,
        )

    @staticmethod
    def _uploads_root() -> Path:
        path = Path(__file__).resolve().parents[2] / "uploads"
        path.mkdir(parents=True, exist_ok=True)
        return path.resolve()

    @classmethod
    def _resolve_upload_path(cls, raw_path: str) -> Path:
        path = Path(raw_path).resolve()
        uploads_root = cls._uploads_root()
        try:
            path.relative_to(uploads_root)
        except ValueError as exc:
            raise OpenAIServiceError(
                "Audio path must be inside backend uploads",
                error_type="invalid_path",
                status_code=400,
            ) from exc
        return path

    @classmethod
    def _resolve_speech_output_path(cls, raw_path: str) -> Path:
        output_dir = cls._uploads_root() / "speech"
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = Path(raw_path or "speech.mp3").name
        if Path(filename).suffix.lower() != ".mp3":
            filename = f"{Path(filename).stem or 'speech'}.mp3"
        return output_dir / filename

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _post_json(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            raise OpenAIServiceError("OPENAI_API_KEY is not configured", error_type="missing_api_key", status_code=503)

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(f"{self.base_url}{endpoint}", json=payload, headers=self._headers())
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise OpenAIServiceError("OpenAI request timed out", error_type="timeout", status_code=504) from exc
        except httpx.HTTPError as exc:
            message = str(exc)
            status_code = 502
            if "401" in message or "403" in message:
                status_code = 401
            elif "429" in message:
                status_code = 429
            raise OpenAIServiceError(
                f"OpenAI request failed: {message}",
                error_type="http_error",
                status_code=status_code,
            ) from exc
        return response.json()

    def _classify_openai_error(self, exc: Exception) -> OpenAIServiceError:
        if isinstance(exc, OpenAIServiceError):
            return exc
        if isinstance(exc, AuthenticationError):
            return OpenAIServiceError("OpenAI authentication failed", error_type="invalid_api_key", status_code=401)
        if isinstance(exc, RateLimitError):
            return OpenAIServiceError("OpenAI rate limit reached", error_type="rate_limit", status_code=429)
        if isinstance(exc, APITimeoutError):
            return OpenAIServiceError("OpenAI request timed out", error_type="timeout", status_code=504)
        if isinstance(exc, APIConnectionError):
            return OpenAIServiceError("OpenAI network connection error", error_type="network_error", status_code=503)
        if isinstance(exc, APIError):
            status = getattr(exc, "status_code", None) or 503
            return OpenAIServiceError(f"OpenAI API error: {exc}", error_type="api_error", status_code=status)
        return OpenAIServiceError(f"OpenAI request failed: {exc}", error_type="unknown_error", status_code=503)

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
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        result = self.send_chat_message(messages=messages, model=model)
        return {
            "model": result.get("model", model),
            "text": str(result.get("content") or "").strip(),
            "raw": result.get("raw", {}),
            "latency_ms": result.get("latency_ms"),
        }

    def marketing_copy(self, prompt: str) -> dict[str, Any]:
        model = get_model_for(AIFunction.MARKETING_COPY)
        result = self.send_chat_message(
            messages=[
                {
                    "role": "user",
                    "content": f"Crie uma copy de marketing profissional em pt-BR:\n\n{prompt}",
                }
            ],
            model=model,
            temperature=0.4,
        )
        return {
            "model": result.get("model", model),
            "text": str(result.get("content") or "").strip(),
            "raw": result.get("raw", {}),
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
            raise OpenAIServiceError("OPENAI_API_KEY is not configured", error_type="missing_api_key", status_code=503)

        model = get_model_for(AIFunction.AUDIO_TRANSCRIPTION_FAST if fast else AIFunction.AUDIO_TRANSCRIPTION)
        path = self._resolve_upload_path(audio_path)

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
            raise OpenAIServiceError("OpenAI transcription timed out", error_type="timeout", status_code=504) from exc
        except httpx.HTTPError as exc:
            raise OpenAIServiceError(f"OpenAI request failed: {exc}", error_type="http_error", status_code=502) from exc

        data = response.json()
        return {
            "model": model,
            "text": data.get("text", ""),
            "raw": data,
        }

    def text_to_speech(self, text: str, voice: str = "alloy", output_path: str = "speech.mp3") -> dict[str, Any]:
        if not self.api_key:
            raise OpenAIServiceError("OPENAI_API_KEY is not configured", error_type="missing_api_key", status_code=503)

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
            raise OpenAIServiceError("OpenAI speech request timed out", error_type="timeout", status_code=504) from exc
        except httpx.HTTPError as exc:
            raise OpenAIServiceError(f"OpenAI request failed: {exc}", error_type="http_error", status_code=502) from exc

        safe_output = self._resolve_speech_output_path(output_path)
        safe_output.write_bytes(response.content)
        return {
            "model": model,
            "file_path": str(safe_output.relative_to(self._uploads_root().parent)).replace("\\", "/"),
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
        started = time.perf_counter()
        try:
            result = self.chat("Responda apenas: OK")
            return {
                "status": "ok",
                "model": result["model"],
                "message": result.get("text", ""),
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            }
        except Exception as exc:
            mapped = self._classify_openai_error(exc)
            return {
                "status": "error",
                "message": str(mapped),
                "error_type": mapped.error_type,
                "status_code": mapped.status_code,
                "latency_ms": round((time.perf_counter() - started) * 1000, 2),
            }

    def send_chat_message(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        if not messages:
            raise OpenAIServiceError("messages cannot be empty", error_type="invalid_request", status_code=400)
        if self.client is None:
            raise OpenAIServiceError("OPENAI_API_KEY is not configured", error_type="missing_api_key", status_code=503)

        selected_model = model or self.default_model
        started = time.perf_counter()
        input_length = sum(len(str(item.get("content") or "")) for item in messages)
        logger.info(
            "openai.chat.request function=chat_completion model=%s input_chars=%s",
            selected_model,
            input_length,
        )

        try:
            response = self.client.chat.completions.create(
                model=selected_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:
            mapped = self._classify_openai_error(exc)
            logger.error(
                "openai.chat.error function=chat_completion model=%s error_type=%s status_code=%s message=%s",
                selected_model,
                mapped.error_type,
                mapped.status_code,
                str(mapped),
            )
            raise mapped from exc

        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        content = ""
        if response.choices:
            content = str(response.choices[0].message.content or "").strip()
        if not content:
            logger.error(
                "openai.chat.empty_response function=chat_completion model=%s latency_ms=%s",
                selected_model,
                latency_ms,
            )
            raise OpenAIServiceError("OpenAI returned empty content", error_type="empty_response", status_code=502)

        logger.info(
            "openai.chat.success function=chat_completion model=%s latency_ms=%s",
            selected_model,
            latency_ms,
        )
        return {
            "content": content,
            "model": response.model or selected_model,
            "usage": response.usage.model_dump() if response.usage else None,
            "raw": response.model_dump(),
            "latency_ms": latency_ms,
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
