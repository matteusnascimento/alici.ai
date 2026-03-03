"""User repository for database operations."""

from database import atualizar_perfil, buscar_usuario_por_email, buscar_usuario_por_id, criar_usuario


class UserRepository:
    def find_by_email(self, email: str):
        return buscar_usuario_por_email(email)

    def find_by_id(self, user_id: int):
        return buscar_usuario_por_id(user_id)

    def create(self, nome: str, email: str, senha_hash: str, plano: str = "free"):
        return criar_usuario(nome, email, senha_hash, plano)

    def update_profile(
        self,
        user_id: int,
        nome: str | None = None,
        senha_hash: str | None = None,
        foto_url: str | None = None,
        tema: str | None = None,
    ) -> bool:
        return atualizar_perfil(user_id, nome=nome, senha_hash=senha_hash, foto_url=foto_url, tema=tema)
