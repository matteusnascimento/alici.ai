# Alici AI Codebase Guide

## 🎯 Project Overview

**Alici** is a Portuguese-language AI chatbot with persistent memory, web search capabilities, and a holographic avatar interface. It's a Flask-based web application deployed on Render with PostgreSQL (Neon) for persistent memory storage across conversations.

The architecture prioritizes a **5-layer decision pipeline** where each layer can short-circuit to avoid redundant processing: identity checks → memory lookups → behavioral patterns → web search → graceful fallback.

## 🏗️ Architecture & Data Flow

### Request Pipeline (`engine.py` - Core Orchestrator)

All user questions flow through `gerar_resposta(pergunta)` with 5 sequential decision layers:

1. **Identity Layer** (Immutable): Detects "quem é você" patterns → returns fixed `identidade_alici()` response
2. **Memory Layer** (Fast retrieval): Exact match search in PostgreSQL → ranked by confidence score
3. **Local Rules Layer** (Behavioral): Pattern matching in `resposta.py` → keyword-triggered responses
4. **Web Search Layer** (External): If `precisa_pesquisa_web()` triggers, calls `buscar_na_web()` with threshold check
5. **Fallback Layer** (Graceful): "Ainda não tenho essa informação armazenada..." - never returns empty string

**Critical invariant**: Every successful response (except identity) MUST call `aprender(pergunta, resposta)` to store the Q&A pair for future learning.

### Component Responsibilities

| File | Purpose | Key Functions |
|------|---------|---|
| **engine.py** | Request orchestration | `gerar_resposta(pergunta)` orchestrates 5 layers; `gerar_resposta_com_emocao()` adds emotional metadata |
| **main.py** | Flask server & UI | Routes: `/` (holographic UI), `/chat` (POST handler), `/status` (health); inline HTML/CSS for avatar |
| **database.py** | PostgreSQL integration | `conectar()`, `buscar_memoria(pergunta)`, `aprender(pergunta, resposta)`, `criar_tabelas()` |
| **identidade.py** | AI personality constant | `identidade_alici()` - immutable, fixed response about creator & nature |
| **resposta.py** | Behavioral Q&A patterns | `responder_local(pergunta)` - ~80 hardcoded keyword→response rules (greetings, capabilities, time) |
| **intencao.py** | Intent detection | `precisa_pesquisa_web(pergunta)` - returns bool based on keyword matching |
| **web_search.py** | Web information retrieval | `buscar_na_web(pergunta)` - queries DuckDuckGo API, extracts abstract text |
| **sistema_emocoes.py** | Emotional metadata | `detectar_emocao(resposta)` analyzes response text for emotion (happy/thinking/serious/mysterious/neutral), returns aura color & animation speed |

## 🔌 Integration Points & External Dependencies

### PostgreSQL/Neon Database
- **Connection**: `DATABASE_URL` env var (from `.env`) - typically `postgresql://user:password@neon-host/dbname?sslmode=require`
- **Schema**: Single `memoria` table with columns: `id` (serial PK), `pergunta` (TEXT, indexed), `resposta` (TEXT), `confianca` (INT, default 1), `criado_em` (TIMESTAMP)
- **Index**: `idx_memoria_pergunta` on `pergunta` column for fast exact-match lookups
- **Confidence scoring**: First answer = `confianca: 1`; repeated Q&A pairs increment by 1; queries return highest confidence match first

### Web Search Integration (DuckDuckGo)
- **Endpoint**: `https://api.duckduckgo.com/?q={quote(pergunta)}&format=json`
- **Response parsing**: Extracts `AbstractText` if present, falls back to `RelatedTopics[0].Text`
- **Confidence threshold**: Web results accepted ONLY if confidence ≥ 0.6 (prevents low-quality answers being learned)
- **Error handling**: Catches timeout/network errors gracefully → returns None → engine uses fallback

### Frontend Communication
- **POST `/chat`**: Expects JSON `{"mensagem": "user question string"}`
- **Response**: JSON `{"resposta": "response text", "emocao": "...", "cor_aura": "#...", "velocidade_animacao": 1.2}`
- **Avatar state machine**: JavaScript controls avatar image transitions (idle→listen→think→speak→idle) based on response timing

## 📋 Patterns & Conventions

### Case Normalization (Critical!)
```python
pergunta = pergunta.lower().strip()  # ALWAYS do this first
```
- DB stores all `pergunta` values lowercased for consistent matching
- All pattern checks in `resposta.py` use `pergunta.lower()`
- Failure to normalize = silent memory misses

### Response Pattern in `resposta.py`
All local Q&A rules follow this structure:
```python
if any(k in pergunta for k in ["padrão1", "padrão2", "padrão3"]):
    return "Resposta aqui..."
```
**Why this pattern**:
- Multiple keywords improve robustness (typos, variations)
- Case-insensitivity via pre-normalized `pergunta`
- Easy to maintain and debug

### Confidence System Mechanics
```python
# Exact match query (case-insensitive)
SELECT resposta FROM memoria 
WHERE pergunta = %s 
ORDER BY confianca DESC LIMIT 1

# Learning (increment if exists, insert otherwise)
if already_learned(pergunta, resposta):
    UPDATE memoria SET confianca = confianca + 1
else:
    INSERT INTO memoria (pergunta, resposta) VALUES (...)
```

### Database Connection Pattern
ALL database operations must follow this cleanup pattern:
```python
try:
    conn = conectar()
    cur = conn.cursor()
    # your query
    conn.commit()
finally:
    if 'cur' in locals(): cur.close()
    if 'conn' in locals(): conn.close()
```
Missing `finally` blocks **leak connections** → deployment hangs after ~50 queries.

## 🚀 Development Workflows

### Local Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with: DATABASE_URL=postgresql://...?sslmode=require

# 3. Run locally
python main.py
# Access http://localhost:5000
```

### Adding New Q&A Rules
1. Edit `resposta.py` → add pattern to `responder_local()` function
2. Test locally: `python -c "from resposta import responder_local; print(responder_local('seu pergunta'))"`
3. Commit → deployed via Render auto-deploy on git push

### Testing Web Search Workflow
```python
from intencao import precisa_pesquisa_web
from web_search import buscar_na_web

if precisa_pesquisa_web("quem é Elon Musk"):
    result = buscar_na_web("quem é Elon Musk")
    if result and result.get("confianca", 0) >= 0.6:
        print(result["resposta"])
```

### Deployment to Render
- **Build command**: `pip install -r requirements.txt`
- **Start command**: `gunicorn main:app`
- **Environment variables**: Set `DATABASE_URL` in Render dashboard
- **Port**: Auto-detected from `PORT` env var; Gunicorn binds to 0.0.0.0:$PORT

## ⚠️ Common Pitfalls & Fixes

| Pitfall | Impact | Prevention |
|---------|--------|-----------|
| Forgetting `pergunta.lower()` | Silent memory misses; no exact matches found | Always normalize at function entry |
| Forgetting `aprender()` call | No learning happens; same questions asked repeatedly | Call in every non-identity branch |
| Web search without confidence check | Low-quality answers poisoned memory | Check `result.get("confianca", 0) >= 0.6` before storing |
| Missing DB connection cleanup | Connections exhaust pool after ~50 requests → 504 errors | Always use try/finally with `cur.close()` & `conn.close()` |
| Hardcoding avatar image paths | Frontend breaks in production | Use `/Static/Imagens/Avatar/` (exact case on Linux servers) |
| Multiple web search calls per question | Rate limiting, slow responses | Call `precisa_pesquisa_web()` BEFORE attempting `buscar_na_web()` |

## 📂 Key Files & Entry Points

- **Response orchestrator**: [engine.py](engine.py) - Read first to understand flow
- **Database queries**: [database.py](database.py#L42) - `buscar_memoria()` pattern
- **Q&A rule patterns**: [resposta.py](resposta.py#L8) - `responder_local()` function
- **Intent keywords**: [intencao.py](intencao.py#L1) - Triggers for web search
- **Web search wrapper**: [web_search.py](web_search.py#L4) - DuckDuckGo API integration
- **Emotion detection**: [sistema_emocoes.py](sistema_emocoes.py#L6) - Avatar animation metadata
- **Flask routes**: [main.py](main.py#L1-L10) - `/` (UI), `/chat` (handler)
- **Deployment config**: `.env.example`, `requirements.txt`, `runtime.txt` (Python 3.11)

## 🎯 Testing & Validation

Use included test utilities (in workspace root):
- `teste_engine_completo.py` - End-to-end pipeline test with sample questions
- `verificar_conexoes_lite.py` - Check imports & basic connectivity (no TensorFlow)
- `verificar_conexoes.py` - Full diagnostics including TensorFlow & database

Run: `python teste_engine_completo.py` to validate the entire request pipeline.

---

## 🔐 NEW: AUTHENTICATION & MULTI-USER ARCHITECTURE (FastAPI)

### User-Isolated System
The system now supports **per-user memory, history, and personalization**:

**Key files:**
- [auth.py](auth.py) - JWT authentication (register/login/logout/refresh)
- [database_models.py](database_models.py) - PostgreSQL schema with users, sessions, messages, user_memory
- [memory.py](memory.py) - Per-user memory with vector embeddings (RAG-ready)
- [embeddings.py](embeddings.py) - SentenceTransformers for semantic search
- [main_fastapi.py](main_fastapi.py) - FastAPI app (replace Flask main.py eventually)

### Request Flow (with auth):
```
Request → /auth/login (JWT token)
        → /chat (send token in header)
        → get_current_user() dependency
        → load user's relevant memories
        → generate response
        → save to user_memory with embedding
```

### Memory System
- **Types**: persona, preference, conversation, context
- **Storage**: PostgreSQL + vector embeddings
- **Retrieval**: Semantic similarity (top-k similar memories)
- **Personas**: técnico, mentor, espiritual, motivacional

### Database Schema (Neon)
```sql
users (id, email, senha_hash, plano)
sessions (id, user_id, token, expira_em)
messages (id, user_id, pergunta, resposta, criado_em)
user_memory (id, user_id, tipo, conteudo, embedding, importancia)
user_documents (id, user_id, nome, conteudo, embedding)
```

### Testing Auth Locally
```bash
# Register
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"nome":"User","email":"test@example.com","senha":"pass12345"}'

# Login (returns access_token)
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","senha":"pass12345"}'

# Chat (with token)
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"pergunta":"hello","incluir_emocao":true}'
```

### Deployment Notes
- Switch `Procfile` start command from `gunicorn main:app` to `gunicorn main_fastapi:app`
- PostgreSQL needs pgvector extension: `CREATE EXTENSION vector`
- Add `DATABASE_URL` env var to Render dashboard
- `requirements_new.txt` has all dependencies (torch, sentence-transformers may take time)
