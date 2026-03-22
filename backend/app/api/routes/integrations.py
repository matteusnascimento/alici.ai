from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.integration import IntegrationRead, IntegrationTestRequest, IntegrationTestResponse
from app.services.integration_service import IntegrationService
from app.services.openai_service import OpenAIService, OpenAIServiceError

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("", response_model=list[IntegrationRead])
def list_integrations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[IntegrationRead]:
    return IntegrationService(db).list_integrations(current_user)


@router.post("/openai/test", response_model=IntegrationTestResponse)
def test_openai(
    _: IntegrationTestRequest,
    __: User = Depends(get_current_user),
) -> IntegrationTestResponse:
    service = OpenAIService()
    if not service.api_key:
        return IntegrationTestResponse(
            provider="openai",
            status="warning",
            message="OPENAI_API_KEY nao configurada. Configure para testes reais.",
        )

    try:
        response = service.send_chat_message(messages=[{"role": "user", "content": "ping"}], temperature=0)
        return IntegrationTestResponse(provider="openai", status="ok", message=f"OpenAI conectado ({response['model']}).")
    except OpenAIServiceError as exc:
        return IntegrationTestResponse(provider="openai", status="error", message=str(exc))


@router.post("/whatsapp/test", response_model=IntegrationTestResponse)
def test_whatsapp(
    _: IntegrationTestRequest,
    __: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationTestResponse:
    return IntegrationService(db).test_provider("whatsapp")


@router.post("/instagram/test", response_model=IntegrationTestResponse)
def test_instagram(
    _: IntegrationTestRequest,
    __: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IntegrationTestResponse:
    return IntegrationService(db).test_provider("instagram")
