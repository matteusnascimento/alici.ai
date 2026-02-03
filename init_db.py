"""
init_db.py
Script para inicializar o banco de dados
Execute uma única vez no primeiro deploy
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """
    Criar tabelas de memória e autenticação
    """
    print("="*60)
    print("🗄️  Inicializando banco de dados...")
    print("="*60)
    
    try:
        # Importar funções de BD
        from database import criar_tabelas as criar_tabelas_memoria
        from database_auth import criar_tabelas as criar_tabelas_auth
        
        # Criar tabelas de memória
        print("\n📝 Criando tabela 'memoria'...")
        criar_tabelas_memoria()
        print("✓ Tabela 'memoria' pronta")
        
        # Criar tabelas de autenticação
        print("\n👤 Criando tabelas de autenticação...")
        criar_tabelas_auth()
        print("✓ Tabelas de autenticação prontas")
        
        print("\n" + "="*60)
        print("✓ BANCO DE DADOS INICIALIZADO COM SUCESSO!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERRO ao inicializar banco: {e}")
        print("Verifique:")
        print("  1. DATABASE_URL está configurada?")
        print("  2. Neon está acessível?")
        print("  3. Permissões do usuário PostgreSQL?")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
