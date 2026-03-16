import os
from redis import Redis
from rq import Queue


def run_workflow(workflow_id: str) -> dict:
    return {"workflow_id": workflow_id, "status": "completed"}


def enqueue(workflow_id: str):
    conn = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    queue = Queue("workflow", connection=conn)
    return queue.enqueue(run_workflow, workflow_id)
