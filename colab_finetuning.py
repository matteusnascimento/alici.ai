"""
colab_finetuning.py
🎓 Script de fine-tuning para Google Colab
Use este script no Google Colab com GPU gratuita para treinar modelos
"""

# ============================================================================
# INSTALAÇÃO DE DEPENDÊNCIAS (Execute no Colab)
# ============================================================================

COLAB_SETUP = """
# Execute este bloco primeiro no Google Colab:
!pip install tensorflow numpy pillow
"""

# ============================================================================
# IMPORTS
# ============================================================================

import tensorflow as tf
import numpy as np
import json
from tensorflow import keras
from tensorflow.keras import layers

print("TensorFlow version:", tf.__version__)
print("GPU disponível:", tf.config.list_physical_devices('GPU'))

# ============================================================================
# CARREGAR DATASET
# ============================================================================

def carregar_dataset(caminho_json="dataset_expandido.json"):
    """
    Carrega dataset de perguntas e respostas
    """
    with open(caminho_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    perguntas = [item["pergunta"] for item in data]
    respostas = [item["resposta"] for item in data]
    
    print(f"✅ Dataset carregado: {len(perguntas)} pares")
    return perguntas, respostas

# ============================================================================
# TOKENIZAÇÃO
# ============================================================================

def criar_tokenizer(textos, vocab_size=10000):
    """
    Cria tokenizer para converter texto em números
    """
    tokenizer = keras.preprocessing.text.Tokenizer(
        num_words=vocab_size,
        oov_token="<OOV>",
        char_level=False
    )
    
    tokenizer.fit_on_texts(textos)
    
    print(f"✅ Tokenizer criado com vocabulário de {len(tokenizer.word_index)} palavras")
    return tokenizer

def preparar_dados(perguntas, respostas, tokenizer, max_length=100):
    """
    Converte texto em sequências numéricas
    """
    # Tokenizar perguntas
    perguntas_seq = tokenizer.texts_to_sequences(perguntas)
    perguntas_pad = keras.preprocessing.sequence.pad_sequences(
        perguntas_seq,
        maxlen=max_length,
        padding='post',
        truncating='post'
    )
    
    # Tokenizar respostas
    respostas_seq = tokenizer.texts_to_sequences(respostas)
    respostas_pad = keras.preprocessing.sequence.pad_sequences(
        respostas_seq,
        maxlen=max_length,
        padding='post',
        truncating='post'
    )
    
    print(f"✅ Dados preparados: {perguntas_pad.shape}")
    return perguntas_pad, respostas_pad

# ============================================================================
# MODELO
# ============================================================================

def criar_modelo_seq2seq(vocab_size, embedding_dim=128, lstm_units=256):
    """
    Cria modelo Seq2Seq com LSTM para Q&A
    """
    # Encoder
    encoder_input = layers.Input(shape=(None,))
    encoder_embedding = layers.Embedding(vocab_size, embedding_dim)(encoder_input)
    encoder_lstm = layers.LSTM(lstm_units, return_state=True)
    encoder_output, state_h, state_c = encoder_lstm(encoder_embedding)
    encoder_states = [state_h, state_c]
    
    # Decoder
    decoder_input = layers.Input(shape=(None,))
    decoder_embedding = layers.Embedding(vocab_size, embedding_dim)(decoder_input)
    decoder_lstm = layers.LSTM(lstm_units, return_sequences=True, return_state=True)
    decoder_output, _, _ = decoder_lstm(decoder_embedding, initial_state=encoder_states)
    decoder_dense = layers.Dense(vocab_size, activation='softmax')
    decoder_output = decoder_dense(decoder_output)
    
    model = keras.Model([encoder_input, decoder_input], decoder_output)
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("✅ Modelo Seq2Seq criado")
    model.summary()
    
    return model

def criar_modelo_simples(vocab_size, embedding_dim=128, max_length=100):
    """
    Cria modelo mais simples para classificação de intenções
    """
    model = keras.Sequential([
        layers.Embedding(vocab_size, embedding_dim, input_length=max_length),
        layers.Bidirectional(layers.LSTM(128, return_sequences=True)),
        layers.Dropout(0.3),
        layers.Bidirectional(layers.LSTM(64)),
        layers.Dropout(0.3),
        layers.Dense(128, activation='relu'),
        layers.Dense(vocab_size, activation='softmax')
    ])
    
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print("✅ Modelo simples criado")
    model.summary()
    
    return model

# ============================================================================
# TREINAMENTO
# ============================================================================

def treinar_modelo(model, X_train, y_train, epochs=50, batch_size=32, validation_split=0.2):
    """
    Treina o modelo
    """
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=0.00001
        )
    ]
    
    history = model.fit(
        X_train,
        y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=validation_split,
        callbacks=callbacks,
        verbose=1
    )
    
    print("✅ Treinamento concluído")
    return history

# ============================================================================
# SALVAR MODELO
# ============================================================================

def salvar_modelo(model, tokenizer, nome_base="alici_treinado"):
    """
    Salva modelo e tokenizer
    """
    # Salvar modelo
    model_path = f"{nome_base}.h5"
    model.save(model_path)
    print(f"✅ Modelo salvo: {model_path}")
    
    # Salvar tokenizer
    tokenizer_config = {
        "word_index": tokenizer.word_index,
        "config": tokenizer.get_config()
    }
    
    tokenizer_path = f"{nome_base}_tokenizer.json"
    with open(tokenizer_path, "w", encoding="utf-8") as f:
        json.dump(tokenizer_config, f, ensure_ascii=False)
    
    print(f"✅ Tokenizer salvo: {tokenizer_path}")
    
    return model_path, tokenizer_path

# ============================================================================
# PIPELINE COMPLETO
# ============================================================================

def pipeline_completo():
    """
    Pipeline completo de treinamento
    """
    print("=" * 70)
    print("🎓 ALICI™ - Fine-tuning no Google Colab")
    print("=" * 70)
    
    # 1. Carregar dataset
    print("\n📊 1. Carregando dataset...")
    perguntas, respostas = carregar_dataset()
    
    # 2. Criar tokenizer
    print("\n🔤 2. Criando tokenizer...")
    todos_textos = perguntas + respostas
    tokenizer = criar_tokenizer(todos_textos, vocab_size=10000)
    
    # 3. Preparar dados
    print("\n🔨 3. Preparando dados...")
    X_train, y_train = preparar_dados(perguntas, respostas, tokenizer)
    
    # 4. Criar modelo
    print("\n🧠 4. Criando modelo...")
    model = criar_modelo_simples(
        vocab_size=10000,
        embedding_dim=128,
        max_length=100
    )
    
    # 5. Treinar
    print("\n🎯 5. Treinando modelo...")
    print("Isso pode levar alguns minutos com GPU...")
    history = treinar_modelo(
        model,
        X_train,
        y_train,
        epochs=50,
        batch_size=32
    )
    
    # 6. Salvar
    print("\n💾 6. Salvando modelo...")
    model_path, tokenizer_path = salvar_modelo(model, tokenizer)
    
    print("\n" + "=" * 70)
    print("✅ TREINAMENTO CONCLUÍDO!")
    print("=" * 70)
    print(f"\nArquivos gerados:")
    print(f"  • {model_path}")
    print(f"  • {tokenizer_path}")
    print(f"\nBaixe estes arquivos e coloque na pasta model/ do projeto")
    
    return model, tokenizer, history

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    """
    INSTRUÇÕES DE USO NO GOOGLE COLAB:
    
    1. Abra Google Colab: https://colab.research.google.com
    2. Ative GPU gratuita: Runtime > Change runtime type > GPU
    3. Upload dataset_expandido.json
    4. Execute este script
    5. Baixe os arquivos .h5 e .json gerados
    6. Coloque na pasta model/ do projeto ALICI
    """
    
    print("\n📚 INSTRUÇÕES:")
    print("1. Certifique-se que dataset_expandido.json está no Colab")
    print("2. Ative GPU: Runtime > Change runtime type > GPU")
    print("3. Execute: pipeline_completo()")
    print("\nExemplo:")
    print(">>> model, tokenizer, history = pipeline_completo()")
    
    # Descomentar para executar automaticamente:
    # model, tokenizer, history = pipeline_completo()
