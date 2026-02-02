#!/usr/bin/env python3
"""
teste_modelo.py - Teste dos Modelos de Machine Learning
Testa os modelos .h5 de animais CIFAR-100
"""

import os
import sys
import numpy as np

print("=" * 70)
print("🧠 TESTE DOS MODELOS DE MACHINE LEARNING")
print("=" * 70)

# Verificar se TensorFlow está instalado
try:
    import tensorflow as tf
    print(f"\n✅ TensorFlow {tf.__version__} instalado")
except ImportError:
    print("\n❌ TensorFlow não está instalado")
    print("   Execute: pip install tensorflow==2.18.0")
    sys.exit(1)

# Lista de modelos para testar
modelos_paths = [
    "modelo_animais.h5",
    "model/modelo_animais_cifar100.h5",
    "model/modelo_animais_treinado.h5",
]

modelos_carregados = []

print("\n" + "=" * 70)
print("📦 CARREGANDO MODELOS")
print("=" * 70)

for path in modelos_paths:
    print(f"\n📝 Tentando carregar: {path}")
    
    if not os.path.exists(path):
        print(f"   ⚠️  Arquivo não encontrado")
        continue
    
    try:
        modelo = tf.keras.models.load_model(path)
        print(f"   ✅ Carregado com sucesso")
        
        # Informações do modelo
        print(f"   📊 Input shape: {modelo.input_shape}")
        print(f"   📊 Output shape: {modelo.output_shape}")
        
        # Contar parâmetros
        total_params = modelo.count_params()
        print(f"   📊 Total de parâmetros: {total_params:,}")
        
        modelos_carregados.append({
            'path': path,
            'modelo': modelo,
            'params': total_params
        })
        
    except Exception as e:
        print(f"   ❌ Erro ao carregar: {e}")

# Verificar se algum modelo foi carregado
if not modelos_carregados:
    print("\n" + "=" * 70)
    print("⚠️  NENHUM MODELO ENCONTRADO")
    print("=" * 70)
    print("\n💡 Os modelos são opcionais. ALICI funciona sem eles.")
    print("\n📝 Para treinar modelos:")
    print("   1. Execute: python gerar_dataset.py")
    print("   2. Treine no Google Colab com colab_finetuning.py")
    print("   3. Coloque os arquivos .h5 na pasta model/")
    sys.exit(0)

# Testar inferência
print("\n" + "=" * 70)
print("🔬 TESTANDO INFERÊNCIA")
print("=" * 70)

for info in modelos_carregados:
    print(f"\n📝 Testando: {info['path']}")
    
    try:
        # Criar entrada dummy (imagem 224x224x3)
        entrada = np.random.rand(1, 224, 224, 3).astype(np.float32)
        
        # Fazer predição
        predicao = info['modelo'].predict(entrada, verbose=0)
        
        print(f"   ✅ Inferência realizada")
        print(f"   📊 Shape da predição: {predicao.shape}")
        print(f"   📊 Maior confiança: {np.max(predicao):.4f}")
        print(f"   📊 Classe predita: {np.argmax(predicao)}")
        
    except Exception as e:
        print(f"   ❌ Erro na inferência: {e}")

# Resumo
print("\n" + "=" * 70)
print("📊 RESUMO")
print("=" * 70)

print(f"\n✅ Modelos carregados: {len(modelos_carregados)}/{len(modelos_paths)}")

if modelos_carregados:
    print("\n🎯 Modelos operacionais:")
    for info in modelos_carregados:
        print(f"   • {info['path']} ({info['params']:,} parâmetros)")
    
    print("\n✅ Os modelos estão prontos para uso!")
    print("\n💡 Integração:")
    print("   • Os modelos são usados automaticamente pelo engine.py")
    print("   • Camada 4 do pipeline de decisão")
    print("   • Fallback gracioso se não houver resposta confiante")
else:
    print("\n⚠️  Nenhum modelo operacional")

print("\n" + "=" * 70)
