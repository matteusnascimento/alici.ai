"""User repository for database operations."""

from database import buscar_usuario_por_email, buscar_usuario_por_id, criar_usuario


class UserRepository:
    def find_by_email(self, email: str):
        return buscar_usuario_por_email(email)

    def find_by_id(self, user_id: int):
        return buscar_usuario_por_id(user_id)

    def create(self, nome: str, email: str, senha_hash: str, plano: str = "free"):
        return criar_usuario(nome, email, senha_hash, plano)
