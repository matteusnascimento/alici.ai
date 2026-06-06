import base64
import hashlib
import hmac
import json
import logging
import re
import secrets
import time
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qsl, quote_plus, urlencode, urlsplit, urlunsplit

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
DEFAULT_META_OAUTH_SCOPES = {
    "whatsapp": "business_management,whatsapp_business_management,whatsapp_business_messaging",
    "instagram": "instagram_basic,instagram_manage_messages,pages_show_list,pages_messaging,business_management",
    "meta_ads": "ads_read,ads_management,business_management",
}
GOOGLE_OAUTH_PROVIDERS = {"google_ads", "google_analytics"}
DEFAULT_GOOGLE_OAUTH_SCOPES = {
    "google_ads": "https://www.googleapis.com/auth/adwords",
    "google_analytics": "https://www.googleapis.com/auth/analytics.readonly",
}
OAUTH_STATE_MAX_AGE_SECONDS = 15 * 60


def _frontend_url(path: str) -> str:
    return f"{settings.frontend_base_url}{path}"


def _sign_state(payload: str) -> str:
    secret = settings.effective_app_secret_key.encode("utf-8")
    return hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()


def _slugify_company(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    return normalized.strip("-")[:80]


def _active_company_context(user: User) -> dict[str, str | bool]:
    company_name = (user.company or "").strip()
    if not company_name:
        if settings.app_env.lower() == "production":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Configure os dados da empresa ativa antes de conectar integrações.",
            )
        company_name = user.email or f"Usuario {user.id}"
        company_id = f"axi-{user.id}"
        return {
            "company_id": company_id,
            "company_name": company_name,
            "company_configured": False,
        }

    company_id = _slugify_company(company_name) or f"axi-{user.id}"
    return {
        "company_id": company_id,
        "company_name": company_name,
        "company_configured": True,
    }


def _meta_scopes(provider: str) -> str:
    return (settings.meta_oauth_scopes or DEFAULT_META_OAUTH_SCOPES[provider]).strip()


def _google_scopes(provider: str) -> str:
    return (settings.google_oauth_scopes or DEFAULT_GOOGLE_OAUTH_SCOPES[provider]).strip()


def _append_query(url: str, params: dict[str, str]) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.update({key: value for key, value in params.items() if value})
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _raise_meta_not_configured() -> None:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Integração Meta não configurada. Configure META_CLIENT_ID, META_CLIENT_SECRET e META_REDIRECT_URI.",
    )


def _raise_google_not_configured() -> None:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Integração Google não configurada. Configure GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET e GOOGLE_REDIRECT_URI.",
    )


def _build_state(user: User, provider: str, family: str) -> str:
    now = int(time.time())
    company = _active_company_context(user)
    payload = {
        "user_id": str(user.id),
        "company_id": company["company_id"],
        "company_name": company["company_name"],
        "company_configured": company["company_configured"],
        "provider": provider,
        "provider_family": family,
        "nonce": secrets.token_urlsafe(18),
        "created_at": now,
        "expires_at": now + OAUTH_STATE_MAX_AGE_SECONDS,
    }
    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    signed = json.dumps(
        {"payload": payload, "sig": _sign_state(payload_json)},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return base64.urlsafe_b64encode(signed.encode("utf-8")).decode("ascii")


def _parse_legacy_state(decoded: str, expected_family: str) -> dict[str, str]:
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


def _parse_state(state: str, expected_family: str) -> dict[str, str]:
    try:
        decoded = base64.urlsafe_b64decode(state.encode("ascii")).decode("utf-8")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state invalido.") from exc

    if decoded.startswith("user:"):
        return _parse_legacy_state(decoded, expected_family)

    try:
        wrapper = json.loads(decoded)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state invalido.") from exc
    if not isinstance(wrapper, dict) or not isinstance(wrapper.get("payload"), dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state invalido.")

    payload = wrapper["payload"]
    signature = str(wrapper.get("sig") or "")
    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    if not signature or not hmac.compare_digest(signature, _sign_state(payload_json)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state nao confere.")
    if str(payload.get("provider_family") or "") != expected_family:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state nao pertence a este provider.")
    try:
        expires_at = int(payload.get("expires_at") or "0")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state sem expiracao valida.") from exc
    if time.time() > expires_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state expirado.")
    return {str(key): str(value) for key, value in payload.items()}


def _oauth_user(db: Session, state_parts: dict[str, str]) -> User:
    raw_user = state_parts.get("user_id") or state_parts.get("user", "")
    try:
        user_id = int(raw_user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OAuth state sem usuario valido.") from exc
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario do OAuth nao encontrado.")
    return user


def _oauth_company_metadata(user: User, state_parts: dict[str, str]) -> dict[str, str | bool]:
    current_company = _active_company_context(user)
    state_company_id = (state_parts.get("company_id") or "").strip()
    state_company_name = (state_parts.get("company_name") or "").strip()
    if state_company_id and state_company_id != current_company["company_id"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empresa ativa do OAuth nao confere.")
    return {
        "company_id": str(current_company["company_id"]),
        "company_name": str(current_company["company_name"]),
        "company_configured": bool(current_company["company_configured"]),
        "state_company_name": state_company_name or str(current_company["company_name"]),
    }


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

    if not settings.is_meta_configured():
        _raise_meta_not_configured()
    client_id = settings.effective_meta_client_id.strip()
    redirect_uri = settings.effective_meta_redirect_uri.strip()

    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": _meta_scopes(normalized),
            "state": _build_state(current_user, normalized, "meta"),
        }
    )
    return IntegrationOAuthStartResponse(
        provider=normalized,
        authorization_url=f"https://www.facebook.com/{settings.meta_graph_api_version}/dialog/oauth?{query}",
    )


@router.get("/meta/connect", response_model=IntegrationOAuthStartResponse)
def connect_meta_oauth(
    provider: str,
    current_user: User = Depends(get_current_user),
) -> IntegrationOAuthStartResponse:
    normalized = provider.strip().lower()
    if normalized not in META_OAUTH_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider Meta invalido.")

    if not settings.is_meta_configured():
        _raise_meta_not_configured()
    client_id = settings.effective_meta_client_id.strip()
    redirect_uri = settings.effective_meta_redirect_uri.strip()

    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": _meta_scopes(normalized),
            "state": _build_state(current_user, normalized, "meta"),
        }
    )
    return IntegrationOAuthStartResponse(
        provider=normalized,
        authorization_url=f"https://www.facebook.com/{settings.meta_graph_api_version}/dialog/oauth?{query}",
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider Meta invalido.")

    if not settings.is_meta_configured():
        _raise_meta_not_configured()
    client_id = settings.effective_meta_client_id.strip()
    client_secret = settings.effective_meta_client_secret.strip()
    redirect_uri = settings.effective_meta_redirect_uri.strip()

    user = _oauth_user(db, state_parts)
    company_metadata = _oauth_company_metadata(user, state_parts)
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
        "tenant": company_metadata,
        "scopes": [item.strip() for item in _meta_scopes(provider).split(",") if item.strip()],
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
    logger.info(
        "integration_connected family=meta provider=%s user_id=%s company_id=%s",
        provider,
        user.id,
        company_metadata["company_id"],
    )
    return RedirectResponse(_frontend_url("/app/integrations?connected=meta"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/google/connect", response_model=IntegrationOAuthStartResponse)
def connect_google_oauth(
    provider: str,
    current_user: User = Depends(get_current_user),
) -> IntegrationOAuthStartResponse:
    normalized = provider.strip().lower()
    if normalized not in GOOGLE_OAUTH_PROVIDERS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider Google invalido.")

    if not settings.is_google_configured():
        _raise_google_not_configured()
    client_id = settings.effective_google_client_id.strip()
    redirect_uri = settings.effective_google_redirect_uri.strip()

    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": _google_scopes(normalized),
            "state": _build_state(current_user, normalized, "google"),
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider Google invalido.")

    if not settings.is_google_configured():
        _raise_google_not_configured()
    client_id = settings.effective_google_client_id.strip()
    client_secret = settings.effective_google_client_secret.strip()
    redirect_uri = settings.effective_google_redirect_uri.strip()

    user = _oauth_user(db, state_parts)
    company_metadata = _oauth_company_metadata(user, state_parts)
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
        "tenant": company_metadata,
        "scopes": [item.strip() for item in _google_scopes(provider).split(" ") if item.strip()],
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
    logger.info(
        "integration_connected family=google provider=%s user_id=%s company_id=%s",
        provider,
        user.id,
        company_metadata["company_id"],
    )
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

    base_url = settings.backend_base_url
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
        if provider == "omnibees" and settings.is_omnibees_configured():
            endpoint = settings.omnibees_api_base_url.strip()
            token = settings.omnibees_client_secret.strip()
        elif provider == "pms" and settings.is_pms_configured():
            endpoint = settings.pms_api_base_url.strip()
            token = settings.pms_client_secret.strip()
    if not endpoint or not token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Integração OmniBees não configurada. Configure OMNIBEES_API_BASE_URL, OMNIBEES_CLIENT_ID e OMNIBEES_CLIENT_SECRET."
                if provider == "omnibees"
                else "Integração PMS não configurada. Configure PMS_API_BASE_URL, PMS_CLIENT_ID e PMS_CLIENT_SECRET."
            ),
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
            "external_account_id": (payload.endpoint or settings.omnibees_api_base_url).strip(),
            "external_account_name": "OmniBees",
            "access_token": payload.token or payload.api_key or settings.omnibees_client_secret,
            "metadata": {
                "config": {"endpoint": (payload.endpoint or settings.omnibees_api_base_url).strip(), "environment": settings.omnibees_environment},
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
            "external_account_id": (payload.endpoint or settings.pms_api_base_url).strip(),
            "external_account_name": "PMS",
            "access_token": payload.token or payload.api_key or settings.pms_client_secret,
            "metadata": {
                "config": {"endpoint": (payload.endpoint or settings.pms_api_base_url).strip(), "environment": settings.pms_environment},
                "connected_at": datetime.now(tz=UTC).isoformat(),
                "scopes": ["reservations", "guests", "availability"],
            },
        },
    )
    logger.info("integration_connected family=hospitality provider=pms user_id=%s", current_user.id)
    return IntegrationAccountRead(**svc._serialize_account(account))


@router.get("/website-chat/widget-script", response_model=WebsiteChatScriptResponse)
def get_website_chat_widget_script(current_user: User = Depends(get_current_user)) -> WebsiteChatScriptResponse:
    if not (settings.public_backend_url and settings.axi_tracker_public_url and settings.axi_widget_public_url):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Website Tracker não configurado. Configure PUBLIC_BACKEND_URL, AXI_TRACKER_PUBLIC_URL e AXI_WIDGET_PUBLIC_URL.",
        )
    base_url = settings.backend_base_url
    company = _active_company_context(current_user)
    company_id = str(company["company_id"])
    tracker_src = _append_query(settings.axi_tracker_public_url.strip(), {"site_id": company_id})
    widget_src = settings.axi_widget_public_url.strip()
    tracker_endpoint = f"{base_url}/api/tracker/events"
    script = (
        f'<script src="{tracker_src}" data-axi-company-id="{company_id}" '
        f'data-axi-endpoint="{tracker_endpoint}" async></script>\n'
        f'<script src="{widget_src}" data-axi-company-id="{company_id}" async></script>'
    )
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
