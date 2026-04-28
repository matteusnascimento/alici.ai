"""
Tool Executor para AXI.
Responsável por executar funções do backend quando a IA solicita uma ferramenta.
"""

from __future__ import annotations

import json
import logging
import time
from html import escape
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable
from email_validator import validate_email, EmailNotValidError
from pydantic import ValidationError

from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.lead import Lead
from app.models.proposal import Proposal
from app.models.reservation import Reservation
from app.schemas.openai_responses import ToolExecutionResult
from app.services.email_service import EmailService
from app.services.crm_service import CRMService
from app.services.lead_service import LeadService
from app.services.reservation_service import ReservationService
from app.services.proposal_service import ProposalService
from app.services.tool_execution_service import ToolExecutionService

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Executor de ferramentas para AXI.
    Mapeia nomes de ferramentas para funções do backend.
    """

    def __init__(self, db: Session | None = None) -> None:
        self.db = db or next(get_db())
        self.tools: dict[str, Callable[..., Any]] = {}
        self._register_default_tools()

    def register_tool(self, name: str, func: Callable[..., Any]) -> None:
        """Registra uma ferramenta."""
        self.tools[name] = func
        logger.info("tool_executor.register_tool name=%s", name)

    def execute(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        agent_id: int | None = None,
        user_id: int | None = None,
        conversation_id: int | None = None,
    ) -> ToolExecutionResult:
        """
        Executa uma ferramenta.

        Args:
            tool_name: Nome da ferramenta
            tool_args: Argumentos da ferramenta
            agent_id: ID do agent que executou
            user_id: ID do usuário
            conversation_id: ID da conversa

        Returns:
            Resultado da execução
        """
        start_time = time.time()

        if tool_name not in self.tools:
            error_msg = f"Ferramenta '{tool_name}' não encontrada"
            self._log_execution(
                tool_name, tool_args, False, None, error_msg, 0,
                agent_id, user_id, conversation_id
            )
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=error_msg,
            )

        try:
            # Valida argumentos
            validated_args = self._validate_tool_args(tool_name, tool_args)

            # Executa função
            func = self.tools[tool_name]
            result = func(**validated_args)

            execution_time = int((time.time() - start_time) * 1000)
            self._log_execution(
                tool_name, tool_args, True, result, None, execution_time,
                agent_id, user_id, conversation_id
            )

            logger.info("tool_executor.execute success tool=%s", tool_name)
            return ToolExecutionResult(tool_name=tool_name, success=True, result=result)

        except (ValueError, ValidationError) as exc:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = f"Erro em argumentos: {exc}"
            self._log_execution(
                tool_name, tool_args, False, None, error_msg, execution_time,
                agent_id, user_id, conversation_id
            )
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=error_msg,
            )
        except Exception as exc:
            execution_time = int((time.time() - start_time) * 1000)
            error_msg = str(exc)
            self._log_execution(
                tool_name, tool_args, False, None, error_msg, execution_time,
                agent_id, user_id, conversation_id
            )
            logger.exception("tool_executor.execute error tool=%s", tool_name)
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=error_msg,
            )

    def _log_execution(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        success: bool,
        result: Any,
        error: str | None,
        execution_time_ms: int,
        agent_id: int | None,
        user_id: int | None,
        conversation_id: int | None,
    ) -> None:
        """Registra execução no banco."""
        try:
            tool_exec_service = ToolExecutionService(self.db)
            tool_exec_service.log_execution(
                tool_name=tool_name,
                tool_args=tool_args,
                success=success,
                result=result,
                error=error,
                execution_time_ms=execution_time_ms,
                agent_id=agent_id,
                user_id=user_id,
                conversation_id=conversation_id,
            )
        except Exception as log_exc:
            logger.warning("Failed to log tool execution: %s", log_exc)

    def _validate_tool_args(self, tool_name: str, tool_args: dict[str, Any]) -> dict[str, Any]:
        """Valida argumentos da ferramenta."""
        validators = {
            "create_reservation": self._validate_create_reservation,
            "check_availability": self._validate_check_availability,
            "create_lead": self._validate_create_lead,
            "generate_proposal": self._validate_generate_proposal,
            "get_dashboard_metrics": self._validate_get_dashboard_metrics,
            "send_email": self._validate_send_email,
            "register_lead_in_crm": self._validate_register_lead_in_crm,
        }

        validator = validators.get(tool_name)
        if validator:
            return validator(tool_args)
        return tool_args

    def _validate_create_reservation(self, args: dict[str, Any]) -> dict[str, Any]:
        """Valida argumentos para create_reservation."""
        required = ["guest_name", "check_in", "check_out", "room_type", "guests"]
        for field in required:
            if field not in args:
                raise ValueError(f"Campo obrigatório: {field}")

        # Valida datas
        try:
            check_in = date.fromisoformat(args["check_in"])
            check_out = date.fromisoformat(args["check_out"])
            if check_in >= check_out:
                raise ValueError("check_out deve ser posterior a check_in")
            if check_in < date.today():
                raise ValueError("check_in não pode ser no passado")
        except ValueError as e:
            raise ValueError(f"Data inválida: {e}")

        # Valida tipo de quarto
        valid_room_types = ["standard", "deluxe", "suite"]
        if args["room_type"] not in valid_room_types:
            raise ValueError(f"room_type deve ser um dos: {valid_room_types}")

        # Valida número de hóspedes
        if not isinstance(args["guests"], int) or args["guests"] < 1:
            raise ValueError("guests deve ser um número inteiro positivo")

        return args

    def _validate_check_availability(self, args: dict[str, Any]) -> dict[str, Any]:
        """Valida argumentos para check_availability."""
        required = ["check_in", "check_out"]
        for field in required:
            if field not in args:
                raise ValueError(f"Campo obrigatório: {field}")

        # Valida datas
        try:
            check_in = date.fromisoformat(args["check_in"])
            check_out = date.fromisoformat(args["check_out"])
            if check_in >= check_out:
                raise ValueError("check_out deve ser posterior a check_in")
        except ValueError as e:
            raise ValueError(f"Data inválida: {e}")

        # Valida tipo de quarto opcional
        if "room_type" in args:
            valid_room_types = ["standard", "deluxe", "suite"]
            if args["room_type"] not in valid_room_types:
                raise ValueError(f"room_type deve ser um dos: {valid_room_types}")

        return args

    def _validate_create_lead(self, args: dict[str, Any]) -> dict[str, Any]:
        """Valida argumentos para create_lead."""
        required = ["name", "email"]
        for field in required:
            if field not in args:
                raise ValueError(f"Campo obrigatório: {field}")

        # Valida email
        try:
            validate_email(args["email"], check_deliverability=False)
        except EmailNotValidError as e:
            raise ValueError(f"Email inválido: {e}")

        # Valida nome
        if len(args["name"].strip()) < 2:
            raise ValueError("name deve ter pelo menos 2 caracteres")

        # Valida telefone opcional
        if "phone" in args and args["phone"]:
            # Remove caracteres não numéricos e valida formato básico
            phone_clean = "".join(c for c in args["phone"] if c.isdigit())
            if len(phone_clean) < 10:
                raise ValueError("phone deve ter pelo menos 10 dígitos")

        return args

    def _validate_generate_proposal(self, args: dict[str, Any]) -> dict[str, Any]:
        """Valida argumentos para generate_proposal."""
        required = ["lead_id", "proposal_type"]
        for field in required:
            if field not in args:
                raise ValueError(f"Campo obrigatório: {field}")

        # Valida lead_id
        if not isinstance(args["lead_id"], (str, int)):
            raise ValueError("lead_id deve ser string ou número")

        # Valida proposal_type
        valid_types = ["consultoria", "produto", "servico", "pacote"]
        if args["proposal_type"] not in valid_types:
            raise ValueError(f"proposal_type deve ser um dos: {valid_types}")

        # Valida value opcional
        if "value" in args and args["value"] is not None:
            if not isinstance(args["value"], (int, float)) or args["value"] <= 0:
                raise ValueError("value deve ser um número positivo")

        return args

    def _validate_send_email(self, args: dict[str, Any]) -> dict[str, Any]:
        """Valida argumentos para send_email."""
        required = ["to_email", "subject", "body"]
        for field in required:
            if field not in args:
                raise ValueError(f"Campo obrigatório: {field}")

        # Valida email
        try:
            validate_email(args["to_email"], check_deliverability=False)
        except EmailNotValidError as e:
            raise ValueError(f"Email inválido: {e}")

        # Valida template opcional
        if "template" in args:
            valid_templates = ["welcome", "proposal", "reminder"]
            if args["template"] not in valid_templates:
                raise ValueError(f"template deve ser um dos: {valid_templates}")

        return args

    def _validate_register_lead_in_crm(self, args: dict[str, Any]) -> dict[str, Any]:
        """Valida argumentos para register_lead_in_crm."""
        required = ["name", "email"]
        for field in required:
            if field not in args:
                raise ValueError(f"Campo obrigatório: {field}")

        # Valida email
        try:
            validate_email(args["email"], check_deliverability=False)
        except EmailNotValidError as e:
            raise ValueError(f"Email inválido: {e}")

        # Valida nome
        if len(args["name"].strip()) < 2:
            raise ValueError("name deve ter pelo menos 2 caracteres")

        # Valida stage opcional
        if "stage" in args:
            valid_stages = ["lead", "qualified", "proposal", "negotiation", "closed"]
            if args["stage"] not in valid_stages:
                raise ValueError(f"stage deve ser um dos: {valid_stages}")

        return args

    def _validate_get_dashboard_metrics(self, args: dict[str, Any]) -> dict[str, Any]:
        """Valida argumentos para get_dashboard_metrics."""
        # Nenhum campo obrigatório, apenas valida metric_type opcional
        if "metric_type" in args:
            valid_types = ["revenue", "occupancy", "reservations", "leads", "proposals"]
            if args["metric_type"] not in valid_types:
                raise ValueError(f"metric_type deve ser um dos: {valid_types}")

        return args

    def _register_default_tools(self) -> None:
        """Registra ferramentas padrão do AXI."""
        # Ferramentas de reserva
        self.register_tool("check_availability", self._check_availability)
        self.register_tool("create_reservation", self._create_reservation)

        # Ferramentas de lead/vendas
        self.register_tool("create_lead", self._create_lead)
        self.register_tool("generate_proposal", self._generate_proposal)

        # Ferramentas de comunicação
        self.register_tool("send_email", self._send_email)
        self.register_tool("register_lead_in_crm", self._register_lead_in_crm)

        # Ferramentas de operação
        self.register_tool("get_dashboard_metrics", self._get_dashboard_metrics)

    # ─────────────────────────────────────────────────────────────────
    # Implementações das ferramentas padrão
    # ─────────────────────────────────────────────────────────────────

    def _check_availability(self, check_in: str, check_out: str, room_type: str | None = None) -> dict[str, Any]:
        """Verifica disponibilidade de quartos."""
        reservation_service = ReservationService(self.db)
        return reservation_service.check_availability(
            check_in=date.fromisoformat(check_in),
            check_out=date.fromisoformat(check_out),
            room_type=room_type,
        )

    def _create_reservation(self, guest_name: str, check_in: str, check_out: str, room_type: str, guests: int) -> dict[str, Any]:
        """Cria uma nova reserva."""
        from app.schemas.reservation import ReservationCreate

        reservation_data = ReservationCreate(
            guest_name=guest_name,
            check_in=date.fromisoformat(check_in),
            check_out=date.fromisoformat(check_out),
            room_type=room_type,
            guests=guests,
        )

        reservation_service = ReservationService(self.db)
        reservation = reservation_service.create_reservation(reservation_data)

        return {
            "status": "success",
            "reservation_id": reservation.reservation_id,
            "guest_name": reservation.guest_name,
            "check_in": reservation.check_in.isoformat(),
            "check_out": reservation.check_out.isoformat(),
            "room_type": reservation.room_type,
            "guests": reservation.guests,
            "total_price": reservation.total_price,
            "confirmation_message": f"Reserva confirmada para {reservation.guest_name}",
        }

    def _create_lead(self, name: str, email: str, phone: str | None = None, lead_source: str | None = None) -> dict[str, Any]:
        """Registra um novo lead."""
        from app.schemas.lead import LeadCreate

        # Verifica se lead já existe
        lead_service = LeadService(self.db)
        existing_lead = lead_service.get_lead_by_email(email)
        if existing_lead:
            return {
                "status": "success",
                "lead_id": existing_lead.id,
                "name": existing_lead.name,
                "email": existing_lead.email,
                "message": "Lead já existe no sistema",
            }

        lead_data = LeadCreate(
            name=name,
            email=email,
            phone=phone,
            lead_source=lead_source or "direct",
        )

        lead = lead_service.create_lead(lead_data)

        return {
            "status": "success",
            "lead_id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "lead_source": lead.lead_source,
            "created_at": lead.created_at.isoformat(),
        }

    def _generate_proposal(self, lead_id: str | int, proposal_type: str, value: float | None = None) -> dict[str, Any]:
        """Gera uma proposta comercial."""
        from app.schemas.proposal import ProposalCreate

        # Converte lead_id para int se necessário
        try:
            lead_id_int = int(lead_id)
        except ValueError:
            raise ValueError("lead_id deve ser um número válido")

        proposal_data = ProposalCreate(
            lead_id=lead_id_int,
            proposal_type=proposal_type,
            value=value or 5000.0,
        )

        proposal_service = ProposalService(self.db)
        proposal = proposal_service.create_proposal(proposal_data)
        lead = self.db.query(Lead).filter(Lead.id == proposal.lead_id).first()
        download_url, file_path = self._write_proposal_document(
            proposal_id=proposal.proposal_id,
            lead_name=lead.name if lead else f"Lead {proposal.lead_id}",
            proposal_type=proposal.proposal_type,
            value=proposal.value,
            created_at=proposal.created_at,
        )

        proposal_row = self.db.query(Proposal).filter(Proposal.id == proposal.id).first()
        if proposal_row:
            proposal_row.file_path = file_path
            proposal_row.content = f"Documento HTML gerado em {download_url}"
            self.db.commit()

        return {
            "status": "success",
            "proposal_id": proposal.proposal_id,
            "lead_id": proposal.lead_id,
            "proposal_type": proposal.proposal_type,
            "value": proposal.value,
            "created_at": proposal.created_at.isoformat(),
            "download_url": download_url,
        }

    def _write_proposal_document(
        self,
        *,
        proposal_id: str,
        lead_name: str,
        proposal_type: str,
        value: float,
        created_at: datetime,
    ) -> tuple[str, str]:
        safe_id = "".join(ch for ch in proposal_id if ch.isalnum() or ch in {"-", "_"}).strip("-_") or "proposal"
        exports_dir = Path(__file__).resolve().parents[2] / "exports" / "proposals"
        exports_dir.mkdir(parents=True, exist_ok=True)
        filename = f"proposal-{safe_id}.html"
        file_path = exports_dir / filename
        html = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Proposta {escape(proposal_id)}</title>
</head>
<body>
  <h1>Proposta Comercial</h1>
  <p><strong>ID:</strong> {escape(proposal_id)}</p>
  <p><strong>Lead:</strong> {escape(lead_name)}</p>
  <p><strong>Tipo:</strong> {escape(proposal_type)}</p>
  <p><strong>Valor:</strong> R$ {value:,.2f}</p>
  <p><strong>Criada em:</strong> {escape(created_at.isoformat())}</p>
</body>
</html>
"""
        file_path.write_text(html, encoding="utf-8")
        relative_path = f"exports/proposals/{filename}"
        return f"/{relative_path}", relative_path

    def _get_dashboard_metrics(self, metric_type: str | None = None) -> dict[str, Any]:
        """Obter métricas do dashboard."""
        today = date.today()
        window_end = today + timedelta(days=30)
        reservations = int(
            self.db.query(func.count(Reservation.id))
            .filter(Reservation.status != "cancelled")
            .scalar()
            or 0
        )
        revenue = float(
            self.db.query(func.coalesce(func.sum(Reservation.total_price), 0.0))
            .filter(Reservation.status != "cancelled")
            .scalar()
            or 0.0
        )
        leads = int(self.db.query(func.count(Lead.id)).scalar() or 0)
        proposals = int(self.db.query(func.count(Proposal.id)).scalar() or 0)

        occupied_nights = 0
        active_reservations = (
            self.db.query(Reservation)
            .filter(
                Reservation.status != "cancelled",
                Reservation.check_in < window_end,
                Reservation.check_out > today,
            )
            .all()
        )
        for reservation in active_reservations:
            start = max(reservation.check_in, today)
            end = min(reservation.check_out, window_end)
            occupied_nights += max((end - start).days, 0)

        total_room_nights = sum(ReservationService.ROOM_INVENTORY.values()) * 30
        occupancy = round(occupied_nights / total_room_nights, 4) if total_room_nights else 0.0
        metrics = {
            "revenue": revenue,
            "occupancy": occupancy,
            "reservations": reservations,
            "leads": leads,
            "proposals": proposals,
        }

        if metric_type and metric_type in metrics:
            return {"status": "success", metric_type: metrics[metric_type]}

        return {"status": "success", "metrics": metrics}
    def _send_email(self, to_email: str, subject: str, body: str, template: str | None = None) -> dict[str, Any]:
        """Envia email para cliente."""
        email_service = EmailService()
        result = email_service.send_email(
            to_email=to_email,
            subject=subject,
            body=body,
            template=template,
        )

        return {
            "status": result["status"],
            "message": result["message"],
            "to_email": to_email,
            "subject": subject,
            "template": template,
        }

    def _register_lead_in_crm(self, name: str, email: str, phone: str | None = None, company: str | None = None, stage: str | None = None, notes: str | None = None) -> dict[str, Any]:
        """Registra lead em CRM."""
        crm_service = CRMService()
        lead_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "stage": stage or "lead",
            "notes": notes,
        }

        result = crm_service.register_lead(lead_data)

        return {
            "status": result["status"],
            "message": result.get("message", "Lead registrado com sucesso"),
            "crm_provider": result.get("crm_provider"),
            "crm_id": result.get("crm_id"),
            "lead_data": lead_data,
        }
