# AXI Platform

Plataforma SaaS com chat inteligente, agentes, marketing e métricas. Backend em FastAPI, frontend em React + Vite + TypeScript, pronta para deploy no Render.

> **Nota:** A camada de IA real (OpenAI) será conectada em uma fase futura. Atualmente o chat opera com respostas de fallback.

---

## Stack

| Camada    | Tecnologia                               |
|-----------|------------------------------------------|
| Backend   | Python 3.12 · FastAPI · SQLAlchemy 2.x   |
| Frontend  | React 18 · Vite · TypeScript · Tailwind  |
| Banco     | SQLite (dev) · PostgreSQL (produção)     |
| Migrações | Alembic                                  |
| Auth      | JWT (PyJWT) + bcrypt (passlib)           |

---

## Estrutura de pastas

```
alici.ai/
├── backend/
│   ├── alembic/          # Configuração e versões de migração
│   ├── app/
│   │   ├── api/routes/   # Endpoints FastAPI
│   │   ├── core/         # Config, segurança, banco de dados
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── schemas/      # Schemas Pydantic
│   │   ├── services/     # Lógica de negócio
│   │   └── main.py       # Ponto de entrada da API
│   ├── .env.example      # Exemplo de variáveis de ambiente
│   ├── alembic.ini       # Configuração do Alembic
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/   # Componentes React
│       ├── hooks/        # React hooks
│       ├── router/       # Definição de rotas
│       ├── services/     # Chamadas de API
│       ├── types/        # Tipos TypeScript
│       └── main.tsx      # Ponto de entrada do frontend
└── tests/
    ├── backend/          # Testes pytest
    └── frontend/         # Testes Vitest
```

---

## Rodando em desenvolvimento

### Backend

```bash
cd backend

# Copiar e ajustar variáveis de ambiente
cp .env.example .env

# Instalar dependências
pip install -r requirements.txt

# Subir o servidor (porta 8000)
uvicorn app.main:app --reload
```

A API ficará disponível em `http://localhost:8000`.  
Documentação interativa: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Subir o servidor de desenvolvimento (porta 5173)
npm run dev
```

O frontend ficará disponível em `http://localhost:5173`.

---

## Variáveis de ambiente (backend)

Copie `backend/.env.example` para `backend/.env` e preencha:

| Variável                     | Descrição                                     | Padrão (dev)              |
|------------------------------|-----------------------------------------------|---------------------------|
| `APP_ENV`                    | Ambiente (`development` / `production`)       | `development`             |
| `DEBUG`                      | Ativa modo debug (forçado `false` em prod)    | `true`                    |
| `DATABASE_URL`               | URL de conexão com o banco                    | `sqlite:///./axi.db`      |
| `SECRET_KEY`                 | Chave JWT — use uma chave forte em produção   | `troque-esta-chave-...`   |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| Expiração do token de acesso (minutos)        | `1440` (24 h)             |
| `CORS_ALLOWED_ORIGINS`       | Origens permitidas no CORS (vírgula)          | `http://localhost:5173`   |
| `DEFAULT_AI_PROVIDER`        | Provider de IA padrão do backend              | `openai`                  |
| `OPENAI_API_KEY`             | Chave da API OpenAI lida apenas no backend    | _(vazio)_                 |
| `OPENAI_MODEL`               | Modelo OpenAI padrão                          | `gpt-4o-mini`             |

---

## Rodando os testes

### Backend (pytest)

```bash
cd backend
pip install -r requirements.txt
pytest ../tests/backend/ -v
```

### Frontend (Vitest)

```bash
cd frontend
npm install
npm test
```

---

## Migrações com Alembic

```bash
cd backend

# Gerar nova migração (detecta mudanças nos models)
alembic revision --autogenerate -m "descricao da migracao"

# Aplicar migrações pendentes
alembic upgrade head

# Ver histórico de migrações
alembic history
```

---

## Deploy no Render

### Backend (Web Service)

1. Crie um **Web Service** apontando para o diretório `backend/`
2. **Build Command:** `pip install -r requirements.txt && alembic upgrade head`
3. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Configure as variáveis de ambiente no painel do Render:
   - `APP_ENV=production`
   - `DATABASE_URL=<sua-url-postgresql>`
   - `SECRET_KEY=<chave-forte-gerada>`
   - `CORS_ALLOWED_ORIGINS=<url-do-frontend>`

### Frontend (Static Site)

1. Crie um **Static Site** apontando para o diretório `frontend/`
2. **Build Command:** `npm install && npm run build`
3. **Publish Directory:** `dist`
4. Configure a variável de ambiente:
   - `VITE_API_URL=<url-do-backend>/api`

### PostgreSQL

1. Crie um banco **PostgreSQL** no Render
2. Copie a **Internal Database URL** para a variável `DATABASE_URL` do backend

---

## Planos disponíveis

| Plano    | Preço/mês |
|----------|-----------|
| free     | R$ 0      |
| pro      | R$ 97     |
| business | R$ 297    |

Novos usuários são criados automaticamente no plano **free**.  
A mudança de plano é feita exclusivamente pela seção de **Assinatura**, nunca pelo formulário de perfil.

---

## Pendências futuras (fora do escopo atual)

- [ ] Conectar provedor real de IA (OpenAI) no `chat_service.py`
- [ ] Implementar integrações reais de WhatsApp e Instagram
- [ ] Cobrança real via gateway de pagamento (Stripe / Pagar.me)
- [ ] Refresh token e fluxo de renovação de sessão
- [ ] CI/CD com testes automáticos no GitHub Actions
