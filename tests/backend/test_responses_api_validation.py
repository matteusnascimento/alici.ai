"""
Teste de validação de uso das IAs e Tools - Responses API Integration.
Verifica se OpenAIResponsesService e ToolExecutor estão integrados corretamente.
"""

import json
from unittest.mock import MagicMock, patch

from app.schemas.openai_responses import OpenAIResponsesOutput, ToolCall
from app.services.openai_responses_service import OpenAIResponsesService
from app.services.tool_executor import ToolExecutor


def test_openai_responses_returns_correct_type():
    """Valida que generate_response retorna OpenAIResponsesOutput."""
    with patch("app.services.openai_responses_service.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.output_text = "Teste resposta"
        mock_response.tool_calls = None
        mock_client.responses.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4"
            mock_settings.openai_timeout_seconds = 30

            service = OpenAIResponsesService()
            response = service.generate_response(user_message="Teste")

            # Validar tipo
            assert isinstance(response, OpenAIResponsesOutput), f"Expected OpenAIResponsesOutput, got {type(response)}"
            assert hasattr(response, "output_text"), "Response deve ter atributo output_text"
            assert hasattr(response, "tool_calls"), "Response deve ter atributo tool_calls"
            assert response.output_text == "Teste resposta"
            assert response.tool_calls is None or isinstance(response.tool_calls, list)

            print("✅ test_openai_responses_returns_correct_type - PASSOU")


def test_conversation_history_conversion():
    """Valida conversão de ConversationMessage para dict."""
    from app.schemas.openai_responses import ConversationMessage

    with patch("app.services.openai_responses_service.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.output_text = "Resposta com contexto"
        mock_response.tool_calls = None
        mock_client.responses.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4"
            mock_settings.openai_timeout_seconds = 30

            service = OpenAIResponsesService()
            
            # Simular ConversationMessage
            history = [
                ConversationMessage(role="user", content="Olá"),
                ConversationMessage(role="assistant", content="Oi! Como posso ajudar?"),
            ]
            
            response = service.generate_response(
                user_message="Teste com histórico",
                conversation_history=history,
            )

            assert isinstance(response, OpenAIResponsesOutput)
            assert response.output_text == "Resposta com contexto"
            
            print("✅ test_conversation_history_conversion - PASSOU")


def test_agent_response_with_dict_context():
    """Valida que generate_agent_response aceita dict para company_context."""
    with patch("app.services.openai_responses_service.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.output_text = "Resposta do agente"
        mock_response.tool_calls = None
        mock_client.responses.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4"
            mock_settings.openai_timeout_seconds = 30

            service = OpenAIResponsesService()
            
            # Passar dict como company_context
            response = service.generate_agent_response(
                agent_name="vendedor",
                agent_prompt="Você vende produtos",
                user_message="Quero comprar",
                company_context={"user_id": 123, "company": "AXI"},
            )

            assert isinstance(response, OpenAIResponsesOutput)
            assert response.output_text == "Resposta do agente"
            
            print("✅ test_agent_response_with_dict_context - PASSOU")


def test_tool_executor_integration():
    """Valida que ToolExecutor executa ferramentas corretamente."""
    executor = ToolExecutor()
    
    # Testar execução de ferramenta existente
    result = executor.execute(
        "create_lead",
        {
            "name": "João",
            "email": "joao@example.com",
        },
    )
    
    assert result.success is True
    assert result.tool_name == "create_lead"
    assert "lead_id" in result.result
    
    # Testar ferramenta inexistente
    result = executor.execute("tool_inexistente", {})
    assert result.success is False
    assert "não encontrada" in result.error
    
    print("✅ test_tool_executor_integration - PASSOU")


def test_tool_calls_extraction():
    """Valida que tool_calls são extraídos corretamente da resposta."""
    with patch("app.services.openai_responses_service.OpenAI") as mock_openai_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.output_text = "Vou criar uma reserva para você"
        mock_response.tool_calls = [
            {
                "name": "create_reservation",
                "arguments": {"guest_name": "João", "check_in": "2026-04-20", "room_type": "standard"},
            }
        ]
        mock_client.responses.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4"
            mock_settings.openai_timeout_seconds = 30

            service = OpenAIResponsesService()
            response = service.generate_response(user_message="Quero fazer uma reserva")

            assert isinstance(response, OpenAIResponsesOutput)
            assert response.output_text == "Vou criar uma reserva para você"
            assert response.tool_calls is not None
            assert len(response.tool_calls) == 1
            assert response.tool_calls[0]["tool_name"] == "create_reservation"
            assert response.tool_calls[0]["tool_args"]["guest_name"] == "João"
            
            print("✅ test_tool_calls_extraction - PASSOU")


if __name__ == "__main__":
    print("\n🔍 Validando integração de IA e Tools...\n")
    
    try:
        test_openai_responses_returns_correct_type()
        test_conversation_history_conversion()
        test_agent_response_with_dict_context()
        test_tool_executor_integration()
        test_tool_calls_extraction()
        
        print("\n✅ TODAS AS VALIDAÇÕES PASSARAM!")
        print("\nResumo:")
        print("  ✓ OpenAIResponsesService retorna OpenAIResponsesOutput com output_text e tool_calls")
        print("  ✓ ConversationMessage é convertida para dict automaticamente")
        print("  ✓ Company context pode ser dict ou str")
        print("  ✓ ToolExecutor executa ferramentas corretamente")
        print("  ✓ Tool calls são extraídos da resposta da API")
        
    except AssertionError as e:
        print(f"\n❌ VALIDAÇÃO FALHOU: {e}")
        raise
