from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime, timedelta
import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.agent_conversation import AgentConversation
from app.models.agent_log import AgentLog
from app.models.agent_message import AgentMessage
from app.models.marketing_project import MarketingProject
from app.models.reservation import Reservation
from app.models.user import User
from app.services.website_tracker_service import WebsiteTrackerService
from app.schemas.revenue import (
    RevenueBreakdownItem,
    RevenueFunnelStep,
    RevenueIntelligenceSnapshot,
    RevenueOriginDemandItem,
    RevenueOpportunityStatusItem,
    RevenueRemarketing,
    RevenueReservationItem,
    RevenueSeriesPoint,
    RevenueSeriesResponse,
    RevenueSummary,
)


_CLOSED_STATUS = {"closed", "closed_won", "won", "reservation_closed", "booked", "fechado"}
_PROPOSAL_STATUS = {"proposal_sent", "proposal", "awaiting_response", "aguardando_resposta"}
_HIGH_INTEREST_STATUS = {"interest_high", "high_interest", "interesse_alto"}
_REMARKETING_STATUS = {"remarketing", "recovery", "reactivated", "recuperacao"}
_AWAITING_STATUS = {"awaiting_response", "aguardando_resposta"}


class RevenueService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _json_loads(raw: str | None) -> dict[str, Any]:
        if not raw:
            return {}
        try:
            value = json.loads(raw)
            if isinstance(value, dict):
                return value
            return {}
        except Exception:
            return {}

    @staticmethod
    def _normalize_status(value: str | None) -> str:
        return (value or "").strip().lower()

    @staticmethod
    def _normalize_stage(value: str | None) -> str:
        return (value or "").strip().lower().replace("-", "_").replace(" ", "_")

    @staticmethod
    def _is_closed(stage: str) -> bool:
        return stage in _CLOSED_STATUS or stage == "fechado"

    @staticmethod
    def _extract_number(payload: dict[str, Any], keys: tuple[str, ...]) -> float:
        for key in keys:
            value = payload.get(key)
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                cleaned = value.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
                try:
                    return float(cleaned)
                except Exception:
                    continue
        return 0.0

    @staticmethod
    def _extract_actions(payload: dict[str, Any]) -> list[dict[str, Any]]:
        actions = payload.get("actions")
        if isinstance(actions, list):
            return [item for item in actions if isinstance(item, dict)]
        return []

    @staticmethod
    def _channel_label(channel_type: str) -> str:
        label = channel_type.replace("_", " ").strip()
        return label.title() if label else "Desconhecido"

    def get_snapshot(self, user: User, days: int = 30) -> RevenueIntelligenceSnapshot:
        window_start = datetime.now(UTC) - timedelta(days=max(1, min(days, 365)))

        agents = self.db.query(Agent).filter(Agent.user_id == user.id).all()
        agent_name_by_id = {item.id: item.nome for item in agents}

        conversations = (
            self.db.query(AgentConversation)
            .join(Agent, Agent.id == AgentConversation.agent_id)
            .filter(Agent.user_id == user.id, AgentConversation.created_at >= window_start)
            .all()
        )
        conversation_ids = [item.id for item in conversations]

        logs_by_conversation: dict[int, list[AgentLog]] = defaultdict(list)
        if conversation_ids:
            logs = (
                self.db.query(AgentLog)
                .filter(AgentLog.conversation_id.in_(conversation_ids), AgentLog.created_at >= window_start)
                .all()
            )
            for log in logs:
                if log.conversation_id is not None:
                    logs_by_conversation[int(log.conversation_id)].append(log)

        user_messages_by_conversation: dict[int, int] = defaultdict(int)
        assistant_messages_by_conversation: dict[int, int] = defaultdict(int)
        if conversation_ids:
            messages = (
                self.db.query(AgentMessage)
                .filter(AgentMessage.conversation_id.in_(conversation_ids), AgentMessage.created_at >= window_start)
                .all()
            )
            for message in messages:
                if message.role == "user":
                    user_messages_by_conversation[message.conversation_id] += 1
                if message.role == "assistant":
                    assistant_messages_by_conversation[message.conversation_id] += 1

        projects_count = (
            self.db.query(MarketingProject)
            .filter(MarketingProject.user_id == user.id, MarketingProject.created_at >= window_start)
            .count()
        )

        reservations: list[RevenueReservationItem] = []
        explicit_reservations = (
            self.db.query(Reservation)
            .filter(Reservation.created_at >= window_start)
            .all()
        )
        revenue_by_channel: dict[str, float] = defaultdict(float)
        revenue_by_agent: dict[str, float] = defaultdict(float)
        source_counter: dict[str, int] = defaultdict(int)
        opportunity_counts: dict[str, int] = defaultdict(int)

        leads_received = len(conversations) + len(explicit_reservations)
        qualified_count = 0
        advanced_count = 0
        proposal_count = 0
        closed_count = 0
        remarketing_leads = 0
        reactivated_leads = 0
        recovered_reservations = 0
        recovered_revenue = 0.0
        total_revenue = 0.0

        for reservation in explicit_reservations:
            is_closed_reservation = self._normalize_status(reservation.status) not in {"cancelled", "canceled", "cancelada"}
            channel_label = reservation.channel or "Reserva direta"
            source_label = reservation.source or channel_label
            value = float(reservation.total_price or 0.0)
            if is_closed_reservation:
                closed_count += 1
                total_revenue += value
                revenue_by_channel[channel_label] += value
                source_counter[source_label] += 1
                reservations.append(
                    RevenueReservationItem(
                        reserva=reservation.reservation_id,
                        cliente=reservation.guest_name,
                        canal=channel_label,
                        origem=source_label,
                        valor=value,
                        status="Fechada",
                        agente_responsavel="Sistema",
                    )
                )

        for conversation in conversations:
            status = self._normalize_status(conversation.status)
            stage = self._normalize_stage(conversation.sales_stage)
            logs = logs_by_conversation.get(conversation.id, [])

            inferred_value = conversation.reservation_value or 0.0
            inferred_source = (conversation.lead_source or "").strip() or "Organico"
            is_remarketing = bool(conversation.is_remarketing) or status in _REMARKETING_STATUS
            is_closed = self._is_closed(stage) or status in _CLOSED_STATUS
            has_qualify_action = False
            has_proposal_action = False

            for log in logs:
                metadata = self._json_loads(log.metadata_json)
                inferred_value = max(
                    inferred_value,
                    self._extract_number(metadata, ("reservation_value", "booking_value", "sale_value", "amount", "revenue")),
                )
                source = metadata.get("source") or metadata.get("campaign")
                if isinstance(source, str) and source.strip():
                    inferred_source = source.strip()
                for action in self._extract_actions(metadata):
                    action_type = str(action.get("type") or "").strip().lower()
                    if action_type in {"save_lead", "qualify_lead"}:
                        has_qualify_action = True
                    if action_type in {"send_proposal", "proposal", "create_quote"}:
                        has_proposal_action = True
                    if action_type in {"close_reservation", "book_reservation", "mark_won"}:
                        is_closed = True
                    if action_type in {"remarketing", "recover_lead", "reactivate_lead"}:
                        is_remarketing = True
                        reactivated_leads += 1
                    action_value = self._extract_number(
                        action,
                        ("reservation_value", "booking_value", "sale_value", "amount", "revenue"),
                    )
                    inferred_value = max(inferred_value, action_value)
                    action_source = action.get("source") or action.get("campaign")
                    if isinstance(action_source, str) and action_source.strip():
                        inferred_source = action_source.strip()

            if has_qualify_action or stage in _HIGH_INTEREST_STATUS or status in _HIGH_INTEREST_STATUS:
                qualified_count += 1
            if assistant_messages_by_conversation.get(conversation.id, 0) >= 2:
                advanced_count += 1
            if has_proposal_action or stage in _PROPOSAL_STATUS or status in _PROPOSAL_STATUS:
                proposal_count += 1

            if is_remarketing:
                remarketing_leads += 1

            if inferred_source:
                source_counter[inferred_source] += 1

            if is_closed:
                closed_count += 1
                total_revenue += inferred_value

                channel_label = self._channel_label(conversation.channel_type)
                agent_label = agent_name_by_id.get(conversation.agent_id, f"Agente {conversation.agent_id}")
                revenue_by_channel[channel_label] += inferred_value
                revenue_by_agent[agent_label] += inferred_value

                normalized_source = inferred_source.lower()
                if is_remarketing or "remarketing" in normalized_source or "reativ" in normalized_source:
                    recovered_reservations += 1
                    recovered_revenue += inferred_value

                reservations.append(
                    RevenueReservationItem(
                        reserva=str(conversation.id),
                        cliente=conversation.external_user_id or f"Contato {conversation.id}",
                        canal=channel_label,
                        origem=inferred_source,
                        valor=inferred_value,
                        status="Fechada",
                        agente_responsavel=agent_label,
                    )
                )
            else:
                if len(reservations) < 12:
                    reservations.append(
                        RevenueReservationItem(
                            reserva=str(conversation.id),
                            cliente=conversation.external_user_id or f"Contato {conversation.id}",
                            canal=self._channel_label(conversation.channel_type),
                            origem=inferred_source,
                            valor=max(inferred_value, 0.0),
                            status="Pendente",
                            agente_responsavel=agent_name_by_id.get(conversation.agent_id, f"Agente {conversation.agent_id}"),
                        )
                    )

            normalized = stage or status or "novo_lead"
            if normalized in {"fechado", *list(_CLOSED_STATUS)}:
                opportunity_counts["Fechado"] += 1
            elif normalized in _AWAITING_STATUS:
                opportunity_counts["Aguardando resposta"] += 1
            elif normalized in _PROPOSAL_STATUS:
                opportunity_counts["Proposta enviada"] += 1
            elif normalized in _HIGH_INTEREST_STATUS:
                opportunity_counts["Interesse alto"] += 1
            elif normalized in _REMARKETING_STATUS:
                opportunity_counts["Recuperacao"] += 1
            elif normalized in {"lost", "perdido", "closed_lost"}:
                opportunity_counts["Perdido"] += 1
            elif normalized in {"active", "active_ai", "in_conversation", "em_conversa"}:
                opportunity_counts["Em conversa"] += 1
            else:
                opportunity_counts["Novo lead"] += 1

        reservations = sorted(
            reservations,
            key=lambda item: (0 if item.status == "Fechada" else 1, -item.valor, -int(item.reserva)),
        )[:15]

        # Garante coerencia do funil sem apagar conversoes reais.
        proposal_count = max(proposal_count, closed_count)
        advanced_count = max(advanced_count, proposal_count)
        qualified_count = max(qualified_count, advanced_count)

        qualified_count = min(qualified_count, leads_received)
        advanced_count = min(advanced_count, qualified_count)
        proposal_count = min(proposal_count, advanced_count)
        closed_count = min(closed_count, proposal_count)

        ticket_medio = (total_revenue / closed_count) if closed_count > 0 else 0.0
        conversao_total = (closed_count * 100.0 / leads_received) if leads_received > 0 else 0.0

        estimated_spend = projects_count * 350.0 + max(remarketing_leads, 1) * 25.0
        roi_estimado = ((total_revenue - estimated_spend) / estimated_spend) if estimated_spend > 0 else 0.0

        campaign_mais_forte = "Sem dados"
        if source_counter:
            campaign_mais_forte = max(source_counter, key=source_counter.get)

        taxa_recuperacao = (recovered_reservations * 100.0 / remarketing_leads) if remarketing_leads > 0 else 0.0

        funil = [
            RevenueFunnelStep(etapa="Leads captados", total=leads_received),
            RevenueFunnelStep(etapa="Leads qualificados", total=qualified_count),
            RevenueFunnelStep(etapa="Conversas avancadas", total=advanced_count),
            RevenueFunnelStep(etapa="Propostas enviadas", total=proposal_count),
            RevenueFunnelStep(etapa="Reservas fechadas", total=closed_count),
        ]

        receita_por_canal = [
            RevenueBreakdownItem(label=label, valor=value)
            for label, value in sorted(revenue_by_channel.items(), key=lambda item: item[1], reverse=True)
        ]
        receita_por_agente = [
            RevenueBreakdownItem(label=label, valor=value)
            for label, value in sorted(revenue_by_agent.items(), key=lambda item: item[1], reverse=True)
        ]

        status_labels = [
            "Novo lead",
            "Em conversa",
            "Interesse alto",
            "Proposta enviada",
            "Aguardando resposta",
            "Recuperacao",
            "Fechado",
            "Perdido",
        ]
        status_oportunidades = [
            RevenueOpportunityStatusItem(status=label, total=opportunity_counts.get(label, 0))
            for label in status_labels
        ]

        origin_demand = [
            RevenueOriginDemandItem(
                cidade=item.city,
                estado=item.state,
                pais=item.country,
                canal=item.channel,
                visitantes=item.visitantes,
                buscas=item.buscas,
                cotacoes=item.cotacoes,
                reservas=item.reservas,
                receita=item.receita,
                conversao=item.conversao,
            )
            for item in WebsiteTrackerService(self.db).origin_demand()
        ]
        if not origin_demand:
            reservation_buckets: dict[tuple[str, str, str, str], dict[str, float | int]] = defaultdict(lambda: {"reservas": 0, "receita": 0.0})
            for reservation in explicit_reservations:
                key = (
                    reservation.city or "",
                    reservation.state or "",
                    reservation.country or "",
                    reservation.channel or "Reserva direta",
                )
                reservation_buckets[key]["reservas"] = int(reservation_buckets[key]["reservas"]) + 1
                reservation_buckets[key]["receita"] = float(reservation_buckets[key]["receita"]) + float(reservation.total_price or 0.0)
            origin_demand = [
                RevenueOriginDemandItem(
                    cidade=city or None,
                    estado=state or None,
                    pais=country or None,
                    canal=channel,
                    visitantes=0,
                    buscas=0,
                    cotacoes=0,
                    reservas=int(values["reservas"]),
                    receita=round(float(values["receita"]), 2),
                    conversao=0.0,
                )
                for (city, state, country, channel), values in sorted(reservation_buckets.items(), key=lambda item: float(item[1]["receita"]), reverse=True)
            ]

        summary = RevenueSummary(
            receita_total=round(total_revenue, 2),
            reservas_fechadas=closed_count,
            ticket_medio=round(ticket_medio, 2),
            conversao_total=round(conversao_total, 2),
            leads_recebidos=leads_received,
            roi_estimado=round(roi_estimado, 2),
            remarketing_recuperado=round(recovered_revenue, 2),
            agentes_gerando_receita=sum(1 for value in revenue_by_agent.values() if value > 0),
        )

        remarketing = RevenueRemarketing(
            leads_em_remarketing=remarketing_leads,
            leads_reativados=reactivated_leads,
            reservas_recuperadas=recovered_reservations,
            receita_recuperada=round(recovered_revenue, 2),
            taxa_recuperacao=round(taxa_recuperacao, 2),
            campanha_mais_forte=campaign_mais_forte,
        )

        return RevenueIntelligenceSnapshot(
            summary=summary,
            reservas=reservations,
            remarketing=remarketing,
            funil=funil,
            receita_por_canal=receita_por_canal,
            receita_por_agente=receita_por_agente,
            status_oportunidades=status_oportunidades,
            mapa_origem_demanda=origin_demand,
        )

    def get_revenue_series(self, user: User, days: int = 30, granularity: str = "daily") -> RevenueSeriesResponse:
        safe_days = max(1, min(days, 365))
        mode = "weekly" if granularity == "weekly" else "daily"
        window_start = datetime.now(UTC) - timedelta(days=safe_days)

        conversations = (
            self.db.query(AgentConversation)
            .join(Agent, Agent.id == AgentConversation.agent_id)
            .filter(Agent.user_id == user.id, AgentConversation.created_at >= window_start)
            .all()
        )
        explicit_reservations = (
            self.db.query(Reservation)
            .filter(Reservation.created_at >= window_start, Reservation.status != "cancelled")
            .all()
        )

        buckets: dict[str, dict[str, Any]] = {}

        def add_bucket(created_at: datetime, value: float) -> None:
            if value <= 0:
                return
            if mode == "weekly":
                start_date = (created_at - timedelta(days=created_at.weekday())).date()
                end_date = start_date + timedelta(days=6)
                key = start_date.isoformat()
                label = f"{start_date.strftime('%d/%m')} - {end_date.strftime('%d/%m')}"
                end_iso = end_date.isoformat()
            else:
                start_date = created_at.date()
                key = start_date.isoformat()
                label = start_date.strftime("%d/%m")
                end_iso = None

            bucket = buckets.get(key)
            if bucket is None:
                bucket = {
                    "label": label,
                    "start_date": key,
                    "end_date": end_iso,
                    "receita": 0.0,
                    "reservas_fechadas": 0,
                }
                buckets[key] = bucket

            bucket["receita"] += value
            bucket["reservas_fechadas"] += 1

        for reservation in explicit_reservations:
            add_bucket(reservation.created_at or datetime.now(UTC), float(reservation.total_price or 0.0))

        for conversation in conversations:
            stage = self._normalize_stage(conversation.sales_stage)
            if not self._is_closed(stage):
                continue

            value = float(conversation.reservation_value or 0.0)
            if value <= 0:
                continue

            add_bucket(conversation.created_at or datetime.now(UTC), value)

        points = [
            RevenueSeriesPoint(
                label=item["label"],
                start_date=item["start_date"],
                end_date=item["end_date"],
                receita=round(float(item["receita"]), 2),
                reservas_fechadas=int(item["reservas_fechadas"]),
            )
            for _, item in sorted(buckets.items(), key=lambda pair: pair[0])
        ]

        return RevenueSeriesResponse(days=safe_days, granularity=mode, points=points)
