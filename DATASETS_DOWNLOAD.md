# 🚀 PIPELINE PROFISSIONAL DE TREINO DE LLM

**Código usado por startups e empresas que treinam modelos grandes.**

Script completo para:
- ✅ Baixar datasets de alta qualidade
- ✅ Limpar e processar dados
- ✅ Remover duplicatas
- ✅ Criar tokenizer
- ✅ Treinar modelo LLM
- ✅ Otimizar para GPU

## 📊 Datasets Inclusos

| Dataset | Items | Tamanho Est. | Descrição |
|---------|-------|-------------|-----------|
| **OpenWebText** | 500k | ~2-3 GB | Web de alta qualidade (similar a WebText do GPT-2) |
| **Wikipedia PT** | 200k | ~300-500 MB | Enciclopédia em português |
| **BookCorpus** | 200k | ~500-800 MB | Livros de qualidade (Project Gutenberg) |
| **The Pile** | 300k | ~1-2 GB | Corpus massivo e diverso (EleutherAI) |
| **TOTAL** | 1.2M | **~4-6 GB** | Dados para treino robusto |

## ⚙️ Pré-requisitos

```bash
# Instalar dependências
pip install -r requirements.txt

# Ou instale especificamente:
pip install datasets transformers torch tqdm tokenizers

# (Opcional) Para GPU NVIDIA:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 🏃 Como Usar

### Passo 1: Baixar Datasets
```bash
python download_datasets.py
```

Isso:
- ✅ Baixa 4 datasets (1.2M items)
- ✅ Limpa e remove HTML
- ✅ Remove duplicatas
- ✅ Normaliza encoding
- ✅ Cria arquivo final para treino
- ✅ Cria tokenizer BPE

**Tempo**: 4-6 horas (depende da internet)

**Saída**:
```
datasets_texto/
├── openwebtext.txt
├── wikipedia_pt.txt
├── bookcorpus.txt
└── pile.txt

datasets_processado/
├── dataset_final.txt    (mesclado, dedupli cado)
└── tokenizer.json       (BPE 50k vocab)
```

### Passo 2: Treinar Modelo LLM
```bash
python train_llm.py
```

Isso:
- ✅ Carrega GPT-2 como modelo base
- ✅ Configura dataset para treino
- ✅ Detecta GPU (CUDA) automaticamente
- ✅ Inicia treino com otimizações
- ✅ Salva checkpoints
- ✅ Salva modelo final

**Tempo**: Varia conforme GPU
- Com GPU RTX 3090: ~24 horas
- Com GPU RTX 4090: ~12 horas
- Sem GPU (CPU): ~1 semana

**Saída**:
```
modelo_treinado/
├── checkpoint-500/
├── checkpoint-1000/
└── final_model/          (modelo pronto para usar)

## 💡 Dicas Profissionais

### 1️⃣ Começar Pequeno (Para Testes)
```python
# Em download_datasets.py, reduzir items:
salvar_dataset(openweb.take(5_000), "openwebtext.txt")  # 5k ao invés de 500k
```

### 2️⃣ Usar Modelo Melhor que GPT-2
```python
# Em train_llm.py, trocar:
MODEL_NAME = "gpt2"
# Para:
MODEL_NAME = "EleutherAI/gpt-neo-1.3B"  # Modelo 1.3B (melhor)
MODEL_NAME = "meta-llama/Llama-2-7b"    # Llama 2 (necessita acesso)
```

### 3️⃣ Treinar com Sua Própria Mistura de Dados
```bash
# Após download_datasets.py, editar dataset_final.txt:
cat meus_dados.txt >> datasets_processado/dataset_final.txt

# Depois:
python train_llm.py
```

### 4️⃣ Usar Dados em Background
```bash
# Windows PowerShell (roda em background):
Start-Process python -ArgumentList "download_datasets.py" -NoNewWindow

# Linux/Mac:
nohup python download_datasets.py > download.log 2>&1 &
```

### 5️⃣ Monitorar Progresso
```bash
# Ver logs em tempo real:
tail -f logs/alici_*.log

# Ver tamanho de arquivos:
Get-ChildItem datasets_* -Recurse | ForEach-Object { Write-Host "$($_.FullName): $([Math]::Round($_.Length/1MB, 2)) MB" }
```

## 📊 Pipeline Completo

```
┌─────────────────────────────────────┐
│  download_datasets.py               │
│  ✅ Baixa 1.2M items               │
│  ✅ Limpa HTML                     │
│  ✅ Remove duplicatas              │
│  ✅ Normaliza encoding             │
│  ✅ Cria tokenizer BPE             │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  Saída: datasets_processado/        │
│  ✓ dataset_final.txt (limpo)       │
│  ✓ tokenizer.json (BPE 50k vocab)  │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  train_llm.py                       │
│  ✅ Carrega GPT-2                  │
│  ✅ Configura treino               │
│  ✅ Detecta GPU                    │
│  ✅ Treina modelo                  │
│  ✅ Salva checkpoints              │
└────────────┬────────────────────────┘
             │
             ↓
┌─────────────────────────────────────┐
│  Saída: modelo_treinado/            │
│  ✓ checkpoint-500/                 │
│  ✓ checkpoint-1000/                │
│  ✓ final_model/ (pronto!)          │
└─────────────────────────────────────┘
```

## 🔧 Usar Modelo Treinado

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Carregar
model = AutoModelForCausalLM.from_pretrained("modelo_treinado/final_model")
tokenizer = AutoTokenizer.from_pretrained("modelo_treinado/final_model")

# Gerar texto
input_ids = tokenizer.encode("Uma vez era", return_tensors="pt")
output = model.generate(input_ids, max_length=100, temperature=0.7)
texto = tokenizer.decode(output[0])

print(texto)
```

## 🎯 Próximos Passos

1. ✅ Baixar datasets: `python download_datasets.py`
2. ✅ Treinar modelo: `python train_llm.py`
3. 🔧 Avaliar performance
4. 🚀 Fazer fine-tune com dados específicos
5. 📈 Deploy em produção

## ⚠️ Troubleshooting

### "Connection timeout"
```bash
export HF_DATASETS_TIMEOUT=300
python download_datasets.py
```

### "Out of memory"
- Reduzir `BATCH_SIZE` em train_llm.py
- Usar modelo menor: `distilgpt2` ao invés de `gpt2`

### "CUDA out of memory"
```python
# Em train_llm.py:
BATCH_SIZE = 4  # reduzir de 8
# Ou:
fp16=True  # usar mixed precision
```

### Logs não aparecem
```bash
ls -la logs/  # verificar se logs existem
tail -f logs/alici_*.log  # mostrar em tempo real
```

## 📚 Referências

- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [The Pile Dataset](https://pile.eleuther.ai/)
- [PyTorch Training](https://pytorch.org/tutorials/)
- [Language Model Training Guide](https://huggingface.co/docs/transformers/training)

## 🎓 Por Que Esse Approach?

**Diversidade de dados**: Modelos fortes aprendem de múltiplas fontes
- OpenWebText: textos naturais da web
- Wikipedia: conhecimento estruturado
- Books: linguagem mais formal
- The Pile: corpus diverso

**Limpeza**: Remove HTML, duplicatas, lixo (= modelo melhor)

**Tokenizer próprio**: Otimizado para seu dataset

**GPU**: 10-100x mais rápido que CPU

## ✨ Resultado

Após este pipeline, você terá:
- 🧠 Um modelo LLM **funcional e treinado**
- 📊 Dados de qualidade processados
- ⚡ Modelo otimizado para inferência
- 🚀 Pronto para fine-tuning em domínios específicos
- 💾 Checkpoints para continuar treino

---

**Status**: ✅ Pronto!

Comece com: `python download_datasets.py` (4-6 horas)

Depois: `python train_llm.py` (12-24 horas com GPU)

