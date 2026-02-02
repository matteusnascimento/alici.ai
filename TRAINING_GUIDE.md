# 🎓 ALICI™ - Guia Completo de Treinamento

## 📋 Visão Geral

Este guia explica como treinar modelos personalizados para ALICI usando Google Colab com GPU gratuita.

---

## 🎯 Pipeline de Treinamento

```
1. Gerar Dataset      → gerar_dataset.py
         ↓
2. Upload para Colab  → dataset_expandido.json
         ↓
3. Fine-tuning        → colab_finetuning.py
         ↓
4. Download Modelo    → modelo.h5 + tokenizer.json
         ↓
5. Deploy Produção    → model/ folder
```

---

## 📊 Passo 1: Gerar Dataset

### Executar Localmente

```bash
python gerar_dataset.py
```

**Output:**
- `dataset_expandido.json` (100+ pares de Q&A)

### Estrutura do Dataset

```json
[
  {
    "pergunta": "Quem é você?",
    "resposta": "Sou ALICI, uma assistente de IA..."
  },
  {
    "pergunta": "Como você está?",
    "resposta": "Estou bem e pronta para ajudar!"
  }
]
```

### Customizar Dataset

Edite `gerar_dataset.py` para adicionar suas próprias perguntas e respostas:

```python
def adicionar_perguntas_customizadas():
    return [
        {
            "pergunta": "Sua pergunta aqui",
            "resposta": "Sua resposta aqui"
        }
    ]
```

---

## 🚀 Passo 2: Treinar no Google Colab

### 2.1 Preparar Colab

1. Acesse: https://colab.research.google.com
2. Criar novo notebook
3. **IMPORTANTE:** Ativar GPU gratuita
   - `Runtime` → `Change runtime type` → `GPU` → `Save`

### 2.2 Upload dos Arquivos

No Colab, upload:
- `colab_finetuning.py`
- `dataset_expandido.json`

### 2.3 Instalar Dependências

```python
!pip install tensorflow numpy
```

### 2.4 Executar Treinamento

```python
# Importar script
from colab_finetuning import pipeline_completo

# Treinar (30-60 min com GPU)
model, tokenizer, history = pipeline_completo()
```

**Saída esperada:**
```
✅ Dataset carregado: 100+ pares
✅ Tokenizer criado
✅ Modelo criado (parâmetros: ~2M)
🎯 Treinando... (50 épocas)
✅ Modelo salvo: alici_treinado.h5
```

### 2.5 Monitorar Treinamento

```python
import matplotlib.pyplot as plt

# Plot loss
plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='validation')
plt.legend()
plt.show()

# Plot accuracy
plt.plot(history.history['accuracy'], label='train')
plt.plot(history.history['val_accuracy'], label='validation')
plt.legend()
plt.show()
```

---

## 📥 Passo 3: Download e Deploy

### 3.1 Baixar Modelos

No Colab:
```python
from google.colab import files

# Baixar modelo
files.download('alici_treinado.h5')

# Baixar tokenizer
files.download('alici_treinado_tokenizer.json')
```

### 3.2 Mover para Produção

```bash
# Localmente
mv alici_treinado.h5 model/modelo_animais_cifar100.h5
mv alici_treinado_tokenizer.json model/tokenizer.json
```

### 3.3 Testar Modelo

```bash
python teste_modelo.py
```

---

## 🧪 Passo 4: Validação

### Testar Engine

```bash
python teste_engine_completo.py
```

### Testar API

```bash
# Iniciar servidor
python main.py

# Em outro terminal
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{"pergunta":"Quem é você?"}'
```

---

## ⚙️ Configurações Avançadas

### Ajustar Hiperparâmetros

Em `colab_finetuning.py`:

```python
# Alterar arquitetura
model = criar_modelo_simples(
    vocab_size=20000,      # Aumentar vocabulário
    embedding_dim=256,     # Embeddings maiores
    max_length=150         # Sequências mais longas
)

# Alterar treinamento
treinar_modelo(
    model,
    X_train,
    y_train,
    epochs=100,            # Mais épocas
    batch_size=64,         # Batch maior
    validation_split=0.15  # Menos validação
)
```

### Data Augmentation

Adicione variações em `gerar_dataset.py`:

```python
def augmentar_dataset(dataset):
    augmented = []
    
    for item in dataset:
        # Original
        augmented.append(item)
        
        # Lowercase
        augmented.append({
            "pergunta": item["pergunta"].lower(),
            "resposta": item["resposta"]
        })
        
        # Sem pontuação
        augmented.append({
            "pergunta": item["pergunta"].rstrip("?!."),
            "resposta": item["resposta"]
        })
    
    return augmented
```

---

## 📊 Benchmarks

### Recursos Necessários

| Recurso | Colab Free | Colab Pro |
|---------|------------|-----------|
| GPU | Tesla K80 | Tesla P100/V100 |
| RAM | 12 GB | 25 GB |
| Tempo | 30-60 min | 15-30 min |
| Custo | Grátis | $10/mês |

### Performance Esperada

| Métrica | Target | Esperado |
|---------|--------|----------|
| Accuracy (train) | >90% | 85-95% |
| Accuracy (val) | >80% | 75-90% |
| Loss (val) | <1.0 | 0.5-1.5 |
| Tempo/época | <60s | 30-90s |

---

## 🐛 Troubleshooting

### Erro: "Out of Memory"

**Solução:**
```python
# Reduzir batch size
treinar_modelo(model, X_train, y_train, batch_size=16)

# Ou reduzir modelo
criar_modelo_simples(embedding_dim=64, max_length=50)
```

### Erro: "Session Timeout"

**Causa:** Colab limita sessão a 12h (free tier)

**Solução:**
```python
# Salvar checkpoints intermediários
callbacks = [
    keras.callbacks.ModelCheckpoint(
        'checkpoint_{epoch}.h5',
        save_best_only=True
    )
]
```

### Underfitting (baixa accuracy)

**Soluções:**
- Aumentar épocas
- Aumentar complexidade do modelo
- Mais dados no dataset
- Remover dropout

### Overfitting (val_loss >> train_loss)

**Soluções:**
- Adicionar dropout
- Reduzir modelo
- Mais dados
- Early stopping mais agressivo

---

## 📈 Próximos Passos

### Transfer Learning

Use modelos pré-treinados:

```python
from transformers import TFBertModel

# Carregar BERT português
bert = TFBertModel.from_pretrained("neuralmind/bert-base-portuguese-cased")

# Fine-tune para ALICI
# ...
```

### Multi-task Learning

Treinar múltiplas tarefas:
- Q&A
- Sentiment analysis
- Intent classification

### Continuous Learning

Atualizar modelo com dados de produção:

```bash
# Exportar conversas reais
python export_conversations.py > novo_dataset.json

# Retreinar
python colab_finetuning.py --dataset novo_dataset.json
```

---

## 📚 Recursos

- **TensorFlow Docs**: https://tensorflow.org
- **Keras Guide**: https://keras.io/guides/
- **Colab Tips**: https://colab.research.google.com/notebooks/
- **NLP Best Practices**: https://huggingface.co/docs

---

## 📞 Suporte

- **Issues**: https://github.com/matteusnascimento/alici.ai/issues
- **Docs**: README.md e SETUP.md

---

**Última atualização**: 2026-02-02
