# 🚀 GUIA RÁPIDO - COLAB MULTI-MODAL

## **Script Completo Pronto!**

O novo `colab_finetuning.py` suporta:
- ✅ **Texto** (JSON)
- ✅ **Áudio** (WAV, MP3)
- ✅ **Imagens** (PNG, JPG)
- ✅ **Multi-modal** (todos juntos!)

---

## **Como Usar em Google Colab**

### **1. Abrir Google Colab**
```
https://colab.research.google.com/
```

### **2. Copiar Código**
```
Copie TODO o arquivo colab_finetuning.py
Cola em UMA célula do Colab
```

### **3. Executar**
```
Pressione Play (▶️) ou Ctrl+Enter
```

### **4. Seguir os Passos**

**Passo 1**: Upload do Modelo
```
Clique no botão que aparecer
Selecione seu arquivo .h5 (modelo atual)
Aguarde upload
```

**Passo 2**: Escolher Tipo de Dado
```
Menu vai aparecer:
  1 = Apenas texto
  2 = Apenas áudio
  3 = Apenas imagens
  4 = Texto + áudio
  5 = Texto + imagens
  6 = Áudio + imagens
  7 = Tudo junto

Digita o número (1-7) e pressiona Enter
```

**Passo 3**: Upload do Dataset
```
Clique no botão para cada tipo de dado
Escolha arquivo JSON ou ZIP com arquivos
Aguarde processar
```

**Passo 4**: Treinar
```
Acompanha em tempo real
GPU grátis do Google trabalhando
15-30 minutos dependendo dos dados
```

**Passo 5**: Baixar Modelo
```
Clique no botão de download
Seu novo modelo desce para o computador
```

---

## **Preparar Dados**

### **Para TEXTO**
```
Arquivo: dataset_expandido.json
Formato:
{
  "perguntas": ["como é...", "quem é..."],
  "respostas": ["resposta 1", "resposta 2"]
}
```

### **Para ÁUDIO**
```
Arquivo: audio.zip contendo:
  ├── audio1.wav
  ├── audio2.wav
  └── audio3.mp3

Extraindo automaticamente em Colab
```

### **Para IMAGENS**
```
Arquivo: imagens.zip contendo:
  ├── img1.jpg
  ├── img2.png
  └── img3.jpg

Dimensionadas automaticamente para 224x224
```

---

## **⏱️ Tempo Esperado**

| Tipo | Tempo | GPU |
|------|-------|-----|
| Texto | 5-10 min | ✅ |
| Áudio | 10-15 min | ✅ |
| Imagens | 10-15 min | ✅ |
| Texto + Áudio | 15-20 min | ✅ |
| Tudo junto | 25-30 min | ✅ |

**GPU**: Google Colab fornece automaticamente!

---

## **Depois de Treinar**

### **1. Baixar Modelo**
```
Clique no link de download que aparece
Salva em seu computador
```

### **2. Fazer Upload para Git**
```bash
cd seu/alici.ai

# Renomear ou substituir
cp alici_treinado_multimodal.h5 alici_modelo.h5

# Versionar
git add alici_modelo.h5
git commit -m "feat: Modelo treinado em Colab (texto+áudio+imagens)"
git push origin main
```

### **3. Render Detecta Automaticamente**
```
Render vê o push
Faz rebuild
Deploy automático
✅ Sistema live em produção!
```

---

## **🎯 Exemplo Completo**

```python
# Tudo que você precisa fazer em Colab:

1. Copiar código de colab_finetuning.py
2. Executar célula
3. Quando pedir:
   - Upload: seu_modelo.h5
   - Opção: 7 (tudo junto)
   - Upload: dataset.json, audio.zip, imagens.zip
4. Esperar treinar
5. Clique para baixar alici_treinado_multimodal.h5
6. git push local
7. ✅ Novo modelo em produção!
```

---

## **⚠️ Troubleshooting**

### ❌ "GPU not available"
```
Menu → Runtime → Change runtime type
Hardware → GPU
Salvar
```

### ❌ "File not found"
```
Fazer upload novamente
Verificar extensão (.h5, .json, .zip)
```

### ❌ "Out of memory"
```
Reduzir epochs: 20 → 10
Reduzir batch_size: 16 → 8
Usar menos amostras
```

### ❌ "Librosa error"
```
!pip install librosa -q
Reexecutar
```

---

## **📊 Status**

```
✅ Script completo e testado
✅ Suporta múltiplos tipos de dados
✅ Interface amigável
✅ Upload/Download automático
✅ Pronto para produção
```

---

## **🚀 Comece Agora**

1. Abra https://colab.research.google.com/
2. Copie `colab_finetuning.py`
3. Execute
4. Siga os passos
5. Seu modelo melhorado em 30 minutos! ✨

---

**Boa sorte com o treinamento! 🎉**
