# Copilot instructions for ALICI

## Big picture architecture
- **Entrypoint**: [main.py](main.py) runs Uvicorn → FastAPI app in [alici_api/app.py](alici_api/app.py)
- **Core response pipeline** in [engine.py](engine.py): `gerar_resposta()` follows 6 layers: identity → memory → local rules → neural models → web search → fallback. Orchestrates calls to [identidade.py](identidade.py), [database.py](database.py), [resposta.py](resposta.py), [web_search.py](web_search.py), and [sistema_emocoes.py](sistema_emocoes.py).
- **Persistent memory**: PostgreSQL (Neon) via [database.py](database.py) (`memoria` table, confidence boosting on repeated answers).
- **Auth/user history**: [auth.py](auth.py) + [database_auth.py](database_auth.py) (JWT + `users`/`history` tables).
- **API Routes**: [alici_api/app.py](alici_api/app.py) serves `/auth/login`, `/auth/register`, `/chat`, `/history`, `/api/status`, `/chat/image`.
- **UI assets**: [templates](templates) and [Static](Static). Chat UI in [templates/chat.html](templates/chat.html) calls endpoints via [Static/chat.js](Static/chat.js).

## Data flows & integration points
- `gerar_resposta_com_emocao()` adds emotion metadata via `adicionar_metadados_resposta()` in [sistema_emocoes.py](sistema_emocoes.py), returning dict with `resposta`, `emocao`, `intensidade`, `cor_aura`, `velocidade_animacao`.
- **Web search**: [web_search.py](web_search.py) uses DuckDuckGo; now returns `{"resposta": str, "confianca": float}` for compatibility with engine.py confidence gating.
- **Neural models**: [engine.py](engine.py) loads from `model/` folder (flexible paths); gracefully degrades if unavailable.

## Runtime & workflows
- **Development**: `python main.py` (Uvicorn with reload on port 8000)
- **Production**: `uvicorn main:app --host 0.0.0.0 --port $PORT` (Render.com, Procfile configured)
- **Database init**: `python init_db.py` creates `memoria` and auth tables in PostgreSQL/Neon
- **Environment variables**: `DATABASE_URL` (Neon), `SECRET_KEY` (JWT), `PORT`, `ENV` (development/production)

## Project-specific conventions
- **Input normalization**: `pergunta` is lowercased early in `gerar_resposta()` and `responder_local()`; preserve this in new rules in [resposta.py](resposta.py).
- **Memory learning**: Triggered after successful responses (`aprender()` in [database.py](database.py)). Keep as side effect when extending response paths.
- **Chat UI endpoints** in [Static/chat.js](Static/chat.js) expect JSON: `/chat` (POST), `/history` (GET), `/api/status` (GET), `/chat/image` (POST). Align backend routes.
- **Error handling**: Database connection leaks fixed with try/finally; all routes return JSON with `{"resposta": ...}` schema.
- **Auth pattern**: JWT tokens via `create_access_token()`, validated by `get_current_user()` middleware in FastAPI.

## Key files at a glance
| File | Purpose |
|------|---------|
| [main.py](main.py) | Uvicorn entrypoint |
| [alici_api/app.py](alici_api/app.py) | FastAPI app with all routes |
| [engine.py](engine.py) | 6-layer decision pipeline |
| [database.py](database.py) | Memory (PostgreSQL) CRUD |
| [database_auth.py](database_auth.py) | Users & history (PostgreSQL) CRUD |
| [resposta.py](resposta.py) | ~260 local Q&A rules |
| [auth.py](auth.py) | JWT + bcrypt utilities |
| [web_search.py](web_search.py) | DuckDuckGo wrapper |
| [sistema_emocoes.py](sistema_emocoes.py) | Emotion detection for UI |
| [init_db.py](init_db.py) | DB initialization script |
