"""Generation job status routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, success
from alici_api.services.generation_job_service import GenerationJobService

router = APIRouter(prefix="/jobs", tags=["jobs"])
job_service = GenerationJobService()


def _public_job(job: dict) -> dict:
    status = job.get("status")
    terminal = status in {"completed", "failed", "dead_letter"}
    progress = int(job.get("progress") or 0)
    if status == "completed":
        progress = 100
    return {
        "id": job.get("id"),
        "status": status,
        "job_type": job.get("job_type"),
        "provider": job.get("provider"),
        "model": job.get("model"),
        "result_url": job.get("result_url"),
        "result_payload": job.get("result_payload") or {},
        "cost": job.get("cost"),
        "progress": progress,
        "terminal": terminal,
        "queue_name": job.get("queue_name"),
        "priority": job.get("priority"),
        "arq_job_id": job.get("arq_job_id"),
        "error_message": job.get("error_message"),
        "attempts": job.get("attempts"),
        "max_retries": job.get("max_retries"),
        "status_url": f"/jobs/{job.get('id')}",
        "created_at": str(job.get("created_at")) if job.get("created_at") is not None else None,
        "updated_at": str(job.get("updated_at")) if job.get("updated_at") is not None else None,
        "completed_at": str(job.get("completed_at")) if job.get("completed_at") is not None else None,
        "refunded_at": str(job.get("refunded_at")) if job.get("refunded_at") is not None else None,
    }


@router.get("/list", name="list_jobs")
def list_jobs(limit: int = Query(default=50, ge=1, le=100), user=Depends(get_current_user)):
    jobs = job_service.list_jobs_for_user(int(user["id"]), limit=limit)
    public_jobs = [_public_job(job) for job in jobs]
    active = [job for job in public_jobs if not job["terminal"]]
    return success(Codes.JOB_STATUS_OK, jobs=public_jobs, active_count=len(active))


@router.get("/{job_id}", name="get_job")
def get_job(job_id: str, user=Depends(get_current_user)):
    job = job_service.get_job_for_user(job_id, int(user["id"]))
    if not job:
        raise HTTPException(
            status_code=404,
            detail={"code": Codes.NOT_FOUND, "message": "Job nao encontrado"},
        )
    return success(Codes.JOB_STATUS_OK, job=_public_job(job))
