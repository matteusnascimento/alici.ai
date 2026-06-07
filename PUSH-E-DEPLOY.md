# AXI — Push e Deploy Oficial

Este documento descreve o fluxo oficial atual para subir o AXI no GitHub e publicar no Render.

## Arquitetura oficial

Produção atual:

- `frontend/` — React/Vite/TypeScript.
- `backend/app/` — backend FastAPI oficial.
- `backend/alembic/` — migrations oficiais.
- `backend/scripts/render_migrate.py` — migration helper do Render.
- `render.yaml` — blueprint oficial de deploy.

Legado:

- `alici_api/` — backend legado/histórico.
- `alembic/` da raiz — migrations legadas.
- scripts antigos da raiz — compatibilidade/histórico.

Não use `uvicorn alici_api.app:app` para produção atual.

O comando oficial de produção é:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Push para GitHub

```bash
git status
git add .
git commit -m "chore: align AXI production deployment"
git push origin main
```

## Deploy oficial no Render

Preferencialmente use o Blueprint:

1. Acesse Render Dashboard.
2. Clique em **New +**.
3. Selecione **Blueprint**.
4. Conecte o repositório `matteusnascimento/alici.ai`.
5. Use o arquivo `render.yaml`.
6. Configure as variáveis `sync: false`.

O `render.yaml` usa:

```yaml
rootDir: backend
startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Variáveis obrigatórias

```env
APP_ENV=production
ENV=production
DATABASE_URL=postgresql://...
SECRET_KEY=...
CORS_ALLOWED_ORIGINS=https://alici-ai.onrender.com
```

## Variáveis por módulo

```env
OPENAI_API_KEY=...
GROQ_API_KEY=...
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
R2_ENDPOINT_URL=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
META_APP_ID=...
META_CLIENT_SECRET=...
META_WEBHOOK_VERIFY_TOKEN=...
```

## Validação esperada no deploy

O log correto deve conter:

```text
Context impl PostgresqlImpl.
Build successful 🎉
Your service is live 🎉
```

Se aparecer:

```text
Context impl SQLiteImpl.
```

o deploy não está usando o banco correto.

## Health checks

```text
GET /health
GET /api/health
```

## Checklist pós-deploy

- [ ] Render terminou com `Build successful`.
- [ ] Serviço terminou com `Your service is live`.
- [ ] Alembic usou `PostgresqlImpl`.
- [ ] `/health` retorna 200.
- [ ] `/api/health` retorna 200.
- [ ] Cadastro de cliente novo funciona.
- [ ] Cliente novo não entra no perfil do fundador.
- [ ] Login/logout funciona.
- [ ] Fluxo empresa -> usuário -> integração funciona.
- [ ] Chat/IA responde ou falha com erro claro.
- [ ] Billing/Stripe validado em sandbox.
- [ ] Integrações Meta/WhatsApp validadas em sandbox.

## Workers

Não crie worker baseado em:

```bash
arq alici_api.jobs.queue.WorkerSettings
```

sem decisão explícita de manter um serviço legado.

Antes de criar workers em produção, valide se o worker pertence ao backend oficial `backend/app` ou se será tratado como serviço legado separado.

## Status real

O AXI está em estado:

```text
MVP avançado online / beta técnico
```

Pronto para teste controlado e validação com cliente piloto.

Ainda exige hardening antes de cliente pagante em escala.
