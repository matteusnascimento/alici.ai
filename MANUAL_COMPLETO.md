# 📘 ALICI™ — Manual Completo do Projeto

**Versão**: 2.2 | **Data**: Março 2026 | **Status**: Production-Ready

---

## 📚 Índice

1. [O que é ALICI?](#-o-que-é-alici)
2. [Visão Estratégica](#-visão-estratégica)
3. [Arquitetura Técnica](#-arquitetura-técnica)
4. [Estrutura de Pastas](#-estrutura-de-pastas)
5. [Instalação e Setup](#-instalação-e-setup)
6. [Rodando Localmente](#-rodando-localmente)
7. [Endpoints da API](#-endpoints-da-api)
8. [Autenticação JWT](#-autenticação-jwt)
9. [Dashboard e Frontend](#-dashboard-e-frontend)
10. [Banco de Dados](#-banco-de-dados)
11. [Planos e Monetização](#-planos-e-monetização)
12. [Fluxos de Uso](#-fluxos-de-uso)
13. [Deploy em Produção](#-deploy-em-produção)
14. [Troubleshooting](#-troubleshooting)
15. [Roadmap](#-roadmap)

---

## 🎯 O que é ALICI?

ALICI é uma **plataforma SaaS de Inteligência Artificial** pronta para captação de investimento, oferecendo:

- **Conversational AI**: Motor de IA multimodal com memória persistente
- **Processamento de Imagens**: Análise visual com rede neural
- **Processamento de Áudio**: Suporte a inteligência auditiva
- **Dashboard Premium**: Interface moderna estilo ChatGPT/OpenAI
- **Sistema de Planos**: Free, Pro, Ultra, Enterprise
- **Rate Limiting**: Proteção contra abuso com limites por plano
- **Autenticação JWT**: Sistema de tokens com refresh automático

---

## 💎 Visão Estratégica

ALICI é posicionada como:

> "Infraestrutura proprietária de IA escalável, pronta para monetização SaaS"

### Diferenciadores:

✅ **Multimodal Core** - Texto, imagem, áudio  
✅ **Memória Neural Persistente** - Aprendizado contínuo  
✅ **Arquitetura Enterprise** - Rate limiting, logging estruturado  
✅ **SaaS-Ready** - Planos, billing, autenticação  
✅ **Responsivo** - Funciona em desktop e mobile  

### Público-Alvo:

- Startups que precisam de IA integrada
- Empresas B2B que querem escalar IA
- Desenvolvedores buscando API de IA robusta
- Investidores de tech/IA

---

## 🏗️ Arquitetura Técnica

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (HTML/CSS/JS)                    │
│  Landing | Login | Register | Dashboard | Portfolio          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Python)                         │
│  ┌──────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐   │
│  │  Auth    │  │  Chat   │  │ History │  │  Billing     │   │
│  │  Routes  │  │ Routes  │  │ Routes  │  │  Routes      │   │
│  └──────────┘  └─────────┘  └─────────┘  └──────────────┘   │
│       │             │            │              │             │
│       └─────────────┴────────────┴──────────────┘             │
│                     │                                         │
│         [Middleware: Auth JWT, Rate Limit, CORS]            │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬─────────────┐
        ↓              ↓              ↓             ↓
   ┌────────┐    ┌─────────┐    ┌──────────┐  ┌─────────┐
   │ IA Txt │    │ IA Vis  │    │ Database │  │ Memory  │
   │Engine  │    │Engine   │    │ (Neon)   │  │(ML)     │
   └────────┘    └─────────┘    └──────────┘  └─────────┘
```

### Stack:

| Camada | Tecnologia |
|--------|------------|
| **Frontend** | HTML5, CSS3, JavaScript, Three.js |
| **Backend** | Python, FastAPI, Uvicorn |
| **BD** | PostgreSQL (Neon) / SQLite (dev) |
| **Auth** | JWT (access + refresh tokens) |
| **Deploy** | Render.com, Railway, Heroku |
| **ML** | TensorFlow, HuggingFace |

---

## 📂 Estrutura de Pastas

```
alici.ai/
├── alici_api/                    # Backend FastAPI
│   ├── app.py                   # Fábrica da aplicação
│   ├── config.py                # Configurações
│   ├── dependencies.py          # Injeção de dependências
│   ├── responses.py             # Padrão de resposta
│   ├── schemas.py               # DTOs (Request/Response)
│   ├── routes/                  # Rotas da API
│   │   ├── auth.py              # /auth/* (login, register)
│   │   ├── chat.py              # /chat/* (conversas)
│   │   ├── history.py           # /history/* (histórico)
│   │   ├── billing.py           # /billing/* (planos)
│   │   ├── health.py            # /health (status)
│   │   ├── media.py             # /media/* (upload)
│   │   └── pages.py             # / (páginas HTML)
│   ├── services/                # Lógica de negócio
│   │   ├── ai.py                # Motor IA (text/image/audio)
│   │   ├── auth_service.py      # Serviço de autenticação
│   │   ├── media_service.py     # Processamento de mídia
│   │   └── text_model_*.py      # Modelos de texto
│   ├── repositories/            # Acesso a dados
│   │   ├── user_repository.py
│   │   ├── history_repository.py
│   │   └── refresh_token_repository.py
│   └── middleware/              # Middleware customizado
│       ├── rate_limit.py        # Rate limiting
│       └── request_id.py        # Request ID
├── static/                       # Arquivos estáticos
│   ├── css/
│   │   ├── global.css           # Design system
│   │   ├── landing.css
│   │   ├── dashboard.css
│   │   └── portfolio.css
│   ├── js/
│   │   ├── three-background.js  # Animações 3D
│   │   ├── landing.js
│   │   ├── dashboard.js         # Integração API
│   │   └── portfolio.js
│   └── assets/
│       ├── logo.svg
│       └── hero-visual.png
├── templates/                    # HTML Jinja2
│   ├── landing.html             # /
│   ├── login.html               # /login
│   ├── register.html            # /register
│   ├── dashboard.html           # /dashboard
│   ├── portfolio.html           # /portfolio
│   └── chat.html                # Legado (deprecado)
├── artifacts/                    # Modelos ML treinados
│   └── alici_cpu_simple/
│       ├── alici_cpu_simple.keras
│       └── metadata.json
├── logs/                         # Logs de execução
├── database.py                   # Funções de BD
├── auth.py                       # Funções de autenticação
├── engine.py                     # Motor de IA
├── resposta.py                   # Geração de respostas
├── main.py                       # Entrypoint ASGI
├── requirements.txt              # Dependências Python
├── Procfile                      # Deploy (Render)
├── runtime.txt                   # Versão Python
├── .env.example                  # Variáveis de ambiente
├── README.md                     # Documentação rápida
└── MANUAL_COMPLETO.md           # Este arquivo
```

---

## ⚙️ Instalação e Setup

### Pré-requisitos

- Python 3.10+
- pip ou Poetry
- PostgreSQL/Neon (opcional; SQLite em dev)
- Git

### 1️⃣ Clone o Repositório

```bash
git clone https://github.com/matteusnascimento/alici.ai.git
cd alici.ai
```

### 2️⃣ Crie Ambiente Virtual

```bash
python -m venv env
source env/bin/activate  # macOS/Linux
# ou
env\Scripts\activate     # Windows
```

### 3️⃣ Instale Dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Variáveis de Ambiente

Crie um arquivo `.env` na raiz:

```env
# Segurança
SECRET_KEY=sua-chave-super-secreta-aqui
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_MINUTES=10080

# Ambiente
ENV=development
PORT=8000

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Rate Limit
RATE_LIMIT_ENABLED=true
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_MAX_REQUESTS=60

# Banco de Dados (opcional)
DATABASE_URL=postgresql://user:pass@localhost/alici_db
USE_SQLITE=true  # ou false para PostgreSQL

# HuggingFace (IA textual)
ALICI_HF_REPO_ID=Matteusnascimento/alici.ai
HUGGINGFACE_TOKEN=seu-token-aqui

# Stripe (opcional)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...

# R2 / CloudFlare (opcional)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

---

## 🚀 Rodando Localmente

### Iniciar o Servidor

```bash
# Modo desenvolvimento (com reload)
uvicorn alici_api.app:app --reload

# Sua aplicação estará em: http://127.0.0.1:8000
```

### Acessar as Páginas

| Página | URL |
|--------|-----|
| **Landing** | http://127.0.0.1:8000/ |
| **Login** | http://127.0.0.1:8000/login |
| **Register** | http://127.0.0.1:8000/register |
| **Dashboard** | http://127.0.0.1:8000/dashboard |
| **Portfolio** | http://127.0.0.1:8000/portfolio |
| **Docs API** | http://127.0.0.1:8000/docs |
| **Health Check** | http://127.0.0.1:8000/health |

### Testar a API com cURL

```bash
# 1. Registrar novo usuário
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"nome":"João","email":"joao@example.com","senha":"senha123"}'

# 2. Fazer login
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"joao@example.com","senha":"senha123"}'

# 3. Salvar o access_token retornado e usar:
TOKEN="eyJhbGci..."
curl -X POST http://127.0.0.1:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"pergunta":"Qual é a capital da França?"}'

# 4. Ver histórico
curl -X GET "http://127.0.0.1:8000/history?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔌 Endpoints da API

### 🔐 Autenticação (`/auth`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/auth/register` | Criar nova conta |
| POST | `/auth/login` | Fazer login (retorna tokens) |
| POST | `/auth/refresh` | Renovar access token |
| POST | `/auth/logout` | Logout (revoga refresh token) |

**Login Request:**
```json
{
  "email": "usuario@example.com",
  "senha": "senha123"
}
```

**Login Response:**
```json
{
  "status": "sucesso",
  "code": "OK-AUTH-LOGIN-200",
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "usuario": {
    "id": 1,
    "nome": "João",
    "email": "joao@example.com",
    "plano": "free"
  }
}
```

---

### 💬 Chat (`/chat`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/chat` | Enviar mensagem | ✅ |
| POST | `/chat/image` | Analisar imagem | ✅ |

**Chat Request:**
```json
{
  "pergunta": "Qual é a capital da França?",
  "incluir_emocao": false
}
```

**Chat Response:**
```json
{
  "status": "sucesso",
  "code": "OK-CHAT-REPLY-200",
  "resposta": "A capital da França é Paris.",
  "usuario": "João",
  "plano": "free",
  "limite_diario": 20,
  "mensagens_hoje": 1
}
```

**Rate Limiting por Plano:**
| Plano | Requisições/min | Mensagens/dia |
|-------|-----------------|---------------|
| Free | 20 | 20 |
| Pro | 120 | 300 |
| Ultra | 300 | 2000 |
| Enterprise | Ilimitado | Ilimitado |

---

### 📜 Histórico (`/history`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/history` | Ver histórico | ✅ |
| DELETE | `/history` | Limpar histórico | ✅ |

**Query Parameters:**
- `limit` (int, default=50): Máximo 200 mensagens

**Response:**
```json
{
  "status": "sucesso",
  "code": "OK-HISTORY-LIST-200",
  "total": 5,
  "historico": [
    {
      "pergunta": "Qual é a capital da França?",
      "resposta": "A capital da França é Paris.",
      "criado_em": "2026-03-04T10:00:00"
    }
  ]
}
```

---

### 💳 Billing (`/billing`)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/billing/plans` | Listar planos | ✅ |
| POST | `/billing/create-checkout` | Criar checkout Stripe | ✅ |

**Plans Response:**
```json
{
  "status": "sucesso",
  "plans": {
    "free": {"name": "Free", "price_brl": 0},
    "pro": {"name": "Pro", "price_brl": 49},
    "ultra": {"name": "Ultra", "price_brl": 99},
    "enterprise": {"name": "Enterprise", "price_brl": null}
  },
  "current_plan": "free"
}
```

---

### 🏥 Health Check

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Status do sistema |

**Response:**
```json
{
  "status": "sucesso",
  "code": "OK-HEALTH-200",
  "ia_disponivel": true,
  "visao_disponivel": false,
  "modelo_texto_r2": {"disponivel": false},
  "timestamp": "2026-03-04T10:00:00"
}
```

---

## 🔐 Autenticação JWT

### Fluxo de Autenticação

```
1. Usuário faz login
   ↓
2. Servidor retorna: access_token (curto, 60 min) + refresh_token (longo, 7 dias)
   ↓
3. Frontend armazena em localStorage
   ↓
4. Usa access_token no header: Authorization: Bearer <token>
   ↓
5. Quando access_token expira, usa refresh_token para renovar
```

### Headers de Autenticação

```js
// JavaScript
const token = localStorage.getItem('access_token');
const response = await fetch('/chat', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ pergunta: 'Olá!' })
});
```

### Token Refresh

Quando o access_token expirar (401 Unauthorized):

```bash
curl -X POST http://127.0.0.1:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"eyJhbGci..."}'
```

---

## 📊 Dashboard e Frontend

### Fluxo de Uso

```
1. Acessar http://127.0.0.1:8000/login
2. Registrar ou fazer login
3. Redirecionado para /dashboard
4. Dashboard carrega histórico via GET /history
5. Usuário digita mensagem
6. dashboard.js envia POST /chat com token
7. API processa via engine.py
8. Resposta aparece no chat
9. Mensagem é salva no DB automaticamente
```

### Componentes do Dashboard

| Componente | Arquivo | Função |
|------------|---------|--------|
| **Sidebar** | dashboard.html | Menu lateral (Nova Conversa, Sair) |
| **Chat Area** | dashboard.html | Histórico + input |
| **Messages** | dashboard.js | Renderiza mensagens (user/assistant) |
| **API Handler** | dashboard.js | Chamadas `/chat`, `/history`, `/auth/logout` |
| **Auth Check** | dashboard.js | Valida token, redireciona se não autenticado |

### Tecnologias Frontend

- **HTML5**: Semântica
- **CSS3**: Grid, Flexbox, Glassmorphism
- **JavaScript**: Vanilla JS com Fetch API
- **Three.js**: Animações 3D na landing
- **Chart.js**: Gráficos (utilizado em analytics)

---

## 🗄️ Banco de Dados

### Tabelas Principais

```sql
-- Usuários
CREATE TABLE users (
  id INT PRIMARY KEY,
  nome TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  senha_hash TEXT NOT NULL,
  plano TEXT DEFAULT 'free',
  mensagens_hoje INT DEFAULT 0,
  criado_em TIMESTAMP
);

-- Histórico de chat
CREATE TABLE history (
  id INT PRIMARY KEY,
  user_id INT NOT NULL,
  pergunta TEXT NOT NULL,
  resposta TEXT NOT NULL,
  criado_em TIMESTAMP
);

-- Memória/Aprendizado
CREATE TABLE memoria (
  id INT PRIMARY KEY,
  pergunta TEXT NOT NULL,
  resposta TEXT NOT NULL,
  confianca INT DEFAULT 1,
  criado_em TIMESTAMP
);

-- Refresh tokens
CREATE TABLE refresh_tokens (
  id INT PRIMARY KEY,
  user_id INT NOT NULL,
  jti TEXT UNIQUE NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  revoked BOOLEAN DEFAULT false,
  criado_em TIMESTAMP
);

-- Subscriptions/Billing
CREATE TABLE subscriptions (
  id INT PRIMARY KEY,
  user_id INT NOT NULL,
  stripe_id TEXT,
  status TEXT,
  plano TEXT,
  renovacao TIMESTAMP,
  criado_em TIMESTAMP
);
```

### Migrações

```bash
# Criar tabelas
python -c "from database import criar_tabelas; criar_tabelas()"

# Limpar DB (apenas em dev)
python -c "from database import limpar_bd; limpar_bd()"
```

### Conexão

```python
# SQLite (desenvolvimento)
DATABASE_URL = "sqlite:///alici.db"

# PostgreSQL (produção)
DATABASE_URL = "postgresql://user:pass@host/alici_db"
```

---

## 💰 Planos e Monetização

### Estrutura de Planos

| Plano | Mensagens/dia | Req/min | Preço/mês | Recurso |
|-------|---------------|---------|-----------|---------|
| **Free** | 20 | 20 | R$0 | Trial |
| **Pro** | 300 | 120 | R$49 | Produtivo |
| **Ultra** | 2.000 | 300 | R$99 | Enterprise |
| **Enterprise** | Ilimitado | Ilimitado | Custom | Dedicated |

### Implementação

```python
# Em alici_api/routes/billing.py
PLAN_CATALOG = {
    "free": {"name": "Free", "price_brl": 0},
    "pro": {"name": "Pro", "price_brl": 49},
    "ultra": {"name": "Ultra", "price_brl": 99},
    "enterprise": {"name": "Enterprise", "price_brl": None},
}
```

### Integração Stripe (TODO)

```bash
# Setup Stripe
export STRIPE_SECRET_KEY=sk_test_...
export STRIPE_PUBLIC_KEY=pk_test_...

# Webhook: POST /billing/stripe-webhook
```

---

## 🔄 Fluxos de Uso

### Fluxo 1: Novo Usuário

```
1. Acessa landing.html (/)
2. Clica "Start Now"
3. Redireciona para /register
4. Preenche: nome, email, senha
5. POST /auth/register
6. Se sucesso → redireciona para /login
7. Faz login → recebe tokens
8. Redireciona para /dashboard
9. Dashboard carrega histórico vazio
10. Usa o chat
```

### Fluxo 2: Usuário Existente

```
1. Acessa /login
2. Email + senha
3. POST /auth/login
4. Recebe access_token + refresh_token
5. localStorage.setItem('access_token', ...)
6. Redireciona para /dashboard
7. Dashboard fetch /history (com token)
8. Histórico carrega
9. Chat pronto de novo
```

### Fluxo 3: Enviar Mensagem

```
1. Usuário digita no input
2. Clica "Enviar" ou Enter
3. dashboard.js pega texto
4. Adiciona mensagem do usuário à UI
5. POST /chat { pergunta }
6. Middleware valida token
7. Rate limit verifica limite/minuto
8. Daily limit verifica limite/dia
9. engine.py gera resposta
10. Historia salva no DB
11. Response envia resposta
12. Dashboard renderiza resposta
```

### Fluxo 4: Logout

```
1. Usuário clica "Logout"
2. POST /auth/logout (com token)
3. Revoga refresh_token no DB
4. localStorage.clear()
5. Redireciona para /login
```

---

## 🌐 Deploy em Produção

### Deploy em Render.com

```bash
# 1. Conectar repositório GitHub no Render

# 2. Configurações no Render:
Service Type: Web Service
Build Command: pip install -r requirements.txt
Start Command: uvicorn alici_api.app:app --host 0.0.0.0 --port $PORT

# 3. Variáveis de Ambiente:
SECRET_KEY=<gerar-novo>
ENV=production
DATABASE_URL=<postgresql://...>
CORS_ALLOWED_ORIGINS=https://seu-dominio.com
STRIPE_SECRET_KEY=sk_live_...
```

### Deploy em Railway.app

```bash
# 1. Login: railway login
# 2. Init: railway init
# 3. Deploy: railway up
# 4. Configurar variáveis via UI
```

### Deploy com Docker

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "alici_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t alici .
docker run -e DATABASE_URL=... -p 8000:8000 alici
```

---

## 🔧 Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'alici_api'"

**Solução:**
```bash
# Certifique-se que está na raiz do projeto
cd alici.ai

# Reinstale dependências
pip install -r requirements.txt

# Rode com python -m
python -m uvicorn alici_api.app:app --reload
```

---

### Problema: "DATABASE_URL not configured"

**Solução:**
```bash
# Adicione ao .env
DATABASE_URL=sqlite:///alici.db

# Ou para PostgreSQL:
DATABASE_URL=postgresql://user:pass@localhost:5432/alici_db
```

---

### Problema: "Token inválido" ao tentar acessar /chat

**Solução:**
```js
// Certifique-se que o token está correto
const token = localStorage.getItem('access_token');
console.log('Token:', token);

// Se vazio, faça login de novo
// Se expirou, use refresh_token
```

---

### Problema: Rate limit atingido

**Solução:**
```bash
# Espere 1 minuto, ou
# Atualize seu plano para aumentar o limite
```

---

## 🚀 Roadmap

### Q1 2026 (Março - Maio)

- ✅ MVP com dashboard funcional
- ✅ Autenticação JWT completa
- ✅ Rate limiting por plano
- 🔄 Integração Stripe (em progresso)
- 📅 Admin dashboard

### Q2 2026 (Junho - Agosto)

- Monetização ao vivo
- API pública (chaves de API)
- Webhooks
- Analytics real-time
- Mobile app (React Native)

### Q3 2026 (Setembro - Novembro)

- Enterprise SLA
- Single Sign-On (SSO)
- Custom branding
- Dedicated support

### Q4 2026 (Dezembro)

- IA multilingue
- Modelos customizáveis
- Marketplace de plugins

---

## 🤝 Contribuindo

```bash
# 1. Fork o repositório
# 2. Crie branch: git checkout -b feature/sua-feature
# 3. Commit: git commit -m "Add sua feature"
# 4. Push: git push origin feature/sua-feature
# 5. Abra PR
```

---

## 📞 Suporte

- **Issues**: https://github.com/matteusnascimento/alici.ai/issues
- **Email**: mateus@example.com
- **Discord**: [Link do servidor]

---

## 📄 Licença

MIT License — Veja LICENSE.md

---

## 🎓 Recursos Adicionais

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [JWT Auth](https://auth0.com/learn/json-web-tokens)
- [Three.js Documentation](https://threejs.org/docs/)
- [PostgreSQL Guide](https://www.postgresql.org/docs/)

---

**Desenvolvido por**: Mateus Nascimento  
**Última atualização**: 4 de março de 2026

---

*ALICI™ é uma marca registrada. Este manual é propriedade da alici.ai e é fornecido como está.*
