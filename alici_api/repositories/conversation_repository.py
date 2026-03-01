"""Conversation repository for multi-chat management."""

from database import (
    adicionar_mensagem_conversa,
    buscar_conversa,
    criar_conversa,
    deletar_conversa,
    listar_conversas,
    listar_mensagens_conversa,
    renomear_conversa,
)


class ConversationRepository:
    def create(self, user_id: int, titulo: str = "Nova conversa"):
        return criar_conversa(user_id, titulo)

    def list(self, user_id: int, limit: int = 50):
        return listar_conversas(user_id, limit)

    def get(self, conv_id: int, user_id: int):
        return buscar_conversa(conv_id, user_id)

    def delete(self, conv_id: int, user_id: int) -> bool:
        return deletar_conversa(conv_id, user_id)

    def rename(self, conv_id: int, user_id: int, titulo: str) -> bool:
        return renomear_conversa(conv_id, user_id, titulo)

    def add_message(self, conv_id: int, role: str, content: str):
        return adicionar_mensagem_conversa(conv_id, role, content)

    def list_messages(self, conv_id: int):
        return listar_mensagens_conversa(conv_id)
