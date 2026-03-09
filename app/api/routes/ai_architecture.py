"""AI architecture control plane endpoints (model router + vector store)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models import User
from app.services.auth_service import AuthService
from app.services.model_router_service import ModelRouterService
from app.services.vector_store_service import VectorStoreService

router = APIRouter()
model_router_service = ModelRouterService()
vector_store_service = VectorStoreService()


class ModelProviderRequest(BaseModel):
    provider: str


class VectorProviderRequest(BaseModel):
    provider: str
    endpoint: str | None = None
    index_name: str | None = None


@router.get("/architecture")
def get_architecture_status(current_user: User = Depends(AuthService.get_current_user)):
    org_id = current_user.organization_id
    return {
        "status": "success",
        "data": {
            "model_router": {
                "available_providers": model_router_service.list_providers(),
                "default_provider": model_router_service.get_default_provider(org_id),
            },
            "vector_store": {
                "available_providers": vector_store_service.list_providers(),
                "configured": vector_store_service.get_org_config(org_id),
            },
        },
        "error": None,
    }


@router.post("/model-router/provider")
def set_default_model_provider(
    payload: ModelProviderRequest,
    current_user: User = Depends(AuthService.get_current_user),
):
    try:
        model_router_service.set_default_provider(current_user.organization_id, payload.provider)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "status": "success",
        "data": {
            "default_provider": model_router_service.get_default_provider(current_user.organization_id),
        },
        "error": None,
    }


@router.post("/vector-store/provider")
def set_vector_provider(
    payload: VectorProviderRequest,
    current_user: User = Depends(AuthService.get_current_user),
):
    try:
        configured = vector_store_service.configure_org_provider(
            current_user.organization_id,
            payload.provider,
            endpoint=payload.endpoint,
            index_name=payload.index_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "status": "success",
        "data": configured,
        "error": None,
    }
