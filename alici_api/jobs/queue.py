"""Arq queue configuration and enqueue helpers."""

from __future__ import annotations

from arq import create_pool
from arq.connections import RedisSettings
from arq.worker import func

from alici_api.config import get_settings
from alici_api.jobs.generation_jobs import record_dead_letter_job, run_generation_job


def get_redis_settings() -> RedisSettings:
    settings = get_settings()
    return RedisSettings.from_dsn(settings.resolved_redis_url)


def queue_for_plan(plan: str | None) -> tuple[str, int]:
    settings = get_settings()
    normalized = (plan or "free").lower()
    if normalized in {"pro", "ultra", "enterprise"}:
        return settings.arq_queue_high, 90
    if normalized == "free":
        return settings.arq_queue_default, 50
    return settings.arq_queue_low, 25


async def enqueue_generation_job(job_id: str, *, queue_name: str | None = None):
    settings = get_settings()
    selected_queue = queue_name or settings.arq_queue_default
    redis = await create_pool(get_redis_settings())
    try:
        return await redis.enqueue_job(
            "run_generation_job",
            job_id,
            _job_id=job_id,
            _queue_name=selected_queue,
            _expires=settings.arq_job_timeout_seconds * max(settings.arq_max_retries, 1) + 300,
        )
    finally:
        await redis.close(close_connection_pool=True)


class WorkerSettings:
    functions = [
        func(run_generation_job, name="run_generation_job", max_tries=get_settings().arq_max_retries),
        func(record_dead_letter_job, name="record_dead_letter_job", max_tries=1),
    ]
    redis_settings = get_redis_settings()
    queue_name = get_settings().arq_queue_default
    max_jobs = 5
    job_timeout = get_settings().arq_job_timeout_seconds
    keep_result = get_settings().arq_keep_result_seconds
    retry_jobs = True


class HighPriorityWorkerSettings(WorkerSettings):
    queue_name = get_settings().arq_queue_high
    max_jobs = 10


class LowPriorityWorkerSettings(WorkerSettings):
    queue_name = get_settings().arq_queue_low
    max_jobs = 3


class DeadLetterWorkerSettings(WorkerSettings):
    queue_name = get_settings().arq_queue_dlq
    max_jobs = 2
    retry_jobs = False
