#!/usr/bin/env python3
"""
Script para inicializar o banco de dados da Alici AI
"""

from database import inicializar_banco

if __name__ == "__main__":
    print("🔧 Inicializando banco de dados da Alici AI...")
    print("=" * 50)
    
    sucesso = inicializar_banco()
    
    if sucesso:
        print("\n🎉 Banco de dados configurado com sucesso!")
        print("✅ Alici AI está pronta para aprender e armazenar conhecimento!")
    else:
        print("\n❌ Falha na inicialização do banco de dados.")
        print("Por favor, verifique as credenciais e conexão com o banco.")