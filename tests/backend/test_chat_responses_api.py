"""
Testes para Chat com OpenAI Responses API.
"""

import pytest
from unittest.mock import MagicMock, patch
from app.schemas.openai_responses import OpenAIResponsesOutput, ToolCall
from app.services.openai_responses_service import OpenAIResponsesError


@pytest.mark.usefixtures("auth_headers", "client")
class TestChatResponsesAPI:
    """Testes para /api/chat/responses endpoint."""

    def test_chat_responses_basic(self, client, auth_headers):
        """Testa envio de mensagem via Responses API."""
        with patch("app.services.openai_responses_service.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.output_text = "Ótimo! Vou ajudar com sua mensagem."
            mock_response.tool_calls = None
            mock_client.responses.create.return_value = mock_response
            mock_openai.return_value = mock_client

            with patch("app.services.openai_responses_service.settings") as mock_settings:
                mock_settings.effective_openai_api_key = "sk-test"
                mock_settings.openai_model = "gpt-4o-mini"
                mock_settings.openai_timeout_seconds = 30

                response = client.post(
                    "/api/chat/responses",
                    headers=auth_headers,
                    json={"text": "Teste de Responses API", "conversation_id": None},
                )

                assert response.status_code == 200
                body = response.json()
                assert body["output_text"] == "Ótimo! Vou ajudar com sua mensagem."
                assert "conversation_id" in body
                assert "message_id" in body

    def test_chat_responses_with_conversation_history(self, client, auth_headers):
        """Testa Responses API mantendo histórico de conversa."""
        with patch("app.services.openai_responses_service.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.output_text = "Continuando a conversa anterior..."
            mock_response.tool_calls = None
            mock_client.responses.create.return_value = mock_response
            mock_openai.return_value = mock_client

            with patch("app.services.openai_responses_service.settings") as mock_settings:
                mock_settings.effective_openai_api_key = "sk-test"
                mock_settings.openai_model = "gpt-4o-mini"
                mock_settings.openai_timeout_seconds = 30

                # Primeira mensagem
                response1 = client.post(
                    "/api/chat/responses",
                    headers=auth_headers,
                    json={"text": "Primeira mensagem", "conversation_id": None},
                )
                assert response1.status_code == 200
                conv_id = response1.json()["conversation_id"]

                # Segunda mensagem mesma conversa
                response2 = client.post(
                    "/api/chat/responses",
                    headers=auth_headers,
                    json={"text": "Segunda mensagem", "conversation_id": conv_id},
                )

                assert response2.status_code == 200
                assert response2.json()["output_text"] == "Continuando a conversa anterior..."

    def test_chat_responses_with_tool_calls(self, client, auth_headers):
        """Testa Responses API com tool calling."""
        with patch("app.services.openai_responses_service.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.output_text = "Vou criar uma reserva para você"
            mock_response.tool_calls = [
                {
                    "name": "create_reservation",
                    "arguments": {
                        "guest_name": "João Silva",
                        "check_in": "2026-04-20",
                        "check_out": "2026-04-22",
                        "room_type": "standard",
                        "guests": 2,
                    },
                }
            ]
            mock_client.responses.create.return_value = mock_response
            mock_openai.return_value = mock_client

            with patch("app.services.openai_responses_service.settings") as mock_settings:
                mock_settings.effective_openai_api_key = "sk-test"
                mock_settings.openai_model = "gpt-4o-mini"
                mock_settings.openai_timeout_seconds = 30

                response = client.post(
                    "/api/chat/responses",
                    headers=auth_headers,
                    json={"text": "Quero fazer uma reserva", "conversation_id": None},
                )

                assert response.status_code == 200
                body = response.json()
                assert body["output_text"] == "Vou criar uma reserva para você"
                # Tool foi executada e mensagem persistida

    def test_chat_responses_error_returns_ai_error(self, client, auth_headers):
        """Testa erro real quando Responses API falha."""
        with patch("app.services.openai_responses_service.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_client.responses.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client

            with patch("app.services.openai_responses_service.settings") as mock_settings:
                mock_settings.effective_openai_api_key = "sk-test"
                mock_settings.openai_model = "gpt-4o-mini"
                mock_settings.openai_timeout_seconds = 30

                response = client.post(
                    "/api/chat/responses",
                    headers=auth_headers,
                    json={"text": "Teste de erro", "conversation_id": None},
                )

                assert response.status_code == 503


@pytest.mark.usefixtures("auth_headers", "client")
class TestChatAgentSpecialized:
    """Testes para /api/chat/agent-respond endpoint."""

    @pytest.mark.parametrize("agent_name", ["sales", "support", "operations"])
    def test_chat_agent_respond(self, client, auth_headers, agent_name):
        """Testa chat com agentes especializados."""
        with patch("app.services.openai_responses_service.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.output_text = f"Resposta do agente {agent_name}"
            mock_response.tool_calls = None
            mock_client.responses.create.return_value = mock_response
            mock_openai.return_value = mock_client

            with patch("app.services.openai_responses_service.settings") as mock_settings:
                mock_settings.effective_openai_api_key = "sk-test"
                mock_settings.openai_model = "gpt-4o-mini"
                mock_settings.openai_timeout_seconds = 30

                response = client.post(
                    f"/api/chat/agent-respond?agent_name={agent_name}",
                    headers=auth_headers,
                    json={"text": f"Pergunta para {agent_name}", "conversation_id": None},
                )

                assert response.status_code == 200
                body = response.json()
                assert f"{agent_name}" in body["output_text"].lower()

    def test_chat_agent_invalid(self, client, auth_headers):
        """Testa chat com agente inválido."""
        response = client.post(
            "/api/chat/agent-respond?agent_name=invalid_agent",
            headers=auth_headers,
            json={"text": "Teste", "conversation_id": None},
        )

        assert response.status_code == 400
        assert "não encontrado" in response.json()["detail"].lower()


@pytest.mark.usefixtures("auth_headers", "client")
class TestChatTools:
    """Testes para /api/chat/tools endpoint."""

    def test_get_available_tools(self, client, auth_headers):
        """Testa listagem de ferramentas disponíveis."""
        response = client.get("/api/chat/tools", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert "tools" in body
        tools = body["tools"]
        
        # Validar estrutura
        assert len(tools) > 0
        
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
            assert isinstance(tool["parameters"], list)
            
            # Cada parâmetro deve ter estrutura completa
            for param in tool["parameters"]:
                assert "name" in param
                assert "type" in param
                assert "description" in param

    def test_tools_include_standard_tools(self, client, auth_headers):
        """Testa se ferramentas padrão estão listadas."""
        response = client.get("/api/chat/tools", headers=auth_headers)

        assert response.status_code == 200
        tools = {t["name"]: t for t in response.json()["tools"]}
        
        expected_tools = [
            "create_reservation",
            "check_availability",
            "create_lead",
            "generate_proposal",
            "get_dashboard_metrics",
        ]
        
        for expected in expected_tools:
            assert expected in tools, f"Tool {expected} não encontrado"
            tool = tools[expected]
            assert tool["description"], f"Tool {expected} sem descrição"
            assert len(tool["parameters"]) > 0, f"Tool {expected} sem parâmetros"


@pytest.mark.usefixtures("auth_headers", "client")
class TestChatIntegration:
    """Testes de integração do chat."""

    def test_chat_send_vs_responses_api(self, client, auth_headers):
        """Compara comportamento de /api/chat/send vs /api/chat/responses."""
        with patch("app.services.openai_responses_service.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.output_text = "Resposta da API"
            mock_response.tool_calls = None
            mock_client.responses.create.return_value = mock_response
            mock_openai.return_value = mock_client

            with patch("app.services.openai_responses_service.settings") as mock_settings:
                mock_settings.effective_openai_api_key = "sk-test-key"
                mock_settings.openai_model = "gpt-4o-mini"
                mock_settings.openai_timeout_seconds = 30

                # Ambos endpoints devem funcionar
                response1 = client.post(
                    "/api/chat/send",
                    headers=auth_headers,
                    json={"text": "Teste 1", "conversation_id": None},
                )
                assert response1.status_code == 200

                response2 = client.post(
                    "/api/chat/responses",
                    headers=auth_headers,
                    json={"text": "Teste 2", "conversation_id": None},
                )
                assert response2.status_code == 200

                # Ambos devem ter mensagens persistidas
                convs = client.get("/api/chat/conversations", headers=auth_headers)
                assert len(convs.json()) >= 2

    def test_chat_billing_integration(self, client, auth_headers, db_session):
        """Testa integração com billing (check_limit)."""
        with patch("app.services.openai_responses_service.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.output_text = "Resposta"
            mock_response.tool_calls = None
            mock_client.responses.create.return_value = mock_response
            mock_openai.return_value = mock_client

            with patch("app.services.openai_responses_service.settings") as mock_settings:
                mock_settings.effective_openai_api_key = "sk-test"
                mock_settings.openai_model = "gpt-4o-mini"
                mock_settings.openai_timeout_seconds = 30

                response = client.post(
                    "/api/chat/responses",
                    headers=auth_headers,
                    json={"text": "Teste billing", "conversation_id": None},
                )

                assert response.status_code == 200
                # Billing check passou (não retornou 402 ou similar)

    def test_chat_persistence(self, client, auth_headers):
        """Testa se mensagens são persistidas corretamente."""
        with patch("app.services.openai_responses_service.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.output_text = "Resposta persistida"
            mock_response.tool_calls = None
            mock_client.responses.create.return_value = mock_response
            mock_openai.return_value = mock_client

            with patch("app.services.openai_responses_service.settings") as mock_settings:
                mock_settings.effective_openai_api_key = "sk-test"
                mock_settings.openai_model = "gpt-4o-mini"
                mock_settings.openai_timeout_seconds = 30

                # Enviar mensagem
                send_response = client.post(
                    "/api/chat/responses",
                    headers=auth_headers,
                    json={"text": "Test persistence", "conversation_id": None},
                )

                assert send_response.status_code == 200
                conv_id = send_response.json()["conversation_id"]
                msg_id = send_response.json()["message_id"]

                # Verificar persistência
                messages = client.get(
                    f"/api/chat/conversations/{conv_id}/messages",
                    headers=auth_headers,
                ).json()

                assert len(messages) == 2  # user + assistant
                user_msg = next(m for m in messages if m["role"] == "user")
                assistant_msg = next(m for m in messages if m["role"] == "assistant")

                assert user_msg["text"] == "Test persistence"
                assert assistant_msg["text"] == "Resposta persistida"


# Testes de aceitação (scenario-based)

def test_chat_scenario_create_reservation(client, auth_headers):
    """Cenário: Usuário solicita reserva via chat."""
    with patch("app.services.openai_responses_service.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.output_text = "Perfeito! Vou criar a reserva para você."
        mock_response.tool_calls = [
            {
                "name": "create_reservation",
                "arguments": {
                    "guest_name": "Maria Silva",
                    "check_in": "2026-04-20",
                    "check_out": "2026-04-22",
                    "room_type": "deluxe",
                    "guests": 2,
                },
            }
        ]
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_timeout_seconds = 30

            response = client.post(
                "/api/chat/responses",
                headers=auth_headers,
                json={
                    "text": "Gostaria de fazer uma reserva para 2 pessoas, de 20 a 22 de abril, quarto deluxe",
                    "conversation_id": None,
                },
            )

            assert response.status_code == 200
            body = response.json()
            assert "Perfeito" in body["output_text"]
            # Tool de reserva foi executada (sem erro)


def test_chat_scenario_lead_creation(client, auth_headers):
    """Cenário: Agente de vendas cria lead via chat."""
    with patch("app.services.openai_responses_service.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.output_text = "Registrei seu interesse! Um gerente entrará em contato."
        mock_response.tool_calls = [
            {
                "name": "create_lead",
                "arguments": {
                    "name": "Carlos Santos",
                    "email": "carlos@example.com",
                    "phone": "11987654321",
                    "lead_source": "chat",
                },
            }
        ]
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = "sk-test"
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_timeout_seconds = 30

            response = client.post(
                "/api/chat/agent-respond?agent_name=sales",
                headers=auth_headers,
                json={
                    "text": "Tenho interesse em seus serviços premium",
                    "conversation_id": None,
                },
            )

            assert response.status_code == 200
            body = response.json()
            assert "Registrei" in body["output_text"] or "interesse" in body["output_text"].lower()
