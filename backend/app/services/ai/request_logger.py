from __future__ import annotations

import logging
from typing import Any

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.ai_request_log import AIRequestLog

logger = logging.getLogger(__name__)


def log_ai_request(
    *,
    task_name: str,
    provider: str,
    model: str,
    status: str,
    latency_ms: float | int | None,
    usage: dict[str, Any] | None = None,
    status_code: int | None = None,
    endpoint: str | None = None,
    user_id: int | None = None,
    agent_id: int | None = None,
    error_summary: str | None = None,
) -> None:
    usage = usage or {}
    input_tokens = int(usage.get("prompt_tokens", 0) or usage.get("input_tokens", 0) or 0)
    output_tokens = int(usage.get("completion_tokens", 0) or usage.get("output_tokens", 0) or 0)
    total_tokens = int(usage.get("total_tokens", 0) or 0)

    logger.info(
        "ai.request task=%s provider=%s model=%s status=%s latency_ms=%s user_id=%s agent_id=%s",
        task_name,
        provider,
        model,
        status,
        latency_ms,
        user_id,
        agent_id,
    )

    # Em ambientes nao-producao, mantemos observabilidade via log textual e
    # evitamos escrita concorrente em banco (especialmente SQLite em testes).
    if settings.app_env.lower() != "production":
        return

    if settings.sqlalchemy_database_url.startswith("sqlite"):
        return

    db = SessionLocal()
    try:
        row = AIRequestLog(
            user_id=user_id,
            agent_id=agent_id,
            endpoint=endpoint,
            task_name=task_name,
            provider=provider,
            model=model,
            status=status,
            status_code=status_code,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            latency_ms=int(latency_ms or 0),
            error_summary=(error_summary or "")[:255] or None,
        )
        db.add(row)
        db.commit()
    except Exception as exc:
        logger.warning("ai.request.log.persist_failed reason=%s", exc)
        db.rollback()
    finally:
        db.close()
