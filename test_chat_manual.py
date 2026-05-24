#!/usr/bin/env python3
"""
Script de teste manual do Chat com Responses API.
Executa testes contra um servidor AXI rodando localmente.

Uso:
    python test_chat_manual.py [--host localhost] [--port 8000] [--token AUTH_TOKEN]

Exemplo:
    python test_chat_manual.py --host localhost --port 8000
"""

import argparse
import json
import sys
from typing import Any, Optional

import httpx


class ChatTester:
    """Testador do chat API."""

    def __init__(self, base_url: str, auth_token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.headers = {"Content-Type": "application/json"}
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
        self.client = httpx.Client(base_url=self.base_url, timeout=30.0)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.client.close()

    def _print_separator(self, title: str = ""):
        """Imprime separador visual."""
        if title:
            print(f"\n{'=' * 80}")
            print(f"  {title}")
            print(f"{'=' * 80}\n")
        else:
            print(f"\n{'-' * 80}\n")

    def _print_response(self, status: int, data: Any):
        """Imprime resposta formatada."""
        if status >= 200 and status < 300:
            print(f"✅ Status {status}")
        else:
            print(f"❌ Status {status}")
        print(json.dumps(data, indent=2, ensure_ascii=False))

    def test_health(self) -> bool:
        """Testa conectividade com servidor."""
        self._print_separator("Teste 1: Health Check")
        try:
            response = self.client.get("/api/health")
            self._print_response(response.status_code, response.json())
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Erro de conectividade: {e}")
            return False

    def test_get_tools(self) -> bool:
        """Testa listagem de ferramentas."""
        self._print_separator("Teste 2: Listar Ferramentas Disponíveis")
        try:
            response = self.client.get("/api/chat/tools", headers=self.headers)
            self._print_response(response.status_code, response.json())
            
            if response.status_code == 200:
                tools = response.json().get("tools", [])
                print(f"\n📋 Ferramentas encontradas: {len(tools)}")
                for tool in tools:
                    params = ", ".join([p["name"] for p in tool.get("parameters", [])])
                    print(f"  • {tool['name']}: {params}")
                return len(tools) > 0
            return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False

    def test_chat_send_basic(self, text: str = "Olá! Como você funciona?") -> Optional[dict]:
        """Testa envio de mensagem via /api/chat/send."""
        self._print_separator("Teste 3: Chat Simples (/api/chat/send)")
        try:
            payload = {"text": text, "conversation_id": None}
            print(f"📤 Enviando: {text}\n")
            
            response = self.client.post("/api/chat/send", headers=self.headers, json=payload)
            self._print_response(response.status_code, response.json())
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Chat funcionando!")
                print(f"   Conversa ID: {data['conversation']['id']}")
                print(f"   Resposta: {data['assistant_message']['text'][:100]}...")
                return data
            return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None

    def test_chat_responses_api(self, text: str = "Olá! Como você funciona?") -> Optional[dict]:
        """Testa envio de mensagem via /api/chat/responses (nova API)."""
        self._print_separator("Teste 4: Chat com Responses API (/api/chat/responses)")
        try:
            payload = {"text": text, "conversation_id": None}
            print(f"📤 Enviando: {text}\n")
            
            response = self.client.post("/api/chat/responses", headers=self.headers, json=payload)
            self._print_response(response.status_code, response.json())
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Responses API funcionando!")
                print(f"   Conversa ID: {data.get('conversation_id')}")
                print(f"   Resposta: {data.get('output_text', '')[:100]}...")
                return data
            return None
        except Exception as e:
            print(f"❌ Erro: {e}")
            return None

    def test_chat_with_history(self, conversation_id: int):
        """Testa chat mantendo histórico."""
        self._print_separator("Teste 5: Chat com Histórico")
        try:
            messages = [
                "Qual é o melhor quarto?",
                "E qual é o preço?",
                "Gostaria de fazer uma reserva",
            ]
            
            for i, text in enumerate(messages, 1):
                print(f"\n📤 Mensagem {i}: {text}")
                
                payload = {"text": text, "conversation_id": conversation_id}
                response = self.client.post("/api/chat/responses", headers=self.headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Resposta: {data.get('output_text', '')[:80]}...")
                else:
                    print(f"❌ Erro: {response.status_code}")
                    return False
            
            return True
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False

    def test_chat_agent(self, agent_name: str = "sales", text: str = "Tenho interesse em contratar"):
        """Testa chat com agente especializado."""
        self._print_separator(f"Teste 6: Chat com Agente ({agent_name})")
        try:
            payload = {"text": text, "conversation_id": None}
            print(f"📤 Enviando para {agent_name}: {text}\n")
            
            response = self.client.post(
                f"/api/chat/agent-respond?agent_name={agent_name}",
                headers=self.headers,
                json=payload,
            )
            self._print_response(response.status_code, response.json())
            
            if response.status_code == 200:
                print(f"\n✅ Agente {agent_name} funcionando!")
                return True
            return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False

    def test_conversation_list(self):
        """Testa listagem de conversas."""
        self._print_separator("Teste 7: Listar Conversas")
        try:
            response = self.client.get("/api/chat/conversations", headers=self.headers)
            self._print_response(response.status_code, response.json())
            
            if response.status_code == 200:
                convs = response.json()
                print(f"\n📊 Total de conversas: {len(convs)}")
                for conv in convs[:3]:  # Mostrar apenas 3 primeiras
                    print(f"  • {conv['title']} (ID: {conv['id']})")
                return True
            return False
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False

    def run_full_test(self):
        """Executa suite completa de testes."""
        results = {}
        
        print("\n" + "=" * 80)
        print("  🧪 TESTE COMPLETO DO CHAT API")
        print("=" * 80)
        
        # 1. Health
        results["health"] = self.test_health()
        if not results["health"]:
            print("\n❌ Servidor não está respondendo. Abortando testes.")
            return results
        
        # 2. Tools
        results["tools"] = self.test_get_tools()
        
        # 3. Chat simples
        chat_data = self.test_chat_send_basic()
        results["chat_send"] = chat_data is not None
        
        # 4. Responses API
        responses_data = self.test_chat_responses_api()
        results["chat_responses"] = responses_data is not None
        
        # 5. Chat com histórico (se temos conversation_id)
        if responses_data:
            conv_id = responses_data.get("conversation_id")
            results["chat_history"] = self.test_chat_with_history(conv_id)
        
        # 6. Agentes
        results["chat_sales"] = self.test_chat_agent("sales")
        results["chat_support"] = self.test_chat_agent("support", "Tenho um problema com...")
        
        # 7. Listar conversas
        results["conversations"] = self.test_conversation_list()
        
        # Resumo
        self._print_separator("📊 RESUMO DOS TESTES")
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test, result in results.items():
            status = "✅" if result else "❌"
            print(f"{status} {test}")
        
        print(f"\nResultado: {passed}/{total} testes passaram")
        
        if passed == total:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
        else:
            print(f"\n⚠️  {total - passed} teste(s) falharam")
        
        return results


def main():
    parser = argparse.ArgumentParser(description="Tester do Chat API")
    parser.add_argument("--host", default="localhost", help="Host do servidor (default: localhost)")
    parser.add_argument("--port", type=int, default=8000, help="Porta do servidor (default: 8000)")
    parser.add_argument("--token", help="Token de autenticação JWT")

    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"

    try:
        with ChatTester(base_url, args.token) as tester:
            results = tester.run_full_test()
            
            # Exit code baseado nos resultados
            passed = sum(1 for v in results.values() if v)
            total = len(results)
            
            sys.exit(0 if passed == total else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
