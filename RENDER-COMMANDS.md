# Render Deploy Commands — AXI

Este documento descreve o deploy oficial atual do AXI no Render.

## Fonte de verdade

Use o `render.yaml` do repositório sempre que possível. Ele usa:

```yaml
rootDir: backend
startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

O backend de produção é `backend/app`. A pasta `alici_api/` é legado/compatibilidade histórica e não deve ser usada para criar novos serviços web de produção.

## Deploy recomendado: Blueprint

1. Render Dashboard → New + → Blueprint.
2. Selecione o repositório `matteusnascimento/alici.ai`.
3. Confirme o serviço `axi-backend` e o banco `axi-db`.
4. Configure as variáveis `sync: false`, como `OPENAI_API_KEY`, `STRIPE_SECRET_KEY` e demais secrets.
5. Faça deploy da branch `main`.

O build esperado executa:

```bash
pip install -r requirements.txt
cd ../frontend && npm ci && npm run build
cd ../backend
python scripts/render_migrate.py
```

O log correto de banco em produção deve mostrar:

```text
Context impl PostgresqlImpl.
```

## Criação manual do serviço web

Use apenas se não estiver usando Blueprint:

```bash
render services create \
  --name axi-backend \
  --type web \
  --env production \
  --repo https://github.com/matteusnascimento/alici.ai.git \
  --branch main \
  --root-dir backend \
  --build-command "pip install -r requirements.txt && cd ../frontend && npm ci && npm run build && test -f dist/index.html && cd ../backend && rm -rf frontend_dist && cp -r ../frontend/dist frontend_dist && python scripts/render_migrate.py" \
  --start-command "uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
```

## Variáveis obrigatórias

```env
APP_ENV=production
ENV=production
DATABASE_URL=postgresql://...
SECRET_KEY=...
CORS_ALLOWED_ORIGINS=https://alici-ai.onrender.com
```

Variáveis por módulo:

```env
OPENAI_API_KEY=...
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
R2_ENDPOINT_URL=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
META_APP_ID=...
META_CLIENT_SECRET=...
META_WEBHOOK_VERIFY_TOKEN=...
```

## Workers

Workers legados baseados em `alici_api.jobs.queue` não fazem parte do deploy web oficial atual. Antes de criar workers em produção, valide se o job runner já foi migrado para `backend/app` ou mantenha-o explicitamente como serviço legado separado.

Não use este comando para o web service oficial:

```bash
uvicorn alici_api.app:app --host 0.0.0.0 --port $PORT
```

## Health checks

```text
GET /health
GET /api/health
```

## Escala inicial

- Comece com 1 instância web.
- Só adicione workers depois de validar fila, Redis e ownership dos jobs.
- Monitore logs de Alembic, auth, chat, billing e integrações após cada deploy.
