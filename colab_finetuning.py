#!/usr/bin/env python3
"""
colab_finetuning.py - Script de Fine-tuning para Google Colab
Treina modelo de IA usando o dataset expandido
Este script deve ser executado no Google Colab com GPU
"""

print("=" * 70)
print("🧠 ALICI™ - FINE-TUNING DE MODELO")
print("=" * 70)
print("\n⚠️  IMPORTANTE: Este script deve ser executado no Google Colab")
print("   com GPU ativada para melhor performance.\n")

import json
import numpy as np
import sys

# Verificar se TensorFlow está disponível
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    print(f"✅ TensorFlow {tf.__version__} instalado")
except ImportError:
    print("❌ TensorFlow não encontrado")
    print("   No Colab, execute: !pip install tensorflow")
    sys.exit(1)

# Verificar GPU
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f"✅ GPU disponível: {len(gpus)} device(s)")
    for gpu in gpus:
        print(f"   • {gpu}")
else:
    print("⚠️  Nenhuma GPU detectada - usando CPU (mais lento)")

print("\n" + "=" * 70)
print("📊 CARREGANDO DATASET")
print("=" * 70)

# Carregar dataset
try:
    with open('dataset_expandido.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    pares = dataset.get("pares_qa", [])
    print(f"✅ Dataset carregado: {len(pares)} pares")
    
except FileNotFoundError:
    print("❌ Arquivo dataset_expandido.json não encontrado")
    print("\n💡 No Colab:")
    print("   1. Faça upload do dataset_expandido.json")
    print("   2. Execute novamente este script")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao carregar dataset: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("🏗️  CONSTRUINDO MODELO")
print("=" * 70)

# Preparar dados de treino (exemplo simplificado)
# Na prática, você precisaria de embeddings adequados
print("\n📝 Criando modelo de exemplo (CNN para imagens CIFAR-100)...")

# Modelo exemplo: CNN simples para classificação de animais
# Este é um exemplo - adapte conforme sua necessidade
modelo = keras.Sequential([
    # Camada de entrada para imagens 32x32x3 (CIFAR-100)
    layers.Input(shape=(32, 32, 3)),
    
    # Bloco convolucional 1
    layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
    layers.BatchNormalization(),
    layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
    layers.MaxPooling2D((2, 2)),
    layers.Dropout(0.2),
    
    # Bloco convolucional 2
    layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
    layers.BatchNormalization(),
    layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
    layers.MaxPooling2D((2, 2)),
    layers.Dropout(0.3),
    
    # Bloco convolucional 3
    layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
    layers.BatchNormalization(),
    layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
    layers.MaxPooling2D((2, 2)),
    layers.Dropout(0.4),
    
    # Camadas densas
    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.5),
    layers.Dense(20, activation='softmax')  # 20 classes de animais CIFAR-100
])

print("✅ Modelo criado")

# Compilar modelo
print("\n🔧 Compilando modelo...")
modelo.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

print("✅ Modelo compilado")

# Mostrar arquitetura
print("\n📋 Arquitetura do modelo:")
modelo.summary()

print("\n" + "=" * 70)
print("💡 INSTRUÇÕES DE TREINAMENTO")
print("=" * 70)

print("""
Para treinar o modelo no Google Colab:

1. PREPARAR DADOS:
   # Carregar CIFAR-100 ou seu dataset
   from tensorflow.keras.datasets import cifar100
   (x_train, y_train), (x_test, y_test) = cifar100.load_data(label_mode='fine')
   
   # Normalizar
   x_train = x_train.astype('float32') / 255.0
   x_test = x_test.astype('float32') / 255.0
   
   # Filtrar apenas animais (classes 0-19 do CIFAR-100)
   animais_mask_train = y_train.flatten() < 20
   animais_mask_test = y_test.flatten() < 20
   
   x_train_animais = x_train[animais_mask_train]
   y_train_animais = y_train[animais_mask_train]
   x_test_animais = x_test[animais_mask_test]
   y_test_animais = y_test[animais_mask_test]

2. TREINAR:
   history = modelo.fit(
       x_train_animais, y_train_animais,
       epochs=50,
       batch_size=64,
       validation_data=(x_test_animais, y_test_animais),
       callbacks=[
           keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
           keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=3)
       ]
   )

3. SALVAR:
   modelo.save('modelo_animais_treinado.h5')
   print("✅ Modelo salvo!")

4. BAIXAR:
   from google.colab import files
   files.download('modelo_animais_treinado.h5')

5. USAR NA ALICI:
   # Coloque o arquivo .h5 na pasta model/
   # O engine.py vai carregá-lo automaticamente
""")

print("\n" + "=" * 70)
print("🎯 PRONTO PARA TREINAR")
print("=" * 70)

print("""
✅ O modelo está pronto para treinamento!

Execute as instruções acima no Google Colab para:
• Treinar o modelo com GPU (30-60 minutos)
• Salvar o arquivo .h5
• Baixar e integrar na ALICI

💡 Dicas:
• Use GPU do Colab (Runtime > Change runtime type > GPU)
• Monitore overfitting com EarlyStopping
• Ajuste hiperparâmetros conforme necessário
• Teste o modelo com teste_modelo.py após baixar
""")

print("\n" + "=" * 70)
