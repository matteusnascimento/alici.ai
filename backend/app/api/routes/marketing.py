from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.marketing import (
    MarketingCampaignRequest,
    MarketingCampaignResponse,
    MarketingAudienceCreate,
    MarketingAudienceRead,
    MarketingCalendarEventCreate,
    MarketingCalendarEventRead,
    MarketingCampaignListItem,
    MarketingCampaignListResponse,
    MarketingChannelRevenueResponse,
    MarketingContentRequest,
    MarketingContentResponse,
    MarketingCopyRequest,
    MarketingCopyResponse,
    MarketingDataStatus,
    MarketingFunnelResponse,
    MarketingImagePromptResponse,
    MarketingKpiRead,
    MarketingOverviewResponse,
    MarketingProjectCreate,
    MarketingProjectRead,
    MarketingProjectUpdate,
    MarketingPublishRequest,
    MarketingPublishResponse,
    MarketingRevenueInvestmentResponse,
    MarketingTool,
)
from app.services.ai_service import AIServiceError
from app.services.billing_service import BillingService
from app.services.marketing_service import MarketingService

router = APIRouter(prefix="/marketing", tags=["marketing"])


def _empty_marketing_message(resource: str) -> str:
    return f"Sem dados reais de {resource}. Conecte integracoes ou crie registros operacionais."


def _marketing_kpis() -> list[MarketingKpiRead]:
    return [
        MarketingKpiRead(key="investment", label="Investimento", message="Conecte Meta Ads ou Google Ads para medir investimento real."),
        MarketingKpiRead(key="revenue", label="Receita gerada", message="Integre Revenue para atribuir receita real a campanhas."),
        MarketingKpiRead(key="roas", label="ROAS", message="Sem custo e receita reais para calcular ROAS."),
        MarketingKpiRead(key="leads", label="Leads gerados", message="Sem leads reais atribuidos a campanhas."),
        MarketingKpiRead(key="reservations", label="Reservas geradas", message="Sem reservas reais atribuidas a campanhas."),
    ]


@router.get("/overview", response_model=MarketingOverviewResponse)
def marketing_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MarketingOverviewResponse:
    projects = MarketingService(db).list_projects(current_user)
    return MarketingOverviewResponse(
        status="empty" if not projects else "partial",
        projects_count=len(projects),
        kpis=_marketing_kpis(),
        message="Marketing Operations usa apenas dados reais; metricas externas dependem de integracoes configuradas.",
    )


@router.get("/kpis", response_model=list[MarketingKpiRead])
def marketing_kpis(_: User = Depends(get_current_user)) -> list[MarketingKpiRead]:
    return _marketing_kpis()


@router.get("/charts/revenue-investment", response_model=MarketingRevenueInvestmentResponse)
def marketing_revenue_investment(_: User = Depends(get_current_user)) -> MarketingRevenueInvestmentResponse:
    return MarketingRevenueInvestmentResponse(status="empty", message=_empty_marketing_message("receita x investimento"))


@router.get("/charts/revenue-by-channel", response_model=MarketingChannelRevenueResponse)
def marketing_revenue_by_channel(_: User = Depends(get_current_user)) -> MarketingChannelRevenueResponse:
    return MarketingChannelRevenueResponse(status="empty", message=_empty_marketing_message("receita por canal"))


@router.get("/funnel", response_model=MarketingFunnelResponse)
def marketing_funnel(_: User = Depends(get_current_user)) -> MarketingFunnelResponse:
    return MarketingFunnelResponse(status="empty", message=_empty_marketing_message("funil"))


@router.get("/action-plans", response_model=list[MarketingDataStatus])
def marketing_action_plans(_: User = Depends(get_current_user)) -> list[MarketingDataStatus]:
    return []


@router.get("/campaigns", response_model=MarketingCampaignListResponse)
def marketing_campaigns(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MarketingCampaignListResponse:
    projects = MarketingService(db).list_projects(current_user)
    return MarketingCampaignListResponse(
        status="empty" if not projects else "partial",
        campaigns=[
            MarketingCampaignListItem(
                id=project.id,
                name=project.name,
                objective=project.objective,
                audience=project.audience,
                status=project.status,
                source="marketing_projects",
                channels=project.channels,
                budget=project.budget,
                last_publish_error=project.last_publish_error,
            )
            for project in projects
        ],
        message="Campanhas externas dependem de integracoes configuradas; projetos internos sao listados como origem real.",
    )


@router.post("/campaigns", response_model=MarketingProjectRead)
def create_campaign(
    payload: MarketingProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingProjectRead:
    return MarketingService(db).create_project(current_user, payload)


@router.patch("/campaigns/{campaign_id}", response_model=MarketingProjectRead)
def update_campaign(
    campaign_id: int,
    payload: MarketingProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingProjectRead:
    return MarketingService(db).update_project(current_user, campaign_id, payload)


@router.post("/campaigns/{campaign_id}/publish", response_model=MarketingPublishResponse)
def publish_campaign(
    campaign_id: int,
    payload: MarketingPublishRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingPublishResponse:
    return MarketingService(db).publish_campaign(current_user, campaign_id, payload.channels)


@router.get("/calendar", response_model=list[MarketingCalendarEventRead])
def marketing_calendar(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[MarketingCalendarEventRead]:
    return MarketingService(db).list_calendar_events(current_user)


@router.post("/calendar/events", response_model=MarketingCalendarEventRead)
def create_calendar_event(
    payload: MarketingCalendarEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingCalendarEventRead:
    return MarketingService(db).create_calendar_event(current_user, payload)


@router.get("/content", response_model=list[MarketingDataStatus])
def marketing_content(_: User = Depends(get_current_user)) -> list[MarketingDataStatus]:
    return []


@router.get("/audiences", response_model=list[MarketingAudienceRead])
def marketing_audiences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[MarketingAudienceRead]:
    return MarketingService(db).list_audiences(current_user)


@router.post("/audiences", response_model=MarketingAudienceRead)
def create_audience(
    payload: MarketingAudienceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingAudienceRead:
    return MarketingService(db).create_audience(current_user, payload)


@router.get("/automations", response_model=list[MarketingDataStatus])
def marketing_automations(_: User = Depends(get_current_user)) -> list[MarketingDataStatus]:
    return []


@router.get("/reports", response_model=list[MarketingDataStatus])
def marketing_reports(_: User = Depends(get_current_user)) -> list[MarketingDataStatus]:
    return []


@router.get("/insights", response_model=list[MarketingDataStatus])
def marketing_insights(_: User = Depends(get_current_user)) -> list[MarketingDataStatus]:
    return []


@router.get("/tasks", response_model=list[MarketingDataStatus])
def marketing_tasks(_: User = Depends(get_current_user)) -> list[MarketingDataStatus]:
    return []


@router.get("/activity", response_model=list[MarketingDataStatus])
def marketing_activity(_: User = Depends(get_current_user)) -> list[MarketingDataStatus]:
    return []


@router.post("/campaign", response_model=MarketingCampaignResponse)
def generate_campaign(
    payload: MarketingCampaignRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingCampaignResponse:
    BillingService(db).assert_can_use(current_user, "messages", 1)
    try:
        result = MarketingService(db).generate(payload)
        BillingService(db).record_usage(current_user, "messages", 1, source="marketing")
        return result
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc


@router.get("/tools", response_model=list[MarketingTool])
def list_tools(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[MarketingTool]:
    return MarketingService(db).list_tools()


@router.post("/generate-copy", response_model=MarketingCopyResponse)
def generate_copy(
    payload: MarketingCopyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingCopyResponse:
    BillingService(db).assert_can_use(current_user, "messages", 1)
    try:
        result = MarketingService(db).generate_copy(payload.prompt)
        BillingService(db).record_usage(current_user, "messages", 1, source="marketing")
        return result
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc


@router.post("/generate-content", response_model=MarketingContentResponse)
def generate_content(
    payload: MarketingContentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingContentResponse:
    BillingService(db).assert_can_use(current_user, "messages", 1)
    try:
        result = MarketingService(db).generate_content(current_user, payload)
        BillingService(db).record_usage(current_user, "messages", 1, source="marketing")
        return result
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc


@router.post("/generate-image-prompt", response_model=MarketingImagePromptResponse)
def generate_image_prompt(
    payload: MarketingCopyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingImagePromptResponse:
    BillingService(db).assert_can_use(current_user, "messages", 1)
    try:
        result = MarketingService(db).generate_image_prompt(payload.prompt)
        BillingService(db).record_usage(current_user, "messages", 1, source="marketing")
        return result
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc


@router.post("/projects", response_model=MarketingProjectRead)
def create_project(
    payload: MarketingProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingProjectRead:
    return MarketingService(db).create_project(current_user, payload)


@router.get("/plans", response_model=list[MarketingProjectRead])
def list_plans(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[MarketingProjectRead]:
    return MarketingService(db).list_projects(current_user)


@router.post("/plans", response_model=MarketingProjectRead)
def create_plan(
    payload: MarketingProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingProjectRead:
    return MarketingService(db).create_project(current_user, payload)


@router.patch("/plans/{plan_id}", response_model=MarketingProjectRead)
def update_plan(
    plan_id: int,
    payload: MarketingProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingProjectRead:
    return MarketingService(db).update_project(current_user, plan_id, payload)


@router.get("/projects", response_model=list[MarketingProjectRead])
def list_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[MarketingProjectRead]:
    return MarketingService(db).list_projects(current_user)


@router.get("/projects/{project_id}", response_model=MarketingProjectRead)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingProjectRead:
    return MarketingService(db).get_project(current_user, project_id)


@router.patch("/projects/{project_id}", response_model=MarketingProjectRead)
def update_project(
    project_id: int,
    payload: MarketingProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingProjectRead:
    return MarketingService(db).update_project(current_user, project_id, payload)


@router.post("/projects/{project_id}/publish", response_model=MarketingPublishResponse)
def publish_project(
    project_id: int,
    payload: MarketingPublishRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingPublishResponse:
    return MarketingService(db).publish_campaign(current_user, project_id, payload.channels)


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    MarketingService(db).delete_project(current_user, project_id)


@router.post("/projects/{project_id}/generate", response_model=MarketingCampaignResponse)
def generate_for_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MarketingCampaignResponse:
    BillingService(db).assert_can_use(current_user, "messages", 1)
    try:
        result = MarketingService(db).generate_for_project(current_user, project_id)
        BillingService(db).record_usage(current_user, "messages", 1, source="marketing")
        return result
    except AIServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc
