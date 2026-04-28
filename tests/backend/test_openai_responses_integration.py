"""
Testes para OpenAI Responses API Integration.
"""

from datetime import date, timedelta
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message
from app.models.user import User
from app.schemas.chat import ChatSendRequest
from app.schemas.openai_responses import (
    AIToolRegistry,
    ConversationMessage,
    OpenAIResponsesOutput,
    ToolCall,
)
from app.services.chat_service import ChatService
from app.services.openai_responses_service import OpenAIResponsesService, OpenAIResponsesError
from app.services.tool_executor import ToolExecutor


class TestOpenAIResponsesService:
    """Testa OpenAIResponsesService diretamente."""

    def test_is_configured_without_api_key(self):
        """Testa detecção de API key não configurada."""
        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = None
            service = OpenAIResponsesService()
            assert service.is_configured() is False

    def test_is_configured_with_api_key(self):
        """Testa detecção de API key configurada."""
        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = "sk-test-key"
            service = OpenAIResponsesService()
            assert service.is_configured() is True

    def test_build_context_with_empty_history(self):
        """Testa construção de contexto com histórico vazio."""
        service = OpenAIResponsesService()
        context = service._build_context([])
        assert context == ""

    def test_build_context_with_messages(self):
        """Testa construção de contexto com histórico."""
        service = OpenAIResponsesService()
        history = [
            ConversationMessage(role="user", content="Oi"),
            ConversationMessage(role="assistant", content="Olá! Como posso ajudar?"),
        ]
        context = service._build_context(history)
        assert "Oi" in context
        assert "Olá! Como posso ajudar?" in context

    def test_classify_error_authentication(self):
        """Testa classificação de erro de autenticação."""
        service = OpenAIResponsesService()
        class _FakeAuthError(Exception):
            status_code = 401

        exc = _FakeAuthError("Invalid API key")
        result = service._classify_error(exc)
        
        assert result.status_code == 401
        assert "Chave API" in result.user_message

    def test_classify_error_rate_limit(self):
        """Testa classificação de erro de rate limit."""
        service = OpenAIResponsesService()
        class _FakeRateLimitError(Exception):
            status_code = 429

        exc = _FakeRateLimitError("Rate limit exceeded")
        result = service._classify_error(exc)
        
        assert result.status_code == 429

    def test_classify_error_timeout(self):
        """Testa classificação de erro de timeout."""
        from openai._exceptions import APITimeoutError
        
        service = OpenAIResponsesService()
        exc = APITimeoutError("Request timeout")
        result = service._classify_error(exc)
        
        assert result.status_code == 504

    @patch("app.services.openai_responses_service.OpenAI")
    def test_generate_response_success(self, mock_openai_class):
        """Testa geração de resposta bem-sucedida."""
        # Mock da chamada à API
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.output_text = "Resposta teste"
        mock_client.responses.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4"
            mock_settings.openai_timeout_seconds = 30

            service = OpenAIResponsesService()
            response = service.generate_response(
                user_message="Teste",
                instructions="Teste instrução",
                conversation_history=[],
            )

            assert response.output_text == "Resposta teste"
            mock_client.responses.create.assert_called_once()

    @patch("app.services.openai_responses_service.OpenAI")
    def test_generate_agent_response(self, mock_openai_class):
        """Testa geração de resposta de agente especializado."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.output_text = "Resposta do agente vendedor"
        mock_client.responses.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4"
            mock_settings.openai_timeout_seconds = 30

            service = OpenAIResponsesService()
            response = service.generate_agent_response(
                agent_name="sales",
                agent_prompt="Você é um vendedor.",
                user_message="Quero comprar",
                company_context={},
                conversation_history=[],
            )

            assert response.output_text == "Resposta do agente vendedor"


class TestToolExecutor:
    """Testa ToolExecutor."""

    def test_execute_nonexistent_tool(self):
        """Testa execução de ferramenta inexistente."""
        executor = ToolExecutor()
        result = executor.execute("tool_inexistente", {})

        assert result.success is False
        assert "não encontrada" in result.error

    def test_execute_check_availability(self):
        """Testa execução de ferramenta de disponibilidade."""
        executor = ToolExecutor()
        result = executor.execute(
            "check_availability",
            {
                "check_in": (date.today() + timedelta(days=7)).isoformat(),
                "check_out": (date.today() + timedelta(days=9)).isoformat(),
                "room_type": "standard",
            },
        )

        assert result.success is True
        assert "available_rooms" in result.result

    def test_execute_create_reservation(self):
        """Testa execução de ferramenta de criação de reserva."""
        executor = ToolExecutor()
        result = executor.execute(
            "create_reservation",
            {
                "guest_name": "João Silva",
                "check_in": (date.today() + timedelta(days=7)).isoformat(),
                "check_out": (date.today() + timedelta(days=9)).isoformat(),
                "room_type": "standard",
                "guests": 2,
            },
        )

        assert result.success is True
        assert "reservation_id" in result.result

    def test_execute_create_lead(self):
        """Testa execução de ferramenta de criação de lead."""
        executor = ToolExecutor()
        result = executor.execute(
            "create_lead",
            {
                "name": "Maria Santos",
                "email": "maria@example.com",
                "phone": "11999999999",
            },
        )

        assert result.success is True
        assert "lead_id" in result.result

    def test_execute_generate_proposal_creates_real_document(self):
        """Testa geracao de proposta com arquivo real."""
        executor = ToolExecutor()
        lead = executor.execute(
            "create_lead",
            {
                "name": "Cliente Proposta",
                "email": "proposta@example.com",
                "phone": "11999999999",
            },
        )
        assert lead.success is True

        result = executor.execute(
            "generate_proposal",
            {
                "lead_id": lead.result["lead_id"],
                "proposal_type": "servico",
                "value": 1500,
            },
        )

        assert result.success is True
        download_url = result.result["download_url"]
        assert download_url.endswith(".html")
        document = Path(__file__).resolve().parents[2] / "backend" / download_url.lstrip("/")
        try:
            assert document.exists()
            assert "Cliente Proposta" in document.read_text(encoding="utf-8")
        finally:
            document.unlink(missing_ok=True)

    def test_execute_with_wrong_arguments(self):
        """Testa execução com argumentos inválidos."""
        executor = ToolExecutor()
        result = executor.execute("create_lead", {"name": "Teste"})  # Faltam argumentos obrigatórios

        assert result.success is False
        assert "Erro em argumentos" in result.error


class TestAIToolRegistry:
    """Testa AIToolRegistry."""

    def test_list_all_tools(self):
        """Testa listagem de todas as ferramentas."""
        tools = AIToolRegistry.list_all_tools()
        tool_names = [tool.name for tool in tools]

        assert "check_availability" in tool_names
        assert "create_reservation" in tool_names
        assert "create_lead" in tool_names
        assert "generate_proposal" in tool_names
        assert "get_dashboard_metrics" in tool_names

    def test_get_tool(self):
        """Testa obtenção de ferramenta específica."""
        tool = AIToolRegistry.get_tool("create_lead")

        assert tool is not None
        assert tool.name == "create_lead"
        assert len(tool.parameters) > 0

    def test_get_nonexistent_tool(self):
        """Testa obtenção de ferramenta inexistente."""
        tool = AIToolRegistry.get_tool("tool_inexistente")
        assert tool is None

    def test_tool_schema_export(self):
        """Testa exportação de schema JSON da ferramenta."""
        tool = AIToolRegistry.get_tool("create_reservation")
        schema = tool.to_json_schema()

        assert "type" in schema
        assert "parameters" in schema
        assert "properties" in schema["parameters"]
        assert schema["type"] == "object"


class TestChatServiceIntegration:
    """Testa integração ChatService com OpenAIResponsesService."""

    @patch("app.services.openai_responses_service.OpenAI")
    def test_send_message_with_responses_api(self, mock_openai_class, db_session):
        """Testa envio de mensagem usando Responses API."""
        # Setup
        user = User(
            name="Test User",
            username="testuser",
            email="test@example.com",
            phone="11999999999",
            password_hash="hash",
        )
        db_session.add(user)
        db_session.commit()

        # Mock da API
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.output_text = "Resposta teste"
        mock_response.tool_calls = []
        mock_client.responses.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4"
            mock_settings.openai_timeout_seconds = 30

            # Execute
            chat_service = ChatService(db_session)
            payload = ChatSendRequest(text="Teste", conversation_id=None)

            conversation, user_msg, assistant_msg = chat_service.send(
                user,
                payload,
                use_responses_api=True,
            )

            # Assertions
            assert user_msg.text == "Teste"
            assert assistant_msg.text == "Resposta teste"
            assert conversation.id is not None

    def test_build_conversation_history(self, db_session):
        """Testa construção de histórico da conversa."""
        # Setup
        conversation = Conversation(user_id=1, title="Teste")
        db_session.add(conversation)
        db_session.flush()

        for i in range(12):  # 12 mensagens para testar limit de 10
            role = "user" if i % 2 == 0 else "assistant"
            msg = Message(conversation_id=conversation.id, role=role, text=f"Mensagem {i}")
            db_session.add(msg)
        db_session.commit()

        # Execute
        chat_service = ChatService(db_session)
        history = chat_service._build_conversation_history(conversation.id)

        # Assertions
        assert len(history) == 10  # Deve limitar a 10
        assert all(isinstance(h, ConversationMessage) for h in history)

    def test_build_instructions_base(self):
        """Testa construção de instruções base."""
        instructions = ChatService._build_instructions(None)
        assert "AXI" in instructions
        assert "Alici" in instructions

    def test_build_instructions_sales_agent(self):
        """Testa construção de instruções para agente de vendas."""
        instructions = ChatService._build_instructions("sales")
        assert "vendas" in instructions or "sales" in instructions.lower()

    def test_build_instructions_support_agent(self):
        """Testa construção de instruções para agente de suporte."""
        instructions = ChatService._build_instructions("support")
        assert "suporte" in instructions or "support" in instructions.lower()
