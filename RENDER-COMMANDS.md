Render Deploy Commands (web + worker)

Assuming you have the Render CLI installed and are logged in (`render login`).

1) Create the web service (Python):

```bash
render services create \
  --name alici-backend-web \
  --type web \
  --env production \
  --repo https://github.com/your/repo.git \
  --branch main \
  --build-command "pip install -r requirements.txt && cd frontend && npm ci && npm run build && cd .. && alembic upgrade head" \
  --start-command "uvicorn alici_api.app:app --host 0.0.0.0 --port $PORT"
```

2) Create the worker service (ARQ):

```bash
render services create \
  --name alici-backend-worker \
  --type worker \
  --env production \
  --repo https://github.com/your/repo.git \
  --branch main \
  --start-command "arq alici_api.jobs.queue.WorkerSettings"
```

3) Environment variables
- Ensure `REDIS_URL`, `DATABASE_URL`, `SECRET_KEY` and provider keys are set in Render dashboard or via `render services env set`.

4) Scaling
- Start with 1 web instance and 1 worker. Increase workers per job throughput and monitor redis job queue.

Notes:
- If you prefer the `backend/` folder approach, change build/start commands accordingly (see `render.yaml`).
- If push requires private repo access, ensure Render has deploy key or GitHub integration enabled.
