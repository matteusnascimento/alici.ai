from app.services.ai.model_router import get_model_for_task, normalize_task

__all__ = [
    "ProviderService",
    "get_default_ai_provider",
    "get_default_chat_model",
    "get_model_for_task_name",
    "get_model_for_task",
    "normalize_task",
]


def __getattr__(name: str):
    if name in {"ProviderService", "get_default_ai_provider", "get_default_chat_model", "get_model_for_task_name"}:
        from app.services.ai.provider_service import (
            ProviderService,
            get_default_ai_provider,
            get_default_chat_model,
            get_model_for_task_name,
        )

        exports = {
            "ProviderService": ProviderService,
            "get_default_ai_provider": get_default_ai_provider,
            "get_default_chat_model": get_default_chat_model,
            "get_model_for_task_name": get_model_for_task_name,
        }
        return exports[name]
    raise AttributeError(name)
