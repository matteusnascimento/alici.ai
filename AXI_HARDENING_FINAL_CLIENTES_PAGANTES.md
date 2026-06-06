# AXI - Hardening Final para Clientes Pagantes

## Objetivo
Concluir hardening de estabilidade, cobertura de testes, UX/erros e validação de staging para elevar de "beta" para "clientes pagantes".

## Escopo executado
1. Estabilidade da suíte backend completa.
2. Cobertura dedicada de Account no backend.
3. Hardening de UX/erros técnicos expostos ao usuário.
4. QA em staging Render com fluxo real de cliente novo.
5. Correções de produção para drift de schema.

## Alterações implementadas

### 1) Estabilidade da suíte backend
- Arquivo: `tests/backend/conftest.py`
- Mudança:
  - Removido `drop_all/create_all` por teste.
  - Substituído por limpeza de dados em todas as tabelas (`DELETE`) mantendo schema.
  - Mantido seed de usuário dev para compatibilidade dos testes.
- Resultado:
  - Redução de risco de lock/intermitência em SQLite.
  - Execução consistente da suíte completa.

### 2) Cobertura dedicada de Account
- Arquivo novo: `tests/backend/test_account.py`
- Coberturas adicionadas:
  - Perfil: leitura e atualização.
  - Validação de conflito (email/username duplicado).
  - Validação de telefone mínimo.
  - Preferências e notificações (round-trip).
  - Integrações (seed e toggle enable/disable).
  - Segurança (troca de senha + relogin + senha atual inválida).
  - Privacidade (export/delete request) e logout.
- Resultado:
  - Fluxo de Account com cobertura dedicada e regressão protegida.

### 3) Hardening UX e mensagens
- Arquivo: `backend/app/services/account_service.py`
- Mudança:
  - Mensagens de exportação/exclusão de conta padronizadas em pt-BR amigável.

### 4) Hardening de erro interno (produção)
- Arquivo: `backend/app/main.py`
- Mudança:
  - Handler global de exceção para retorno seguro:
    - HTTP 500 com mensagem amigável.
    - Sem vazamento de traceback técnico para cliente.

### 5) Hardening de migração/deploy
- Arquivo: `backend/scripts/render_migrate.py`
- Mudança:
  - Removido comportamento perigoso de `stamp head` automático quando banco tem tabelas sem `alembic_version`.
  - Agora o deploy falha explicitamente nesse cenário para evitar drift silencioso.

- Arquivo novo: `backend/alembic/versions/c4d5e6f7a8b9_fix_conversations_title_drift.py`
- Mudança:
  - Migração corretiva idempotente para adicionar coluna ausente `conversations.title` em bases com drift.

### 6) Hardening de testes frontend (ruído/warnings)
- Arquivos:
  - `frontend/src/test/dashboard-panel.test.tsx`
  - `frontend/src/test/agents-v2-flow.test.tsx`
  - `frontend/src/test/agent-overview-onboarding.test.tsx`
- Mudanças:
  - Sincronização de asserts com updates assíncronos (redução de warnings de `act`).
  - Remoção de ruído de stderr esperado nos testes.
  - Ajuste de validação de link sem navegar para rota não registrada.

## Evidências de validação

### Backend
- `pytest tests/backend -q`
  - Resultado: **42 passed**

- `pytest tests/backend/test_account.py -q`
  - Resultado: **3 passed**

### Frontend
- `npm run test` em `frontend/`
  - Resultado: **10 arquivos / 18 testes passed**
  - Sem warnings críticos de `act` após ajustes.

### Staging Render (smoke real)
Base: `https://alici-ai.onrender.com`

- `GET /health` -> **200**
- `POST /api/auth/register` -> **200**
- `POST /api/auth/login` -> **200**
- `GET /api/user/me` -> **200**
- `GET /api/account/profile` -> **200**
- `POST /api/chat/send` -> **500** (antes da migração corretiva em produção)

Diagnóstico do 500:
- Banco de staging com drift (coluna `conversations.title` ausente).
- Correção já implementada via migração `c4d5e6f7a8b9`.

## Veredito

**Status atual do código**: APROVADO para clientes pagantes (hardening concluído no repositório).

**Status do ambiente staging/render**: APROVAÇÃO CONDICIONAL até próximo deploy com migração aplicada.

Condição para liberar pagantes sem ressalva:
1. Deploy da versão com migração `c4d5e6f7a8b9`.
2. Reexecutar smoke staging e confirmar `POST /api/chat/send` = 200 (ou erro de IA controlado sem traceback).

Após essa condição, o sistema fica apto para operação com clientes pagantes com risco residual baixo e controles de regressão adequados.

## Adendo de deploy e smoke (2026-04-12)

### Ações executadas
- Verificação de pendências de git em `main` e validação de testes antes de publicação.
- Testes locais executados antes do push:
  - `pytest tests/backend -q` -> 42 passed
  - `npm run test` (frontend) -> 10 arquivos / 18 testes passed
- Commits publicados em `main`:
  - `e15c071` (hardening final + migração + ajustes)
  - `510a8d8` (remoção de artefato gerado)
- Push realizado com sucesso para `origin/main`.

### Evidência de staging após push
Smoke reexecutado duas vezes em `https://alici-ai.onrender.com` com usuário novo em cada rodada:
- `GET /health` -> 200
- `POST /api/auth/register` -> 200
- `POST /api/auth/login` -> 200
- `GET /api/user/me` -> 200
- `GET /api/account/profile` -> 200
- `POST /api/chat/send` -> 500

Detalhe do erro atual no staging:
- Ainda retorna traceback técnico com `psycopg.errors.UndefinedColumn: column "title" of relation "conversations" does not exist`.
- Isso indica que o ambiente em execução ainda não aplicou a migração corretiva `c4d5e6f7a8b9_fix_conversations_title_drift.py`.

### Tentativa de migração manual
- Tentativa local de `alembic upgrade head` apontando para o banco remoto via configuração do backend: falhou por erro de autenticação no PostgreSQL (`password authentication failed`).
- Sem acesso válido ao banco e sem token/API do Render no ambiente local, não foi possível consultar logs de deploy/build/start/migration pelo painel/CLI diretamente a partir deste terminal.

### Status final deste ciclo
- Código no `main`: atualizado e publicado.
- Staging Render: ainda bloqueado por drift de schema (`conversations.title` ausente).

### Ação necessária para desbloqueio
Executar no ambiente Render (Shell/Job do serviço) com credenciais ativas do próprio runtime:
1. `cd /opt/render/project/src/backend`
2. `alembic upgrade head`
3. Confirmar `alembic current` contendo `c4d5e6f7a8b9`
4. Reexecutar smoke e validar `POST /api/chat/send` sem erro de schema.

## Veredito atualizado
- Não aprovado sem ressalvas neste momento.
- Bloqueio exato: migração `c4d5e6f7a8b9` ainda não aplicada no banco do staging em execução.
