#!/usr/bin/env python3
"""
Verificador rápido: Chat está respondendo?
Executa 5 verificações essenciais em segundos.
"""

import sys
import subprocess
from pathlib import Path

def check_api_key():
    """Verifica se OPENAI_API_KEY está configurada."""
    from app.core.config import settings
    if settings.effective_openai_api_key:
        return True, "✅ OPENAI_API_KEY configurada"
    return False, "❌ OPENAI_API_KEY NÃO CONFIGURADA - Configure em .env"

def check_service():
    """Verifica se OpenAIResponsesService funciona."""
    try:
        from app.services.openai_responses_service import OpenAIResponsesService
        service = OpenAIResponsesService()
        if service.is_configured():
            return True, "✅ OpenAIResponsesService OK"
        return False, "❌ OpenAIResponsesService não configurado"
    except Exception as e:
        return False, f"❌ Erro em OpenAIResponsesService: {e}"

def check_database():
    """Verifica se database funciona."""
    try:
        from app.core.database import init_db
        init_db()
        return True, "✅ Database OK"
    except Exception as e:
        return False, f"❌ Erro em Database: {e}"

def check_imports():
    """Verifica se todos os imports funcionam."""
    try:
        from app.services.chat_service import ChatService
        from app.services.tool_executor import ToolExecutor
        from app.schemas.openai_responses import OpenAIResponsesOutput
        return True, "✅ Todos os imports OK"
    except Exception as e:
        return False, f"❌ Erro em imports: {e}"

def check_healthcheck():
    """Executa healthcheck da API."""
    try:
        from app.services.openai_responses_service import OpenAIResponsesService
        service = OpenAIResponsesService()
        result = service.healthcheck()
        if result['status'] == 'ok':
            return True, "✅ Healthcheck OK (API respondendo)"
        else:
            error = result.get('error_type', 'unknown')
            return False, f"❌ Healthcheck falhou: {error}"
    except Exception as e:
        return False, f"❌ Erro no healthcheck: {e}"

def main():
    print("\n" + "="*70)
    print("  🔍 VERIFICADOR RÁPIDO: CHAT RESPONDENDO?")
    print("="*70 + "\n")
    
    checks = [
        ("1. API Key", check_api_key),
        ("2. Service", check_service),
        ("3. Database", check_database),
        ("4. Imports", check_imports),
        ("5. API Connection", check_healthcheck),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"{name}...", end=" ", flush=True)
        success, message = check_func()
        results.append((success, message))
        print(message)
    
    print("\n" + "="*70)
    
    passed = sum(1 for success, _ in results if success)
    total = len(results)
    
    if passed == total:
        print(f"  ✅ TUDO OK! ({passed}/{total} verificações passaram)")
        print("\n  🚀 Chat está pronto para usar!")
        print("\n  Próximo passo:")
        print("     python test_chat_manual.py")
    else:
        print(f"  ⚠️  PROBLEMAS ENCONTRADOS ({total - passed}/{total})")
        print("\n  Erros:")
        for success, message in results:
            if not success:
                print(f"     {message}")
        
        print("\n  Solução:")
        print("     1. Leia LEIA_PRIMEIRO.txt")
        print("     2. Execute: python debug_chat.py")
        print("     3. Verifique TROUBLESHOOTING_CHAT.md")
    
    print("\n" + "="*70 + "\n")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
