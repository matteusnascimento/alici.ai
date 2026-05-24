# Troubleshooting: Chat não Responde

**Status:** 🔴 Chat não respondendo / IA silenciosa

---

## 🔍 Diagnóstico Rápido

### 1️⃣ Verificar OPENAI_API_KEY

**Este é o problema mais comum:**

```bash
# Verifique se está configurada:
echo $OPENAI_API_KEY

# Se vazio, configure em .env:
OPENAI_API_KEY=sk-seu-token-real
```

**Como obter a chave:**
1. Acesse https://platform.openai.com/account/api-keys
2. Clique em "Create new secret key"
3. Copie e salve em `.env`:
   ```
   OPENAI_API_KEY=sk-proj-...
   ```

### 2️⃣ Executar Debug Script

```bash
python debug_chat.py
```

**Possíveis saídas:**

| Saída | Significado | Solução |
|-------|-----------|---------|
| `OPENAI_API_KEY: [MISSING]` | API key não configurada | Configure em .env |
| `is_configured(): False` | Serviço não inicializou | Verifique a chave |
| `Healthcheck: error` | API não respondendo | Verifique chave / quota |
| `TODOS OS TESTES PASSARAM` | Sistema ok, problema no chat | Ver próximas seções |

---

## ❌ Problemas Comuns e Soluções

### Erro 1: "OPENAI_API_KEY não configurada"

**Sintomas:**
- Chat não responde
- Nenhuma mensagem de erro visível
- Resposta em "modo seguro"

**Solução:**
```bash
# 1. Edite .env
nano backend/.env

# 2. Adicione/atualize:
OPENAI_API_KEY=sk-seu-token-real

# 3. Reinicie o servidor
pkill -f uvicorn
python -m uvicorn app.main:app --reload
```

---

### Erro 2: "Invalid API Key"

**Sintomas:**
- IA não responde
- Log mostra: `401 authentication_error`

**Solução:**
```bash
# 1. Verifique se a chave é válida
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer sk-sua-chave"

# 2. Se erro 401, a chave é inválida
# 3. Obtenha nova chave em https://platform.openai.com/account/api-keys
```

---

### Erro 3: "Rate Limit Exceeded"

**Sintomas:**
- IA responde ocasionalmente
- Log mostra: `429 rate_limit_error`

**Solução:**
```bash
# 1. Aguarde antes de tentar novamente (1 minuto)
# 2. Verifique seu plano na OpenAI:
#    https://platform.openai.com/account/billing/overview
# 3. Aumente rate limit se tiver plano pago
```

---

### Erro 4: "Timeout"

**Sintomas:**
- Chat espera mais de 30s e falha
- Log mostra: `504 timeout`

**Solução:**
```bash
# 1. Aumente timeout em .env:
OPENAI_TIMEOUT_SECONDS=60

# 2. Verifique sua conexão:
ping api.openai.com

# 3. Tente novamente
```

---

### Erro 5: "No Response Text"

**Sintomas:**
- Chat envia mensagem mas resposta vem vazia

**Solução:**
```bash
# Esse erro foi corrigido na última atualização
# Se ainda ocorrer, execute:
python debug_chat.py

# Envie o output para análise
```

---

## 🧪 Teste Manual Passo a Passo

### Passo 1: Servidor Rodando

```bash
# Terminal 1: Inicie o servidor
cd /path/to/alici.ai
python -m uvicorn app.main:app --reload --port 8000

# Verifique:
curl http://localhost:8000/api/health
# Esperado: {"status": "ok"}
```

### Passo 2: Execute Debug

```bash
# Terminal 2: Debug completo
python debug_chat.py

# Se tudo ok, continuamos
```

### Passo 3: Teste Manual do Chat

```bash
# Terminal 2: Execute teste manual
python test_chat_manual.py

# Esperado: 8/8 testes passaram
```

### Passo 4: Verifique Logs

```bash
# No terminal 1 (servidor), procure por:
# ✅ "openai_responses.success" = Tudo ok
# ❌ "openai_responses.error" = Problema!
# ⚠️  "tool_executor.execute" = Tool sendo executada
```

---

## 🔧 Verificações Técnicas

### Verificação 1: Variáveis de Ambiente

```bash
# Verificar todas as variáveis:
python -c "from app.core.config import settings; print(f'API Key: {\"set\" if settings.effective_openai_api_key else \"MISSING\"}')"
```

### Verificação 2: Database

```bash
# Verificar se DB está ok:
python -c "from app.core.database import get_db; print('Database OK')"

# Limpar DB se necessário (development):
rm backend/axi.db
python -m uvicorn app.main:app
```

### Verificação 3: Imports

```bash
# Testar se módulos importam:
python -c "from app.services.openai_responses_service import OpenAIResponsesService; print('OK')"
python -c "from app.services.chat_service import ChatService; print('OK')"
python -c "from app.services.tool_executor import ToolExecutor; print('OK')"
```

---

## 📊 Checklist de Troubleshooting

- [ ] OPENAI_API_KEY configurada em .env
- [ ] Servidor rodando: `curl http://localhost:8000/api/health` retorna 200
- [ ] Debug script passou: `python debug_chat.py`
- [ ] Teste manual rodou: `python test_chat_manual.py`
- [ ] Logs mostram "openai_responses.success"
- [ ] Nenhum erro de autenticação (401)
- [ ] Nenhum erro de rate limit (429)
- [ ] Nenhum timeout (504)

---

## 📞 Se Ainda Não Funcionar

### Colete informações:

```bash
# 1. Execute debug
python debug_chat.py > debug.log 2>&1

# 2. Copie logs do servidor
# (Terminal onde rodou uvicorn)

# 3. Execute teste manual
python test_chat_manual.py > test.log 2>&1

# 4. Envie logs para análise
```

### Informações a fornecer:

1. Output de `debug_chat.py`
2. Output de `test_chat_manual.py`
3. Logs do servidor (últimas 50 linhas)
4. Versão Python: `python --version`
5. Sistema: `uname -a` (Linux) ou `systeminfo` (Windows)

---

## 🚀 Solução Rápida (se nada funcionar)

```bash
# 1. Limpe tudo
rm -rf backend/__pycache__ backend/axi.db
pip install --upgrade openai

# 2. Verifique chave
export OPENAI_API_KEY=sk-proj-seu-token

# 3. Inicie servidor
python -m uvicorn app.main:app --reload

# 4. Teste em outro terminal
python test_chat_manual.py
```

---

## 📚 Recursos Úteis

- [OpenAI API Keys](https://platform.openai.com/account/api-keys)
- [OpenAI Pricing](https://platform.openai.com/pricing)
- [OpenAI Status](https://status.openai.com/)
- [Debug Script](./debug_chat.py)
- [Teste Manual](./test_chat_manual.py)

---

**Última atualização:** 2026-04-15  
**Status:** ✅ Guia completo de troubleshooting
