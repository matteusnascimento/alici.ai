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
        from database import criar_tabelas
        
        # Criar tabelas
        print("\n📝 Criando tabelas 'memoria', 'users', 'history'...")
        criar_tabelas()
        print("✓ Tabelas prontas")
        
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
