# ALICI™ API

API FastAPI da ALICI com autenticação JWT, chat com memória, histórico e endpoints multimodais.

## Principais ajustes aplicados

- Resolução de conflitos e padronização de backend para produção.
- Token padronizado no frontend para uma única chave: `access_token`.
- Endpoint de refresh token: `POST /auth/refresh`.
- Refresh token com rotação e revogação persistida em banco (`refresh_tokens`).
- Validação de tipo JWT (`type=access` e `type=refresh`).
- Tratamento global de exceções sem vazamento de erro interno.
- Correlação por requisição com header `X-Request-ID`.
- CORS configurável por ambiente via `CORS_ALLOWED_ORIGINS`.
- Rate limiting global e por usuário/plano no chat.
- Upload de imagem com limpeza garantida de arquivo temporário.
- Camadas iniciais para escalabilidade: repository + service + DTOs.

## Estrutura (API)

- `alici_api/app.py`: fábrica da aplicação, middleware e handlers globais.
- `alici_api/routes/`: rotas (`auth`, `chat`, `history`, `health`, `media`, `billing`, `pages`).
- `alici_api/services/`: serviços de IA/mídia/autenticação.
- `alici_api/repositories/`: acesso a dados (usuário, histórico e refresh tokens).
- `alici_api/schemas.py`: DTOs (requests).

## Variáveis de ambiente

### Segurança / JWT

- `SECRET_KEY` (obrigatória em produção)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default: `60`)
- `REFRESH_TOKEN_EXPIRE_MINUTES` (default: `10080`)

### CORS

- `ENV` (`development` | `production`)
- `CORS_ALLOWED_ORIGINS` (lista separada por vírgula em produção)

Exemplo:

`CORS_ALLOWED_ORIGINS=https://app.seudominio.com,https://admin.seudominio.com`

### Rate Limit

- `RATE_LIMIT_ENABLED` (`true`/`false`, default `true`)
- `RATE_LIMIT_WINDOW_SECONDS` (default `60`)
- `RATE_LIMIT_MAX_REQUESTS` (default `60`)

### HuggingFace Hub (modelo textual)

O modelo textual da ALICI é carregado do HuggingFace Space <a href="https://huggingface.co/spaces/Matteusnascimento/alici.ai">Matteusnascimento/alici.ai</a>.

- `ALICI_HF_REPO_ID` (default: `Matteusnascimento/alici.ai`)
- `ALICI_HF_REPO_TYPE` (default: `space`)
- `ALICI_HF_SUBFOLDER` (opcional, subfolder dentro do Space)
- `HUGGINGFACE_TOKEN` — token de acesso gerado em <a href="https://huggingface.co/settings/tokens">https://huggingface.co/settings/tokens</a> (necessário para Spaces privados ou com rate-limit)
- `ALICI_HF_CACHE_DIR` (default: `/tmp/alici_hf_cache`)

> ⚠️ **Nunca armazene o token HuggingFace no código-fonte.** Use variáveis de ambiente ou um gerenciador de segredos.

Consulte `.env.example` para um modelo completo de configuração.

### Redis (obrigatório em produção)

- `REDIS_URL` — URL de conexão (ex: `redis://:<password>@redis-host:6379/0`).
- `REDIS_PREFIX` — prefixo de chaves (default `alici`).

Em `production` `REDIS_URL` é obrigatório; sem Redis a API não inicializa. Para desenvolvimento local use Docker:

```bash
docker run -p 6379:6379 --name alici-redis -d redis:7-alpine
```

### Cloudflare R2 (opcional, usado para modelos/artefatos)

- `ALICI_R2_ACCOUNT_ID`, `ALICI_R2_ACCESS_KEY`, `ALICI_R2_SECRET_KEY` — credenciais R2
- `ALICI_R2_BUCKET` — bucket (ex: `alici-lake`)
- `ALICI_R2_MODEL_PREFIX` — prefixo/pasta dos artefatos

Se usar R2, instale `boto3` e verifique `ALICI_R2_ENDPOINT` quando usar contas customizadas.

### Provedores de IA

- `DEFAULT_AI_PROVIDER` — `groq` | `gemini` | `ollama` | `openai` (default: `groq`)
- `GROQ_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`, etc. — configure apenas os que for usar.

As chaves faltantes desabilitam o provider correspondente; o app escolhe provider por ordem de fallback configurada.

## Rotas essenciais

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /api/status` (autenticado)
- `POST /chat` (autenticado)
- `POST /chat/image` (autenticado)
- `GET /history` (autenticado)
- `DELETE /history` (autenticado)
- `GET /health`

## Execução local
## Execução local

Dependências (recomendado criar um virtualenv):

```bash
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
```

Iniciar Redis local (recomendado):

```bash
docker run -p 6379:6379 --name alici-redis -d redis:7-alpine
```

Rodar a API (modo desenvolvimento):

```bash
# Usando o backend principal (alici_api)
uvicorn alici_api.app:app --reload --host 0.0.0.0 --port 8000

# Alternativa: se você usa a pasta legacy `backend/` (Render blueprint)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health checks:

```text
GET /health        -> liveness
GET /health/live   -> liveness (simple)
GET /health/ready  -> readiness (DB + Redis + models)
```

## Deploy (Render)
## Deploy (Render)

This repo contains two deployable backends historically: `alici_api` (root) and `backend/` (legacy). The Render blueprint in `render.yaml` targets `backend/`. The `Procfile` targets `alici_api` and also defines worker processes.

Recommended (simple): use `Procfile` with Render's `web` + `worker` services.

Procfile example (already present):

```text
web: uvicorn alici_api.app:app --host 0.0.0.0 --port $PORT
worker: arq alici_api.jobs.queue.WorkerSettings
worker-high: arq alici_api.jobs.queue.HighPriorityWorkerSettings
worker-dlq: arq alici_api.jobs.queue.DeadLetterWorkerSettings
```

Render CLI / Dashboard quick commands (web + worker):

1) Using Render dashboard: create two services:
	- Web service: start command `uvicorn alici_api.app:app --host 0.0.0.0 --port $PORT`
	- Worker service(s): start command `arq alici_api.jobs.queue.WorkerSettings`

2) Using `render.yaml` (example in repo) the web service is configured to build frontend + backend. If you prefer the root `alici_api` app, update `render.yaml` to point `rootDir: .` and `startCommand: uvicorn alici_api.app:app --host 0.0.0.0 --port $PORT`.

Render deploy steps (CLI):

```bash
# from repo root
render services create --name alici-backend --env production --branch main --repo https://github.com/your/repo.git
# Or push commits and let render auto-deploy from branch
```

Note: ensure `REDIS_URL`, `DATABASE_URL`, and `SECRET_KEY` are set in Render environment variables antes de escalar workers.
