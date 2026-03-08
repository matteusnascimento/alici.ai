# Arquitetura Completa ALICI para Milhoes de Usuarios

## 1. Objetivo de Escala

Este documento define a arquitetura alvo da ALICI como uma `AI Automation Platform` capaz de atender milhoes de usuarios com alta disponibilidade, baixo tempo de resposta, seguranca e controle de custo.

Metas operacionais:
- 99.95% de disponibilidade (camada API e chat).
- p95 < 1.5s para endpoints de chat sem ferramenta externa.
- p95 < 3.5s para fluxo com RAG.
- Escalar horizontalmente sem downtime.
- Isolamento forte por tenant (organizacao).

---

## 2. Principios de Arquitetura

- `API stateless`: escalar via replicas sem afinidade.
- `Event-driven`: tarefas lentas e externas via filas e workers.
- `Tenant-aware`: todos os dados indexados por `organization_id`.
- `Async-first`: I/O externo nao bloqueante.
- `Graceful degradation`: fallback local quando provedor externo falhar.
- `Cost-aware orchestration`: roteamento inteligente entre modelos.

---

## 3. Arquitetura Macro (Niveis)

```text
Clients (Web Next.js, Mobile Flutter, API Clients)
        |
   CDN + WAF + API Gateway
        |
    Edge Auth + Rate Limit
        |
   Core API (FastAPI services)
        |
+-----------------------------+
| Domain Services             |
| Chat | Agents | RAG | Tools |
| Billing | Integrations      |
+-----------------------------+
        |
+------------------------------------------------+
| Data Plane                                      |
| Postgres (OLTP) | Redis | Vector DB | Object   |
| Queue (Kafka/Rabbit/SQS) | Analytics Store      |
+------------------------------------------------+
        |
 Providers: LLMs, Stripe, WhatsApp, Slack, Email
```

---

## 4. Core de Agentes (Coracao da Plataforma)

Modelo canonical do agente:

```text
Agent
├ Tools
├ Memory
├ Planner
├ Executor
└ Knowledge
```

### 4.1 Componentes

- `Agent Registry`: cadastro, versionamento, publicacao e rollout.
- `Planner`: quebra objetivo em passos (task graph).
- `Executor`: executa passos com retries e timeout.
- `Tool Runtime`: sandbox para ferramentas com permissoes por agente.
- `Policy Guard`: valida seguranca, custo e compliance antes da execucao.
- `Agent State Store`: estado transitorio e checkpoints.

### 4.2 Fluxo de criacao no produto

```text
Criar agente -> Selecionar ferramentas -> Definir comportamento -> Publicar
```

### 4.3 Escalabilidade

- Agentes executados em workers desacoplados da API.
- Fila por tipo de workload (chat, automacao, integracao).
- Idempotencia por `run_id` para evitar acao duplicada.
- Dead-letter queue para erros nao recuperaveis.

---

## 5. Sistema de Memoria Inteligente

### 5.1 Memoria curta (conversa)

- Armazenada em Redis (TTL configuravel).
- Janela de contexto por sessao (ex.: ultimas N mensagens e resumo recente).
- Compressao automatica de historico para reduzir tokens.

### 5.2 Memoria longa (usuario/tenant)

- Persistencia em Postgres + vetorizacao em Vector DB.
- Tipos:
  - preferencias do usuario
  - fatos persistentes
  - historico resumido
- Processo de consolidacao assincromo (worker de memoria).

### 5.3 Politica de recuperacao

- Recencia + similaridade semantica + prioridade manual.
- Top-k memórias por consulta.
- Isolamento por tenant e opcionalmente por usuario.

---

## 6. Knowledge Base e RAG

### 6.1 Pipeline

```text
Upload -> Parsing -> Chunking -> Embedding -> Indexacao vetorial -> Retrieval -> Re-ranking -> Resposta
```

### 6.2 Fontes aceitas

- PDF, DOC, TXT, FAQ, website, CSV, markdown.

### 6.3 Armazenamento

- Metadados e ACL em Postgres.
- Arquivos originais em Object Storage (S3/R2/GCS).
- Embeddings em `pgvector` (MVP) ou `Qdrant/Weaviate` (escala maior).

### 6.4 Praticas para escala

- Ingestao assincrona por lotes.
- Re-indexacao incremental por versao de documento.
- Cache de resultados de retrieval por consulta normalizada.

---

## 7. Sistema de Ferramentas (Tools)

Estrutura alvo:

```text
tools/
├ web_search
├ database_query
├ email_sender
├ calendar
└ http_request
```

### Requisitos de producao

- Manifesto da tool: schema de entrada/saida, timeout, permissoes.
- Execucao isolada (container/sandbox) para ferramentas sensiveis.
- Auditoria completa de chamada: quem, quando, custo, resultado.
- Circuit breaker por integracao externa.

---

## 8. Hub de Integracoes

Integracoes prioritarias:
- WhatsApp, Instagram, Telegram, Slack, Discord, Shopify, WordPress.

### Arquitetura

- `Connector API`: credenciais e onboarding.
- `Webhook Ingress`: entrada de eventos externos.
- `Event Normalizer`: padroniza payloads para o formato interno.
- `Action Dispatcher`: envia resposta/acao para canal externo.

### Escala

- Particionamento por canal e tenant.
- Reentrega com retry exponencial.
- Protecao anti-spike com filas e rate limits por provedor.

---

## 9. Marketplace de Agentes

### Capacidades

- Publicar template de agente.
- Instalar por 1 clique.
- Versionamento semantico.
- Ranking por uso, avaliacao e categoria.

### Seguranca

- Assinatura de pacote do agente.
- Revisao automatica de tools permitidas.
- Permission boundary por tenant.

---

## 10. Dashboard Inteligente

Metricas minimas:
- mensagens processadas
- agentes ativos
- uso de tokens
- custo
- taxa de sucesso

### Arquitetura analitica

- Eventos operacionais em fila.
- Ingestao em stream para store analitica.
- Agregados pre-computados para dashboards p95 < 300ms.

---

## 11. Monetizacao e Billing (Stripe)

Planos:
- Free: chat basico
- Pro: agentes
- Business: integracoes
- Enterprise: API + automacoes

### Backend de billing

- Subscription state machine: `pending_checkout -> active -> canceling -> canceled`.
- Webhooks Stripe assinados para consistencia de estado.
- Quotas por plano aplicadas por tenant em tempo real.

---

## 12. API Publica estilo OpenAI

Endpoints alvo:
- `POST /v1/chat`
- `POST /v1/agents`
- `POST /v1/embeddings`

### Requisitos

- API keys por projeto.
- Limites por minuto/dia e por plano.
- Idempotency key para operacoes mutaveis.
- Versionamento de API e changelog contratual.

---

## 13. Orquestrador de IA (`ai_router.py`)

Regra de roteamento:

```text
Pergunta simples  -> modelo local
Pergunta complexa -> LLM premium
Documento         -> RAG
Automacao         -> agente + tools
```

### Criterios de decisao

- custo estimado
- latencia alvo
- risco/compliance
- confianca do classificador de intencao

---

## 14. Upload e Conversa com Arquivos

Suporte:
- PDF, DOC, CSV, imagens

Fluxo:
- upload seguro -> antivirus -> parser -> indexacao -> chat contextual

Controles:
- limite de tamanho por plano
- deduplicacao por hash
- expurgo e retention policy

---

## 15. Mobile (Flutter)

Arquitetura:

```text
Flutter App -> API Gateway -> Core API -> Services
```

Requisitos mobile:
- autenticacao JWT + refresh
- notificacoes push para eventos de agente
- modo offline para rascunhos
- telemetria de crash/performance

---

## 16. Banco de Dados e Particionamento

### Postgres (OLTP)

- Tabelas criticas com `organization_id` indexado.
- Particionamento por tempo em tabelas de alto volume (`messages`, `usage_logs`).
- Read replicas para leitura pesada.

### Redis

- cache de sessao e rate limit.
- locks distribuidos para jobs criticos.

### Vector DB

- Colecoes por tenant grande ou por dominio.
- Namespaces por organizacao para isolamento logico.

---

## 17. Escala de Infra para Milhoes

### Topologia recomendada

- Multi-AZ desde o inicio.
- Multi-regiao ativo-passivo (depois ativo-ativo para APIs criticas).
- Kubernetes com autoscaling por CPU, memoria e fila.
- CDN global para frontend e assets.

### Componentes de confiabilidade

- API Gateway + WAF + DDoS protection.
- Service mesh (mTLS, retries, observabilidade).
- Queue central (Kafka/SQS/RabbitMQ) para workloads assincronos.

---

## 18. SLOs, Observabilidade e Operacao

### SLOs

- Chat API availability: 99.95%
- Webhook processing success: 99.9%
- Billing consistency lag: < 60s

### Observabilidade

- Logs estruturados (JSON) com `request_id`.
- Tracing distribuido (OpenTelemetry).
- Dashboards por dominio (chat, agents, rag, billing).
- Alertas por erro, latencia p95 e backlog de fila.

---

## 19. Seguranca e Compliance

- OAuth2/JWT com rotacao de refresh token.
- Segredos em vault (nunca em codigo).
- Criptografia em transito (TLS) e repouso (KMS).
- RBAC por organizacao e ambiente.
- Auditoria de acoes sensiveis (tools e billing).
- LGPD/GDPR: consentimento, exportacao e delecao de dados.

---

## 20. Plano de Evolucao por Fases

### Fase A (0-3 meses)
- Consolidar core API stateless.
- Agent runtime basico com planner/executor.
- RAG MVP com pgvector.
- Billing e webhook em producao.

### Fase B (3-6 meses)
- Tool sandbox + marketplace beta.
- Integracoes prioritarias (WhatsApp, Slack, Telegram).
- Analytics near real-time.
- Flutter app MVP.

### Fase C (6-12 meses)
- Multi-regiao, DR automatizado.
- Vector DB dedicado (Qdrant/Weaviate cluster).
- Orquestrador de IA com controle de custo por tenant.
- API publica com ecossistema de developers.

---

## 21. Gargalos Esperados e Mitigacoes

- `LLM cost explosion`: roteamento de modelo + cache semantico.
- `Pico em integrações`: filas por canal + autoscaling de workers.
- `Crescimento de embeddings`: tiering de indice e retention inteligente.
- `Latencia de banco`: read replica + particionamento + query budgets.

---

## 22. Decisao Final de Arquitetura

A ALICI deve adotar arquitetura `modular + event-driven + tenant-aware`, com:
- `Core` de agentes autonomos (planner/executor/tools/memory/knowledge).
- `RAG` industrial com pipeline de ingestao e retrieval robusto.
- `Integracoes` como produtos de primeira classe.
- `Billing/API` prontos para escala e monetizacao.
- `Observabilidade e seguranca` desde o inicio.

Esse desenho suporta crescimento para milhoes de usuarios sem quebrar servidor porque remove acoplamento entre entrada web e execucao pesada, escala horizontalmente por dominio e protege os pontos de gargalo com filas, cache, particionamento e operacao orientada por SLO.
