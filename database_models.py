"""
database_models.py - Modelos e operações do banco de dados
"""
import psycopg
from psycopg import sql
from datetime import datetime, timedelta
import uuid
from typing import Optional, List, Dict
import os

class Database:
    """Gerenciador de conexões e operações com Neon/PostgreSQL"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
    
    def get_connection(self):
        """Conecta ao banco"""
        return psycopg.connect(self.connection_string)
    
    def init_tables(self):
        """Cria as tabelas necessárias"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Extensões necessárias: UUIDs, geração de UUIDs e vetor (pgvector)
                cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
                cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
                
                # Tabela de usuários
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        nome TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        senha_hash TEXT NOT NULL,
                        plano TEXT DEFAULT 'free',
                        avatar_url TEXT,
                        criado_em TIMESTAMP DEFAULT NOW(),
                        atualizado_em TIMESTAMP DEFAULT NOW(),
                        ativo BOOLEAN DEFAULT TRUE
                    );
                """)
                
                # Tabela de sessões
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        token TEXT UNIQUE NOT NULL,
                        token_refresh TEXT,
                        criado_em TIMESTAMP DEFAULT NOW(),
                        expira_em TIMESTAMP NOT NULL,
                        expira_refresh_em TIMESTAMP,
                        ip TEXT,
                        dispositivo TEXT,
                        ativo BOOLEAN DEFAULT TRUE
                    );
                """)
                
                # Tabela de histórico de mensagens
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        pergunta TEXT NOT NULL,
                        resposta TEXT NOT NULL,
                        emocao TEXT,
                        tokens_usados INT DEFAULT 0,
                        tempo_resposta_ms INT,
                        criado_em TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                # Tabela de memória por usuário
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_memory (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        tipo TEXT NOT NULL,
                        conteudo TEXT NOT NULL,
                        embedding VECTOR(384),
                        importancia INT DEFAULT 1,
                        criado_em TIMESTAMP DEFAULT NOW(),
                        atualizado_em TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                # Tabela de documentos do usuário (para RAG)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_documents (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        nome TEXT NOT NULL,
                        tipo TEXT,
                        conteudo TEXT,
                        embedding VECTOR(384),
                        criado_em TIMESTAMP DEFAULT NOW()
                    );
                """)
                
                # Índices
                cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_memory_user_id ON user_memory(user_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_documents_user_id ON user_documents(user_id)")
                # Tabela de jobs de curadoria (pending -> ready -> approved/rejected)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS curation_jobs (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        params JSONB,
                        status TEXT DEFAULT 'pending',
                        summary TEXT,
                        candidate_ids UUID[],
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                cur.execute("CREATE INDEX IF NOT EXISTS idx_curation_user_id ON curation_jobs(user_id)")
                
                conn.commit()
                print("✅ Tabelas criadas com sucesso")

# Instância global
db = None

def init_db(connection_string: str):
    global db
    db = Database(connection_string)
    db.init_tables()
    return db

def get_db() -> Database:
    global db
    if db is None:
        db = Database(os.getenv("DATABASE_URL"))
    return db
