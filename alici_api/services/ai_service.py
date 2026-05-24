"""Central AI service used by routes and future application services."""

from __future__ import annotations

from alici_api.services.ai import AIManager
from alici_api.services.ai.manager import AICostEstimate
from alici_api.services.ai.base import AIResponse
from alici_api.services.ai_cache import AICache
from alici_api.services.prompt_security import validate_prompt
from database import salvar_ai_log


DEFAULT_SYSTEM_PROMPT = (
    "Voce e a AXI, uma IA proprietaria da Alici. "
    "Responda em portugues do Brasil com clareza, objetividade e tom profissional. "
    "Nunca diga que e ChatGPT e nao mencione OpenAI como identidade."
)


def estimate_chat_cost(prompt: str, system_prompt: str = DEFAULT_SYSTEM_PROMPT) -> AICostEstimate:
    validate_prompt(prompt, purpose="chat")
    return AIManager().estimate_cost("chat")


def actual_chat_cost(response: AIResponse) -> int:
    return AIManager().provider_cost(response.provider, "chat")


async def get_cached_chat_response(prompt: str, system_prompt: str = DEFAULT_SYSTEM_PROMPT) -> AIResponse | None:
    safe_prompt = validate_prompt(prompt, purpose="chat")
    return await AICache().get_response(operation="chat", prompt=safe_prompt, system_prompt=system_prompt)


def _save_ai_log(prompt: str, response: AIResponse) -> None:
    salvar_ai_log(
        pergunta=prompt,
        resposta=response.content,
        provider=response.provider,
        modelo=response.model,
        tempo_resposta_ms=response.response_time_ms,
        tokens_estimados=response.estimated_tokens,
    )


async def generate_chat_response(prompt: str, system_prompt: str = DEFAULT_SYSTEM_PROMPT) -> AIResponse:
    safe_prompt = validate_prompt(prompt, purpose="chat")
    cache = AICache()
    cached = await cache.get_response(operation="chat", prompt=safe_prompt, system_prompt=system_prompt)
    if cached:
        _save_ai_log(safe_prompt, cached)
        return cached

    response = await AIManager().chat(safe_prompt, system_prompt)
    await cache.set_response(operation="chat", prompt=safe_prompt, system_prompt=system_prompt, response=response)
    _save_ai_log(safe_prompt, response)
    return response


async def generate_summary(text: str) -> AIResponse:
    safe_text = validate_prompt(text, purpose="summary")
    cache = AICache()
    cached = await cache.get_response(operation="summary", prompt=safe_text)
    if cached:
        _save_ai_log(safe_text, cached)
        return cached

    response = await AIManager().summarize(safe_text)
    await cache.set_response(operation="summary", prompt=safe_text, response=response)
    _save_ai_log(safe_text, response)
    return response


async def generate_code(prompt: str) -> AIResponse:
    safe_prompt = validate_prompt(prompt, purpose="code")
    cache = AICache()
    cached = await cache.get_response(operation="code", prompt=safe_prompt)
    if cached:
        _save_ai_log(safe_prompt, cached)
        return cached

    response = await AIManager().generate_code(safe_prompt)
    await cache.set_response(operation="code", prompt=safe_prompt, response=response)
    _save_ai_log(safe_prompt, response)
    return response
