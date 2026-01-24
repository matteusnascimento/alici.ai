"""
📝 RAMO DE TEXTO - LSTM
Processa sequências de texto através de embedding e LSTM
Input: (50,) - sequência tokenizada
Output: 128 features
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


def text_branch(vocab_size=5000, embedding_dim=64, max_length=50):
    """
    Cria um ramo LSTM para processar texto
    
    Args:
        vocab_size: Tamanho do vocabulário
        embedding_dim: Dimensão do embedding
        max_length: Comprimento máximo da sequência
    
    Returns:
        (input_layer, output_features): Input tensor e output após processamento
    """
    
    # Input
    text_input = keras.Input(shape=(max_length,), dtype='int32', name="text_input")
    
    # Embedding layer
    x = layers.Embedding(
        input_dim=vocab_size,
        output_dim=embedding_dim,
        mask_zero=True,
        name="embedding"
    )(text_input)
    
    # Dropout
    x = layers.Dropout(0.2, name="dropout1")(x)
    
    # LSTM Layer 1
    x = layers.LSTM(
        units=128,
        return_sequences=True,
        dropout=0.2,
        recurrent_dropout=0.2,
        name="lstm1"
    )(x)
    
    # LSTM Layer 2
    x = layers.LSTM(
        units=64,
        dropout=0.2,
        recurrent_dropout=0.2,
        name="lstm2"
    )(x)
    
    # Dense layer - Output features
    text_output = layers.Dense(128, activation='relu', name="text_features")(x)
    
    return text_input, text_output


def create_text_model(vocab_size=5000, embedding_dim=64, max_length=50):
    """Cria modelo completo (útil para teste isolado)"""
    text_input, text_features = text_branch(vocab_size, embedding_dim, max_length)
    model = keras.Model(inputs=text_input, outputs=text_features, name="TextBranch")
    return model


if __name__ == "__main__":
    # Teste
    print("📝 Testando Text Branch...")
    model = create_text_model()
    model.summary()
    
    # Teste com dummy data
    import numpy as np
    test_text = np.random.randint(0, 5000, (1, 50))
    output = model.predict(test_text, verbose=0)
    print(f"✅ Output shape: {output.shape}")
