class VectorSearch:
    def search(self, query_embedding: list[float], vectors: list[dict], top_k: int = 5) -> list[dict]:
        return vectors[:top_k]
