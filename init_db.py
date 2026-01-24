#!/usr/bin/env python3
"""
Script para inicializar o banco de dados no Neon
Cria a tabela 'memoria' necessária para a Alici
"""

import os
from dotenv import load_dotenv
from database import criar_tabelas

def main():
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ ERRO: DATABASE_URL não configurada em .env")
        print("\n📋 Configure assim:")
        print("   DATABASE_URL=postgresql://user:password@seu-host.neon.tech/alici?sslmode=require")
        return False
    
    print("🔌 Conectando ao Neon...")
    print(f"   {DATABASE_URL[:50]}...")
    
    try:
        criar_tabelas()
        print("✅ Banco de dados inicializado com sucesso!")
        print("✅ Tabela 'memoria' criada")
        print("✅ Índice 'idx_memoria_pergunta' criado")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
