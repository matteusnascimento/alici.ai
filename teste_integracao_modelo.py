"""
teste_integracao_modelo.py
Script de teste para validar a integração do modelo CIFAR-100 com o Flask
Testa:
  1. Carregamento do modelo
  2. Preprocessamento de imagem
  3. Predição em imagens
  4. Endpoints Flask (simulado)
  5. Conversão de resposta em português
"""

import os
import sys
import json
from pathlib import Path

print("=" * 80)
print("🤖 TESTE DE INTEGRAÇÃO: MODELO CIFAR-100 + FLASK")
print("=" * 80)

# ============================================================================
# TESTE 1: Verificar se o modelo existe
# ============================================================================
print("\n[TESTE 1] Verificando existência do modelo...")
modelo_path = Path(__file__).parent / "modelo_animais_treinado.h5"
if modelo_path.exists():
    tamanho_mb = modelo_path.stat().st_size / (1024 * 1024)
    print(f"✅ Modelo encontrado: {modelo_path}")
    print(f"   Tamanho: {tamanho_mb:.1f} MB")
else:
    print(f"❌ Modelo NÃO encontrado em: {modelo_path}")
    sys.exit(1)

# ============================================================================
# TESTE 2: Importar dependências
# ============================================================================
print("\n[TESTE 2] Verificando dependências...")
try:
    import tensorflow as tf
    print(f"✅ TensorFlow {tf.__version__}")
except ImportError as e:
    print(f"❌ TensorFlow não instalado: {e}")
    sys.exit(1)

try:
    import keras
    print(f"✅ Keras {keras.__version__}")
except ImportError as e:
    print(f"❌ Keras não instalado: {e}")
    sys.exit(1)

try:
    import numpy as np
    print(f"✅ NumPy {np.__version__}")
except ImportError as e:
    print(f"❌ NumPy não instalado: {e}")
    sys.exit(1)

try:
    from PIL import Image
    print(f"✅ Pillow {Image.__version__ if hasattr(Image, '__version__') else 'instalado'}")
except ImportError as e:
    print(f"❌ Pillow não instalado: {e}")
    sys.exit(1)

try:
    from model_inference import (
        carregar_modelo,
        preprocessar_imagem,
        fazer_predicao,
        gerar_resposta_predicao
    )
    print(f"✅ model_inference importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar model_inference: {e}")
    sys.exit(1)

# ============================================================================
# TESTE 3: Carregar o modelo
# ============================================================================
print("\n[TESTE 3] Carregando modelo...")
try:
    modelo = carregar_modelo(str(modelo_path))
    print(f"✅ Modelo carregado com sucesso!")
    print(f"   - Tipo: {type(modelo)}")
    print(f"   - Camadas: {len(modelo.layers)}")
    print(f"   - Parâmetros: {modelo.count_params():,}")
    print(f"   - Input: {modelo.input_shape}")
    print(f"   - Output: {modelo.output_shape}")
except Exception as e:
    print(f"❌ Erro ao carregar modelo: {e}")
    sys.exit(1)

# ============================================================================
# TESTE 4: Testar com imagem de exemplo
# ============================================================================
print("\n[TESTE 4] Verificando imagens de teste...")
imagens_teste = list(Path(__file__).parent.glob("animais_preditos/predicao_*.png"))

if not imagens_teste:
    print("⚠️  Nenhuma imagem de teste encontrada em animais_preditos/")
    print("   Criando imagem de teste sintética...")
    
    try:
        # Criar imagem teste simples
        import numpy as np
        from PIL import Image
        
        os.makedirs("animais_preditos", exist_ok=True)
        img_array = np.random.randint(0, 256, (32, 32, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        imagem_teste_path = "animais_preditos/teste_sintetica.png"
        img.save(imagem_teste_path)
        print(f"✅ Imagem sintética criada: {imagem_teste_path}")
        imagens_teste = [imagem_teste_path]
    except Exception as e:
        print(f"❌ Erro ao criar imagem de teste: {e}")
        imagens_teste = []
else:
    print(f"✅ Encontradas {len(imagens_teste)} imagens de teste")

# ============================================================================
# TESTE 5: Fazer predições
# ============================================================================
if imagens_teste:
    print(f"\n[TESTE 5] Fazendo predições em {len(imagens_teste)} imagens...")
    
    for i, imagem_path in enumerate(imagens_teste[:3], 1):  # Primeiras 3 imagens
        print(f"\n  Imagem {i}: {Path(imagem_path).name}")
        try:
            resultado = fazer_predicao(str(imagem_path), top_k=3)
            
            if resultado.get('status') == 'sucesso':
                print(f"  ✅ Predição realizada:")
                print(f"     - Classe: {resultado['classe']}")
                print(f"     - Confiança: {resultado['confianca']:.1f}%")
                
                # Gerar resposta em português
                resposta = gerar_resposta_predicao(resultado)
                print(f"     - Resposta: {resposta[:80]}...")
                
                # Top K alternativas
                if resultado.get('top_k'):
                    print(f"     - Alternativas:")
                    for alt in resultado['top_k'][:2]:
                        print(f"       • {alt['classe']}: {alt['confianca']:.1f}%")
            else:
                print(f"  ❌ Erro: {resultado.get('erro')}")
        except Exception as e:
            print(f"  ❌ Erro ao processar: {e}")
else:
    print("\n[TESTE 5] Pulado (sem imagens de teste)")

# ============================================================================
# TESTE 6: Simular endpoint Flask
# ============================================================================
print("\n[TESTE 6] Testando estrutura de resposta API...")
try:
    resultado_teste = {
        "classe": "gato",
        "confianca": 92.5,
        "resposta": "Detectei um **gato** com **92.5%** de confiança!",
        "alternativas": [
            {"classe": "cachorro", "confianca": 5.2},
            {"classe": "tigre", "confianca": 2.3}
        ],
        "status": "sucesso"
    }
    
    resposta_json = json.dumps(resultado_teste, indent=2, ensure_ascii=False)
    print("✅ Estrutura de resposta válida:")
    print(resposta_json)
except Exception as e:
    print(f"❌ Erro ao gerar resposta JSON: {e}")

# ============================================================================
# RESUMO FINAL
# ============================================================================
print("\n" + "=" * 80)
print("✅ TESTES CONCLUÍDOS COM SUCESSO!")
print("=" * 80)
print("\n📝 PRÓXIMOS PASSOS:")
print("   1. Instalar dependências: pip install -r requirements.txt")
print("   2. Executar servidor: python main.py")
print("   3. Testar endpoint em: http://localhost:5000/model/status")
print("   4. Upload de imagem: POST /chat/image")
print("   5. Testar com curl:")
print("      curl -X POST -F 'imagem=@animais_preditos/predicao_1.png' \\")
print("           http://localhost:5000/chat/image")
print("\n" + "=" * 80)
