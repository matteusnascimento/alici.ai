import base64
import hashlib
import hmac
import logging
import secrets
import time
from datetime import UTC, datetime, timedelta
from urllib.parse import quote_plus, urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
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
    WebsiteChatScriptResponse,
)
from app.services.ai_service import AIConfigurationError, AIService, AIServiceError
from app.services.channel_integration_service import ChannelIntegrationService
from app.models.website_event import WebsiteEvent

router = APIRouter(prefix="/integrations", tags=["integrations"])
logger = logging.getLogger(__name__)

META_OAUTH_PROVIDERS = {"whatsapp", "instagram", "meta_ads"}
META_OAUTH_SCOPES = {
    "whatsapp": "business_management,whatsapp_business_management,whatsapp_business_messaging",
    "instagram": "instagram_basic,instagram_manage_messages,pages_show_list,pages_messaging,business_management",
    "meta_ads": "ads_read,ads_management,business_management",
}
GOOGLE_OAUTH_PROVIDERS = {"google_ads", "google_analytics"}
GOOGLE_OAUTH_SCOPES = {
    "google_ads": "https://www.googleapis.com/auth/adwords",
    "google_analytics": "https://www.googleapis.com/auth/analytics.readonly",
}
OAUTH_STATE_MAX_AGE_SECONDS = 15 * 60


def _frontend_url(path: str) -> str:
    return f"{(settings.app_base_url or 'http://localhost:5173').rstrip('/')}{path}"


def _sign_state(payload: str) -> str:
    secret = settings.secret_key.encode("utf-8")
    return hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()


def _build_state(user_id: int, provider: str, family: str) -> str:
    payload = f"user:{user_id}|provider:{provider}|family:{family}|ts:{int(time.time())}|nonce:{secrets.token_urlsafe(12)}"
    signed = f"{payload}|sig:{_sign_state(payload)}"
    return base64.urlsafe_b64encode(signed.encode("utf-8")).decode("ascii")


def _parse_state(state: str, expected_family: str) -> dict[str, str]:
    try:
        decoded = base64.urlsafe_b64decode(state.encode("ascii")).decode("utf-8")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state invalido.") from exc

    parts = dict(part.split(":", 1) for part in decoded.split("|") if ":" in part)
    signature = parts.pop("sig", None)
    payload = "|".join([part for part in decoded.split("|") if not part.startswith("sig:")])
    if not signature or not hmac.compare_digest(signature, _sign_state(payload)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state nao confere.")
    if parts.get("family") != expected_family:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state nao pertence a este provider.")
    try:
        created_at = int(parts.get("ts") or "0")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state sem timestamp valido.") from exc
    if time.time() - created_at > OAUTH_STATE_MAX_AGE_SECONDS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state expirado.")
    return parts


def _oauth_user(db: Session, state_parts: dict[str, str]) -> User:
    raw_user = state_parts.get("user", "")
    try:
        user_id = int(raw_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state sem usuario valido.") from exc
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario do OAuth nao encontrado.")
    return user


def _safe_oauth_error(exc: httpx.HTTPStatusError) -> str:
    try:
        payload = exc.response.json()
    except ValueError:
        return "Provider OAuth retornou erro sem JSON."
    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict):
            return str(error.get("message") or error.get("error_description") or error.get("type") or "Provider OAuth recusou a solicitacao.")
        return str(payload.get("error_description") or payload.get("error") or "Provider OAuth recusou a solicitacao.")
    return "Provider OAuth recusou a solicitacao."


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


@router.get("/meta/connect", response_model=IntegrationOAuthStartResponse)
def connect_meta_oauth(
    provider: str,
    current_user: User = Depends(get_current_user),
) -> IntegrationOAuthStartResponse:
    normalized = provider.strip().lower()
    if normalized not in META_OAUTH_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provider Meta invalido.")

    client_id = (settings.meta_oauth_client_id or "").strip()
    redirect_uri = (settings.meta_oauth_redirect_uri or "").strip()
    if not client_id or not redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OAuth Meta nao configurado no ambiente.",
        )

    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": META_OAUTH_SCOPES[normalized],
            "state": _build_state(current_user.id, normalized, "meta"),
        }
    )
    return IntegrationOAuthStartResponse(
        provider=normalized,
        authorization_url=f"https://www.facebook.com/v20.0/dialog/oauth?{query}",
    )


@router.get("/meta/callback")
def meta_oauth_callback(
    code: str | None = None,
    state: str | None = None,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    if not code or not state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Callback Meta incompleto.")
    state_parts = _parse_state(state, "meta")
    provider = (state_parts.get("provider") or "").strip().lower()
    if provider not in META_OAUTH_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provider Meta invalido.")

    client_id = (settings.meta_oauth_client_id or "").strip()
    client_secret = (settings.meta_app_secret or "").strip()
    redirect_uri = (settings.meta_oauth_redirect_uri or "").strip()
    if not client_id or not client_secret or not redirect_uri:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OAuth Meta nao configurado no ambiente.")

    user = _oauth_user(db, state_parts)
    try:
        with httpx.Client(timeout=15.0) as client:
            token_response = client.get(
                "https://graph.facebook.com/v20.0/oauth/access_token",
                params={
                    "client_id": client_id,
                    "redirect_uri": redirect_uri,
                    "client_secret": client_secret,
                    "code": code,
                },
            )
            token_response.raise_for_status()
            token_payload = token_response.json()
            access_token = str(token_payload.get("access_token") or "")
            if not access_token:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Meta nao retornou access token.")

            account_response = client.get(
                "https://graph.facebook.com/v20.0/me",
                params={"fields": "id,name", "access_token": access_token},
            )
            account_response.raise_for_status()
            account_payload = account_response.json()
    except httpx.HTTPStatusError as exc:
        logger.warning("meta_oauth_callback_failed provider=%s user_id=%s error=%s", provider, user.id, _safe_oauth_error(exc))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=_safe_oauth_error(exc)) from exc
    except httpx.HTTPError as exc:
        logger.warning("meta_oauth_network_failed provider=%s user_id=%s error_type=%s", provider, user.id, type(exc).__name__)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Falha de rede ao concluir OAuth Meta.") from exc

    expires_in = int(token_payload.get("expires_in") or 0)
    expires_at = datetime.now(tz=UTC) + timedelta(seconds=expires_in) if expires_in else None
    metadata = {
        "oauth_family": "meta",
        "scopes": META_OAUTH_SCOPES[provider].split(","),
        "expires_at": expires_at.isoformat() if expires_at else None,
        "connected_at": datetime.now(tz=UTC).isoformat(),
        "account_payload_received": bool(account_payload),
    }
    ChannelIntegrationService(db).upsert_connected_account(
        user,
        provider,
        {
            "external_account_id": str(account_payload.get("id") or f"meta:{user.id}:{provider}"),
            "external_account_name": str(account_payload.get("name") or "Conta Meta conectada"),
            "access_token": access_token,
            "metadata": metadata,
        },
    )
    logger.info("integration_connected family=meta provider=%s user_id=%s", provider, user.id)
    return RedirectResponse(_frontend_url("/app/integrations?connected=meta"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/google/connect", response_model=IntegrationOAuthStartResponse)
def connect_google_oauth(
    provider: str,
    current_user: User = Depends(get_current_user),
) -> IntegrationOAuthStartResponse:
    normalized = provider.strip().lower()
    if normalized not in GOOGLE_OAUTH_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provider Google invalido.")

    client_id = (settings.google_oauth_client_id or "").strip()
    redirect_uri = (settings.google_oauth_redirect_uri or "").strip()
    if not client_id or not redirect_uri:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OAuth Google nao configurado no ambiente.")

    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": GOOGLE_OAUTH_SCOPES[normalized],
            "state": _build_state(current_user.id, normalized, "google"),
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
        }
    )
    return IntegrationOAuthStartResponse(
        provider=normalized,
        authorization_url=f"https://accounts.google.com/o/oauth2/v2/auth?{query}",
    )


@router.get("/google/callback")
def google_oauth_callback(
    code: str | None = None,
    state: str | None = None,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    if not code or not state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Callback Google incompleto.")
    state_parts = _parse_state(state, "google")
    provider = (state_parts.get("provider") or "").strip().lower()
    if provider not in GOOGLE_OAUTH_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provider Google invalido.")

    client_id = (settings.google_oauth_client_id or "").strip()
    client_secret = (settings.google_oauth_client_secret or "").strip()
    redirect_uri = (settings.google_oauth_redirect_uri or "").strip()
    if not client_id or not client_secret or not redirect_uri:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OAuth Google nao configurado no ambiente.")

    user = _oauth_user(db, state_parts)
    try:
        with httpx.Client(timeout=15.0) as client:
            token_response = client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                    "code": code,
                },
            )
            token_response.raise_for_status()
            token_payload = token_response.json()
            access_token = str(token_payload.get("access_token") or "")
            refresh_token = str(token_payload.get("refresh_token") or "")
            if not access_token:
                raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Google nao retornou access token.")

            profile_response = client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            profile_response.raise_for_status()
            profile_payload = profile_response.json()
    except httpx.HTTPStatusError as exc:
        logger.warning("google_oauth_callback_failed provider=%s user_id=%s error=%s", provider, user.id, _safe_oauth_error(exc))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=_safe_oauth_error(exc)) from exc
    except httpx.HTTPError as exc:
        logger.warning("google_oauth_network_failed provider=%s user_id=%s error_type=%s", provider, user.id, type(exc).__name__)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Falha de rede ao concluir OAuth Google.") from exc

    expires_in = int(token_payload.get("expires_in") or 0)
    expires_at = datetime.now(tz=UTC) + timedelta(seconds=expires_in) if expires_in else None
    metadata = {
        "oauth_family": "google",
        "scopes": GOOGLE_OAUTH_SCOPES[provider].split(" "),
        "expires_at": expires_at.isoformat() if expires_at else None,
        "connected_at": datetime.now(tz=UTC).isoformat(),
        "token_type": token_payload.get("token_type"),
    }
    ChannelIntegrationService(db).upsert_connected_account(
        user,
        provider,
        {
            "external_account_id": str(profile_payload.get("sub") or f"google:{user.id}:{provider}"),
            "external_account_name": str(profile_payload.get("email") or profile_payload.get("name") or "Conta Google conectada"),
            "access_token": access_token,
            "refresh_token": refresh_token or None,
            "metadata": metadata,
        },
    )
    logger.info("integration_connected family=google provider=%s user_id=%s", provider, user.id)
    return RedirectResponse(_frontend_url("/app/integrations?connected=google"), status_code=status.HTTP_303_SEE_OTHER)


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


def _test_hospitality_credentials(provider: str, payload: IntegrationTestRequest) -> IntegrationTestResponse:
    endpoint = (payload.endpoint or "").strip()
    token = (payload.token or payload.api_key or "").strip()
    if provider not in {"omnibees", "pms"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Provider hoteleiro invalido.")
    if not endpoint or not token:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Informe URL da API e token/API key para testar a conexao.",
        )
    try:
        with httpx.Client(timeout=12.0) as client:
            response = client.get(endpoint, headers={"Authorization": f"Bearer {token}", "X-API-Key": token})
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.warning("%s_test_failed status_code=%s", provider, exc.response.status_code)
        return IntegrationTestResponse(
            provider=provider,
            status="error",
            message=f"{provider} recusou a conexao com status {exc.response.status_code}.",
            error_type="provider_http_error",
            status_code=exc.response.status_code,
        )
    except httpx.HTTPError as exc:
        logger.warning("%s_test_network_failed error_type=%s", provider, type(exc).__name__)
        return IntegrationTestResponse(
            provider=provider,
            status="error",
            message=f"Nao foi possivel conectar ao endpoint {provider}.",
            error_type="provider_network_error",
            status_code=502,
        )
    return IntegrationTestResponse(
        provider=provider,
        status="ok",
        message="Conexao externa validada com sucesso.",
        status_code=200,
    )


@router.post("/omnibees/test", response_model=IntegrationTestResponse)
def test_omnibees(payload: IntegrationTestRequest, _: User = Depends(get_current_user)) -> IntegrationTestResponse:
    return _test_hospitality_credentials("omnibees", payload)


@router.post("/omnibees/connect", response_model=IntegrationAccountRead)
def connect_omnibees(
    payload: IntegrationTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationAccountRead:
    result = _test_hospitality_credentials("omnibees", payload)
    if result.status != "ok":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=result.message)
    svc = ChannelIntegrationService(db)
    account = svc.upsert_connected_account(
        current_user,
        "omnibees",
        {
            "external_account_id": payload.endpoint,
            "external_account_name": "OmniBees",
            "access_token": payload.token or payload.api_key,
            "metadata": {
                "config": {"endpoint": payload.endpoint},
                "connected_at": datetime.now(tz=UTC).isoformat(),
                "scopes": ["reservations", "availability"],
            },
        },
    )
    logger.info("integration_connected family=hospitality provider=omnibees user_id=%s", current_user.id)
    return IntegrationAccountRead(**svc._serialize_account(account))


@router.post("/pms/test", response_model=IntegrationTestResponse)
def test_pms(payload: IntegrationTestRequest, _: User = Depends(get_current_user)) -> IntegrationTestResponse:
    return _test_hospitality_credentials("pms", payload)


@router.post("/pms/connect", response_model=IntegrationAccountRead)
def connect_pms(
    payload: IntegrationTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationAccountRead:
    result = _test_hospitality_credentials("pms", payload)
    if result.status != "ok":
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=result.message)
    svc = ChannelIntegrationService(db)
    account = svc.upsert_connected_account(
        current_user,
        "pms",
        {
            "external_account_id": payload.endpoint,
            "external_account_name": "PMS",
            "access_token": payload.token or payload.api_key,
            "metadata": {
                "config": {"endpoint": payload.endpoint},
                "connected_at": datetime.now(tz=UTC).isoformat(),
                "scopes": ["reservations", "guests", "availability"],
            },
        },
    )
    logger.info("integration_connected family=hospitality provider=pms user_id=%s", current_user.id)
    return IntegrationAccountRead(**svc._serialize_account(account))


@router.get("/website-chat/widget-script", response_model=WebsiteChatScriptResponse)
def get_website_chat_widget_script(current_user: User = Depends(get_current_user)) -> WebsiteChatScriptResponse:
    base_url = (settings.app_base_url or "http://localhost:5173").rstrip("/")
    company_id = f"axi-{current_user.id}"
    script = f'<script src="{base_url}/widget.js" data-axi-company-id="{company_id}" async></script>'
    return WebsiteChatScriptResponse(company_id=company_id, script=script)


@router.post("/website-chat/test-installation", response_model=IntegrationTestResponse)
def test_website_chat_installation(
    payload: IntegrationTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationTestResponse:
    site_id = (payload.endpoint or f"axi-{current_user.id}").strip()
    event = db.query(WebsiteEvent).filter(WebsiteEvent.site_id == site_id).order_by(WebsiteEvent.created_at.desc()).first()
    if not event:
        return IntegrationTestResponse(
            provider="website_chat",
            status="disconnected",
            message="Nenhum evento real do widget foi recebido ainda.",
            status_code=404,
        )
    return IntegrationTestResponse(
        provider="website_chat",
        status="ok",
        message="Widget instalado: eventos reais recebidos pelo AXI Tracker.",
        status_code=200,
    )


@router.post("/{provider}/connect", response_model=IntegrationAccountRead)
def connect_provider(
    provider: str,
    payload: IntegrationAccountCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationAccountRead:
    normalized = provider.strip().lower()
    if normalized in META_OAUTH_PROVIDERS or normalized in GOOGLE_OAUTH_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Use o fluxo OAuth oficial deste provider; o AXI nao recebe senha/token manual para Meta ou Google.",
        )
    svc = ChannelIntegrationService(db)
    data = payload.model_dump()
    data["provider"] = normalized
    account = svc.create_integration_account(current_user, data)
    return IntegrationAccountRead(**svc._serialize_account(account))


@router.post("/{provider}/test", response_model=IntegrationTestResponse)
def test_provider(
    provider: str,
    _: IntegrationTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationTestResponse:
    if provider.strip().lower() == "openai":
        return _run_openai_healthcheck()
    result = ChannelIntegrationService(db).test_provider(current_user, provider)
    return IntegrationTestResponse(**result)


@router.post("/{provider}/sync", response_model=IntegrationTestResponse)
def sync_provider(
    provider: str,
    _: IntegrationTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationTestResponse:
    result = ChannelIntegrationService(db).sync_provider(current_user, provider)
    return IntegrationTestResponse(**result)
