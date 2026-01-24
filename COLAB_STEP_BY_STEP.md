# 📱 INSTRUÇÕES PASSO-A-PASSO PARA COLAB

## **PASSO 1: Abrir Google Colab**

```
URL: https://colab.research.google.com/
Ou: Google.com → Procurar "Google Colab"
```

**Tela esperada**: Home do Colab com botão "+ New Notebook"

---

## **PASSO 2: Criar Novo Notebook**

```
Clique em "+ New Notebook"
Ou "File" → "New Notebook"
Aguarde a página carregar
```

**Tela esperada**: Notebook vazio com célula pronta

---

## **PASSO 3: Copiar Script**

```
Abra arquivo: colab_finetuning.py
Pressione: Ctrl+A (seleciona tudo)
Pressione: Ctrl+C (copia)
```

---

## **PASSO 4: Colar em Colab**

```
Clique na célula vazia do Colab
Pressione: Ctrl+V (cola)
Verifique se tem 300+ linhas de código
```

**Resultado esperado**: Código Python aparece na célula

---

## **PASSO 5: Ativar GPU (IMPORTANTE!)**

```
Menu superior → "Runtime"
                → "Change runtime type"
                → Hardware accelerator: GPU
                → "Save"
```

**Verificar**:
```python
import tensorflow as tf
print(f"GPU: {tf.config.list_physical_devices('GPU')}")
# Deve retornar: GPU: [PhysicalDevice(...)]
```

---

## **PASSO 6: Executar Script**

```
Clique no botão ▶️ (Play) à esquerda da célula
Ou pressione: Ctrl+Enter
Aguarde "Installing dependencies..."
```

**Você verá**:
```
📦 Instalando dependências...
✅ Dependências instaladas!

🚀 ALICI™ FINE-TUNING MULTI-MODAL - GOOGLE COLAB
...
```

---

## **PASSO 7: Upload do Modelo**

**Você verá**:
```
🧠 Carregando MODELO EXISTENTE...

📤 Nenhum modelo encontrado localmente
Clique em 'Executar' para fazer upload do modelo .h5...
```

**O Que Fazer**:
```
1. Clique no botão "Choose Files" que aparece
2. Procure seu arquivo .h5 (ex: alici_modelo.h5)
3. Selecione e clique "Open"
4. Aguarde upload (0-30 segundos)
5. Verá: "✅ modelo.h5 (246.5 MB)"
```

---

## **PASSO 8: Escolher Tipo de Treinamento**

**Você verá**:
```
Escolha quais dados usar para treinar:

  1️⃣  Apenas TEXTO (rápido, 5-10 min)
  2️⃣  Apenas ÁUDIO (médio, 10-15 min)
  3️⃣  Apenas IMAGENS (médio, 10-15 min)
  4️⃣  TEXTO + ÁUDIO (longo, 15-20 min)
  5️⃣  TEXTO + IMAGENS (longo, 15-20 min)
  6️⃣  ÁUDIO + IMAGENS (longo, 15-20 min)
  7️⃣  TODOS (texto + áudio + imagens, 25-30 min)

Digite o número (1-7) ou pressione Enter para TEXTO (padrão):
```

**Exemplo**:
```
Digita: 7
Pressiona Enter
```

---

## **PASSO 9: Upload de Datasets**

Dependendo da opção escolhida:

### **Se escolheu Texto**:
```
Clique em "Choose Files"
Selecione: dataset_expandido.json
Upload automático
```

### **Se escolheu Áudio**:
```
Clique em "Choose Files"
Selecione: audio.zip (com WAV/MP3 dentro)
Upload automático
Extrai automaticamente
```

### **Se escolheu Imagens**:
```
Clique em "Choose Files"
Selecione: imagens.zip (com PNG/JPG dentro)
Upload automático
```

### **Se escolheu Tudo (opção 7)**:
```
Repete para cada tipo:
1. Clique em "Choose Files" → dataset_expandido.json
2. Clique em "Choose Files" → audio.zip
3. Clique em "Choose Files" → imagens.zip
```

---

## **PASSO 10: Acompanhar Treinamento**

**Você verá**:
```
🏋️ Iniciando fine-tuning com TEXTO...
   Epochs: 20
   Batch size: 16
   Samples: 100

Epoch 1/20
32/32 [==============================] - 2s 65ms/step - loss: 0.4521 - accuracy: 0.8200
Epoch 2/20
32/32 [==============================] - 2s 64ms/step - loss: 0.3124 - accuracy: 0.9100
...
✅ Treinamento concluído!
```

**Deixe rodar**: Não feche a aba, não desconecte!

---

## **PASSO 11: Finalização**

**Quando terminar**:
```
✅ TREINAMENTO CONCLUÍDO COM SUCESSO!

📋 RESUMO DO TREINAMENTO:

  Modelo: alici_treinado_multimodal.h5
  Tamanho: 246.5 MB

  Métricas por tipo de dado:
    • TEXTO:
        Loss: 0.2134
        Accuracy: 93.50%
    • ÁUDIO:
        Loss: 0.3456
        Accuracy: 88.20%
    • IMAGENS:
        Loss: 0.1987
        Accuracy: 95.60%

🎯 PRÓXIMOS PASSOS:
  1. Clique em 'Executar' para BAIXAR o modelo:
  [Botão de Download] alici_treinado_multimodal.h5
```

---

## **PASSO 12: Baixar Modelo**

**Você verá Botão de Download**:
```
Clique em: ↓ alici_treinado_multimodal.h5
Arquivo desce para seu computador
(Pode demorar 30 segundos)
```

**Você terá**:
```
C:\Downloads\alici_treinado_multimodal.h5 (246 MB)
```

---

## **PASSO 13: Fazer Deploy**

**No seu computador**:
```bash
cd C:\alici.ai

# Copie o modelo
cp C:\Downloads\alici_treinado_multimodal.h5 .\alici_modelo.h5

# Versione
git add alici_modelo.h5
git commit -m "feat: Modelo treinado multi-modal em Colab"
git push origin main

# Render detecta em 10 segundos
# Deploy em ~15 minutos
# ✅ Seu novo modelo live em produção!
```

---

## **PASSO 14: Testar**

**Localmente**:
```bash
python main.py
# Acessar http://localhost:5000
```

**Em produção**:
```
https://alici-ai.onrender.com
# Seu novo modelo já está funcionando!
```

---

## **⏱️ Tempo Total**

```
Preparação: 2-5 min
Upload: 2-5 min
Treinamento: 15-30 min (depende dos dados)
Download: 1-2 min
Deploy: 15 min (automático)

TOTAL: ~45-60 minutos
```

---

## **✅ Checklist Completo**

- [ ] Abrir Colab
- [ ] Criar Notebook
- [ ] Copiar código
- [ ] Colar em Colab
- [ ] Ativar GPU
- [ ] Executar
- [ ] Upload modelo .h5
- [ ] Escolher opção (1-7)
- [ ] Upload datasets
- [ ] Acompanhar treinamento
- [ ] Baixar novo modelo
- [ ] git push
- [ ] Verificar Render deploy
- [ ] Testar em produção
- [ ] ✅ PRONTO!

---

## **Tudo Pronto?**

```
1. Acesse: https://colab.research.google.com/
2. Novo Notebook
3. Copie e cole colab_finetuning.py
4. Pressione Play
5. Siga os passos acima
6. Em ~1 hora: Novo modelo em produção!
```

---

**Boa sorte! Seu modelo vai ficar 10x melhor! 🚀✨**
