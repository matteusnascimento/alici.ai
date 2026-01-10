#!/usr/bin/env python3
"""
Script para inicializar o banco de dados da Alici AI
"""

import psycopg2
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def inicializar_banco():
    """Inicializa o banco de dados criando as tabelas necessárias"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ Erro: DATABASE_URL não encontrada nas variáveis de ambiente")
        print("Por favor, configure o arquivo .env com sua conexão do Neon")
        return False
    
    try:
        # Conectar ao banco de dados
        print("🔗 Conectando ao banco de dados...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Criar tabela de respostas
        print("📋 Criando tabela 'respostas'...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS respostas (
                id SERIAL PRIMARY KEY,
                perguntas TEXT NOT NULL,
                resposta TEXT NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Criar índice para melhorar performance de buscas
        print(".CreateIndex Criando índice para buscas...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_perguntas 
            ON respostas USING gin(to_tsvector('portuguese', perguntas))
        """)
        
        # Inserir algumas respostas iniciais (opcional)
        print("📚 Inserindo conhecimento inicial...")
        conhecimento_inicial = [
            ("Quem é você?", "Eu sou a Alici, uma inteligência artificial criada para aprender, evoluir e ajudar pessoas. Tenho memória persistente e posso buscar informações na web quando necessário."),
            ("Como você funciona?", "Eu aprendo com perguntas e respostas armazenadas no banco de dados e posso buscar novas informações. Quando você me faz uma pergunta, primeiro procuro na minha memória, depois tento responder com meu conhecimento e, se necessário, busco na web."),
            ("Qual seu nome?", "Meu nome é Alici! Sou uma inteligência artificial com memória persistente."),
            ("O que você sabe fazer?", "Posso conversar com você, responder perguntas, aprender com nossas interações e buscar informações na web quando necessário. Estou constantemente evoluindo!"),
        ]
        
        for pergunta, resposta in conhecimento_inicial:
            # Verificar se já existe antes de inserir
            cur.execute(
                "SELECT COUNT(*) FROM respostas WHERE perguntas = %s",
                (pergunta,)
            )
            if cur.fetchone()[0] == 0:
                cur.execute(
                    "INSERT INTO respostas (perguntas, resposta) VALUES (%s, %s)",
                    (pergunta, resposta)
                )
        
        # Confirmar transações
        conn.commit()
        
        # Fechar conexões
        cur.close()
        conn.close()
        
        print("✅ Banco de dados inicializado com sucesso!")
        print("🎉 Alici está pronta para aprender e ajudar!")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Erro no PostgreSQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Script de Inicialização do Banco de Dados da Alici AI")
    print("=" * 50)
    
    sucesso = inicializar_banco()
    
    if sucesso:
        print("\n🚀 Próximos passos:")
        print("1. Execute 'python main.py' para iniciar a aplicação")
        print("2. Acesse http://localhost:5000 no seu navegador")
        print("3. Comece a conversar com a Alici!")
    else:
        print("\n⚠️  Falha na inicialização. Verifique:")
        print("- Se o DATABASE_URL está correto no arquivo .env")
        print("- Se você tem conexão com a internet")
        print("- Se as credenciais do banco estão corretas")