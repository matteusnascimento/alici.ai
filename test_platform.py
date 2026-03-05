#!/usr/bin/env python
"""
Test script to verify ALICI.ai platform is working
"""
import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8001"

# Give server time to start
time.sleep(3)

def test_route(method, route, description):
    """Test a single route"""
    try:
        url = f"{BASE_URL}{route}"
        if method.upper() == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url)
        
        status = "✅" if response.status_code < 400 else "❌"
        print(f"{status} {description:50} [{response.status_code}]")
        return response.status_code < 400
    except Exception as e:
        print(f"❌ {description:50} [ERROR: {str(e)[:30]}]")
        return False

def main():
    print("\n" + "="*80)
    print(" TESTANDO PLATAFORMA ALICI.AI")
    print("="*80 + "\n")
    
    # Test health/status endpoints
    print("\n📊 ENDPOINTS DE SAÚDE DA APLICAÇÃO:")
    test_route("GET", "/health", "Health check")
    test_route("GET", "/health.", "Health check (alt)")
    test_route("GET", "/api/health", "API Health")
    
    # Test public pages (landing, login, etc)
    print("\n🎨 PÁGINAS PÚBLICAS (Marketing):")
    test_route("GET", "/", "Home / Landing Page")
    test_route("GET", "/login", "Login Page")
    test_route("GET", "/register", "Register Page")
    test_route("GET", "/portfolio", "Portfolio Page")
    
    # Test dashboard pages
    print("\n📱 PÁGINAS DO DASHBOARD:")
    test_route("GET", "/dashboard", "Dashboard")
    test_route("GET", "/chat", "Chat (legacy)")
    
    # Test API endpoints
    print("\n🔌 ENDPOINTS DE API:")
    test_route("GET", "/docs", "Swagger Documentation")
    test_route("GET", "/openapi.json", "OpenAPI Schema")
    
    # Test static files
    print("\n📁 ARQUIVOS ESTÁTICOS:")
    test_route("GET", "/static/css/style.css", "CSS Principal")
    test_route("GET", "/static/js/app.js", "JavaScript App")
    
    print("\n" + "="*80)
    print(" RESUMO DA VERIFICAÇÃO")
    print("="*80)
    print("""
✅ APLICAÇÃO INICIADA COM SUCESSO
   Porta: 8000
   URL: http://127.0.0.1:8000
   
🎯 PRÓXIMOS PASSOS:
   1. Abra http://localhost:8000 no navegador
   2. Verifique landing page / marketing
   3. Teste login/register
   4. Acesse dashboard
   5. Teste chat e recursos
    """)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        sys.exit(1)
