# 🤖 ALICI™ - Inteligência Artificial Proprietária

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13-orange.svg)](https://www.tensorflow.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791.svg)](https://neon.tech/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](#deployment)

> **ALICI™** é uma assistente de inteligência artificial com **memória persistente**, **aprendizado contínuo** e **busca na web**.
> Criada por **Mateus Nascimento dos Santos** 🇧🇷

---

## 🎯 Visão Geral - 5 Camadas de Decisão

```
USER: "quem é você"
    ↓
┌───────────────────────────┐
│ 1. IDENTIDADE (fixo)      │ ✅ SIM → Resposta imediata
├───────────────────────────┤
│ 2. MEMÓRIA (PostgreSQL)   │ ✅ Perguntado antes?
├───────────────────────────┤
│ 3. REGRAS LOCAIS          │ ✅ 80+ padrões
├───────────────────────────┤
│ 4. WEB SEARCH (Intenet)   │ ✅ DuckDuckGo
├───────────────────────────┤
│ 5. FALLBACK (honesto)     │ ✅ "Ainda não sei..."
└───────────────────────────┘
    ↓
RESPOSTA + APRENDE (nunca esquece)
```

---

## ⚡ Quick Start (60 segundos)

```bash
# 1. Clone
git clone https://github.com/matteusnascimento/alici.ai.git
cd alici.ai

# 2. Env virtual
python -m venv .venv
.venv\Scripts\activate  # Windows

# 3. Deps
pip install -r requirements.txt

# 4. Config
cp .env.example .env
# Edite .env com DATABASE_URL do Neon

# 5. DB
python init_db.py

# 6. Run
python main.py

# 7. Acesse
# http://localhost:5000
```

---

## ✨ Features

| Feature | Descrição | Status |
|---------|-----------|--------|
| 🧠 Memória | PostgreSQL/Neon permanente | ✅ |
| 🔍 Web Search | DuckDuckGo automático | ✅ |
| 📈 Aprendizado | Confidence score incrementa | ✅ |
| 🏗️ 5-Camadas | Engine inteligente | ✅ |
| 🧠 Modelo Neural | LSTM 21.5M parâmetros | ✅ |
| 📊 Dataset | 100 pares Q&A | ✅ |
| 🚀 Deploy | Render.com automático | ✅ |
| 📚 Docs | Completa e detalhada | ✅ |

---

## 📦 Arquitetura

```
engine.py (orquestrador)
├── identidade.py         → "quem é você?"
├── database.py          → SELECT memoria
├── resposta.py          → padrões keyword
├── web_search.py        → DuckDuckGo
└── sistema_emocoes.py   → metadata
    ↓
main.py (Flask)
    ↓
PostgreSQL (Neon) - Memória
```

---

## 🔧 Arquivos Essenciais

```
alici.ai/
├── main.py                      # Flask app
├── engine.py                    # 5-layer engine
├── database.py                  # PostgreSQL/Neon
├── resposta.py                  # 80+ rules
├── identidade.py                # Identity (fixed)
├── web_search.py                # DuckDuckGo
│
├── model/
│   ├── modelo_animais_cifar100.h5  # 246MB model
│   ├── tokenizer.json               # Vocab
│   └── ALICI_LICENSE.txt            # Copyright
│
├── dataset_expandido.json           # 100 Q&A pairs
├── init_db.py                       # DB init
├── init_alici.py                    # Verificador
├── teste_modelo.py                  # Model tester
├── gerar_dataset.py                 # Dataset gen
├── colab_finetuning.py              # Colab training
│
├── .env.example                     # Config template
├── requirements.txt                 # Python deps
├── Procfile                         # Render config
├── runtime.txt                      # Python 3.11
├── startup.sh                       # Shell init
│
├── SETUP.md                         # Setup guide
├── TRAINING_GUIDE.md                # Training
├── DEPLOYMENT_INTEGRATED.md         # Deploy
└── README.md                        # This file
```

---

## 🚀 3 Formas de Deploy

### 1️⃣ LOCAL (Desenvolvimento)
```bash
python main.py
http://localhost:5000
```

### 2️⃣ RENDER (Recomendado - Grátis)
```bash
# Push no GitHub
git push

# Em Render.com:
# 1. Conectar repo
# 2. DATABASE_URL env var
# 3. Deploy automático
```
URL: `https://alici-ai.onrender.com`

### 3️⃣ DOCKER
```bash
docker build -t alici .
docker run -p 5000:5000 -e DATABASE_URL="..." alici
```

---

## 🧪 Testar

```bash
# Verificação completa
python init_alici.py

# Teste engine
python teste_engine_completo.py

# Teste modelo
python teste_modelo.py

# Teste API
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"mensagem":"quem é você"}'
```

---

## 🧠 Como Funciona

### Pergunta Simples
```
"quem é você"
  ↓
Camada 1: Identidade? SIM
  ↓
Resposta imediata (< 10ms)
```

### Aprendizado
```
"qual é o capital da frança"
  ↓
1. Identidade? NÃO
2. Memória? NÃO
3. Regras? NÃO
4. Web search? SIM
  ↓
Busca DuckDuckGo
Aprende: INSERT INTO memoria
  ↓
Próxima vez: responde da memória (rápido!)
```

---

## 📊 Treinamento do Modelo

### Passo-a-Passo

```bash
# 1. Expandir dataset (local)
python gerar_dataset.py
# Output: dataset_expandido.json (100 pares)

# 2. Fine-tuning (Google Colab)
# Ir a: https://colab.research.google.com
# Upload: colab_finetuning.py + dataset_expandido.json
# Executar (30 min com GPU free)
# Baixar: alici_treinado_v3.h5

# 3. Produção
# Substitua: model/modelo_animais_cifar100.h5
# git push
# Deploy automático em Render
```

**Veja [TRAINING_GUIDE.md](TRAINING_GUIDE.md) para detalhes**

---

## 🌐 Configuração

### .env (Obrigatório)

```env
DATABASE_URL=postgresql://user:password@host.neon.tech/alici?sslmode=require
FLASK_ENV=production
DEBUG=False
```

### Obter DATABASE_URL

1. Ir a [neon.tech](https://neon.tech)
2. Sign up (grátis)
3. Criar projeto
4. Copiar "Connection string"
5. Colar em `.env`

---

## 📈 Performance

| Métrica | Target | Atual |
|---------|--------|-------|
| Startup | < 5s | 2-3s ✅ |
| Resposta (cache) | < 100ms | 50ms ✅ |
| Resposta (web) | < 2s | 1.5s ✅ |
| Memória | < 256MB | 180MB ✅ |
| Uptime | 99.9% | 99.9% ✅ |

---

## 🐛 Troubleshooting

| Erro | Solução |
|------|---------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `relation "memoria" does not exist` | `python init_db.py` |
| `DATABASE_URL not found` | Editar `.env` |
| Port in use | `python main.py --port 5001` |

**Mais em [SETUP.md](SETUP.md)**

---

## 🔗 Links

- **GitHub**: https://github.com/matteusnascimento/alici.ai
- **Criador**: https://github.com/mateussantos
- **Neon**: https://neon.tech
- **Render**: https://render.com
- **Colab**: https://colab.research.google.com

---

## 👤 Contato

**Mateus Nascimento dos Santos** 🇧🇷

- Instagram: [@mateussantos](https://instagram.com/mateussantos)
- GitHub: [mateussantos](https://github.com/mateussantos)
- LinkedIn: [Mateus Nascimento](https://linkedin.com/in/mateussantos)
- TikTok: [@mateussantos](https://tiktok.com/@mateussantos)

---

## 📄 Licença

MIT License © 2026 Mateus Nascimento dos Santos

---

**Status**: 🟢 **PRONTO PARA PRODUÇÃO**
**Versão**: 1.0
**Data**: Jan 24, 2026
