# 🧠 Machine Learning no ALICI

## 📊 Arquitetura de Dados

O ALICI usa **dois sistemas complementares**:

### 1. 🗄️ Neon PostgreSQL (Storage)
**Função:** Armazenamento de dados estruturados
- ✅ Memória de conversas (tabela `memoria`)
- ✅ Usuários e autenticação (tabela `users`)
- ✅ Histórico de chat (tabela `history`)
- ✅ Confidence scores

**Por que Neon?**
- Serverless PostgreSQL
- Scale-to-zero
- Grátis até 3GB
- Integração fácil

### 2. 🤖 Hugging Face (ML/NLP)
**Função:** Processamento de linguagem natural
- ✅ Modelos de transformers
- ✅ Tokenização
- ✅ Embeddings
- ✅ Datasets de treino

**Casos de uso:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# Gerar respostas mais sofisticadas
model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")
```

---

## 🔄 Fluxo Completo

```
Usuário faz pergunta
    ↓
┌─────────────────────────┐
│ 1. Engine (engine.py)   │ → Decisão inteligente
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ 2. Neon PostgreSQL      │ → Busca na memória
│    SELECT memoria       │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ 3. Hugging Face         │ → Processa com NLP
│    Transformers         │    (se necessário)
└─────────────────────────┘
    ↓
Resposta gerada
    ↓
┌─────────────────────────┐
│ 4. Neon PostgreSQL      │ → Salva aprendizado
│    INSERT/UPDATE        │
└─────────────────────────┘
```

---

## 📦 Dependências Completas

```bash
# Instalar tudo
pip install -r requirements.txt
```

**Inclui:**
- `psycopg2-binary` - Conexão PostgreSQL/Neon
- `transformers` - Modelos Hugging Face
- `torch` - Backend PyTorch
- `datasets` - Datasets para treino
- `tensorflow` - Modelos TensorFlow (opcional)
- `fastapi` - API backend
- `requests` - Web search

---

## 🚀 Setup Completo

### 1. Neon (Banco de Dados)
```bash
# 1. Crie conta: https://neon.tech
# 2. Copie DATABASE_URL
# 3. Configure .env
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb

# 4. Crie tabelas
python init_db.py
```

### 2. Hugging Face (Modelos)
```bash
# Modelos baixam automaticamente ao usar
# Cache em: ~/.cache/huggingface/

# Opcional - login para modelos privados:
huggingface-cli login
```

### 3. Executar
```bash
python main.py
```

---

## 💾 Onde cada coisa fica?

| Dado | Armazenado em | Tecnologia |
|------|---------------|------------|
| Perguntas/respostas | Neon PostgreSQL | SQL |
| Usuários | Neon PostgreSQL | SQL |
| Histórico chat | Neon PostgreSQL | SQL |
| Modelos NLP | Cache local | Hugging Face |
| Embeddings | Memória RAM | Transformers |
| Tokenizer | Cache local | Hugging Face |

---

## 🎯 Resumo

- **Neon** = Onde os DADOS ficam salvos (banco)
- **Hugging Face** = Como a IA PENSA (modelos)

Ambos são essenciais! 🚀
