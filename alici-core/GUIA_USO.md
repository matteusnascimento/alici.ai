"""
🎓 GUIA DE USO - ALICI™ CORE DEFINITIVO
Arquitetura Multimodal + Neon + Render
"""

# 📚 ÍNDICE
# 1. Estrutura do Projeto
# 2. Setup Local
# 3. Treinamento
# 4. API & Deployment
# 5. Integração com Colab


## 1. 📁 ESTRUTURA DO PROJETO

alici-core/
├── database/
│   ├── __init__.py
│   └── neon.py              # 🗄️ Conexão com Neon + Logging
│
├── models/
│   ├── __init__.py
│   ├── image_branch.py      # 🖼️ Ramo CNN para imagens
│   ├── text_branch.py       # 📝 Ramo LSTM para texto
│   ├── audio_branch.py      # 🎵 Ramo Dense para áudio
│   └── multimodal_model.py  # 🔀 Fusão dos 3 ramos
│
├── training/
│   ├── __init__.py
│   └── trainer.py           # 🎓 Orquestra treinamento
│
├── api/
│   ├── __init__.py
│   └── main.py              # ⚡ FastAPI para Render
│
├── .env.example             # 🔐 Template de variáveis
└── Procfile                 # 🚀 Deploy Render


## 2. 🔧 SETUP LOCAL

### 2.1 Instalação

```bash
# Clone ou navegue até o projeto
cd alici-core

# Crie um virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Instale dependências
pip install -r ../requirements.txt

# Configure o banco de dados
cp .env.example .env
# Edite .env com sua DATABASE_URL do Neon
```

### 2.2 Teste de Conexão

```bash
# Teste conexão com Neon
python database/neon.py
# Deve imprimir: ✅ Conexão OK, ✅ Tabelas criadas com sucesso!

# Teste ramos isolados
python models/image_branch.py
python models/text_branch.py
python models/audio_branch.py

# Teste modelo multimodal
python models/multimodal_model.py
# Output: ✅ Output shape: (1, 256)
```


## 3. 🎓 TREINAMENTO

### 3.1 Local (Teste)

```bash
python training/trainer.py
# Treina com dados dummy por 5 épocas
# Salva como alici_core_test.h5
# Loga métricas no Neon
```

### 3.2 Com Dados Reais

```python
from training.trainer import TrainerMultimodal
import numpy as np

# Carregar seus dados
# X_train = [imagens, textos, áudios]
# y_train = labels one-hot encoded (256 classes)

trainer = TrainerMultimodal(
    model_name="alici_core_v1",
    learning_rate=1e-4  # Fine-tuning
)

trainer.compilar_modelo(num_classes=256)

trainer.treinar(
    X_train, y_train,
    X_val=X_val, y_val=y_val,
    epochs=50,
    batch_size=32
)

trainer.salvar_modelo("alici_core.h5")
```

### 3.3 No Google Colab (Recomendado)

```python
# 1. Upload do arquivo colab_finetuning.py
# 2. Crie os datasets (JSON para texto, WAV para áudio, PNG para imagens)
# 3. Execute menu_principal() e selecione opção multimodal
# 4. Modelo será treinado com GPU
# 5. Baixe alici_core.h5 após treinamento
# 6. Faça upload para repositório / Render
```

### 3.4 Monitorar Logs no Neon

```bash
# Após treinamento, consulte os logs:

```python
from database.neon import db

# Ver últimos 20 logs
logs = db.obter_logs_treino(modelo="alici_core_v1", limit=20)
for log in logs:
    print(f"Epoch {log['epoch']}: Loss={log['loss']:.4f}, Acc={log['accuracy']:.4f}")
```


## 4. ⚡ API & DEPLOYMENT

### 4.1 Executar Localmente

```bash
cd api

# Opção 1: Direto com Uvicorn
uvicorn main:app --reload

# Opção 2: Com Gunicorn (production-like)
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# API estará em http://localhost:8000
# Docs interativa: http://localhost:8000/docs
```

### 4.2 Endpoints

```bash
# Status
GET /               # Status geral
GET /health         # Health check (Render)
GET /status         # Status detalhado

# Inferência
POST /predict
  - image: arquivo PNG/JPG (opcional)
  - text: string (opcional)
  - audio: arquivo WAV (opcional)
  Retorna: {"prediction": {"class": 42, "confidence": 0.98}, "tempo_ms": 125}

# Logs & Modelos
GET /logs/treino?modelo=alici_core&limit=100
GET /modelos

# Admin
POST /reload-model  # Recarregar modelo após novo treino
```

### 4.3 Deploy no Render

```bash
# 1. Faça push para GitHub (com alici_core.h5 via LFS ou gitignore)
git add .
git commit -m "ALICI Core v1.0"
git push

# 2. No painel Render:
# - New Web Service
# - Connect repositório
# - Root directory: / (ou alici-core se quiser)
# - Build command: pip install -r requirements.txt
# - Start command: gunicorn alici_core.api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
# - Add env var: DATABASE_URL = seu_neon_url
# - Deploy

# 3. API estará online em https://seu-dominio.onrender.com
```

### 4.4 Testar API em Produção

```bash
# Status
curl https://seu-dominio.onrender.com/

# Fazer predição (com arquivo)
curl -X POST https://seu-dominio.onrender.com/predict \
  -F "image=@imagem.png" \
  -F "text=olá mundo" \
  -F "audio=@audio.wav"

# Buscar logs
curl https://seu-dominio.onrender.com/logs/treino?limite=10
```


## 5. 🔗 INTEGRAÇÃO COLAB + RENDER

### 5.1 Fluxo Completo

```
Google Colab (GPU)
  ↓
  [colab_finetuning.py] - treina modelo
  ↓
  Download: alici_core.h5
  ↓
  Upload para GitHub (ou Render assets)
  ↓
Render (Production)
  ↓
  [api/main.py] - carrega e faz predições
  ↓
  /predict endpoint (REST API)
```

### 5.2 Automatizar Upload do Modelo

```python
# No Colab, após treinamento:

from google.colab import files
import subprocess

# Comprimir modelo
subprocess.run(["gzip", "alici_core.h5"])

# Fazer download
files.download("alici_core.h5.gz")

# Depois faça upload para GitHub via git ou interface
```

### 5.3 Versioning de Modelos

```python
# Manter histórico no Neon

versao_atual = "1.0"
modelos = db.obter_modelos()

# Sempre a versão mais recente com melhor accuracy
melhor_modelo = max(modelos, key=lambda x: x['accuracy'])
print(f"Usando {melhor_modelo['nome']} v{melhor_modelo['versao']}")
```


## 🎯 PRÓXIMOS PASSOS

1. ✅ Modelo multimodal arquitetura
2. ✅ Neon logging
3. ✅ FastAPI deployment
4. 🔜 Autenticação JWT (auth.py)
5. 🔜 Memória persistente por usuário
6. 🔜 RAG (Retrieval Augmented Generation)
7. 🔜 Agentes autônomos


## 📞 SUPORTE

- Docs interativa: /docs (local ou Render)
- GitHub Issues: [seu-repo]/issues
- Comunidade: Discord/Telegram


---

**🤖 ALICI™ Core v1.0**
*Arquitetura profissional, escalável, pronta para produção*
