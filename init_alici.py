"""
init_alici.py
🔍 Verificador completo do sistema ALICI™
Testa todos os componentes e reporta o status
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def verificar_arquivo(caminho, descricao):
    """Verifica se um arquivo existe"""
    existe = os.path.exists(caminho)
    simbolo = "✅" if existe else "❌"
    print(f"  {simbolo} {descricao}: {caminho}")
    return existe

def verificar_modulo(nome_modulo, descricao):
    """Verifica se um módulo Python pode ser importado"""
    try:
        __import__(nome_modulo)
        print(f"  ✅ {descricao}")
        return True
    except ImportError as e:
        print(f"  ❌ {descricao}: {e}")
        return False

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    print("\n📦 Verificando dependências Python...")
    
    deps = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("psycopg2", "PostgreSQL driver"),
        ("tensorflow", "TensorFlow"),
        ("requests", "Requests"),
        ("dotenv", "Python-dotenv"),
        ("jose", "Python-JOSE (JWT)"),
        ("passlib", "Passlib (hashing)"),
    ]
    
    resultados = []
    for modulo, desc in deps:
        resultados.append(verificar_modulo(modulo, desc))
    
    return all(resultados)

def verificar_arquivos_core():
    """Verifica arquivos essenciais do projeto"""
    print("\n📁 Verificando arquivos essenciais...")
    
    arquivos = [
        ("main.py", "FastAPI wrapper"),
        ("main_auth.py", "Main application"),
        ("engine.py", "Decision engine"),
        ("database.py", "Database module"),
        ("database_auth.py", "Auth database module"),
        ("identidade.py", "Identity module"),
        ("resposta.py", "Response patterns"),
        ("intencao.py", "Intent detection"),
        ("web_search.py", "Web search"),
        ("auth.py", "Authentication"),
        ("sistema_emocoes.py", "Emotion system"),
        (".env", "Environment config"),
        ("requirements.txt", "Dependencies list"),
    ]
    
    resultados = []
    for arquivo, desc in arquivos:
        resultados.append(verificar_arquivo(arquivo, desc))
    
    return all(resultados)

def verificar_configuracao():
    """Verifica variáveis de ambiente"""
    print("\n⚙️  Verificando configuração (.env)...")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if DATABASE_URL:
        # Ocultar senha na exibição
        url_safe = DATABASE_URL[:30] + "..." if len(DATABASE_URL) > 30 else DATABASE_URL
        print(f"  ✅ DATABASE_URL configurada: {url_safe}")
        return True
    else:
        print(f"  ❌ DATABASE_URL não encontrada")
        print(f"     Configure no arquivo .env")
        return False

def verificar_banco_dados():
    """Verifica conexão com o banco de dados"""
    print("\n🗄️  Verificando banco de dados...")
    
    try:
        from database import conectar
        
        conn = conectar()
        if conn:
            print("  ✅ Conexão com banco estabelecida")
            
            # Verificar tabelas
            cur = conn.cursor()
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tabelas = cur.fetchall()
            
            tabelas_esperadas = ["memoria", "usuarios", "historico"]
            tabelas_encontradas = [t[0] for t in tabelas]
            
            for tabela in tabelas_esperadas:
                if tabela in tabelas_encontradas:
                    print(f"  ✅ Tabela '{tabela}' existe")
                else:
                    print(f"  ❌ Tabela '{tabela}' não encontrada")
                    print(f"     Execute: python init_db.py")
            
            cur.close()
            conn.close()
            
            return all(t in tabelas_encontradas for t in tabelas_esperadas)
        else:
            print("  ❌ Falha ao conectar ao banco")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro ao verificar banco: {e}")
        return False

def verificar_engine():
    """Verifica se o engine está funcionando"""
    print("\n🧠 Verificando engine de IA...")
    
    try:
        from engine import gerar_resposta
        
        # Teste simples
        resposta = gerar_resposta("teste")
        
        if resposta:
            print("  ✅ Engine respondendo")
            return True
        else:
            print("  ❌ Engine não gerou resposta")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro no engine: {e}")
        return False

def verificar_modelos():
    """Verifica se os modelos neurais estão disponíveis"""
    print("\n🤖 Verificando modelos de ML...")
    
    modelos = [
        "modelo_animais.h5",
        "model/modelo_animais_cifar100.h5",
        "model/modelo_animais_treinado.h5",
    ]
    
    encontrados = 0
    for modelo in modelos:
        if os.path.exists(modelo):
            print(f"  ✅ Modelo encontrado: {modelo}")
            encontrados += 1
        else:
            print(f"  ⚠️  Modelo não encontrado: {modelo}")
    
    if encontrados > 0:
        print(f"  ℹ️  {encontrados}/{len(modelos)} modelos disponíveis")
        return True
    else:
        print("  ⚠️  Nenhum modelo encontrado (opcional)")
        return False

def verificar_templates():
    """Verifica se os templates HTML existem"""
    print("\n🎨 Verificando templates...")
    
    templates = [
        ("templates/login.html", "Login page"),
        ("templates/index.html", "Chat interface"),
    ]
    
    resultados = []
    for template, desc in templates:
        resultados.append(verificar_arquivo(template, desc))
    
    return any(resultados)  # Pelo menos um template deve existir

def main():
    """Executa todas as verificações"""
    print("=" * 70)
    print("🤖 ALICI™ - Verificação Completa do Sistema")
    print("=" * 70)
    
    resultados = {
        "Dependências": verificar_dependencias(),
        "Arquivos Core": verificar_arquivos_core(),
        "Configuração": verificar_configuracao(),
        "Banco de Dados": verificar_banco_dados(),
        "Engine IA": verificar_engine(),
        "Modelos ML": verificar_modelos(),
        "Templates": verificar_templates(),
    }
    
    print("\n" + "=" * 70)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("=" * 70)
    
    for componente, status in resultados.items():
        simbolo = "✅" if status else "❌"
        print(f"{simbolo} {componente}")
    
    print()
    
    # Status geral
    total = len(resultados)
    aprovados = sum(resultados.values())
    porcentagem = (aprovados / total) * 100
    
    print(f"Status Geral: {aprovados}/{total} componentes OK ({porcentagem:.1f}%)")
    
    if porcentagem == 100:
        print("\n🎉 Sistema 100% operacional!")
        print("\nPróximos passos:")
        print("  1. python main.py")
        print("  2. Acesse http://localhost:8000")
        return 0
    elif porcentagem >= 70:
        print("\n⚠️  Sistema parcialmente operacional")
        print("Alguns componentes opcionais estão faltando")
        return 0
    else:
        print("\n❌ Sistema não está pronto")
        print("Corrija os erros acima antes de continuar")
        return 1

if __name__ == "__main__":
    sys.exit(main())
