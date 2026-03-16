import os
from redis import Redis
from rq import Queue


def index_document(document_id: str) -> dict:
    return {"document_id": document_id, "indexed": True}


def enqueue(document_id: str):
    conn = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    queue = Queue("vector", connection=conn)
    return queue.enqueue(index_document, document_id)
