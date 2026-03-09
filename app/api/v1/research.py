"""
Research API v1 - Asynchronous deep research endpoint

POST /v1/research  - Dispatch a deep research task and return a task_id
GET  /v1/research/{task_id} - Poll the status / result of a running task
"""
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class ResearchRequest(BaseModel):
    """Payload for starting a deep research job."""

    query: str = Field(..., min_length=1, description="The research question or topic")
    user_id: str = Field(..., min_length=1, description="Identifier of the requesting user")


class ResearchAccepted(BaseModel):
    """Immediate response returned when a task is successfully queued."""

    task_id: str
    status: str = "accepted"


class TaskStatusResponse(BaseModel):
    """Response for task status polling."""

    task_id: str
    status: str
    result: dict | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/research", response_model=ResearchAccepted, status_code=202)
async def start_research(payload: ResearchRequest):
    """Dispatch a deep research task asynchronously.

    The endpoint returns immediately with a ``task_id`` that the client can
    use to poll ``GET /v1/research/{task_id}`` for the result.
    """
    try:
        from app.tasks.worker import run_deep_research

        task = run_deep_research.delay(payload.user_id, payload.query)
        logger.info("Research task queued – task_id=%s user_id=%s", task.id, payload.user_id)
        return ResearchAccepted(task_id=task.id)
    except Exception as exc:
        logger.exception("Failed to dispatch research task.")
        raise HTTPException(status_code=503, detail=f"Task queue unavailable: {exc}") from exc


@router.get("/research/{task_id}", response_model=TaskStatusResponse)
async def get_research_status(task_id: str):
    """Poll the status and result of a queued research task.

    Returns one of the following ``status`` values:

    - ``pending``   – task is queued but not yet started
    - ``processing`` – task is currently running
    - ``success``   – task completed successfully (``result`` is populated)
    - ``failure``   – task failed (``result`` contains the error)
    """
    try:
        from celery.result import AsyncResult

        from app.tasks.worker import celery_app

        async_result = AsyncResult(task_id, app=celery_app)
        state = async_result.state.lower()

        status_map = {
            "pending": "pending",
            "started": "processing",
            "retry": "processing",
            "success": "success",
            "failure": "failure",
        }
        status = status_map.get(state, state)

        result = None
        if state == "success":
            result = async_result.result
        elif state == "failure":
            result = {"error": str(async_result.result)}

        return TaskStatusResponse(task_id=task_id, status=status, result=result)
    except Exception as exc:
        logger.exception("Failed to retrieve task status – task_id=%s", task_id)
        raise HTTPException(status_code=503, detail=f"Task backend unavailable: {exc}") from exc
