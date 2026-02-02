"""
init_db.py
🗄️ Script de inicialização do banco de dados PostgreSQL/Neon
Cria todas as tabelas necessárias para ALICI funcionar
"""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def criar_tabelas():
    """
    Cria todas as tabelas necessárias no banco de dados
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ Erro: DATABASE_URL não encontrada no .env")
        print("Configure a variável DATABASE_URL com a connection string do Neon")
        return False
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("🔗 Conectado ao banco de dados...")
        
        # Tabela de memória (sistema de aprendizado)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS memoria (
                id SERIAL PRIMARY KEY,
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL,
                confianca INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabela 'memoria' criada/verificada")
        
        # Índice para busca rápida
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_memoria_pergunta 
            ON memoria (pergunta)
        """)
        print("✅ Índice 'idx_memoria_pergunta' criado/verificado")
        
        # Tabela de usuários (autenticação)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                senha_hash VARCHAR(255) NOT NULL,
                plano VARCHAR(50) DEFAULT 'free',
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabela 'usuarios' criada/verificada")
        
        # Tabela de histórico de conversas
        cur.execute("""
            CREATE TABLE IF NOT EXISTS historico (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                pergunta TEXT NOT NULL,
                resposta TEXT NOT NULL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabela 'historico' criada/verificada")
        
        # Índice para busca por usuário
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_historico_usuario 
            ON historico (usuario_id, criado_em DESC)
        """)
        print("✅ Índice 'idx_historico_usuario' criado/verificado")
        
        # Commit das alterações
        conn.commit()
        
        print("\n🎉 Banco de dados inicializado com sucesso!")
        print("\nTabelas criadas:")
        print("  • memoria - Armazena aprendizado da ALICI")
        print("  • usuarios - Gerenciamento de usuários")
        print("  • historico - Histórico de conversas")
        
        # Fechar conexões
        cur.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


def verificar_conexao():
    """
    Verifica se a conexão com o banco está funcionando
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL não configurada")
        return False
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Testar query simples
        cur.execute("SELECT version();")
        version = cur.fetchone()
        
        print(f"✅ Conexão estabelecida com sucesso!")
        print(f"PostgreSQL version: {version[0]}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 ALICI™ - Inicialização do Banco de Dados")
    print("=" * 60)
    print()
    
    # Verificar conexão
    print("📡 Verificando conexão...")
    if not verificar_conexao():
        print("\n⚠️  Não foi possível conectar ao banco de dados")
        print("Verifique se DATABASE_URL está correta no arquivo .env")
        exit(1)
    
    print()
    
    # Criar tabelas
    print("🔨 Criando/verificando tabelas...")
    if criar_tabelas():
        print("\n✅ Inicialização concluída com sucesso!")
        print("\nPróximos passos:")
        print("  1. Execute: python main.py")
        print("  2. Acesse: http://localhost:8000")
        print("  3. Faça login ou registre-se")
    else:
        print("\n❌ Falha na inicialização")
        exit(1)
