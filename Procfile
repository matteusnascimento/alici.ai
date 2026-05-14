web: uvicorn alici_api.app:app --host 0.0.0.0 --port $PORT
worker: arq alici_api.jobs.queue.WorkerSettings
worker-high: arq alici_api.jobs.queue.HighPriorityWorkerSettings
worker-dlq: arq alici_api.jobs.queue.DeadLetterWorkerSettings
