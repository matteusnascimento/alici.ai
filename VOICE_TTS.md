# 🎙️ INTEGRAÇÃO VOICE - TEXT-TO-SPEECH

## ✅ Você Tem 2 Opções de Voz

### 1️⃣ GOOGLE TTS (Recomendado)
```bash
pip install gtts==2.3.1
```
- ✅ Melhor qualidade
- ✅ Suporta 100+ idiomas
- ✅ Online (precisa internet)
- ✅ Grátis e ilimitado

### 2️⃣ PYTTSX3 (Offline)
```bash
pip install pyttsx3==2.90
```
- ✅ Funciona sem internet
- ⚠️ Qualidade mais robótica
- ✅ Disponível em Windows/Mac/Linux

---

## 🚀 Integração em main.py

Seu `main.py` já tem suporte para áudio! Você pode usar o endpoint:

```python
# POST /chat/audio
{
    "mensagem": "Olá Alici",
    "idioma": "pt"  # "pt", "en", "es"
}

# Resposta:
{
    "resposta": "Olá! Como posso ajudá-lo?",
    "audio_base64": "SUQzBAAAAAAAI1NT...",
    "tipo": "audio/mpeg"
}
```

---

## 💻 Testar Localmente

```bash
# 1. Instalar dependências
pip install gtts pyttsx3

# 2. Rodar servidor
python main.py

# 3. Em outro terminal, testar:
curl -X POST http://localhost:5000/chat/audio \
  -H "Content-Type: application/json" \
  -d '{
    "mensagem": "olá",
    "idioma": "pt"
  }'
```

---

## 🎯 Usar em Frontend HTML/JS

```html
<script>
async function enviarComAudio(mensagem) {
    const response = await fetch('/chat/audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            mensagem: mensagem,
            idioma: 'pt'
        })
    });
    
    const data = await response.json();
    
    // 1. Mostrar resposta
    console.log(data.resposta);
    
    // 2. Reproduzir áudio
    if (data.audio_base64) {
        const audio = new Audio(
            'data:audio/mpeg;base64,' + data.audio_base64
        );
        audio.play();
    }
}

// Usar:
enviarComAudio("quem é você");
</script>
```

---

## 🔧 Configuração Avançada

### Em `alici_tts.py`:

```python
from alici_tts import AliciTTS

# Criar conversor
tts = AliciTTS(
    idioma="pt",
    velocidade_lenta=False  # True = fala mais devagar
)

# Converter em memória (rápido)
audio_bytes = tts.converter_em_memoria("Olá mundo!")

# Salvar em arquivo
arquivo = tts.converter("Olá mundo!", "resposta.mp3")

# Converter resposta de chat completa
audio = tts.converter_resposta_audio(
    resposta="Bem vindo ao Alici!",
    idioma="pt"
)
```

---

## 📊 Idiomas Suportados

| Idioma | Código | Qualidade gTTS |
|--------|--------|---|
| Português (Brasil) | `pt` | ⭐⭐⭐⭐⭐ |
| English | `en` | ⭐⭐⭐⭐⭐ |
| Español | `es` | ⭐⭐⭐⭐ |

---

## ⚠️ Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'gtts'"
```bash
pip install gtts
```

### ❌ "Network error / Timeout"
```
Solução: Sua internet está lenta ou gTTS indisponível
Fallback para pyttsx3 automático
```

### ❌ "Audio muito lento/rápido"
```python
# Em alici_tts.py:
velocidade_lenta=True   # Mais devagar
velocidade_lenta=False  # Normal
```

### ❌ "Permission denied (em arquivo)"
```python
# Usar memória em vez de arquivo:
audio_bytes = tts.converter_em_memoria(texto)
# Em vez de:
arquivo = tts.converter(texto, "/caminho/arquivo.mp3")
```

---

## 🎙️ Deploy em Render

1. ✅ gTTS já está em `requirements.txt`
2. ✅ Endpoint `/chat/audio` já está em `main.py`
3. Fazer `git push`
4. Render deploya automaticamente
5. ✅ Voz ativa em produção!

---

## 📝 Status Implementação

| Feature | Status | Arquivo |
|---------|--------|---------|
| Módulo TTS | ✅ Pronto | `alici_tts.py` |
| Endpoint `/chat/audio` | ✅ Pronto | `main.py` |
| Google TTS | ✅ Em requirements.txt | `requirements.txt` |
| Documentação | ✅ Completa | Este arquivo |
| Deploy Render | ✅ Pronto | Procfile |

---

## 🚀 Próximo Passo

```bash
# 1. Instalar localmente
pip install gtts pyttsx3

# 2. Testar
python alici_tts.py

# 3. Se OK, commit
git add .
git commit -m "feat: Text-to-Speech com gTTS ativado"
git push

# 4. Em Render, versão com voz ativa automaticamente!
```

---

Seu Alici agora pode **falar**! 🎤✨
