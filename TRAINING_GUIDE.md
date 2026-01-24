# 🚀 TREINAMENTO DO MODELO ALICI™ - GUIA COMPLETO

## 📋 Visão Geral

Este documento guia você por **3 etapas** para expandir e treinar o modelo da ALICI em produção:

1. ✅ **C) Expandir Dataset** - Gerar 100+ pares Q&A
2. ✅ **A) Fine-tuning em Colab** - Treinar com GPU grátis
3. ✅ **B) Integrar em Produção** - Colocar modelo no chat

---

## 🎯 C) EXPANDIR DATASET (Executado ✅)

### O que foi feito:
```bash
python gerar_dataset.py
```

**Resultado:**
- ✅ 100 pares Q&A estruturados
- ✅ 5 categorias: Identidade, Criador, Redes Sociais, Capacidades, Personalidade
- ✅ Arquivo: `dataset_expandido.json`

**Conteúdo do Dataset:**
```json
{
  "metadata": {
    "total_pares": 100,
    "criador": "Mateus Nascimento dos Santos",
    "data": "2026-01-24"
  },
  "pares": [
    {
      "pergunta": "quem é você",
      "resposta": "Sou ALICI, uma inteligência artificial proprietária."
    },
    ...
  ]
}
```

---

## 🚀 A) FINE-TUNING EM GOOGLE COLAB

### ⚠️ Instruções Passo-a-Passo:

#### 1️⃣ Acessar Google Colab
```
https://colab.research.google.com
```
- Criar novo notebook
- Colar o código de `colab_finetuning.py`

#### 2️⃣ Fazer Upload de Arquivos
Na primeira célula do Colab:
```python
from google.colab import files
files.upload()  # Selecione:
                # ✅ dataset_expandido.json
                # ✅ modelo_animais_cifar100.h5
```

#### 3️⃣ Instalar Dependências (se necessário)
```python
!pip install tensorflow-gpu==2.13.0
!pip install keras==2.13.0
```

#### 4️⃣ Copiar + Executar Script de Fine-tuning
```python
# Copie TODO o conteúdo de colab_finetuning.py aqui
# Execute a célula

# Output esperado:
# ✅ Dataset carregado: 100 pares Q&A
# ✅ Dados processados: X shape (100, 40)
# 🏋️ Iniciando fine-tuning...
# Epoch 1/20: loss=... accuracy=...
# ...
# ✅ FINE-TUNING CONCLUÍDO COM SUCESSO!
```

#### 5️⃣ Baixar Modelo Treinado
```python
from google.colab import files
files.download('alici_treinado_v3.h5')  # Salva em Downloads
```

### 📊 Métricas Esperadas:

| Métrica | Esperado |
|---------|----------|
| Loss final | < 1.5 |
| Accuracy | > 70% |
| Tempo (GPU) | 2-5 min |
| Tamanho modelo | ~250 MB |

---

## 🎯 B) INTEGRAR AO CHAT (Próximo Passo)

### Arquitetura de Integração:

```
┌─────────────────────────────────────────────────┐
│              PERGUNTA DO USUÁRIO                │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
    [REGRAS LOCAIS]      [MODELO NEURAL]
    (resposta.py)        (novo modelo)
        │                     │
        └──────────┬──────────┘
                   │
       ┌───────────┴───────────┐
       │                       │
    [CACHE]          [MEMÓRIA POSTGRESQL]
       │                       │
       └───────────┬───────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
    [RESPOSTA]           [WEB SEARCH]
        │                     │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │   RESPOSTA FINAL    │
        └─────────────────────┘
```

---

## 📦 Arquivos Necessários

### Gerados:
```
✅ dataset_expandido.json      (100 pares Q&A)
✅ gerar_dataset.py             (gerador)
✅ colab_finetuning.py          (treinamento)
✅ TRAINING_GUIDE.md            (este arquivo)
```

### Esperados do Colab:
```
⏳ alici_treinado_v3.h5         (baixar do Colab)
```

### Existentes:
```
✅ modelo_animais_cifar100.h5   (modelo atual)
✅ engine.py                    (orquestrador)
✅ resposta.py                  (regras locais)
✅ database.py                  (memória)
✅ main.py                      (Flask)
```

---

## 🔄 FLUXO COMPLETO (Timeline)

### Semana 1: Dataset
- ✅ Gerar dataset: `python gerar_dataset.py`
- ✅ Revisar qualidade em `dataset_expandido.json`
- ✅ Ajustar se necessário

### Semana 2: Treinamento
- ⏳ Fazer upload para Colab
- ⏳ Executar fine-tuning
- ⏳ Baixar modelo treinado

### Semana 3: Produção
- ⏳ Substitui modelo em `model/`
- ⏳ Integrar endpoint em `main.py`
- ⏳ Testar com `teste_modelo.py`
- ⏳ Deploy em Render

---

## 🐛 Troubleshooting

### ❌ "Dataset file not found" no Colab
```
Solução: Fazer upload manual na aba "Files" à esquerda
```

### ❌ "Model has incompatible input shape"
```
Solução: Verifique X.shape no script
Esperado: (100, 40) - 100 amostras, 40 tokens cada
```

### ❌ "CUDA out of memory"
```
Solução: Reduzir batch_size em fine-tuning de 16 → 8
```

### ❌ "Accuracy não melhora"
```
Causas possíveis:
- Learning rate muito alto (reduzir: 1e-4 → 1e-5)
- Dataset muito pequeno (adicionar mais pares)
- Epochs insuficientes (aumentar: 20 → 50)
```

---

## 📈 Otimizações Futuras

### 1. Aumentar Dataset
```python
# Adicione mais pares em gerar_dataset.py
perguntas_novas = [...]
respostas_novas = [...]
```

### 2. Data Augmentation
```python
# Adicionar variações de perguntas:
"quem é você" → "quem você é", "você quem é", etc
```

### 3. Validação Cruzada
```python
from sklearn.model_selection import KFold
# Testar em múltiplos splits
```

### 4. Hyperparameter Tuning
```python
# Testar diferentes:
learning_rate = [1e-3, 1e-4, 1e-5]
epochs = [10, 20, 50]
batch_size = [8, 16, 32]
```

---

## 🎓 Conceitos Importantes

### Fine-tuning vs Retraining
- **Fine-tuning**: Mantém pesos anteriores, ajusta com learning rate baixo ✅
- **Retraining**: Apaga tudo e começa do zero ❌

### Learning Rate
- Muito alto (1e-2): Apaga aprendizado anterior
- Bom (1e-4): Ajusta levemente com novos dados ✅
- Muito baixo (1e-6): Sem progresso

### Tokenizer
- Deve ser **reutilizado** do modelo original
- VOCAB_SIZE: 15.000 (máximo de palavras)
- MAX_LEN: 40 (máximo de tokens por sequência)

---

## ✅ Checklist de Implementação

- [ ] Gerar dataset: `python gerar_dataset.py`
- [ ] Verificar `dataset_expandido.json`
- [ ] Colocar `colab_finetuning.py` no Colab
- [ ] Fazer upload de arquivos no Colab
- [ ] Executar fine-tuning (20 epochs)
- [ ] Baixar `alici_treinado_v3.h5`
- [ ] Substituir modelo em `model/`
- [ ] Testar localmente: `python teste_modelo.py`
- [ ] Integrar em `engine.py` ou `main.py`
- [ ] Deploy em Render.com
- [ ] Testar em produção

---

## 📚 Referências

- TensorFlow: https://www.tensorflow.org/guide/keras
- Google Colab: https://colab.research.google.com
- Keras: https://keras.io/
- Transfer Learning: https://en.wikipedia.org/wiki/Transfer_learning

---

**Status**: 🚀 Pronto para executar
**Criador**: Mateus Nascimento dos Santos
**Data**: Jan 24, 2026
**Versão**: 1.0
