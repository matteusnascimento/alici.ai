Go-Live Checklist — ALICI

1. Secrets & env
- [ ] `SECRET_KEY` set and different from dev default
- [ ] `DATABASE_URL` (Postgres/Neon) configured
- [ ] `REDIS_URL` configured and reachable
- [ ] Provider keys set: `OPENAI_API_KEY` / `GROQ_API_KEY` / `GEMINI_API_KEY` as needed
- [ ] `ALICI_R2_*` configured if using R2

2. Migrations & DB
- [ ] Run migrations: `alembic upgrade head` (or `python scripts/render_migrate.py` on Render)
- [ ] Confirm `alembic_version` table present
- [ ] Run smoke queries and confirm `SELECT 1` passes

3. Infra & dependencies
- [ ] Redis reachable (ping) and workers connected
- [ ] Object storage (R2/S3) credentials validated (if used)
- [ ] Sentry DSN configured (optional)

4. App checks
- [ ] `GET /health` returns OK with `ia_disponivel` and `ai_providers`
- [ ] `GET /health/ready` returns ready and DB/Redis OK
- [ ] Run smoke: `POST /api/chat/send` and `POST /chat` (sample requests)
- [ ] Verify rate-limiting paths excluded: `/health`, `/static`

5. Security
- [ ] CORS_ALLOWED_ORIGINS set to production domains (no `*`)
- [ ] HTTPS terminated at load balancer (PUBLIC_APP_URL starts with `https://`)
- [ ] Rotate any temporary test keys

6. Scaling & workers
- [ ] Start web service with 1+ instance
- [ ] Start worker(s) using `arq` with proper concurrency
- [ ] Monitor logs for job failures and requeue behavior

7. Observability
- [ ] Sentry/Papertrail confirmed working
- [ ] Basic alerts: high error rate, job failures, Redis down

8. Post-deploy smoke tests
- [ ] Create test user and perform full chat flow
- [ ] Verify billing flow (test Stripe keys)
- [ ] Verify uploads & media processing

Render quick commands
```bash
# Build & deploy via Render dashboard or push to main branch
# Ensure env vars set on Render before scaling
# If using Procfile, Render will detect and run web + workers
```

Optional: Push to GitHub after final commit:
```bash
git add .
git commit -m "chore: final go-live fixes (redis, r2, health, README, checklist)"
git push origin main
```