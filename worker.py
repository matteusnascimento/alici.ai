"""
Simple RQ worker launcher for processing curation jobs.
Run this on the host where Redis is reachable.

Usage:
    python worker.py

It will start an RQ worker listening on the default queue and importing the `memory` module.
"""
from rq import Worker, Queue, Connection
from redis import Redis
import os

if __name__ == '__main__':
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    redis_conn = Redis.from_url(redis_url)
    with Connection(redis_conn):
        q = Queue()
        w = Worker([q])
        print('RQ worker started, waiting for jobs...')
        w.work()
