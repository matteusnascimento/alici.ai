from __future__ import annotations

from app.core.config import settings

# Mapa central de tarefa -> modelo OpenAI.
TASK_MODEL_MAP: dict[str, str] = {
    "chat": settings.openai_model or "gpt-4o-mini",
    "agent_builder": settings.openai_model or "gpt-4o-mini",
    "prompt_playground": settings.openai_model or "gpt-4o-mini",
    "caption_generator": settings.openai_model or "gpt-4o-mini",
    "cta_generator": settings.openai_model or "gpt-4o-mini",
    "ad_copy_generator": settings.openai_model or "gpt-4o-mini",
    "social_post_generator": settings.openai_model or "gpt-4o-mini",
    "product_description_generator": settings.openai_model or "gpt-4o-mini",
    "image_analysis": settings.openai_model_vision or settings.openai_model or "gpt-4o-mini",
    "document_analysis": settings.openai_model or "gpt-4o-mini",
    "analytics_insights": settings.openai_model or "gpt-4o-mini",
    "platform_assistant": settings.openai_model or "gpt-4o-mini",
    "workflow_builder": settings.openai_model or "gpt-4o-mini",
}

# Alias de compatibilidade com nomenclaturas antigas já usadas na base.
TASK_ALIASES: dict[str, str] = {
    "chat_general": "chat",
    "chat_support": "platform_assistant",
    "prompt_generation": "ad_copy_generator",
    "copy": "ad_copy_generator",
    "classification": "document_analysis",
    "vision_analysis": "image_analysis",
    "knowledge_qa": "document_analysis",
    "agent_runtime": "chat",
    "summarization": "document_analysis",
}


def normalize_task(task_name: str | None) -> str:
    raw = (task_name or "chat").strip().lower()
    return TASK_ALIASES.get(raw, raw)


def get_model_for_task(task_name: str | None) -> str:
    normalized = normalize_task(task_name)
    return TASK_MODEL_MAP.get(normalized) or settings.openai_model or "gpt-4o-mini"
