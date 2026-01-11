from database import conectar
from embedding import gerar_embedding

def salvar_interacao(pergunta, resposta):
    embedding = gerar_embedding(pergunta)

    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO conversas (pergunta, resposta, embedding)
        VALUES (%s, %s, %s)
    """, (pergunta, resposta, embedding))

    conn.commit()
    cur.close()
    conn.close()
