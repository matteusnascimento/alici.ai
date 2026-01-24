#!/usr/bin/env python3
"""
🚀 SCRIPT DE FINE-TUNING EM GOOGLE COLAB
ALICI™ - Continua treinamento com dataset expandido

⚠️ INSTRUÇÕES PARA COLAB:
1. Copie este script para uma célula do Colab
2. Faça upload do arquivo 'dataset_expandido.json'
3. Faça upload do modelo 'modelo_animais_cifar100.h5' (ou 'alici_blindado.h5')
4. Execute a célula
5. Baixe 'alici_treinado_v3.h5'

Criador: Mateus Nascimento dos Santos
"""

import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# ============================================================================
# 1️⃣ CARREGAR DATASET
# ============================================================================

def carregar_dataset(arquivo_json="dataset_expandido.json"):
    """Carrega dataset JSON gerado"""
    print("📚 Carregando dataset...")
    
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    perguntas = data['perguntas']
    respostas = data['respostas']
    
    print(f"✅ Dataset carregado: {len(perguntas)} pares Q&A")
    return perguntas, respostas

# ============================================================================
# 2️⃣ PRÉ-PROCESSAR DADOS
# ============================================================================

def preprocessar_dados(perguntas, respostas, vocab_size=15000, max_len=40):
    """
    Tokeniza e prepara dados para treinamento
    Mantém compatibilidade com modelo original
    """
    print("\n🔧 Pré-processando dados...")
    
    # Tokenizer
    tokenizer = Tokenizer(num_words=vocab_size, oov_token="<OOV>")
    tokenizer.fit_on_texts(perguntas + respostas)
    
    # Converter para sequências
    X = tokenizer.texts_to_sequences(perguntas)
    Y = tokenizer.texts_to_sequences(respostas)
    
    # Padding
    X = pad_sequences(X, maxlen=max_len, padding="post")
    Y = pad_sequences(Y, maxlen=max_len, padding="post")
    
    # Converter Y para labels (primeiro token da resposta)
    Y_labels = Y[:, 0]
    
    print(f"✅ Dados processados:")
    print(f"   X shape: {X.shape}")
    print(f"   Y shape: {Y_labels.shape}")
    
    return X, Y_labels, tokenizer

# ============================================================================
# 3️⃣ CARREGAR MODELO EXISTENTE
# ============================================================================

def carregar_modelo_existente(modelo_path="modelo_animais_cifar100.h5"):
    """
    Carrega modelo treinado anteriormente
    Mantém todos os pesos e aprendizado anterior
    """
    print("\n🧠 Carregando modelo existente...")
    
    try:
        model = tf.keras.models.load_model(modelo_path)
        print(f"✅ Modelo carregado: {modelo_path}")
        print(f"   Total parâmetros: {model.count_params():,}")
        return model
    except Exception as e:
        print(f"❌ Erro ao carregar: {e}")
        print("⚠️ Será criado modelo novo")
        return None

# ============================================================================
# 4️⃣ COMPILAR PARA FINE-TUNING
# ============================================================================

def compilar_modelo(model, learning_rate=1e-4):
    """
    Compila modelo com learning rate BAIXO
    (essencial para não apagar aprendizado anterior)
    """
    print("\n⚙️ Compilando modelo para fine-tuning...")
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    
    print(f"✅ Modelo compilado com learning_rate={learning_rate}")
    return model

# ============================================================================
# 5️⃣ TREINAR (FINE-TUNING)
# ============================================================================

def treinar_modelo(model, X, Y, epochs=20, batch_size=16):
    """
    Continua treinamento com dados novos
    """
    print("\n🏋️ Iniciando fine-tuning...")
    print(f"   Epochs: {epochs}")
    print(f"   Batch size: {batch_size}")
    print(f"   Samples: {len(X)}")
    print()
    
    history = model.fit(
        X,
        Y,
        epochs=epochs,
        batch_size=batch_size,
        shuffle=True,
        verbose=1,
        validation_split=0.1  # 10% para validação
    )
    
    print("\n✅ Treinamento concluído!")
    return history

# ============================================================================
# 6️⃣ SALVAR MODELO TREINADO
# ============================================================================

def salvar_modelo(model, arquivo="alici_treinado_v3.h5"):
    """Salva modelo treinado"""
    
    print(f"\n💾 Salvando modelo em '{arquivo}'...")
    model.save(arquivo)
    
    tamanho_mb = Path(arquivo).stat().st_size / (1024 * 1024)
    print(f"✅ Modelo salvo: {tamanho_mb:.1f} MB")
    
    return arquivo

# ============================================================================
# 7️⃣ AVALIAR MODELO
# ============================================================================

def avaliar_modelo(model, X, Y):
    """Avalia performance no dataset"""
    
    print("\n📊 Avaliando modelo...")
    loss, accuracy = model.evaluate(X, Y, verbose=0)
    
    print(f"✅ Loss: {loss:.4f}")
    print(f"✅ Accuracy: {accuracy*100:.2f}%")
    
    return loss, accuracy

# ============================================================================
# 🎯 MAIN - ORQUESTRA TUDO
# ============================================================================

def main():
    print("=" * 80)
    print("🚀 FINE-TUNING DO MODELO ALICI™ - GOOGLE COLAB")
    print("=" * 80)
    print()
    
    # 1. Carregar dataset
    try:
        perguntas, respostas = carregar_dataset("dataset_expandido.json")
    except FileNotFoundError:
        print("❌ Erro: 'dataset_expandido.json' não encontrado")
        print("   Faça upload do arquivo antes de executar")
        return False
    
    # 2. Pré-processar
    X, Y, tokenizer = preprocessar_dados(perguntas, respostas)
    
    # 3. Carregar modelo existente
    model = carregar_modelo_existente("modelo_animais_cifar100.h5")
    
    if model is None:
        print("❌ Nenhum modelo encontrado")
        return False
    
    # 4. Compilar para fine-tuning
    model = compilar_modelo(model, learning_rate=1e-4)
    
    # 5. Treinar
    history = treinar_modelo(model, X, Y, epochs=20, batch_size=16)
    
    # 6. Avaliar
    loss, accuracy = avaliar_modelo(model, X, Y)
    
    # 7. Salvar
    arquivo_novo = salvar_modelo(model, "alici_treinado_v3.h5")
    
    # Resumo final
    print("\n" + "=" * 80)
    print("✅ FINE-TUNING CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    print()
    print("📋 Resumo:")
    print(f"   • Modelo: alici_treinado_v3.h5 ({Path(arquivo_novo).stat().st_size / (1024*1024):.1f} MB)")
    print(f"   • Accuracy final: {accuracy*100:.2f}%")
    print(f"   • Loss final: {loss:.4f}")
    print(f"   • Dataset: {len(perguntas)} pares Q&A")
    print(f"   • Epochs: 20")
    print()
    print("🎯 Próximos passos:")
    print("   1. Baixe 'alici_treinado_v3.h5' do Colab")
    print("   2. Substitua em production: model/modelo_animais_cifar100.h5")
    print("   3. Redeploy em Render.com")
    print("   4. Teste com teste_modelo.py")
    print()
    
    return True

if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)
