"""
⚡ QUICK REFERENCE - ALICI™ CORE
Cheat sheet para desenvolvimento rápido
"""

# ═══════════════════════════════════════════════════════════════════════

## 1. IMPORTS PRINCIPAIS

from database.neon import db, NeonDB
from models.image_branch import image_branch, create_image_model
from models.text_branch import text_branch, create_text_model
from models.audio_branch import audio_branch, create_audio_model
from models.multimodal_model import criar_modelo_multimodal
from training.trainer import TrainerMultimodal, gerar_dados_dummy
from api.main import app

# ═══════════════════════════════════════════════════════════════════════

## 2. SETUP RÁPIDO

# Instalar dependências
pip install -r requirements.txt

# Configurar env
cp .env.example .env
# Edite DATABASE_URL

# Validar
python teste_completo.py


# ═══════════════════════════════════════════════════════════════════════

## 3. TRABALHAR COM DATABASE

# Conectar
conn = db.conectar()

# Criar tabelas
db.criar_tabelas()

# Log de treinamento
db.log_treino(
    modelo="alici_core",
    tipo_dado="multimodal",
    epoch=1,
    loss=0.45,
    accuracy=0.92,
    val_loss=0.48,
    val_accuracy=0.90,
    tempo_epoch=125
)

# Consultar logs
logs = db.obter_logs_treino(modelo="alici_core_v1", limit=20)
for log in logs:
    print(f"Epoch {log['epoch']}: Loss={log['loss']:.4f}")

# Registrar modelo
db.registrar_modelo(
    nome="alici_core_v2",
    versao="2.0",
    tipo="multimodal",
    tamanho_mb=152.5,
    accuracy=0.945,
    parameters=2847504
)

# Listar modelos
modelos = db.obter_modelos()


# ═══════════════════════════════════════════════════════════════════════

## 4. CRIAR MODELOS

# Image Branch
img_input, img_output = image_branch(input_shape=(32, 32, 3))
img_model = create_image_model()  # Model completo para teste

# Text Branch
txt_input, txt_output = text_branch(vocab_size=5000)
txt_model = create_text_model()

# Audio Branch
aud_input, aud_output = audio_branch(input_dim=13)
aud_model = create_audio_model()

# Multimodal Completo
modelo = criar_modelo_multimodal(
    num_classes=256,
    vocab_size=5000,
    embedding_dim=64,
    max_text_length=50,
    image_shape=(32, 32, 3),
    audio_features=13
)


# ═══════════════════════════════════════════════════════════════════════

## 5. TREINAR MODELO

# Criar trainer
trainer = TrainerMultimodal(
    model_name="alici_core_v1",
    learning_rate=1e-4
)

# Compilar
trainer.compilar_modelo(num_classes=256)

# Preparar dados
X_train, y_train = gerar_dados_dummy(n_samples=1000)
X_val, y_val = gerar_dados_dummy(n_samples=200)

# OU seus dados reais
# X_train = [imagens, textos, áudios]
# y_train = labels one-hot encoded (N, 256)

# Treinar
history = trainer.treinar(
    X_train, y_train,
    X_val=X_val, y_val=y_val,
    epochs=50,
    batch_size=32,
    verbose=1
)

# Avaliar
metrics = trainer.avaliar(X_test, y_test)
print(f"Loss: {metrics['loss']:.4f}, Accuracy: {metrics['accuracy']:.4f}")

# Fazer predições
predictions = trainer.fazer_predicao([X_test_img, X_test_txt, X_test_aud])

# Salvar modelo
trainer.salvar_modelo("alici_core.h5")

# Carregar modelo pré-treinado
trainer.carregar_modelo("alici_core.h5")


# ═══════════════════════════════════════════════════════════════════════

## 6. PREPARAR DADOS

import numpy as np
from PIL import Image
import librosa

# Imagens
img = Image.open("foto.png")
img = img.resize((32, 32))
X_img = np.array(img) / 255.0  # Normalizar
X_img = np.expand_dims(X_img, 0)  # Add batch dimension

# Texto
from tensorflow.keras.preprocessing.text import Tokenizer

tokenizer = Tokenizer(num_words=5000)
texts = ["seu texto aqui"]
tokenizer.fit_on_texts(texts)
X_txt = tokenizer.texts_to_sequences(texts)
X_txt = pad_sequences(X_txt, maxlen=50)  # (N, 50)

# Áudio
y, sr = librosa.load("audio.wav")
mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
X_aud = np.mean(mfcc, axis=1)  # (13,)
X_aud = np.expand_dims(X_aud, 0)  # (1, 13)

# Labels one-hot
y_onehot = to_categorical(np.array([42]), num_classes=256)


# ═══════════════════════════════════════════════════════════════════════

## 7. API ENDPOINTS

# Status
GET /

# Health check
GET /health

# Status detalhado
GET /status

# Fazer predição
POST /predict
{
  "image": <file>,
  "text": "sua pergunta",
  "audio": <file>
}

# Histórico de treinamento
GET /logs/treino?modelo=alici_core&limit=100

# Listar modelos
GET /modelos

# Recarregar modelo
POST /reload-model

# Documentação
GET /docs


# ═══════════════════════════════════════════════════════════════════════

## 8. EXECUTAR API

# Desenvolvimento
cd api
uvicorn main:app --reload

# Produção
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Com port customizado
uvicorn main:app --port 8001

# Access swagger: http://localhost:8000/docs


# ═══════════════════════════════════════════════════════════════════════

## 9. TESTES

# Teste completo
python teste_completo.py

# Demo visual
python demo.py

# Teste individual
python models/image_branch.py
python models/text_branch.py
python models/audio_branch.py
python models/multimodal_model.py
python training/trainer.py

# Test API
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/status


# ═══════════════════════════════════════════════════════════════════════

## 10. DEBUGGING

# Verificar conexão Neon
from database.neon import db
conn = db.conectar()
if conn:
    print("✅ Conectado")
    conn.close()
else:
    print("❌ Erro de conexão")

# Verificar GPU
import tensorflow as tf
print(tf.config.list_physical_devices('GPU'))

# Verificar imports
python -c "from models.multimodal_model import criar_modelo_multimodal; print('✅ OK')"

# Logs do modelo
modelo.summary()

# Verificar shapes
print(f"X_img: {X_img.shape}")
print(f"X_txt: {X_txt.shape}")
print(f"X_aud: {X_aud.shape}")


# ═══════════════════════════════════════════════════════════════════════

## 11. ENVIRONMENT VARIABLES

# .env
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/alici?sslmode=require
ENVIRONMENT=development  # ou production
PORT=8000
LOG_LEVEL=INFO
MODEL_PATH=alici_core.h5
ALLOWED_ORIGINS=http://localhost:3000,https://seu-dominio.com


# ═══════════════════════════════════════════════════════════════════════

## 12. ESTRUTURA DE DADOS

# Modelo Multimodal Input:
[
  X_img: (batch, 32, 32, 3),     # Imagem RGB
  X_txt: (batch, 50),             # Sequência de tokens
  X_aud: (batch, 13)              # MFCC features
]

# Output:
(batch, 256)  # Probabilidades de cada classe

# Labels:
(batch, 256)  # One-hot encoded


# ═══════════════════════════════════════════════════════════════════════

## 13. FLUXO DE PREDIÇÃO

# 1. Receber input
image_file, text_string, audio_file

# 2. Processar
img_array = prepare_image(image_file)  # (1, 32, 32, 3)
txt_array = prepare_text(text_string)  # (1, 50)
aud_array = prepare_audio(audio_file)  # (1, 13)

# 3. Predição
pred = modelo.predict([img_array, txt_array, aud_array])

# 4. Extrair resultado
class_idx = np.argmax(pred[0])
confidence = np.max(pred[0])
probabilities = pred[0].tolist()

# 5. Responder
{
  "prediction": {
    "class": class_idx,
    "confidence": confidence,
    "probabilities": probabilities
  }
}


# ═══════════════════════════════════════════════════════════════════════

## 14. CALLBACKS

# Early Stopping
callbacks.EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

# Reduce LR
callbacks.ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=2,
    min_lr=1e-7
)

# Custom (Neon Logging)
NeonLoggingCallback(model_name="alici_core")


# ═══════════════════════════════════════════════════════════════════════

## 15. DEPLOY

# 1. Atualizar Procfile
web: gunicorn alici_core.api.main:app --workers 4 \
     --worker-class uvicorn.workers.UvicornWorker

# 2. Atualizar requirements.txt
pip freeze > requirements.txt

# 3. Git push
git add .
git commit -m "ALICI Core v1.0"
git push

# 4. Configurar no Render
# - DATABASE_URL env var
# - Auto-deploy ativado

# 5. Verificar
curl https://seu-dominio.onrender.com/
curl https://seu-dominio.onrender.com/status


# ═══════════════════════════════════════════════════════════════════════

## 16. TROUBLESHOOTING RÁPIDO

# Erro: ModuleNotFoundError
pip install -r requirements.txt

# Erro: DATABASE_URL não encontrado
export DATABASE_URL="postgresql://..."

# Erro: Porta em uso
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Erro: Modelo não carrega
python -c "from tensorflow.keras.models import load_model; print(load_model('alici_core.h5'))"

# Erro: Shape mismatch
print(f"X_img: {X_img.shape} (esperado: (batch, 32, 32, 3))")
print(f"X_txt: {X_txt.shape} (esperado: (batch, 50))")
print(f"X_aud: {X_aud.shape} (esperado: (batch, 13))")


# ═══════════════════════════════════════════════════════════════════════

## 17. RECURSOS ÚTEIS

# Documentação
📖 GUIA_USO.md - Tutorial completo
📖 README.md - Overview
📖 TROUBLESHOOTING.md - Soluções

# Código
🔧 teste_completo.py - Validação automática
🎬 demo.py - Demonstração visual
📊 ARCHITECTURE_DIAGRAM.py - Diagramas

# Deployment
🚀 Procfile - Render config
📦 requirements.txt - Dependências
🔐 .env.example - Variáveis


# ═══════════════════════════════════════════════════════════════════════

## 18. DICAS PRO

# Carregar múltiplos modelos
models = {}
models['v1'] = load_model('alici_core_v1.h5')
models['v2'] = load_model('alici_core_v2.h5')

# A/B Testing
pred_v1 = models['v1'].predict(X)
pred_v2 = models['v2'].predict(X)

# Ensembling
ensemble = (pred_v1 + pred_v2) / 2

# Caching
@cache.cached()
def predict_cached(X):
    return model.predict(X)

# Streaming responses
for epoch in range(50):
    train_one_epoch()
    yield f"data: Epoch {epoch}\n\n"


# ═══════════════════════════════════════════════════════════════════════

## 19. PADRÕES COMUNS

# Fine-tuning
trainer = TrainerMultimodal(learning_rate=1e-4)  # LR baixa

# Transfer learning
base_model = load_model('alici_core_v1.h5')
# Congelar pesos
for layer in base_model.layers[:-5]:
    layer.trainable = False
# Treinar últimas 5 camadas

# Distributed training
import tensorflow as tf
strategy = tf.distribute.MirroredStrategy()
with strategy.scope():
    modelo = criar_modelo_multimodal()


# ═══════════════════════════════════════════════════════════════════════

## 20. ROADMAP

Próximas features:
□ JWT Authentication (auth.py)
□ Per-user memory (user_memory.py)
□ Vector embeddings (embeddings.py)
□ RAG integration
□ Autonomous agents
□ Mobile app
□ Voice input/output


# ═══════════════════════════════════════════════════════════════════════

QUICK START (5 minutos):

1. cd alici-core && python teste_completo.py
2. cd api && uvicorn main:app --reload
3. Acesse: http://localhost:8000/docs
4. Teste POST /predict com imagem + texto + áudio
5. Veja resposta em JSON com classe + confiança

═══════════════════════════════════════════════════════════════════════
"""

if __name__ == "__main__":
    print(__doc__)
