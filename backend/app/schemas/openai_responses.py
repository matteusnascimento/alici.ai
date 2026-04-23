"""Schemas Pydantic para OpenAI Responses API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AIToolParameter(BaseModel):
    """Parâmetro de uma ferramenta."""

    name: str
    type: str = Field(description="Tipo do parâmetro: string, number, boolean, etc.")
    description: str = Field(description="Descrição do parâmetro")
    required: bool = False


class AITool(BaseModel):
    """Definição de uma ferramenta (tool calling)."""

    name: str = Field(description="Nome único da ferramenta")
    description: str = Field(description="Descrição do que a ferramenta faz")
    parameters: list[AIToolParameter] = Field(default_factory=list, description="Parâmetros da ferramenta")

    def to_json_schema(self) -> dict[str, Any]:
        """Converte para JSON schema compatível com OpenAI."""
        return {
            "type": "object",
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {p.name: {"type": p.type, "description": p.description} for p in self.parameters},
                "required": [p.name for p in self.parameters if p.required],
            },
        }


# ─────────────────────────────────────────────────────────────────
# Chat Requests/Responses
# ─────────────────────────────────────────────────────────────────


class ConversationMessage(BaseModel):
    """Mensagem em uma conversa."""

    role: str = Field(description="'user' ou 'assistant'")
    content: str = Field(description="Conteúdo da mensagem")


class OpenAIResponsesRequest(BaseModel):
    """Requisição para gerar resposta com Responses API."""

    user_message: str = Field(description="Mensagem do usuário")
    instructions: str | None = Field(default=None, description="Instruções do sistema/agente")
    conversation_history: list[ConversationMessage] | None = Field(
        default=None, description="Histórico de conversa para contexto"
    )
    tools: list[AITool] | None = Field(default=None, description="Ferramentas disponíveis")


class OpenAIResponsesOutput(BaseModel):
    """Resposta da Responses API."""

    output_text: str = Field(description="Texto da resposta")
    tool_calls: list["ToolCall"] | None = Field(default=None, description="Chamadas de ferramentas (se houver)")
    conversation_id: int | None = Field(default=None, description="ID da conversa persistida (quando aplicável)")
    message_id: int | None = Field(default=None, description="ID da mensagem do assistente (quando aplicável)")


# ─────────────────────────────────────────────────────────────────
# Agent Specialized Response
# ─────────────────────────────────────────────────────────────────


class AgentGenerateRequest(BaseModel):
    """Requisição para gerar resposta de um agente especializado."""

    agent_name: str = Field(description="Nome do agente (ex: Recepcionista)")
    agent_prompt: str = Field(description="Instruções específicas do agente")
    user_message: str = Field(description="Mensagem do usuário")
    company_context: str | None = Field(default=None, description="Contexto da empresa")
    conversation_history: list[ConversationMessage] | None = Field(default=None, description="Histórico")


class AgentGenerateResponse(BaseModel):
    """Resposta de um agente."""

    agent_name: str
    response: str = Field(description="Texto da resposta do agente")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ─────────────────────────────────────────────────────────────────
# Tool Execution
# ─────────────────────────────────────────────────────────────────


class ToolCall(BaseModel):
    """Chamada de ferramenta retornada pela IA."""

    tool_name: str = Field(description="Nome da ferramenta a executar")
    tool_args: dict[str, Any] = Field(default_factory=dict, description="Argumentos para a ferramenta")


class ToolExecutionRequest(BaseModel):
    """Requisição para executar uma ferramenta."""

    tool_name: str = Field(description="Nome da ferramenta a executar")
    tool_args: dict[str, Any] = Field(default_factory=dict, description="Argumentos para a ferramenta")


class ToolExecutionResult(BaseModel):
    """Resultado da execução de uma ferramenta."""

    tool_name: str
    success: bool = True
    result: Any = Field(description="Resultado da execução")
    error: str | None = Field(default=None, description="Erro se houver")


# ─────────────────────────────────────────────────────────────────
# Predefined Tools for AXI
# ─────────────────────────────────────────────────────────────────


class AIToolRegistry:
    """Registry das ferramentas disponíveis no AXI."""

    # Ferramentas para reservas
    CREATE_RESERVATION = AITool(
        name="create_reservation",
        description="Criar uma nova reserva no sistema",
        parameters=[
            AIToolParameter(name="guest_name", type="string", description="Nome do hóspede", required=True),
            AIToolParameter(name="check_in", type="string", description="Data de check-in (YYYY-MM-DD)", required=True),
            AIToolParameter(name="check_out", type="string", description="Data de check-out (YYYY-MM-DD)", required=True),
            AIToolParameter(name="room_type", type="string", description="Tipo de quarto", required=True),
            AIToolParameter(name="guests", type="number", description="Número de hóspedes", required=True),
        ],
    )

    CHECK_AVAILABILITY = AITool(
        name="check_availability",
        description="Verificar disponibilidade de quartos",
        parameters=[
            AIToolParameter(name="check_in", type="string", description="Data de check-in (YYYY-MM-DD)", required=True),
            AIToolParameter(name="check_out", type="string", description="Data de check-out (YYYY-MM-DD)", required=True),
            AIToolParameter(name="room_type", type="string", description="Tipo de quarto (opcional)", required=False),
        ],
    )

    # Ferramentas para vendas/marketing
    CREATE_LEAD = AITool(
        name="create_lead",
        description="Registrar um novo lead no CRM",
        parameters=[
            AIToolParameter(name="name", type="string", description="Nome do lead", required=True),
            AIToolParameter(name="email", type="string", description="Email", required=True),
            AIToolParameter(name="phone", type="string", description="Telefone", required=False),
            AIToolParameter(name="lead_source", type="string", description="Origem do lead", required=False),
        ],
    )

    GENERATE_PROPOSAL = AITool(
        name="generate_proposal",
        description="Gerar uma proposta comercial",
        parameters=[
            AIToolParameter(name="lead_id", type="string", description="ID do lead", required=True),
            AIToolParameter(name="proposal_type", type="string", description="Tipo de proposta", required=True),
            AIToolParameter(name="value", type="number", description="Valor da proposta", required=False),
        ],
    )

    # Ferramentas para comunicação
    SEND_EMAIL = AITool(
        name="send_email",
        description="Enviar email para cliente",
        parameters=[
            AIToolParameter(name="to_email", type="string", description="Email destinatário", required=True),
            AIToolParameter(name="subject", type="string", description="Assunto do email", required=True),
            AIToolParameter(name="body", type="string", description="Corpo do email", required=True),
            AIToolParameter(name="template", type="string", description="Template: welcome, proposal, reminder", required=False),
        ],
    )

    REGISTER_LEAD_IN_CRM = AITool(
        name="register_lead_in_crm",
        description="Registrar ou atualizar lead em CRM",
        parameters=[
            AIToolParameter(name="name", type="string", description="Nome do lead", required=True),
            AIToolParameter(name="email", type="string", description="Email", required=True),
            AIToolParameter(name="phone", type="string", description="Telefone", required=False),
            AIToolParameter(name="company", type="string", description="Empresa", required=False),
            AIToolParameter(name="stage", type="string", description="Estágio: lead, qualified, proposal, negotiation", required=False),
            AIToolParameter(name="notes", type="string", description="Notas internas", required=False),
        ],
    )

    # Ferramentas para operação
    GET_DASHBOARD_METRICS = AITool(
        name="get_dashboard_metrics",
        description="Obter métricas do dashboard",
        parameters=[
            AIToolParameter(name="metric_type", type="string", description="Tipo de métrica (revenue, occupancy, etc)", required=False),
        ],
    )

    @classmethod
    def get_tool(cls, name: str) -> AITool | None:
        """Obter ferramenta por nome."""
        attr = getattr(cls, name.upper(), None)
        if isinstance(attr, AITool):
            return attr
        return None

    @classmethod
    def list_all_tools(cls) -> list[AITool]:
        """Listar todas as ferramentas disponíveis."""
        tools = []
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, AITool):
                tools.append(attr)
        return tools
