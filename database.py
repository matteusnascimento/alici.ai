"""
database.py
Conexão com PostgreSQL (Neon) ou SQLite e operações de banco de dados
"""

import os
import sqlite3
from contextlib import contextmanager
from dotenv import load_dotenv
from logger import get_logger

# Configurar logger
logger_db = get_logger("database")

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_ENABLED = bool(DATABASE_URL)

# Detectar tipo de banco
USE_SQLITE = DATABASE_URL and DATABASE_URL.startswith("sqlite")
USE_POSTGRES = DATABASE_URL and DATABASE_URL.startswith("postgresql")

if not DATABASE_ENABLED:
    logger_db.warning("⚠️  DATABASE_URL não configurado - funcionalidades de banco desabilitadas")
elif USE_SQLITE:
    logger_db.info(f"🗄️  Usando SQLite: {DATABASE_URL.replace('sqlite:///', '')}")
elif USE_POSTGRES:
    import psycopg2
    logger_db.info("🗄️  Usando PostgreSQL/Neon")
else:
    logger_db.error(f"❌ DATABASE_URL inválido: {DATABASE_URL}")
    DATABASE_ENABLED = False


def conectar():
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco de dados não configurado")
    
    if USE_SQLITE:
        db_path = DATABASE_URL.replace("sqlite:///", "")
        return sqlite3.connect(db_path)
    elif USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL, sslmode="require")
    else:
        raise RuntimeError("Tipo de banco não suportado")


@contextmanager
def get_db_connection():
    """
    Context manager para conexão com banco de dados
    Suporta PostgreSQL e SQLite
    """
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco de dados não configurado")
    
    if USE_SQLITE:
        db_path = DATABASE_URL.replace("sqlite:///", "")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
    elif USE_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    else:
        raise RuntimeError("Tipo de banco não suportado")
    
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def criar_tabelas():
    """
    Cria as tabelas necessárias no banco de dados
    Compatível com PostgreSQL e SQLite
    """
    if not DATABASE_ENABLED:
        logger_db.warning("Banco não configurado - pulando criação de tabelas")
        return
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        # Sintaxe diferente para PRIMARY KEY AUTO INCREMENT
        if USE_SQLITE:
            id_field = "INTEGER PRIMARY KEY AUTOINCREMENT"
            timestamp_field = "DATETIME DEFAULT CURRENT_TIMESTAMP"
        else:  # PostgreSQL
            id_field = "SERIAL PRIMARY KEY"
            timestamp_field = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        
        # Tabela de memória
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS memoria (
                id {id_field},
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL,
                confianca INTEGER DEFAULT 1,
                criado_em {timestamp_field}
            )
        """)

        # Tabela de usuários
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                id {id_field},
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                plano TEXT DEFAULT 'free',
                criado_em {timestamp_field},
                atualizado_em {timestamp_field}
            )
        """)

        # Tabela de histórico
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS history (
                id {id_field},
                user_id INTEGER NOT NULL,
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL,
                criado_em {timestamp_field},
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Índices
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_memoria_pergunta
            ON memoria (pergunta)
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_history_user_id ON history(user_id)
        """)
        
        cur.close()
        logger_db.info("✅ Tabelas criadas com sucesso")



def buscar_memoria(pergunta):
    """
    Busca resposta na memória usando context manager
    Garante fechamento correto de conexão mesmo em caso de erro
    """
    if not DATABASE_ENABLED:
        return None
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"
            
            cur.execute(f"""
                SELECT resposta
                FROM memoria
                WHERE pergunta = {placeholder}
                ORDER BY confianca DESC
                LIMIT 1
            """, (pergunta.lower(),))

            r = cur.fetchone()
            cur.close()
            return r[0] if r else None

    except Exception as e:
        logger_db.error(f"Erro ao buscar memória: {e}")
        return None


def aprender(pergunta, resposta):
    """
    Aprende armazenando pergunta/resposta ou incrementando confiança
    Usa context manager para gerenciar conexão com segurança
    """
    if not DATABASE_ENABLED:
        return
    
    try:
        with get_db_connection() as conn:
            cur = conn.cursor()
            placeholder = "?" if USE_SQLITE else "%s"
            
            cur.execute(f"""
                SELECT id FROM memoria
                WHERE pergunta = {placeholder} AND resposta = {placeholder}
            """, (pergunta.lower(), resposta))

            existe = cur.fetchone()

            if existe:
                cur.execute(f"""
                    UPDATE memoria
                    SET confianca = confianca + 1
                    WHERE id = {placeholder}
                """, (existe[0],))
            else:
                cur.execute(f"""
                    INSERT INTO memoria (pergunta, resposta)
                    VALUES ({placeholder}, {placeholder})
                """, (pergunta.lower(), resposta))
            
            cur.close()

    except Exception as e:
        logger_db.error(f"Erro ao aprender: {e}")


def salvar_interacao(pergunta, resposta):
    """
    Salva qualquer interação, mesmo quando não há aprendizado.
    """
    aprender(pergunta, resposta)


# ============================================================================
# OPERAÇÕES DE USUÁRIO
# ============================================================================

def criar_usuario(nome: str, email: str, senha_hash: str, plano: str = "free") -> dict:
    if not DATABASE_ENABLED:
        raise RuntimeError("Banco de dados não configurado")
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        placeholder = "?" if USE_SQLITE else "%s"
        
        try:
            if USE_SQLITE:
                cur.execute(f"""
                    INSERT INTO users (nome, email, senha_hash, plano)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
                """, (nome, email, senha_hash, plano))
                user_id = cur.lastrowid
                
                cur.execute(f"SELECT id, nome, email, plano, criado_em FROM users WHERE id = {placeholder}", (user_id,))
                resultado = cur.fetchone()
            else:  # PostgreSQL
                cur.execute(f"""
                    INSERT INTO users (nome, email, senha_hash, plano)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
                    RETURNING id, nome, email, plano, criado_em
                """, (nome, email, senha_hash, plano))
                resultado = cur.fetchone()

            cur.close()
            
            if resultado:
                return {
                    "id": resultado[0],
                    "nome": resultado[1],
                    "email": resultado[2],
                    "plano": resultado[3],
                    "criado_em": resultado[4]
                }
        except (sqlite3.IntegrityError if USE_SQLITE else Exception) as e:
            cur.close()
            if "UNIQUE" in str(e) or "unique" in str(e):
                raise ValueError("Email já está registrado")
            raise Exception(f"Erro ao criar usuário: {str(e)}")


def buscar_usuario_por_email(email: str) -> dict:
    if not DATABASE_ENABLED:
        return None
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        placeholder = "?" if USE_SQLITE else "%s"
        
        cur.execute(
            f"SELECT id, nome, email, senha_hash, plano FROM users WHERE email = {placeholder}",
            (email,)
        )
        resultado = cur.fetchone()
        cur.close()

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
    if not DATABASE_ENABLED:
        return None
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        placeholder = "?" if USE_SQLITE else "%s"
        
        cur.execute(
            f"SELECT id, nome, email, plano FROM users WHERE id = {placeholder}",
            (user_id,)
        )
        resultado = cur.fetchone()
        cur.close()

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
    if not DATABASE_ENABLED:
        return None
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        placeholder = "?" if USE_SQLITE else "%s"
        
        if USE_SQLITE:
            cur.execute(f"""
                INSERT INTO history (user_id, pergunta, resposta)
                VALUES ({placeholder}, {placeholder}, {placeholder})
            """, (user_id, pergunta, resposta))
            history_id = cur.lastrowid
            
            cur.execute(f"SELECT id, user_id, pergunta, resposta, criado_em FROM history WHERE id = {placeholder}", (history_id,))
            resultado = cur.fetchone()
        else:  # PostgreSQL
            cur.execute(f"""
                INSERT INTO history (user_id, pergunta, resposta)
                VALUES ({placeholder}, {placeholder}, {placeholder})
                RETURNING id, user_id, pergunta, resposta, criado_em
            """, (user_id, pergunta, resposta))
            resultado = cur.fetchone()
        
        cur.close()

        if resultado:
            return {
                "id": resultado[0],
                "user_id": resultado[1],
                "pergunta": resultado[2],
                "resposta": resultado[3],
                "criado_em": resultado[4]
            }


def buscar_historico(user_id: int, limite: int = 50) -> list:
    if not DATABASE_ENABLED:
        return []
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        placeholder = "?" if USE_SQLITE else "%s"
        
        cur.execute(f"""
            SELECT id, pergunta, resposta, criado_em
            FROM history
            WHERE user_id = {placeholder}
            ORDER BY criado_em DESC
            LIMIT {placeholder}
        """, (user_id, limite))
        resultados = cur.fetchall()
        cur.close()

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
    if not DATABASE_ENABLED:
        return False
    
    with get_db_connection() as conn:
        cur = conn.cursor()
        placeholder = "?" if USE_SQLITE else "%s"
        
        cur.execute(f"DELETE FROM history WHERE user_id = {placeholder}", (user_id,))
        cur.close()
        return True