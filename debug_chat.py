#!/usr/bin/env python3
"""
Script de debug para identificar problema no chat.
Executa testes simples para ver exatamente onde falha.
"""

import sys
import logging
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("\n" + "="*80)
print("  🔍 DEBUG: Problema no Chat")
print("="*80 + "\n")

# Test 1: Settings
print("📋 Teste 1: Verificando Configurações\n")
try:
    from app.core.config import settings
    print(f"✅ Settings carregado")
    print(f"   - effective_openai_api_key: {'[SET]' if settings.effective_openai_api_key else '[MISSING]'}")
    print(f"   - openai_model: {settings.openai_model}")
    print(f"   - openai_timeout_seconds: {settings.openai_timeout_seconds}")
    
    if not settings.effective_openai_api_key:
        print("\n❌ PROBLEMA IDENTIFICADO: OPENAI_API_KEY não configurada!")
        print("   Configure em .env: OPENAI_API_KEY=sk-...")
        sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao carregar settings: {e}")
    sys.exit(1)

# Test 2: OpenAIResponsesService
print("\n📋 Teste 2: OpenAIResponsesService\n")
try:
    from app.services.openai_responses_service import OpenAIResponsesService
    service = OpenAIResponsesService()
    print(f"✅ OpenAIResponsesService criado")
    print(f"   - is_configured(): {service.is_configured()}")
    print(f"   - model: {service.model}")
    print(f"   - client: {type(service.client)}")
    
    if not service.is_configured():
        print("\n❌ PROBLEMA: Service não configurado!")
        sys.exit(1)
except Exception as e:
    print(f"❌ Erro crítico: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Healthcheck
print("\n📋 Teste 3: Healthcheck da OpenAI\n")
try:
    result = service.healthcheck()
    print(f"✅ Healthcheck resultado: {result['status']}")
    if result['status'] == 'error':
        print(f"❌ Erro no healthcheck: {result.get('message')}")
        print(f"   Error type: {result.get('error_type')}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Erro no healthcheck: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Schema
print("\n📋 Teste 4: Schema de Resposta\n")
try:
    from app.schemas.openai_responses import OpenAIResponsesOutput
    output = OpenAIResponsesOutput(output_text="Test", tool_calls=None)
    print(f"✅ OpenAIResponsesOutput criado")
    print(f"   - output_text: {output.output_text}")
    print(f"   - tool_calls: {output.tool_calls}")
except Exception as e:
    print(f"❌ Erro no schema: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: ChatService
print("\n📋 Teste 5: ChatService Setup\n")
try:
    from sqlalchemy.orm import Session
    from app.core.database import get_db, init_db
    from app.services.chat_service import ChatService
    from app.models.user import User
    
    print(f"✅ ChatService importado")
    
    # Inicializar DB
    print(f"\n   Inicializando banco de dados...")
    init_db()
    print(f"   ✅ Database inicializado")
    
except Exception as e:
    print(f"❌ Erro ao setup ChatService: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Mock Chat
print("\n📋 Teste 6: Teste de Chat com Mock\n")
try:
    from unittest.mock import MagicMock, patch
    from app.schemas.openai_responses import ConversationMessage
    
    # Mock do OpenAI
    with patch("app.services.openai_responses_service.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.output_text = "✅ IA respondeu com sucesso!"
        mock_response.tool_calls = None
        mock_client.responses.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch("app.services.openai_responses_service.settings") as mock_settings:
            mock_settings.effective_openai_api_key = "sk-mock-test"
            mock_settings.openai_model = "gpt-4o-mini"
            mock_settings.openai_timeout_seconds = 30
            
            service_mock = OpenAIResponsesService()
            
            # Testar generate_response
            response = service_mock.generate_response(
                user_message="Teste",
                instructions="Teste instrução",
                conversation_history=[]
            )
            
            print(f"✅ Response retornado")
            print(f"   - Type: {type(response)}")
            print(f"   - output_text: {response.output_text}")
            print(f"   - tool_calls: {response.tool_calls}")
            
except Exception as e:
    print(f"❌ Erro no teste mock: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("  ✅ TODOS OS TESTES PASSARAM - SISTEMA FUNCIONANDO")
print("="*80)
print("\nPróximos passos:")
print("1. Verifique se OPENAI_API_KEY está corretamente configurada em .env")
print("2. Verifique os logs do servidor para erros específicos")
print("3. Execute o teste manual:")
print("   python test_chat_manual.py")
print()
