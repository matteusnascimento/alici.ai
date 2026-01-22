"""
main.py - FastAPI app para ALICI™ com autenticação e memória
"""
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import time
import uuid
import os

from config import get_settings
from database_models import init_db
from auth import router as auth_router, get_current_user
from engine import gerar_resposta, gerar_resposta_com_emocao
from database_models import get_db
from memory import UserMemory, UserPreferences
from embeddings import init_embeddings

# ==================== CONFIG ====================

settings = get_settings()

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="ALICI™ - IA com Identidade, Memória e Autenticação"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== INICIALIZAÇÃO ====================

@app.on_event("startup")
async def startup_event():
    """Inicializa banco, embeddings e modelos"""
    print("🚀 Iniciando ALICI™...")
    
    # Conecta ao banco e cria tabelas
    init_db(os.getenv("DATABASE_URL"))
    print("✅ Banco de dados inicializado")
    
    # Carrega modelo de embeddings
    init_embeddings()
    print("✅ Modelo de embeddings carregado")
    
    print("🟢 ALICI™ pronta para receber requisições")

# ==================== MODELOS ====================

class ChatRequest(BaseModel):
    pergunta: str
    incluir_emocao: bool = True

class ChatResponse(BaseModel):
    id: str
    resposta: str
    emocao: Optional[str] = None
    cor_aura: Optional[str] = None
    timestamp: str

from typing import Optional

# ==================== ROTAS DE CHAT ====================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: str = Depends(get_current_user)):
    """
    Endpoint principal de chat com memória e autenticação
    
    Fluxo:
    1. Valida usuário
    2. Busca memória relevante
    3. Enriquece contexto
    4. Gera resposta
    5. Salva na memória
    """
    db = get_db()
    start_time = time.time()
    message_id = str(uuid.uuid4())
    
    pergunta = request.pergunta.lower().strip()
    
    # Busca memória relevante
    relevant_memories = UserMemory.get_relevant_memory(current_user, pergunta, limit=3)
    context = "\n".join([m["conteudo"] for m in relevant_memories if m["similaridade"] > 0.5])
    
    # Gera resposta
    if request.incluir_emocao:
        result = gerar_resposta_com_emocao(pergunta)
        resposta = result["resposta"]
        emocao = result.get("emocao")
        cor_aura = result.get("cor_aura")
    else:
        resposta = gerar_resposta(pergunta)
        emocao = None
        cor_aura = None
    
    # Calcula tempo de resposta
    tempo_resposta_ms = int((time.time() - start_time) * 1000)
    
    # Salva mensagem no histórico
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO messages 
                (id, user_id, pergunta, resposta, emocao, tempo_resposta_ms)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (message_id, current_user, pergunta, resposta, emocao, tempo_resposta_ms)
            )
            conn.commit()
    
    # Salva na memória se for relevante
    if len(resposta) > 50:  # Salva respostas significativas
        UserMemory.save_memory(
            current_user,
            tipo="conversa",
            conteudo=f"P: {pergunta}\nR: {resposta[:200]}",
            importancia=min(5, len(resposta) // 100)
        )
    
    return ChatResponse(
        id=message_id,
        resposta=resposta,
        emocao=emocao,
        cor_aura=cor_aura,
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/chat/history")
async def get_chat_history(
    limit: int = 20,
    offset: int = 0,
    current_user: str = Depends(get_current_user)
):
    """Retorna histórico de conversas do usuário"""
    db = get_db()
    
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, pergunta, resposta, emocao, criado_em
                FROM messages
                WHERE user_id = %s
                ORDER BY criado_em DESC
                LIMIT %s OFFSET %s
                """,
                (current_user, limit, offset)
            )
            
            messages = []
            for row in cur.fetchall():
                messages.append({
                    "id": row[0],
                    "pergunta": row[1],
                    "resposta": row[2],
                    "emocao": row[3],
                    "criado_em": row[4].isoformat()
                })
            
            return {"messages": messages}

# ==================== ROTAS DE MEMÓRIA ====================

@app.get("/memory")
async def get_memory(
    tipo: Optional[str] = None,
    min_importancia: Optional[int] = None,
    since_iso: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: str = Depends(get_current_user)
):
    """Retorna a memória do usuário com filtros e busca semântica.

    Query params:
    - `tipo`: filtra por tipo
    - `min_importancia`: filtra por importância mínima
    - `since_iso`: ISO timestamp, memórias depois desta data
    - `query`: busca semântica (usa embeddings)
    - `limit`/`offset`: paginação
    """
    memories = UserMemory.get_all_memory(
        current_user,
        tipo=tipo,
        min_importancia=min_importancia,
        since_iso=since_iso,
        query=query,
        limit=limit,
        offset=offset,
    )
    return {"memory": memories}

@app.post("/memory")
async def save_memory(
    tipo: str,
    conteudo: str,
    importancia: int = 1,
    current_user: str = Depends(get_current_user)
):
    """Salva um novo item na memória"""
    memory_id = UserMemory.save_memory(current_user, tipo, conteudo, importancia)
    return {"id": memory_id, "status": "salvo com sucesso"}

@app.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str, current_user: str = Depends(get_current_user)):
    """Deleta um item da memória"""
    UserMemory.delete_memory(current_user, memory_id)
    return {"status": "deletado com sucesso"}


@app.post("/memory/curate")
async def curate_memory(
    older_than_days: int = 90,
    similarity_threshold: float = 0.8,
    keep_top: int = 3,
    current_user: str = Depends(get_current_user)
):
    """Enfileira um job de curadoria em background (RQ). Retorna `job_id`.

    Requer Redis/RQ worker em execução para processar o job.
    """
    from rq import Queue
    from redis import Redis
    from config import get_settings

    settings = get_settings()
    redis_url = os.getenv('REDIS_URL', getattr(settings, 'REDIS_URL', 'redis://localhost:6379'))
    redis_conn = Redis.from_url(redis_url)
    q = Queue(connection=redis_conn)

    params = {
        'older_than_days': older_than_days,
        'similarity_threshold': similarity_threshold,
        'keep_top': keep_top,
    }

    # Cria job de curadoria no banco
    job_id = UserMemory.create_curation_job(current_user, params)

    # Enfileira worker para processar o job
    q.enqueue('memory.process_curate_job', job_id)

    return {"status": "queued", "job_id": job_id}


@app.get('/memory/curation_jobs')
async def list_curation_jobs(current_user: str = Depends(get_current_user)):
    db = get_db()
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, params, status, summary, candidate_ids, created_at, updated_at FROM curation_jobs WHERE user_id = %s ORDER BY created_at DESC",
                (current_user,)
            )
            jobs = []
            for row in cur.fetchall():
                jobs.append({
                    'id': row[0],
                    'params': row[1],
                    'status': row[2],
                    'summary': row[3],
                    'candidate_ids': row[4],
                    'created_at': row[5].isoformat() if row[5] else None,
                    'updated_at': row[6].isoformat() if row[6] else None,
                })
            return {'jobs': jobs}


@app.post('/memory/curation_jobs/{job_id}/approve')
async def approve_curation_job(job_id: str, current_user: str = Depends(get_current_user)):
    """Aprova a curadoria (insere resumo e remove candidatos)."""
    # Finaliza job
    result = UserMemory.finalize_curation_job(job_id, approve=True)
    return result


@app.post('/memory/curation_jobs/{job_id}/reject')
async def reject_curation_job(job_id: str, current_user: str = Depends(get_current_user)):
    """Rejeita a curadoria (marca como rejeitado)."""
    result = UserMemory.finalize_curation_job(job_id, approve=False)
    return result

# ==================== ROTAS DE PERFIL ====================

@app.post("/profile/persona")
async def set_persona(persona: str, current_user: str = Depends(get_current_user)):
    """Define a persona (tom) da ALICI para o usuário"""
    try:
        UserPreferences.save_persona(current_user, persona)
        return {"status": "persona atualizada", "persona": persona}
    except ValueError as e:
        raise HTTPException(400, str(e))

# ==================== ROTAS DE SAÚDE ====================

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "online",
        "timestamp": datetime.utcnow().isoformat()
    }

# ==================== INCLUIR ROTAS DE AUTH ====================

app.include_router(auth_router)

# ==================== EXECUTAR ====================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
