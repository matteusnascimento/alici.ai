"""
🖼️ RAMO DE IMAGEM - CNN
Processa imagens através de convolução
Input: (32, 32, 3)
Output: 128 features
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


def image_branch(input_shape=(32, 32, 3)):
    """
    Cria um ramo CNN para processar imagens
    
    Args:
        input_shape: Shape das imagens (altura, largura, canais)
    
    Returns:
        (input_layer, output_features): Input tensor e output após processamento
    """
    
    # Input
    img_input = keras.Input(shape=input_shape, name="image_input")
    
    # Block 1: Conv + MaxPool
    x = layers.Conv2D(32, (3, 3), activation='relu', padding='same', name="conv1")(img_input)
    x = layers.MaxPooling2D((2, 2), name="pool1")(x)
    x = layers.BatchNormalization(name="bn1")(x)
    
    # Block 2: Conv + MaxPool
    x = layers.Conv2D(64, (3, 3), activation='relu', padding='same', name="conv2")(x)
    x = layers.MaxPooling2D((2, 2), name="pool2")(x)
    x = layers.BatchNormalization(name="bn2")(x)
    
    # Block 3: Conv
    x = layers.Conv2D(128, (3, 3), activation='relu', padding='same', name="conv3")(x)
    x = layers.BatchNormalization(name="bn3")(x)
    
    # Global Average Pooling
    x = layers.GlobalAveragePooling2D(name="gap")(x)
    
    # Dense layer - Output features
    img_output = layers.Dense(128, activation='relu', name="image_features")(x)
    
    return img_input, img_output


def create_image_model(input_shape=(32, 32, 3)):
    """Cria modelo completo (útil para teste isolado)"""
    img_input, img_features = image_branch(input_shape)
    model = keras.Model(inputs=img_input, outputs=img_features, name="ImageBranch")
    return model


if __name__ == "__main__":
    # Teste
    print("🖼️ Testando Image Branch...")
    model = create_image_model()
    model.summary()
    
    # Teste com dummy data
    import numpy as np
    test_img = np.random.rand(1, 32, 32, 3)
    output = model.predict(test_img, verbose=0)
    print(f"✅ Output shape: {output.shape}")
