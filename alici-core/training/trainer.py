"""
🎓 TREINAMENTO CENTRALIZADO
Orquestra o treinamento do modelo multimodal
Loga métricas no Neon a cada época
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import callbacks
import numpy as np
import os
import time
from datetime import datetime
import sys

# Adicionar path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.multimodal_model import criar_modelo_multimodal
from database.neon import db


class TrainerMultimodal:
    def __init__(self, model_name="alici_core", learning_rate=1e-4):
        """
        Inicializa o trainer
        
        Args:
            model_name: Nome do modelo
            learning_rate: Taxa de aprendizado (default 1e-4 para fine-tuning)
        """
        self.model_name = model_name
        self.learning_rate = learning_rate
        self.model = None
        self.history = None
    
    def compilar_modelo(self, num_classes=256):
        """Compila o modelo com otimizador Adam e learning rate baixa"""
        print(f"📦 Compilando modelo {self.model_name}...")
        
        self.model = criar_modelo_multimodal(num_classes=num_classes)
        
        optimizer = keras.optimizers.Adam(learning_rate=self.learning_rate)
        
        self.model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        print(f"✅ Modelo compilado com LR={self.learning_rate}")
        print(f"📊 Parâmetros: {self.model.count_params():,}")
        
        return self.model
    
    def criar_callbacks(self, patience=5):
        """Cria callbacks para treinamento"""
        
        callback_list = [
            # Early stopping
            callbacks.EarlyStopping(
                monitor='val_loss',
                patience=patience,
                restore_best_weights=True,
                verbose=1
            ),
            
            # Reduce LR on plateau
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=2,
                min_lr=1e-7,
                verbose=1
            ),
            
            # Callback customizado para Neon logging
            NeonLoggingCallback(self.model_name)
        ]
        
        return callback_list
    
    def treinar(
        self,
        X_train, y_train,
        X_val=None, y_val=None,
        epochs=50,
        batch_size=32,
        verbose=1
    ):
        """
        Treina o modelo multimodal
        
        Args:
            X_train: Lista [imagens, textos, áudios]
            y_train: Labels (one-hot encoded)
            X_val: Validation data
            y_val: Validation labels
            epochs: Número de épocas
            batch_size: Tamanho do batch
            verbose: Verbosidade
        
        Returns:
            history: Histórico de treinamento
        """
        
        print(f"\n🚀 Iniciando treinamento...")
        print(f"📊 Epochs: {epochs}, Batch size: {batch_size}")
        
        callbacks_list = self.criar_callbacks()
        
        if X_val is not None and y_val is not None:
            validation_data = (X_val, y_val)
        else:
            validation_data = None
        
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks_list,
            verbose=verbose
        )
        
        return self.history
    
    def salvar_modelo(self, path="alici_core.h5"):
        """Salva o modelo treinado"""
        if self.model is None:
            print("❌ Modelo não inicializado")
            return False
        
        try:
            self.model.save(path)
            print(f"✅ Modelo salvo em {path}")
            
            # Registrar no Neon
            tamanho_mb = os.path.getsize(path) / (1024 * 1024)
            
            # Accuracy do melhor resultado
            val_accs = self.history.history.get('val_accuracy', [0])
            best_acc = max(val_accs) if val_accs else 0
            
            db.registrar_modelo(
                nome=self.model_name,
                versao="1.0",
                tipo="multimodal",
                tamanho_mb=tamanho_mb,
                accuracy=float(best_acc),
                parameters=self.model.count_params()
            )
            
            return True
        
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            return False
    
    def avaliar(self, X_test, y_test):
        """Avalia o modelo no conjunto de teste"""
        if self.model is None:
            print("❌ Modelo não carregado")
            return None
        
        print("\n📈 Avaliando modelo...")
        loss, accuracy = self.model.evaluate(X_test, y_test, verbose=0)
        
        print(f"✅ Loss: {loss:.4f}")
        print(f"✅ Accuracy: {accuracy:.4f}")
        
        return {"loss": loss, "accuracy": accuracy}
    
    def fazer_predicao(self, X):
        """Faz predições"""
        if self.model is None:
            print("❌ Modelo não carregado")
            return None
        
        predictions = self.model.predict(X, verbose=0)
        return predictions
    
    def carregar_modelo(self, path="alici_core.h5"):
        """Carrega um modelo pré-treinado"""
        try:
            self.model = keras.models.load_model(path)
            print(f"✅ Modelo carregado de {path}")
            return self.model
        except Exception as e:
            print(f"❌ Erro ao carregar modelo: {e}")
            return None


class NeonLoggingCallback(callbacks.Callback):
    """Callback customizado para logar métricas no Neon"""
    
    def __init__(self, modelo_nome):
        super().__init__()
        self.modelo_nome = modelo_nome
        self.epoch_start = None
    
    def on_epoch_begin(self, epoch, logs=None):
        self.epoch_start = time.time()
    
    def on_epoch_end(self, epoch, logs=None):
        if logs is None:
            logs = {}
        
        tempo_epoch = int((time.time() - self.epoch_start) * 1000)  # em ms
        
        loss = logs.get('loss', 0)
        accuracy = logs.get('accuracy', 0)
        val_loss = logs.get('val_loss', 0)
        val_accuracy = logs.get('val_accuracy', 0)
        
        # Log no Neon
        success = db.log_treino(
            modelo=self.modelo_nome,
            tipo_dado="multimodal",
            epoch=epoch + 1,
            loss=float(loss),
            accuracy=float(accuracy),
            val_loss=float(val_loss),
            val_accuracy=float(val_accuracy),
            tempo_epoch=tempo_epoch
        )
        
        if success:
            print(f"  📊 [NEON] Epoch {epoch + 1} - Loss: {loss:.4f}, Acc: {accuracy:.4f}, Val Acc: {val_accuracy:.4f}")


# Funções helper para testing
def gerar_dados_dummy(n_samples=100):
    """Gera dados dummy para testes"""
    X_img = np.random.rand(n_samples, 32, 32, 3)
    X_text = np.random.randint(0, 5000, (n_samples, 50))
    X_audio = np.random.rand(n_samples, 13)
    y = tf.keras.utils.to_categorical(np.random.randint(0, 256, n_samples), 256)
    
    return [X_img, X_text, X_audio], y


if __name__ == "__main__":
    print("🎓 Teste de Treinamento Multimodal\n")
    
    # Inicializar trainer
    trainer = TrainerMultimodal(model_name="alici_core_test", learning_rate=1e-4)
    
    # Compilar
    trainer.compilar_modelo(num_classes=256)
    
    # Gerar dados dummy
    print("📂 Gerando dados dummy...")
    X_train, y_train = gerar_dados_dummy(n_samples=100)
    X_val, y_val = gerar_dados_dummy(n_samples=20)
    
    # Treinar
    print("\n🚀 Iniciando treinamento (5 épocas)...")
    trainer.treinar(
        X_train, y_train,
        X_val=X_val, y_val=y_val,
        epochs=5,
        batch_size=16,
        verbose=1
    )
    
    # Avaliar
    X_test, y_test = gerar_dados_dummy(n_samples=20)
    trainer.avaliar(X_test, y_test)
    
    # Salvar
    trainer.salvar_modelo("alici_core_test.h5")
    
    print("\n✅ Teste completo!")
