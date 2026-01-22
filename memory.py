"""
memory.py - Sistema de memória por usuário
"""
from database_models import get_db
from embeddings import embed_text, embed_texts, similarity
import json
import os
from typing import Any
try:
    import openai
except Exception:
    openai = None
import uuid
from datetime import datetime
from typing import List, Dict, Optional

class UserMemory:
    """Gerencia memória persistente do usuário"""
    
    @staticmethod
    def save_memory(user_id: str, tipo: str, conteudo: str, importancia: int = 1):
        """Salva um item na memória do usuário"""
        db = get_db()
        embedding = embed_text(conteudo)
        memory_id = str(uuid.uuid4())
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO user_memory (id, user_id, tipo, conteudo, embedding, importancia)
                    VALUES (%s, %s, %s, %s, %s::vector, %s)
                    """,
                    (memory_id, user_id, tipo, conteudo, embedding, importancia)
                )
                conn.commit()
        
        return memory_id
    
    @staticmethod
    def get_relevant_memory(user_id: str, query: str, limit: int = 5) -> List[Dict]:
        """Busca memórias relevantes usando similaridade de embeddings"""
        db = get_db()
        query_embedding = embed_text(query)
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                # Busca usando similaridade vetorial
                cur.execute(
                    """
                    SELECT id, tipo, conteudo, importancia, 
                           embedding <-> %s::vector as distancia
                    FROM user_memory
                    WHERE user_id = %s
                    ORDER BY distancia ASC
                    LIMIT %s
                    """,
                    (query_embedding, user_id, limit)
                )
                
                results = []
                for row in cur.fetchall():
                    results.append({
                        "id": row[0],
                        "tipo": row[1],
                        "conteudo": row[2],
                        "importancia": row[3],
                        "similaridade": 1 - row[4]  # converte distância em similaridade
                    })
                
                return results
    
    @staticmethod
    def get_all_memory(
        user_id: str,
        tipo: Optional[str] = None,
        min_importancia: Optional[int] = None,
        since_iso: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict]:
        """Retorna memórias do usuário com filtros e opcional busca semântica.

        - `tipo`: filtra por tipo de memória
        - `min_importancia`: filtra por importância mínima
        - `since_iso`: ISO timestamp para retornar memórias criadas depois dessa data
        - `query`: se fornecido, faz busca semântica (usa embeddings) e ordena por similaridade
        """
        db = get_db()

        # Se foi enviada uma query semântica, use busca vetorial
        if query:
            query_embedding = embed_text(query)
            with db.get_connection() as conn:
                with conn.cursor() as cur:
                    # Monta cláusula WHERE base
                    where_clauses = ["user_id = %s"]
                    params = [user_id]

                    if tipo:
                        where_clauses.append("tipo = %s")
                        params.append(tipo)
                    if min_importancia is not None:
                        where_clauses.append("importancia >= %s")
                        params.append(min_importancia)
                    if since_iso:
                        where_clauses.append("criado_em >= %s")
                        params.append(since_iso)

                    where_sql = " AND ".join(where_clauses)

                    cur.execute(
                        f"""
                        SELECT id, tipo, conteudo, importancia, criado_em,
                               embedding <-> %s::vector as distancia
                        FROM user_memory
                        WHERE {where_sql}
                        ORDER BY distancia ASC
                        LIMIT %s OFFSET %s
                        """,
                        tuple([query_embedding] + params + [limit, offset])
                    )

                    results = []
                    for row in cur.fetchall():
                        results.append({
                            "id": row[0],
                            "tipo": row[1],
                            "conteudo": row[2],
                            "importancia": row[3],
                            "criado_em": row[4].isoformat(),
                            "similaridade": 1 - row[5]
                        })

                    return results

        # Caso sem query semântica, usa filtros SQL simples
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                where_clauses = ["user_id = %s"]
                params = [user_id]

                if tipo:
                    where_clauses.append("tipo = %s")
                    params.append(tipo)
                if min_importancia is not None:
                    where_clauses.append("importancia >= %s")
                    params.append(min_importancia)
                if since_iso:
                    where_clauses.append("criado_em >= %s")
                    params.append(since_iso)

                where_sql = " AND ".join(where_clauses)

                cur.execute(
                    f"""
                    SELECT id, tipo, conteudo, importancia, criado_em
                    FROM user_memory
                    WHERE {where_sql}
                    ORDER BY importancia DESC, criado_em DESC
                    LIMIT %s OFFSET %s
                    """,
                    tuple(params + [limit, offset])
                )

                results = []
                for row in cur.fetchall():
                    results.append({
                        "id": row[0],
                        "tipo": row[1],
                        "conteudo": row[2],
                        "importancia": row[3],
                        "criado_em": row[4].isoformat()
                    })

                return results
    
    @staticmethod
    def delete_memory(user_id: str, memory_id: str):
        """Deleta um item da memória"""
        db = get_db()
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM user_memory WHERE id = %s AND user_id = %s",
                    (memory_id, user_id)
                )
                conn.commit()
    
    @staticmethod
    def update_memory_importance(user_id: str, memory_id: str, importancia: int):
        """Atualiza a importância de um item"""
        db = get_db()
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE user_memory 
                    SET importancia = %s, atualizado_em = NOW()
                    WHERE id = %s AND user_id = %s
                    """,
                    (importancia, memory_id, user_id)
                )
                conn.commit()

    @staticmethod
    def create_curation_job(user_id: str, params: Dict[str, Any]) -> str:
        """Cria um registro de job de curadoria com status 'pending'. Retorna job_id."""
        db = get_db()
        job_id = str(uuid.uuid4())
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO curation_jobs (id, user_id, params, status)
                    VALUES (%s, %s, %s::jsonb, %s)
                    """,
                    (job_id, user_id, json.dumps(params), 'pending')
                )
                conn.commit()

        return job_id

    def update_curation_job(job_id: str, status: str, summary: Optional[str] = None, candidate_ids: Optional[List[str]] = None):
        db = get_db()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE curation_jobs
                    SET status = %s, summary = %s, candidate_ids = %s, updated_at = NOW()
                    WHERE id = %s
                    """,
                    (status, summary, candidate_ids, job_id)
                )
                conn.commit()

    def process_curate_job(job_id: str):
        """Executado pelo worker: processa o job de curadoria e grava resumo (status -> ready)."""
        from datetime import datetime, timedelta

        db = get_db()

        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id, params FROM curation_jobs WHERE id = %s", (job_id,))
                row = cur.fetchone()
                if not row:
                    return {"error": "job not found"}

                user_id = row[0]
                params = row[1] or {}

                older_than_days = int(params.get('older_than_days', 90))
                similarity_threshold = float(params.get('similarity_threshold', 0.8))
                keep_top = int(params.get('keep_top', 3))

                cutoff = datetime.utcnow() - timedelta(days=older_than_days)

                cur.execute(
                    """
                    SELECT id, tipo, conteudo, importancia, criado_em
                    FROM user_memory
                    WHERE user_id = %s AND criado_em < %s
                    ORDER BY criado_em ASC
                    """,
                    (user_id, cutoff)
                )

                rows = cur.fetchall()
                if not rows:
                    UserMemory.update_curation_job(job_id, status='ready', summary=None, candidate_ids=[])
                    return {"curated": 0}

                contents = [r[2] for r in rows]
                ids = [r[0] for r in rows]

                embeddings = embed_texts(contents)

                clusters = []
                for idx, emb in enumerate(embeddings):
                    placed = False
                    for c in clusters:
                        rep_idx = c[0]
                        sim = similarity(embeddings[rep_idx], emb)
                        if sim >= similarity_threshold:
                            c.append(idx)
                            placed = True
                            break
                    if not placed:
                        clusters.append([idx])

                summaries = []
                affected_ids = []

                for c in clusters:
                    if len(c) == 1:
                        continue

                    members = sorted(c, key=lambda i: rows[i][3], reverse=True)
                    to_keep = members[:keep_top]
                    to_remove = members[keep_top:]

                    removed_texts = [contents[i] for i in to_remove]

                    # Gera resumo via LLM se disponível, senão concatena
                    summary_text = None
                    if openai and os.getenv('OPENAI_API_KEY'):
                        try:
                            openai.api_key = os.getenv('OPENAI_API_KEY')
                            prompt = "Summarize the following texts into a concise Portuguese summary:\n\n" + "\n---\n".join(removed_texts)
                            resp = openai.ChatCompletion.create(
                                model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                                messages=[{"role":"user","content":prompt}],
                                max_tokens=512,
                                temperature=0.2
                            )
                            summary_text = resp['choices'][0]['message']['content'].strip()
                        except Exception:
                            summary_text = "\n---\n".join(removed_texts)[:4000]
                    else:
                        summary_text = "\n---\n".join(removed_texts)[:4000]

                    summaries.append(summary_text)
                    affected_ids.extend([ids[i] for i in to_remove])

                # Store job result as 'ready' with candidate ids
                UserMemory.update_curation_job(job_id, status='ready', summary='\n\n'.join(summaries)[:8000], candidate_ids=affected_ids)

                return {"curated": len(affected_ids), "candidates": affected_ids}

    def finalize_curation_job(job_id: str, approve: bool = True) -> Dict:
        """Se aprovado, insere o resumo em `user_memory` e remove os candidatos; atualiza status."""
        db = get_db()
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id, summary, candidate_ids FROM curation_jobs WHERE id = %s", (job_id,))
                row = cur.fetchone()
                if not row:
                    return {"error": "job not found"}
                user_id, summary, candidate_ids = row[0], row[1], row[2] or []

                if not approve:
                    UserMemory.update_curation_job(job_id, status='rejected')
                    return {"status": "rejected"}

                # Inserir resumo como memória
                summary_id = str(uuid.uuid4())
                cur.execute(
                    """
                    INSERT INTO user_memory (id, user_id, tipo, conteudo, embedding, importancia)
                    VALUES (%s, %s, %s, %s, %s::vector, %s)
                    """,
                    (summary_id, user_id, 'curated', summary, embed_text(summary), 5)
                )

                # Deleta candidatos
                if candidate_ids:
                    cur.execute("DELETE FROM user_memory WHERE id = ANY(%s)", (candidate_ids,))

                UserMemory.update_curation_job(job_id, status='approved')
                conn.commit()

                return {"status": "approved", "summary_id": summary_id}


class UserPreferences:
    """Gerencia preferências e perfil do usuário"""
    
    PERSONAS = {
        "tecnico": "Focado em precisão, dados e lógica",
        "mentor": "Orientador, paciente, educador",
        "espiritual": "Profundo, reflexivo, filosófico",
        "motivacional": "Agressivo, direto, inspirador"
    }
    
    @staticmethod
    def save_persona(user_id: str, persona: str):
        """Salva a persona escolhida pelo usuário"""
        if persona not in UserPreferences.PERSONAS:
            raise ValueError(f"Persona inválida: {persona}")
        
        UserMemory.save_memory(
            user_id,
            tipo="persona",
            conteudo=f"Prefere tom {persona}: {UserPreferences.PERSONAS[persona]}",
            importancia=10  # Muito importante
        )
    
    @staticmethod
    def get_persona_prompt(user_id: str) -> str:
        """Retorna instrução de sistema baseada na persona do usuário"""
        memories = UserMemory.get_all_memory(user_id)
        persona_memories = [m for m in memories if m["tipo"] == "persona"]
        
        if persona_memories:
            return persona_memories[0]["conteudo"]
        
        return "Você é a ALICI™, uma inteligência artificial com identidade e memória."
