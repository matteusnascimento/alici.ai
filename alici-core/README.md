# 🤖 ALICI™ CORE v1.0

**Arquitetura Multimodal Profissional para Produção**

```
┌─────────────────────────────────────────────────┐
│         ALICI™ - CHATBOT PORTUGUÊS              │
│    Com IA Multimodal, Memória Persistente,      │
│         Avatar Holográfico & Render Deploy      │
└─────────────────────────────────────────────────┘
```

---

## ✨ Características

✅ **Arquitetura Multimodal**
- 🖼️ Ramo CNN para processamento de imagens
- 📝 Ramo LSTM para processamento de texto
- 🎵 Ramo Dense para processamento de áudio
- 🔀 Camada de Fusão com Concatenation

✅ **Persistência em Produção**
- 🗄️ PostgreSQL/Neon para logs de treinamento
- 📊 Métricas automáticas de cada época
- 📈 Dashboard de histórico de modelos
- 🔍 Rastreabilidade completa

✅ **API Profissional**
- ⚡ FastAPI com Uvicorn
- 🚀 Pronto para Render deployment
- 📋 Documentação interativa (Swagger)
- 🔐 Preparado para autenticação JWT

✅ **Treinamento Flexível**
- 💾 Trainer centralizado reutilizável
- 🎓 Early stopping e reduce LR automáticos
- 🐍 Compatível com Google Colab (GPU)
- 📦 Salva modelos versionados no Neon

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                   API FastAPI                       │
│  (POST /predict, GET /status, GET /logs/treino)    │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
    ┌───▼──────────┐   ┌─────────▼───┐
    │  Modelo      │   │  Neon DB    │
    │  Multimodal  │   │  (Logs)     │
    └───┬──────────┘   └─────────────┘
        │
    ┌───┴──────────────────┬──────────────┐
    │                      │              │
┌───▼────────┐ ┌──────────▼──┐ ┌────────▼───┐
│   Image    │ │     Text    │ │    Audio   │
│   Branch   │ │    Branch   │ │   Branch   │
│   (CNN)    │ │   (LSTM)    │ │   (Dense)  │
└──────────┬─┘ └──────────┬──┘ └────────┬───┘
           │              │             │
        ┌──▼──────────────▼─────────────▼──┐
        │      Concatenation + Fusion      │
        │   (Dense → Softmax → Output)     │
        └──────────────────────────────────┘
```

---

## 📁 Estrutura

```
alici-core/
│
├── 🗄️ database/
│   ├── __init__.py
│   └── neon.py                  # Conexão + Logging
│
├── 🧠 models/
│   ├── __init__.py
│   ├── image_branch.py          # CNN (32x32x3 → 128)
│   ├── text_branch.py           # LSTM (50 → 128)
│   ├── audio_branch.py          # Dense (13 → 128)
│   └── multimodal_model.py      # Fusão (384 → 256)
│
├── 🎓 training/
│   ├── __init__.py
│   └── trainer.py               # Orquestra + Logging
│
├── ⚡ api/
│   ├── __init__.py
│   └── main.py                  # FastAPI + Render
│
├── 🧪 teste_completo.py         # Validação da arquitetura
├── 📖 GUIA_USO.md               # Guia completo
└── .env.example                 # Variáveis de ambiente

```

---

## 🚀 Quick Start

### 1. Setup Local

```bash
cd alici-core
python -m venv venv
source venv/bin/activate

pip install -r ../requirements.txt
cp .env.example .env
# Edite .env com sua DATABASE_URL do Neon
```

### 2. Teste da Arquitetura

```bash
python teste_completo.py
# Output: ✅ TUDO FUNCIONANDO!
```

### 3. Treinar Modelo

```bash
python training/trainer.py
# Treina 5 épocas com dados dummy
# Salva como alici_core_test.h5
# Loga métricas no Neon
```

### 4. Executar API

```bash
cd api
uvicorn main:app --reload
# Acesse http://localhost:8000/docs
```

---

## 📊 Componentes Detalhados

### 🗄️ Database (Neon)

```python
from database.neon import db

# Criar tabelas
db.criar_tabelas()

# Log de treinamento
db.log_treino(
    modelo="alici_core",
    tipo_dado="multimodal",
    epoch=1,
    loss=0.45,
    accuracy=0.92
)

# Consultar logs
logs = db.obter_logs_treino(modelo="alici_core", limit=50)
```

**Tabelas Criadas:**
- `treino_logs` - Métricas por época
- `modelos` - Histórico de modelos
- `predicoes` - Log de predições
- `usuarios` - Para futuro (autenticação)

### 🧠 Modelos Multimodais

Cada ramo é independente:

```python
from models.image_branch import image_branch
from models.text_branch import text_branch
from models.audio_branch import audio_branch

# Cada um retorna (input_tensor, output_features)
img_in, img_feat = image_branch(input_shape=(32,32,3))
txt_in, txt_feat = text_branch(vocab_size=5000)
aud_in, aud_feat = audio_branch(input_dim=13)
```

**Outputs dos ramos:**
- Image Branch: 128 features
- Text Branch: 128 features
- Audio Branch: 128 features
- **Total após fusão:** 256 classes (softmax)

### 🎓 Trainer Centralizado

```python
from training.trainer import TrainerMultimodal

trainer = TrainerMultimodal(
    model_name="alici_core_v1",
    learning_rate=1e-4  # Fine-tuning
)

trainer.compilar_modelo(num_classes=256)

trainer.treinar(
    X_train=[imgs, textos, áudios],
    y_train=labels_onehot,
    epochs=50,
    batch_size=32
)

trainer.salvar_modelo("alici_core.h5")
```

**Features:**
- Early Stopping (patience=5)
- Reduce LR on Plateau
- Logging automático no Neon
- Model checkpointing

### ⚡ API FastAPI

```python
from fastapi import FastAPI

# Endpoints principais
GET  /                  # Status
GET  /health            # Health check (Render)
GET  /status            # Status detalhado
POST /predict           # Inferência multimodal
GET  /logs/treino       # Histórico
GET  /modelos           # Modelos registrados
POST /reload-model      # Recarregar após treino
```

**Teste Local:**

```bash
curl http://localhost:8000/status

curl -X POST http://localhost:8000/predict \
  -F "image=@foto.png" \
  -F "text=olá mundo" \
  -F "audio=@audio.wav"
```

---

## 🚀 Deploy no Render

### 1. Preparação

```bash
# Certifique-se de que alici_core.h5 existe
# (ou será criado no primeiro treino)

git add .
git commit -m "ALICI Core v1.0"
git push
```

### 2. No Painel Render

```
New Web Service
├─ Connect GitHub Repo
├─ Build: pip install -r requirements.txt
├─ Start: gunicorn alici_core.api.main:app --workers 4 \
│         --worker-class uvicorn.workers.UvicornWorker
├─ Environment Variables:
│  └─ DATABASE_URL = postgresql://...
└─ Deploy
```

### 3. Testar em Produção

```bash
# Status
curl https://seu-dominio.onrender.com/

# Logs
curl https://seu-dominio.onrender.com/logs/treino?limit=10
```

---

## 🔗 Integração com Colab

Use `colab_finetuning.py` para treinar com GPU:

```python
# No Colab
from colab_finetuning import menu_principal

menu_principal()
# Escolha opção 7: Treinar Multimodal (Texto + Áudio + Imagens)
# Baixe alici_core.h5 após treino
# Faça upload para Render
```

**Fluxo:**
```
Colab (treino com GPU)
    ↓ alici_core.h5
    ↓
GitHub
    ↓
Render (API em produção)
    ↓
/predict endpoint
```

---

## 📈 Métricas & Monitoramento

Todos os treinos são logados no Neon:

```python
from database.neon import db

# Ver histórico de uma modelo
logs = db.obter_logs_treino(modelo="alici_core_v1")

# Análise
for log in logs:
    print(f"Epoch {log['epoch']:3d} | "
          f"Loss: {log['loss']:.4f} | "
          f"Acc: {log['accuracy']:.4f} | "
          f"Val Acc: {log['val_accuracy']:.4f}")

# Registrar novo modelo
db.registrar_modelo(
    nome="alici_core_v2",
    versao="2.0",
    tipo="multimodal",
    tamanho_mb=152.5,
    accuracy=0.945,
    parameters=2847504
)
```

---

## ✅ Checklist de Produção

- [x] Arquitetura multimodal funcional
- [x] Neon database integrado
- [x] Logging de métricas automático
- [x] FastAPI com Swagger
- [x] Pronto para Render
- [x] Modelo versionado
- [ ] Autenticação JWT
- [ ] Memória persistente por usuário
- [ ] RAG (Retrieval Augmented Generation)
- [ ] Agentes autônomos

---

## 🔐 Variáveis de Ambiente

Crie `.env` baseado em `.env.example`:

```bash
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/alici?sslmode=require
ENVIRONMENT=production
PORT=8000
LOG_LEVEL=INFO
```

---

## 📚 Documentação

- **[GUIA_USO.md](GUIA_USO.md)** - Tutorial completo
- **[/docs](http://localhost:8000/docs)** - Swagger interativo (local/Render)
- **[colab_finetuning.py](../colab_finetuning.py)** - Treino em Colab

---

## 🧪 Testes

```bash
# Teste completo da arquitetura
python teste_completo.py

# Teste individual dos ramos
python models/image_branch.py
python models/text_branch.py
python models/audio_branch.py
python models/multimodal_model.py

# Teste do trainer
python training/trainer.py

# Teste da API
python -m pytest api/
```

---

## 🤝 Contribuindo

```bash
# 1. Crie uma branch
git checkout -b feature/minha-feature

# 2. Faça as mudanças
# 3. Teste
python teste_completo.py

# 4. Commit
git add .
git commit -m "Add: minha feature"
git push origin feature/minha-feature

# 5. Pull Request
```

---

## 📞 Suporte

- **Documentação Swagger:** `/docs` no servidor
- **Issues:** GitHub Issues
- **Email:** [seu email]
- **Discord:** [seu discord]

---

## 📄 License

MIT License - Veja LICENSE para detalhes

---

## 🎯 Roadmap

```
v1.0 (✅ Atual)
├─ Multimodal architecture
├─ Neon logging
├─ FastAPI + Render
└─ Trainer centralizado

v1.1 (🔜 Próximo)
├─ JWT Authentication
├─ Per-user memory
└─ Vector embeddings

v2.0 (🚀 Futuro)
├─ RAG Integration
├─ Autonomous agents
├─ Voice synthesis
└─ Image generation
```

---

<div align="center">

**🤖 ALICI™ Core v1.0**

*Arquitetura Multimodal Profissional*

Made with ❤️ for Portuguese-speaking AI enthusiasts

[⭐ Star](#) · [🐛 Report Issue](#) · [📖 Docs](#)

</div>
