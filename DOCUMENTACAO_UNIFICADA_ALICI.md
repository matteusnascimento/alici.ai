# DOCUMENTACAO UNIFICADA ALICI

Data de consolidacao: 2026-03-08
Escopo: consolidacao tecnica e funcional do projeto ALICI em um unico documento, com base na documentacao existente e no estado atual do codigo.

## 1. Resumo executivo

ALICI e uma plataforma SaaS de IA multimodal orientada a produto enterprise, com:
- chat inteligente com memoria,
- base de conhecimento e RAG,
- agentes e automacoes,
- integracoes externas,
- billing e governanca por plano,
- frontend moderno em Next.js.

A arquitetura atual combina backend FastAPI modular, servicos de IA e frontend feature-driven. A estrategia de evolucao mira escala para alto volume de usuarios com design stateless, processamento assincrono e isolamento por tenant.

## 2. Visao do produto

Proposta central:
- oferecer infraestrutura de IA pronta para uso em produto digital e operacao B2B.

Capacidades principais:
- Conversational AI (chat com historico e contexto)
- Agents/Assistants (automacao e comportamento configuravel)
- Knowledge + Vector Search (RAG)
- Integrations hub (canais e ferramentas)
- Billing (planos e monetizacao)
- Analytics operacional
- API publica estilo produto de plataforma

Publico-alvo:
- startups e empresas que desejam IA integrada sem construir stack do zero,
- times que precisam automatizar operacoes via agentes,
- desenvolvedores que desejam API de IA com governanca.

## 3. Estado atual da arquitetura (codigo)

### 3.1 Backend

Entrypoint:
- `main.py`

Framework e runtime:
- FastAPI
- Uvicorn

Caracteristicas observadas:
- tratamento global de excecoes com envelope padrao de erro,
- montagem de rotas por dominio,
- rotas de compatibilidade legada (`/chat` e paginas em template),
- endpoints de health (`/health`, `/healthz`).

Rotas carregadas no backend atual:
- `/api/chat`
- `/api/conversations`
- `/api/auth`
- `/api/user`
- `/api/agents`
- `/api/billing`
- `/api/integrations`
- `/api/knowledge`
- `/api/analytics`
- `/api/workflows`
- `/api/platform`
- `/v1` (public API)
- `/api` (settings e expansion)
- `/api/ai` (arquitetura de IA)

### 3.2 Frontend

Aplicacao frontend principal:
- `frontend/alici-platform` (Next.js 14, App Router, TypeScript, Tailwind)

Padrao arquitetural:
- feature-driven modules (agents, chat, billing, integrations, workflows etc.),
- servicos de API separados,
- hooks por dominio,
- estado com Zustand,
- tipos compartilhados para contratos.

Camadas relevantes:
- `app/` (rotas e paginas)
- `features/` (modulos funcionais)
- `services/` (integracao HTTP)
- `types/` (contratos)
- `components/` (UI e blocos de tela)

## 4. Modulos funcionais consolidados

### 4.1 Chat e Conversas
- Conversa com contexto historico.
- Endpoint legado para compatibilidade.
- Estrutura preparada para stream SSE em cenarios de resposta incremental.
- Frontend com pagina dedicada de chat e fluxo por conversa.

### 4.2 Agents e Assistants
- Cadastro e gestao de agentes.
- Evolucao de schema para suporte a:
  - `instructions`
  - `tools`
  - `knowledge`
  - `memory`
- Compatibilidade com campos legados de prompt.

### 4.3 Knowledge e RAG
- Fluxo de ingestao de documentos para contextualizacao de respostas.
- Integracao com busca vetorial por servico dedicado.
- Estrutura de servicos para vector store e roteamento de modelo.

### 4.4 Workflows e Integracoes
- Rota de workflows ativa no backend e consumida no frontend.
- Integracoes com modelo extensivel por conectores.
- Roteiro de crescimento para canais como WhatsApp, Slack e similares.

### 4.5 Platform/Billing/Analytics
- Endpoints de plataforma com dados agregados para dashboard.
- Billing com modelo de planos e base para checkout.
- Analytics para acompanhamento de uso e operacao.

## 5. Contratos de API e padronizacao

Padrao recomendado e aplicado nas rotas principais:

```json
{
  "status": "success|error",
  "data": {},
  "error": {
    "code": "...",
    "message": "..."
  }
}
```

Beneficios:
- previsibilidade para frontend,
- tratamento uniforme de falhas,
- menor acoplamento entre paginas e formatos especificos de cada endpoint.

No frontend, o contrato foi centralizado por tipo compartilhado em:
- `frontend/alici-platform/types/api.ts`

## 6. Persistencia e dados

Base relacional:
- Postgres (producao) com fallback local em contexto de desenvolvimento em partes do projeto.

Evolucao de schema:
- migracoes versionadas via Alembic,
- migracao recente para ampliar modelo de agentes:
  - `migrations/versions/20260308_0004_add_agent_schema_fields.py`

Dados de IA e contexto:
- memoria de usuario (servico dedicado),
- base vetorial (servico dedicado),
- conhecimento e embeddings em trilha de maturacao de RAG.

## 7. Seguranca e governanca

Controles presentes no ecossistema documental e de codigo:
- autenticacao JWT,
- rate limiting,
- CORS configuravel,
- padronizacao de erro no backend,
- checklist de hardening de producao documentado.

Checklist de hardening cobre:
- IAM e segredos,
- rede e perimetro,
- seguranca Kubernetes,
- auditoria e observabilidade,
- supply chain e CI/CD,
- runbooks de incidente.

## 8. Infra e operacao

Diretorio de infraestrutura:
- `infra/terraform`
- `infra/k8s`

Fluxo operacional recomendado:
1. provisionar infra com Terraform,
2. configurar segredos e registry,
3. aplicar manifests Kubernetes,
4. validar health checks e autoscaling,
5. executar carga e tuning.

## 9. Qualidade e testes

Guia de testes cobre:
- unitarios,
- integracao,
- e2e,
- cobertura e mocks.

Comandos de referencia (Python):
- `pytest tests/`
- `pytest tests/test_services.py`
- `pytest tests/ --cov=...`

Status recente observado em execucao tecnica:
- testes especificos da arquitetura de IA executaram com sucesso (2 passed no contexto da ultima validacao local).

## 10. Estrategia de escala (visao alvo)

Arquitetura alvo para milhoes de usuarios inclui:
- API stateless,
- processamento event-driven com filas/workers,
- isolamento por tenant,
- roteamento de modelos por custo/latencia,
- observabilidade completa com SLO.

SLOs de referencia documentados:
- alta disponibilidade da API,
- p95 controlado para chat e RAG,
- resiliencia em integracoes externas,
- controle de custo por workload.

## 11. Roadmap tecnico consolidado (90 dias)

Trilhas principais:
- fundacao de escala (infra + governanca),
- core de agentes v1,
- memoria inteligente + RAG MVP,
- tools e integracoes de producao,
- billing + API publica v1,
- operacao de escala + marketplace beta.

KPIs tecnicos chave:
- disponibilidade,
- latencia p95,
- sucesso de jobs assincronos,
- erro em webhooks,
- custo por volume de mensagens.

## 12. Estrutura atual relevante do repositorio

Camadas de codigo atuais (resumo pratico):
- Backend principal: `app/` + `main.py`
- Frontend Next.js: `frontend/alici-platform/`
- Infra: `infra/`
- Migracoes: `migrations/`
- Testes: `tests/`
- Legado preservado: `legacy/alici_api/`

Observacao:
- o conteudo legado foi movido para `legacy/alici_api/` para preservar historico e reduzir acoplamento com a arquitetura ativa.

## 13. Como executar (referencia consolidada)

### Backend
1. Instalar dependencias Python:
   - `pip install -r requirements.txt`
2. Configurar `.env` com chaves obrigatorias.
3. Subir app:
   - `uvicorn main:app --reload`

### Frontend (quando Node estiver disponivel)
1. `cd frontend/alici-platform`
2. `npm install`
3. `npm run dev`
4. Validacoes:
   - `npm run typecheck`
   - `npm run build`

## 14. Riscos e pendencias tecnicas

Riscos/prioridades de curto prazo:
- garantir toolchain frontend consistente em todos os ambientes (Node/npm),
- consolidar testes de contrato backend-frontend,
- reduzir divergencia entre documentacao historica (templates legados) e arquitetura atual (Next.js + app modular),
- fechar lacunas de observabilidade e hardening para producao total.

## 15. Decisoes arquiteturais recomendadas

1. Manter envelope API como contrato oficial para todas as rotas novas.
2. Padronizar dominio por modulo (routes/services/types/hooks).
3. Evoluir RAG com pipeline assincrono e metadados por tenant.
4. Tratar `legacy/alici_api` como referencia historica, sem reintroduzir dependencia direta.
5. Fortalecer CI/CD com gates obrigatorios:
   - testes,
   - typecheck,
   - validacao de migracao,
   - scan de seguranca.

## 16. Conclusao

ALICI possui base funcional robusta para uma plataforma de IA enterprise, com stack moderna, dominios de negocio bem definidos e documentacao ampla. A consolidacao deste documento unifica a visao tecnica e de produto em um artefato unico, reduzindo ambiguidade e servindo como referencia principal para execucao, evolucao e governanca do projeto.
