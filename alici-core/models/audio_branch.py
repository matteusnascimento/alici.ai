"""
🎵 RAMO DE ÁUDIO - DENSE LAYERS
Processa features de áudio (MFCC) através de dense layers
Input: (13,) - MFCC features
Output: 128 features
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


def audio_branch(input_dim=13):
    """
    Cria um ramo Dense para processar áudio
    
    Args:
        input_dim: Número de features (MFCC default = 13)
    
    Returns:
        (input_layer, output_features): Input tensor e output após processamento
    """
    
    # Input
    audio_input = keras.Input(shape=(input_dim,), name="audio_input")
    
    # Dense Block 1
    x = layers.Dense(256, activation='relu', name="dense1")(audio_input)
    x = layers.BatchNormalization(name="bn1")(x)
    x = layers.Dropout(0.3, name="dropout1")(x)
    
    # Dense Block 2
    x = layers.Dense(128, activation='relu', name="dense2")(x)
    x = layers.BatchNormalization(name="bn2")(x)
    x = layers.Dropout(0.3, name="dropout2")(x)
    
    # Dense Block 3
    x = layers.Dense(128, activation='relu', name="dense3")(x)
    x = layers.BatchNormalization(name="bn3")(x)
    
    # Output features
    audio_output = layers.Dense(128, activation='relu', name="audio_features")(x)
    
    return audio_input, audio_output


def create_audio_model(input_dim=13):
    """Cria modelo completo (útil para teste isolado)"""
    audio_input, audio_features = audio_branch(input_dim)
    model = keras.Model(inputs=audio_input, outputs=audio_features, name="AudioBranch")
    return model


if __name__ == "__main__":
    # Teste
    print("🎵 Testando Audio Branch...")
    model = create_audio_model()
    model.summary()
    
    # Teste com dummy data
    import numpy as np
    test_audio = np.random.rand(1, 13)  # MFCC features
    output = model.predict(test_audio, verbose=0)
    print(f"✅ Output shape: {output.shape}")
