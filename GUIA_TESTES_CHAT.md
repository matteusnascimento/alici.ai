# Guia de Testes: Chat com OpenAI Responses API

**Data:** 2026-04-15  
**Status:** ✅ Testes Implementados e Documentados

---

## 📋 Índice

1. [Testes Automatizados (pytest)](#testes-automatizados)
2. [Testes Manuais (script)](#testes-manuais)
3. [Fluxos de Teste](#fluxos-de-teste)
4. [Troubleshooting](#troubleshooting)

---

## 🤖 Testes Automatizados

### Localização
```
tests/backend/test_chat_responses_api.py
```

### Estrutura

#### **TestChatResponsesAPI** (4 testes)
Testa o endpoint `/api/chat/responses`:
- ✅ `test_chat_responses_basic()` - Envio simples
- ✅ `test_chat_responses_with_conversation_history()` - Com histórico
- ✅ `test_chat_responses_with_tool_calls()` - Com tool calling
- ✅ `test_chat_responses_error_fallback()` - Fallback em erro

#### **TestChatAgentSpecialized** (2 testes)
Testa agentes em `/api/chat/agent-respond`:
- ✅ `test_chat_agent_respond()` - Todos 3 agentes (sales, support, operations)
- ✅ `test_chat_agent_invalid()` - Validação de agente inválido

#### **TestChatTools** (2 testes)
Testa `/api/chat/tools`:
- ✅ `test_get_available_tools()` - Listagem de tools
- ✅ `test_tools_include_standard_tools()` - Validação de 5 tools padrão

#### **TestChatIntegration** (3 testes)
Testes de integração:
- ✅ `test_chat_send_vs_responses_api()` - Compatibilidade /send vs /responses
- ✅ `test_chat_billing_integration()` - Integração com billing
- ✅ `test_chat_persistence()` - Persistência em DB

#### **Cenários (2 testes)**
Testes de aceitação:
- ✅ `test_chat_scenario_create_reservation()` - Criar reserva via chat
- ✅ `test_chat_scenario_lead_creation()` - Criar lead via agente

**Total: 13 testes automatizados**

### Como Executar

#### Todos os testes do chat:
```bash
pytest tests/backend/test_chat_responses_api.py -v
```

#### Um teste específico:
```bash
pytest tests/backend/test_chat_responses_api.py::TestChatResponsesAPI::test_chat_responses_basic -v
```

#### Com coverage:
```bash
pytest tests/backend/test_chat_responses_api.py --cov=app.services.openai_responses_service --cov=app.services.chat_service
```

#### Com output detalhado:
```bash
pytest tests/backend/test_chat_responses_api.py -vv -s
```

---

## 🧪 Testes Manuais

### Localização
```
test_chat_manual.py
```

### Requisitos
```bash
pip install httpx
```

### Como Executar

#### Teste completo (padrão):
```bash
python test_chat_manual.py
```

#### Com servidor customizado:
```bash
python test_chat_manual.py --host 192.168.1.100 --port 8001
```

#### Com token de autenticação:
```bash
python test_chat_manual.py --token "seu_jwt_token_aqui"
```

### Testes Inclusos

| # | Teste | Endpoint | O que Testa |
|---|-------|----------|------------|
| 1 | Health Check | `/api/health` | Conectividade do servidor |
| 2 | Ferramentas | `GET /api/chat/tools` | Listagem de tools |
| 3 | Chat Simples | `POST /api/chat/send` | Chat tradicional |
| 4 | Responses API | `POST /api/chat/responses` | Nova API |
| 5 | Com Histórico | `POST /api/chat/responses` | Multi-turno |
| 6 | Agentes | `POST /api/chat/agent-respond` | Sales, support, operations |
| 7 | Conversas | `GET /api/chat/conversations` | Listagem |

### Output Esperado

```
================================================================================
  🧪 TESTE COMPLETO DO CHAT API
================================================================================

================================================================================
  Teste 1: Health Check
================================================================================

✅ Status 200
{
  "status": "ok",
  "database": "ok"
}

...

================================================================================
  📊 RESUMO DOS TESTES
================================================================================

✅ health
✅ tools
✅ chat_send
✅ chat_responses
✅ chat_history
✅ chat_sales
✅ chat_support
✅ conversations

Resultado: 8/8 testes passaram

🎉 TODOS OS TESTES PASSARAM!
```

---

## 📊 Fluxos de Teste

### Fluxo 1: Chat Simples

```
POST /api/chat/send
├─ user_id: autenticado
├─ text: "Olá!"
├─ conversation_id: null
└─ Resposta esperada:
   ├─ conversation (id, title, created_at)
   ├─ user_message (id, text, role="user")
   └─ assistant_message (id, text, role="assistant")
```

### Fluxo 2: Responses API

```
POST /api/chat/responses
├─ Chama OpenAIResponsesService.generate_response()
├─ Extrai: output_text, tool_calls
├─ Se tool_calls: ToolExecutor.execute()
└─ Resposta esperada:
   ├─ output_text: str
   ├─ conversation_id: int
   ├─ message_id: int
   └─ Status: 200
```

### Fluxo 3: Agente Especializado

```
POST /api/chat/agent-respond?agent_name=sales
├─ Valida agent_name ∈ {sales, support, operations}
├─ Chama OpenAIResponsesService.generate_agent_response()
├─ Injeta instruções especializadas
└─ Resposta esperada:
   └─ output_text com contexto da especialidade
```

### Fluxo 4: Multi-Turno

```
1. POST /api/chat/responses {text: "msg 1"} → conversation_id = 123
2. POST /api/chat/responses {text: "msg 2", conversation_id: 123}
├─ Carrega histórico das 10 últimas mensagens
├─ Injeta no contexto via context injection
├─ IA vê a conversa anterior
└─ Resposta tem contexto adequado
```

### Fluxo 5: Tool Calling

```
1. POST /api/chat/responses {text: "Quero uma reserva"}
2. OpenAI Responses API retorna:
   {
     output_text: "Vou criar...",
     tool_calls: [
       {
         name: "create_reservation",
         arguments: {...}
       }
     ]
   }
3. ToolExecutor.execute("create_reservation", {...})
   └─ Criação real no DB
4. Resposta persistida com metadados de tool execution
```

---

## ✅ Checklist de Teste

### Pre-Teste
- [ ] Servidor rodando em `http://localhost:8000`
- [ ] Database inicializado
- [ ] Token JWT obtido (se necessário)
- [ ] `OPENAI_API_KEY` configurada em `.env`

### Testes Automatizados
- [ ] `pytest tests/backend/test_chat_responses_api.py -v` passou
- [ ] Todos 13 testes executados
- [ ] Nenhum erro de importação
- [ ] Coverage > 80%

### Testes Manuais
- [ ] Health check passando
- [ ] Tools listadas corretamente
- [ ] Chat simples respondendo
- [ ] Responses API respondendo
- [ ] Histórico mantido
- [ ] Agentes especializados funcionando
- [ ] Conversas listadas

### Integração
- [ ] Mensagens persistidas em DB
- [ ] Billing check passando
- [ ] Tool calls executadas
- [ ] Fallback funcionando em erro

---

## 🔍 Troubleshooting

### "Connection refused"
```bash
# Servidor não está rodando
# Inicie com:
python -m uvicorn app.main:app --reload --port 8000
```

### "401 Unauthorized"
```bash
# Token expirado ou inválido
# Obtenha novo token via /api/signin
# Ou execute com --token
python test_chat_manual.py --token "novo_token"
```

### "OpenAI API Error"
```bash
# OPENAI_API_KEY não configurada
# Verifique em .env:
OPENAI_API_KEY=sk-...

# Ou teste mock passará:
pytest tests/backend/test_chat_responses_api.py -v
```

### "Database locked"
```bash
# SQLite em uso
# Feche outras conexões
# Or use: export DATABASE_URL=sqlite:///./test_axi.db
```

### Tool call não executada
```bash
# Verifique:
1. ToolExecutor registrou a ferramenta
2. Tool call foi extraída corretamente
3. Argumentos correspondem ao schema

# Debug:
pytest -vv -s tests/backend/test_responses_api_validation.py::test_tool_calls_extraction
```

---

## 📈 Métricas de Teste

### Cobertura Esperada
- `openai_responses_service.py`: > 85%
- `chat_service.py`: > 80%
- `tool_executor.py`: > 90%
- `openai_responses.py`: > 75%

### Performance
- Chat simples: < 500ms
- Responses API: < 2s (depende OpenAI)
- Tool execution: < 1s

### Taxa de Sucesso
- Testes automatizados: 100%
- Testes manuais: 100%
- Integração end-to-end: 100%

---

## 🚀 Próximos Passos

Após passar todos os testes:

1. ✅ Deployment em staging
2. ✅ Teste de carga
3. ✅ Teste em produção (canary)
4. ✅ Monitoramento

---

**Status:** ✅ PRONTO PARA TESTE  
**Última atualização:** 2026-04-15
