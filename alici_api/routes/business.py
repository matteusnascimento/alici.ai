"""Business/CRM module routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from alici_api.dependencies import get_current_user
from alici_api.responses import Codes, success
from database import (
    atualizar_business_status,
    business_summary,
    criar_business_call,
    criar_business_contact,
    criar_business_deal,
    criar_business_contract,
    criar_business_group,
    criar_business_logistic,
    criar_business_meeting,
    criar_business_pipeline,
    criar_business_product,
    criar_business_quick_message,
    criar_business_task,
    listar_business_calls,
    listar_business_contacts,
    listar_business_contracts,
    listar_business_deals,
    listar_business_groups,
    listar_business_logistics,
    listar_business_meetings,
    listar_business_pipelines,
    listar_business_products,
    listar_business_quick_messages,
    listar_business_revenue_goals,
    listar_business_tasks,
    salvar_business_revenue_goal,
)

router = APIRouter(prefix="/business", tags=["business"])


class PipelineCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    stages: list[str] | None = None
    is_default: bool = False


class ContactCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    email: str | None = Field(default=None, max_length=160)
    phone: str | None = Field(default=None, max_length=40)
    company: str | None = Field(default=None, max_length=160)
    status: str = Field(default="prospect", max_length=40)
    source: str = Field(default="manual", max_length=40)


class DealCreate(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    value_cents: int = Field(default=0, ge=0)
    pipeline_id: int | None = None
    contact_id: int | None = None
    stage: str = Field(default="novo", max_length=60)
    status: str = Field(default="open", max_length=40)
    probability: int = Field(default=10, ge=0, le=100)
    expected_close_date: str | None = Field(default=None, max_length=40)


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    description: str | None = Field(default=None, max_length=1000)
    price_cents: int = Field(default=0, ge=0)
    status: str = Field(default="active", max_length=40)


class CallCreate(BaseModel):
    phone: str = Field(min_length=3, max_length=40)
    contact_id: int | None = None
    direction: str = Field(default="outbound", max_length=30)
    outcome: str = Field(default="pending", max_length=40)
    duration_seconds: int = Field(default=0, ge=0)
    notes: str | None = Field(default=None, max_length=1000)


class GenericBusinessCreate(BaseModel):
    title: str | None = Field(default=None, max_length=180)
    name: str | None = Field(default=None, max_length=180)
    description: str | None = Field(default=None, max_length=1000)
    body: str | None = Field(default=None, max_length=2000)
    contact_id: int | None = None
    deal_id: int | None = None
    value_cents: int = Field(default=0, ge=0)
    scheduled_at: str | None = Field(default=None, max_length=80)
    due_at: str | None = Field(default=None, max_length=80)
    signed_at: str | None = Field(default=None, max_length=80)
    status: str = Field(default="active", max_length=40)
    priority: str = Field(default="medium", max_length=40)
    category: str = Field(default="atendimento", max_length=80)
    tracking_code: str | None = Field(default=None, max_length=120)
    notes: str | None = Field(default=None, max_length=1000)


class RevenueGoalCreate(BaseModel):
    year: int = Field(ge=2020, le=2100)
    month: int = Field(ge=1, le=12)
    target_cents: int = Field(default=0, ge=0)


class StatusUpdate(BaseModel):
    status: str = Field(min_length=2, max_length=40)


def _user_id(user: dict) -> int:
    return int(user["id"])


@router.get("/summary")
def get_summary(user=Depends(get_current_user)):
    return success(Codes.SUCCESS_DEFAULT, data=business_summary(_user_id(user)))


@router.get("/pipelines")
def get_pipelines(user=Depends(get_current_user)):
    return success(Codes.SUCCESS_DEFAULT, data=listar_business_pipelines(_user_id(user)))


@router.post("/pipelines")
def create_pipeline(payload: PipelineCreate, user=Depends(get_current_user)):
    item = criar_business_pipeline(
        _user_id(user),
        payload.name,
        description=payload.description,
        stages=payload.stages,
        is_default=payload.is_default,
    )
    return success(Codes.SUCCESS_DEFAULT, data=item, message="Pipeline criado")


@router.get("/contacts")
def get_contacts(
    search: str | None = Query(default=None, max_length=120),
    status: str | None = Query(default=None, max_length=40),
    user=Depends(get_current_user),
):
    return success(Codes.SUCCESS_DEFAULT, data=listar_business_contacts(_user_id(user), search=search, status=status))


@router.post("/contacts")
def create_contact(payload: ContactCreate, user=Depends(get_current_user)):
    item = criar_business_contact(
        _user_id(user),
        payload.name,
        email=payload.email,
        phone=payload.phone,
        company=payload.company,
        status=payload.status,
        source=payload.source,
    )
    return success(Codes.SUCCESS_DEFAULT, data=item, message="Contato criado")


@router.get("/deals")
def get_deals(
    search: str | None = Query(default=None, max_length=120),
    status: str | None = Query(default=None, max_length=40),
    user=Depends(get_current_user),
):
    return success(Codes.SUCCESS_DEFAULT, data=listar_business_deals(_user_id(user), search=search, status=status))


@router.post("/deals")
def create_deal(payload: DealCreate, user=Depends(get_current_user)):
    item = criar_business_deal(
        _user_id(user),
        payload.title,
        value_cents=payload.value_cents,
        pipeline_id=payload.pipeline_id,
        contact_id=payload.contact_id,
        stage=payload.stage,
        status=payload.status,
        probability=payload.probability,
        expected_close_date=payload.expected_close_date,
    )
    return success(Codes.SUCCESS_DEFAULT, data=item, message="Negocio criado")


@router.get("/products")
def get_products(
    search: str | None = Query(default=None, max_length=120),
    status: str | None = Query(default=None, max_length=40),
    user=Depends(get_current_user),
):
    return success(Codes.SUCCESS_DEFAULT, data=listar_business_products(_user_id(user), search=search, status=status))


@router.post("/products")
def create_product(payload: ProductCreate, user=Depends(get_current_user)):
    item = criar_business_product(
        _user_id(user),
        payload.name,
        description=payload.description,
        price_cents=payload.price_cents,
        status=payload.status,
    )
    return success(Codes.SUCCESS_DEFAULT, data=item, message="Produto criado")


@router.get("/calls")
def get_calls(user=Depends(get_current_user)):
    return success(Codes.SUCCESS_DEFAULT, data=listar_business_calls(_user_id(user)))


@router.post("/calls")
def create_call(payload: CallCreate, user=Depends(get_current_user)):
    item = criar_business_call(
        _user_id(user),
        payload.phone,
        contact_id=payload.contact_id,
        direction=payload.direction,
        outcome=payload.outcome,
        duration_seconds=payload.duration_seconds,
        notes=payload.notes,
    )
    return success(Codes.SUCCESS_DEFAULT, data=item, message="Ligacao registrada")


@router.get("/groups")
def get_groups(search: str | None = Query(default=None, max_length=120), status: str | None = Query(default=None, max_length=40), user=Depends(get_current_user)):
    return success(Codes.SUCCESS_DEFAULT, data=listar_business_groups(_user_id(user), search=search, status=status))


@router.post("/groups")
def create_group(payload: GenericBusinessCreate, user=Depends(get_current_user)):
    name = payload.name or payload.title
    if not name:
        raise HTTPException(status_code=422, detail="Nome obrigatorio")
    return success(Codes.SUCCESS_DEFAULT, data=criar_business_group(_user_id(user), name, payload.description, payload.status), message="Grupo criado")


@router.get("/meetings")
def get_meetings(search: str | None = Query(default=None, max_length=120), status: str | None = Query(default=None, max_length=40), user=Depends(get_current_user)):
    return success(Codes.SUCCESS_DEFAULT, data=listar_business_meetings(_user_id(user), search=search, status=status))


@router.post("/meetings")
def create_meeting(payload: GenericBusinessCreate, user=Depends(get_current_user)):
    if not payload.title:
        raise HTTPException(status_code=422, detail="Titulo obrigatorio")
    return success(Codes.SUCCESS_DEFAULT, data=criar_business_meeting(_user_id(user), payload.title, payload.contact_id, payload.scheduled_at, payload.status or "scheduled", payload.notes), message="Reuniao criada")


@router.get("/contracts")
def get_contracts(search: str | None = Query(default=None, max_length=120), status: str | None = Query(default=None, max_length=40), user=Depends(get_current_user)):
    return success(Codes.SUCCESS_DEFAULT, data=listar_business_contracts(_user_id(user), search=search, status=status))


@router.post("/contracts")
def create_contract(payload: GenericBusinessCreate, user=Depends(get_current_user)):
    if not payload.title:
        raise HTTPException(status_code=422, detail="Titulo obrigatorio")
    return success(Codes.SUCCESS_DEFAULT, data=criar_business_contract(_user_id(user), payload.title, payload.contact_id, payload.deal_id, payload.value_cents, payload.status or "draft", payload.signed_at), message="Contrato criado")


@router.get("/tasks")
def get_tasks(search: str | None = Query(default=None, max_length=120), status: str | None = Query(default=None, max_length=40), user=Depends(get_current_user)):
    return success(Codes.SUCCESS_DEFAULT, data=listar_business_tasks(_user_id(user), search=search, status=status))


@router.post("/tasks")
def create_task(payload: GenericBusinessCreate, user=Depends(get_current_user)):
    if not payload.title:
        raise HTTPException(status_code=422, detail="Titulo obrigatorio")
    return success(Codes.SUCCESS_DEFAULT, data=criar_business_task(_user_id(user), payload.title, payload.contact_id, payload.due_at, payload.status or "open", payload.priority), message="Tarefa criada")


@router.get("/quick-messages")
def get_quick_messages(search: str | None = Query(default=None, max_length=120), status: str | None = Query(default=None, max_length=40), user=Depends(get_current_user)):
    return success(Codes.SUCCESS_DEFAULT, data=listar_business_quick_messages(_user_id(user), search=search, status=status))


@router.post("/quick-messages")
def create_quick_message(payload: GenericBusinessCreate, user=Depends(get_current_user)):
    if not payload.title or not payload.body:
        raise HTTPException(status_code=422, detail="Titulo e mensagem obrigatorios")
    return success(Codes.SUCCESS_DEFAULT, data=criar_business_quick_message(_user_id(user), payload.title, payload.body, payload.category, payload.status), message="Mensagem rapida criada")


@router.get("/logistics")
def get_logistics(search: str | None = Query(default=None, max_length=120), status: str | None = Query(default=None, max_length=40), user=Depends(get_current_user)):
    return success(Codes.SUCCESS_DEFAULT, data=listar_business_logistics(_user_id(user), search=search, status=status))


@router.post("/logistics")
def create_logistic(payload: GenericBusinessCreate, user=Depends(get_current_user)):
    if not payload.title:
        raise HTTPException(status_code=422, detail="Titulo obrigatorio")
    return success(Codes.SUCCESS_DEFAULT, data=criar_business_logistic(_user_id(user), payload.title, payload.contact_id, payload.status or "pending", payload.tracking_code, payload.notes), message="Evento logistico criado")


@router.get("/revenue-goals")
def get_revenue_goals(user=Depends(get_current_user)):
    return success(Codes.SUCCESS_DEFAULT, data=listar_business_revenue_goals(_user_id(user)))


@router.post("/revenue-goals")
def save_revenue_goal(payload: RevenueGoalCreate, user=Depends(get_current_user)):
    return success(Codes.SUCCESS_DEFAULT, data=salvar_business_revenue_goal(_user_id(user), payload.year, payload.month, payload.target_cents), message="Meta salva")


@router.patch("/{resource}/{item_id}/status")
def update_status(resource: str, item_id: int, payload: StatusUpdate, user=Depends(get_current_user)):
    table_map = {
        "contacts": "business_contacts",
        "deals": "business_deals",
        "products": "business_products",
        "groups": "business_groups",
        "meetings": "business_meetings",
        "contracts": "business_contracts",
        "tasks": "business_tasks",
        "quick-messages": "business_quick_messages",
        "logistics": "business_logistics",
    }
    table = table_map.get(resource)
    if not table:
        raise HTTPException(status_code=404, detail="Recurso nao encontrado")
    item = atualizar_business_status(table, _user_id(user), item_id, payload.status)
    return success(Codes.SUCCESS_DEFAULT, data=item, message="Status atualizado")
