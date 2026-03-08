# Relatorio Tecnico de Auditoria Completa - ALICI
Data: 2026-03-08

## Resumo Geral
- Total de erros encontrados: 17
- Erros criticos: 9
- Erros medios: 8
- Rotas quebradas/inexistentes chamadas pelo frontend: 1
- Botoes sem funcao (acao real): 3
- Event listeners ausentes para elementos acionaveis: 3
- Funcoes backend sem retorno explicito nos endpoints auditados: 0

## Escopo Coberto
- Frontend legado: `frontend/static/js/`, `frontend/templates/`
- Frontend Next: `frontend/alici-platform/`
- Backend principal: `main.py`, `app/api/routes/`, `app/services/`, `app/models/`
- Backend legado/alternativo: `alici_api/routes/`, `alici_api/services/`, `alici_api/middleware/`

Observacao de estrutura:
- Diretorios literais `backend/`, `controllers/`, `middlewares/` (plural) na raiz nao existem.
- Equivalentes encontrados: `app/api/routes`, `app/services`, `app/models`, `alici_api/middleware`.

## Erros Criticos
1) arquivo: `frontend/static/js/app.js`
- linha: 205
- problema: optional chaining quebrado (`profileModal ? .querySelector(...)`), gera erro de parse e derruba o script.
- solucao recomendada: corrigir para `profileModal?.querySelector(...)` e bloquear regressao com lint/CI.

2) arquivo: `frontend/static/js/app.js`
- linha: 295
- problema: optional chaining quebrado (`...('profileFullName') ? .value`), erro de parse.
- solucao recomendada: corrigir para `?.value`.

3) arquivo: `frontend/static/js/app.js`
- linha: 296
- problema: optional chaining quebrado (`profileCurrentPassword ? .value`), erro de parse.
- solucao recomendada: corrigir para `?.value`.

4) arquivo: `frontend/static/js/app.js`
- linha: 297
- problema: optional chaining quebrado (`profileNewPassword ? .value`), erro de parse.
- solucao recomendada: corrigir para `?.value`.

5) arquivo: `frontend/static/js/app.js`
- linha: 314
- problema: optional chaining quebrado (`... ? .focus()`), erro de parse.
- solucao recomendada: corrigir para `?.focus()`.

6) arquivo: `frontend/static/js/dashboard.js`
- linha: 59
- problema: optional chaining quebrado (`data ? .historico`) em fluxo de historico.
- solucao recomendada: corrigir para `data?.historico`.

7) arquivo: `frontend/static/js/chat.js`
- linha: 132
- problema: optional chaining quebrado (`data ? .id`) em criacao de conversa.
- solucao recomendada: corrigir para `data?.id`.

8) arquivo: `frontend/templates/quantum.html`
- linha: 735
- problema: chamada `POST /chat` inexistente no backend principal (so existe `GET /chat` para pagina e `POST /api/chat/message` para API).
- solucao recomendada: migrar para `POST /api/chat/message` com payload compativel e token.

9) arquivo: `frontend/templates/chat.html`
- linha: 321
- problema: pagina de chat carrega `app.js` (chat simplificado) em vez de `chat.js` (multi-conversa), quebrando o fluxo esperado de conversas/historico.
- solucao recomendada: usar `type="module"` e carregar `chat.js`, ou alinhar uma unica implementacao oficial.

## Erros Medios
1) arquivo: `frontend/static/js/app.js`
- linha: 61
- problema: login fake (gera JWT local sem chamar `/api/auth/login`), fluxo visual sem autenticacao real.

2) arquivo: `frontend/static/js/dashboard.js`
- linha: 59
- problema: parser de historico espera `data.historico`/`data.history`, mas `GET /api/chat/conversations` retorna array de conversas. Resultado: historico nao renderiza corretamente.

3) arquivo: `frontend/templates/dashboard.html`
- linha: 189
- problema: botao `Escolher Pro` (classe `plan-btn`) sem listener/acao no `dashboard.js`.

4) arquivo: `frontend/templates/settings.html`
- linha: 48
- problema: botao `Fazer upgrade` sem id/listener e sem acao backend.

5) arquivo: `frontend/templates/settings.html`
- linha: 123
- problema: botao `Atualizar seguranca` sem listener e sem endpoint acionado.

6) arquivo: `frontend/static/js/api.js`
- linha: 92
- problema: cliente retorna `response.json()` sem validar `response.ok`; erros HTTP viram "sucesso" no chamador (erro silencioso).

7) arquivo: `frontend/static/js/chat.js`
- linha: 340
- problema: `catch {}` vazio em carregamento de perfil, suprime falhas e dificulta diagnostico.

8) arquivo: `frontend/alici-platform/`
- linha: multiplas
- problema: 178 erros de compilacao reportados no estado atual da workspace (ex.: React namespace/tipos/modulos), impedindo validacao consistente desse frontend.

## Endpoints Faltando / Invalidos
- `POST /chat` chamado em `frontend/templates/quantum.html:735` -> inexistente no backend principal.

## Botoes Sem Funcao
- `frontend/templates/dashboard.html:189` - `Escolher Pro` (`plan-btn`) sem listener no `dashboard.js`.
- `frontend/templates/settings.html:48` - `Fazer upgrade` sem listener/acao.
- `frontend/templates/settings.html:123` - `Atualizar seguranca` sem listener/acao.

## Rotas Inexistentes Chamadas
- `POST /chat` em `frontend/templates/quantum.html:735`.

## Funcoes Sem Retorno (Backend)
- Nos endpoints auditados em `app/api/routes/` e `alici_api/routes/`, nao foi identificado handler sem retorno explicito (retornam dict/lista ou levantam `HTTPException`).
- Problema predominante de contrato: inconsistencia de formato (nem todos retornam `{status, data, error}`).

## Event Listeners Ausentes
- `frontend/templates/dashboard.html:189` (botao de compra) sem binding no `frontend/static/js/dashboard.js`.
- `frontend/templates/settings.html:48` sem binding no `frontend/static/js/settings.js`.
- `frontend/templates/settings.html:123` sem binding no `frontend/static/js/settings.js`.

## Inconsistencias Frontend x Backend
- Duas pilhas de backend coexistem (`main.py` com `app/api/routes/*` e `alici_api/app.py` com `alici_api/routes/*`), aumentando risco de divergencia de contrato.
- Frontend legado misto: `chat.html` usa `app.js` enquanto existe `chat.js` separado com contrato diferente.
- Contrato de resposta minimo `{status,data,error}` nao e padrao em toda API; apenas algumas rotas seguem envelope.

## Fluxos Principais (Status)
### LOGIN
- `frontend/templates/login.html` chama `/api/auth/login` e salva token.
- Status: parcialmente operacional (fluxo de login da pagina dedicada existe).
- Risco: `app.js` possui login local fake e pode confundir comportamento em rotas que usam esse script.

### CHAT
- Fluxo esperado (criar conversa, enviar mensagem, salvar historico) nao esta consistente no legado:
  - `chat.html` carrega script errado (`app.js`) e nao fluxo multi-conversa real.
  - `chat.js` tem quebra de sintaxe em `data ? .id`.
- Status: quebrado/instavel.

### DASHBOARD
- Navegacao e envio de chat existem, mas billing/profiling nao completam contrato.
- `dashboard.js` nao trata compra de plano.
- Status: parcialmente operacional.

### BILLING
- Endpoint backend existe (`POST /api/billing/checkout`), mas dashboard legado nao aciona.
- Status: quebrado no dashboard; funciona apenas na tela/script que implementa chamada explicitamente.

## Melhorias Recomendadas
1) Unificar frontend oficial (escolher `app.js` ou `chat.js`/`dashboard.js`) e remover duplicidade de fluxos.
- beneficio tecnico: reduz regressao e contratos conflitantes.

2) Padronizar resposta API em envelope `{status,data,error}` em todos endpoints.
- beneficio tecnico: simplifica tratamento uniforme no frontend e observabilidade.

3) Endurecer cliente HTTP (`api.js`) para lançar excecao quando `!response.ok`.
- beneficio tecnico: elimina erro silencioso e melhora confiabilidade.

4) Adicionar lint/teste estatico para barrar `? .` / `? ?` antes de merge.
- beneficio tecnico: previne quebra total de scripts por erro de parse.

5) Cobrir botoes criticos com testes E2E (Playwright/Cypress) para login, chat, billing, settings.
- beneficio tecnico: garante que funcionalidade nao fique apenas visual.

6) Criar matriz de contrato endpoint-frontend (fonte unica de verdade).
- beneficio tecnico: evita chamadas para rotas inexistentes.

7) Resolver setup de dependencias do frontend Next (`frontend/alici-platform`) e reexecutar typecheck/lint.
- beneficio tecnico: recupera confianca de build e reduz defeitos em producao.

## Evidencia de Testes
- Suite executada: `tests/test_enterprise_expansion_contracts.py`, `tests/test_platform_validation.py`, `tests/test_knowledge_rag_flow.py`
- Resultado: `10 passed, 1 warning`.
- Interpretação: backend principal possui estabilidade basica de contrato nas suites cobertas, mas o frontend legado ainda apresenta falhas criticas de fluxo e integracao.
