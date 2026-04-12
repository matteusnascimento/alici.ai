from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.user import User
from app.schemas.integration import IntegrationTestResponse
from app.services.ai_service import AIConfigurationError, AIService, AIServiceError

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/test", response_model=IntegrationTestResponse)
def test_ai(_: User = Depends(get_current_user)) -> IntegrationTestResponse:
    service = AIService(provider="openai")
    try:
        result = service.healthcheck()
        return IntegrationTestResponse(
            provider="openai",
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
            provider="openai",
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
            provider="openai",
            status="error",
            message=exc.user_message,
            model=None,
            model_used=None,
            latency_ms=None,
            error_type=exc.code,
            status_code=exc.status_code,
        )
