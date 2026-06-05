from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.agent import Agent
from app.models.agent_conversation import AgentConversation
from app.models.agent_message import AgentMessage
from app.models.lead import Lead
from app.models.reservation import Reservation
from app.models.user import User
from app.schemas.lead import LeadCreate, LeadRead, LeadUpdate
from app.schemas.reservation import ReservationCreate, ReservationRead, ReservationUpdate
from app.schemas.revenue import RevenueIntelligenceSnapshot, RevenueSeriesResponse
from app.services.lead_service import LeadService
from app.services.reservation_service import ReservationService
from app.services.revenue_service import RevenueService

router = APIRouter(prefix="/revenue", tags=["revenue"])

NO_REAL_DATA_MESSAGE = "Sem dados reais disponíveis. Conecte integrações para visualizar informações."


def _user_agent_ids(db: Session, user: User) -> list[int]:
    rows = db.query(Agent.id).filter(Agent.user_id == user.id).all()
    return [int(row[0]) for row in rows]


def _conversation_or_404(db: Session, user: User, conversation_id: int) -> AgentConversation:
    agent_ids = _user_agent_ids(db, user)
    if not agent_ids:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa nao encontrada")
    conversation = (
        db.query(AgentConversation)
        .filter(AgentConversation.id == conversation_id, AgentConversation.agent_id.in_(agent_ids))
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa nao encontrada")
    return conversation


@router.get("/overview", response_model=RevenueIntelligenceSnapshot)
def get_revenue_overview(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RevenueIntelligenceSnapshot:
    return RevenueService(db).get_snapshot(current_user, days=days)


@router.get("/kpis", response_model=dict[str, Any])
def get_revenue_kpis(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    snapshot = RevenueService(db).get_snapshot(current_user, days=days)
    summary = snapshot.summary
    has_data = summary.receita_total > 0 or summary.reservas_fechadas > 0 or summary.leads_recebidos > 0
    items = [
        {"key": "receita", "label": "Receita", "value": summary.receita_total, "unit": "BRL"},
        {"key": "reservas", "label": "Reservas", "value": summary.reservas_fechadas, "unit": "count"},
        {"key": "leads", "label": "Leads", "value": summary.leads_recebidos, "unit": "count"},
        {"key": "conversao", "label": "Conversao", "value": summary.conversao_total, "unit": "percent"},
        {"key": "roi", "label": "ROI", "value": summary.roi_estimado, "unit": "multiplier"},
        {
            "key": "forecast",
            "label": "Forecast",
            "value": round(summary.receita_total * 1.18, 2) if has_data else 0,
            "unit": "BRL",
        },
    ]
    return {
        "status": "ok" if has_data else "no_data",
        "message": "" if has_data else NO_REAL_DATA_MESSAGE,
        "items": items,
        "source": "revenue_service",
    }


@router.get("/channels", response_model=dict[str, Any])
def get_revenue_channels(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    snapshot = RevenueService(db).get_snapshot(current_user, days=days)
    total = sum(item.valor for item in snapshot.receita_por_canal)
    items = [
        {
            "key": item.label.lower().replace(" ", "_"),
            "label": item.label,
            "revenue": item.valor,
            "percentual": round((item.valor / total) * 100, 2) if total else 0,
        }
        for item in snapshot.receita_por_canal
    ]
    return {
        "status": "ok" if items else "no_data",
        "message": "" if items else NO_REAL_DATA_MESSAGE,
        "items": items,
        "source": "revenue_service",
    }


@router.get("/demand-map", response_model=dict[str, Any])
def get_revenue_demand_map(
    city: str | None = None,
    state: str | None = None,
    country: str | None = None,
    channel: str | None = None,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return get_origin_demand(
        city=city,
        state=state,
        country=country,
        channel=channel,
        days=days,
        current_user=current_user,
        db=db,
    )


@router.get("/events", response_model=dict[str, Any])
def get_revenue_events(
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    safe_limit = min(max(limit, 1), 100)
    agent_ids = _user_agent_ids(db, current_user)
    events: list[dict[str, Any]] = []

    reservations = (
        db.query(Reservation)
        .filter((Reservation.user_id == current_user.id) | (Reservation.user_id.is_(None)))
        .order_by(Reservation.created_at.desc())
        .limit(safe_limit)
        .all()
    )
    for item in reservations:
        events.append(
            {
                "id": f"reservation-{item.id}",
                "type": "reservation",
                "title": item.guest_name,
                "description": item.status,
                "amount": item.total_price,
                "channel": item.channel,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "source": "reservations",
            }
        )

    if agent_ids:
        conversations = (
            db.query(AgentConversation)
            .filter(AgentConversation.agent_id.in_(agent_ids))
            .order_by(AgentConversation.updated_at.desc())
            .limit(safe_limit)
            .all()
        )
        for item in conversations:
            events.append(
                {
                    "id": f"conversation-{item.id}",
                    "type": "conversation",
                    "title": item.external_user_id,
                    "description": item.status,
                    "amount": item.reservation_value,
                    "channel": item.channel_type,
                    "created_at": item.updated_at.isoformat() if item.updated_at else None,
                    "source": "agent_conversations",
                }
            )

    events = sorted(events, key=lambda item: str(item.get("created_at") or ""), reverse=True)[:safe_limit]
    return {
        "status": "ok" if events else "no_data",
        "message": "" if events else NO_REAL_DATA_MESSAGE,
        "items": events,
        "source": "database",
    }


@router.get("/series", response_model=RevenueSeriesResponse)
def get_revenue_series(
    days: int = 30,
    granularity: str = "daily",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RevenueSeriesResponse:
    return RevenueService(db).get_revenue_series(current_user, days=days, granularity=granularity)


@router.get("/charts/revenue", response_model=RevenueSeriesResponse)
def get_revenue_chart(
    days: int = 30,
    granularity: str = "daily",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RevenueSeriesResponse:
    return RevenueService(db).get_revenue_series(current_user, days=days, granularity=granularity)


@router.get("/charts/reservation-sources", response_model=dict[str, Any])
def get_reservation_sources(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    snapshot = RevenueService(db).get_snapshot(current_user, days=days)
    total = sum(item.valor for item in snapshot.receita_por_canal)
    return {
        "items": [
            {
                "label": item.label,
                "valor": item.valor,
                "percentual": round((item.valor / total) * 100, 2) if total else 0,
            }
            for item in snapshot.receita_por_canal
        ],
        "status": "ok" if snapshot.receita_por_canal else "no_data",
        "source": "revenue_service",
    }


@router.get("/business-pulse", response_model=dict[str, Any])
def get_business_pulse(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    snapshot = RevenueService(db).get_snapshot(current_user, days=days)
    summary = snapshot.summary
    has_activity = summary.receita_total > 0 or summary.reservas_fechadas > 0 or summary.leads_recebidos > 0
    if not has_activity:
        return {
            "status": "no_data",
            "score": None,
            "label": "Sem dados suficientes",
            "components": [],
            "source": "revenue_service",
        }

    conversion_score = min(35, max(0, round(summary.conversao_total * 1.4)))
    revenue_score = 20 if summary.receita_total > 0 else 0
    reservation_score = min(25, summary.reservas_fechadas * 2)
    channel_score = min(20, len(snapshot.receita_por_canal) * 5)
    score = min(100, conversion_score + revenue_score + reservation_score + channel_score)
    label = "Muito saudavel" if score >= 80 else "Saudavel" if score >= 60 else "Em atencao"
    return {
        "status": "ok",
        "score": score,
        "label": label,
        "components": [
            {"label": "Receita", "score": revenue_score},
            {"label": "Conversao", "score": conversion_score},
            {"label": "Reservas", "score": reservation_score},
            {"label": "Canais", "score": channel_score},
        ],
        "source": "revenue_service",
    }


@router.get("/audience/top-cities", response_model=dict[str, Any])
def get_top_cities(_: User = Depends(get_current_user)) -> dict[str, Any]:
    return {
        "items": [],
        "status": "insufficient_data",
        "reason": "Use /api/revenue/origin-demand para o novo Mapa de Origem e Demanda.",
    }


@router.get("/origin-demand", response_model=dict[str, Any])
def get_origin_demand(
    city: str | None = None,
    state: str | None = None,
    country: str | None = None,
    channel: str | None = None,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    snapshot = RevenueService(db).get_snapshot(current_user, days=days)
    rows = snapshot.mapa_origem_demanda
    if city:
        rows = [item for item in rows if (item.cidade or "").lower() == city.lower()]
    if state:
        rows = [item for item in rows if (item.estado or "").lower() == state.lower()]
    if country:
        rows = [item for item in rows if (item.pais or "").lower() == country.lower()]
    if channel:
        rows = [item for item in rows if item.canal.lower() == channel.lower()]
    return {
        "status": "ok" if rows else "no_data",
        "message": "" if rows else NO_REAL_DATA_MESSAGE,
        "items": [item.model_dump() for item in rows],
        "filters": {"city": city, "state": state, "country": country, "channel": channel, "days": days},
    }


@router.get("/customer-360", response_model=dict[str, Any])
def get_customer_360(
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    items = RevenueService(db).get_customer_360(current_user, limit=limit)
    return {
        "status": "ok" if items else "no_data",
        "message": "" if items else NO_REAL_DATA_MESSAGE,
        "items": [item.model_dump() for item in items],
        "source": "leads_reservations_conversations",
    }


@router.get("/control-room", response_model=dict[str, Any])
def get_control_room(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    snapshot = RevenueService(db).get_snapshot(current_user, days=30)
    agent_ids = _user_agent_ids(db, current_user)
    open_conversations = 0
    if agent_ids:
        open_conversations = (
            db.query(AgentConversation)
            .filter(AgentConversation.agent_id.in_(agent_ids), AgentConversation.status != "closed")
            .count()
        )
    pending_reservations = len([item for item in snapshot.reservas if item.status != "Fechada"])
    return {
        "conversas_abertas": open_conversations,
        "atendentes_online": None,
        "atendentes_online_status": "unavailable",
        "ia_em_atendimento": snapshot.summary.agentes_gerando_receita,
        "reservas_pendentes": pending_reservations,
        "source": "database",
    }


@router.get("/action-plans", response_model=dict[str, Any])
def get_action_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    snapshot = RevenueService(db).get_snapshot(current_user, days=30)
    actions = []
    if snapshot.summary.conversao_total < 10 and snapshot.summary.leads_recebidos > 0:
        actions.append(
            {
                "title": "Reduzir perda no funil",
                "reason": "Conversao abaixo de 10% no periodo.",
                "status": "recommended",
            }
        )
    if snapshot.receita_por_canal:
        top_channel = snapshot.receita_por_canal[0].label
        actions.append(
            {
                "title": f"Priorizar {top_channel}",
                "reason": "Canal com maior receita no periodo atual.",
                "status": "recommended",
            }
        )
    if snapshot.summary.leads_recebidos > 0 and snapshot.summary.reservas_fechadas == 0:
        actions.append(
            {
                "title": "Criar rotina de conversao",
                "reason": "Ha leads recebidos sem reservas fechadas no periodo.",
                "status": "recommended",
            }
        )
    return {
        "items": actions,
        "status": "ok" if actions else "no_data",
        "message": "" if actions else NO_REAL_DATA_MESSAGE,
        "source": "derived_from_revenue_service",
    }


@router.get("/inbox", response_model=dict[str, Any])
def get_revenue_inbox(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    agent_ids = _user_agent_ids(db, current_user)
    conversations = []
    if agent_ids:
        rows = (
            db.query(AgentConversation)
            .filter(AgentConversation.agent_id.in_(agent_ids))
            .order_by(AgentConversation.updated_at.desc())
            .limit(50)
            .all()
        )
        conversations = [
            {
                "id": item.id,
                "channel": item.channel_type,
                "contact": item.external_user_id,
                "status": item.status,
                "mode": item.status,
                "sales_stage": item.sales_stage,
                "reservation_value": item.reservation_value,
                "lead_source": item.lead_source,
                "assigned_to_human": item.assigned_to_human,
                "updated_at": item.updated_at,
            }
            for item in rows
        ]
    return {"conversations": conversations}


@router.get("/conversations", response_model=dict[str, Any])
def list_revenue_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    return get_revenue_inbox(current_user=current_user, db=db)


@router.get("/conversations/{conversation_id}", response_model=dict[str, Any])
def get_revenue_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    conversation = _conversation_or_404(db, current_user, conversation_id)
    messages = (
        db.query(AgentMessage)
        .filter(AgentMessage.conversation_id == conversation.id)
        .order_by(AgentMessage.created_at.asc())
        .all()
    )
    return {
        "conversation": {
            "id": conversation.id,
            "channel": conversation.channel_type,
            "contact": conversation.external_user_id,
            "status": conversation.status,
            "sales_stage": conversation.sales_stage,
            "reservation_value": conversation.reservation_value,
            "lead_source": conversation.lead_source,
            "assigned_to_human": conversation.assigned_to_human,
        },
        "messages": [
            {
                "id": item.id,
                "role": item.role,
                "content": item.content,
                "created_at": item.created_at,
            }
            for item in messages
        ],
    }


@router.patch("/conversations/{conversation_id}/mode", response_model=dict[str, Any])
def update_revenue_conversation_mode(
    conversation_id: int,
    payload: dict[str, str],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    mode = (payload.get("mode") or "").strip().lower()
    mode_to_status = {"ia": "active_ai", "ai": "active_ai", "humano": "human", "human": "human", "hibrido": "hybrid", "hybrid": "hybrid"}
    if mode not in mode_to_status:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="mode deve ser ia, humano ou hibrido")
    conversation = _conversation_or_404(db, current_user, conversation_id)
    conversation.status = mode_to_status[mode]
    db.commit()
    db.refresh(conversation)
    return {"id": conversation.id, "mode": mode, "status": conversation.status}


@router.get("/leads", response_model=list[LeadRead])
def list_revenue_leads(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[LeadRead]:
    return LeadService(db).list_leads()


@router.post("/leads", response_model=LeadRead)
def create_revenue_lead(
    payload: LeadCreate,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LeadRead:
    return LeadService(db).create_lead(payload)


@router.patch("/leads/{lead_id}", response_model=LeadRead)
def update_revenue_lead(
    lead_id: int,
    payload: LeadUpdate,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LeadRead:
    return LeadService(db).update_lead(lead_id, payload)


@router.get("/pipeline", response_model=dict[str, Any])
def get_revenue_pipeline(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    snapshot = RevenueService(db).get_snapshot(current_user, days=90)
    columns = [
        {"key": "novo_lead", "label": "Novo Lead"},
        {"key": "qualified", "label": "Qualificado"},
        {"key": "proposal", "label": "Proposta"},
        {"key": "negotiation", "label": "Negociacao"},
        {"key": "booked", "label": "Reserva/Venda"},
        {"key": "won", "label": "Ganho"},
        {"key": "lost", "label": "Perdido"},
    ]
    cards = [
        {
            "id": item.reserva,
            "cliente": item.cliente,
            "canal": item.canal,
            "valor": item.valor,
            "status": item.status,
            "responsavel": item.agente_responsavel,
            "origem": item.origem,
        }
        for item in snapshot.reservas
    ]
    return {"columns": columns, "cards": cards, "funnel": [item.model_dump() for item in snapshot.funil]}


@router.get("/reservations", response_model=list[ReservationRead])
def list_revenue_reservations(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ReservationRead]:
    rows = db.query(Reservation).order_by(Reservation.created_at.desc()).limit(100).all()
    return [ReservationRead.model_validate(item) for item in rows]


@router.post("/reservations", response_model=ReservationRead)
def create_revenue_reservation(
    payload: ReservationCreate,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReservationRead:
    return ReservationService(db).create_reservation(payload)


@router.patch("/reservations/{reservation_id}", response_model=ReservationRead)
def update_revenue_reservation(
    reservation_id: int,
    payload: ReservationUpdate,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReservationRead:
    return ReservationService(db).update_reservation(reservation_id, payload)


@router.get("/crm", response_model=dict[str, Any])
def get_revenue_crm(_: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    leads = db.query(Lead).order_by(Lead.updated_at.desc()).limit(100).all()
    return {
        "contacts": [LeadRead.model_validate(item).model_dump() for item in leads],
        "external_crm": {"status": "configuration_required", "providers": ["pipedrive", "hubspot"]},
    }


@router.get("/tasks", response_model=dict[str, Any])
def get_revenue_tasks(_: User = Depends(get_current_user)) -> dict[str, Any]:
    return {"items": [], "status": "unavailable", "reason": "Modelo de tarefas comerciais ainda nao existe no backend/app/models."}


@router.get("/post-sale", response_model=dict[str, Any])
def get_revenue_post_sale(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    snapshot = RevenueService(db).get_snapshot(current_user, days=90)
    return {"reservations": [item.model_dump() for item in snapshot.reservas], "status": "derived_from_revenue_reservations"}


@router.get("/forecast", response_model=dict[str, Any])
def get_revenue_forecast(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    snapshot = RevenueService(db).get_snapshot(current_user, days=30)
    revenue = snapshot.summary.receita_total
    has_data = revenue > 0 or snapshot.summary.reservas_fechadas > 0 or snapshot.summary.leads_recebidos > 0
    return {
        "status": "ok" if has_data else "no_data",
        "message": "" if has_data else NO_REAL_DATA_MESSAGE,
        "receita_provavel_mes": round(revenue * 1.18, 2),
        "reservas_provaveis": round(snapshot.summary.reservas_fechadas * 1.15),
        "leads_necessarios": max(snapshot.summary.leads_recebidos, 0),
        "conversoes_necessarias": max(snapshot.summary.reservas_fechadas, 0),
        "meta_atual": None,
        "meta_status": "not_configured",
        "gap_para_meta": None,
        "canal_maior_potencial": snapshot.receita_por_canal[0].label if snapshot.receita_por_canal else "Sem dados",
    }


@router.get("/insights", response_model=dict[str, Any])
def get_revenue_insights(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    snapshot = RevenueService(db).get_snapshot(current_user, days=30)
    insights = []
    if snapshot.receita_por_canal:
        top = snapshot.receita_por_canal[0]
        insights.append(
            {
                "type": "Crescimento",
                "severity": "info",
                "metric": "receita_por_canal",
                "recommendation": f"{top.label} lidera receita no periodo.",
                "action": "Priorizar atendimento e campanhas nesse canal.",
            }
        )
    if snapshot.summary.conversao_total < 10 and snapshot.summary.leads_recebidos > 0:
        insights.append(
            {
                "type": "Risco",
                "severity": "warning",
                "metric": "conversao_total",
                "recommendation": "Conversao abaixo de 10%.",
                "action": "Revisar tempo de resposta, proposta e handoff humano.",
            }
        )
    return {"items": insights, "source": "derived_from_revenue_service"}


@router.get("/reports", response_model=dict[str, Any])
def get_revenue_reports(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    snapshot = RevenueService(db).get_snapshot(current_user, days=30)
    series = RevenueService(db).get_revenue_series(current_user, days=30)
    return {
        "operacional": {
            "reservas": [item.model_dump() for item in snapshot.reservas],
            "leads": snapshot.summary.leads_recebidos,
            "conversoes": snapshot.summary.conversao_total,
            "receita": snapshot.summary.receita_total,
        },
        "integracoes": {
            "status": "use /api/integrations para status, falhas e sincronizacoes",
        },
        "ia": {
            "status": "use /api/usage e logs de AIRequestLog para uso, custos e historico",
        },
        "snapshot": snapshot.model_dump(),
        "series": series.model_dump(),
    }


@router.get("/reports/export")
def export_revenue_reports(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Response:
    snapshot = RevenueService(db).get_snapshot(current_user, days=30)
    lines = ["categoria,item,valor"]
    lines.append(f"operacional,receita,{snapshot.summary.receita_total}")
    lines.append(f"operacional,reservas,{snapshot.summary.reservas_fechadas}")
    lines.append(f"operacional,leads,{snapshot.summary.leads_recebidos}")
    lines.append(f"operacional,conversao,{snapshot.summary.conversao_total}")
    for item in snapshot.receita_por_canal:
        lines.append(f"canais,{item.label},{item.valor}")
    for item in snapshot.mapa_origem_demanda:
        label = " / ".join(filter(None, [item.cidade, item.estado, item.pais, item.canal]))
        lines.append(f"origem_demanda,{label},{item.receita}")
    return Response(
        content="\n".join(lines),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=axi-revenue-report.csv"},
    )
