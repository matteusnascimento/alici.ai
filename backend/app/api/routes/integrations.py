import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import quote_plus, urlencode

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.integration import (
    IntegrationAccountCreateRequest,
    IntegrationAccountRead,
    IntegrationOAuthStartRequest,
    IntegrationOAuthStartResponse,
    IntegrationProviderRead,
    IntegrationProviderStatusRead,
    IntegrationQrStartRequest,
    IntegrationQrStartResponse,
    IntegrationTestRequest,
    IntegrationTestResponse,
)
from app.services.ai_service import AIConfigurationError, AIService, AIServiceError
from app.services.channel_integration_service import ChannelIntegrationService

router = APIRouter(prefix="/integrations", tags=["integrations"])

META_OAUTH_PROVIDERS = {"instagram"}
META_OAUTH_SCOPES = {
    "instagram": "instagram_basic,instagram_manage_messages,pages_show_list,pages_messaging,business_management",
}


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


@router.post("/{provider}/oauth/start", response_model=IntegrationOAuthStartResponse)
def start_provider_oauth(
    provider: str,
    payload: IntegrationOAuthStartRequest,
    current_user: User = Depends(get_current_user),
) -> IntegrationOAuthStartResponse:
    normalized = provider.strip().lower()
    if normalized not in META_OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Este canal ainda nao possui login oficial automatico.",
        )

    client_id = (settings.meta_oauth_client_id or "").strip()
    redirect_uri = (settings.meta_oauth_redirect_uri or "").strip()
    if not client_id or not redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Login oficial ainda nao configurado pela equipe tecnica.",
        )

    state_parts = [f"user:{current_user.id}", f"provider:{normalized}"]
    if payload.redirect_path:
        state_parts.append(f"return:{payload.redirect_path}")

    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": META_OAUTH_SCOPES[normalized],
            "state": "|".join(state_parts),
        }
    )
    return IntegrationOAuthStartResponse(
        provider=normalized,
        authorization_url=f"https://www.facebook.com/v20.0/dialog/oauth?{query}",
    )


@router.post("/whatsapp/qr/start", response_model=IntegrationQrStartResponse)
def start_whatsapp_qr(
    payload: IntegrationQrStartRequest,
    current_user: User = Depends(get_current_user),
) -> IntegrationQrStartResponse:
    expires_at = datetime.now(tz=UTC) + timedelta(minutes=5)
    pairing_code = f"AXI-WA-{secrets.token_urlsafe(6).replace('_', '').replace('-', '').upper()[:8]}"
    state_parts = [f"user:{current_user.id}", "provider:whatsapp", f"code:{pairing_code}"]
    if payload.redirect_path:
        state_parts.append(f"return:{payload.redirect_path}")

    base_url = (settings.app_base_url or "http://localhost:5173").rstrip("/")
    pairing_url = f"{base_url}/api/integrations/whatsapp/qr/pair?state={quote_plus('|'.join(state_parts))}"
    qr_code_url = (
        "https://api.qrserver.com/v1/create-qr-code/"
        f"?size=280x280&margin=12&data={quote_plus(pairing_url)}"
    )
    return IntegrationQrStartResponse(
        provider="whatsapp",
        qr_code_url=qr_code_url,
        pairing_code=pairing_code,
        expires_at=expires_at,
    )


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
