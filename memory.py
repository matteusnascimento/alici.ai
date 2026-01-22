"""
memory.py - Sistema de memória por usuário
"""
from database_models import get_db
from embeddings import embed_text
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
    def get_all_memory(user_id: str) -> List[Dict]:
        """Retorna toda a memória do usuário"""
        db = get_db()
        
        with db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, tipo, conteudo, importancia, criado_em
                    FROM user_memory
                    WHERE user_id = %s
                    ORDER BY importancia DESC, criado_em DESC
                    """,
                    (user_id,)
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
