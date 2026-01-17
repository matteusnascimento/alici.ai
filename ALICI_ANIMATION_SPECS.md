# 🎨 ALICI - ESPECIFICAÇÕES DE ANIMAÇÃO CYBERPUNK

## 📸 Referência Visual
Avatar: Cyberpunk futurista com cabelo ciano, olhos azuis brilhantes, estilo anime realista

---

## 🎭 ESTADOS DE ANIMAÇÃO

### 1️⃣ **IDLE** - Esperando (Neutral)
**Descrição:** Postura relaxada, respiração suave, movimento mínimo

**Características:**
- Cabelo: Ondulação suave (amplitude: 3px, velocidade: 0.04 rad/frame)
- Olhos: Piscadas ocasionais (a cada 3-5s), olhar frontal
- Boca: Linha neutra
- Corpo: Respiração suave (subida/descida 2px)
- Aura: Ciano (#06b6d4), tamanho normal
- Partículas: Nenhuma

**Velocidade de animação:** 0.08

---

### 2️⃣ **THINKING** - Pensando (Contemplativo)
**Descrição:** Expressão reflexiva, símbolos matemáticos flutuando

**Características:**
- Cabelo: Leve rotação (5°), ondulação moderada
- Olhos: Olhar para cima, piscadas frequentes
- Boca: Leve sorriso (forma de "hmm")
- Corpo: Inclinação para frente
- Aura: Âmbar/Ouro (#fbbf24), pulsação lenta
- Partículas: Símbolos matemáticos (∫, ∞, √, π, ψ) orbitando
  - Quantidade: 3
  - Órbita: raio 80px
  - Cor: Verde neon (#00ff88)

**Velocidade de animação:** 0.08

---

### 3️⃣ **TALKING** - Falando (Comunicativo)
**Descrição:** Dinâmico, animado, boca sincronizada

**Características:**
- Cabelo: Balança lado a lado, flutuação dinâmica
- Olhos: Movimento animado, seguimento com a boca
- Boca: Formas variadas (a, e, i, o, u), movimento sincronizado
- Corpo: Respiração enfatizada, gestos ondulantes
- Aura: Intensidade 0.8, pulsação rápida
- Partículas: Bolhas de fala, linhas de som
  - Cor: Verde ciano (#00ffaa)

**Velocidade de animação:** 0.15

---

### 4️⃣ **HAPPY** - Feliz (Energético)
**Descrição:** Entusiasmado, radiante, explosivo

**Características:**
- Cabelo: Flutuação energética ampla, balanceio intenso
- Olhos: Forma de crescente (feliz), brilho intenso com estrelas
- Boca: Sorriso radiante, movimento exagerado
- Corpo: Pulo leve, movimento de celebração
- Aura: Verde ciano (#00ffaa), expandida, intensidade máxima
- Partículas: Sparkles/confetes (6-8)
  - Cores: #fbbf24 (âmbar), #00ffaa (verde), #ff00ff (magenta)
  - Movimento: Explosivo para cima

**Velocidade de animação:** 0.18

---

### 5️⃣ **SERIOUS** - Sério (Alerta)
**Descrição:** Tense, determinado, avisador

**Características:**
- Cabelo: Eletrizador (ondas eletromagnéticas)
- Olhos: Cor vermelha (#ff0000), brilho de laser, fixação focal
- Sobrancelhas: Visíveis, ângulo para baixo (20°), aproximadas
- Boca: Linha reta, tensão máxima
- Corpo: Postura rígida
- Aura: Vermelha (#ff0000), pulsação de alerta rápida
- Partículas: Raios de alerta (5)
  - Cor: Vermelho (#ff0000)
  - Movimento: Zig-zag

**Velocidade de animação:** 0.10

---

### 6️⃣ **MYSTICAL** - Místico (Espiritual)
**Descrição:** Enigmático, cósmico, etéreo

**Características:**
- Cabelo: Levitação etérea, transformação em partículas
- Olhos: Cor roxa (#8b5cf6), meia-lua, mandala cósmica
- Boca: Leve sorriso enigmático
- Corpo: Levitação sutil, oscilação vertical
- Aura: Roxo (#8b5cf6), expandida, pulsação muito lenta, efeito vórtex
- Partículas: Runas arcanas + símbolos cósmicos (8-12)
  - Cores: Roxo (#8b5cf6), Ciano (#00ffff), Amarelo (#ffff00)
  - Movimento: Órbita lenta, círcular
  - Efeitos: Nebulosa, distorção do espaço

**Velocidade de animação:** 0.06

---

## 🎨 PALETA DE CORES

| Nome | Código | Uso |
|------|--------|-----|
| Ciano Primário | #00ffff | Cabelo, brilho primário |
| Azul Primário | #0099ff | Íris do olho |
| Roxo Místico | #8b5cf6 | Aura padrão, corpo |
| Âmbar | #fbbf24 | Aura pensativo, contemplação |
| Vermelho Alerta | #ef4444 | Aura sério, alerta |
| Verde Ciano | #00ffaa | Aura feliz, sucesso |
| Pele | #f0e6d2 | Rosto e pescoço |
| Branco | #ffffff | Brilho nos olhos |

---

## ⚡ VELOCIDADES

| Tipo | Valor | Uso |
|------|-------|-----|
| Muito Lenta | 0.04 | Mystical (cósmico) |
| Lenta | 0.08 | Idle, Thinking |
| Normal | 0.12 | Padrão |
| Rápida | 0.15 | Talking |
| Muito Rápida | 0.18 | Happy, energético |

---

## 🔄 TRANSIÇÕES

### Idle → Thinking
- Duração: 0.5s
- Easing: ease-out
- Mudanças: Inclinação de cabeça, direção de olhos, cor de aura

### Thinking → Talking
- Duração: 0.3s
- Easing: ease-in-out
- Mudanças: Expressão facial, movimento de cabelo, abertura de boca

### Talking → Idle
- Duração: 0.8s
- Easing: ease-out
- Mudanças: Calma progressiva, redução de movimento

### Any → Happy
- Duração: 0.4s
- Easing: ease-out-bounce
- Mudanças: Explosão de alegria, sparkles

### Any → Serious
- Duração: 0.3s
- Easing: ease-in
- Mudanças: Tensionamento, fixação de olhar

---

## 🧮 DIMENSÕES E PROPORÇÕES

| Parte | Tamanho |
|-------|---------|
| Canvas | 500×600 px |
| Cabeça | 32×40 px (ellipse) |
| Olhos | 8×10 px (iris) |
| Aura | 150 px (raio) |
| Órbita Partículas | 80-100 px |

---

## 🎬 IMPLEMENTAÇÃO

### Arquivo Principal
`alici_renderer.js` - Classe `AliciRenderer` com métodos:
- `setState(estado, emocao, velocidade)`
- `render()` - Loop de animação
- `desenhar*()` - Métodos específicos por elemento

### Integração
```javascript
const controller = new AliciAnimationController("canvas-id");
controller.setState("talking", "happy", 0.18);
```

### Estados Disponíveis
- `"idle"` - Padrão
- `"thinking"` - Contemplativo
- `"talking"` - Comunicativo
- `"happy"` - Entusiasmado
- `"serious"` - Alerta
- `"mystical"` - Espiritual

---

## 🚀 ROTAS DISPONÍVEIS

| Rota | Descrição |
|------|-----------|
| `/personagem` | Interface interativa com chat |
| `/demo-animacoes` | Demonstração de 6 estados |
| `/api/chat-animado` | POST - Retorna resposta + metadados |

---

## 📦 ARQUIVOS CRIADOS

```
Static/
├── alici_renderer.js           # Renderização do personagem
├── alici_animator.js           # Integração com chat
├── alici_character.html        # Interface personagem
└── alici_animation_demo.html   # Demo interativa

Python/
├── alici_specs.py              # Especificações
├── sistema_emocoes.py          # Detecção de emoções
└── engine.py (atualizado)      # Com metadados emocionais
```

---

## ✨ Próximos Passos

1. ✅ Renderização 2D cyberpunk
2. ✅ 6 estados de animação
3. ✅ Sistema de detecção de emoções
4. ⏳ Voice + mouth sync (Text-to-Speech)
5. ⏳ Modelo 3D/Live2D
6. ⏳ Versão mobile (Flutter)

---

**Data:** 16 de janeiro de 2026  
**Versão:** 1.0  
**Status:** 🚀 Pronto para integração
