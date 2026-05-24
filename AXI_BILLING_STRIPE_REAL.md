# AXI — BILLING ATUAL EVOLUÍDO PARA STRIPE REAL

## 1. O que já existia e foi reaproveitado
- BillingService existente foi mantido e expandido (não recriado).
- Subscription model existente foi mantido e evoluído com campos Stripe.
- BillingEvent/history existente foi mantido e evoluído para rastreabilidade/idempotência.
- Endpoints existentes `GET /billing/plans`, `GET /billing/current`, `GET /billing/usage`, `GET /billing/history` foram mantidos.
- Endpoint legado `POST /billing/upgrade` foi mantido como compatibilidade/admin.
- Frontend existente (`useBilling`, `billing.service.ts`, `PlanCard.tsx`, `AccountPanel.tsx`) foi evoluído sem trocar arquitetura.

## 2. Campos/tabelas evoluídos
- `subscriptions` evoluída com:
  - `stripe_customer_id`
  - `stripe_subscription_id`
  - `stripe_price_id`
  - `provider`
  - `cancel_at_period_end`
  - `last_checkout_session_id`
  - `last_invoice_id`
  - `currency`
  - `external_status`
  - `metadata_json`
- `billing_events` evoluída com:
  - `stripe_event_id` (idempotência)
  - `status`
  - `payload_json`
- Migração Alembic criada: `backend/alembic/versions/b9f1c2d3e4f5_add_stripe_billing_fields.py`

## 3. Env vars adicionadas
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `STRIPE_PUBLISHABLE_KEY`
- `STRIPE_PRICE_PRO_MONTHLY`
- `STRIPE_PRICE_PRO_YEARLY`
- `STRIPE_PRICE_BUSINESS_MONTHLY`
- `STRIPE_PRICE_BUSINESS_YEARLY`
- `APP_BASE_URL`
- `STRIPE_SUCCESS_URL`
- `STRIPE_CANCEL_URL`

## 4. Endpoints novos
- `POST /billing/checkout`
- `POST /billing/portal`
- `POST /billing/cancel`
- `POST /billing/resume`
- `POST /billing/webhook`

## 5. Endpoints antigos mantidos por compatibilidade
- `GET /billing/plans`
- `GET /billing/current`
- `GET /billing/usage`
- `GET /billing/history`
- `POST /billing/upgrade` (marcado no código como legado/admin)

## 6. Checkout Stripe implementado
- Backend cria checkout session real via Stripe (`mode=subscription`).
- Resolve `price_id` por plano/ciclo usando env vars.
- Cria/reutiliza customer Stripe por usuário.
- Retorna `checkout_url` e `session_id` para redirect do frontend.
- Não confia em retorno do frontend para mudar plano.

## 7. Portal Stripe implementado
- Endpoint autenticado cria `billing_portal.Session` real.
- Frontend redireciona para URL do portal para gestão de assinatura.

## 8. Webhook implementado
- Verificação de assinatura via `stripe.Webhook.construct_event(...)`.
- Processamento de eventos:
  - `checkout.session.completed`
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.paid`
  - `invoice.payment_failed`
- Idempotência por `stripe_event_id`.
- Sincronização da assinatura local e redundância de `user.plan` preservada.
- Registro de `BillingEvent` com status/payload quando aplicável.

## 9. Limites por plano implementados
- Enforcements ativos no backend:
  - Mensagens: bloqueio em `/chat/send` ao atingir limite.
  - Agentes: bloqueio em `POST /agents` ao atingir limite.
- `UsageLog` agora é alimentado automaticamente no envio de mensagens (`chat`).
- Endpoint `/billing/usage` usa uso real:
  - `messages`: soma em `UsageLog`
  - `agents`: contagem de agentes não arquivados

## 10. Módulos agora protegidos por plano
- Chat: `POST /api/chat/send`
- Criação de agentes: `POST /api/agents`

## 11. Frontend atualizado
- `useBilling` evoluído com:
  - `startCheckout(planId, billingCycle)`
  - `openPortal()`
  - `cancel()`
  - `resume()`
- `PlanCard` evoluído com:
  - toggle mensal/anual
  - botão de gerenciar assinatura
  - upgrade via checkout real
- `AccountPanel` evoluído para:
  - exibir status real e próxima renovação
  - gerenciar assinatura (portal)
  - cancelar/reativar assinatura
- Novas rotas/páginas:
  - `/app/billing/success`
  - `/app/billing/cancel`

## 12. Testes executados
- Build frontend:
  - `npm run build` (OK)
- Testes frontend:
  - `npm run test` (OK)
  - Resultado final: 11 arquivos, 21 testes passados.
- Testes backend:
  - `python -m pytest tests/backend/ -q` (OK)
  - Resultado final: 47 testes passados.

## 13. O que ficou pronto
- Stripe Checkout real integrado ao backend e frontend.
- Stripe Billing Portal real integrado.
- Webhook real com validação + idempotência.
- Sincronização assinatura Stripe -> assinatura local.
- Eventos de billing persistidos com metadados úteis.
- Enforcement real de limites para chat e criação de agentes.
- Base legada preservada e expandida sem duplicar arquitetura.

## 14. O que ainda depende da configuração externa do Stripe
- Preencher env vars reais de produção com chaves/price IDs válidos.
- Criar produtos/price IDs no Stripe Dashboard.
- Configurar endpoint público de webhook no Stripe Dashboard apontando para `/api/billing/webhook`.
- Validar URLs de sucesso/cancel no ambiente final.
- (Opcional) Expandir enforcement para integrações/workspaces/features premium de studio/marketing conforme regras comerciais finais.

## VEREDITO FINAL
- o billing atual foi evoluído sem ser recriado? **Sim**.
- o checkout é real? **Sim** (Stripe Checkout Session real).
- o portal é real? **Sim** (Stripe Billing Portal real).
- o webhook é real? **Sim** (assinatura validada + idempotência).
- os limites estão sendo aplicados? **Sim**, para chat e criação de agentes.
- a área de billing está pronta para clientes pagantes? **Sim, estruturalmente pronta**; depende apenas da configuração externa real do Stripe em produção.
