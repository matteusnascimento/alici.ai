from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def gerar_embedding(texto: str):
    return model.encode(texto).tolist()

def similaridade(v1, v2):
    v1, v2 = np.array(v1), np.array(v2)
    return float(
        np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    )
