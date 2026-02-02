#!/usr/bin/env python3
"""
init_db.py - Inicialização do Banco de Dados PostgreSQL/Neon
Script para criar tabelas e índices necessários para a ALICI™
"""

import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Verificar se DATABASE_URL está configurado
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ ERRO: DATABASE_URL não configurado no .env")
    print("\n📝 Configure DATABASE_URL no arquivo .env:")
    print("   DATABASE_URL=postgresql://user:password@host.neon.tech/alici?sslmode=require")
    sys.exit(1)

print("🚀 Iniciando configuração do banco de dados...")
print(f"📍 Conectando ao: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'PostgreSQL'}")

try:
    from database import criar_tabelas
    
    print("\n🔧 Criando tabelas e índices...")
    criar_tabelas()
    
    print("\n✅ Banco de dados inicializado com sucesso!")
    print("\n📊 Estrutura criada:")
    print("   ✓ Tabela 'memoria' (id, pergunta, resposta, confianca, criado_em)")
    print("   ✓ Índice 'idx_memoria_pergunta' para buscas rápidas")
    
    print("\n🎯 Próximos passos:")
    print("   1. Execute: python main.py")
    print("   2. Acesse: http://localhost:8000")
    print("   3. Comece a conversar com a ALICI!")
    
except Exception as e:
    print(f"\n❌ ERRO ao criar tabelas: {e}")
    print("\n🔍 Verifique:")
    print("   • DATABASE_URL está correto no .env")
    print("   • Você tem permissões no banco de dados Neon")
    print("   • A conexão de internet está funcionando")
    sys.exit(1)
