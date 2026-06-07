"""
OpenAI Responses API Service para AXI.
Integração com a Responses API recomendada pela OpenAI para apps conversacionais.
Suporta multi-turno, contexto contínuo e ferramentas (tools).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import APIError, APITimeoutError, AuthenticationError, OpenAI, RateLimitError

from app.core.config import settings
from app.schemas.openai_responses import OpenAIResponsesOutput, ToolCall

logger = logging.getLogger(__name__)


class OpenAIResponsesError(RuntimeError):
    """Erro específico da Responses API."""

    def __init__(
        self,
        message: str,
        *,
        error_type: str = "responses_api_error",
        status_code: int = 503,
        user_message: str | None = None,
    ) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.status_code = status_code
        self.user_message = user_message or message


class OpenAIResponsesService:
    """
    Serviço para interagir com OpenAI Responses API.
    
    Características:
    - Suporte a multi-turno com contexto contínuo
    - Ferramentas (tool calling) para ações externas
    - Instruções por agente
    - Streaming de respostas
    """

    def __init__(self) -> None:
        self.api_key = settings.effective_openai_api_key
        self.model = settings.openai_model or "gpt-4o-mini"
        self.timeout_seconds = settings.openai_timeout_seconds
        self.client = OpenAI(api_key=self.api_key, timeout=self.timeout_seconds) if self.api_key else None

        logger.info(
            "openai_responses.init api_key=%s model=%s timeout=%s",
            "set" if self.api_key else "missing",
            self.model,
            self.timeout_seconds,
        )

    def is_configured(self) -> bool:
        """Verifica se a chave OpenAI está configurada."""
        return bool(self.api_key and self.client)

    def _classify_error(self, exc: Exception) -> OpenAIResponsesError:
        """Classifica exceções OpenAI em OpenAIResponsesError."""
        if isinstance(exc, OpenAIResponsesError):
            return exc
        status = getattr(exc, "status_code", None)
        if status == 401:
            return OpenAIResponsesError(
                "OpenAI authentication failed",
                error_type="invalid_api_key",
                status_code=401,
                user_message="Chave API inválida",
            )
        if status == 429:
            return OpenAIResponsesError(
                "OpenAI rate limit reached",
                error_type="rate_limit",
                status_code=429,
                user_message="Limite temporário de requisições atingido",
            )
        if isinstance(exc, AuthenticationError):
            return OpenAIResponsesError(
                "OpenAI authentication failed",
                error_type="invalid_api_key",
                status_code=401,
                user_message="Chave API inválida",
            )
        if isinstance(exc, RateLimitError):
            return OpenAIResponsesError(
                "OpenAI rate limit reached",
                error_type="rate_limit",
                status_code=429,
                user_message="Limite temporário de requisições atingido",
            )
        if isinstance(exc, APITimeoutError):
            return OpenAIResponsesError(
                "OpenAI request timed out",
                error_type="timeout",
                status_code=504,
                user_message="Tempo limite excedido ao chamar a IA",
            )
        if isinstance(exc, APIError):
            status = getattr(exc, "status_code", None) or 503
            return OpenAIResponsesError(
                f"OpenAI API error: {exc}",
                error_type="api_error",
                status_code=status,
                user_message="Falha temporária ao chamar a IA",
            )
        return OpenAIResponsesError(
            f"OpenAI request failed: {exc}",
            error_type="unknown_error",
            status_code=503,
            user_message="Falha temporária ao chamar a IA",
        )

    def generate_response(
        self,
        *,
        user_message: str,
        instructions: str | None = None,
        conversation_history: list[Any] | None = None,
        tools: list[dict[str, Any]] | None = None,
    ) -> "OpenAIResponsesOutput":
        """
        Gera resposta usando Responses API com suporte a multi-turno.
        
        Args:
            user_message: Mensagem do usuário
            instructions: Instruções do sistema (comportamento do agente)
            conversation_history: Histórico de conversa para contexto contínuo
            tools: Definições de ferramentas disponíveis (JSON schema)
        
        Returns:
            Texto da resposta
        
        Raises:
            OpenAIResponsesError: Se houver erro na chamada à API
        """
        if not self.is_configured():
            raise OpenAIResponsesError(
                "OpenAI API key is not configured",
                error_type="missing_api_key",
                status_code=503,
            )

        if not user_message.strip():
            raise OpenAIResponsesError(
                "User message cannot be empty",
                error_type="invalid_input",
                status_code=400,
            )

        # Padrão de instruções default
        default_instructions = (
            "Você é o assistente AXI. Responda em pt-BR, com clareza e foco em valor ao usuário. "
            "Seja útil, objetivo e profissional."
        )
        instructions = (instructions or default_instructions).strip()

        try:
            # Construir contexto com histórico se fornecido
            # Converter mensagens para dict de forma tolerante
            history_dicts = None
            if conversation_history:
                history_dicts = [
                    {
                        "role": msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", ""),
                        "content": msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", ""),
                    }
                    for msg in conversation_history
                ]
            
            context = self._build_context(history_dicts) if history_dicts else ""
            full_input = f"{context}\n{user_message}".strip() if context else user_message

            # Chamada à Responses API
            request_kwargs: dict[str, Any] = {
                "model": self.model,
                "instructions": instructions,
                "input": full_input,
            }

            # Adicionar ferramentas se definidas
            if tools:
                request_kwargs["tools"] = tools

            response = self.client.responses.create(**request_kwargs)

            # Extrair texto da resposta
            # Response pode ter output_text ou content
            output_text = ""
            if hasattr(response, "output_text"):
                output_text = response.output_text or ""
            elif hasattr(response, "content"):
                output_text = response.content or ""
            elif isinstance(response, dict):
                output_text = response.get("output_text") or response.get("content") or ""
            else:
                # Tentar converter para string se nada funcionar
                logger.warning("openai_responses.unknown_response_type type=%s", type(response))
                output_text = str(response) if response else ""

            # Extrair tool calls se houver
            tool_calls = []
            if hasattr(response, "tool_calls") and response.tool_calls:
                tool_calls = [
                    {
                        "tool_name": tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None),
                        "tool_args": tc.get("arguments", {}) if isinstance(tc, dict) else getattr(tc, "arguments", {}),
                    }
                    for tc in response.tool_calls
                ]

            logger.info(
                "openai_responses.success model=%s output_length=%s tool_calls=%s",
                self.model,
                len(output_text),
                len(tool_calls),
            )

            return OpenAIResponsesOutput(output_text=output_text.strip(), tool_calls=tool_calls)

        except Exception as exc:
            mapped = self._classify_error(exc)
            logger.error(
                "openai_responses.error error_type=%s status_code=%s message=%s",
                mapped.error_type,
                mapped.status_code,
                str(mapped),
            )
            raise mapped from exc

    def _build_context(self, history: list[Any]) -> str:
        """Constrói contexto a partir do histórico de conversa."""
        if not history or len(history) == 0:
            return ""

        context_lines = ["Contexto da conversa anterior:"]
        for msg in history[-10:]:  # Últimas 10 mensagens para evitar contexto muito grande
            role_value = msg.get("role", "") if isinstance(msg, dict) else getattr(msg, "role", "")
            content = msg.get("content", "") if isinstance(msg, dict) else getattr(msg, "content", "")
            role = str(role_value).capitalize()
            if role and content:
                context_lines.append(f"{role}: {content}")

        return "\n".join(context_lines)

    def generate_agent_response(
        self,
        *,
        agent_name: str,
        agent_prompt: str,
        user_message: str,
        company_context: str | dict[str, Any] | None = None,
        conversation_history: list[dict[str, Any] | Any] | None = None,
    ) -> "OpenAIResponsesOutput":
        """
        Gera resposta de um agente especializado.
        
        Args:
            agent_name: Nome do agente (ex: "Recepcionista")
            agent_prompt: Instruções específicas do agente
            user_message: Mensagem do usuário
            company_context: Contexto da empresa
            conversation_history: Histórico de conversa
        
        Returns:
            Resposta do agente
        """
        instructions = f"""
Você é o agente {agent_name} da plataforma AXI.
Role e instruções:
{agent_prompt}
""".strip()

        if company_context:
            context_str = json.dumps(company_context) if isinstance(company_context, dict) else str(company_context)
            instructions += f"\n\nContexto da empresa:\n{context_str}"

        return self.generate_response(
            user_message=user_message,
            instructions=instructions,
            conversation_history=conversation_history,
        )

    def healthcheck(self) -> dict[str, Any]:
        """Verifica saúde da conexão com OpenAI."""
        try:
            result = self.generate_response(user_message="Responda apenas com OK")
            return {
                "status": "ok",
                "model": self.model,
                "message": result.output_text,
                "error_type": None,
                "status_code": 200,
            }
        except Exception as exc:
            mapped = self._classify_error(exc)
            return {
                "status": "error",
                "model": self.model,
                "message": str(mapped),
                "error_type": mapped.error_type,
                "status_code": mapped.status_code,
            }
