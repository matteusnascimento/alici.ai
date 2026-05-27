from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse

from alici_api.dependencies import get_current_user
from alici_api.schemas import SocialConnectRequest, SocialConnectionToggleRequest
from alici_api.services.omnichannel_service import OmnichannelService

router = APIRouter(prefix="/integrations", tags=["integrations"])
service = OmnichannelService()


@router.get("")
def list_integrations(current_user=Depends(get_current_user)):
    return service.list_providers(int(current_user["id"]))


@router.get("/accounts")
def list_accounts(current_user=Depends(get_current_user)):
    return service.list_accounts(int(current_user["id"]))


@router.post("")
def connect_account(payload: SocialConnectRequest, current_user=Depends(get_current_user)):
    try:
        return service.connect(
            user_id=int(current_user["id"]),
            provider=payload.provider,
            external_account_id=payload.external_account_id,
            external_account_name=payload.external_account_name,
            access_token=payload.access_token,
            enabled=payload.enabled,
            metadata=payload.metadata,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{provider}/oauth/start")
def start_oauth(provider: str, current_user=Depends(get_current_user)):
    try:
        return service.oauth_start_url(int(current_user["id"]), provider)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
):
    if error:
        return RedirectResponse(url=f"/app/integrations?oauth=error&provider={provider}")
    if not code or not state:
        return RedirectResponse(url=f"/app/integrations?oauth=invalid&provider={provider}")
    try:
        await service.handle_oauth_callback(provider, code, state)
    except Exception:
        return RedirectResponse(url=f"/app/integrations?oauth=failed&provider={provider}")
    return RedirectResponse(url=f"/app/integrations?oauth=success&provider={provider}")


@router.get("/{provider}/status")
def provider_status(provider: str, current_user=Depends(get_current_user)):
    try:
        return service.get_provider_status(int(current_user["id"]), provider)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{provider}/disconnect")
def disconnect_provider(provider: str, current_user=Depends(get_current_user)):
    try:
        return service.disconnect_provider(int(current_user["id"]), provider)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/accounts/{connection_id}")
def toggle_connection(connection_id: int, payload: SocialConnectionToggleRequest, current_user=Depends(get_current_user)):
    try:
        return service.set_enabled(int(current_user["id"]), connection_id, payload.enabled)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/accounts/{connection_id}")
def disconnect_connection(connection_id: int, current_user=Depends(get_current_user)):
    try:
        return service.set_enabled(int(current_user["id"]), connection_id, False)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
