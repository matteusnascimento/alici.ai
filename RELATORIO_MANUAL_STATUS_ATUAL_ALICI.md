# ALICI.AI - Relatorio Manual Consolidado do Status Atual

Data da consolidacao: 2026-05-15
Escopo real avaliado: repositório local em `C:\Users\PC\dados\alici.ai`
Backend principal decidido: `alici_api/`
Status geral: **codigo em hardening avancado, mas ainda nao pronto para go-live sem configurar Redis, R2, providers de IA/midia e Stripe em producao**.

---

## 1. Objetivo deste documento

Este documento consolida os relatórios existentes no projeto e compara cada conclusão antiga com o estado real atual do código.

Ele deve ser usado como fonte de verdade operacional a partir de agora, porque vários relatórios antigos foram criados em fases diferentes do projeto e alguns falam de uma pilha antiga em `backend/app/`, enquanto a decisão atual é usar `alici_api/` como backend principal.

---

## 2. Resumo executivo

### Confirmado no código atual

- Backend principal FastAPI em `alici_api/`.
- Launcher único criado na raiz: `app_run.py`.
- `main.py` também continua exportando `app` para deploy ASGI.
- Configuração centralizada com Pydantic Settings v2 em `alici_api/config.py`.
- `.env.example` atualizado para Redis, Stripe, R2, providers de IA, media providers e Ollama.
- Redis obrigatório em produção por validação de settings.
- Rate limit Redis implementado em `alici_api/middleware/rate_limit.py`.
- Cache Redis para IA em `alici_api/services/ai_cache.py`.
- AI proxy centralizado em `alici_api/services/ai/`.
- Providers de texto: Grok/xAI, Groq, Gemini, Ollama e OpenAI.
- Provider padrao recomendado: `grok`, com `groq` como fallback rapido quando configurado.
- Ollama é opt-in, tem probe rápido e não entra no fallback se estiver offline.
- Health checks separados: `/health`, `/health/live`, `/health/ready`, `/health/deep`.
- Créditos atômicos implementados em `credit_repository.py` e `credit_service.py`.
- Migrações Alembic presentes para créditos, Stripe events, jobs Arq e idempotência por invoice.
- Stripe real implementado em `billing_service.py`, `routes/billing.py` e `routes/webhooks.py`.
- Jobs Arq implementados em `alici_api/jobs/`.
- Mídia paga deixou de ser fake:
  - imagem: Replicate/Flux e Runway;
  - vídeo: Luma e Runway;
  - áudio: ElevenLabs;
  - análise de imagem: Gemini ou OpenAI.
- Saídas de mídia são persistidas em Cloudflare R2, sem depender de `generated/` local.
- Mídia só debita crédito após sucesso do provider e persistência no R2.
- Se provider/R2 não estiver configurado, a API responde erro honesto com `charged:false`.
- Templates Jinja2 antigos foram preservados visualmente, com ajustes de mensagens falsas.
- Busca por termos de mock/fake em runtime ficou limpa fora de testes/package-lock.

### Confirmado no ambiente local atual

Resultado de `python app_run.py --doctor`:

```text
env=development
database_url=ok
redis_url=redis://localhost:6379/0
docs_enabled=True
openapi_enabled=True
r2_configured=no
redis_ready=no
```

Resultado de health com `TestClient` no estado local:

```text
/health       -> 200
/health/live  -> 200
/health/ready -> 503
/health/deep  -> 503
```

Isso está correto para o ambiente local atual, porque Redis/R2/providers ainda não estão ativos neste terminal.

---

## 3. Comparativo dos relatórios antigos versus estado real

| Relatório | Conclusão antiga | Estado real atual | Ação |
|---|---|---|---|
| `AXI_BILLING_STRIPE_REAL.md` | Stripe real implementado estruturalmente | Coerente com `alici_api/services/billing_service.py`, `routes/billing.py`, `routes/webhooks.py` | Manter como histórico, mas atualizar endpoints se necessário |
| `AXI_BILLING_PRODUCAO_VALIDADO.md` | Produção ativa estava defasada e sem endpoints novos | Ainda não há validação nova de produção nesta máquina | Continua como alerta: produção precisa novo deploy |
| `AXI_HARDENING_FINAL_CLIENTES_PAGANTES.md` | Código aprovado condicionalmente, staging dependente de deploy/migração | Parcialmente obsoleto; fala muito da pilha `backend/app` | Usar apenas como histórico |
| `AXI_VALIDACAO_FUNCIONAL_FINAL_PARA_CLIENTES_REAIS.md` | Muitos fluxos validados | Parcialmente obsoleto; mistura backend antigo e estado anterior | Revalidar após deploy do `alici_api` |
| `FICHA_TECNICA_MODELO_ALICI_CPU_SIMPLE.md` | Modelo textual via R2 implementado | Ainda compatível: `text_model_r2.py` existe e usa lazy-load/R2 | Manter como ficha técnica |
| `RENDER_FRONTEND_DEPLOY.md` | Deploy frontend/backend no Render com build embutido | Pode estar desatualizado em relação ao uso atual de `alici_api/` | Revisar antes do deploy final |
| `README.md` | Descreve API FastAPI e ajustes gerais | Parcialmente atual, mas precisa incorporar `app_run.py`, mídia real, R2 e health novo | Atualizar em seção futura |
| `AGENTS.md` | Orienta comandos usando `backend/` | Divergente da decisão atual (`alici_api/`) | Marcar como legado ou reescrever |
| `TROUBLESHOOTING_CHAT.md` | Foco em OpenAI e endpoint antigo | Desatualizado: AI agora passa pelo `AIManager` com Grok/Groq/Gemini/Ollama/OpenAI | Reescrever depois |
| `GUIA_TESTES_CHAT.md` | Guia de testes Responses API | Parcialmente legado; ajustado para remover menção de mock | Revalidar testes reais |
| `RESPONSES_API_INTEGRATION_SNAPSHOT.md` | Snapshot da pilha antiga OpenAI Responses | Fala de `backend/app`, não do backend atual principal | Arquivar como histórico |
| `AUDITORIA_USO_IA_TOOLS.md` | Auditoria de tools OpenAI | Parcialmente legado | Arquivar ou revalidar contra `alici_api` |
| Relatórios removidos nesta limpeza | Apontavam mocks/fakes antigos ou conclusões obsoletas | Removidos do working tree para não confundir lançamento | Não restaurar sem motivo |

---

## 4. Estrutura real do backend principal

### Entrypoints

- `app_run.py`
  - Launcher local único.
  - `python app_run.py` tenta subir API + worker.
  - Se Redis não responder em desenvolvimento, sobe apenas API e avisa.
- `main.py`
  - Exporta `app` para `uvicorn main:app`.
  - Mantém comandos `web`, `worker`, `migrate`, `doctor`, `all`.
- `alici_api/app.py`
  - Fábrica FastAPI.
  - Inclui routers de auth, billing, chat, media, jobs, webhooks, history, pages e health.

### Rotas principais

- `alici_api/routes/auth.py`
- `alici_api/routes/chat.py`
- `alici_api/routes/media.py`
- `alici_api/routes/jobs.py`
- `alici_api/routes/billing.py`
- `alici_api/routes/webhooks.py`
- `alici_api/routes/health.py`
- `alici_api/routes/history.py`
- `alici_api/routes/pages.py`

### Serviços principais

- `alici_api/services/ai/manager.py`
- `alici_api/services/ai_service.py`
- `alici_api/services/ai_cache.py`
- `alici_api/services/media_service.py`
- `alici_api/services/media_storage.py`
- `alici_api/services/media_uploads.py`
- `alici_api/services/credit_service.py`
- `alici_api/services/billing_service.py`
- `alici_api/services/generation_job_service.py`
- `alici_api/services/redis_client.py`
- `alici_api/services/prompt_security.py`

---

## 5. Status real por área

### 5.1 Configuração e segurança

Status: **bom, com pendências externas**.

Implementado:

- Pydantic Settings v2.
- Validação forte em produção.
- `SECRET_KEY` obrigatório em produção.
- `DATABASE_URL` PostgreSQL obrigatório em produção.
- `REDIS_URL` obrigatório em produção.
- CORS restrito em produção.
- Docs/OpenAPI desabilitados automaticamente em produção.
- Security headers centralizados.
- Prompt security em rotas de chat/mídia.

Pendências:

- Rotacionar qualquer segredo que já tenha sido exposto em `.env` local.
- Garantir que `.env` real nunca seja commitado.
- Revisar CSP depois de remover mais JS inline dos templates.

### 5.2 Banco, Alembic e créditos

Status: **implementado no código, exige `alembic upgrade head` no ambiente real**.

Migrações presentes:

- `0001_add_credit_system.py`
- `0002_add_stripe_events.py`
- `0003_extend_generation_jobs_for_arq.py`
- `0004_add_stripe_invoice_credit_idempotency.py`

Implementado:

- `credit_balances`
- `credit_transactions`
- `generation_jobs`
- `credit_pricing`
- `stripe_events`
- idempotência extra por invoice de Stripe.
- Spend atômico via `SELECT ... FOR UPDATE` em Postgres e fallback SQLite.
- Refund auditado.

Ponto crítico:

- Em produção, antes de abrir para usuários, rodar:

```powershell
alembic upgrade head
```

### 5.3 Stripe Billing

Status: **código real implementado, não validado neste ambiente contra Stripe/Render atual**.

Implementado:

- Checkout Session real.
- Customer Portal real.
- Webhook com assinatura.
- Tabela/evento de idempotência.
- Grant de créditos em pagamento bem-sucedido.
- Proteção por `invoice_id`.

Pendências externas:

- Configurar `STRIPE_SECRET_KEY`.
- Configurar `STRIPE_WEBHOOK_SECRET`.
- Configurar price IDs.
- Criar endpoint webhook no Stripe Dashboard apontando para `/webhooks/stripe`.
- Fazer smoke real com Stripe test mode.

### 5.4 IA textual

Status: **arquitetura correta; ambiente local sem provider ativo neste momento**.

Implementado:

- Camada central `AIManager`.
- Providers:
  - Grok/xAI;
  - Groq;
  - Gemini;
  - Ollama;
  - OpenAI.
- Fallback por provider padrao, disponibilidade, prioridade, custo e latência recente.
- Circuit breaker básico para provider instável.
- Ollama opt-in e probe rápido para não travar chat.
- Cache Redis para prompts/resultados.
- Logs com provider/model/tokens/latência.

Estado local verificado:

- `AIManager().available_providers()` retornou `[]` neste terminal.
- Isso significa que as chaves de IA textual não estão configuradas/visíveis no ambiente local atual.

Para ativar:

```env
DEFAULT_AI_PROVIDER=grok
GROK_API_KEY=
XAI_API_KEY=
GROQ_API_KEY=
GEMINI_API_KEY=
OPENAI_API_KEY=
OLLAMA_ENABLED=false
```

### 5.5 Mídia real

Status: **código real implementado; depende de R2 e chaves de providers**.

Implementado:

- Imagem real:
  - Replicate/Flux;
  - Runway fallback.
- Vídeo real:
  - Luma;
  - Runway fallback.
- Áudio real:
  - ElevenLabs.
- Análise de imagem:
  - Gemini;
  - OpenAI.
- Sem geração local fake.
- Sem SVG fake.
- Sem WAV senoidal.
- Sem JSON placeholder.
- Sem cobrança antes do sucesso.
- Resultado salvo em R2 antes de completar job.

Estado local:

- `r2_configured=no`.
- Sem R2 configurado, mídia paga deve falhar com erro honesto e `charged:false`.

Variáveis necessárias:

```env
R2_ENDPOINT_URL=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_UPLOADS=
R2_PUBLIC_BASE_URL=

REPLICATE_API_TOKEN=
LUMA_API_KEY=
ELEVENLABS_API_KEY=
RUNWAY_API_SECRET=
```

### 5.6 Redis, cache e rate limit

Status: **implementado; local atual sem Redis respondendo**.

Implementado:

- Redis client central.
- Rate limit via Redis.
- AI cache via Redis.
- Arq jobs via Redis.
- Redis obrigatório em produção.

Estado local:

- `redis_ready=no`.

Para subir local:

```powershell
docker run -d --name redis-alici -p 6379:6379 redis:7-alpine
```

### 5.7 Jobs Arq

Status: **implementado no código; depende de Redis ativo**.

Implementado:

- `alici_api/jobs/queue.py`
- `alici_api/jobs/generation_jobs.py`
- filas default/high/low/dead.
- progress tracking.
- DLQ.
- refund em falha quando houve cobrança.
- mídia usa `charge_on_success`.

Comandos:

```powershell
python app_run.py --worker-only
python main.py worker
python main.py worker-high
python main.py worker-dlq
```

### 5.8 Templates e frontend

Status: **Jinja2 preservado; frontend React possui relatórios antigos e deve ser revalidado separadamente**.

Implementado recentemente:

- `templates/chat.html` não mostra mais `Sem resposta.` como resposta falsa.
- `templates/quantum.html` mostra erro honesto quando a IA falha.
- `routes/pages.py` não renderiza HTML improvisado quando template falta.
- `frontend/src/components/account/pages/AccountSecurityPage.tsx` não exibe mais sessões fictícias.
- Badges “Em breve” trocados para “Indisponivel”.

Pendência:

- `npm` não está disponível no PATH desta máquina, então typecheck/build frontend não foi executado nesta consolidação.

### 5.9 Testes e validação

Executado nesta fase:

```powershell
python -m compileall alici_api engine.py resposta.py main.py app_run.py
python app_run.py --doctor
git diff --check
```

Resultado:

- Compilação Python: passou.
- `git diff --check`: passou.
- `app_run.py --doctor`: passou, mas mostrou Redis/R2 ausentes.
- Health local: `/health/ready` e `/health/deep` retornam 503 porque o ambiente não está pronto.

Não executado:

- Suite pytest completa.
- Typecheck/build frontend.
- Smoke real Stripe.
- Smoke real mídia com R2/provider.
- Smoke real Render/produção.

---

## 6. Divergências importantes encontradas

1. Muitos relatórios antigos falam da pilha `backend/app/`, mas a decisão operacional atual é usar `alici_api/`.
2. Alguns relatórios dizem “pronto para produção”, mas o health atual local mostra `ready=false` enquanto providers/Redis/R2 não forem configurados.
3. Relatórios de billing em produção indicam que o deploy público antigo estava defasado. Não há evidência nova neste terminal de que produção já recebeu o código atual.
4. `README.md`, `AGENTS.md` e guias antigos foram removidos da raiz por decisao operacional; este relatorio concentra os comandos atuais de `app_run.py`, `alici_api/`, R2, Arq e health checks.
5. O frontend React moderno existe, mas o pedido atual preserva templates Jinja2 antigos; validar ambos separadamente antes de deploy.

---

## 7. Manual operacional atual

### Verificar ambiente

```powershell
python app_run.py --doctor
```

Se Redis local nao estiver ativo:

```powershell
docker run -d --name redis-alici -p 6379:6379 redis:7-alpine
```

O doctor atual mostra `redis_local_setup=...` quando Redis nao responde, lista `r2_missing=...` quando R2 esta incompleto e exibe o status de cada provider de IA/midia sem imprimir segredos.

### Rodar somente API local

```powershell
python app_run.py --web-only
```

### Rodar API + worker quando Redis estiver ativo

```powershell
python app_run.py
```

### Rodar worker

```powershell
python app_run.py --worker-only
```

### Rodar migrações

```powershell
python app_run.py --migrate
```

### Testar health

```powershell
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/health/live
curl http://127.0.0.1:8000/health/ready
curl http://127.0.0.1:8000/health/deep
```

Interpretação:

- `/health/live` deve ser 200 se o processo está vivo.
- `/health/ready` deve ser 200 apenas quando banco, Redis, R2 obrigatório e pelo menos um provider de IA textual estão prontos.
- `/health/deep` faz checks mais completos, incluindo probe de providers locais e probe de bucket R2 quando aplicável.

---

## 8. Checklist para deixar pronto para go-live

### Infra obrigatória

- [ ] Neon/Postgres configurado em `DATABASE_URL`.
- [ ] Redis Cloud/Upstash configurado em `REDIS_URL`.
- [ ] Em dev local, rodar `docker run -d --name redis-alici -p 6379:6379 redis:7-alpine` antes de testar jobs/cache/rate limit.
- [ ] Cloudflare R2 configurado para uploads e mídia gerada.
- [ ] Bucket R2 público ou CDN configurado em `R2_PUBLIC_BASE_URL`.
- [ ] Worker Arq rodando como processo separado em produção.
- [ ] `alembic upgrade head` executado no banco real.

### IA

- [ ] `GROK_API_KEY` ou `XAI_API_KEY` configurada para Grok/xAI como provider principal.
- [ ] `GROQ_API_KEY` configurada como fallback rapido/custo baixo.
- [ ] `GEMINI_API_KEY` configurada se quiser fallback barato/visão.
- [ ] `OPENAI_API_KEY` configurada apenas se realmente for usar fallback pago.
- [ ] `OLLAMA_ENABLED=false` em produção, exceto se houver Ollama local confiável no mesmo ambiente.
- [ ] Testar `/chat` com provider real.
- [ ] Confirmar logs com provider/model/tokens/latência.

### Mídia

- [ ] `REPLICATE_API_TOKEN` para imagens.
- [ ] `LUMA_API_KEY` ou `RUNWAY_API_SECRET` para vídeo.
- [ ] `ELEVENLABS_API_KEY` para áudio.
- [ ] Testar geração de imagem e confirmar URL final no R2.
- [ ] Testar geração de vídeo e confirmar URL final no R2.
- [ ] Testar áudio e confirmar URL final no R2.
- [ ] Confirmar que erro de provider não cobra crédito.

### Stripe

- [ ] Criar produtos e prices no Stripe.
- [ ] Configurar `STRIPE_SECRET_KEY`.
- [ ] Configurar `STRIPE_PUBLISHABLE_KEY`.
- [ ] Configurar `STRIPE_WEBHOOK_SECRET`.
- [ ] Configurar `STRIPE_PRICE_PRO`, `STRIPE_PRICE_ULTRA`, `STRIPE_PRICE_ENTERPRISE`.
- [ ] Configurar webhook para `POST /webhooks/stripe`.
- [ ] Testar `checkout.session.completed`.
- [ ] Testar `invoice.payment_succeeded`.
- [ ] Confirmar grant de créditos uma única vez por invoice.

### Segurança

- [ ] Trocar `SECRET_KEY`.
- [ ] Rotacionar qualquer segredo que já tenha sido exposto.
- [ ] Garantir `.env` fora do Git.
- [ ] CORS restrito ao domínio final.
- [ ] `PUBLIC_APP_URL` e `API_BASE_URL` com HTTPS.
- [ ] Sentry DSN configurado se for usar observabilidade.

### Validação final

- [ ] `python -m compileall alici_api engine.py resposta.py main.py app_run.py`
- [ ] `pytest` da suíte crítica.
- [ ] Build/typecheck frontend quando `npm` estiver disponível.
- [ ] Smoke local com Redis.
- [ ] Smoke staging Render.
- [ ] Smoke Stripe test mode.
- [ ] Smoke mídia real com R2.
- [ ] `/health/ready` retornando 200 em produção.
- [ ] `/health/deep` retornando 200 em produção.

---

## 9. Limpeza de relatorios duplicados

Este arquivo passou a ser o unico relatorio oficial de status do projeto.

Foram consolidados e removidos os relatorios antigos que competiam com este documento:

- `AUDITORIA_USO_IA_TOOLS.md`
- `AXI_BILLING_PRODUCAO_VALIDADO.md`
- `AXI_BILLING_STRIPE_REAL.md`
- `AXI_HARDENING_FINAL_CLIENTES_PAGANTES.md`
- `AXI_IMPLEMENTACAO_APLICACOES_COMPLETAS.md`
- `AXI_VALIDACAO_FUNCIONAL_FINAL_PARA_CLIENTES_REAIS.md`
- `FICHA_TECNICA_MODELO_ALICI_CPU_SIMPLE.md`
- `PROFILE_REDESIGN_SUMMARY.md`
- `REFACTOR_SUMMARY.md`
- `RESPONSES_API_INTEGRATION_SNAPSHOT.md`
- `THEME_PREFERENCES_IMPLEMENTATION.md`

Por ordem operacional final, todos os outros arquivos `.md` da raiz tambem foram removidos. Este documento ficou como o unico Markdown de referencia no diretorio principal do projeto.

---

## 10. Conclusão técnica

O código atual está muito mais próximo de uma versão monetizável do que os relatórios antigos indicam, principalmente porque:

- mídia fake foi substituída por providers reais;
- cobrança de mídia passou a ocorrer só após sucesso;
- storage local efêmero foi substituído por R2;
- Ollama deixou de travar fallback quando offline;
- health checks passaram a reportar prontidão real;
- mocks visíveis e relatórios obsoletos foram removidos do caminho principal.

Mas o projeto ainda não deve ser considerado pronto para lançamento público enquanto:

1. Redis não estiver ativo em produção.
2. R2 não estiver configurado.
3. Pelo menos um provider de IA textual não estiver configurado.
4. Pelo menos os providers de mídia vendidos no produto não estiverem configurados.
5. Stripe não estiver validado com webhook real.
6. Migrações não estiverem aplicadas no banco de produção.
7. Testes e smoke de deploy não forem executados.

Status final deste relatório: **pronto para próxima etapa de configuração/validação, ainda não pronto para abrir cobrança pública sem checklist completo**.
