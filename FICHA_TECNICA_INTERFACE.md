# Ficha Técnica da Interface — ALICI™ AI

## 1. Visão Geral

A interface do utilizador da ALICI™ é composta por quatro páginas HTML servidas directamente pela API FastAPI através do módulo `alici_api/routes/pages.py`. O design adopta uma estética **cyberpunk / neurotech**: fundos escuros, efeitos de néon, partículas animadas, glassmorphism e tipografia futurista. As páginas não dependem de nenhuma framework JavaScript de componentes (React, Vue, etc.); toda a lógica de UI é implementada em JavaScript vanilla.

### Inventário de Páginas

| Ficheiro | Rota | Descrição |
|---|---|---|
| `templates/login.html` | `GET /` | Página de autenticação (login + registo em abas) |
| `templates/chat.html` | `GET /chat` | Interface de chat directa com a ALICI |
| `templates/index.html` | — | Plataforma SaaS completa (Dashboard, Chat, Modelos, Analytics, Configurações) |
| `templates/quantum.html` | — | Interface futurista experimental com avatar animado |

> **Nota de roteamento:** O servidor serve `login.html` em `/` e `chat.html` em `/chat` e `/dashboard`. O `index.html` e o `quantum.html` não estão expostos em rotas activas mas estão disponíveis no directório `templates/`.

---

## 2. Linguagem Visual

### 2.1 Paletas de Cor

#### Paleta — `login.html` e `quantum.html` (tema cyberpunk neon)

| Variável CSS | Valor | Uso |
|---|---|---|
| `--neon-cyan` | `#00ffff` | Cor primária, bordas, indicadores, glow |
| `--neon-blue` | `#0066ff` | Gradientes de fundo e botões |
| `--neon-pink` | `#ff0099` | Estados de erro, hover, destaque secundário |
| `--neon-purple` | `#9933ff` | Gradientes de identidade, abas activas |
| `--neon-green` | `#00ff66` | Indicadores de estado online / sucesso |
| `--neon-yellow` | `#ffcc00` | Estado "Aprendendo" no chat |
| `--neon-orange` | `#ff6600` | Uso futuro / destaque terciário |
| `--bg-dark` | `#0a0a0f` | Fundo principal do body |
| `--glass-bg` | `rgba(15,15,25,0.85)` | Superfície glassmorphism |

#### Paleta — `index.html` (tema SaaS profissional)

| Variável CSS | Valor | Uso |
|---|---|---|
| `--bg-primary` | `#0b1120` (dark) / `#f1f5f9` (light) | Fundo principal |
| `--bg-secondary` | `#0f172a` (dark) / `#e2e8f0` (light) | Fundo secundário |
| `--surface` | `rgba(15,23,42,.6)` | Superfície glassmorphism |
| `--surface-strong` | `rgba(15,23,42,.82)` | Superfície sólida (inputs, topbar) |
| `--text-primary` | `#e5edff` (dark) / `#0f172a` (light) | Texto principal |
| `--text-secondary` | `#94a3b8` (dark) / `#334155` (light) | Texto secundário |
| `--electric-blue` | `#2563eb` | Botões primários, nav activa |
| `--cyan` | `#22d3ee` | Acentuação, loading, gráfico |
| `--purple` | `#8b5cf6` | Logo mark, gradientes |
| `--success` | `#22c55e` | Indicador de status online (pulse dot) |
| `--border` | `rgba(148,163,184,.22)` | Bordas subtis |
| `--radius` | `16px` | Raio de borda padrão global |

### 2.2 Tipografia

| Página | Fonte principal | Fonte secundária | Fonte de sistema |
|---|---|---|---|
| `login.html` / `quantum.html` | Orbitron (wght: 400–900) — para títulos e botões | Exo 2 (wght: 300–800) — para corpo e inputs | — |
| `index.html` | Inter (wght: 400–800) | — | sans-serif |
| `chat.html` | Arial | — | sans-serif |

Fontes carregadas via Google Fonts CDN. O `index.html` usa `Inter` desde `fonts.googleapis.com`; o `login.html` usa `Orbitron` e `Exo 2` também via Google Fonts.

### 2.3 Efeito Glassmorphism

Implementado com:
```css
background: rgba(..., 0.6–0.85);
backdrop-filter: blur(14px–20px);
-webkit-backdrop-filter: blur(14px–20px);
border: 1px–2px solid rgba(cor, 0.2–0.3);
box-shadow: 0 16px–60px rgba(0,0,0,0.36–0.5);
border-radius: 16px–25px;
```

Usado em: cards de login, sidebar, topbar, cards de stats, chat shell, avatar container (quantum).

---

## 3. Páginas — Descrição Detalhada

### 3.1 `login.html` — Página de Autenticação

**Rota:** `GET /`  
**Estilo:** Cyberpunk neon, glassmorphism, fundo escuro com gradientes radiais e grelha animada.

#### Estrutura HTML

```
<body>
├── .animated-bg           (gradiente radial em rotação — z-index: 1)
├── .cyber-grid            (grelha 50×50 px com scrolling infinito — z-index: 2)
├── .particles#particles   (50 partículas de néon flutuantes — z-index: 3)
└── .login-container       (cartão central — max-width: 500px — z-index: 10)
    ├── .login-header
    │   ├── .logo-3d       (círculo "A" com pulse animado 3 s)
    │   ├── .login-title   ("ALICI™" — gradiente de texto cyan→purple)
    │   └── .login-subtitle ("Neural Access System")
    ├── .form-section
    │   ├── .tab-buttons   (2 abas: "Login" | "Registro")
    │   ├── #loginForm     (email + password + botão + loading spinner)
    │   └── #registerForm  (nome + email + password + botão + loading spinner)
    └── .login-footer      (copyright + link Termos de Uso)
```

#### Comportamento JavaScript (inline)

| Função | Responsabilidade |
|---|---|
| `createParticles()` | Gera 50 `<div class="particle">` com posição, velocidade e cor aleatórias |
| `switchTab(tab)` | Alterna entre `#loginForm` e `#registerForm` adicionando/removendo classe `.active` |
| `showMessage(id, msg)` | Exibe mensagem de erro ou sucesso no elemento identificado |
| `hideMessage(id)` | Oculta mensagem de feedback |
| `handleLogin()` | `POST /auth/login` → grava `access_token`, `refresh_token`, `alici_user` em `localStorage` → redireciona para `/chat` |
| `handleRegister()` | `POST /auth/register` → em sucesso, alterna para aba de login e pré-preenche o email |

#### Animações

| Elemento | Animação | Duração |
|---|---|---|
| `.animated-bg` | `bg-shift` — translate + scale + rotate | 20 s infinite |
| `.cyber-grid` | `grid-flow` — background-position +50 px | 3 s linear infinite |
| `.particle` | `float-up` — translateY 100 vh → -100 vh + translateX | 10–25 s linear infinite |
| `.login-container` | `container-appear` — translateY(50px) scale(0.9) → 0 | 0.8 s ease-out |
| `.logo-3d` | `logo-pulse` — scale 1→1.05, glow cyan→pink | 3 s ease-in-out infinite |
| `.tab-btn.active` | Gradiente cyan→purple, glow box-shadow | CSS transition 0.3 s |
| `.form-container.active` | `form-appear` — translateY(20px) → 0 | 0.5 s ease-out |
| `.error-message` | `shake` — translateX ±10 px | 0.5 s |
| `.spinner` | `spin` — rotate 360° | 1 s linear infinite |

#### Responsividade

| Breakpoint | Adaptação |
|---|---|
| `max-width: 600px` | `.login-container` max-width: 95%, margin: 20px; `.login-title` font-size: 2rem; `.logo-3d` 100×100 px |

---

### 3.2 `chat.html` — Interface de Chat

**Rota:** `GET /chat` e `GET /dashboard`  
**Estilo:** Minimalista dark, partículas de néon, indicador de estado da IA animado.

#### Estrutura HTML

```
<body>
├── #particles             (partículas geradas por JS — position: fixed, z-index: 0)
├── <header>
│   ├── #indicator         (círculo 12×12 px com glow — indica estado da IA)
│   └── #statusLabel       (texto: "Online" | "Analisando" | "Processando" | ...)
├── #messages              (área de mensagens — flex-column, overflow-y: auto)
│   └── .message (user-message | ai-message)
├── #inputArea             (flex row — background: #111827)
│   ├── #userInput         (input text)
│   └── <button>           (Enviar — background: #00ffff)
└── .logout                (position: absolute top:15px right:15px — "Sair")
```

#### Sistema de Estados da IA (indicador visual)

| Estado | Cor (#) | Glow | Label |
|---|---|---|---|
| `online` | `#00ffff` | `0 0 20px #00ffff` | "Online" |
| `analyze` | `#ff0099` | `0 0 40px #ff0099` | "Analisando" |
| `process` | `#00ff66` | `0 0 40px #00ff66` | "Processando" |
| `learn` | `#ffcc00` | `0 0 40px #ffcc00` | "Aprendendo" |
| `respond` | `#00ffff` | `0 0 40px #00ffff` | "Respondendo" |

#### Comportamento JavaScript (inline)

| Função | Responsabilidade |
|---|---|
| `createParticles()` | Gera 60 partículas com 5 cores de néon; recriadas a cada 40 s |
| `changeState(state)` | Altera cor e texto do indicador de estado via `states` map |
| `addMessage(text, sender)` | Adiciona `<div class="message [sender]-message">` e faz scroll automático |
| `sendMsg()` | Lê input → `addMessage` → sequência de estados (analyze → process → respond → online) → `POST /chat` com `Authorization: Bearer <token>` → exibe resposta |
| `handleKey(e)` | Intercepta Enter (sem Shift) para submeter |
| `logout()` | Remove `access_token`, `refresh_token`, `alici_user` do `localStorage` → redireciona para `/` |

#### Chamada de API realizada

```
POST /chat
Headers: { Content-Type: application/json, Authorization: Bearer <access_token> }
Body:    { "pergunta": "<mensagem>", "incluir_emocao": false }
Response campo lido: data.resposta
```

#### Observação de Segurança

O `DOMContentLoaded` verifica `localStorage.getItem('alici_token')` (chave legada), mas o login em `login.html` grava `access_token`. Existe inconsistência entre as duas chaves que pode impedir a verificação de sessão ao entrar na página `/chat` directamente.

---

### 3.3 `index.html` — Plataforma SaaS (Dashboard)

**Rota:** Não exposto activamente (template extra).  
**Estilo:** SaaS moderno, glassmorphism em tons de azul/ciano escuro, suporte a tema claro/escuro, sidebar recolhível, Chart.js e Lucide Icons.

#### Estrutura HTML

```
<body>
├── #appLoader (.app-loader)        (ecrã de carregamento — desaparece após 900 ms)
├── #particlesCanvas                (canvas HTML5 — partículas flutuantes, z-index: -1)
│
├── #loginScreen (.login-screen)    (visível até autenticar)
│   └── .login-card.glass
│       ├── .brand-block            (logo, título, subtítulo)
│       └── #loginForm              (email, password, botão "Entrar")
│
└── #app (.app) [hidden até login]
    ├── <aside #sidebar .sidebar.glass>
    │   ├── .sidebar-top
    │   │   ├── #closeSidebarBtn    (mobile: fecha sidebar)
    │   │   ├── .logo-wrap          (logo mark "A" + "ALICI / AI Platform")
    │   │   └── .nav-menu           (5 botões: Dashboard, Chat IA, Modelos, Analytics, Configurações)
    │   └── #toggleSidebarBtn       (colapsa sidebar para 90 px em desktop)
    │
    ├── #sidebarOverlay             (overlay escuro em mobile quando sidebar aberta)
    │
    └── <main .main-shell>
        ├── <header .topbar.glass>  (sticky top:12px)
        │   ├── .topbar-left        (#openSidebarBtn + #sectionTitle)
        │   └── .topbar-actions     (#themeToggle + #notifyBtn com badge)
        │
        ├── #dashboard (.app-section.active)
        │   ├── .stats-grid         (4 stat-cards: Usuários Online, Requisições, Uso Modelo, Status API)
        │   └── .chart-card         (Chart.js — gráfico de linha "Requisições por Hora")
        │
        ├── #chat (.app-section)
        │   └── .chat-shell.glass
        │       ├── #chatMessages   (mensagens — 1 welcome message inicial)
        │       └── #chatForm       (#chatInput + botão "Enviar")
        │
        ├── #models (.app-section)  (placeholder — "Gerencie versões...")
        ├── #analytics (.app-section) (placeholder — "Métricas operacionais...")
        └── #settings (.app-section)  (placeholder — "Preferências de conta...")
    │
└── #notifications                  (container de toasts — fixed top:18px right:18px)
```

#### Comportamento JavaScript (`Static/js/app.js`)

| Função | Responsabilidade |
|---|---|
| `initializeApp()` | Orquestra inicialização: tema, bindings, partículas, chart, ícones Lucide, boot loader |
| `bootLoader()` | Adiciona classe `.hide` ao `#appLoader` após 900 ms |
| `bindUI()` | Regista todos os event listeners; se `alici_jwt` existe em localStorage, desbloqueia app |
| `login()` | Grava `alici_jwt` fictício no localStorage → chama `unlockApp()` (sem chamada à API real) |
| `unlockApp()` | Oculta `#loginScreen`, mostra `#app`, chama `autoScroll()` |
| `showSection(id)` | Troca secção activa, actualiza nav e título do topbar |
| `toggleSidebar()` | Alterna classe `.sidebar-collapsed` no `#app` (desktop: 280 px ↔ 90 px) |
| `closeMobileSidebar()` | Remove `.sidebar-open` do `#app` |
| `appendMessage(content, role)` | Cria `<article class="message user/assistant-message">` e faz scroll |
| `createTypingLoader()` | Cria indicador de digitação (3 pontos animados) com `id="typingLoader"` |
| `removeTypingLoader()` | Remove o indicador de digitação |
| `sendMessage()` | `POST /chat` com `{ message: userMessage }` (sem token JWT — campo `message` não é o campo esperado pelo backend que usa `pergunta`) |
| `showNotification(msg, type)` | Toast com auto-remoção após 2600 ms + fade out de 200 ms |
| `toggleTheme()` | Alterna `data-theme` entre `dark` e `light`, persiste em `localStorage`, recria chart |
| `initializeChart()` | Chart.js — gráfico de linha com dados estáticos para demonstração |
| `initializeParticles()` | Canvas 2D — 80 partículas ciano com velocidade aleatória |

> **Nota:** O `login()` em `index.html` não faz chamada real à API. É uma simulação local (grava `alici_jwt` no localStorage). Para integração real, deve usar `POST /auth/login` como implementado em `login.html`.

#### Estado da Aplicação

```javascript
const state = {
  currentSection: 'dashboard',   // secção activa
  chart: null,                   // instância Chart.js
  theme: 'dark' | 'light',       // tema persistido em localStorage('alici_theme')
  sidebarCollapsed: false        // sidebar recolhida (desktop)
};
```

#### Dependências Externas

| Biblioteca | Versão / CDN | Uso |
|---|---|---|
| Chart.js | `cdn.jsdelivr.net/npm/chart.js` | Gráfico de requisições por hora |
| Lucide Icons | `unpkg.com/lucide@latest` | Ícones vectoriais (menu, bell, moon, etc.) |
| Google Fonts (Inter) | `fonts.googleapis.com` | Tipografia SaaS |

---

### 3.4 `quantum.html` — Interface Neural Experimental

**Rota:** Não exposto em rota activa.  
**Estilo:** Cyberpunk avançado com avatar da ALICI, grelha animada, partículas, painéis de stats em tempo real e chat integrado.

#### Estrutura HTML (resumida)

```
<body>
├── .animated-bg          (gradiente radial em rotação — z-index: 1)
├── .cyber-grid           (grelha 50×50 px com scrolling — z-index: 2)
├── .particles#particles  (partículas geradas por JS — z-index: 3)
└── .container            (max-width: 1600px — z-index: 10)
    ├── .futuristic-header
    │   ├── .alici-logo-container
    │   │   └── .logo-3d  (rotação 3D 360° em 20 s, glow pulse cyan↔pink)
    │   ├── .title-futuristic  ("ALICI™" — gradiente animado cyan→pink→purple, 5 s)
    │   └── .subtitle-futuristic  (flicker animation, letra-espaçamento 5 px)
    └── .main-interface   (grid 2 col: 1fr 550px)
        ├── .chat-glass   (painel de chat — borda 2px néon, shine-sweep animation)
        │   ├── .chat-header-glass
        │   │   ├── .chat-title    ("ALICI™ Neural Chat")
        │   │   └── .status-bar    (dot pulsante + texto de estado)
        │   ├── .messages-area    (height: 500px, overflow-y: auto)
        │   └── .input-zone
        │       └── .input-container
        │           ├── .cyber-input  (foco: glow cyan→pink)
        │           └── .send-btn     (shine sweep hover)
        └── .avatar-section   (sticky top: 20px)
            └── .avatar-container
                ├── .avatar-title  ("Interface Visual")
                ├── .avatar-display
                │   ├── .avatar-img     (imagem estado da ALICI — muda com estado)
                │   ├── .avatar-overlay (scan diagonal cyan + pink — mix-blend: screen)
                │   └── .scan-lines     (linhas horizontais 2 px — move 4 s)
                └── .status-panel   (indicador + texto de estado)
```

#### Sistema de Avatar por Estado

| Estado | Imagem | Cor do indicador |
|---|---|---|
| idle | `Static/Imagens/Avatar/alici_idle.jpg` | cyan `#00ffff` |
| listening | `Static/Imagens/Avatar/alici_listening.jpg` | verde `#00ff66` |
| thinking | `Static/Imagens/Avatar/alici_thinking.jpeg` | amarelo `#ffcc00` |
| speaking | `Static/Imagens/Avatar/alici_speaking.jpg` | pink `#ff0099` |

---

## 4. Assets de Avatar

Localizados em `Static/Imagens/Avatar/`:

| Ficheiro | Estado | Tamanho aproximado |
|---|---|---|
| `alici_idle.jpg` | Repouso / aguardando | ~313 KB |
| `alici_listening.jpg` | A ouvir / receber input | ~391 KB |
| `alici_thinking.jpeg` | A processar / pensar | ~386 KB |
| `alici_speaking.jpg` | A responder / falar | ~402 KB |
| `IMG_1795.jpeg` | Imagem adicional | ~419 KB |
| `IMG_1806.jpeg` | Imagem adicional | ~354 KB |
| `IMG_1807.jpeg` | Imagem adicional | ~402 KB |
| `IMG_1809.jpeg` | Imagem adicional | ~386 KB |

---

## 5. Folha de Estilos Global (`Static/css/style.css`)

Usada exclusivamente pelo `index.html`. Contém **609 linhas** de CSS puro.

### Componentes documentados

| Componente | Classe CSS | Descrição |
|---|---|---|
| Ecrã de carregamento | `.app-loader` | Fixed inset:0, grid center, fundo semitransparente escuro, fade com `.hide` |
| Anel de carregamento | `.loader-orbit` | 74×74 px, borda rotativa, 1 s linear infinite |
| Ecrã de login | `.login-screen` | min-height: 100vh, grid center, padding: 24px |
| Cartão de login | `.login-card` | width: min(420px,100%), padding: 28px, glassmorphism |
| Ponto de marca | `.brand-dot` | 10×10 px, blink 1.6 s ease-in-out, gradiente tricolor |
| Formulário de login | `.login-form` | display: grid, gap: 10px |
| Botão primário | `.btn-primary` | Gradiente electric-blue→cyan, hover: translateY(-1px) + brightness |
| App shell | `.app` | min-height: 100vh, grid 2 col (280px 1fr), collapse via `.sidebar-collapsed` (90px 1fr) |
| Sidebar | `.sidebar` | sticky, height: 100vh, flex column, justify-content: space-between |
| Item de navegação | `.nav-item` | border transparent→var(--border), hover/active: background azul 16%, translateY(-1px) |
| Topbar | `.topbar` | sticky top:12px, flex, glass, padding: 10px 12px |
| Badge de notificação | `.badge` | position absolute, top/right -4px, background #ef4444, font-size .65rem |
| Secção de app | `.app-section` | display: none → `.active`: display block, animação `sectionIn` 0.28 s |
| Grid de stats | `.stats-grid` | grid 4 col → 2 col (≤1024px) → 1 col (≤768px) |
| Chat shell | `.chat-shell` | min-height calc(100vh - 146px), grid 2 rows (1fr auto) |
| Mensagem do utilizador | `.user-message` | justify-self: end, gradiente blue→cyan, cor: #f8fbff |
| Mensagem do assistente | `.assistant-message` | justify-self: start, background rgba cinza claro, borda |
| Loader de digitação | `.loading-message span` | 8×8 px, animação `jump` escalonada (0, 0.12, 0.24 s) |
| Input de chat | `.chat-input-wrap` | sticky bottom:0, grid 2 col (1fr auto), borda topo |
| Toast de notificação | `.toast` | fixed top:18px right:18px, min-width: 260px, animação `toastIn` |

### Breakpoints de Responsividade

| Breakpoint | Comportamento |
|---|---|
| `max-width: 1024px` | Stats grid passa de 4 para 2 colunas |
| `max-width: 768px` | App shell passa para 1 coluna; sidebar torna-se fixed + off-canvas; `.mobile-only` fica visível |

---

## 6. Script de Aplicação (`Static/js/app.js`)

Ficheiro de **113 linhas** em JavaScript vanilla, denso (formatação compacta). Usado apenas pelo `index.html`.

### Fluxo de Inicialização

```
DOMContentLoaded
└── initializeApp()
    ├── initializeTheme()        → aplica data-theme do localStorage
    ├── bindUI()                 → regista todos os event listeners
    ├── initializeParticles()    → cria canvas de partículas 80 pontos
    ├── initializeChart()        → cria Chart.js com dados estáticos
    ├── initializeLucide()       → renderiza ícones Lucide
    └── bootLoader()             → esconde loader após 900 ms
```

### Integração API (index.html)

A chamada a `POST /chat` em `app.js` usa `{ message: userMessage }` como corpo, enquanto o backend espera `{ pergunta: string }`. Esta inconsistência resulta em erro de validação (HTTP 422) quando o endpoint real está activo.

---

## 7. Catálogo de Animações

| Nome da animação | Ficheiro | Efeito |
|---|---|---|
| `bg-shift` | login / quantum | Gradiente radial de fundo em translate + scale + rotate, 20 s |
| `grid-flow` | login / quantum | Grelha CSS com background-position +50 px, 3 s |
| `float-up` | login / quantum | Partículas sobem de 100vh a -100vh com fade, 10–25 s |
| `float` | chat.html | Variante simples de float-up para partículas, 10–25 s |
| `logo-rotate-3d` | quantum | rotateY 360° + rotateX 10° em 20 s com perspectiva 1000px (CSS 3D) |
| `logo-glow-pulse` | quantum | Alternância glow cyan ↔ pink na face do logo, 3 s |
| `gradient-flow` | quantum | Gradiente de texto move background-position 0%→100%→0%, 5 s |
| `text-flicker` | quantum | Opacidade 1↔0.8 + text-shadow pulsante, 4 s |
| `shine-sweep` | quantum | Faixa de brilho diagonal percorre chat panel, 6 s |
| `overlay-scan` | quantum | Gradiente diagonal duplo (cyan + pink) percorre avatar, 8 s |
| `scan-move` | quantum | Linhas horizontais 2 px sobem continuamente, 4 s |
| `message-appear` | quantum | opacity 0→1 + translateY(20px)→0 + scale(0.95)→1, 0.6 s |
| `container-appear` | login | Cartão principal sobe e escala ao carregar, 0.8 s |
| `logo-pulse` | login | Logo 3D pulsa entre scale 1 e 1.05 alternando glow, 3 s |
| `form-appear` | login | Formulário de aba desce suavemente ao activar, 0.5 s |
| `shake` | login | Mensagem de erro vibra ±10 px, 0.5 s |
| `dot-pulse` | quantum | Indicador de status escala 1→1.5 com glow, 2 s |
| `indicator-glow` | quantum | Glow 20px→60px do indicador de estado, 2 s |
| `blink` | index.html | Ponto de marca pulsa opacidade 0.35→1, 1.6 s |
| `spin` | login / index | Spinner de carregamento rotaciona 360°, 1 s |
| `pulse` | index.html | Pulse dot do status online emite ondas de cor, 1.4 s |
| `jump` | index.html | Dots do typing loader saltam verticalmente, 0.8 s escalonado |
| `sectionIn` | index.html | Secção activa aparece com translateY(8px)→0, 0.28 s |
| `msgIn` | index.html | Mensagem de chat entra com translateY(6px)→0, 0.24 s |
| `toastIn` | index.html | Toast aparece com translateX(8px)→0, 0.22 s |

---

## 8. Integração API — Resumo por Página

| Página | Endpoint chamado | Método | Autenticação | Campo enviado | Campo lido |
|---|---|---|---|---|---|
| `login.html` | `/auth/login` | POST | Não | `{ email, senha }` | `data.access_token`, `data.refresh_token`, `data.usuario` |
| `login.html` | `/auth/register` | POST | Não | `{ nome, email, senha }` | — (verifica `response.ok`) |
| `chat.html` | `/chat` | POST | Bearer token (localStorage) | `{ pergunta, incluir_emocao }` | `data.resposta` |
| `index.html` | `/chat` | POST | Sem token ⚠️ | `{ message }` ⚠️ | `data.response \| data.reply \| data.message` ⚠️ |

> ⚠️ A integração em `index.html/app.js` usa campos incorrectos (`message` em vez de `pergunta`) e não envia token JWT. Requer correcção para funcionar com o backend real.

---

## 9. Gestão de Sessão (localStorage)

| Chave | Gravada por | Lida por | Conteúdo |
|---|---|---|---|
| `access_token` | `login.html` (handleLogin) | `chat.html` (sendMsg) | JWT de acesso |
| `refresh_token` | `login.html` (handleLogin) | — (não usado no frontend) | JWT de refresh |
| `alici_user` | `login.html` (handleLogin) | — (disponível, não lida) | JSON com id, nome, email, plano |
| `alici_token` | — (não gravado) | `chat.html` (DOMContentLoaded) ⚠️ | Chave legada — nunca gravada |
| `alici_jwt` | `index.html` (login simulado) | `index.html` (bindUI) | Token simulado fictício |
| `alici_theme` | `index.html` (toggleTheme) | `index.html` (state init) | `'dark'` \| `'light'` |

---

## 10. Acessibilidade

| Elemento | Atributo de Acessibilidade | Observação |
|---|---|---|
| `#appLoader` | `aria-live="polite"`, `aria-label="Carregando aplicação"` | Anuncia carregamento a leitores de ecrã |
| `#particlesCanvas` | `aria-hidden="true"` | Decorativo — ignorado por tecnologias de assistência |
| `#closeSidebarBtn` | `aria-label="Fechar menu"` | Identificado para leitores de ecrã |
| `#toggleSidebarBtn` | `aria-label="Recolher menu"` | Identificado para leitores de ecrã |
| `#openSidebarBtn` | `aria-label="Abrir menu"` | Identificado para leitores de ecrã |
| `#themeToggle` | `aria-label="Alternar tema"` | Identificado para leitores de ecrã |
| `#notifyBtn` | `aria-label="Notificações"` | Identificado para leitores de ecrã |
| `button:focus-visible`, `input:focus-visible` | `outline: 2px solid rgba(34,211,238,.55)` | Foco visível acessível em `style.css` |

---

## 11. Limitações e Recomendações

| Limitação | Recomendação |
|---|---|
| `index.html` usa login simulado sem chamar a API | Substituir `login()` em `app.js` por chamada real a `POST /auth/login`, igual ao `login.html` |
| `app.js` envia `{ message }` em vez de `{ pergunta }` para `POST /chat` | Corrigir o corpo do pedido e adicionar header `Authorization: Bearer <token>` |
| Inconsistência de chave localStorage (`alici_token` vs `access_token`) em `chat.html` | Uniformizar para `access_token` em todas as páginas |
| Dados do Dashboard (Usuários Online, Requisições) são estáticos | Ligar aos endpoints `/health` e `/api/status` para dados reais |
| Dados do gráfico Chart.js são hard-coded | Criar endpoint de métricas agregadas e alimentar o gráfico com dados reais |
| `quantum.html` não está exposto em nenhuma rota | Avaliar exposição ou remoção; adicionar rota em `alici_api/routes/pages.py` se necessário |
| Sem CSP (Content Security Policy) nas páginas | Adicionar header `Content-Security-Policy` via middleware FastAPI |
| Partículas recriadas a cada 40 s em `chat.html` sem limpeza da anterior | Limpar partículas anteriores antes de recriar para evitar acumulação no DOM |
| Sem tratamento de refresh token automático no frontend | Implementar interceptor que, ao receber 401, chame `POST /auth/refresh` e repita o pedido |

---

## 12. Referências

- [README.md](./README.md) — Documentação da API (variáveis, rotas, execução)
- [RELATORIO_COMPLETO_PROJECTO.md](./RELATORIO_COMPLETO_PROJECTO.md) — Relatório completo do projecto (arquitectura, backend, base de dados)
- [FICHA_TECNICA_MODELO_ALICI_CPU_SIMPLE.md](./FICHA_TECNICA_MODELO_ALICI_CPU_SIMPLE.md) — Ficha técnica do modelo NLP
- `alici_api/routes/pages.py` — Roteamento das páginas HTML
- `Static/css/style.css` — Folha de estilos do dashboard (`index.html`)
- `Static/js/app.js` — Script de lógica do dashboard (`index.html`)
