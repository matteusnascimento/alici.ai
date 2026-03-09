# ALICI Platform – Checklist de Rotas e Templates HTML

> Última verificação: 2026-03-09

---

## Templates HTML (`frontend/templates/`)

| Template | Rota | Status |
|---|---|---|
| `landing.html` | `GET /` | ✅ Mapeado |
| `chat.html` | `GET /chat` | ✅ Mapeado |
| `platform.html` | `GET /platform` | ✅ Mapeado |
| `dashboard.html` | `GET /dashboard` | ✅ Mapeado |
| `agents.html` | `GET /agents` | ✅ Mapeado |
| `create_agent.html` | `GET /agents/create` | ✅ Mapeado |
| `integrations.html` | `GET /integrations` | ✅ Mapeado |
| `settings.html` | `GET /settings` | ✅ Mapeado |
| `login.html` | `GET /login` | ✅ Mapeado |
| `register.html` | `GET /register` | ✅ Mapeado |
| `portfolio.html` | `GET /portfolio` | ✅ Mapeado |
| `quantum.html` | `GET /quantum` | ✅ Mapeado |
| `index.html` | `GET /index` | ✅ Mapeado |

---

## Rotas de Frontend (`main.py`)

| Rota | Método | Template | Descrição |
|---|---|---|---|
| `/` | GET | `landing.html` | Landing page principal |
| `/chat` | GET | `chat.html` | Interface de chat |
| `/chat` | POST | — | Endpoint legado de compatibilidade |
| `/platform` | GET | `platform.html` | Dashboard da plataforma |
| `/dashboard` | GET | `dashboard.html` | Dashboard alternativo |
| `/agents` | GET | `agents.html` | Vitrine e gestão de agentes |
| `/agents/create` | GET | `create_agent.html` | Formulário de criação de agente |
| `/integrations` | GET | `integrations.html` | Catálogo de integrações |
| `/settings` | GET | `settings.html` | Hub de configurações do usuário |
| `/login` | GET | `login.html` | Página de login |
| `/register` | GET | `register.html` | Página de cadastro |
| `/portfolio` | GET | `portfolio.html` | Portfolio do fundador |
| `/quantum` | GET | `quantum.html` | Página de funcionalidades Quantum |
| `/index` | GET | `index.html` | Shell legado da plataforma |
| `/health` | GET | — | Health check (JSON) |
| `/healthz` | GET | — | Health check para Kubernetes (JSON) |

---

## Rotas de API (`/api/` e `/v1/`)

### Autenticação — `/api/auth/`
- [ ] `POST /api/auth/register` — Registro de novo usuário
- [ ] `POST /api/auth/login` — Login e emissão de token
- [ ] `POST /api/auth/refresh` — Renovação do token de acesso
- [ ] `POST /api/auth/logout` — Encerramento de sessão

### Chat — `/api/chat/`
- [ ] `POST /api/chat/` — Envio de mensagem (streaming e não-streaming)

### Conversas — `/api/conversations/`
- [ ] `GET /api/conversations/` — Listar conversas (paginado)
- [ ] `POST /api/conversations/` — Criar conversa
- [ ] `GET /api/conversations/{id}` — Detalhes de uma conversa
- [ ] `GET /api/conversations/{id}/messages` — Mensagens de uma conversa
- [ ] `DELETE /api/conversations/{id}` — Remover conversa

### Usuários — `/api/user/`
- [ ] `GET /api/user/profile` — Obter perfil do usuário
- [ ] `PUT /api/user/update` — Atualizar perfil
- [ ] `POST /api/user/avatar` — Enviar avatar

### Agentes — `/api/agents/`
- [ ] `GET /api/agents/` — Listar agentes
- [ ] `POST /api/agents/` — Criar agente
- [ ] `GET /api/agents/{agent_id}` — Detalhes de um agente
- [ ] `PUT /api/agents/{agent_id}` — Atualizar agente
- [ ] `DELETE /api/agents/{agent_id}` — Remover agente

### Faturamento — `/api/billing/`
- [ ] `GET /api/billing/plans` — Listar planos
- [ ] `GET /api/billing/subscription` — Assinatura atual
- [ ] `POST /api/billing/checkout` — Iniciar checkout
- [ ] `POST /api/billing/subscription/confirm` — Confirmar assinatura
- [ ] `POST /api/billing/subscription/cancel` — Cancelar assinatura
- [ ] `POST /api/billing/webhook` — Webhook do Stripe

### Integrações — `/api/integrations/`
- [ ] `GET /api/integrations/` — Listar integrações
- [ ] `POST /api/integrations/` — Criar integração
- [ ] `DELETE /api/integrations/{integration_type}` — Remover integração

### Base de Conhecimento — `/api/knowledge/`
- [ ] `POST /api/knowledge/upload` — Enviar documentos
- [ ] `POST /api/knowledge/query` — Consultar base de conhecimento
- [ ] `GET /api/knowledge/` — Listar documentos
- [ ] `DELETE /api/knowledge/{document_id}` — Remover documento

### Analytics — `/api/analytics/`
- [ ] `GET /api/analytics/` — Dados de analytics

### Workflows — `/api/workflows/`
- [ ] `GET /api/workflows/` — Listar workflows

### Plataforma — `/api/platform/`
- [ ] `GET /api/platform/overview` — Visão geral da plataforma
- [ ] `GET /api/platform/stats` — Estatísticas da plataforma
- [ ] `GET /api/platform/api-keys` — Listar chaves de API
- [ ] `POST /api/platform/api-keys` — Criar chave de API
- [ ] `DELETE /api/platform/api-keys/{key_id}` — Remover chave de API

### Configurações — `/api/settings/`
- [ ] `GET /api/settings/theme` — Tema atual
- [ ] `PUT /api/settings/theme` — Atualizar tema
- [ ] `GET /api/settings/notifications` — Configurações de notificações
- [ ] `PUT /api/settings/notifications` — Atualizar notificações
- [ ] `GET /api/settings/ai` — Configurações de IA
- [ ] `PUT /api/settings/ai` — Atualizar configurações de IA

### Arquitetura de IA — `/api/ai/`
- [ ] `GET /api/ai/architecture` — Informações da arquitetura de IA
- [ ] `POST /api/ai/model-router/provider` — Configurar model router
- [ ] `POST /api/ai/vector-store/provider` — Configurar vector store

### API Pública (compatível com OpenAI) — `/v1/`
- [ ] `POST /v1/chat/completions` — Chat completions
- [ ] `GET /v1/models` — Listar modelos disponíveis
- [ ] `GET /v1/models/{model}` — Detalhes de um modelo

---

## Health Checks

| Rota | Uso | Status |
|---|---|---|
| `GET /health` | Geral / uptime monitoring | ✅ |
| `GET /healthz` | Kubernetes / Docker liveness probe | ✅ |
