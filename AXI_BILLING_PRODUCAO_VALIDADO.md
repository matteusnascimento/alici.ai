# AXI — BILLING PRODUÇÃO VALIDADO

## envs conferidas
- Não foi possível ler variáveis de ambiente diretamente do serviço em produção a partir deste terminal (sem acesso a Render Dashboard API/CLI autenticada neste ambiente).
- Validação indireta foi tentada via endpoints de billing Stripe em produção e mostrou que a versão ativa não expõe os endpoints novos.

Resultado:
- Status: não validado diretamente.
- Bloqueio: ausência de acesso administrativo ao ambiente Render para leitura de envs.

## stripe configurado
Validação indireta executada no host de produção:
- OpenAPI em produção não contém:
  - /api/billing/checkout
  - /api/billing/portal
  - /api/billing/cancel
  - /api/billing/resume
  - /api/billing/webhook
- Chamadas reais para esses endpoints retornaram 405 Method Not Allowed.

Conclusão técnica:
- A versão em execução em produção não é a versão Stripe-ready presente no repositório atual.
- Assim, não é possível confirmar configuração de Products/Prices reais do Stripe pelo fluxo do app ativo.

## webhook validado
- Não validado em produção.
- Evidência: endpoint /api/billing/webhook retornando 405 no ambiente ativo.
- Portanto, não há como confirmar recebimento/processamento de eventos Stripe neste estado de deploy.

## migração aplicada
Migração alvo:
- backend/alembic/versions/b9f1c2d3e4f5_add_stripe_billing_fields.py

Status:
- Não confirmada em produção por falta de acesso administrativo ao banco/serviço em execução.
- A resposta de /api/billing/current em produção indica payload antigo (sem campos novos de Stripe), reforçando que o deploy ativo está defasado.

Como aplicar exatamente (Render):
1. Abrir o serviço backend no Render.
2. Confirmar que o deploy está na revisão mais recente do repositório.
3. Abrir Shell do serviço (ou criar Job one-off com a mesma imagem/variáveis).
4. Executar:
   - cd /opt/render/project/src/backend
   - alembic upgrade head
   - alembic current
5. Confirmar que current inclui b9f1c2d3e4f5.
6. Garantir também que a migração de drift de conversations já aplicada no hardening (c4d5e6f7a8b9) esteja em head.
7. Reiniciar o serviço backend.

## smoke test executado
Smoke real executado em produção (API pública):

1) Fluxo base de auth e billing legado
- POST /api/auth/register -> 200
- GET /api/billing/plans -> 200
- GET /api/billing/current -> 200
- GET /api/billing/history -> 200
- GET /api/billing/usage -> 200

2) Fluxo Stripe esperado (produção ativa)
- POST /api/billing/checkout (pro monthly) -> 405
- POST /api/billing/checkout (pro yearly) -> 405
- POST /api/billing/checkout (business monthly) -> 405
- POST /api/billing/checkout (business yearly) -> 405
- POST /api/billing/portal -> 405
- POST /api/billing/cancel -> 405
- POST /api/billing/resume -> 405
- POST /api/billing/webhook -> 405

3) Enforcements relacionados
- Criação de 3 agentes no plano free retornou 200 nas três tentativas.
- Isso indica ausência do enforcement esperado para limite de agentes na versão ativa.
- Enforcements de chat não puderam ser validados ponta a ponta devido estado inconsistente atual do deploy ativo (já observado no hardening anterior com erro de schema no chat).

## resultado final
- Não pronto para cobrar clientes pagantes neste momento no ambiente de produção atual.

Bloqueios exatos:
1. Produção ativa não está com a versão Stripe-ready publicada (endpoints Stripe de billing ausentes).
2. Webhook de billing não está validável via aplicação ativa (rota ausente no deploy atual).
3. Migração b9f1c2d3e4f5 não está confirmada no runtime/banco de produção.
4. Enforcement esperado de limites (agentes) não está efetivo no comportamento observado em produção.

Critério objetivo para liberar cobrança:
1. Deployar revisão atual contendo billing Stripe real.
2. Aplicar alembic upgrade head e confirmar b9f1c2d3e4f5 + c4d5e6f7a8b9 em current.
3. Confirmar envs Stripe no Render:
   - STRIPE_SECRET_KEY
   - STRIPE_WEBHOOK_SECRET
   - STRIPE_PRICE_PRO_MONTHLY
   - STRIPE_PRICE_PRO_YEARLY
   - STRIPE_PRICE_BUSINESS_MONTHLY
   - STRIPE_PRICE_BUSINESS_YEARLY
4. Confirmar webhook no Stripe Dashboard para POST https://alici-ai.onrender.com/api/billing/webhook.
5. Reexecutar smoke de checkout real até:
   - checkout_url retornando 200
   - redirecionamento Stripe OK
   - retorno em /app/billing/success
   - evento de webhook processado
   - atualização de /api/billing/current, /api/billing/history, /api/billing/usage
   - enforcement efetivo em chat/agentes.
