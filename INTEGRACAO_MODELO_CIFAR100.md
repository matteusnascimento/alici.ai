# 🤖 #3 - Conexão Real do Modelo com /chat Endpoint

**Versão:** 1.0  
**Data:** Janeiro 24, 2026  
**Status:** ✅ IMPLEMENTAÇÃO CONCLUÍDA

---

## 📋 Resumo Executivo

Integração completa do modelo CIFAR-100 treinado (`modelo_animais_treinado.h5`) com o servidor Flask via novos endpoints de reconhecimento de imagem. O sistema agora pode:

✅ **Receber imagens** via upload (multipart/form-data)  
✅ **Processar imagens** com normalização 32x32 RGB  
✅ **Fazer predições** usando CNN CIFAR-100  
✅ **Retornar respostas** em português natural com confiança  
✅ **Suportar alternativas** (top-3 predições)

---

## 🏗️ Arquitetura da Solução

```
User Request (Imagem)
      ↓
[Flask /chat/image]
      ↓
[model_inference.py]
      ├─ Carregar modelo (cache)
      ├─ Preprocessar imagem (32x32, normalizar)
      ├─ Model.predict()
      └─ Gerar resposta em português
      ↓
JSON Response (classe, confiança, alternativas)
      ↓
Frontend (Avatar reage)
```

### Componentes Novos

| Arquivo | Função | Status |
|---------|--------|--------|
| **model_inference.py** | Módulo de inferência do modelo | ✅ Criado |
| **main.py** (atualizado) | 3 novos endpoints Flask | ✅ Integrado |
| **requirements.txt** (atualizado) | TensorFlow + Keras + NumPy | ✅ Atualizado |
| **teste_integracao_modelo.py** | Testes de integração | ✅ Criado |

---

## 🚀 Endpoints Implementados

### 1. **POST /chat/image** - Análise via Upload de Arquivo

Upload multipart de uma imagem e retorna a predição.

**Request:**
```bash
curl -X POST \
  -F "imagem=@animais_preditos/predicao_1.png" \
  http://localhost:5000/chat/image
```

**Response (Sucesso - 200):**
```json
{
  "classe": "gato",
  "confianca": 94.5,
  "resposta": "Detectei um **gato** com **94.5%** de confiança!\n\nOutras possibilidades: tigre (3.2%), leão (2.3%)",
  "alternativas": [
    {"classe": "tigre", "confianca": 3.2},
    {"classe": "leão", "confianca": 2.3}
  ],
  "status": "sucesso"
}
```

**Response (Erro - 400/500):**
```json
{
  "erro": "Descrição do erro",
  "status": "erro"
}
```

**Parâmetros:**
- `imagem` (form file, obrigatório): PNG, JPG, JPEG, GIF, BMP
- Max size: 16 MB
- Formatos suportados: .png, .jpg, .jpeg, .gif, .bmp

---

### 2. **POST /chat/image-base64** - Análise via Base64

Envia imagem em Base64 (útil para JavaScript/Canvas).

**Request:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "imagem_base64": "data:image/png;base64,iVBORw0KGgo...",
    "nome": "foto.png"
  }' \
  http://localhost:5000/chat/image-base64
```

**Response:** Mesmo formato que `/chat/image`

**Parâmetros JSON:**
- `imagem_base64` (string, obrigatório): Imagem em Base64 (com ou sem prefixo `data:image/...;base64,`)
- `nome` (string, opcional): Nome do arquivo para logging

---

### 3. **GET /model/status** - Status do Modelo

Verifica se o modelo está carregado e retorna metadados.

**Request:**
```bash
curl http://localhost:5000/model/status
```

**Response (Sucesso - 200):**
```json
{
  "modelo_disponivel": true,
  "modelo_carregado": true,
  "resumo": {
    "tipo": "CNN CIFAR-100 (Animais/Objetos)",
    "parametros": 152868,
    "input_shape": [null, 32, 32, 3],
    "output_shape": [null, 100],
    "classes_suportadas": 100
  },
  "endpoints": {
    "/chat/image": "Análise de imagem via multipart upload",
    "/chat/image-base64": "Análise de imagem via Base64",
    "/model/status": "Status do modelo (este endpoint)"
  }
}
```

**Response (Erro - 503):**
```json
{
  "modelo_disponivel": false,
  "erro": "Descrição do erro"
}
```

---

## 📦 Instalação e Configuração Local

### Passo 1: Instalar Dependências

```bash
cd c:\alici.ai

# Instalar todas as dependências
pip install -r requirements.txt

# Ou apenas as necessárias (se TensorFlow já está instalado)
pip install tensorflow==2.13.1 keras==2.13.1 numpy==1.24.3
```

**Nota:** TensorFlow (~500 MB) leva 2-5 minutos para instalar na primeira vez.

### Passo 2: Verificar Arquivos Necessários

```bash
# Verificar modelo
ls -lh modelo_animais_treinado.h5
# Esperado: ~526 KB

# Verificar módulo de inferência
ls -l model_inference.py
# Esperado: Novo arquivo criado
```

### Passo 3: Executar Testes Locais

```bash
# Teste de integração completo
python teste_integracao_modelo.py

# Esperado:
# ✅ Modelo encontrado
# ✅ Dependências importadas
# ✅ Modelo carregado
# ✅ Predições realizadas
# ✅ TESTES CONCLUÍDOS COM SUCESSO!
```

### Passo 4: Iniciar Servidor

```bash
# Modo desenvolvimento
python main.py

# Ou com Gunicorn (produção)
gunicorn main:app --workers 2 --worker-class sync --bind 0.0.0.0:5000

# Esperado:
# WARNING in app.run() is not intended for production use!
# Running on http://0.0.0.0:5000
```

### Passo 5: Testar Endpoints Localmente

```bash
# 1. Verificar status do modelo
curl http://localhost:5000/model/status

# 2. Enviar imagem para análise
curl -X POST \
  -F "imagem=@animais_preditos/predicao_1.png" \
  http://localhost:5000/chat/image

# 3. Testar resposta text
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"mensagem":"Olá"}' \
  http://localhost:5000/chat
```

---

## 🧠 Como Funciona a Predição

### Fluxo Completo

```
1. RECEBER IMAGEM
   └─ Validar formato (PNG, JPG, etc)
   └─ Salvar temporariamente

2. PREPROCESSAR
   └─ Abrir com PIL
   └─ Redimensionar para 32x32 (LANCZOS)
   └─ Converter para RGB
   └─ Normalizar [0,255] → [0,1]
   └─ Adicionar batch dimension: (32,32,3) → (1,32,32,3)

3. CARREGAR MODELO (Cache)
   └─ Se não carregado: load_model('modelo_animais_treinado.h5')
   └─ Se carregado: usar cache

4. FAZER PREDIÇÃO
   └─ model.predict(imagem_processada)
   └─ Retorna: array de 100 probabilidades

5. EXTRAIR RESULTADOS
   └─ Argmax para classe principal
   └─ Argsort para top-k alternativas
   └─ Converter índice → nome de classe

6. GERAR RESPOSTA
   └─ Português natural com emoji
   └─ Exemplo: "Detectei um **gato** com **94.5%** de confiança!"
   └─ Se confiança < 85%: adicionar alternativas

7. LIMPAR
   └─ Remover arquivo temporário
   └─ Retornar JSON

8. OPCIONAL: APRENDER
   └─ Chamar database.aprender()
   └─ Persistir predição para memória
```

### Classes CIFAR-100 Suportadas

O modelo foi treinado com todas as 100 classes CIFAR-100:

```python
# Exemplos de classes suportadas:
['apple', 'aquarium_fish', 'bear', 'beaver', 'bee', 'beetle',
 'bicycle', 'bottle', 'boy', 'bridge', 'bus', 'butterfly', 'camel',
 'car', 'castle', 'caterpillar', 'cattle', 'chair', 'chimpanzee',
 'clock', 'cloud', 'cockroach', 'couch', 'crab', 'crocodile', 'cup',
 'dog', 'doll', 'dolphin', 'domino', 'donkey', 'door', 'dragon',
 'dragonfly', 'dress', 'duck', 'dumbbell', 'eagle', 'eel', 'eggplant',
 ... (100 total)
]
```

---

## 🔧 Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'tensorflow'"

**Solução:**
```bash
pip install tensorflow==2.13.1 --upgrade

# Se ainda não funcionar, instalar versão específica
pip install tensorflow==2.13.1 keras==2.13.1 numpy==1.24.3 --no-cache-dir
```

### Problema: "FileNotFoundError: modelo_animais_treinado.h5"

**Solução:**
```bash
# Verificar se o arquivo existe
ls -lh c:\alici.ai\modelo_animais_treinado.h5

# Se não existir, gerar novo modelo (veja treinamento no Colab)
# Ou usar modelo pré-treinado de exemplo
```

### Problema: "Imagem não é válida ou corrompida"

**Solução:**
```bash
# Verificar formato da imagem
file animais_preditos/predicao_1.png

# Reconverter imagem
from PIL import Image
img = Image.open('imagem_ruim.png')
img.save('imagem_boa.png', 'PNG')
```

### Problema: Resposta lenta em primeira execução

**Esperado:** Primeira predição leva 5-10 segundos (carregando modelo)  
**Solução:** Implementado cache - predições subsequentes < 1 segundo

```python
# O módulo implementa cache automático:
_model_cache = None  # Primeira chamada: carrega
                     # Próximas chamadas: usa cache
```

### Problema: "Erro 503: Modelo não disponível"

**Causa:** Dependências não instaladas  
**Solução:**
```bash
# Verificar importações
python -c "import tensorflow, keras, numpy; print('OK')"

# Se falhar, instalar novamente
pip install -r requirements.txt --force-reinstall
```

---

## 📊 Formato de Resposta Detalhado

### Sucesso (200)
```json
{
  "classe": "animal/objeto detectado",
  "confianca": 94.5,
  "resposta": "Resposta em português natural com ** negrito **",
  "alternativas": [
    {"classe": "classe_2", "confianca": 3.2},
    {"classe": "classe_3", "confianca": 2.3}
  ],
  "status": "sucesso"
}
```

### Erro - Arquivo não fornecido (400)
```json
{
  "erro": "Nenhum arquivo de imagem enviado. Use chave 'imagem'.",
  "status": "erro"
}
```

### Erro - Formato inválido (400)
```json
{
  "erro": "Tipo de arquivo não permitido. Use: png, jpg, jpeg, gif, bmp",
  "status": "erro"
}
```

### Erro - Processamento (500)
```json
{
  "erro": "Erro ao processar imagem: [descrição técnica]",
  "status": "erro"
}
```

### Erro - Modelo indisponível (503)
```json
{
  "erro": "Modelo não disponível",
  "status": "erro"
}
```

---

## 📱 Frontend - Como Integrar no JavaScript

### HTML com Input de Arquivo

```html
<form id="imageForm">
  <input type="file" id="imageInput" accept="image/*" />
  <button type="submit">Analisar Imagem</button>
</form>
<div id="resultado"></div>

<script>
  document.getElementById('imageForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('imageInput');
    const formData = new FormData();
    formData.append('imagem', fileInput.files[0]);
    
    try {
      const response = await fetch('/chat/image', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (data.status === 'sucesso') {
        document.getElementById('resultado').innerHTML = `
          <h3>${data.classe}</h3>
          <p><strong>Confiança:</strong> ${data.confianca.toFixed(1)}%</p>
          <p>${data.resposta}</p>
        `;
      } else {
        document.getElementById('resultado').innerHTML = `
          <p style="color: red;">Erro: ${data.erro}</p>
        `;
      }
    } catch (error) {
      console.error('Erro:', error);
    }
  });
</script>
```

### Envio via Canvas (Base64)

```javascript
const canvas = document.getElementById('canvas');
const imageData = canvas.toDataURL('image/png');

fetch('/chat/image-base64', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    imagem_base64: imageData,
    nome: 'drawing.png'
  })
})
.then(r => r.json())
.then(data => {
  console.log('Predição:', data.classe, data.confianca);
});
```

---

## 🚀 Deploy no Render (Próximo Passo)

### Procfile Atualizado

```
web: gunicorn main:app --workers 1 --worker-class sync --bind 0.0.0.0:$PORT --timeout 120
```

**Nota:** Aumentado timeout para 120s (TensorFlow pode levar tempo)

### Variáveis de Ambiente (Render Dashboard)

```
PORT=10000
DATABASE_URL=postgresql://...
SECRET_KEY=seu_secret_aqui
```

### Build Steps (Automático)

```bash
1. pip install -r requirements.txt
   └─ TensorFlow (~500 MB)
   └─ Keras, NumPy
   └─ Flask, Gunicorn

2. Validar arquivo modelo
   └─ modelo_animais_treinado.h5 (526 KB)

3. Iniciar Gunicorn
   └─ Listening on http://0.0.0.0:10000
```

**Tempo esperado:** 5-8 minutos (TensorFlow é grande)

### URL em Produção

```
https://alici-ai.onrender.com/chat/image
```

### Teste em Produção

```bash
curl -X POST \
  -F "imagem=@animais_preditos/predicao_1.png" \
  https://alici-ai.onrender.com/chat/image
```

---

## ✅ Checklist de Validação

- [x] `model_inference.py` criado e funcional
- [x] `main.py` atualizado com 3 novos endpoints
- [x] `requirements.txt` atualizado (TensorFlow + Keras)
- [x] `teste_integracao_modelo.py` criado
- [x] Documentação completa (este arquivo)
- [x] Testes locais passando
- [ ] Deploy no Render (próximo passo)
- [ ] Testar em produção
- [ ] Integrar com avatar holográfico

---

## 📈 Performance Esperada

| Métrica | Valor | Notas |
|---------|-------|-------|
| Tamanho do modelo | 526 KB | Leve, otimizado |
| Parâmetros | 152,868 | CNN compacto |
| Primeira predição | 8-15s | Carrega modelo em cache |
| Predições seguintes | 200-500ms | Modelo em cache RAM |
| Taxa de sucesso | >95% | Imagens válidas |
| Tempo resposta API | <1s (cached) | Com cache |
| Memória utilizada | ~150 MB | Modelo carregado |

---

## 🎯 Próximos Passos (Depois do Deploy)

1. **Integração com Avatar**
   - Avatar muda para estado "listening" → "thinking" → "speaking"
   - Reproduzir resposta em áudio (TTS)

2. **Persistência de Predições**
   - `database.aprender()` armazena predições
   - "Você já me perguntou sobre isso antes..."

3. **Multimodal Router**
   - Detectar tipo de input (texto vs imagem)
   - Rotear para motor apropriado

4. **Batch Processing**
   - Enviar múltiplas imagens
   - Comparar resultados

5. **Export Mobile**
   - Converter para `.tflite`
   - Fazer app Android/iOS

---

## 📚 Referências

- [TensorFlow Documentation](https://www.tensorflow.org/)
- [Keras Models](https://keras.io/api/models/)
- [Flask File Upload](https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/)
- [CIFAR-100 Dataset](https://www.cs.toronto.edu/~kriz/cifar.html)

---

## 🤝 Suporte

Se encontrar problemas:

1. Executar: `python teste_integracao_modelo.py`
2. Verificar logs: `python main.py` (modo debug)
3. Testar manualmente: `curl http://localhost:5000/model/status`

---

**Status Final:** ✅ #3 PRONTO PARA DEPLOY
