"""Validation tests for OpenAI Responses API and tool integration."""

from unittest.mock import MagicMock, patch

from app.schemas.openai_responses import ConversationMessage, OpenAIResponsesOutput
from app.services.openai_responses_service import OpenAIResponsesService
from app.services.tool_executor import ToolExecutor


def _mock_responses_service(output_text: str, tool_calls=None) -> MagicMock:
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.output_text = output_text
    mock_response.tool_calls = tool_calls
    mock_client.responses.create.return_value = mock_response
    return mock_client


def test_openai_responses_returns_correct_type():
    """generate_response returns OpenAIResponsesOutput."""
    with patch("app.services.openai_responses_service.OpenAI") as mock_openai_class:
        mock_openai_class.return_value = _mock_responses_service("Teste resposta")

        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4"
            mock_settings.openai_timeout_seconds = 30

            response = OpenAIResponsesService().generate_response(user_message="Teste")

            assert isinstance(response, OpenAIResponsesOutput)
            assert hasattr(response, "output_text")
            assert hasattr(response, "tool_calls")
            assert response.output_text == "Teste resposta"
            assert response.tool_calls is None or isinstance(response.tool_calls, list)


def test_conversation_history_conversion():
    """ConversationMessage history is accepted and converted."""
    with patch("app.services.openai_responses_service.OpenAI") as mock_openai_class:
        mock_openai_class.return_value = _mock_responses_service("Resposta com contexto")

        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4"
            mock_settings.openai_timeout_seconds = 30

            history = [
                ConversationMessage(role="user", content="Ola"),
                ConversationMessage(role="assistant", content="Oi! Como posso ajudar?"),
            ]
            response = OpenAIResponsesService().generate_response(
                user_message="Teste com historico",
                conversation_history=history,
            )

            assert isinstance(response, OpenAIResponsesOutput)
            assert response.output_text == "Resposta com contexto"


def test_agent_response_with_dict_context():
    """generate_agent_response accepts dict company_context."""
    with patch("app.services.openai_responses_service.OpenAI") as mock_openai_class:
        mock_openai_class.return_value = _mock_responses_service("Resposta do agente")

        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4"
            mock_settings.openai_timeout_seconds = 30

            response = OpenAIResponsesService().generate_agent_response(
                agent_name="vendedor",
                agent_prompt="Voce vende produtos",
                user_message="Quero comprar",
                company_context={"user_id": 123, "company": "AXI"},
            )

            assert isinstance(response, OpenAIResponsesOutput)
            assert response.output_text == "Resposta do agente"


def test_tool_executor_integration():
    """ToolExecutor runs known tools and rejects unknown ones."""
    executor = ToolExecutor()

    result = executor.execute(
        "create_lead",
        {
            "name": "Joao",
            "email": "joao@example.com",
        },
    )
    assert result.success is True
    assert result.tool_name == "create_lead"
    assert "lead_id" in result.result

    result = executor.execute("tool_inexistente", {})
    assert result.success is False
    assert "tool_inexistente" in result.error
    assert "encontrada" in result.error


def test_tool_calls_extraction():
    """Tool calls are extracted from the API response."""
    with patch("app.services.openai_responses_service.OpenAI") as mock_openai_class:
        mock_openai_class.return_value = _mock_responses_service(
            "Vou criar uma reserva para voce",
            tool_calls=[
                {
                    "name": "create_reservation",
                    "arguments": {"guest_name": "Joao", "check_in": "2026-04-20", "room_type": "standard"},
                }
            ],
        )

        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4"
            mock_settings.openai_timeout_seconds = 30

            response = OpenAIResponsesService().generate_response(user_message="Quero fazer uma reserva")

            assert isinstance(response, OpenAIResponsesOutput)
            assert response.output_text == "Vou criar uma reserva para voce"
            assert response.tool_calls is not None
            assert len(response.tool_calls) == 1
            assert response.tool_calls[0]["tool_name"] == "create_reservation"
            assert response.tool_calls[0]["tool_args"]["guest_name"] == "Joao"


if __name__ == "__main__":
    test_openai_responses_returns_correct_type()
    test_conversation_history_conversion()
    test_agent_response_with_dict_context()
    test_tool_executor_integration()
    test_tool_calls_extraction()
    print("OK all validations passed")
