# AXI / ALICI Platform

Plataforma SaaS AXI com backend FastAPI, frontend React/Vite, autenticação JWT, módulos de Revenue, Chats, Agents, Studio, Marketing, Integrations, Billing e Admin.

## Arquitetura oficial

O repositório possui código histórico da Alici, mas a arquitetura oficial atual é:

- `backend/app`: backend FastAPI oficial usado em produção no Render.
- `frontend`: aplicação web React/Vite oficial.
- `backend/alembic`: migrations oficiais do banco usado pelo backend de produção.
- `render.yaml`: blueprint oficial de deploy.
- `alici_api`: backend legado/compatibilidade histórica. Não é o backend principal do Render.
- `alembic/`: migrations legadas da raiz, relacionadas ao backend legado.

> Importante: novas features de produção devem ser implementadas em `backend/app` e `frontend`. Não use `alici_api` como alvo principal sem decisão explícita de migração.

## Deploy oficial no Render

O deploy oficial usa `render.yaml` com:

```yaml
rootDir: backend
startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

O build compila o frontend, copia `frontend/dist` para `backend/frontend_dist`, instala dependências do backend e executa as migrations via:

```bash
python scripts/render_migrate.py
```

A variável `DATABASE_URL` deve apontar para PostgreSQL/Neon. Em produção, o esperado no log é:

```text
Context impl PostgresqlImpl.
```

Nunca publique produção usando SQLite.

## Variáveis obrigatórias de produção

Configurações mínimas para o serviço web:

```env
APP_ENV=production
ENV=production
DATABASE_URL=postgresql://...
SECRET_KEY=uma_chave_forte_com_32_ou_mais_caracteres
CORS_ALLOWED_ORIGINS=https://alici-ai.onrender.com
```

Configurações recomendadas conforme módulos ativos:

```env
REDIS_URL=redis://...
OPENAI_API_KEY=...
GROQ_API_KEY=...
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
R2_ENDPOINT_URL=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=...
R2_PUBLIC_BASE_URL=...
META_APP_ID=...
META_CLIENT_SECRET=...
META_WEBHOOK_VERIFY_TOKEN=...
```

Chaves ausentes devem desabilitar providers externos com erro claro, sem derrubar o app inteiro, exceto variáveis obrigatórias como `DATABASE_URL` e `SECRET_KEY` em produção.

## Execução local do backend oficial

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Para desenvolvimento local, SQLite é permitido. Para produção, use PostgreSQL.

## Execução local do frontend

```bash
cd frontend
npm install
npm run dev
```

Build de produção:

```bash
cd frontend
npm run typecheck
npm run build
```

## Testes e validação

Backend oficial:

```bash
cd backend
python -m compileall app alembic
alembic heads
```

Testes backend:

```bash
pytest tests/backend -q
```

Frontend:

```bash
cd frontend
npm run typecheck
npm run build
npm run test -- --run
```

O GitHub Actions possui dois blocos:

- `production-backend`: valida `backend/app`, `backend/alembic` e `tests/backend`.
- `legacy-launch`: mantém testes históricos do `alici_api` enquanto o legado ainda existir.

## Rotas essenciais

Health:

```text
GET /health
GET /api/health
```

Autenticação:

```text
POST /api/auth/register
POST /api/auth/login
GET /api/auth/me
```

Módulos principais:

```text
/api/chat
/api/chats
/api/agents
/api/revenue
/api/marketing
/api/studio
/api/integrations
/api/billing
/api/admin
```

## Módulos atuais

- Landing/Home
- Auth e Account
- Revenue / Business Pulse
- Chats
- AXI Assistant
- Agents
- Marketing
- Studio
- Integrations
- Billing / Subscriptions
- Admin
- Notifications
- Tracker / Website Widget

## Legado

A pasta `alici_api` e arquivos antigos na raiz permanecem por compatibilidade e histórico. Antes de remover, valide dependências, testes e jobs que ainda possam referenciá-los.

Arquivos/pastas legados devem ser tratados como candidatos a `legacy/`, não como alvo de novas features.

## Checklist antes de cliente real

- Render com `PostgresqlImpl` no Alembic.
- Cadastro de novo cliente validado.
- Cliente não cai no perfil pessoal do fundador.
- Fluxo usuário -> empresa -> integração validado.
- Login/logout validado.
- Isolamento multiempresa validado.
- Stripe webhook validado em ambiente real/sandbox.
- Providers IA configurados ou falhando com erro claro.
- Uploads/exports críticos usando storage externo quando necessário.
