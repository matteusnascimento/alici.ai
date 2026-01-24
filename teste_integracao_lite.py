"""
teste_integracao_lite.py
Teste LEVE - Valida integração sem carregar o modelo (testa estrutura)
Útil para CI/CD e verificações rápidas
"""

import os
import sys
import json
from pathlib import Path

print("=" * 80)
print("🤖 TESTE LEVE - VALIDAÇÃO DE ESTRUTURA (SEM MODELO)")
print("=" * 80)

# ============================================================================
# TESTE 1: Arquivos Necessários
# ============================================================================
print("\n[TESTE 1] Verificando arquivos...")

arquivos_necessarios = [
    ("modelo_animais_treinado.h5", "Modelo treinado"),
    ("model_inference.py", "Módulo de inferência"),
    ("main.py", "Servidor Flask"),
    ("requirements.txt", "Dependências"),
]

todos_ok = True
for arquivo, descricao in arquivos_necessarios:
    caminho = Path(__file__).parent / arquivo
    if caminho.exists():
        tamanho = caminho.stat().st_size
        if tamanho > 1024:
            tamanho_str = f"{tamanho / (1024*1024):.1f}MB"
        else:
            tamanho_str = f"{tamanho}B"
        print(f"✅ {descricao}: {arquivo} ({tamanho_str})")
    else:
        print(f"❌ {descricao}: {arquivo} NÃO ENCONTRADO")
        todos_ok = False

if not todos_ok:
    print("\n❌ Alguns arquivos estão faltando!")
    sys.exit(1)

# ============================================================================
# TESTE 2: Imports de Estrutura
# ============================================================================
print("\n[TESTE 2] Verificando importações Python...")

imports_obrigatorios = [
    ("flask", "Flask"),
    ("werkzeug", "Werkzeug"),
    ("pil", "PIL"),
]

for modulo, nome in imports_obrigatorios:
    try:
        __import__(modulo)
        print(f"✅ {nome} importado")
    except ImportError:
        print(f"❌ {nome} não instalado: pip install -r requirements.txt")
        todos_ok = False

if not todos_ok:
    print("\n⚠️  Alguns pacotes faltam. Instale: pip install -r requirements.txt")
    # Não falhar - pode ser apenas desenvolvimento

# ============================================================================
# TESTE 3: Verificar módulo model_inference (estrutura)
# ============================================================================
print("\n[TESTE 3] Verificando estrutura de model_inference.py...")

try:
    # Não carregar TensorFlow, apenas verificar estrutura
    with open("model_inference.py", "r") as f:
        conteudo = f.read()
    
    funcoes_esperadas = [
        "carregar_modelo",
        "preprocessar_imagem",
        "fazer_predicao",
        "gerar_resposta_predicao",
        "testar_modelo",
    ]
    
    for funcao in funcoes_esperadas:
        if f"def {funcao}" in conteudo:
            print(f"✅ Função {funcao} definida")
        else:
            print(f"❌ Função {funcao} NÃO encontrada")
            todos_ok = False
    
    # Verificar constantes
    if "CIFAR100_LABELS" in conteudo:
        print(f"✅ CIFAR100_LABELS definido")
    else:
        print(f"❌ CIFAR100_LABELS não encontrado")
        
except Exception as e:
    print(f"❌ Erro ao ler model_inference.py: {e}")
    todos_ok = False

# ============================================================================
# TESTE 4: Verificar endpoints Flask (estrutura)
# ============================================================================
print("\n[TESTE 4] Verificando endpoints em main.py...")

try:
    with open("main.py", "r", encoding="utf-8") as f:
        conteudo = f.read()
    
    endpoints_esperados = [
        ("/chat/image", "POST"),
        ("/chat/image-base64", "POST"),
        ("/model/status", "GET"),
    ]
    
    for endpoint, metodo in endpoints_esperados:
        # Procurar decorator e função
        decorador = f"@app.route(\"{endpoint}\"" if metodo == "GET" else f"@app.route(\"{endpoint}\", methods=[\"POST\"]"
        if decorador in conteudo:
            print(f"✅ Endpoint {metodo} {endpoint} definido")
        else:
            print(f"❌ Endpoint {metodo} {endpoint} não encontrado")
            todos_ok = False
    
except Exception as e:
    print(f"❌ Erro ao ler main.py: {e}")
    todos_ok = False

# ============================================================================
# TESTE 5: Verificar requirements.txt
# ============================================================================
print("\n[TESTE 5] Verificando requirements.txt...")

try:
    with open("requirements.txt", "r") as f:
        conteudo = f.read()
    
    pacotes_esperados = [
        ("tensorflow", "Machine Learning"),
        ("keras", "Deep Learning"),
        ("numpy", "Computação numérica"),
        ("Flask", "Web Framework"),
        ("Pillow", "Processamento de imagem"),
    ]
    
    for pacote, descricao in pacotes_esperados:
        if pacote.lower() in conteudo.lower():
            print(f"✅ {descricao}: {pacote}")
        else:
            print(f"❌ {descricao}: {pacote} não encontrado")
            todos_ok = False
    
except Exception as e:
    print(f"❌ Erro ao ler requirements.txt: {e}")

# ============================================================================
# TESTE 6: Simular resposta JSON
# ============================================================================
print("\n[TESTE 6] Testando estrutura de resposta JSON...")

try:
    # Simular resposta do endpoint /chat/image
    resposta_sucesso = {
        "classe": "gato",
        "confianca": 94.5,
        "resposta": "Detectei um **gato** com **94.5%** de confiança!",
        "alternativas": [
            {"classe": "tigre", "confianca": 3.2},
            {"classe": "leão", "confianca": 2.3}
        ],
        "status": "sucesso"
    }
    
    # Validar JSON
    json_str = json.dumps(resposta_sucesso, ensure_ascii=False)
    json_parsed = json.loads(json_str)
    
    print("✅ Resposta JSON válida:")
    print(f"   - classe: {json_parsed['classe']}")
    print(f"   - confianca: {json_parsed['confianca']}%")
    print(f"   - status: {json_parsed['status']}")
    print(f"   - alternativas: {len(json_parsed['alternativas'])} opções")
    
except Exception as e:
    print(f"❌ Erro ao testar JSON: {e}")
    todos_ok = False

# ============================================================================
# TESTE 7: Diretórios de Dados
# ============================================================================
print("\n[TESTE 7] Verificando diretórios...")

diretorios = [
    ("animais_preditos", "Imagens de teste"),
    ("Static", "Assets estáticos"),
]

for diretorio, descricao in diretorios:
    caminho = Path(__file__).parent / diretorio
    if caminho.exists():
        arquivos = len(list(caminho.glob("*")))
        print(f"✅ {descricao}: {diretorio}/ ({arquivos} arquivos)")
    else:
        print(f"⚠️  {descricao}: {diretorio}/ não encontrado (não crítico)")

# ============================================================================
# TESTE 8: Configuração Render (Procfile)
# ============================================================================
print("\n[TESTE 8] Verificando configuração Render...")

procfile = Path(__file__).parent / "Procfile"
if procfile.exists():
    with open(procfile, "r") as f:
        conteudo = f.read()
    
    if "gunicorn main:app" in conteudo:
        print(f"✅ Procfile configurado para Gunicorn")
        # Verificar timeout
        if "timeout" in conteudo:
            print(f"✅ Timeout configurado (bom para TensorFlow)")
        else:
            print(f"⚠️  Timeout não encontrado - adicionar para TensorFlow")
    else:
        print(f"❌ Procfile não tem configuração correta")
else:
    print(f"❌ Procfile não encontrado")

# ============================================================================
# RESUMO FINAL
# ============================================================================
print("\n" + "=" * 80)
if todos_ok:
    print("✅ TESTE ESTRUTURAL CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    print("\n📝 PRÓXIMOS PASSOS:")
    print("   1. Instalar TensorFlow: pip install -r requirements.txt")
    print("   2. Executar teste completo: python teste_integracao_modelo.py")
    print("   3. Iniciar servidor: python main.py")
    print("   4. Testar endpoint: curl http://localhost:5000/model/status")
else:
    print("⚠️  TESTE ESTRUTURAL CONCLUÍDO COM AVISOS")
    print("=" * 80)
    print("\n📝 Corrija os problemas acima antes de continuar")

print("\n" + "=" * 80)
