import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    """Conecta ao banco de dados PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        print(f"❌ Erro de conexão com PostgreSQL: {e}")
        raise
    except Exception as e:
        print(f"❌ Erro desconhecido na conexão: {e}")
        raise

def buscar_resposta(pergunta):
    """Busca uma resposta no banco de dados"""
    try:
        conn = conectar()
        cur = conn.cursor()

        cur.execute(
            "SELECT resposta FROM respostas WHERE perguntas ILIKE %s LIMIT 1",
            (pergunta,)
        )
        resultado = cur.fetchone()

        cur.close()
        conn.close()

        return resultado[0] if resultado else None
    except psycopg2.Error as e:
        print(f"❌ Erro no PostgreSQL ao buscar resposta: {e}")
        return None
    except Exception as e:
        print(f"❌ Erro desconhecido ao buscar resposta: {e}")
        return None

def salvar_interacao(pergunta, resposta):
    """Salva uma interação no banco de dados"""
    try:
        conn = conectar()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO respostas (perguntas, resposta) VALUES (%s, %s)",
            (pergunta, resposta)
        )

        conn.commit()
        cur.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"❌ Erro no PostgreSQL ao salvar interação: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ Erro desconhecido ao salvar interação: {e}")
        if conn:
            conn.rollback()

# Função para inicializar o banco de dados (caso as tabelas não existam)
def inicializar_banco():
    """Inicializa o banco de dados criando as tabelas necessárias"""
    try:
        conn = conectar()
        cur = conn.cursor()
        
        # Criar tabela se não existir
        cur.execute("""
            CREATE TABLE IF NOT EXISTS respostas (
                id SERIAL PRIMARY KEY,
                perguntas TEXT NOT NULL,
                resposta TEXT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Banco de dados inicializado com sucesso!")
        return True
    except psycopg2.Error as e:
        print(f"❌ Erro no PostgreSQL ao inicializar banco: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro desconhecido ao inicializar banco: {e}")
        return False