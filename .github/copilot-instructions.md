# Alici AI Codebase Guide

## 🎯 Project Overview

**Alici** is a Portuguese-language AI chatbot with persistent memory, web search, and a holographic avatar interface. It's a Flask-based web app deployed on Render with PostgreSQL (Neon) for memory storage.

## 🏗️ Architecture & Data Flow

### Request Pipeline (`engine.py` - Core Logic)
Requests flow through 5 sequential decision layers:
1. **Identity Layer**: Hardcoded responses for "quem é você" (who are you) → returns `identidade_alici()`
2. **Memory Layer**: Query PostgreSQL for exact question match → `buscar_memoria(pergunta)`
3. **Local Rules**: Pattern matching in `resposta.py` for behavioral responses
4. **Web Search**: If question triggers keywords (who/what/news/price/how) → `buscar_na_web()`
5. **Fallback**: "Ainda não tenho essa informação" - never returns blank

**Critical**: Each successful response calls `aprender()` to store the Q&A pair with confidence scoring.

### Component Responsibilities

| File | Purpose | Key Functions |
|------|---------|---|
| `main.py` | Flask server & holographic UI | Routes: `/` (UI), `/status`, `/chat` (POST) |
| `engine.py` | Response generation logic | `gerar_resposta(pergunta)` - orchestrates all layers |
| `database.py` | PostgreSQL integration | `buscar_memoria()`, `aprender()` - Q&A storage |
| `identidade.py` | AI personality constant | `identidade_alici()` - immutable identity response |
| `resposta.py` | Behavioral patterns (keyword→response) | `responder_local()` - ~50 hardcoded Q&A rules |
| `intencao.py` | Intent detection for web search | `precisa_pesquisa_web()` - keyword triggers |
| `web_search.py` | External information retrieval | `buscar_na_web()` - searches web, returns `{"resposta": str, "confianca": float}` |

## 🔌 Integration Points & External Dependencies

### PostgreSQL/Neon Setup
- **Connection**: `DATABASE_URL` environment variable (from `.env`)
- **Schema**: Single `memoria` table with indexed `pergunta` column for fast matching
- **Confidence System**: `confianca` INT increments on repeated Q&As; exact matches ranked by `ORDER BY confianca DESC`

### Web Search Integration
- `web_search.py` must return dict: `{"resposta": "...", "confianca": 0.6-1.0}`
- Only accepts confidence ≥ 0.6 to prevent low-quality responses being learned
- Question lowercase comparison: `pergunta.lower()` stored in DB for case-insensitive matching

### Frontend Communication
- **Input**: POST `/chat` with JSON `{"mensagem": "user question"}`
- **Output**: JSON `{"resposta": "ai response"}`
- **Avatar State Machine**: Frontend changes avatar image (idle→listen→think→speak→idle) based on timing

## 📋 Patterns & Conventions

### Case Sensitivity
- **Always normalize**: `pergunta.lower().strip()` before DB queries and pattern matching
- DB stores lowercased `pergunta` column
- String matching uses lowercase: `if "quem é" in pergunta`

### Response Pattern in `resposta.py`
All local responses follow this structure:
```python
if any(k in pergunta for k in ["pattern1", "pattern2", "pattern3"]):
    return "Response text..."
```
**Why**: Multiple keywords prevent typos; case-insensitive via `pergunta.lower()`

### Confidence in Memory
- First query = `confianca: 1`
- Repeated Q&As increment `confianca`
- Highest confidence results ranked first in `buscar_memoria()`
- Web search requires ≥0.6 confidence before learning

### Error Handling Pattern
All DB functions wrapped in try/except with resource cleanup:
```python
try:
    conn = conectar()
    # query
finally:
    if 'cur' in locals(): cur.close()
    if 'conn' in locals(): conn.close()
```

## 🚀 Development Workflows

### Local Development
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env: DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
python main.py
# Access: http://localhost:5000
```

### Adding New Q&A Rules
1. Edit `resposta.py` → add pattern to `responder_local()`
2. Test locally: `python -c "from resposta import responder_local; print(responder_local('your question'))"`
3. Function automatically saves to DB via `aprender()` in `engine.py`

### Testing Web Search Integration
```python
from web_search import buscar_na_web
result = buscar_na_web("test question")
# Should return: {"resposta": "...", "confianca": float}
```

### Deployment (Render)
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn main:app`
- **Env vars required**: `DATABASE_URL` (Neon connection string), `PORT` (auto-set by Render)

## ⚠️ Common Pitfalls

1. **Forgetting `.lower()`**: Database queries fail if not normalized → no memory hits
2. **Not calling `aprender()`**: Responses aren't stored, learning breaks
3. **Web search confidence threshold**: Results below 0.6 are ignored (prevents poisoning memory)
4. **Connection cleanup**: Missing `finally` blocks leak DB connections
5. **Avatar UI paths**: Case-sensitive on production; use `/Static/Imagens/Avatar/` paths exactly

## 📂 Key Files Reference

- **Response logic entry point**: [engine.py](engine.py#L1)
- **DB query patterns**: [database.py](database.py#L35) (`buscar_memoria` function)
- **Frontend HTML/CSS/JS**: [main.py](main.py#L12) (inline in home() route)
- **Local Q&A rules**: [resposta.py](resposta.py#L1)
- **Production config**: [Procfile](Procfile), [requirements.txt](requirements.txt)
