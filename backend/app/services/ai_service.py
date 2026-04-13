from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.services.ai.moderation_service import ModerationService
from app.services.ai.prompt_builder import build_prompt_for_task
from app.services.ai.provider_service import ProviderService, get_default_chat_model
from app.services.ai.request_logger import log_ai_request
from app.services.ai.response_formatter import format_ai_response


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
        self.default_model = get_default_chat_model()
        self._provider_service = ProviderService(self.provider)
        self._moderation = ModerationService()

    def is_configured(self) -> bool:
        return self._provider_service.is_configured()

    def _ensure_provider(self) -> None:
        if self.provider != "openai":
            raise AIConfigurationError(f"Unsupported AI provider: {self.provider}")
        if not settings.effective_openai_api_key:
            raise AIConfigurationError("OPENAI_API_KEY is not configured")
        if not self._provider_service.is_configured():
            raise AIConfigurationError("AI provider is not configured")

    def _model_for(self, task_name: str, model: str | None = None) -> str:
        if model:
            return model
        return settings.openai_model if task_name == "chat" else self.default_model

    @staticmethod
    def _task_from_function_name(function_name: Any | None) -> str:
        raw = str(function_name.value if hasattr(function_name, "value") else function_name or "chat")
        normalized = raw.strip().lower()
        mapping = {
            "chat_general": "chat",
            "chat": "chat",
            "agent_runtime": "chat",
            "chat_support": "platform_assistant",
            "prompt_generation": "ad_copy_generator",
            "classification": "document_analysis",
            "vision_analysis": "image_analysis",
            "summarization": "document_analysis",
            "knowledge_qa": "document_analysis",
        }
        return mapping.get(normalized, normalized or "chat")

    def _wrap_error(self, exc: Exception) -> AIServiceError:
        if isinstance(exc, AIServiceError):
            return exc
        message = str(exc)
        if "OPENAI_API_KEY" in message:
            return AIConfigurationError(message)
        status_code = getattr(exc, "status_code", 503)
        code = getattr(exc, "code", "openai_request_failed")
        if hasattr(exc, "code") and getattr(exc, "code") == "missing_api_key":
            return AIConfigurationError(message)
        return AIServiceError(
            message,
            user_message="Nao foi possivel executar a tarefa com IA no momento.",
            status_code=status_code,
            code=code,
        )

    def _moderate_or_raise(self, text: str, *, task_name: str) -> None:
        if task_name not in {"chat", "agent_builder", "document_analysis", "platform_assistant"}:
            return
        moderation = self._moderation.check_text(text)
        if moderation.allowed:
            return
        raise AIServiceError(
            moderation.reason or "Conteudo bloqueado por moderacao.",
            user_message="Conteudo bloqueado pela politica de seguranca da plataforma.",
            status_code=403,
            code="moderation_blocked",
        )

    def run_task(
        self,
        *,
        task_name: str,
        context: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
        max_tokens: int | None = None,
        model: str | None = None,
        structured_schema: dict[str, Any] | None = None,
        user_id: int | None = None,
        agent_id: int | None = None,
        endpoint: str | None = None,
    ) -> dict[str, Any]:
        self._ensure_provider()
        self._moderate_or_raise(context, task_name=task_name)

        selected_model = self._model_for(task_name, model)
        system_text, user_text = build_prompt_for_task(
            task_name,
            context=context,
            extra={"system_prompt": system_prompt},
        )

        try:
            if structured_schema is not None:
                raw = self._provider_service.run_structured(
                    task_name=task_name,
                    system_prompt=system_text,
                    user_prompt=user_text,
                    schema=structured_schema,
                    model=selected_model,
                )
            else:
                raw = self._provider_service.run_text(
                    task_name=task_name,
                    messages=[
                        {"role": "system", "content": system_text},
                        {"role": "user", "content": user_text},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    model=selected_model,
                )
        except Exception as exc:
            wrapped = self._wrap_error(exc)
            log_ai_request(
                task_name=task_name,
                provider=self.provider,
                model=selected_model,
                status="error",
                latency_ms=0,
                status_code=wrapped.status_code,
                endpoint=endpoint,
                user_id=user_id,
                agent_id=agent_id,
                error_summary=str(wrapped),
            )
            raise wrapped from exc

        response = format_ai_response(
            success=True,
            provider=self.provider,
            model=raw.get("model", selected_model),
            task=task_name,
            content=raw.get("content") or "",
            structured_data=raw.get("structured_data"),
            usage=raw.get("usage") or {},
            latency_ms=raw.get("latency_ms"),
        )

        log_ai_request(
            task_name=task_name,
            provider=self.provider,
            model=response["model"],
            status="success",
            latency_ms=response["meta"]["latency_ms"],
            usage=response["usage"],
            status_code=200,
            endpoint=endpoint,
            user_id=user_id,
            agent_id=agent_id,
        )
        return response

    def chat_completion(
        self,
        *,
        messages: list[dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int | None = None,
        model: str | None = None,
        function_name: Any = "chat_general",
    ) -> dict[str, Any]:
        self._ensure_provider()
        task_name = self._task_from_function_name(function_name)
        context = "\n".join(str(item.get("content") or "") for item in messages if item.get("role") != "system")
        system_prompt = next((str(item.get("content") or "") for item in messages if item.get("role") == "system"), None)
        try:
            raw = self._provider_service.run_text(
                task_name=task_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                model=self._model_for(task_name, model),
            )
            if not (raw.get("content") or "").strip():
                raw["content"] = "No momento não foi possível gerar resposta completa. Tente novamente."
            return raw
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
        function_name: Any = "chat_general",
    ) -> str:
        task_name = self._task_from_function_name(function_name)
        response = self.run_task(
            task_name=task_name,
            context=user_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
        )
        content = str(response.get("content") or "").strip()
        if not content:
            return "No momento não foi possível gerar conteúdo. Tente novamente em instantes."
        return content

    def generate_structured_output(
        self,
        *,
        prompt: str,
        schema: dict[str, Any],
        system_prompt: str | None = None,
        model: str | None = None,
        function_name: Any = "classification",
    ) -> dict[str, Any]:
        task_name = self._task_from_function_name(function_name)
        response = self.run_task(
            task_name=task_name,
            context=prompt,
            system_prompt=system_prompt,
            model=model,
            structured_schema=schema,
        )
        return response.get("structured_data") or {}

    def analyze_image(
        self,
        *,
        image_bytes: bytes,
        prompt: str,
        model: str | None = None,
        user_id: int | None = None,
        endpoint: str | None = None,
    ) -> dict[str, Any]:
        self._ensure_provider()
        selected_model = self._model_for("image_analysis", model)
        try:
            raw = self._provider_service.run_image_analysis(
                task_name="image_analysis",
                image_bytes=image_bytes,
                prompt=prompt,
                model=selected_model,
            )
            response = format_ai_response(
                success=True,
                provider=self.provider,
                model=raw.get("model", selected_model),
                task="image_analysis",
                content=raw.get("content"),
                structured_data={
                    "description": raw.get("content", ""),
                    "tags": [],
                    "suggestions": [],
                    "extracted_context": raw.get("content", ""),
                },
                usage=raw.get("usage") or {},
                latency_ms=raw.get("latency_ms"),
            )
            log_ai_request(
                task_name="image_analysis",
                provider=self.provider,
                model=response["model"],
                status="success",
                latency_ms=response["meta"]["latency_ms"],
                usage=response["usage"],
                status_code=200,
                endpoint=endpoint,
                user_id=user_id,
            )
            return response
        except Exception as exc:
            wrapped = self._wrap_error(exc)
            log_ai_request(
                task_name="image_analysis",
                provider=self.provider,
                model=selected_model,
                status="error",
                latency_ms=0,
                status_code=wrapped.status_code,
                endpoint=endpoint,
                user_id=user_id,
                error_summary=str(wrapped),
            )
            raise wrapped from exc

    # ------------------------------------------------------------------
    # Agent response - ponto unico de chamada para agentes
    # ------------------------------------------------------------------

    def generate_agent_response(
        self,
        *,
        agent_nome: str,
        agent_funcao: str,
        agent_prompt: str,
        user_message: str,
        conversation_history: list[dict[str, Any]] | None = None,
        preferred_model: str | None = None,
        temperature: float = 0.4,
    ) -> str:
        """Gera resposta do agente usando OpenAI no backend.

        - preferred_model: modelo especifico do agente (fallback: OPENAI_MODEL do env)
        - Nunca expoe OPENAI_API_KEY para o frontend
        """
        system_prompt = (
            f"Voce e {agent_nome}, um assistente de IA com a funcao: {agent_funcao}.\n\n"
            f"Instrucoes do agente:\n{agent_prompt}\n\n"
            "Responda de forma direta, profissional e alinhada com sua funcao. "
            "Nao invente informacoes. Se nao souber, diga que precisa verificar."
        )
        messages: list[dict[str, Any]] = []
        if conversation_history:
            messages.extend(conversation_history[-10:])
        messages.append({"role": "user", "content": user_message})

        model = preferred_model or self._model_for("chat")
        return self.generate_text(
            user_prompt=user_message,
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            function_name="agent_runtime",
        )

    def healthcheck(self) -> dict[str, Any]:
        try:
            content = self.generate_text(
                user_prompt="Responda apenas com OK",
                system_prompt="Healthcheck interno",
                function_name="platform_assistant",
            )
        except Exception as exc:
            raise self._wrap_error(exc) from exc
        return {
            "provider": self.provider,
            "status": "ok",
            "model": self.default_model,
            "message": content,
            "latency_ms": None,
            "error_type": None,
            "status_code": 200,
        }
