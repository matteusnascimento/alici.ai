from sqlalchemy.orm import Session

from app.models.integration import Integration
from app.models.user import User
from app.schemas.integration import IntegrationRead, IntegrationTestResponse


class IntegrationService:
    DEFAULTS = [
        ("openai", "OpenAI"),
        ("whatsapp", "WhatsApp"),
        ("instagram", "Instagram"),
    ]

    # Providers with real connectivity implemented in this legacy service.
    _LIVE_PROVIDERS: set[str] = set()

    def __init__(self, db: Session):
        self.db = db

    def list_integrations(self, user: User) -> list[IntegrationRead]:
        self._seed_defaults(user)
        rows = (
            self.db.query(Integration)
            .filter(Integration.user_id == user.id)
            .order_by(Integration.provider.asc())
            .all()
        )
        return [
            IntegrationRead(
                id=item.id,
                provider=item.provider,
                name=item.name,
                is_active=item.is_active,
                created_at=item.created_at,
            )
            for item in rows
        ]

    def test_provider(self, provider: str) -> IntegrationTestResponse:
        labels = {"openai": "OpenAI", "whatsapp": "WhatsApp", "instagram": "Instagram"}
        label = labels.get(provider, provider)

        if provider in self._LIVE_PROVIDERS:
            return IntegrationTestResponse(
                provider=provider,
                status="ok",
                message=f"Conexão com {label} validada com sucesso.",
            )

        return IntegrationTestResponse(
            provider=provider,
            status="error",
            message=(
                f"A integracao com {label} nao possui teste real neste endpoint legado. "
                "Use o fluxo atual de integracoes com credenciais reais."
            ),
            error_type="legacy_provider_not_available",
            status_code=501,
        )

    def _seed_defaults(self, user: User) -> None:
        existing = {
            item.provider
            for item in self.db.query(Integration).filter(Integration.user_id == user.id).all()
        }
        created = False
        for provider, name in self.DEFAULTS:
            if provider in existing:
                continue
            self.db.add(Integration(user_id=user.id, provider=provider, name=name, is_active=False))
            created = True

        if created:
            self.db.commit()
