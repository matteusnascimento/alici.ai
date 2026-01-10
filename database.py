import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    return psycopg2.connect(DATABASE_URL)

def buscar_resposta(pergunta):
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
    except Exception as e:
        print(f"Erro ao buscar resposta: {e}")
        return None

def salvar_interacao(pergunta, resposta):
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
    except Exception as e:
        print(f"Erro ao salvar interação: {e}")

# Função para inicializar o banco de dados (caso as tabelas não existam)
def inicializar_banco():
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
        print("Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")