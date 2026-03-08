# Roadmap Tecnico de 90 Dias - ALICI

## Objetivo
Executar a arquitetura de escala da ALICI em 6 sprints de 2 semanas com entregas incrementais e validacao por SLO.

## Metas dos 90 dias
- Core de agentes em producao (planner, executor, tools, memory, knowledge).
- RAG operacional para clientes enterprise.
- Integracoes principais com webhooks robustos.
- Billing e API publica com governanca de quota.
- Observabilidade completa para operacao 24x7.

---

## Sprint 1 (Semanas 1-2) - Fundacao de Escala

### Epico A: Plataforma e Infra
- Provisionar base `infra/terraform` em ambiente de staging.
- Subir cluster K8s e deploy inicial de API e workers.
- Configurar secrets, policies de rede e autoscaling baseline.

### Epico B: Governanca Tecnica
- Definir padrao de logs estruturados e request_id.
- Ativar tracing distribuido (OpenTelemetry).
- Definir SLOs e alertas iniciais.

### Criterios de aceite
- Deploy repetivel via IaC.
- API escalando horizontalmente com HPA.
- Dashboards de latencia/erro ativos.

---

## Sprint 2 (Semanas 3-4) - Core de Agentes v1

### Epico C: Agent Runtime
- Implementar runtime `Agent -> Planner -> Executor -> Tool Runtime`.
- Criar estado de execucao por `run_id` com idempotencia.
- Definir policies de timeout/retry por etapa.

### Epico D: Criacao e Publicacao de Agentes
- Fluxo backend para `criar/configurar/publicar`.
- Versao inicial de templates: atendimento, vendas, marketing, suporte.

### Criterios de aceite
- Agente executa workflow de multiplos passos sem travar API.
- Falhas de ferramenta nao derrubam run completo.

---

## Sprint 3 (Semanas 5-6) - Memoria Inteligente + RAG MVP

### Epico E: Memoria
- Memoria curta em Redis com TTL e sumarizacao.
- Memoria longa em Postgres + embeddings vetoriais.
- Recuperacao por recencia + similaridade.

### Epico F: Ingestao de conhecimento
- Pipeline upload -> parser -> chunk -> embedding -> index.
- Suporte inicial: PDF, DOCX, TXT, FAQ.

### Criterios de aceite
- Resposta contextual com memoria relevante.
- Documento enviado impacta respostas em menos de 2 min.

---

## Sprint 4 (Semanas 7-8) - Integracoes e Tools de Producao

### Epico G: Tooling
- Ferramentas oficiais: `web_search`, `http_request`, `email_sender`, `database_query`.
- Contratos de input/output e auditoria de execucao.

### Epico H: Hub de Integracoes
- Conectores prioritarios: WhatsApp, Slack, Telegram.
- Webhook ingress com normalizacao de eventos.

### Criterios de aceite
- Eventos externos processados por fila com retry exponencial.
- Tool executions auditaveis por tenant.

---

## Sprint 5 (Semanas 9-10) - Billing + API Publica

### Epico I: Monetizacao
- Consolidar fluxo Stripe e webhooks de assinatura.
- Enforcement de quotas por plano (Free/Pro/Business/Enterprise).

### Epico J: API Publica
- Endpoints v1: `/v1/chat`, `/v1/agents`, `/v1/embeddings`.
- API keys por projeto e rate limits por plano.

### Criterios de aceite
- Bloqueio de uso acima da quota em tempo real.
- Contratos v1 publicados com changelog.

---

## Sprint 6 (Semanas 11-12) - Operacao de Escala + Marketplace Beta

### Epico K: Confiabilidade
- Teste de carga para 10x trafego atual.
- Ajuste de particionamento e replicas de leitura.
- DR runbook e exercicio de recuperacao.

### Epico L: Marketplace de Agentes (Beta)
- Publicacao e instalacao de templates.
- Versionamento semantico e controles de permissao.

### Criterios de aceite
- Ambiente passa em teste de resiliencia sem downtime.
- Marketplace beta funcional para clientes piloto.

---

## Backlog transversal (todos os sprints)
- Seguranca: RBAC, secrets vault, auditoria.
- Qualidade: suites E2E e testes de contrato.
- Custos: dashboards por tenant e otimização de modelo.
- Produto: telemetria de funil e feedback de usuarios.

---

## KPI tecnico por trilha
- Disponibilidade API >= 99.95%
- p95 chat <= 1.5s (sem tool externa)
- Erro de webhook <= 0.1%
- Sucesso de jobs assincronos >= 99.5%
- Custo medio por 1k mensagens reduzido sprint a sprint

---

## Anexo de Hardening
- Checklist operacional de seguranca e producao: `HARDENING_CHECKLIST_PRODUCAO.md`
