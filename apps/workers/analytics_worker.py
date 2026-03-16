import os
from redis import Redis
from rq import Queue


def process_event(event: dict) -> dict:
    return {"processed": True, "event": event}


def enqueue(event: dict):
    conn = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    queue = Queue("analytics", connection=conn)
    return queue.enqueue(process_event, event)
