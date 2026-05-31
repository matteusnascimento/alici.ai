# Revenue Reuse Audit

## Objetivo

Centralizar operacao comercial, metricas, CRM, leads, pipeline, reservas, inbox e analytics dentro de Revenue, sem recriar modulos paralelos.

## Implementacoes Existentes Reaproveitadas

- `backend/app/services/revenue_service.py`: fonte principal de snapshot, funil, reservas, receita por canal/agente e serie historica.
- `backend/app/services/dashboard_service.py`: metricas gerais, uso, saude de IA e metricas de IA. Deve ser compatibilidade, nao nova fonte visual fora de Revenue.
- `backend/app/services/lead_service.py`: CRUD basico de leads existente.
- `backend/app/services/reservation_service.py`: criacao/atualizacao e disponibilidade de reservas existente.
- `backend/app/services/crm_service.py`: integracao externa com Pipedrive/HubSpot existente, deve alimentar Revenue CRM.
- `backend/app/services/agent_analytics_service.py`: metricas de agentes ja usadas no overview do agente, devem aparecer em Revenue via `view=agents`.
- `backend/app/models/lead.py`: tabela existente `leads`.
- `backend/app/models/reservation.py`: tabela existente `reservations`.
- `backend/app/models/conversation.py`: conversa de chat geral existente.
- `backend/app/models/agent_conversation.py`: conversa operacional de agentes, com canal, status, etapa comercial, valor de reserva e handoff humano.
- `backend/app/models/agent_message.py`: mensagens das conversas operacionais.
- `frontend/src/components/platform/DashboardPanel.tsx`: painel antigo com metricas uteis, mas nao deve ser rota final; `/app/dashboard` redireciona para Revenue.
- `frontend/src/components/revenue/RevenueIntelligencePage.tsx`: tela canonica atual para Revenue.

## Rotas Antigas ou Paralelas

- `/app/dashboard`: ja redireciona para `/app/revenue`.
- `/app/chat`: ja redireciona para `/app/agents`.
- `/app/agents/:id/analytics`: ja redireciona para `/app/revenue?view=agents`.
- `/api/dashboard/revenue-intelligence` e `/api/dashboard/revenue-series`: manter apenas como compatibilidade.

## Decisao

Criar `backend/app/api/routes/revenue.py` como roteador canonico `/api/revenue/*`, reaproveitando `RevenueService`, `LeadService`, `Reservation`, `AgentConversation` e `AgentMessage`.

Nao criar tabelas duplicadas `revenue_*` enquanto houver modelos existentes capazes de sustentar o fluxo. Novas tabelas so devem ser criadas quando o modelo atual nao representar o dominio necessario.

## Views Canonicas

- `/app/revenue?view=overview`
- `/app/revenue?view=inbox`
- `/app/revenue?view=leads`
- `/app/revenue?view=pipeline`
- `/app/revenue?view=crm`
- `/app/revenue?view=reservations`
- `/app/revenue?view=customers`
- `/app/revenue?view=tasks`
- `/app/revenue?view=post_sale`
- `/app/revenue?view=forecast`
- `/app/revenue?view=insights`
- `/app/revenue?view=reports`

Aliases preservados:

- `geral` -> `overview`
- `pipelines` -> `pipeline`
- `reservas` -> `reservations`
- `funil` -> `pipeline`
- `canais` -> `inbox`
- `conversoes` e `roi` -> `overview`
- `agents` e `marketing` continuam como views internas de Revenue.
