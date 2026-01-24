#!/usr/bin/env python3
"""
🚀 SCRIPT COMPLETO DE FINE-TUNING EM GOOGLE COLAB
ALICI™ - Treinamento Multi-Modal (Texto + Áudio + Imagens)

⚠️ INSTRUÇÕES PARA COLAB:
1. Copie TODO este código para uma célula do Colab
2. Execute a célula
3. Ele vai pedir upload do modelo .h5 (botão aparecerá automaticamente)
4. Ele vai pedir upload de datasets (botões para cada tipo)
5. Escolha quais dados quer usar (texto, áudio, imagens)
6. Treina automaticamente com GPU grátis
7. Baixe o modelo treinado ao final

Suporta:
  ✅ Texto (JSON)
  ✅ Áudio (WAV, MP3)
  ✅ Imagens (PNG, JPG)
  ✅ Multi-modal (todos juntos)

Criador: Mateus Nascimento dos Santos
Data: 2024/2026
"""

import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications import MobileNetV2
from pathlib import Path
import warnings
import os
import librosa
from google.colab import files
import zipfile
import shutil

warnings.filterwarnings('ignore')

# ============================================================================
# 🔧 UTILITÁRIOS - UPLOAD/DOWNLOAD
# ============================================================================

def fazer_upload_arquivo(tipos_permitidos=['.h5', '.json', '.zip']):
    """Upload interativo de arquivo com botão no Colab"""
    print(f"\n📁 Permitidos: {', '.join(tipos_permitidos)}")
    print("Clique em 'Executar' e selecione arquivo...")
    uploaded = files.upload()
    
    for filename in uploaded.keys():
        ext = Path(filename).suffix
        if ext not in tipos_permitidos:
            print(f"❌ {filename}: tipo não permitido")
            os.remove(filename)
            continue
        print(f"✅ {filename} ({len(uploaded[filename]) / (1024*1024):.1f} MB)")
        return filename
    
    return None

def fazer_download_arquivo(arquivo):
    """Download do arquivo para computador local"""
    if os.path.exists(arquivo):
        tamanho = os.path.getsize(arquivo) / (1024 * 1024)
        print(f"\n📥 Baixando {arquivo} ({tamanho:.1f} MB)...")
        files.download(arquivo)
        print("✅ Download iniciado!")
    else:
        print(f"❌ Arquivo não encontrado: {arquivo}")

# ============================================================================
# 1️⃣ TREINAR COM TEXTO
# ============================================================================

def carregar_dataset_texto(arquivo_json="dataset_expandido.json"):
    """Carrega dataset JSON de texto"""
    print("📚 Carregando dataset de TEXTO...")
    
    if not os.path.exists(arquivo_json):
        print(f"❌ Arquivo não encontrado: {arquivo_json}")
        print("Faça upload do arquivo JSON primeiro")
        return None, None
    
    try:
        with open(arquivo_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        perguntas = data.get('perguntas', [])
        respostas = data.get('respostas', [])
        
        print(f"✅ Texto carregado: {len(perguntas)} pares Q&A")
        return perguntas, respostas
    
    except Exception as e:
        print(f"❌ Erro ao carregar: {e}")
        return None, None

def preprocessar_texto(perguntas, respostas, vocab_size=15000, max_len=40):
    """Tokeniza e prepara dados de texto para treinamento"""
    print("\n🔧 Pré-processando TEXTO...")
    
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
    
    print(f"✅ Texto processado:")
    print(f"   X shape: {X.shape}")
    print(f"   Y shape: {Y_labels.shape}")
    print(f"   Vocab size: {len(tokenizer.word_index)}")
    
    return X, Y_labels

# ============================================================================
# 2️⃣ TREINAR COM ÁUDIO
# ============================================================================

def carregar_dataset_audio(pasta_audio="audio_files"):
    """Carrega arquivos de áudio (WAV, MP3)"""
    print(f"\n🎙️ Carregando áudios de '{pasta_audio}'...")
    
    if not os.path.exists(pasta_audio):
        print(f"⚠️ Pasta não encontrada: {pasta_audio}")
        print("Extraindo de ZIP se houver...")
        
        for arquivo_zip in Path(".").glob("*.zip"):
            with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
                zip_ref.extractall()
            print(f"✅ Extraído: {arquivo_zip}")
            break
    
    if not os.path.exists(pasta_audio):
        print(f"❌ Nenhum arquivo de áudio encontrado")
        return None, None
    
    X_audio = []
    labels = []
    
    extensoes = ['.wav', '.mp3', '.flac', '.ogg']
    
    for arquivo in Path(pasta_audio).iterdir():
        if arquivo.suffix.lower() not in extensoes:
            continue
        
        try:
            # Carregar áudio
            y, sr = librosa.load(str(arquivo), sr=22050, duration=3)
            
            # Extrair features (MFCC)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # Redimensionar para tamanho padrão
            mfcc_resized = np.pad(mfcc, ((0, 0), (0, 130 - mfcc.shape[1])), mode='constant')[:, :130]
            
            X_audio.append(mfcc_resized)
            labels.append(arquivo.stem)
            
        except Exception as e:
            print(f"⚠️ Erro ao processar {arquivo}: {e}")
            continue
    
    if X_audio:
        X_audio = np.array(X_audio)
        print(f"✅ Áudio carregado: {len(X_audio)} arquivos")
        print(f"   Shape: {X_audio.shape}")
        return X_audio, np.arange(len(X_audio))
    
    return None, None

def preprocessar_audio(X_audio):
    """Normaliza features de áudio"""
    print("\n🔧 Pré-processando ÁUDIO...")
    
    # Normalizar
    X_audio_norm = (X_audio - np.mean(X_audio, axis=0)) / (np.std(X_audio, axis=0) + 1e-8)
    
    print(f"✅ Áudio processado:")
    print(f"   Shape: {X_audio_norm.shape}")
    
    return X_audio_norm

# ============================================================================
# 3️⃣ TREINAR COM IMAGENS
# ============================================================================

def carregar_dataset_imagens(pasta_imagens="imagens"):
    """Carrega imagens (PNG, JPG)"""
    print(f"\n🖼️ Carregando imagens de '{pasta_imagens}'...")
    
    if not os.path.exists(pasta_imagens):
        print(f"⚠️ Pasta não encontrada: {pasta_imagens}")
        return None, None
    
    X_imagens = []
    labels = []
    
    extensoes = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    
    for arquivo in Path(pasta_imagens).iterdir():
        if arquivo.suffix.lower() not in extensoes:
            continue
        
        try:
            # Carregar imagem
            img = load_img(str(arquivo), target_size=(224, 224))
            img_array = img_to_array(img) / 255.0  # Normalizar
            
            X_imagens.append(img_array)
            labels.append(arquivo.stem)
            
        except Exception as e:
            print(f"⚠️ Erro ao processar {arquivo}: {e}")
            continue
    
    if X_imagens:
        X_imagens = np.array(X_imagens)
        print(f"✅ Imagens carregadas: {len(X_imagens)} arquivos")
        print(f"   Shape: {X_imagens.shape}")
        return X_imagens, np.arange(len(X_imagens))
    
    return None, None

# ============================================================================
# 4️⃣ CARREGAR MODELO EXISTENTE
# ============================================================================

def carregar_modelo_existente(modelo_path=None):
    """
    Carrega modelo .h5 existente
    Se não fornecer path, pede upload interativo
    """
    print("\n🧠 Carregando MODELO EXISTENTE...")
    
    if modelo_path is None:
        print("\n📤 Nenhum modelo encontrado localmente")
        print("Clique em 'Executar' para fazer upload do modelo .h5...")
        modelo_path = fazer_upload_arquivo(['.h5'])
        
        if modelo_path is None:
            print("❌ Nenhum modelo foi enviado")
            return None
    
    try:
        model = tf.keras.models.load_model(modelo_path)
        print(f"✅ Modelo carregado: {modelo_path}")
        print(f"   Parâmetros: {model.count_params():,}")
        print(f"   Camadas: {len(model.layers)}")
        return model
    
    except Exception as e:
        print(f"❌ Erro ao carregar: {e}")
        return None

# ============================================================================
# 5️⃣ COMPILAR PARA FINE-TUNING
# ============================================================================

def compilar_modelo(model, learning_rate=1e-4):
    """
    Compila modelo com learning rate BAIXO
    Essencial para não apagar aprendizado anterior
    """
    print("\n⚙️ Compilando modelo para fine-tuning...")
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    
    print(f"✅ Compilado com learning_rate={learning_rate}")
    return model

# ============================================================================
# 6️⃣ TREINAR (FINE-TUNING)
# ============================================================================

def treinar_modelo(model, X, Y, tipo_dado="Texto", epochs=20, batch_size=16):
    """Fine-tuning do modelo com novos dados"""
    
    print(f"\n🏋️ Iniciando fine-tuning com {tipo_dado}...")
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
        validation_split=0.15,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=3,
                restore_best_weights=True
            )
        ]
    )
    
    print(f"\n✅ Treinamento concluído!")
    return history

# ============================================================================
# 7️⃣ AVALIAR MODELO
# ============================================================================

def avaliar_modelo(model, X, Y, tipo_dado="Texto"):
    """Avalia performance no dataset"""
    
    print(f"\n📊 Avaliando modelo em {tipo_dado}...")
    loss, accuracy = model.evaluate(X, Y, verbose=0)
    
    print(f"✅ Loss: {loss:.4f}")
    print(f"✅ Accuracy: {accuracy*100:.2f}%")
    
    return loss, accuracy

# ============================================================================
# 8️⃣ SALVAR MODELO
# ============================================================================

def salvar_modelo(model, arquivo="alici_treinado_multimodal.h5"):
    """Salva modelo treinado"""
    
    print(f"\n💾 Salvando modelo em '{arquivo}'...")
    model.save(arquivo)
    
    tamanho_mb = Path(arquivo).stat().st_size / (1024 * 1024)
    print(f"✅ Modelo salvo: {tamanho_mb:.1f} MB")
    
    return arquivo

# ============================================================================
# 🎯 MAIN - ORQUESTRA TUDO COM INTERFACE INTERATIVA
# ============================================================================

def menu_principal():
    """Menu interativo para escolher tipos de dados"""
    
    print("\n" + "="*80)
    print("🤖 ALICI™ - TREINAMENTO MULTI-MODAL EM COLAB")
    print("="*80)
    print()
    print("Escolha quais dados usar para treinar:")
    print()
    print("  1️⃣  Apenas TEXTO (rápido, 5-10 min)")
    print("  2️⃣  Apenas ÁUDIO (médio, 10-15 min)")
    print("  3️⃣  Apenas IMAGENS (médio, 10-15 min)")
    print("  4️⃣  TEXTO + ÁUDIO (longo, 15-20 min)")
    print("  5️⃣  TEXTO + IMAGENS (longo, 15-20 min)")
    print("  6️⃣  ÁUDIO + IMAGENS (longo, 15-20 min)")
    print("  7️⃣  TODOS (texto + áudio + imagens, 25-30 min)")
    print()
    print("Digite o número (1-7) ou pressione Enter para TEXTO (padrão):")
    
    return input().strip() or "1"

def main():
    """Orquestra todo o processo de treinamento"""
    
    print("\n" + "="*80)
    print("🚀 ALICI™ FINE-TUNING MULTI-MODAL - GOOGLE COLAB")
    print("="*80)
    print()
    
    # Passo 1: Carregar modelo
    print("📤 PASSO 1: CARREGAR MODELO EXISTENTE")
    print("-" * 80)
    model = carregar_modelo_existente()
    
    if model is None:
        print("❌ Nenhum modelo carregado. Abortando.")
        return False
    
    # Passo 2: Menu de escolha
    opcao = menu_principal()
    
    datasets = {
        "1": ["texto"],
        "2": ["audio"],
        "3": ["imagens"],
        "4": ["texto", "audio"],
        "5": ["texto", "imagens"],
        "6": ["audio", "imagens"],
        "7": ["texto", "audio", "imagens"]
    }
    
    tipos_selecionados = datasets.get(opcao, ["texto"])
    
    # Passo 3: Carregar datasets
    print(f"\n📥 PASSO 2: CARREGAR DATASETS - {', '.join(tipos_selecionados).upper()}")
    print("-" * 80)
    
    dados = {}
    
    if "texto" in tipos_selecionados:
        print("\n📄 TEXTO")
        print("Faça upload de 'dataset_expandido.json' ou similar")
        arquivo_json = fazer_upload_arquivo(['.json'])
        
        if arquivo_json:
            perguntas, respostas = carregar_dataset_texto(arquivo_json)
            if perguntas and respostas:
                X_texto, Y_texto = preprocessar_texto(perguntas, respostas)
                dados["texto"] = (X_texto, Y_texto)
    
    if "audio" in tipos_selecionados:
        print("\n🎙️ ÁUDIO")
        print("Faça upload de ZIP com arquivos WAV/MP3 ou pasta de áudios")
        arquivo_zip = fazer_upload_arquivo(['.zip'])
        
        if arquivo_zip:
            X_audio, Y_audio = carregar_dataset_audio("audio_files")
            if X_audio is not None:
                X_audio = preprocessar_audio(X_audio)
                dados["audio"] = (X_audio, Y_audio)
    
    if "imagens" in tipos_selecionados:
        print("\n🖼️ IMAGENS")
        print("Faça upload de ZIP com imagens ou pasta de imagens")
        arquivo_zip = fazer_upload_arquivo(['.zip'])
        
        if arquivo_zip:
            X_imagens, Y_imagens = carregar_dataset_imagens("imagens")
            if X_imagens is not None:
                dados["imagens"] = (X_imagens, Y_imagens)
    
    if not dados:
        print("❌ Nenhum dataset carregado. Abortando.")
        return False
    
    # Passo 4: Compilar modelo
    print(f"\n⚙️ PASSO 3: COMPILAR MODELO")
    print("-" * 80)
    model = compilar_modelo(model, learning_rate=1e-4)
    
    # Passo 5: Treinar com cada tipo de dado
    print(f"\n🏋️ PASSO 4: TREINAR COM CADA TIPO DE DADO")
    print("-" * 80)
    
    metricas_finais = {}
    
    for tipo_dado, (X, Y) in dados.items():
        print(f"\n{'='*80}")
        print(f"Treinando com {tipo_dado.upper()}...")
        print(f"{'='*80}")
        
        history = treinar_modelo(model, X, Y, tipo_dado=tipo_dado.upper(), epochs=20, batch_size=16)
        loss, accuracy = avaliar_modelo(model, X, Y, tipo_dado=tipo_dado.upper())
        
        metricas_finais[tipo_dado] = {
            "loss": loss,
            "accuracy": accuracy
        }
    
    # Passo 6: Salvar modelo
    print(f"\n💾 PASSO 5: SALVAR MODELO TREINADO")
    print("-" * 80)
    arquivo_modelo = salvar_modelo(model, "alici_treinado_multimodal.h5")
    
    # Passo 7: Resumo final
    print("\n" + "="*80)
    print("✅ TREINAMENTO CONCLUÍDO COM SUCESSO!")
    print("="*80)
    print()
    print("📋 RESUMO DO TREINAMENTO:")
    print()
    print(f"  Modelo: {arquivo_modelo}")
    tamanho_mb = Path(arquivo_modelo).stat().st_size / (1024 * 1024)
    print(f"  Tamanho: {tamanho_mb:.1f} MB")
    print()
    print("  Métricas por tipo de dado:")
    for tipo_dado, metricas in metricas_finais.items():
        print(f"    • {tipo_dado.upper()}:")
        print(f"        Loss: {metricas['loss']:.4f}")
        print(f"        Accuracy: {metricas['accuracy']*100:.2f}%")
    print()
    print("🎯 PRÓXIMOS PASSOS:")
    print()
    print("  1. Clique em 'Executar' para BAIXAR o modelo:")
    fazer_download_arquivo(arquivo_modelo)
    print()
    print("  2. No seu computador:")
    print("     git add alici_treinado_multimodal.h5")
    print("     git commit -m 'feat: Modelo treinado em Colab (multi-modal)'")
    print("     git push")
    print()
    print("  3. Render vai fazer deploy automaticamente")
    print()
    print("="*80)
    
    return True

if __name__ == "__main__":
    # Instalar dependências primeiro
    print("📦 Instalando dependências...")
    os.system("pip install -q librosa -q tensorflow -q keras -q")
    print("✅ Dependências instaladas!\n")
    
    sucesso = main()
    exit(0 if sucesso else 1)
