"""
treinar_modelo_local.py
🎓 Script de treinamento local simplificado para ALICI
Demonstra o processo de treinamento de forma rápida
"""

import os
import json
import numpy as np

print("=" * 70)
print("🎓 ALICI™ - Treinamento de Modelo Local")
print("=" * 70)
print()

# Verificar TensorFlow
print("📦 Verificando TensorFlow...")
try:
    import tensorflow as tf
    print(f"✅ TensorFlow {tf.__version__} disponível")
    TF_DISPONIVEL = True
except ImportError:
    print("⚠️  TensorFlow não disponível")
    print("Para treinar modelos completos, instale: pip install tensorflow")
    TF_DISPONIVEL = False

print()

# Carregar dataset
print("📊 Carregando dataset...")
if not os.path.exists("dataset_expandido.json"):
    print("❌ Dataset não encontrado! Execute gerar_dataset.py primeiro")
    exit(1)

with open("dataset_expandido.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

print(f"✅ Dataset carregado: {len(dataset)} pares")
print()

if TF_DISPONIVEL:
    print("🔨 Preparando dados para treinamento...")
    
    from tensorflow import keras
    
    # Extrair perguntas e respostas
    perguntas = [item["pergunta"] for item in dataset]
    respostas = [item["resposta"] for item in dataset]
    
    # Criar tokenizer
    print("🔤 Criando tokenizer...")
    tokenizer = keras.preprocessing.text.Tokenizer(
        num_words=1000,
        oov_token="<OOV>"
    )
    
    todos_textos = perguntas + respostas
    tokenizer.fit_on_texts(todos_textos)
    
    vocab_size = len(tokenizer.word_index) + 1
    print(f"✅ Vocabulário: {vocab_size} palavras")
    
    # Preparar sequências
    print("📝 Preparando sequências...")
    perguntas_seq = tokenizer.texts_to_sequences(perguntas)
    perguntas_pad = keras.preprocessing.sequence.pad_sequences(
        perguntas_seq,
        maxlen=50,
        padding='post'
    )
    
    respostas_seq = tokenizer.texts_to_sequences(respostas)
    respostas_pad = keras.preprocessing.sequence.pad_sequences(
        respostas_seq,
        maxlen=50,
        padding='post'
    )
    
    print(f"✅ Sequências preparadas: {perguntas_pad.shape}")
    print()
    
    # Criar modelo simples
    print("🧠 Criando modelo neural...")
    
    model = keras.Sequential([
        keras.layers.Embedding(vocab_size, 64, input_length=50),
        keras.layers.Bidirectional(keras.layers.LSTM(64, return_sequences=True)),
        keras.layers.Dropout(0.3),
        keras.layers.Bidirectional(keras.layers.LSTM(32)),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dense(vocab_size, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("✅ Modelo criado")
    print()
    model.summary()
    print()
    
    # Treinar modelo (poucas épocas para demonstração)
    print("🎯 Iniciando treinamento (demonstração rápida)...")
    print("⚠️  Para treinamento completo, use colab_finetuning.py no Google Colab")
    print()
    
    # Preparar targets (usar primeira palavra da resposta como target simplificado)
    targets = np.array([seq[0] if len(seq) > 0 else 0 for seq in respostas_seq])
    
    history = model.fit(
        perguntas_pad,
        targets,
        epochs=5,
        batch_size=8,
        validation_split=0.2,
        verbose=1
    )
    
    print()
    print("✅ Treinamento demonstrativo concluído!")
    print()
    
    # Mostrar resultados
    print("📊 Resultados do treinamento:")
    print(f"  • Acurácia final (treino): {history.history['accuracy'][-1]:.4f}")
    print(f"  • Acurácia final (validação): {history.history['val_accuracy'][-1]:.4f}")
    print(f"  • Loss final (treino): {history.history['loss'][-1]:.4f}")
    print(f"  • Loss final (validação): {history.history['val_loss'][-1]:.4f}")
    print()
    
    # Salvar modelo
    print("💾 Salvando modelo...")
    model_path = "model/alici_demo_treinado.h5"
    
    # Criar diretório se não existir
    os.makedirs("model", exist_ok=True)
    
    model.save(model_path)
    print(f"✅ Modelo salvo: {model_path}")
    
    # Salvar tokenizer
    tokenizer_config = {
        "word_index": tokenizer.word_index,
        "config": tokenizer.get_config()
    }
    
    tokenizer_path = "model/alici_demo_tokenizer.json"
    with open(tokenizer_path, "w", encoding="utf-8") as f:
        json.dump(tokenizer_config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Tokenizer salvo: {tokenizer_path}")
    print()
    
    # Teste rápido
    print("🧪 Testando modelo com exemplo...")
    teste_pergunta = ["quem é você"]
    teste_seq = tokenizer.texts_to_sequences(teste_pergunta)
    teste_pad = keras.preprocessing.sequence.pad_sequences(teste_seq, maxlen=50, padding='post')
    
    predicao = model.predict(teste_pad, verbose=0)
    palavra_idx = np.argmax(predicao[0])
    
    # Encontrar palavra pelo índice
    palavra = None
    for word, idx in tokenizer.word_index.items():
        if idx == palavra_idx:
            palavra = word
            break
    
    print(f"  Pergunta: '{teste_pergunta[0]}'")
    print(f"  Predição (palavra): '{palavra}' (confiança: {predicao[0][palavra_idx]:.4f})")
    print()

else:
    print("⚠️  Pulando treinamento (TensorFlow não disponível)")
    print()
    print("📋 Para treinar modelos:")
    print("  1. Instale TensorFlow: pip install tensorflow")
    print("  2. Execute este script novamente")
    print("  3. Ou use colab_finetuning.py no Google Colab com GPU")
    print()

print("=" * 70)
print("✅ PROCESSO CONCLUÍDO!")
print("=" * 70)
print()

if TF_DISPONIVEL:
    print("🎉 Modelo demonstrativo treinado com sucesso!")
    print()
    print("📌 Próximos passos:")
    print("  • Para treinamento completo, use Google Colab")
    print("  • Upload colab_finetuning.py e dataset_expandido.json")
    print("  • Treine com GPU (30-60 minutos)")
    print("  • Baixe modelo .h5 treinado")
    print("  • Substitua em model/")
else:
    print("📌 Dataset pronto para treinamento!")
    print("  • Upload dataset_expandido.json para Google Colab")
    print("  • Use colab_finetuning.py para treinar")
