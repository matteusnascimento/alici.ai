#!/usr/bin/env python3
"""
Script de teste para verificar conexão com banco de dados
"""

import os
from database import criar_tabelas, aprender, buscar_memoria, DATABASE_ENABLED, USE_SQLITE, USE_POSTGRES

def test_database():
    print("=" * 60)
    print("🧪 TESTE DE BANCO DE DADOS ALICI")
    print("=" * 60)
    
    print(f"\n📊 Status:")
    print(f"   Banco habilitado: {DATABASE_ENABLED}")
    
    if DATABASE_ENABLED:
        if USE_SQLITE:
            print(f"   Tipo: SQLite ✅")
        elif USE_POSTGRES:
            print(f"   Tipo: PostgreSQL ✅")
    else:
        print(f"   ⚠️  Banco não configurado")
        return



    print(f"\n🔧 Criando tabelas...")
    criar_tabelas()
    print(f"   ✅ Tabelas criadas")
    
    print(f"\n📝 Testando aprendizado...")
    aprender("teste python", "Python é uma linguagem de programação")
    print(f"   ✅ Registro salvo")
    
    print(f"\n🔍 Testando busca...")
    resultado = buscar_memoria("teste python")
    if resultado:
        print(f"   ✅ Encontrado: {resultado}")
    else:
        print(f"   ❌ Não encontrado")
    
    print(f"\n{'=' * 60}")
    print(f"✅ TESTE COMPLETO!")
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    test_database()
