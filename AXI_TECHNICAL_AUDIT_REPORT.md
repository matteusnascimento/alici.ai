# AXI - Verificacao Tecnica Profunda (Arquitetura Full Stack)

Data: 12/04/2026  
Escopo: frontend, backend, banco, env, OpenAI, agentes, integracoes, AXI Studio, rotas, endpoints, services, models, schemas, deploy e fluxo real.

## 1) Estrutura real do projeto

## Top-level
- backend/
- frontend/
- tests/
- render.yaml
- README.md
- REFACTOR_SUMMARY.md
- RENDER_FRONTEND_DEPLOY.md
- dev.ps1

## Backend (FastAPI)
- API routes: backend/app/api/routes/
- Servicos: backend/app/services/
- Models SQLAlchemy: backend/app/models/
- Schemas Pydantic: backend/app/schemas/
- Core/config: backend/app/core/
- Alembic: backend/alembic/versions/
- Deploy migration helper: backend/scripts/render_migrate.py

## Frontend (React + Vite + TS)
- Router principal: frontend/src/router/AppRouter.tsx
- Services HTTP: frontend/src/services/
- Modulos UI: frontend/src/components/
- Hooks: frontend/src/hooks/
- Testes: frontend/src/test/

## Deploy
- Render blueprint: render.yaml
- Backend serve frontend buildado via frontend_dist

## 2) O que funciona (validado)

## Fluxos com backend correspondente
- Cadastro/login: frontend + backend alinhados.
- Chat: frontend + backend alinhados.
- Agentes v2: frontend + backend alinhados.
- Studio v2 (rotas e geracao): frontend + backend alinhados.
- Integracoes (catalog/status/disconnect): frontend + backend alinhados.
- Account/billing/dashboard/security: frontend + backend alinhados.

## Evidencia de testes executados (smoke)
- Backend: test_auth.py, test_chat.py, test_agents_v2.py, test_studio_module.py, test_integrations.py (passaram).
- Frontend: login.test.tsx, chat.test.tsx, platform.test.tsx, agents-v2-flow.test.tsx (passaram).

## 3) O que esta quebrado / inconsistente

## Critico
1. Modelo OpenAI default invalido no backend (corrigido nesta execucao).
- Arquivo: backend/app/core/config.py
- Problema anterior: openai_model = gpt-5.4-mini (modelo invalido).
- Correcao aplicada: openai_model = gpt-4o-mini.

## Alto
1. Duas pilhas de Studio no frontend (v2 real + legado mock local), risco de comportamento divergente.
- Mock legado importado por paginas antigas:
  - frontend/src/components/studio/tools/AdsWorkspace.tsx (usa studioService.ts)
  - frontend/src/components/studio/tools/PosterWorkspace.tsx
  - frontend/src/components/studio/tools/PhotoEditorWorkspace.tsx
  - frontend/src/components/studio/tools/RemoveBackgroundWorkspace.tsx
  - frontend/src/components/studio/tools/CaptionsWorkspace.tsx
  - frontend/src/components/studio/tools/MarketingToolsWorkspace.tsx
- Service mock: frontend/src/services/studioService.ts
- Service real API: frontend/src/services/studio.service.ts

2. Modulo Marketing legado com mock local sem backend real acoplado.
- Componentes:
  - frontend/src/components/marketing/CampaignBuilder.tsx
  - frontend/src/components/marketing/CreativeGenerator.tsx
  - frontend/src/components/marketing/FunnelBuilder.tsx
  - frontend/src/components/marketing/LandingPageBuilder.tsx
  - frontend/src/components/marketing/WhatsAppFlows.tsx
- Service mock: frontend/src/services/marketingService.ts
- Service real API: frontend/src/services/marketing.service.ts (uso pequeno via hook)

3. Segredos sensiveis presentes em backend/.env local (nao versionado, mas inseguro em texto plano).
- Arquivo: backend/.env
- Achado: contem credenciais de banco e chave OpenAI em claro.

## Medio
1. projectService usa localStorage sem sincronizacao backend.
- Service: frontend/src/services/projectService.ts
- Uso:
  - frontend/src/hooks/useStudioWorkspace.ts
  - frontend/src/components/studio/tools/StudioHomePage.tsx
  - frontend/src/components/studio/tools/ProjectsWorkspace.tsx

2. Sobreposicao de APIs de agentes (v1 e v2 coexistindo), aumenta custo de manutencao e risco de drift.
- frontend/src/services/agents.service.ts
- frontend/src/services/agentsV2.service.ts

3. Endpoints redundantes para assinatura:
- /account/subscription
- /billing/current
- /subscriptions/current

## Baixo
1. README inconsistente com estado atual da IA (diz “fase futura” em alguns trechos, enquanto backend ja integra OpenAI).
2. Rotas legacy de redirect ainda ativas em AppRouter para compatibilidade.

## 4) Arquivos mortos / duplicados / apenas visual

## Duplicados / concorrentes
- frontend/src/services/studioService.ts (mock)
- frontend/src/services/studio.service.ts (API)
- frontend/src/services/marketingService.ts (mock)
- frontend/src/services/marketing.service.ts (API)
- frontend/src/services/agents.service.ts (parcial legado)
- frontend/src/services/agentsV2.service.ts (principal)

## Apenas visual ou sem logica de backend (explicito)
- Workspace legado de Studio em frontend/src/components/studio/tools/* usa dados simulados do studioService.ts.
- Componentes de Marketing em frontend/src/components/marketing/* usam marketingService.ts mock.
- Esses modulos nao estao no fluxo principal moderno do router protegido (v2), mas existem e podem ser reusados indevidamente.

## 5) Verificacao frontend -> backend

## Cada pagina tem backend quando necessario?
- /login e /register: sim.
- /app/chat: sim.
- /app/agents/* (v2): sim.
- /app/studio/* (v2): sim.
- /app/account/*: sim.
- /app/dashboard: sim.
- /app/marketing/*: e redirect para Studio (nao modulo funcional proprio).

## Cada service frontend tem endpoint real?
- auth.service.ts: sim.
- chat.service.ts: sim.
- account.service.ts: sim.
- settings.service.ts: sim.
- settingsAccount.service.ts: sim.
- agentsV2.service.ts: sim.
- integrations.service.ts: sim.
- billing.service.ts / subscription.service.ts: sim (com redundancia).
- studio.service.ts: sim.
- marketing.service.ts: sim (uso ainda limitado).
- studioService.ts: nao (mock local).
- marketingService.ts: nao (mock local).
- projectService.ts: nao (localStorage local).

## 6) Verificacao endpoint -> schema/model/service

A maior parte dos endpoints centrais segue padrao coerente route -> service -> schema -> model.
Exemplos consistentes:
- auth: backend/app/api/routes/auth.py + backend/app/services/auth_service.py + backend/app/schemas/auth.py + backend/app/models/user.py
- chat: backend/app/api/routes/chat.py + backend/app/services/chat_service.py + backend/app/schemas/chat.py + models de conversation/message
- studio: backend/app/api/routes/studio.py + services studio_* + schemas studio + models studio_*
- agents: backend/app/api/routes/agents.py + services agent_* + schemas agent_runtime/agentes_v2 + models agent_*

Pontos de atencao arquitetural:
- Endpoints aliases/duplicados (chat send alias, subscription/current duplicado).
- Convivencia v1/v2 no dominio de agentes.

## 7) Banco e cobertura de fluxo

## Suporte de banco para fluxos principais
- Auth/account/subscription/settings: suportado.
- Chat/conversation/message/usage: suportado.
- Agents (runtime, knowledge, actions, logs, channels, tests): suportado.
- Studio (projects, versions, assets, exports, generations): suportado.
- Integracoes e webhooks: suportado.

## Migracoes
- Alembic configurado e com historico relevante em backend/alembic/versions/.
- Startup aplica create_all + schema sync, e Render usa migracao via backend/scripts/render_migrate.py.

## 8) ENV e seguranca

## Estado
- .gitignore protege .env e .env.* (bom).
- backend/.env.example esta adequado para onboarding.
- backend/.env local contem segredos reais em claro (risco operacional).

## Recomendacoes imediatas de seguranca
1. Rotacionar credenciais expostas (OpenAI e DB).
2. Mover segredos para secret manager do ambiente (Render env vars), nao manter em arquivo local compartilhavel.
3. Desativar ENABLE_DEV_SEED_USER fora de desenvolvimento local isolado.
4. Evitar uso de credencial de producao em APP_ENV=development.

## 9) OpenAI como provider padrao

## Resultado
- DEFAULT_AI_PROVIDER=openai em config/deploy: OK.
- Integracao de healthcheck OpenAI existe em /api/integrations/openai/test: OK.
- Correcao critica aplicada no modelo default para gpt-4o-mini: OK.

## 10) Deploy Render readiness

## Positivos
- render.yaml presente e coerente.
- buildCommand instala backend, builda frontend e copia para frontend_dist.
- startCommand uvicorn correto.
- DATABASE_URL via banco Render.

## Riscos
- README tem desatualizacoes sobre IA e pode gerar operacao incorreta.
- Dominio legado (mock/local) no frontend aumenta risco de regressao funcional apos deploy.

## 11) Correcao aplicada nesta auditoria

1. Correcao critica no backend:
- Arquivo alterado: backend/app/core/config.py
- Mudanca: openai_model default de gpt-5.4-mini para gpt-4o-mini.

## 12) O que ainda precisa ser feito

## Critica
1. Rotacionar imediatamente segredos encontrados em backend/.env e substituir por novos valores no ambiente seguro.

## Alta
1. Descontinuar frontend/src/services/studioService.ts e migrar usos para frontend/src/services/studio.service.ts.
2. Descontinuar frontend/src/services/marketingService.ts e migrar usos para frontend/src/services/marketing.service.ts.
3. Eliminar dependencia de localStorage em projectService (migrar para /studio/projects).

## Media
1. Definir estrategia unica para agentes (v2 como padrao) e deprecar v1.
2. Consolidar endpoints redundantes de subscription.
3. Atualizar README para refletir IA real em runtime.

## Baixa
1. Limpar rotas legacy quando telemetria confirmar nao uso.

## 13) Prioridade consolidada

- Critica: 1
- Alta: 3
- Media: 3
- Baixa: 1

## 14) Veredito final de readiness do AXI

Status atual: PARCIALMENTE PRONTO (com bloqueio de seguranca).

- Para homologacao tecnica: pronto com baixo risco funcional nos fluxos principais.
- Para producao com seguranca: NAO pronto ate rotacao de segredos e eliminacao de caminhos legados mock mais sensiveis.

Readiness estimado:
- Funcionalidade principal: alta
- Consistencia arquitetural: media
- Seguranca operacional: baixa ate rotacao de credenciais
- Deploy Render: tecnicamente apto, condicionado aos itens criticos de seguranca
