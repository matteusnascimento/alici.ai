"""AI provider selection, fallback, and response normalization."""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

import httpx

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
    supported_providers = ("grok", "groq", "gemini", "ollama", "openai")
    provider_priority = {
        "grok": 0,
        "groq": 10,
        "gemini": 20,
        "ollama": 80,
        "openai": 100,
    }
    _provider_failure_counts: dict[str, int] = {}
    _provider_disabled_until: dict[str, float] = {}
    _provider_latency_ms: dict[str, int] = {}
    _ollama_probe_cache: tuple[float, bool] = (0.0, False)

    def __init__(self, default_provider: str | None = None, credit_service: CreditService | None = None):
        self.settings = get_settings()
        self.credit_service = credit_service or CreditService()
        self.default_provider = (default_provider or self.settings.default_ai_provider).strip().lower()
        self.providers = self._build_providers()

    def _build_providers(self) -> dict[str, BaseAIProvider]:
        providers: dict[str, BaseAIProvider] = {}

        if self.settings.resolved_grok_api_key:
            try:
                from .providers.grok_provider import GrokProvider

                providers["grok"] = GrokProvider()
            except Exception as exc:
                logger_ai.warning(f"Grok/xAI nao inicializado: {exc}")
        if self.settings.groq_api_key:
            try:
                from .providers.groq_provider import GroqProvider

                providers["groq"] = GroqProvider()
            except Exception as exc:
                logger_ai.warning(f"Groq nao inicializado: {exc}")
        if self.settings.gemini_api_key:
            try:
                from .providers.gemini_provider import GeminiProvider

                providers["gemini"] = GeminiProvider()
            except Exception as exc:
                logger_ai.warning(f"Gemini nao inicializado: {exc}")
        if self.settings.ollama_enabled and self.settings.ollama_base_url and self._ollama_reachable():
            try:
                from .providers.ollama_provider import OllamaProvider

                providers["ollama"] = OllamaProvider()
            except Exception as exc:
                logger_ai.warning(f"Ollama nao inicializado: {exc}")
        elif self.settings.ollama_enabled:
            logger_ai.info("Ollama habilitado, mas offline; removido do fallback desta execucao")
        if self.settings.openai_api_key:
            try:
                from .providers.openai_provider import OpenAIProvider

                providers["openai"] = OpenAIProvider()
            except Exception as exc:
                logger_ai.warning(f"OpenAI nao inicializado: {exc}")

        return providers

    def available_providers(self) -> list[str]:
        return list(self.providers.keys())

    def _is_configured(self, provider_name: str) -> bool:
        if provider_name == "grok":
            return bool(self.settings.resolved_grok_api_key)
        if provider_name == "groq":
            return bool(self.settings.groq_api_key)
        if provider_name == "gemini":
            return bool(self.settings.gemini_api_key)
        if provider_name == "ollama":
            return bool(self.settings.ollama_enabled and self.settings.ollama_base_url)
        if provider_name == "openai":
            return bool(self.settings.openai_api_key)
        return False

    def _ollama_reachable(self, *, force: bool = False) -> bool:
        if not self.settings.ollama_enabled or not self.settings.ollama_base_url:
            return False

        now = time.monotonic()
        cached_at, cached_value = self.__class__._ollama_probe_cache
        if not force and now - cached_at < 30:
            return cached_value

        try:
            with httpx.Client(
                timeout=httpx.Timeout(
                    float(self.settings.ollama_probe_timeout_seconds),
                    connect=min(0.5, float(self.settings.ollama_probe_timeout_seconds)),
                )
            ) as client:
                response = client.get(f"{self.settings.ollama_base_url.rstrip('/')}/api/tags")
                reachable = response.status_code < 500
        except Exception:
            reachable = False

        self.__class__._ollama_probe_cache = (now, reachable)
        return reachable

    def _circuit_open(self, provider_name: str) -> bool:
        return time.monotonic() < self.__class__._provider_disabled_until.get(provider_name, 0.0)

    def _record_provider_success(self, provider_name: str, latency_ms: int) -> None:
        self.__class__._provider_failure_counts[provider_name] = 0
        self.__class__._provider_disabled_until.pop(provider_name, None)
        self.__class__._provider_latency_ms[provider_name] = latency_ms

    def _record_provider_failure(self, provider_name: str) -> None:
        failures = self.__class__._provider_failure_counts.get(provider_name, 0) + 1
        self.__class__._provider_failure_counts[provider_name] = failures
        if failures >= 2:
            backoff_seconds = min(60, 2 ** failures)
            self.__class__._provider_disabled_until[provider_name] = time.monotonic() + backoff_seconds

    def provider_statuses(self, *, include_probe: bool = False) -> dict[str, dict]:
        statuses: dict[str, dict] = {}
        for provider_name in self.supported_providers:
            configured = self._is_configured(provider_name)
            runtime_enabled = provider_name in self.providers
            reachable = runtime_enabled
            reason = None
            if provider_name == "ollama" and configured:
                reachable = self._ollama_reachable(force=include_probe)
                if not reachable:
                    reason = "offline_or_timeout"
            elif not configured:
                reason = "not_configured"
            elif not runtime_enabled:
                reason = "init_failed"

            statuses[provider_name] = {
                "configured": configured,
                "enabled": runtime_enabled,
                "reachable": reachable,
                "model": self.provider_model(provider_name, "chat"),
                "chat_cost_credits": self._safe_provider_cost(provider_name, "chat") if configured else None,
                "circuit_open": self._circuit_open(provider_name),
                "recent_latency_ms": self.__class__._provider_latency_ms.get(provider_name),
                "failure_count": self.__class__._provider_failure_counts.get(provider_name, 0),
                "reason": reason,
            }
        return statuses

    def provider_model(self, provider_name: str, operation_name: str = "chat") -> str:
        if provider_name == "grok":
            return self.settings.grok_model_code if operation_name == "generate_code" else self.settings.grok_model_chat
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
        order = [self.default_provider, "grok", "groq", "gemini", "ollama", "openai"]
        return [provider for index, provider in enumerate(order) if provider in self.supported_providers and provider not in order[:index]]

    def provider_cost(self, provider_name: str, operation_name: str = "chat") -> int:
        job_type = "code" if operation_name == "generate_code" else "chat"
        model = self.provider_model(provider_name, operation_name)
        if provider_name == "ollama":
            return 0
        return self.credit_service.calculate_cost(job_type=job_type, provider=provider_name, model=model)

    def _safe_provider_cost(self, provider_name: str, operation_name: str = "chat") -> int | None:
        try:
            return self.provider_cost(provider_name, operation_name)
        except Exception as exc:
            logger_ai.warning(f"Nao foi possivel calcular custo de {provider_name}: {exc}")
            return None

    def _fallback_order(self, operation_name: str = "chat") -> list[str]:
        candidates = [
            provider
            for provider in self._configured_order()
            if provider in self.providers and not self._circuit_open(provider)
        ]
        if not candidates:
            candidates = [provider for provider in self._configured_order() if provider in self.providers]

        ordered = sorted(
            candidates,
            key=lambda provider: (
                0 if provider == self.default_provider else 1,
                self.provider_priority.get(provider, 50),
                self.provider_cost(provider, operation_name),
                self.__class__._provider_latency_ms.get(provider, 10_000),
            ),
        )
        return ordered

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
                self._record_provider_success(provider_name, response.response_time_ms)
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
                self._record_provider_failure(provider_name)
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
