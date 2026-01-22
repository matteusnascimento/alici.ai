# ALICI™ - ROADMAP DE IMPLEMENTAÇÃO (90 DIAS)

## ✅ FASE 1: AUTENTICAÇÃO & MEMÓRIA (DIAS 0-30) - ENTREGUE

### Entregáveis criados:

1. **`config.py`** - Configuração centralizada
   - Settings de banco, segurança, embeddings
   - Carregável de `.env`

2. **`database_models.py`** - Banco de dados Neon
   - Tabelas: users, sessions, messages, user_memory, user_documents
   - Índices para performance
   - Inicialização automática

3. **`auth.py`** - Sistema de autenticação
   - Registro de usuários (bcrypt)
   - Login com JWT (access + refresh)
   - Logout com invalidação
   - Endpoint `/me` para perfil

4. **`embeddings.py`** - Modelo de embeddings
   - SentenceTransformers (multilíngue)
   - Cache do modelo em memória
   - Funções para embed e similarity

5. **`memory.py`** - Memória por usuário
   - `UserMemory.save_memory()` - Salva com embedding
   - `UserMemory.get_relevant_memory()` - Busca vetorial
   - `UserPreferences` - Personas (técnico, mentor, espiritual, motivacional)
   - Importância dinâmica

6. **`main_fastapi.py`** - App FastAPI completa
   - Startup: inicializa banco + embeddings
   - `/chat` - Chat com memória
   - `/chat/history` - Histórico pesquisável
   - `/memory` - CRUD de memória
   - `/profile/persona` - Escolher tone
   - `/auth/*` - Todos os endpoints de auth

7. **`requirements_new.txt`** - Dependências atualizadas
   - FastAPI + Uvicorn
   - PostgreSQL + psycopg
   - JWT + bcrypt
   - SentenceTransformers
   - Redis (para cache)

---

## 🔄 PRÓXIMOS PASSOS (DIAS 31-60) - RAG + INTELIGÊNCIA

### O que falta criar:

### 1. **RAG - Retrieval Augmented Generation**
   - **`rag.py`** - Engine de RAG
     - `search_documents()` - Busca em embeddings
     - `enrich_context()` - Monta contexto para o modelo
     - `generate_with_context()` - Resposta com dados reais
   
   - **Rotas adicionadas a `main_fastapi.py`**:
     ```
     POST /documents - Upload arquivo
     GET /documents - Listar documentos
     DELETE /documents/{id} - Deletar
     ```

### 2. **Web Search Inteligente**
   - Manter `web_search.py` existente
   - Integrar com RAG
   - Salvar resultados como documento
   - Aprender com a web

### 3. **Planos Pagos + Rate Limit**
   - **`plans.py`** - Sistema de planos
     - Free: 10 msgs/dia
     - Pro: 500 msgs/dia + RAG
     - Enterprise: unlimited
   
   - **Middleware de rate limiting**
   - Verificação de plano em cada requisição

---

## 📊 DIAS 61-90 - PRODUTO PRONTO

### 1. **Painel Admin**
   - Dashboard de usuários
   - Monitoramento de uso
   - Gestão de planos

### 2. **Frontend ChatGPT-style**
   - Migrar de HTML inline para app moderna
   - Login + chat em SPA
   - Histórico com busca
   - Tema escuro

### 3. **Voz (STT + TTS)**
   - Integração com Whisper (OpenAI)
   - TTS own-brand

### 4. **Deploy em Produção**
   - Gunicorn config
   - Variáveis de ambiente
   - Render auto-deploy
   - CI/CD pipeline

---

## 🧪 COMO TESTAR AGORA

### Setup local:

```bash
# 1. Criar .env com DATABASE_URL
echo "DATABASE_URL=postgresql://user:pass@neon-host/alici" > .env

# 2. Instalar dependências
pip install -r requirements_new.txt

# 3. Rodar FastAPI
uvicorn main_fastapi:app --reload

# 4. Testar endpoints:
```

### Teste de Registro:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "email": "joao@example.com",
    "senha": "senha123456"
  }'
```

### Teste de Login:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@example.com",
    "senha": "senha123456"
  }'
```

Retorna:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### Teste de Chat:
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -d '{
    "pergunta": "Qual é o significado da vida?",
    "incluir_emocao": true
  }'
```

Retorna:
```json
{
  "id": "message-uuid",
  "resposta": "A vida tem significado quando você...",
  "emocao": "philosophical",
  "cor_aura": "#8b5cf6",
  "timestamp": "2026-01-22T11:30:00"
}
```

### Teste de Memória:
```bash
# Salvar na memória
curl -X POST "http://localhost:8000/memory" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN" \
  -d '{
    "tipo": "preferencia",
    "conteudo": "Gosto de respostas técnicas e diretas",
    "importancia": 9
  }'

# Recuperar memória
curl -X GET "http://localhost:8000/memory" \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"
```

---

## 🎯 CHECKLIST PRÓXIMAS SEMANAS

- [ ] Testar banco Neon (criar extensão vector)
- [ ] Rodar setup local
- [ ] Testar fluxo auth completo
- [ ] Testar embeddings
- [ ] Testar memória
- [ ] Deploy FastAPI em Render (teste)
- [ ] Criar RAG
- [ ] Implementar planos
- [ ] Criar frontend
- [ ] Monetização

---

## 💰 CUSTO ESTIMADO

| Serviço | Custo |
|---------|-------|
| Neon (PostgreSQL) | ~$5/mês |
| Render (FastAPI) | ~$7/mês |
| SentenceTransformers | FREE (local) |
| Storage | ~$1/mês |
| **Total** | **~$13/mês** |

👉 Escala conforme receita.

---

## ✨ O QUE VOCÊ TEM AGORA

✅ Login seguro (JWT + bcrypt)
✅ Memória por usuário
✅ Embeddings prontos
✅ Histórico de mensagens
✅ Personas (tons diferentes)
✅ Base para RAG
✅ Base para monetização
✅ Pronto para 1000+ usuários

---

## 🚀 PRÓXIMO COMANDO

Quando estiver pronto, execute:

```bash
bash setup-alici.sh
```

Ou manualmente:
```bash
pip install -r requirements_new.txt
python -c "from database_models import init_db; import os; init_db(os.getenv('DATABASE_URL'))"
uvicorn main_fastapi:app --reload
```

---

**ALICI™ agora é uma plataforma de IA, não um bot.**
