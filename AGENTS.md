# AGENTS.md — alici.ai

Plataforma SaaS (AXI Platform) com chat inteligente, agentes de IA, dashboard e billing.  
**Backend**: FastAPI (Python 3.12) · **Frontend**: React 18 + Vite + TypeScript · **DB**: SQLite (dev) / PostgreSQL (prod via Neon) · **Deploy**: Render

---

## Comandos essenciais

### Backend
```bash
# A partir da raiz do projeto
cd backend

uvicorn app.main:app --reload         # Dev (porta 8000)
python -m pytest tests/backend/ -x    # Testes (pode ser lento; ~5-6 min para test_studio_module)

# Migrações
alembic upgrade head                  # Aplicar migrações
alembic revision --autogenerate -m "descrição"  # Gerar nova migração
```

### Frontend
```bash
cd frontend

npm run dev          # Dev (porta 5173)
npm run build        # Build prod (tsc + vite build)
npm run typecheck    # Verificar tipagem (tsc --noEmit)
npm run test         # Vitest — NÃO use flag -q
```

---

## Estrutura de pastas

```
backend/app/
├── api/routes/      # Endpoints FastAPI
├── core/            # Config (config.py), DB (database.py), JWT (security.py)
├── models/          # SQLAlchemy 2.0 models (Mapped/mapped_column)
├── schemas/         # Pydantic DTOs (*Create, *Read, *Update, *Response)
├── services/        # Lógica de negócio (*_service.py)
└── integrations/    # Serviços externos (OpenAI, Stripe, etc.)

frontend/src/
├── services/        # api.ts (base), *.service.ts (por domínio)
├── types/           # Interfaces TypeScript por domínio
├── components/      # Componentes React (agents/v2/ é o padrão atual)
├── hooks/           # Custom React hooks
└── router/          # Configuração de rotas
```

---

## Padrões obrigatórios

### Backend — Camada de serviço
- Classe `XxxService(db: Session)`; métodos privados de validação prefixados com `_` (ex: `_agent_or_404`)
- Erros via `HTTPException(status_code=..., detail="...")`
- DB: `db.query()`, `db.add()`, `db.commit()`, `db.refresh()`

### Backend — Rotas
- `router = APIRouter(prefix="/resource", tags=["resource"])`
- Sempre especificar `response_model=`; serializar com `XxxRead.model_validate(obj)`
- Dependências: `Depends(get_current_user)`, `Depends(get_db)`

### Backend — Modelos
- SQLAlchemy 2.0: `Mapped[T]` / `mapped_column`
- Timestamps com `timezone=True`, `server_default=func.now()`, `onupdate=func.now()`
- FK com `ondelete="CASCADE"`; relações com `back_populates` e `cascade="all, delete-orphan"`

### Frontend — Serviços de API
- Sempre usar `apiFetch<T>()` de `services/api.ts`
- Token em `localStorage` com chave `axi_token`
- `VITE_API_URL` ou fallback `/api`

### Frontend — Componentes
- Componentes funcionais: estado → render → callbacks
- Loading com booleano; erro com `string | null`; captura com `ApiError`
- Tailwind: cores primárias `cyan`, erro `rose`, neutro `slate`

### Convenção de nomes
- Campos de model/schema em **português**: `nome`, `funcao`, `tipo`, `ativo`
- Serviços frontend: `verboDominio()` — `listAgents()`, `createAgent()`

---

## Resposta da API — envelope padrão

```json
{ "status": "success", "data": { ... }, "error": null }
```

A rota `/api/chat/responses` também expõe `output_text` diretamente. **Não anexar logs de tool calls ao campo `output_text`** — isso quebra contrato com frontend e testes.

---

## Autenticação e canais de agentes

- Auth: JWT Bearer, gerado em `backend/app/core/security.py`, `pbkdf2_sha256` (260000 rounds)
- Canais: usar `agent_channel_bindings`; endpoints `/channels/registry` e `/connections` retornam **410 Gone** (legados)

---

## Deploy (Render)

- Configuração em [`render.yaml`](render.yaml)
- Migrações via `backend/scripts/render_migrate.py`
- **Atenção**: se o banco existir sem tabela `alembic_version`, o deploy falha explicitamente para evitar drift. Corrija o baseline manualmente antes de `alembic upgrade head`

---

## Testes

| Escopo | Comando | Observação |
|--------|---------|-----------|
| Backend (todos) | `pytest tests/backend/` | Usar `-x` para parar no 1º erro |
| Frontend (todos) | `npm run test` (em `frontend/`) | Sem flag `-q` |
| Sintaxe Python | `python -m compileall app` (em `backend/`) | Validação rápida |

---

## Documentação interna relevante

- [README.md](README.md) — visão geral e setup
- [AXI_TECHNICAL_AUDIT_REPORT.md](AXI_TECHNICAL_AUDIT_REPORT.md) — auditoria técnica
- [OPENAI_RESPONSES_API_IMPLEMENTATION.md](OPENAI_RESPONSES_API_IMPLEMENTATION.md) — integração OpenAI
- [TROUBLESHOOTING_CHAT.md](TROUBLESHOOTING_CHAT.md) — debug do chat
- [RENDER_FRONTEND_DEPLOY.md](RENDER_FRONTEND_DEPLOY.md) — deploy frontend
