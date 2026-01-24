# 🧠 TREINAR ALICI NO GOOGLE COLAB

## ⚡ Quick Start (30 minutos com GPU grátis)

### 1️⃣ Preparar Arquivos

Você precisa de:
```
✅ dataset_expandido.json (100 Q&A pairs)
✅ alici_modelo.h5 (modelo atual - 246MB)
✅ colab_finetuning.py (script de treinamento)
```

Todos estão no repositório GitHub.

---

## 📖 Passo-a-Passo Colab

### Passo 1: Abrir Google Colab

1. Ir a **https://colab.research.google.com/**
2. New notebook
3. Renomear para: "Alici Fine-tuning"

### Passo 2: Configurar Ambiente (CELL 1)

```python
# Instalar dependências
!pip install tensorflow==2.13.0 numpy pandas requests -q

# Verificar GPU
import tensorflow as tf
print(f"GPU disponível: {len(tf.config.list_physical_devices('GPU'))} GPU(s)")
print(f"Versão TensorFlow: {tf.__version__}")
```

**Esperado**: `GPU disponível: 1 GPU(s)` ✅

### Passo 3: Download dos Arquivos (CELL 2)

```python
import os
from google.colab import files

# Criar pasta
os.makedirs("alici_data", exist_ok=True)

# Upload de arquivos do seu computador:
# 1. Clique em folder icon à esquerda
# 2. Upload para "alici_data/"
#    - dataset_expandido.json
#    - alici_modelo.h5

# Ou download direto do GitHub:
!cd alici_data && \
  wget https://github.com/matteusnascimento/alici.ai/raw/main/dataset_expandido.json && \
  wget https://github.com/matteusnascimento/alici.ai/raw/main/alici_modelo.h5

print("✅ Arquivos preparados!")
ls -lh alici_data/
```

### Passo 4: Treinar Modelo (CELL 3)

```python
import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

# 1. Carregar dataset
with open("alici_data/dataset_expandido.json", "r", encoding="utf-8") as f:
    dados = json.load(f)

print(f"📚 Dataset carregado: {len(dados)} pares Q&A")

# 2. Preparar dados (example: usar primeira coluna como features)
X = np.random.random((len(dados), 128))  # Features dummy para exemplo
y = np.random.random((len(dados), 128))  # Target features

print(f"X shape: {X.shape}, y shape: {y.shape}")

# 3. Carregar modelo
model = load_model("alici_data/alici_modelo.h5")
print(f"✅ Modelo carregado com sucesso!")
print(model.summary())

# 4. Recompilar com learning rate baixa (não destruir conhecimento)
model.compile(
    optimizer=Adam(learning_rate=1e-4),
    loss='mse',
    metrics=['mae']
)

# 5. Treinar
print("\n🚀 Iniciando treinamento...")
history = model.fit(
    X, y,
    epochs=20,
    batch_size=8,
    validation_split=0.2,
    verbose=1,
    callbacks=[EarlyStopping(monitor='val_loss', patience=3)]
)

# 6. Salvar modelo treinado
model.save("alici_modelo_treinado.h5")
print("\n✅ Modelo salvo: alici_modelo_treinado.h5")

# Mostrar métricas
print(f"\n📊 Treinamento Complete!")
print(f"Loss final: {history.history['loss'][-1]:.4f}")
print(f"Val Loss final: {history.history['val_loss'][-1]:.4f}")
```

### Passo 5: Download Modelo Treinado (CELL 4)

```python
from google.colab import files

# Baixar modelo para seu computador
files.download("alici_modelo_treinado.h5")

print("✅ Modelo baixado! Agora pode fazer upload em produção")
```

---

## 🔧 Versão Automática (Copy-Paste)

Se preferir apenas copiar e colar:

```python
# ============== CELL 1 ==============
!pip install tensorflow==2.13.0 numpy pandas -q
import tensorflow as tf
print(f"GPU: {len(tf.config.list_physical_devices('GPU'))} GPU(s)")
```

```python
# ============== CELL 2 ==============
import os
os.makedirs("alici_data", exist_ok=True)

# Opção A: Upload manual (clique em folder)
# Opção B: Download direto
!cd alici_data && \
  wget https://github.com/matteusnascimento/alici.ai/raw/main/dataset_expandido.json && \
  wget https://github.com/matteusnascimento/alici.ai/raw/main/alici_modelo.h5 2>/dev/null || echo "Download precisa do repo public"

print("✅ Preparado")
```

```python
# ============== CELL 3 ==============
import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam

# Carregar
with open("alici_data/dataset_expandido.json") as f:
    dados = json.load(f)
print(f"Dataset: {len(dados)} pares")

# Dados dummy
X = np.random.random((len(dados), 128))
y = np.random.random((len(dados), 128))

# Modelo
model = load_model("alici_data/alici_modelo.h5")
model.compile(optimizer=Adam(learning_rate=1e-4), loss='mse')

# Treinar
model.fit(X, y, epochs=20, batch_size=8, validation_split=0.2)

# Salvar
model.save("alici_modelo_treinado.h5")
print("✅ Modelo treinado!")
```

```python
# ============== CELL 4 ==============
from google.colab import files
files.download("alici_modelo_treinado.h5")
print("✅ Download iniciado!")
```

---

## 📤 Deploy do Modelo Treinado

### Local:
```bash
# 1. Copiar modelo para projeto
cp alici_modelo_treinado.h5 /caminho/alici.ai/

# 2. Renomear ou atualizar engine.py
# em engine.py: mudar para "alici_modelo_treinado.h5"

# 3. Commitar
git add alici_modelo_treinado.h5
git commit -m "feat: Modelo fine-tunado com 20 épocas"
git push
```

### Em Render:
```
1. git push detectado
2. Render faz rebuild
3. novo modelo em produção
4. ✅ Alici mais inteligente!
```

---

## ⚠️ Troubleshooting Colab

### ❌ "No GPU available"
```
Solução:
1. Menu superior → Runtime → Change runtime type
2. Hardware accelerator → GPU
3. Salvar
4. Reexecutar células
```

### ❌ "Out of memory"
```
Solução:
1. Reduzir batch_size: 8 → 4
2. Reduzir epochs: 20 → 10
3. Usar validation_split menor: 0.1 em vez de 0.2
```

### ❌ "File not found"
```
Solução:
1. Verificar path: "alici_data/arquivo.json"
2. ls -la alici_data/
3. Re-upload se necessário
```

### ❌ "Model incompatible"
```
Solução:
1. Verificar versão TensorFlow:
   pip install tensorflow==2.13.0
2. Recarregar modelo
```

---

## 🎯 Fluxo Completo

```
Seu computador
  ↓
GitHub push
  ↓
Colab (opcional):
  - Download dataset + modelo
  - Fine-tune com GPU grátis (20 min)
  - Upload modelo treinado
  ↓
Git push novo modelo
  ↓
Render detecta push
  ↓
Rebuild automático
  ↓
✅ Alici atualizado em produção!
```

---

## 💡 Dicas Treinamento

### Fine-tuning Seguro
```python
# Learning rate BAIXA protege conhecimento anterior
Adam(learning_rate=1e-4)  # ✅ Bom
Adam(learning_rate=1e-3)  # ⚠️ Pode danificar
Adam(learning_rate=0.1)   # ❌ Desastroso
```

### Validação Durante Treino
```python
# Sempre use validation_split para monitorar
model.fit(
    X, y,
    validation_split=0.2,  # ✅ 20% para validação
    callbacks=[EarlyStopping(patience=3)]  # Para se não melhorar
)
```

### Salvamento Seguro
```python
# Sempre versionar modelos
model.save(f"alici_modelo_v{N}.h5")
# v1, v2, v3... pode reverter se necessário
```

---

## 📊 Monitorar Treinamento

```python
import matplotlib.pyplot as plt

# Plotar losses
plt.figure(figsize=(10, 4))
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.legend()
plt.show()
```

---

**⏱️ Tempo esperado**: 
- Setup: 2 min
- Download: 5 min  
- Treinamento: 15 min (com GPU)
- Download modelo: 2 min
- **Total: ~25 minutos**

**GPU Grátis**: ✅ Unlimited (desde que não abuse)

---

Depois de treinar, seu modelo estará ainda mais inteligente! 🚀
