from __future__ import annotations

import json
from typing import Any

from app.core.config import settings
from app.services.model_router import AIFunction, get_model_for
from app.services.openai_service import OpenAIService, OpenAIServiceError


class AIServiceError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        user_message: str = "Nao foi possivel executar a tarefa com IA no momento.",
        status_code: int = 503,
        code: str = "ai_service_error",
    ) -> None:
        super().__init__(message)
        self.user_message = user_message
        self.status_code = status_code
        self.code = code


class AIConfigurationError(AIServiceError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            user_message="A integracao de IA nao esta configurada.",
            status_code=503,
            code="ai_not_configured",
        )


class AIService:
    def __init__(self, provider: str | None = None) -> None:
        self.provider = (provider or settings.default_ai_provider or "openai").strip().lower()
        self.default_model = settings.openai_model
        self._openai = OpenAIService() if self.provider == "openai" else None

    def is_configured(self) -> bool:
        return self.provider == "openai" and bool(settings.openai_api_key)

    def _ensure_provider(self) -> None:
        if self.provider != "openai":
            raise AIConfigurationError(f"Unsupported AI provider: {self.provider}")
        if not settings.openai_api_key:
            raise AIConfigurationError("OPENAI_API_KEY is not configured")
        if self._openai is None:
            self._openai = OpenAIService()

    def _model_for(self, function_name: AIFunction, model: str | None = None) -> str:
        if model:
            return model
        try:
            return get_model_for(function_name)
        except Exception:
            return self.default_model

    def _wrap_error(self, exc: Exception) -> AIServiceError:
        if isinstance(exc, AIServiceError):
            return exc
        if isinstance(exc, OpenAIServiceError):
            message = str(exc)
            if "OPENAI_API_KEY" in message:
                return AIConfigurationError(message)
            return AIServiceError(
                message,
                user_message="Nao foi possivel executar a tarefa com IA no momento.",
                status_code=503,
                code="openai_request_failed",
            )
        return AIServiceError(str(exc))

    def chat_completion(
        self,
        *,
        messages: list[dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int | None = None,
        model: str | None = None,
        function_name: AIFunction = AIFunction.CHAT,
    ) -> dict[str, Any]:
        self._ensure_provider()
        assert self._openai is not None
        try:
            return self._openai.send_chat_message(
                messages=messages,
                model=self._model_for(function_name, model),
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:
            raise self._wrap_error(exc) from exc

    def generate_text(
        self,
        *,
        user_prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int | None = None,
        model: str | None = None,
        function_name: AIFunction = AIFunction.CHAT,
    ) -> str:
        messages: list[dict[str, Any]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        response = self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
            function_name=function_name,
        )
        content = str(response.get("content") or "").strip()
        if not content:
            raise AIServiceError("OpenAI returned empty content")
        return content

    def generate_structured_output(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        system_prompt: str | None = None,
        model: str | None = None,
        function_name: AIFunction = AIFunction.STRUCTURED_EXTRACTION,
    ) -> dict[str, Any]:
        self._ensure_provider()
        assert self._openai is not None
        full_prompt = prompt if not system_prompt else f"{system_prompt}\n\n{prompt}"
        try:
            result = self._openai.structured_extract(full_prompt, schema)
            text = str(result.get("text") or "{}").strip()
            return json.loads(text) if text else {}
        except Exception as exc:
            raise self._wrap_error(exc) from exc

    def healthcheck(self) -> dict[str, Any]:
        self._ensure_provider()
        assert self._openai is not None
        try:
            result = self._openai.healthcheck()
        except Exception as exc:
            raise self._wrap_error(exc) from exc
        return {
            "provider": self.provider,
            "status": result.get("status", "error"),
            "model": result.get("model", self.default_model),
            "message": result.get("message", "Falha ao validar integracao de IA."),
        }
