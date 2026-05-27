"""Marketing workspace routes backed by real CRM, omnichannel and AI data."""

from __future__ import annotations

import json
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from alici_api.config import get_settings
from alici_api.dependencies import get_current_user
from alici_api.services.ai_service import generate_chat_response
from database import (
    atualizar_marketing_project,
    buscar_marketing_project,
    criar_marketing_project,
    deletar_marketing_project,
    listar_conexoes_sociais,
    listar_marketing_projects,
    marketing_performance_summary,
)

router = APIRouter(prefix="/marketing", tags=["marketing"])


class MarketingProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    audience: str = Field(min_length=2, max_length=240)
    objective: str = Field(min_length=2, max_length=240)
    offer: str = Field(min_length=2, max_length=240)
    tone: str = Field(default="premium", max_length=60)
    notes: str | None = Field(default=None, max_length=2000)


class MarketingProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    audience: str | None = Field(default=None, min_length=2, max_length=240)
    objective: str | None = Field(default=None, min_length=2, max_length=240)
    offer: str | None = Field(default=None, min_length=2, max_length=240)
    tone: str | None = Field(default=None, max_length=60)
    notes: str | None = Field(default=None, max_length=2000)


class CampaignRequest(BaseModel):
    company_name: str = Field(min_length=2, max_length=160)
    audience: str = Field(min_length=2, max_length=240)
    objective: str = Field(min_length=2, max_length=240)
    offer: str = Field(min_length=2, max_length=240)
    tone: str = Field(default="premium", max_length=60)


class GenerateContentRequest(BaseModel):
    project_id: int
    context: str = Field(min_length=2, max_length=1200)
    type: str = Field(default="social_post", max_length=60)


class QuickBriefRequest(BaseModel):
    idea: str = Field(min_length=5, max_length=1000)
    tone: str = Field(default="premium", max_length=60)


def _user_id(user: dict) -> int:
    return int(user["id"])


def _json_from_ai(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        payload = json.loads(cleaned)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        pass
    return {}


async def _fetch_google_ads_metrics(user_id: int) -> dict[str, int] | None:
    settings = get_settings()
    if not settings.google_ads_developer_token:
        return None

    connections = [
        connection
        for connection in listar_conexoes_sociais(user_id)
        if connection.get("provider") == "google_ads"
        and connection.get("enabled")
        and connection.get("status") == "connected"
        and connection.get("access_token")
    ]
    if not connections:
        return None

    access_token = connections[0]["access_token"]
    developer_token = settings.google_ads_developer_token.get_secret_value()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "developer-token": developer_token,
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=20) as client:
        customers_resp = await client.get(
            "https://googleads.googleapis.com/v22/customers:listAccessibleCustomers",
            headers=headers,
        )
        if customers_resp.status_code >= 400:
            raise HTTPException(status_code=502, detail="Google Ads nao retornou contas acessiveis para este usuario.")
        resource_names = customers_resp.json().get("resourceNames") or []
        if not resource_names:
            return {"views": 0, "clicks": 0, "cost_micros": 0, "conversions": 0}
        customer_id = str(resource_names[0]).split("/")[-1]
        query = """
            SELECT
              metrics.impressions,
              metrics.clicks,
              metrics.cost_micros,
              metrics.conversions
            FROM campaign
            WHERE segments.date DURING LAST_30_DAYS
        """
        stream_resp = await client.post(
            f"https://googleads.googleapis.com/v22/customers/{customer_id}/googleAds:searchStream",
            headers=headers,
            json={"query": query},
        )
        if stream_resp.status_code >= 400:
            raise HTTPException(status_code=502, detail="Falha ao importar metricas do Google Ads.")
        totals = {"views": 0, "clicks": 0, "cost_micros": 0, "conversions": 0}
        for batch in stream_resp.json() or []:
            for row in batch.get("results", []):
                metrics = row.get("metrics", {})
                totals["views"] += int(metrics.get("impressions") or 0)
                totals["clicks"] += int(metrics.get("clicks") or 0)
                totals["cost_micros"] += int(metrics.get("costMicros") or metrics.get("cost_micros") or 0)
                totals["conversions"] += int(float(metrics.get("conversions") or 0))
        return totals


@router.get("/projects")
def list_projects(user=Depends(get_current_user)):
    return listar_marketing_projects(_user_id(user))


@router.post("/projects")
def create_project(payload: MarketingProjectCreate, user=Depends(get_current_user)):
    return criar_marketing_project(_user_id(user), **payload.model_dump())


@router.get("/projects/{project_id}")
def get_project(project_id: int, user=Depends(get_current_user)):
    item = buscar_marketing_project(_user_id(user), project_id)
    if not item:
        raise HTTPException(status_code=404, detail="Projeto de marketing nao encontrado")
    return item


@router.patch("/projects/{project_id}")
def update_project(project_id: int, payload: MarketingProjectUpdate, user=Depends(get_current_user)):
    item = atualizar_marketing_project(_user_id(user), project_id, **payload.model_dump(exclude_unset=True))
    if not item:
        raise HTTPException(status_code=404, detail="Projeto de marketing nao encontrado")
    return item


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: int, user=Depends(get_current_user)):
    if not deletar_marketing_project(_user_id(user), project_id):
        raise HTTPException(status_code=404, detail="Projeto de marketing nao encontrado")
    return None


@router.get("/performance")
async def get_performance(user=Depends(get_current_user)):
    user_id = _user_id(user)
    summary = marketing_performance_summary(user_id)
    google_metrics = await _fetch_google_ads_metrics(user_id)
    if google_metrics is not None:
        summary["views"] = google_metrics["views"]
        summary["clicks"] = google_metrics["clicks"]
        summary["ads_cost_micros"] = google_metrics["cost_micros"]
        summary["reservations"] = max(int(summary.get("reservations") or 0), google_metrics["conversions"])
        summary["ads_connected"] = True
        summary["message"] = None
    return summary


@router.post("/quick-brief")
async def quick_brief(payload: QuickBriefRequest, user=Depends(get_current_user)):
    prompt = f"""
Extraia um briefing de marketing a partir da ideia abaixo.
Responda SOMENTE JSON valido com as chaves:
name, audience, objective, offer, tone, notes.
Use pt-BR, seja especifico e nao invente dados externos.
Tom preferido: {payload.tone}
Ideia: {payload.idea}
"""
    try:
        response = await generate_chat_response(prompt)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"IA de marketing indisponivel: {exc}") from exc

    data = _json_from_ai(response.content)
    if not data:
        raise HTTPException(status_code=502, detail="A IA nao retornou um briefing estruturado.")
    return {
        "name": str(data.get("name") or "Campanha de Marketing").strip()[:160],
        "audience": str(data.get("audience") or "Publico-alvo qualificado").strip()[:240],
        "objective": str(data.get("objective") or "Gerar conversoes").strip()[:240],
        "offer": str(data.get("offer") or "Oferta principal").strip()[:240],
        "tone": str(data.get("tone") or payload.tone or "premium").strip()[:60],
        "notes": str(data.get("notes") or payload.idea).strip()[:2000],
    }


@router.post("/campaign")
async def generate_campaign(payload: CampaignRequest, user=Depends(get_current_user)):
    performance = marketing_performance_summary(_user_id(user))
    prompt = f"""
Crie uma campanha profissional para a AXI Marketing.
Empresa: {payload.company_name}
Publico: {payload.audience}
Objetivo: {payload.objective}
Oferta: {payload.offer}
Tom: {payload.tone}
Dados reais disponiveis: {json.dumps(performance, ensure_ascii=False)}

Responda SOMENTE JSON valido com:
campaign, copy, cta, ad_structure, creative_suggestion.
Nao invente metricas de anuncios. Quando faltar Google Ads/Meta Ads, recomende conectar a fonte.
"""
    try:
        response = await generate_chat_response(prompt)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"IA de marketing indisponivel: {exc}") from exc
    data = _json_from_ai(response.content)
    if not data:
        raise HTTPException(status_code=502, detail="A IA nao retornou campanha estruturada.")
    return data


@router.post("/generate-content")
async def generate_content(payload: GenerateContentRequest, user=Depends(get_current_user)):
    project = buscar_marketing_project(_user_id(user), payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projeto de marketing nao encontrado")
    prompt = f"""
Gere conteudo de marketing para o projeto abaixo.
Projeto: {json.dumps(project, ensure_ascii=False)}
Tipo: {payload.type}
Contexto: {payload.context}

Responda SOMENTE JSON valido com:
copies (array com 3 opcoes), cta, hook, hashtags (array).
"""
    try:
        response = await generate_chat_response(prompt)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"IA de marketing indisponivel: {exc}") from exc
    data = _json_from_ai(response.content)
    if not data:
        raise HTTPException(status_code=502, detail="A IA nao retornou conteudo estruturado.")
    return data
