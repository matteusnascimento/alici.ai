"""History repository for chat history operations."""

from database import buscar_historico, limpar_historico, salvar_historico


class HistoryRepository:
    def save(self, user_id: int, pergunta: str, resposta: str) -> None:
        salvar_historico(user_id, pergunta, resposta)

    def list(self, user_id: int, limit: int = 50):
        return buscar_historico(user_id, limit)

    def clear(self, user_id: int) -> None:
        limpar_historico(user_id)
