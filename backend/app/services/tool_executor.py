"""
Tool Executor para AXI.
Responsável por executar funções do backend quando a IA solicita uma ferramenta.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from app.schemas.openai_responses import ToolExecutionResult

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Executor de ferramentas para AXI.
    Mapeia nomes de ferramentas para funções do backend.
    """

    def __init__(self) -> None:
        self.tools: dict[str, Callable[..., Any]] = {}
        self._register_default_tools()

    def register_tool(self, name: str, func: Callable[..., Any]) -> None:
        """Registra uma ferramenta."""
        self.tools[name] = func
        logger.info("tool_executor.register_tool name=%s", name)

    def execute(self, tool_name: str, tool_args: dict[str, Any]) -> ToolExecutionResult:
        """
        Executa uma ferramenta.

        Args:
            tool_name: Nome da ferramenta
            tool_args: Argumentos da ferramenta

        Returns:
            Resultado da execução
        """
        if tool_name not in self.tools:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Ferramenta '{tool_name}' não encontrada",
            )

        try:
            func = self.tools[tool_name]
            result = func(**tool_args)
            logger.info("tool_executor.execute success tool=%s", tool_name)
            return ToolExecutionResult(tool_name=tool_name, success=True, result=result)
        except TypeError as exc:
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Erro em argumentos: {exc}",
            )
        except Exception as exc:
            logger.exception("tool_executor.execute error tool=%s", tool_name)
            return ToolExecutionResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=str(exc),
            )

    def _register_default_tools(self) -> None:
        """Registra ferramentas padrão do AXI."""
        # Ferramentas de reserva (exemplos simples)
        self.register_tool("check_availability", self._check_availability)
        self.register_tool("create_reservation", self._create_reservation)

        # Ferramentas de lead/vendas
        self.register_tool("create_lead", self._create_lead)
        self.register_tool("generate_proposal", self._generate_proposal)

        # Ferramentas de operação
        self.register_tool("get_dashboard_metrics", self._get_dashboard_metrics)

    # ─────────────────────────────────────────────────────────────────
    # Implementações das ferramentas padrão
    # ─────────────────────────────────────────────────────────────────

    @staticmethod
    def _check_availability(check_in: str, check_out: str, room_type: str | None = None) -> dict[str, Any]:
        """Verifica disponibilidade de quartos."""
        # Implementação real buscaria no banco de dados
        return {
            "status": "success",
            "check_in": check_in,
            "check_out": check_out,
            "available_rooms": [
                {"type": "standard", "count": 5, "price_per_night": 150.0},
                {"type": "deluxe", "count": 3, "price_per_night": 250.0},
                {"type": "suite", "count": 1, "price_per_night": 400.0},
            ] if room_type is None or room_type in ["standard", "deluxe", "suite"] else [],
        }

    @staticmethod
    def _create_reservation(guest_name: str, check_in: str, check_out: str, room_type: str, guests: int) -> dict[str, Any]:
        """Cria uma nova reserva."""
        # Implementação real gravaria no banco de dados
        return {
            "status": "success",
            "reservation_id": "RES-2026-001",
            "guest_name": guest_name,
            "check_in": check_in,
            "check_out": check_out,
            "room_type": room_type,
            "guests": guests,
            "total_price": 300.0,
            "confirmation_email": f"Confirmação enviada para o email do hóspede",
        }

    @staticmethod
    def _create_lead(name: str, email: str, phone: str | None = None, lead_source: str | None = None) -> dict[str, Any]:
        """Registra um novo lead."""
        # Implementação real integraria com CRM
        return {
            "status": "success",
            "lead_id": "LEAD-2026-001",
            "name": name,
            "email": email,
            "phone": phone,
            "lead_source": lead_source or "direct",
            "created_at": "2026-04-15T10:00:00Z",
        }

    @staticmethod
    def _generate_proposal(lead_id: str, proposal_type: str, value: float | None = None) -> dict[str, Any]:
        """Gera uma proposta comercial."""
        # Implementação real criaria documento/PDF
        return {
            "status": "success",
            "proposal_id": "PROP-2026-001",
            "lead_id": lead_id,
            "proposal_type": proposal_type,
            "value": value or 5000.0,
            "created_at": "2026-04-15T10:00:00Z",
            "download_url": "/exports/proposal-PROP-2026-001.pdf",
        }

    @staticmethod
    def _get_dashboard_metrics(metric_type: str | None = None) -> dict[str, Any]:
        """Obter métricas do dashboard."""
        # Implementação real buscaria no banco
        metrics = {
            "revenue": 150000.0,
            "occupancy": 0.85,
            "reservations": 42,
            "leads": 15,
            "proposals": 8,
        }
        
        if metric_type and metric_type in metrics:
            return {"status": "success", metric_type: metrics[metric_type]}
        
        return {"status": "success", "metrics": metrics}
