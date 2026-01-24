"""
🔀 MODELO MULTIMODAL - FUSÃO
Combina os 3 ramos (imagem, texto, áudio) e cria camadas de fusão
Arquitetura: [image_branch] \
                              → Concatenate → Dense → Dropout → Output
            [text_branch]  /
            [audio_branch] \
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from .image_branch import image_branch
from .text_branch import text_branch
from .audio_branch import audio_branch


def criar_modelo_multimodal(
    num_classes=256,
    vocab_size=5000,
    embedding_dim=64,
    max_text_length=50,
    image_shape=(32, 32, 3),
    audio_features=13
):
    """
    Cria modelo multimodal com 3 ramos e fusão
    
    Args:
        num_classes: Número de classes para output (default 256)
        vocab_size: Tamanho do vocabulário para texto
        embedding_dim: Dimensão do embedding de texto
        max_text_length: Comprimento máximo de sequência de texto
        image_shape: Shape das imagens
        audio_features: Número de features de áudio (MFCC)
    
    Returns:
        modelo: Modelo Keras compilado
    """
    
    # 1️⃣ RAMO DE IMAGEM
    img_input, img_features = image_branch(input_shape=image_shape)
    
    # 2️⃣ RAMO DE TEXTO
    text_input, text_features = text_branch(
        vocab_size=vocab_size,
        embedding_dim=embedding_dim,
        max_length=max_text_length
    )
    
    # 3️⃣ RAMO DE ÁUDIO
    audio_input, audio_features = audio_branch(input_dim=audio_features)
    
    # 🔀 FUSÃO - Concatenar outputs dos 3 ramos
    # Cada ramo output: 128 features
    # Total após concat: 128 * 3 = 384 features
    fused = layers.Concatenate(name="fusion_concatenate")([
        img_features,
        text_features,
        audio_features
    ])
    
    # 🎯 CAMADAS DENSAS DE FUSÃO
    fused = layers.Dense(256, activation='relu', name="fusion_dense1")(fused)
    fused = layers.BatchNormalization(name="fusion_bn1")(fused)
    fused = layers.Dropout(0.4, name="fusion_dropout1")(fused)
    
    fused = layers.Dense(128, activation='relu', name="fusion_dense2")(fused)
    fused = layers.BatchNormalization(name="fusion_bn2")(fused)
    fused = layers.Dropout(0.3, name="fusion_dropout2")(fused)
    
    # OUTPUT
    output = layers.Dense(num_classes, activation='softmax', name="output")(fused)
    
    # 📦 CRIAR MODELO
    modelo = keras.Model(
        inputs=[img_input, text_input, audio_input],
        outputs=output,
        name="AliciMultimodal"
    )
    
    return modelo


def contar_parametros(modelo):
    """Conta total de parâmetros"""
    total = modelo.count_params()
    return total


if __name__ == "__main__":
    print("🔀 Testando Modelo Multimodal...")
    
    modelo = criar_modelo_multimodal(num_classes=256)
    modelo.summary()
    
    print(f"\n✅ Total de parâmetros: {contar_parametros(modelo):,}")
    
    # Teste com dummy data
    import numpy as np
    
    batch_size = 1
    dummy_image = np.random.rand(batch_size, 32, 32, 3)
    dummy_text = np.random.randint(0, 5000, (batch_size, 50))
    dummy_audio = np.random.rand(batch_size, 13)
    
    print(f"\n📊 Teste de forward pass...")
    output = modelo.predict(
        [dummy_image, dummy_text, dummy_audio],
        verbose=0
    )
    
    print(f"✅ Output shape: {output.shape}")
    print(f"✅ Modelo compilado e testado com sucesso!")
