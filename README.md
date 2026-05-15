# alici.ai

Monolito FastAPI principal em `alici_api/`, com templates Jinja2 preservados, creditos atomicos, Stripe real, Redis, Arq, R2 e camada central de IA.

Relatorio operacional atual: `RELATORIO_MANUAL_STATUS_ATUAL_ALICI.md`.

## Rodar Local

```powershell
python -m pip install -r requirements.txt -r requirements-test.txt
docker run -d --name redis-alici -p 6379:6379 redis:7-alpine
python app_run.py --doctor
python app_run.py --migrate
python app_run.py
```

Comandos uteis:

```powershell
python app_run.py --web-only
python app_run.py --worker-only
python app_run.py --doctor
pytest
```

## Variaveis Minimas

Obrigatorias para producao:

```env
ENV=production
DATABASE_URL=postgresql://...
SECRET_KEY=troque-por-valor-forte
PUBLIC_APP_URL=https://seu-dominio.com
API_BASE_URL=https://seu-dominio.com
CORS_ALLOWED_ORIGINS=https://seu-dominio.com
ALLOWED_HOSTS=seu-dominio.com
REDIS_URL=redis://...
```

IA textual:

```env
DEFAULT_AI_PROVIDER=grok
GROK_API_KEY=
XAI_API_KEY=
GROQ_API_KEY=
GEMINI_API_KEY=
OPENAI_API_KEY=
OLLAMA_ENABLED=false
```

Storage e midia:

```env
R2_ENDPOINT_URL=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_UPLOADS=uploads
R2_PUBLIC_BASE_URL=
MEDIA_STORAGE_REQUIRED=true

REPLICATE_API_TOKEN=
LUMA_API_KEY=
RUNWAY_API_SECRET=
ELEVENLABS_API_KEY=
```

Stripe:

```env
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_PRO=
STRIPE_PRICE_ULTRA=
STRIPE_PRICE_ENTERPRISE=
```

## Deploy no Render

Crie servicos separados usando o mesmo repositorio e as mesmas variaveis de ambiente.

### Web Service

Build command:

```bash
pip install -r requirements.txt
alembic upgrade head
```

Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT --proxy-headers
```

Health check:

```text
/health/live
```

Readiness manual depois do deploy:

```text
/health/ready
/health/deep
```

### Worker Arq

Crie pelo menos um Background Worker:

```bash
arq alici_api.jobs.queue.WorkerSettings
```

Opcional para usuarios pagos:

```bash
arq alici_api.jobs.queue.HighPriorityWorkerSettings
```

Opcional para baixa prioridade:

```bash
arq alici_api.jobs.queue.LowPriorityWorkerSettings
```

## Stripe Webhook

Configure no Stripe:

```text
POST https://seu-dominio.com/webhooks/stripe
```

Eventos minimos:

- `checkout.session.completed`
- `invoice.payment_succeeded`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`

O grant de creditos usa idempotencia por `event_id` e por `invoice_id`.

## Testes

Os testes de lancamento ficam em `tests/launch`.

```powershell
pytest
```

O CI roda:

- `compileall`
- testes `tests/launch`
- cobertura basica de `alici_api`
- `python app_run.py --doctor`

## Go-Live Checklist

1. Rotacionar qualquer segredo que ja tenha sido exposto.
2. Confirmar que `.env` real nao esta versionado.
3. Configurar Neon/Postgres em `DATABASE_URL`.
4. Rodar `alembic upgrade head` no banco de producao.
5. Configurar Redis Cloud/Upstash em `REDIS_URL`.
6. Configurar Cloudflare R2 e validar `R2_PUBLIC_BASE_URL`.
7. Configurar Grok/xAI ou Groq para IA textual.
8. Configurar providers de midia que serao vendidos no produto.
9. Confirmar que falha de midia retorna erro honesto e nao cobra creditos.
10. Configurar produtos/precos Stripe.
11. Configurar webhook Stripe e validar eventos em modo teste.
12. Subir web service no Render.
13. Subir pelo menos um Arq worker no Render.
14. Rodar `python app_run.py --doctor` no ambiente.
15. Validar `/health/live`, `/health/ready` e `/health/deep`.
16. Rodar `pytest` antes do push final.
17. Fazer smoke test: login, chat, saldo de creditos, checkout, webhook, job de midia.
18. Configurar Sentry se `SENTRY_DSN` estiver disponivel.
19. Verificar logs de custo/provider/modelo/tokens/latencia.
20. Liberar cobranca publica somente quando `/health/ready` estiver 200.
