"""AI provider selection, fallback, and response normalization."""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from alici_api.config import get_settings
from alici_api.services.credit_service import CreditService
from logger import get_logger

from .base import AIResponse, BaseAIProvider

logger_ai = get_logger("ai_manager")


@dataclass(frozen=True)
class AICostEstimate:
    operation: str
    provider: str
    model: str
    cost_credits: int
    fallback_order: list[str]


class AIManager:
    supported_providers = ("groq", "gemini", "ollama", "openai")
    provider_priority = {
        "ollama": 0,
        "groq": 10,
        "gemini": 20,
        "openai": 100,
    }

    def __init__(self, default_provider: str | None = None, credit_service: CreditService | None = None):
        self.settings = get_settings()
        self.credit_service = credit_service or CreditService()
        self.default_provider = (default_provider or self.settings.default_ai_provider).strip().lower()
        self.providers = self._build_providers()

    def _build_providers(self) -> dict[str, BaseAIProvider]:
        providers: dict[str, BaseAIProvider] = {}
        # Groq
        if self.settings.groq_api_key:
            try:
                from .providers.groq_provider import GroqProvider

                providers["groq"] = GroqProvider()
            except Exception as exc:
                logger_ai.warning(f"Groq nao inicializado durante import/inicializacao: {exc}")
        else:
            logger_ai.info("Groq nao configurado (GROQ_API_KEY ausente)")
        if self.settings.gemini_api_key:
            try:
                from .providers.gemini_provider import GeminiProvider
                providers["gemini"] = GeminiProvider()
            except Exception as exc:
                logger_ai.warning(f"Gemini nao inicializado durante import/inicializacao: {exc}")
        else:
            logger_ai.info("Gemini nao configurado (GEMINI_API_KEY ausente)")
        if self.settings.ollama_enabled and self.settings.ollama_base_url:
            try:
                from .providers.ollama_provider import OllamaProvider
                providers["ollama"] = OllamaProvider()
            except Exception as exc:
                logger_ai.warning(f"Ollama nao inicializado durante import/inicializacao: {exc}")
        else:
            if not self.settings.ollama_enabled:
                logger_ai.info("Ollama desabilitado por configuracao (OLLAMA_ENABLED=false)")
            else:
                logger_ai.info("Ollama nao configurado (OLLAMA_BASE_URL ausente)")
        if self.settings.openai_api_key:
            try:
                from .providers.openai_provider import OpenAIProvider
                providers["openai"] = OpenAIProvider()
            except Exception as exc:
                logger_ai.warning(f"OpenAI nao inicializado durante import/inicializacao: {exc}")
        else:
            logger_ai.info("OpenAI nao configurado (OPENAI_API_KEY ausente)")

        return providers

    def available_providers(self) -> list[str]:
        return list(self.providers.keys())

    def provider_model(self, provider_name: str, operation_name: str = "chat") -> str:
        if provider_name == "groq":
            return self.settings.groq_model_code if operation_name == "generate_code" else self.settings.groq_model_chat
        if provider_name == "gemini":
            return self.settings.gemini_model
        if provider_name == "ollama":
            return self.settings.ollama_model
        if provider_name == "openai":
            return self.settings.openai_model_chat_general
        return "unknown"

    def _configured_order(self) -> list[str]:
        order = [self.default_provider, "groq", "gemini", "ollama", "openai"]
        return [provider for index, provider in enumerate(order) if provider in self.supported_providers and provider not in order[:index]]

    def provider_cost(self, provider_name: str, operation_name: str = "chat") -> int:
        job_type = "code" if operation_name == "generate_code" else "chat"
        model = self.provider_model(provider_name, operation_name)
        if provider_name == "ollama":
            return 0
        return self.credit_service.calculate_cost(job_type=job_type, provider=provider_name, model=model)

    def _fallback_order(self, operation_name: str = "chat") -> list[str]:
        candidates = [provider for provider in self._configured_order() if provider in self.providers]
        return sorted(
            candidates,
            key=lambda provider: (
                self.provider_cost(provider, operation_name),
                self.provider_priority.get(provider, 50),
            ),
        )

    def estimate_cost(self, operation_name: str = "chat") -> AICostEstimate:
        order = self._fallback_order(operation_name)
        if not order:
            raise RuntimeError(f"Nenhum provider de IA configurado para {operation_name}")

        provider = order[0]
        model = self.provider_model(provider, operation_name)
        cost = max(self.provider_cost(candidate, operation_name) for candidate in order)
        return AICostEstimate(
            operation=operation_name,
            provider=provider,
            model=model,
            cost_credits=cost,
            fallback_order=order,
        )

    async def _run_with_fallback(
        self,
        operation_name: str,
        operation: Callable[[BaseAIProvider], Awaitable[AIResponse]],
    ) -> AIResponse:
        errors: list[str] = []

        for provider_name in self._fallback_order(operation_name):
            provider = self.providers.get(provider_name)
            if not provider:
                errors.append(f"{provider_name}: nao configurado")
                continue

            started = time.perf_counter()
            try:
                response = await operation(provider)
                response.provider = provider_name
                response.response_time_ms = int((time.perf_counter() - started) * 1000)
                if not response.estimated_tokens:
                    response.estimated_tokens = self.estimate_tokens(response.content)
                logger_ai.info(
                    "ai_provider_success",
                    extra={
                        "operation": operation_name,
                        "provider": provider_name,
                        "model": response.model,
                        "latency_ms": response.response_time_ms,
                        "estimated_tokens": response.estimated_tokens,
                    },
                )
                return response
            except Exception as exc:
                logger_ai.warning(f"Provider {provider_name} falhou em {operation_name}: {exc}")
                errors.append(f"{provider_name}: {exc}")

        raise RuntimeError(f"Nenhum provider de IA disponivel para {operation_name}. Erros: {'; '.join(errors)}")

    async def chat(self, prompt: str, system_prompt: str = "") -> AIResponse:
        return await self._run_with_fallback(
            "chat",
            lambda provider: provider.chat(prompt=prompt, system_prompt=system_prompt),
        )

    async def summarize(self, text: str) -> AIResponse:
        return await self._run_with_fallback("summarize", lambda provider: provider.summarize(text=text))

    async def generate_code(self, prompt: str) -> AIResponse:
        return await self._run_with_fallback("generate_code", lambda provider: provider.generate_code(prompt=prompt))

    @staticmethod
    def estimate_tokens(text: str) -> int:
        return max(1, len((text or "").split()) + len(text or "") // 12)
