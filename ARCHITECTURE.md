# 🧠 Arquitetura ALICI - Neon + Hugging Face

## 📊 Componentes Principais

### 🗄️ **Neon PostgreSQL** - Banco de Dados
**Propósito:** Armazenamento persistente de dados
- ✅ Memória (perguntas e respostas aprendidas)
- ✅ Usuários (autenticação)
- ✅ Histórico de conversas
- ✅ Confidence scores

### 🤖 **Hugging Face** - Modelos de IA
**Propósito:** Processamento de linguagem natural
- ✅ Transformers (modelos pré-treinados)
- ✅ Datasets (dados de treino)
- ✅ Tokenizers (processamento de texto)
- ✅ Fine-tuning personalizado

## 🔄 Como trabalham juntos

```
USUÁRIO: "qual a capital do Brasil?"
    ↓
┌─────────────────────────────────┐
│  ENGINE (engine.py)             │
│  1. Identidade                  │
│  2. Memória (NEON) ←─────────┐  │
│  3. Regras locais             │  │
│  4. Modelo IA (Hugging Face)  │  │
│  5. Web search                │  │
└─────────────────────────────────┘
    ↓                             ↑
RESPOSTA: "Brasília"              │
    ↓                             │
APRENDE e SALVA no NEON ──────────┘
```

## 🚀 Setup Completo

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```
Isso instala **tudo**:
- FastAPI + Uvicorn (web)
- PostgreSQL (psycopg2-binary) 
- Hugging Face (transformers, datasets)
- TensorFlow (modelos neurais)
- Torch (PyTorch)

### 2. Configurar Neon (Storage)
```bash
# .env
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### 3. Criar tabelas
```bash
python init_db.py
```

### 4. (Opcional) Treinar modelos Hugging Face
```bash
# Download de datasets
python download_datasets.py

# Treinar modelo customizado
python train_llm.py
```

### 5. Executar ALICI
```bash
python main.py
```

## 📦 Arquivos por Componente

### Neon (Database)
- `database.py` - CRUD operations
- `init_db.py` - Criar tabelas
- `test_db.py` - Testar conexão

### Hugging Face (AI)
- `train_llm.py` - Treinar modelos
- `download_datasets.py` - Baixar dados
- `engine.py` - Carregar e usar modelos

### Core ALICI
- `main.py` - Entrypoint
- `alici_api/app.py` - FastAPI routes
- `resposta.py` - Regras locais
- `identidade.py` - Identidade fixa
- `sistema_emocoes.py` - Emoções

## 💡 Quando usar cada um?

| Situação | Usa | Motivo |
|----------|-----|--------|
| "Quem é você?" | Identidade (fixo) | Resposta instantânea |
| "Já perguntei isso" | Neon (SELECT) | Memória persistente |
| "2+2?" | Regras locais | Pattern matching |
| "Analise este texto" | Hugging Face | NLP avançado |
| "Notícias de hoje" | Web Search | Dados em tempo real |

## ⚠️ Importante

**TODOS os componentes trabalham juntos em ALICI:**

- 🗄️ **Neon** = Database (armazenamento persistente)
- 🤖 **Hugging Face** = IA (processamento de linguagem)
- 🧠 **TensorFlow** = Modelos neurais (opcional)
- 🔍 **Web Search** = Dados em tempo real
- 📝 **Regras Locais** = Respostas rápidas

## 🎯 Fluxo Completo

1. **Pergunta chega** → engine.py
2. **Verifica identidade** → identidade.py (instantâneo)
3. **Busca na memória** → database.py → **Neon PostgreSQL**
4. **Tenta regras locais** → resposta.py (260+ padrões)
5. **Usa modelos IA** → **Hugging Face** (se necessário)
6. **Busca na web** → web_search.py (se necessário)
7. **Salva no banco** → **Neon PostgreSQL** (aprendizado)

---

**Resumo:** 
- 🗄️ **Neon** = Onde os dados ficam salvos
- 🤖 **Hugging Face** = Como a IA processa linguagem
- 🚀 **Juntos** = ALICI™ completo e inteligente
