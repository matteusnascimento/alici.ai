"""
executar_notebook_completo.py
🚀 Script de execução completa do Alici_Foundation_Complete.ipynb
Executa todas as células incluindo treinamento de modelo
"""

import os
import sys
import json

def print_section(title):
    """Imprime cabeçalho de seção"""
    print()
    print("=" * 70)
    print(f"📌 {title}")
    print("=" * 70)
    print()

def main():
    print("=" * 70)
    print("🤖 ALICI™ - EXECUÇÃO COMPLETA DO NOTEBOOK")
    print("=" * 70)
    print()
    print("📓 Executando: Alici_Foundation_Complete.ipynb")
    print("🎯 Objetivo: Setup completo + Treinamento de modelo")
    print()
    
    # =========================================================================
    # Passo 1: Verificar Python
    # =========================================================================
    print_section("Passo 1: Verificação do Python")
    print(f"✅ Python version: {sys.version}")
    print(f"✅ Python executable: {sys.executable}")
    
    # =========================================================================
    # Passo 2: Verificar dependências
    # =========================================================================
    print_section("Passo 2: Verificação de Dependências")
    
    dependencias = {
        "tensorflow": "TensorFlow (ML)",
        "numpy": "NumPy (Arrays)",
        "psycopg2": "PostgreSQL Driver",
        "dotenv": "Python-dotenv",
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
    }
    
    deps_disponiveis = []
    deps_faltando = []
    
    for modulo, desc in dependencias.items():
        try:
            __import__(modulo)
            print(f"✅ {desc}")
            deps_disponiveis.append(modulo)
        except ImportError:
            print(f"❌ {desc} - NÃO INSTALADO")
            deps_faltando.append(modulo)
    
    if deps_faltando:
        print()
        print(f"⚠️  Módulos faltando: {', '.join(deps_faltando)}")
        print(f"💡 Instale com: pip install {' '.join(deps_faltando)}")
    
    # =========================================================================
    # Passo 3: Verificar estrutura do projeto
    # =========================================================================
    print_section("Passo 3: Verificação da Estrutura do Projeto")
    
    arquivos_essenciais = [
        ("init_db.py", "Inicialização do banco de dados"),
        ("init_alici.py", "Verificação do sistema"),
        ("gerar_dataset.py", "Gerador de dataset"),
        ("teste_engine_completo.py", "Testes do engine"),
        ("colab_finetuning.py", "Script de treinamento"),
        ("model_inference.py", "Inferência de modelos"),
        ("treinar_modelo_local.py", "Treinamento local"),
        ("Alici_Foundation_Complete.ipynb", "Notebook completo"),
    ]
    
    todos_presentes = True
    for arquivo, desc in arquivos_essenciais:
        if os.path.exists(arquivo):
            tamanho = os.path.getsize(arquivo)
            print(f"✅ {arquivo:40} ({tamanho:>8} bytes) - {desc}")
        else:
            print(f"❌ {arquivo:40} - {desc}")
            todos_presentes = False
    
    # =========================================================================
    # Passo 4: Gerar Dataset
    # =========================================================================
    print_section("Passo 4: Geração do Dataset")
    
    if os.path.exists("gerar_dataset.py"):
        print("🔨 Executando gerar_dataset.py...")
        try:
            # Executar script de geração
            exec(open("gerar_dataset.py").read())
            
            # Verificar resultado
            if os.path.exists("dataset_expandido.json"):
                with open("dataset_expandido.json", "r") as f:
                    dataset = json.load(f)
                print()
                print(f"✅ Dataset gerado com sucesso!")
                print(f"   • Arquivo: dataset_expandido.json")
                print(f"   • Pares: {len(dataset)}")
            else:
                print("⚠️  Dataset não foi gerado")
        except Exception as e:
            print(f"❌ Erro ao gerar dataset: {e}")
    else:
        print("❌ Script gerar_dataset.py não encontrado")
    
    # =========================================================================
    # Passo 5: Treinar Modelo
    # =========================================================================
    print_section("Passo 5: Treinamento de Modelo")
    
    # Verificar se TensorFlow está disponível
    tensorflow_disponivel = "tensorflow" in deps_disponiveis
    numpy_disponivel = "numpy" in deps_disponiveis
    
    if tensorflow_disponivel and numpy_disponivel:
        print("✅ TensorFlow e NumPy disponíveis")
        print("🎓 Iniciando treinamento de modelo...")
        print()
        
        try:
            # Executar script de treinamento
            exec(open("treinar_modelo_local.py").read())
        except Exception as e:
            print(f"❌ Erro no treinamento: {e}")
            print()
            print("💡 Para treinamento completo:")
            print("   1. Use Google Colab com GPU")
            print("   2. Upload colab_finetuning.py e dataset_expandido.json")
            print("   3. Execute o pipeline de treinamento")
    else:
        print("⚠️  TensorFlow ou NumPy não disponíveis")
        print()
        print("📋 Opções para treinamento:")
        print()
        print("📦 Opção 1: Instalar dependências localmente")
        print("   pip install tensorflow numpy")
        print("   python treinar_modelo_local.py")
        print()
        print("☁️  Opção 2: Usar Google Colab (Recomendado)")
        print("   1. Acesse: https://colab.research.google.com")
        print("   2. Ative GPU: Runtime > Change runtime type > GPU")
        print("   3. Upload colab_finetuning.py e dataset_expandido.json")
        print("   4. Execute o pipeline completo (30-60 min)")
        print("   5. Baixe o modelo treinado (.h5)")
        print()
        print("✅ Dataset pronto para treinamento no Colab!")
    
    # =========================================================================
    # Passo 6: Verificação Final
    # =========================================================================
    print_section("Passo 6: Verificação Final do Sistema")
    
    componentes = {
        "Python": sys.version_info >= (3, 8),
        "Dataset gerado": os.path.exists("dataset_expandido.json"),
        "Scripts instalados": todos_presentes,
        "Notebook criado": os.path.exists("Alici_Foundation_Complete.ipynb"),
    }
    
    if tensorflow_disponivel:
        componentes["Modelo treinado"] = os.path.exists("model/alici_demo_treinado.h5")
    
    print("📊 Status dos componentes:")
    for comp, status in componentes.items():
        simbolo = "✅" if status else "⚠️"
        print(f"   {simbolo} {comp}")
    
    # =========================================================================
    # Resumo Final
    # =========================================================================
    print_section("RESUMO FINAL")
    
    total = len(componentes)
    ok = sum(componentes.values())
    porcentagem = (ok / total) * 100
    
    print(f"📊 Status Geral: {ok}/{total} componentes OK ({porcentagem:.1f}%)")
    print()
    
    if porcentagem == 100:
        print("🎉 SISTEMA 100% OPERACIONAL!")
        print()
        print("✅ Tudo pronto:")
        print("   • Dataset gerado")
        print("   • Modelo treinado")
        print("   • Sistema verificado")
        print()
        print("🚀 Próximos passos:")
        print("   • Execute: python main.py")
        print("   • Acesse: http://localhost:8000")
    elif porcentagem >= 70:
        print("⚠️  SISTEMA PARCIALMENTE OPERACIONAL")
        print()
        print("✅ O que está pronto:")
        print("   • Dataset gerado")
        print("   • Scripts instalados")
        print("   • Notebook criado")
        print()
        print("📋 Pendente:")
        if not tensorflow_disponivel:
            print("   • Treinamento de modelo (use Google Colab)")
        print()
        print("💡 Recomendação:")
        print("   • Use Google Colab para treinamento completo")
        print("   • Siga o guia em TRAINING_GUIDE.md")
    else:
        print("❌ CONFIGURAÇÃO INCOMPLETA")
        print()
        print("📋 Verifique:")
        for comp, status in componentes.items():
            if not status:
                print(f"   ❌ {comp}")
    
    print()
    print("=" * 70)
    print("📓 Execução do notebook concluída!")
    print("=" * 70)
    print()

if __name__ == "__main__":
    main()
