"""
embeddings.py - Geração e gerenciamento de embeddings para RAG
"""
from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from config import get_settings

settings = get_settings()

# Carrega modelo de embeddings (executa uma vez ao iniciar)
model = None

def init_embeddings():
    """Inicializa o modelo de embeddings"""
    global model
    if model is None:
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        model = SentenceTransformer(settings.EMBEDDING_MODEL)
    return model

def get_embeddings_model():
    """Retorna o modelo carregado"""
    global model
    if model is None:
        model = init_embeddings()
    return model

def embed_text(text: str) -> List[float]:
    """Gera embedding para um texto"""
    model = get_embeddings_model()
    embedding = model.encode(text, convert_to_tensor=False)
    return embedding.tolist()

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Gera embeddings para múltiplos textos"""
    model = get_embeddings_model()
    embeddings = model.encode(texts, convert_to_tensor=False)
    return [e.tolist() for e in embeddings]

def similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Calcula similaridade cosseno entre dois embeddings"""
    a = np.array(embedding1)
    b = np.array(embedding2)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def similar_embeddings(query_embedding: List[float], candidates: List[List[float]], top_k: int = 5) -> List[int]:
    """Retorna os índices dos embeddings mais similares"""
    similarities = [similarity(query_embedding, cand) for cand in candidates]
    indices = np.argsort(similarities)[::-1][:top_k].tolist()
    return indices
