# ALICI.ai — Copilot Coding Agent Instructions

## Project Overview

ALICI is a SaaS AI-chat platform (ChatGPT-style) built with **FastAPI** (Python) on the backend and vanilla JS/HTML/CSS on the frontend. It features JWT authentication, multi-conversation history, billing via Stripe, and AI responses from HuggingFace models.

---

## Architecture

```
alici.ai/
├── alici_api/               # Backend (FastAPI)
│   ├── app.py               # Application factory, middleware, global handlers
│   ├── config.py            # Settings (Pydantic / env vars)
│   ├── dependencies.py      # FastAPI dependency injection
│   ├── schemas.py           # Pydantic DTOs (request/response)
│   ├── responses.py         # Shared response helpers
│   ├── routes/              # Route modules (one file per domain)
│   │   ├── auth.py          # /auth/*
│   │   ├── chat.py          # /chat
│   │   ├── history.py       # /history
│   │   ├── billing.py       # /billing/*
│   │   ├── media.py         # /media/*
│   │   ├── health.py        # /health
│   │   └── pages.py         # HTML page serving
│   ├── services/            # Business logic (pure functions / classes)
│   │   ├── ai.py            # AI orchestration
│   │   ├── auth_service.py  # Password hashing, JWT creation
│   │   ├── media_service.py # File upload handling
│   │   ├── text_model_hf.py # HuggingFace inference (isolated)
│   │   └── text_model_r2.py # Cloudflare R2 model loader
│   ├── repositories/        # Database access layer (no business logic)
│   │   ├── user_repository.py
│   │   ├── history_repository.py
│   │   └── refresh_token_repository.py
│   └── middleware/
│       ├── rate_limit.py
│       └── request_id.py
├── templates/               # Jinja2 HTML templates
│   ├── chat.html            # Main chat UI (ChatGPT-style two-panel layout)
│   ├── login.html
│   ├── index.html
│   └── quantum.html
├── Static/
│   ├── js/
│   │   ├── app.js           # Main frontend logic
│   │   ├── api.js           # AliciAPI client (all fetch calls centralised here)
│   │   ├── chat.js          # Chat UI behaviour
│   │   └── neural-bg.js     # Animated neural-network background (canvas)
│   └── css/style.css
├── database.py              # DB connection + auto-migration helpers
├── main.py                  # Entry point (imports alici_api.app)
├── requirements.txt
├── Procfile                 # Render deployment: uvicorn alici_api.app:app
└── .env.example             # Template for all environment variables
```

### Key design rules

- **Routes** contain only request parsing and response serialisation — no business logic.
- **Services** contain all business logic and call repositories or external APIs.
- **Repositories** contain all SQL/ORM queries — no HTTP calls, no business logic.
- **Never** mix these three layers in the same function.
- Every route that touches user data **must** verify ownership (e.g. `conversation.user_id == current_user.id`).

---

## Authentication & Security

- JWT access tokens (`type=access`) + refresh tokens (`type=refresh`).
- Frontend stores tokens in `localStorage` under the key `access_token`.
- All authenticated routes go through the `get_current_user` dependency in `alici_api/dependencies.py`.
- Refresh token rotation and revocation are persisted in the `refresh_tokens` table.
- `POST /auth/refresh` must invalidate the old refresh token and issue a new pair.
- CORS origins are configured via `CORS_ALLOWED_ORIGINS` (comma-separated). In development, all origins are allowed.
- Rate limiting is applied globally and per-user/plan via `middleware/rate_limit.py`.
- File uploads are limited to ≤ 5 MB and temp files are always cleaned up after processing.
- Webhook payloads from Stripe must be verified with `stripe.Webhook.construct_event` before any processing.

---

## API Endpoints Reference

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login, returns access + refresh tokens |
| POST | `/auth/refresh` | Rotate refresh token |
| POST | `/auth/logout` | Revoke refresh token |
| GET  | `/auth/profile` | Get profile (name, email, photo_url, theme, plan) |
| PUT  | `/auth/profile` | Update name, password, or theme |
| POST | `/auth/profile/photo` | Upload avatar (≤ 5 MB) |

### Chat & History
| Method | Path | Description |
|--------|------|-------------|
| POST | `/chat` | Send a message, get AI response |
| POST | `/chat/image` | Send an image message |
| GET  | `/history` | List last 50 conversations |
| DELETE | `/history` | Clear all history |
| GET  | `/conversations/{id}/messages` | Messages for a conversation (ownership check required) |
| DELETE | `/conversations/{id}` | Delete conversation + messages |

### Billing
| Method | Path | Description |
|--------|------|-------------|
| POST | `/billing/create-checkout` | Create Stripe checkout session |
| POST | `/billing/webhook` | Stripe webhook (verify signature before handling) |

### Misc
| Method | Path | Description |
|--------|------|-------------|
| GET  | `/health` | Health check (no auth) |
| GET  | `/api/status` | Authenticated status |

---

## Frontend (AliciAPI client)

All HTTP calls from the frontend go through the **`AliciAPI`** class in `Static/js/api.js`. **Do not** use `fetch` directly in other JS files.

```js
// Pattern for adding a new API call
const result = await api.post('/some/endpoint', { key: value });
const data   = await api.get('/some/endpoint');
```

The client automatically:
- Attaches the `Authorization: Bearer <token>` header.
- Retries once after a 401 by calling `refreshToken()`.
- Handles multipart uploads when `isMultipart = true`.

---

## HuggingFace AI Service

- Located at `alici_api/services/text_model_hf.py`.
- Completely isolated: no imports from routes or repositories.
- Uses `tenacity` for automatic retries (3 attempts, 2 s fixed wait).
- Timeout and token limits are configurable via environment variables.
- **Never** load a model locally inside a route; always call the service layer.

---

## Database & Migrations

- Supports **SQLite** (local dev) and **PostgreSQL** (production) via `DATABASE_URL`.
- `database.py` applies lightweight auto-migrations on startup (e.g. `ALTER TABLE … ADD COLUMN IF NOT EXISTS`).
- Always add new columns through the auto-migration helper — do **not** drop or rename existing columns without a migration plan.

---

## Environment Variables

All variables are documented in `.env.example`. Key groups:

| Group | Variables |
|-------|-----------|
| App | `ENV`, `SECRET_KEY`, `DATABASE_URL` |
| JWT | `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_MINUTES` |
| CORS | `CORS_ALLOWED_ORIGINS` |
| Rate limit | `RATE_LIMIT_ENABLED`, `RATE_LIMIT_WINDOW_SECONDS`, `RATE_LIMIT_MAX_REQUESTS` |
| HuggingFace | `HUGGINGFACE_API_KEY`, `HUGGINGFACE_MODEL_URL`, `HUGGINGFACE_TIMEOUT_SECONDS`, `HUGGINGFACE_MAX_RETRIES` |
| HF Hub | `ALICI_HF_REPO_ID`, `ALICI_HF_REPO_TYPE`, `HUGGINGFACE_TOKEN` |
| Cloudflare R2 | `ALICI_R2_ACCOUNT_ID`, `ALICI_R2_ACCESS_KEY`, `ALICI_R2_SECRET_KEY`, `ALICI_R2_ENDPOINT`, `ALICI_R2_BUCKET` |
| Stripe | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_PRO`, `STRIPE_SUCCESS_URL`, `STRIPE_CANCEL_URL` |

**Never** commit real secrets. Always use environment variables or a secrets manager.

---

## Coding Standards

- Use **Python type hints** everywhere (function signatures and return types).
- Use **Pydantic schemas** (`alici_api/schemas.py`) for all request bodies and responses.
- Write **docstrings** for every public function/class.
- Structured logging via `logger.py` — use `logger.info/warning/error`, never `print`.
- Use the `X-Request-ID` header (injected by `middleware/request_id.py`) in log messages for traceability.
- Do **not** expose internal error details in HTTP responses — return generic messages and log the detail server-side.

---

## Local Development

```bash
pip install -r requirements.txt
cp .env.example .env          # then fill in your values
uvicorn alici_api.app:app --reload
```

Health check: `GET http://localhost:8000/health`

---

## Deployment (Render)

```
web: uvicorn alici_api.app:app --host 0.0.0.0 --port $PORT
```

Set all required environment variables in the Render dashboard. `DATABASE_URL` should point to a PostgreSQL instance in production.
