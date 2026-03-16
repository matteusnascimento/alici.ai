import os
from redis import Redis
from rq import Queue


def send_email(payload: dict) -> dict:
    return {"sent": True, "to": payload.get("to")}


def enqueue(payload: dict):
    conn = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    queue = Queue("email", connection=conn)
    return queue.enqueue(send_email, payload)
