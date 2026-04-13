from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.integration import (
    IntegrationAccountCreateRequest,
    IntegrationAccountRead,
    IntegrationProviderRead,
    IntegrationProviderStatusRead,
    IntegrationTestRequest,
    IntegrationTestResponse,
)
from app.services.ai_service import AIConfigurationError, AIService, AIServiceError
from app.services.channel_integration_service import ChannelIntegrationService

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("", response_model=list[IntegrationProviderRead])
def list_integrations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[IntegrationProviderRead]:
    rows = ChannelIntegrationService(db).list_integrations(current_user)
    return [IntegrationProviderRead(**item) for item in rows]


@router.post("", response_model=IntegrationAccountRead)
def create_integration(
    payload: IntegrationAccountCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationAccountRead:
    svc = ChannelIntegrationService(db)
    account = svc.create_integration_account(current_user, payload.model_dump())
    return IntegrationAccountRead(
        id=account.id,
        provider=account.provider,
        external_account_id=account.external_account_id,
        external_account_name=account.external_account_name,
        status=account.status,
        metadata=svc._load_json(account.metadata_json),
        created_at=account.created_at,
        updated_at=account.updated_at,
    )


@router.get("/accounts", response_model=list[IntegrationAccountRead])
def list_accounts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[IntegrationAccountRead]:
    svc = ChannelIntegrationService(db)
    accounts = svc.list_accounts(current_user)
    return [
        IntegrationAccountRead(
            id=a.id,
            provider=a.provider,
            external_account_id=a.external_account_id,
            external_account_name=a.external_account_name,
            status=a.status,
            metadata=svc._load_json(a.metadata_json),
            created_at=a.created_at,
            updated_at=a.updated_at,
        )
        for a in accounts
    ]


@router.get("/{provider}/status", response_model=IntegrationProviderStatusRead)
def get_provider_status(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationProviderStatusRead:
    return IntegrationProviderStatusRead(**ChannelIntegrationService(db).get_provider_status(current_user, provider))


@router.post("/{provider}/disconnect", response_model=IntegrationProviderStatusRead)
def disconnect_provider(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationProviderStatusRead:
    return IntegrationProviderStatusRead(**ChannelIntegrationService(db).disconnect_provider(current_user, provider))


def _run_openai_healthcheck() -> IntegrationTestResponse:
    service = AIService(provider="openai")
    try:
        result = service.healthcheck()
        status = result.get("status", "error")
        model = result.get("model")
        latency_ms = result.get("latency_ms")
        error_type = result.get("error_type")
        result_status_code = result.get("status_code")
        message = result.get("message", "Falha ao validar OpenAI")
        if status == "ok" and model:
            message = "OpenAI integration is working."
        return IntegrationTestResponse(
            provider="openai",
            status=status,
            message=message,
            model=model,
            model_used=model,
            latency_ms=latency_ms,
            error_type=error_type,
            status_code=result_status_code,
        )
    except AIConfigurationError:
        return IntegrationTestResponse(
            provider="openai",
            status="warning",
            message="A chave da OpenAI nao foi encontrada no ambiente.",
            model=None,
            model_used=None,
            error_type="missing_api_key",
            status_code=503,
        )
    except AIServiceError as exc:
        return IntegrationTestResponse(
            provider="openai",
            status="error",
            message=exc.user_message,
            model=None,
            model_used=None,
            error_type=exc.code,
            status_code=exc.status_code,
        )


@router.get("/openai/test", response_model=IntegrationTestResponse)
def test_openai_get(__: User = Depends(get_current_user)) -> IntegrationTestResponse:
    return _run_openai_healthcheck()


@router.post("/openai/test", response_model=IntegrationTestResponse)
def test_openai(
    _: IntegrationTestRequest,
    __: User = Depends(get_current_user),
) -> IntegrationTestResponse:
    return _run_openai_healthcheck()


@router.post("/whatsapp/test", response_model=IntegrationTestResponse)
def test_whatsapp(
    _: IntegrationTestRequest,
    __: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationTestResponse:
    summary = ChannelIntegrationService(db).get_provider_status(__, "whatsapp")
    return IntegrationTestResponse(
        provider="whatsapp",
        status=summary["status"],
        message=summary["helper_text"],
    )


@router.post("/instagram/test", response_model=IntegrationTestResponse)
def test_instagram(
    _: IntegrationTestRequest,
    __: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationTestResponse:
    summary = ChannelIntegrationService(db).get_provider_status(__, "instagram")
    return IntegrationTestResponse(
        provider="instagram",
        status=summary["status"],
        message=summary["helper_text"],
    )
