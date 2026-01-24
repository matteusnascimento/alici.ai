"""
database.py
Conexão com PostgreSQL (Neon) e operações de banco de dados
"""

import os
import psycopg
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL não configurado em .env")

# ============================================================================
# GERENCIADOR DE CONEXÃO
# ============================================================================

@contextmanager
def get_db_connection():
    """
    Context manager para conexão com banco de dados
    
    Yields:
        Conexão psycopg
    """
    conn = psycopg.connect(DATABASE_URL, autocommit=False)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# ============================================================================
# OPERAÇÕES DE USUÁRIO
# ============================================================================

def criar_usuario(nome: str, email: str, senha_hash: str, plano: str = "free") -> dict:
    """
    Cria novo usuário no banco de dados
    
    Args:
        nome: Nome completo
        email: Email único
        senha_hash: Hash bcrypt da senha
        plano: "free" ou "pro" (default: "free")
    
    Returns:
        Dicionário com dados do usuário criado
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO users (nome, email, senha_hash, plano)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, nome, email, plano, criado_em
                    """,
                    (nome, email, senha_hash, plano)
                )
                resultado = cur.fetchone()
                
                if resultado:
                    return {
                        "id": resultado[0],
                        "nome": resultado[1],
                        "email": resultado[2],
                        "plano": resultado[3],
                        "criado_em": resultado[4]
                    }
            except psycopg.errors.UniqueViolation:
                raise ValueError("Email já está registrado")
            except Exception as e:
                raise Exception(f"Erro ao criar usuário: {str(e)}")


def buscar_usuario_por_email(email: str) -> dict:
    """
    Busca usuário pelo email
    
    Args:
        email: Email do usuário
    
    Returns:
        Dicionário com dados do usuário ou None
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, email, senha_hash, plano FROM users WHERE email = %s",
                (email,)
            )
            resultado = cur.fetchone()
            
            if resultado:
                return {
                    "id": resultado[0],
                    "nome": resultado[1],
                    "email": resultado[2],
                    "senha_hash": resultado[3],
                    "plano": resultado[4]
                }
            return None


def buscar_usuario_por_id(user_id: int) -> dict:
    """
    Busca usuário pelo ID
    
    Args:
        user_id: ID do usuário
    
    Returns:
        Dicionário com dados do usuário ou None
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, nome, email, plano FROM users WHERE id = %s",
                (user_id,)
            )
            resultado = cur.fetchone()
            
            if resultado:
                return {
                    "id": resultado[0],
                    "nome": resultado[1],
                    "email": resultado[2],
                    "plano": resultado[3]
                }
            return None


# ============================================================================
# OPERAÇÕES DE HISTÓRICO
# ============================================================================

def salvar_historico(user_id: int, pergunta: str, resposta: str) -> dict:
    """
    Salva pergunta e resposta no histórico do usuário
    
    Args:
        user_id: ID do usuário
        pergunta: Pergunta feita
        resposta: Resposta gerada
    
    Returns:
        Dicionário com dados salvos
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO history (user_id, pergunta, resposta)
                VALUES (%s, %s, %s)
                RETURNING id, user_id, pergunta, resposta, criado_em
                """,
                (user_id, pergunta, resposta)
            )
            resultado = cur.fetchone()
            
            if resultado:
                return {
                    "id": resultado[0],
                    "user_id": resultado[1],
                    "pergunta": resultado[2],
                    "resposta": resultado[3],
                    "criado_em": resultado[4]
                }


def buscar_historico(user_id: int, limite: int = 50) -> list:
    """
    Busca histórico do usuário
    
    Args:
        user_id: ID do usuário
        limite: Número máximo de registros (default: 50)
    
    Returns:
        Lista de dicionários com histórico
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, pergunta, resposta, criado_em
                FROM history
                WHERE user_id = %s
                ORDER BY criado_em DESC
                LIMIT %s
                """,
                (user_id, limite)
            )
            resultados = cur.fetchall()
            
            return [
                {
                    "id": r[0],
                    "pergunta": r[1],
                    "resposta": r[2],
                    "criado_em": r[3]
                }
                for r in resultados
            ]


def limpar_historico(user_id: int) -> bool:
    """
    Limpa todo o histórico do usuário
    
    Args:
        user_id: ID do usuário
    
    Returns:
        True se sucesso
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM history WHERE user_id = %s", (user_id,))
            return True


# ============================================================================
# FUNÇÕES DE SETUP
# ============================================================================

def criar_tabelas():
    """
    Cria as tabelas necessárias no banco de dados
    Deve ser chamada uma única vez durante a inicialização
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Tabela de usuários
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    senha_hash TEXT NOT NULL,
                    plano TEXT DEFAULT 'free',
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de histórico
            cur.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id SERIAL PRIMARY KEY,
                    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    pergunta TEXT NOT NULL,
                    resposta TEXT NOT NULL,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Índices para performance
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_user_id ON history(user_id)
            """)
            
            print("✅ Tabelas criadas/verificadas com sucesso!")


if __name__ == "__main__":
    criar_tabelas()
