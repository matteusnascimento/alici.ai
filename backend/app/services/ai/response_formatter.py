from __future__ import annotations

from typing import Any


def format_ai_response(
    *,
    success: bool,
    provider: str,
    model: str,
    task: str,
    content: str | None,
    usage: dict[str, Any] | None = None,
    structured_data: dict[str, Any] | None = None,
    latency_ms: float | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    usage = usage or {}
    return {
        "success": success,
        "provider": provider,
        "model": model,
        "task": task,
        "content": content,
        "structured_data": structured_data,
        "usage": {
            "input_tokens": usage.get("prompt_tokens", 0) or usage.get("input_tokens", 0) or 0,
            "output_tokens": usage.get("completion_tokens", 0) or usage.get("output_tokens", 0) or 0,
            "total_tokens": usage.get("total_tokens", 0) or 0,
        },
        "meta": {
            "latency_ms": latency_ms or 0,
            "error": error,
        },
    }
