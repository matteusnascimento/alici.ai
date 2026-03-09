"""
Celery Worker - Background task processing for ALICI Platform

Tasks:
- run_deep_research: Executes a deep research session asynchronously
"""
import logging

from celery import Celery

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Celery application
# ---------------------------------------------------------------------------

_broker_url = settings.redis_url or "redis://redis:6379/0"
_backend_url = settings.redis_url or "redis://redis:6379/0"

celery_app = Celery(
    "alici_tasks",
    broker=_broker_url,
    backend=_backend_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Retry failed tasks up to 3 times with exponential back-off
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

@celery_app.task(name="run_deep_research", bind=True, max_retries=3)
def run_deep_research(self, session_id: str, query: str):
    """Execute a deep research session in the background.

    Args:
        session_id: Unique identifier for this research session (maps to a
                    user/conversation in the database).
        query:      The user's research question or topic.

    Returns:
        A dict with ``content``, ``session_id``, ``steps_executed``, and
        ``steps_successful`` keys.
    """
    from app.agents.orchestrator import DeepResearchAgent

    logger.info("Task run_deep_research started – session=%s", session_id)
    try:
        agent = DeepResearchAgent(session_id=session_id)
        result = agent.execute(query)
        logger.info("Task run_deep_research completed – session=%s", session_id)
        return result
    except Exception as exc:
        logger.exception("Task run_deep_research failed – session=%s", session_id)
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
