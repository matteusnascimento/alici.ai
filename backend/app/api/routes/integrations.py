from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.config import settings
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


@router.get("/meta/webhook")
async def verify_meta_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
) -> PlainTextResponse:
    expected_token = settings.meta_webhook_verify_token
    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="META_WEBHOOK_VERIFY_TOKEN nao configurado no servidor.",
        )
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        return PlainTextResponse(content=str(hub_challenge or ""))
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token de webhook invalido.")


@router.post("/meta/webhook")
async def receive_meta_webhook(request: Request) -> dict[str, str]:
    await request.json()
    return {"status": "received"}


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
    return IntegrationAccountRead(**svc._serialize_account(account))


@router.get("/accounts", response_model=list[IntegrationAccountRead])
def list_accounts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[IntegrationAccountRead]:
    svc = ChannelIntegrationService(db)
    accounts = svc.list_accounts(current_user)
    return [IntegrationAccountRead(**svc._serialize_account(a)) for a in accounts]


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
