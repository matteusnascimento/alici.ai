import json

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.core.security import get_current_user
from app.integrations.providers.http_security import UnsafeProviderURL, assert_public_http_url
from app.models.user import User
from app.schemas.ai import (
    AIStandardResponse,
    AgentBuilderRequest,
    AnalyticsInsightsRequest,
    DocumentAnalysisRequest,
    ImageAnalysisRequest,
    PromptPlaygroundRequest,
    TaskTextRequest,
    WorkflowBuilderRequest,
)
from app.schemas.integration import IntegrationTestResponse
from app.services.ai_service import AIConfigurationError, AIService, AIServiceError

router = APIRouter(prefix="/ai", tags=["ai"])

MAX_IMAGE_ANALYSIS_BYTES = 10 * 1024 * 1024
ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def _download_public_image(image_url: str) -> bytes:
    try:
        assert_public_http_url(image_url)
    except UnsafeProviderURL as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    chunks: list[bytes] = []
    total = 0
    with httpx.Client(timeout=settings.openai_timeout_seconds) as client:
        with client.stream("GET", image_url, follow_redirects=False) as response:
            response.raise_for_status()
            content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
            if content_type and content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
                raise HTTPException(status_code=400, detail="URL informada nao retornou uma imagem permitida")
            for chunk in response.iter_bytes():
                total += len(chunk)
                if total > MAX_IMAGE_ANALYSIS_BYTES:
                    raise HTTPException(status_code=400, detail="Imagem excede 10MB")
                chunks.append(chunk)
    return b"".join(chunks)


@router.post("/test", response_model=IntegrationTestResponse)
def test_ai(_: User = Depends(get_current_user)) -> IntegrationTestResponse:
    service = AIService()
    try:
        result = service.healthcheck()
        return IntegrationTestResponse(
            provider=service.provider,
            status=result.get("status", "error"),
            message=result.get("message", "Falha ao validar IA."),
            model=result.get("model"),
            model_used=result.get("model"),
            latency_ms=result.get("latency_ms"),
            error_type=result.get("error_type"),
            status_code=result.get("status_code"),
        )
    except AIConfigurationError as exc:
        return IntegrationTestResponse(
            provider=service.provider,
            status="warning",
            message=exc.user_message,
            model=None,
            model_used=None,
            latency_ms=None,
            error_type=exc.code,
            status_code=exc.status_code,
        )
    except AIServiceError as exc:
        return IntegrationTestResponse(
            provider=service.provider,
            status="error",
            message=exc.user_message,
            model=None,
            model_used=None,
            latency_ms=None,
            error_type=exc.code,
            status_code=exc.status_code,
        )


def _raise_ai_http_error(exc: AIServiceError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc


@router.post("/playground", response_model=AIStandardResponse)
def prompt_playground(payload: PromptPlaygroundRequest, current_user: User = Depends(get_current_user)) -> AIStandardResponse:
    service = AIService()
    context = payload.user_prompt
    if payload.history:
        history_text = "\n".join(f"{m.get('role')}: {m.get('content')}" for m in payload.history[-8:])
        context = f"Historico:\n{history_text}\n\nPrompt atual:\n{payload.user_prompt}"
    try:
        result = service.run_task(
            task_name="prompt_playground",
            context=context,
            system_prompt=payload.system_prompt,
            temperature=payload.temperature,
            endpoint="/api/ai/playground",
            user_id=current_user.id,
        )
        return AIStandardResponse(**result)
    except AIServiceError as exc:
        _raise_ai_http_error(exc)


@router.post("/agent-definition", response_model=AIStandardResponse)
def generate_agent_definition(payload: AgentBuilderRequest, current_user: User = Depends(get_current_user)) -> AIStandardResponse:
    service = AIService()
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "role": {"type": "string"},
            "goal": {"type": "string"},
            "tone": {"type": "string"},
            "system_prompt": {"type": "string"},
            "welcome_message": {"type": "string"},
            "suggested_channels": {"type": "array", "items": {"type": "string"}},
            "suggested_tools": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "name",
            "role",
            "goal",
            "tone",
            "system_prompt",
            "welcome_message",
            "suggested_channels",
            "suggested_tools",
        ],
        "additionalProperties": False,
    }
    try:
        result = service.run_task(
            task_name="agent_builder",
            context=payload.context,
            structured_schema=schema,
            endpoint="/api/ai/agent-definition",
            user_id=current_user.id,
        )
        return AIStandardResponse(**result)
    except AIServiceError as exc:
        _raise_ai_http_error(exc)


@router.post("/document-analysis", response_model=AIStandardResponse)
def document_analysis(payload: DocumentAnalysisRequest, current_user: User = Depends(get_current_user)) -> AIStandardResponse:
    service = AIService()
    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "key_points": {"type": "array", "items": {"type": "string"}},
            "action_items": {"type": "array", "items": {"type": "string"}},
            "faq": {"type": "array", "items": {"type": "string"}},
            "suggested_agent_use": {"type": "string"},
        },
        "required": ["summary", "key_points", "action_items", "faq", "suggested_agent_use"],
        "additionalProperties": False,
    }
    try:
        result = service.run_task(
            task_name="document_analysis",
            context=payload.content,
            structured_schema=schema,
            endpoint="/api/ai/document-analysis",
            user_id=current_user.id,
        )
        return AIStandardResponse(**result)
    except AIServiceError as exc:
        _raise_ai_http_error(exc)


@router.post("/analytics-insights", response_model=AIStandardResponse)
def analytics_insights(payload: AnalyticsInsightsRequest, current_user: User = Depends(get_current_user)) -> AIStandardResponse:
    service = AIService()
    schema = {
        "type": "object",
        "properties": {
            "executive_summary": {"type": "string"},
            "warnings": {"type": "array", "items": {"type": "string"}},
            "opportunities": {"type": "array", "items": {"type": "string"}},
            "recommendations": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["executive_summary", "warnings", "opportunities", "recommendations"],
        "additionalProperties": False,
    }
    try:
        result = service.run_task(
            task_name="analytics_insights",
            context=json.dumps(payload.metrics_json, ensure_ascii=True),
            structured_schema=schema,
            endpoint="/api/ai/analytics-insights",
            user_id=current_user.id,
        )
        return AIStandardResponse(**result)
    except AIServiceError as exc:
        _raise_ai_http_error(exc)


@router.post("/platform-assistant", response_model=AIStandardResponse)
def platform_assistant(payload: TaskTextRequest, current_user: User = Depends(get_current_user)) -> AIStandardResponse:
    service = AIService()
    try:
        result = service.run_task(
            task_name="platform_assistant",
            context=payload.prompt,
            endpoint="/api/ai/platform-assistant",
            user_id=current_user.id,
        )
        return AIStandardResponse(**result)
    except AIServiceError as exc:
        _raise_ai_http_error(exc)


@router.post("/workflow-builder", response_model=AIStandardResponse)
def workflow_builder(payload: WorkflowBuilderRequest, current_user: User = Depends(get_current_user)) -> AIStandardResponse:
    service = AIService()
    schema = {
        "type": "object",
        "properties": {
            "trigger": {"type": "string"},
            "conditions": {"type": "array", "items": {"type": "string"}},
            "actions": {"type": "array", "items": {"type": "string"}},
            "fallbacks": {"type": "array", "items": {"type": "string"}},
            "channel_targets": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["trigger", "conditions", "actions", "fallbacks", "channel_targets"],
        "additionalProperties": False,
    }
    try:
        result = service.run_task(
            task_name="workflow_builder",
            context=payload.context,
            structured_schema=schema,
            endpoint="/api/ai/workflow-builder",
            user_id=current_user.id,
        )
        return AIStandardResponse(**result)
    except AIServiceError as exc:
        _raise_ai_http_error(exc)


@router.post("/image-analysis", response_model=AIStandardResponse)
def image_analysis(payload: ImageAnalysisRequest, current_user: User = Depends(get_current_user)) -> AIStandardResponse:
    if not payload.image_url:
        raise HTTPException(status_code=422, detail="image_url é obrigatório no momento")
    service = AIService()
    try:
        image_bytes = _download_public_image(payload.image_url)
        result = service.analyze_image(
            image_bytes=image_bytes,
            prompt=payload.prompt or "Analise esta imagem para uso em marketing e operação.",
            user_id=current_user.id,
            endpoint="/api/ai/image-analysis",
        )
        return AIStandardResponse(**result)
    except HTTPException:
        raise
    except AIServiceError as exc:
        _raise_ai_http_error(exc)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao analisar imagem: {exc}") from exc
