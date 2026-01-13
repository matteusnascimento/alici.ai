import os
from flask import Flask, request, jsonify, render_template_string
from engine import gerar_resposta

# Inicializar a aplicação Flask
app = Flask(__name__)

# Rota principal para servir a interface web da Alici com design holográfico e avatar animado
@app.route("/")
def home():
    html_content = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alici - IA Holográfica com Avatar Animado</title>
    <style>
        :root {
            --hologram-primary: #00ffff;
            --hologram-secondary: #00ffaa;
            --hologram-accent: #ff00ff;
            --dark-bg: #000011;
            --darker-bg: #000000;
            --card-bg: #001122;
            --text-light: #e0ffff;
            --text-secondary: #a0dddd;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, var(--darker-bg), var(--dark-bg), #001133);
            color: var(--text-light);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }
        
        /* Efeitos holográficos de fundo */
        .hologram-grid {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                linear-gradient(rgba(0, 255, 255, 0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 255, 0.05) 1px, transparent 1px);
            background-size: 30px 30px;
            pointer-events: none;
            z-index: 1;
        }
        
        .hologram-particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 2;
        }
        
        .particle {
            position: absolute;
            width: 2px;
            height: 2px;
            background: var(--hologram-primary);
            border-radius: 50%;
            animation: float 8s infinite linear;
            opacity: 0.7;
        }
        
        @keyframes float {
            0% { 
                transform: translateY(100vh) translateX(0) rotate(0deg); 
                opacity: 0;
            }
            10% { opacity: 0.7; }
            90% { opacity: 0.7; }
            100% { 
                transform: translateY(-10px) translateX(20px) rotate(360deg); 
                opacity: 0;
            }
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
            z-index: 3;
        }
        
        header {
            text-align: center;
            padding: 30px 0;
            position: relative;
        }
        
        .logo-container {
            width: 120px;
            height: 120px;
            margin: 0 auto 20px;
            position: relative;
        }
        
        .logo {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: radial-gradient(circle, var(--hologram-primary), var(--hologram-secondary));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            font-weight: bold;
            box-shadow: 
                0 0 30px rgba(0, 255, 255, 0.5),
                inset 0 0 20px rgba(255, 255, 255, 0.3);
            animation: hologram-pulse 3s infinite;
            border: 2px solid var(--hologram-primary);
            position: relative;
            overflow: hidden;
        }
        
        .logo::before {
            content: "";
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            animation: shine 4s infinite;
        }
        
        @keyframes shine {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes hologram-pulse {
            0% { 
                box-shadow: 
                    0 0 30px rgba(0, 255, 255, 0.5),
                    inset 0 0 20px rgba(255, 255, 255, 0.3);
                transform: scale(1);
            }
            50% { 
                box-shadow: 
                    0 0 50px rgba(0, 255, 255, 0.8),
                    inset 0 0 30px rgba(255, 255, 255, 0.5);
                transform: scale(1.05);
            }
            100% { 
                box-shadow: 
                    0 0 30px rgba(0, 255, 255, 0.5),
                    inset 0 0 20px rgba(255, 255, 255, 0.3);
                transform: scale(1);
            }
        }
        
        h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            background: linear-gradient(90deg, var(--hologram-primary), var(--hologram-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
            position: relative;
        }
        
        .subtitle {
            font-size: 1.2rem;
            opacity: 0.8;
            margin-bottom: 30px;
            color: var(--text-secondary);
        }
        
        .main-content {
            display: flex;
            gap: 30px;
            margin: 20px 0;
        }
        
        .chat-section {
            flex: 1;
        }
        
        .hologram-section {
            flex: 0 0 400px;
        }
        
        .chat-container {
            background: rgba(0, 17, 34, 0.8);
            backdrop-filter: blur(15px);
            border-radius: 25px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 
                0 0 30px rgba(0, 255, 255, 0.2),
                inset 0 0 20px rgba(0, 255, 255, 0.1);
            border: 1px solid rgba(0, 255, 255, 0.3);
            position: relative;
        }
        
        .chat-container::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, transparent, rgba(0, 255, 255, 0.05), transparent);
            border-radius: 25px;
            pointer-events: none;
        }
        
        .chat-history {
            height: 450px;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            border: 1px solid rgba(0, 255, 255, 0.2);
            position: relative;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 15px 20px;
            border-radius: 20px;
            animation: messageSlide 0.4s ease-out;
            max-width: 85%;
            word-wrap: break-word;
            line-height: 1.5;
        }
        
        @keyframes messageSlide {
            from { 
                opacity: 0; 
                transform: translateY(20px) scale(0.95); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0) scale(1); 
            }
        }
        
        .user-message {
            background: linear-gradient(135deg, var(--hologram-primary), var(--hologram-secondary));
            margin-left: auto;
            text-align: right;
            box-shadow: 0 5px 15px rgba(0, 255, 255, 0.3);
            color: var(--dark-bg);
            font-weight: 500;
        }
        
        .ai-message {
            background: rgba(0, 255, 255, 0.15);
            margin-right: auto;
            border: 1px solid rgba(0, 255, 255, 0.3);
            position: relative;
            box-shadow: 0 5px 15px rgba(0, 255, 255, 0.1);
        }
        
        .ai-message::before {
            content: "🤖";
            position: absolute;
            left: -35px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 20px;
            background: rgba(0, 255, 255, 0.2);
            padding: 5px;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .input-area {
            display: flex;
            gap: 15px;
            align-items: center;
            padding: 15px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 25px;
            border: 1px solid rgba(0, 255, 255, 0.3);
        }
        
        input {
            flex: 1;
            padding: 15px 25px;
            border: none;
            border-radius: 25px;
            background: rgba(0, 255, 255, 0.1);
            color: var(--text-light);
            font-size: 16px;
            outline: none;
            transition: all 0.3s ease;
        }
        
        input:focus {
            background: rgba(0, 255, 255, 0.15);
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.2);
        }
        
        input::placeholder {
            color: rgba(224, 255, 255, 0.6);
        }
        
        button {
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            background: linear-gradient(135deg, var(--hologram-primary), var(--hologram-accent));
            color: var(--dark-bg);
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0, 255, 255, 0.4);
            font-size: 16px;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 255, 255, 0.6);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        /* Seção holográfica com avatar animado */
        .hologram-container {
            background: rgba(0, 17, 34, 0.8);
            backdrop-filter: blur(15px);
            border-radius: 25px;
            padding: 25px;
            box-shadow: 
                0 0 30px rgba(0, 255, 255, 0.2),
                inset 0 0 20px rgba(0, 255, 255, 0.1);
            border: 1px solid rgba(0, 255, 255, 0.3);
            height: fit-content;
            position: sticky;
            top: 20px;
        }
        
        .hologram-title {
            text-align: center;
            margin-bottom: 20px;
            font-size: 1.5rem;
            color: var(--hologram-primary);
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.3);
        }
        
        .hologram-display {
            width: 100%;
            height: 350px;
            background: linear-gradient(135deg, var(--darker-bg), var(--dark-bg));
            border-radius: 20px;
            margin-bottom: 20px;
            position: relative;
            overflow: hidden;
            border: 1px solid rgba(0, 255, 255, 0.3);
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.1);
        }
        
        .alici-avatar {
            width: 100%;
            height: 100%;
            position: relative;
            border-radius: 18px;
            overflow: hidden;
        }
        
        .avatar-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 18px;
            transition: all 0.3s ease;
            opacity: 1;
            position: absolute;
            top: 0;
            left: 0;
        }
        
        .avatar-image.hidden {
            opacity: 0;
        }
        
        /* Efeitos holográficos sobre o avatar */
        .alici-avatar::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, transparent, rgba(0, 255, 255, 0.1), transparent);
            animation: scan-line 3s infinite;
            border-radius: 18px;
            z-index: 2;
        }
        
        .alici-avatar::after {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 30% 40%, rgba(0, 255, 255, 0.1) 0%, transparent 30%),
                radial-gradient(circle at 70% 60%, rgba(0, 255, 170, 0.1) 0%, transparent 30%);
            border-radius: 18px;
            z-index: 1;
        }
        
        @keyframes scan-line {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(100%); }
        }
        
        /* Animação de movimento da boca */
        @keyframes mouth-movement {
            0%, 100% { transform: scaleY(1); }
            25% { transform: scaleY(1.1); }
            50% { transform: scaleY(0.9); }
            75% { transform: scaleY(1.05); }
        }
        
        .avatar-speaking {
            animation: mouth-movement 0.5s ease-in-out infinite;
        }
        
        /* Animação de piscada */
        @keyframes blink {
            0%, 90%, 100% { transform: scaleY(1); }
            95% { transform: scaleY(0.1); }
        }
        
        .avatar-blinking {
            animation: blink 3s ease-in-out infinite;
        }
        
        /* Animação de respiração */
        @keyframes breathing {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
        
        .avatar-breathing {
            animation: breathing 4s ease-in-out infinite;
        }
        
        .hologram-status {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 25px;
            margin-bottom: 20px;
            border: 1px solid rgba(0, 255, 255, 0.2);
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: var(--hologram-primary);
            animation: status-pulse 2s infinite;
            box-shadow: 0 0 10px var(--hologram-primary);
        }
        
        @keyframes status-pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.6; transform: scale(1.2); }
        }
        
        .status-text {
            font-size: 0.9rem;
            color: var(--text-light);
            font-weight: 500;
        }
        
        .hologram-controls {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-top: 20px;
        }
        
        .hologram-btn {
            padding: 12px 15px;
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 15px;
            background: rgba(0, 0, 0, 0.3);
            color: var(--text-light);
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.85rem;
            font-weight: 500;
            text-align: center;
        }
        
        .hologram-btn:hover {
            background: rgba(0, 255, 255, 0.2);
            border-color: rgba(0, 255, 255, 0.6);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 255, 0.2);
        }
        
        .hologram-btn.active {
            background: rgba(0, 255, 255, 0.3);
            border-color: rgba(0, 255, 255, 0.8);
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.3);
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }
        
        .feature-card {
            background: rgba(0, 17, 34, 0.8);
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(0, 255, 255, 0.2);
            backdrop-filter: blur(10px);
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            background: rgba(0, 17, 34, 0.9);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            border-color: rgba(0, 255, 255, 0.4);
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
            background: linear-gradient(90deg, var(--hologram-primary), var(--hologram-secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .feature-title {
            font-size: 1.3rem;
            margin-bottom: 10px;
            color: var(--text-light);
        }
        
        .feature-desc {
            opacity: 0.8;
            font-size: 0.9rem;
            color: var(--text-secondary);
            line-height: 1.5;
        }
        
        footer {
            text-align: center;
            padding: 30px 0;
            opacity: 0.6;
            font-size: 0.9rem;
            margin-top: 40px;
            border-top: 1px solid rgba(0, 255, 255, 0.1);
        }
        
        /* Responsividade */
        @media (max-width: 1024px) {
            .main-content {
                flex-direction: column;
            }
            
            .hologram-section {
                flex: none;
                order: -1;
            }
            
            .hologram-container {
                position: static;
            }
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            
            h1 {
                font-size: 2.5rem;
            }
            
            .chat-history {
                height: 350px;
            }
            
            .input-area {
                flex-direction: column;
                gap: 10px;
            }
            
            .features {
                grid-template-columns: 1fr;
            }
            
            .hologram-display {
                height: 280px;
            }
        }
        
        /* Scrollbar personalizada */
        .chat-history::-webkit-scrollbar {
            width: 6px;
        }
        
        .chat-history::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 3px;
        }
        
        .chat-history::-webkit-scrollbar-thumb {
            background: rgba(0, 255, 255, 0.3);
            border-radius: 3px;
        }
        
        .chat-history::-webkit-scrollbar-thumb:hover {
            background: rgba(0, 255, 255, 0.5);
        }
    </style>
</head>
<body>
    <!-- Efeitos holográficos de fundo -->
    <div class="hologram-grid"></div>
    <div class="hologram-particles" id="particles"></div>
    
    <div class="container">
        <header>
            <div class="logo-container">
                <div class="logo">A</div>
            </div>
            <h1>Alici 🤖</h1>
            <p class="subtitle">Inteligência Artificial Holográfica com Avatar Animado</p>
        </header>
        
        <div class="main-content">
            <div class="chat-section">
                <div class="chat-container">
                    <div class="chat-history" id="chatHistory">
                        <div class="message ai-message">
                            Olá! Eu sou a Alici, sua assistente de IA holográfica com avatar animado. Como posso ajudar você hoje?
                        </div>
                    </div>
                    <div class="input-area">
                        <input type="text" id="userInput" placeholder="Digite sua mensagem para a Alici..." onkeypress="handleKeyPress(event)">
                        <button onclick="sendMessage()">Enviar</button>
                    </div>
                </div>
                
                <div class="features">
                    <div class="feature-card">
                        <div class="feature-icon">🧠</div>
                        <h3 class="feature-title">Memória Persistente</h3>
                        <p class="feature-desc">Aprendo com cada interação e guardo conhecimento no banco de dados PostgreSQL</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🎭</div>
                        <h3 class="feature-title">Avatar Animado</h3>
                        <p class="feature-desc">Avatar cyberpunk com animações faciais, movimentos da boca e expressões realistas</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🌐</div>
                        <h3 class="feature-title">Busca na Web</h3>
                        <p class="feature-desc">Quando não sei algo, busco informações atualizadas na internet</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">⚡</div>
                        <h3 class="feature-title">Respostas Rápidas</h3>
                        <p class="feature-desc">Processo perguntas e gero respostas em milissegundos com Flask</p>
                    </div>
                </div>
            </div>
            
            <div class="hologram-section">
                <div class="hologram-container">
                    <h3 class="hologram-title">Alici Avatar</h3>
                    <div class="hologram-display">
                        <div class="alici-avatar" id="aliciAvatar">
                            <!-- Avatar principal - estado idle -->
                            <img src="/static/images/avatar/alici_idle.jpg" 
                                 alt="Alici Avatar Idle" 
                                 class="avatar-image avatar-breathing" 
                                 id="avatarIdle">
                            
                            <!-- Avatar falando - com movimento da boca -->
                            <img src="/static/images/avatar/alici_speaking.jpg" 
                                 alt="Alici Avatar Speaking" 
                                 class="avatar-image avatar-speaking hidden" 
                                 id="avatarSpeaking">
                            
                            <!-- Avatar ouvindo -->
                            <img src="/static/images/avatar/alici_listening.jpg" 
                                 alt="Alici Avatar Listening" 
                                 class="avatar-image hidden" 
                                 id="avatarListening">
                            
                            <!-- Avatar pensando -->
                            <img src="/static/images/avatar/alici_thinking.jpg" 
                                 alt="Alici Avatar Thinking" 
                                 class="avatar-image hidden" 
                                 id="avatarThinking">
                        </div>
                    </div>
                    <div class="hologram-status">
                        <div class="status-indicator" id="statusIndicator"></div>
                        <div class="status-text" id="statusText">Online e pronta para ajudar</div>
                    </div>
                    <div class="hologram-controls">
                        <button class="hologram-btn" onclick="changeAvatarState('listen')">👂 Ouvir</button>
                        <button class="hologram-btn" onclick="changeAvatarState('think')">🧠 Pensar</button>
                        <button class="hologram-btn" onclick="changeAvatarState('speak')">💬 Falar</button>
                        <button class="hologram-btn" onclick="changeAvatarState('greet')">👋 Saudar</button>
                    </div>
                </div>
            </div>
        </div>
        
        <footer>
            <p>Alici AI v2.0 | IA Holográfica com Avatar Animado | © 2026</p>
        </footer>
    </div>
    
    <script>
        // Variáveis globais para controle do avatar
        let currentAvatarState = 'idle';
        let speakingInterval = null;
        let blinkInterval = null;
        
        // Criar partículas holográficas
        function createHologramParticles() {
            const particlesContainer = document.getElementById('particles');
            const particleCount = 60;
            
            for (let i = 0; i < particleCount; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.animationDelay = Math.random() * 8 + 's';
                particle.style.animationDuration = (Math.random() * 4 + 4) + 's';
                particle.style.opacity = Math.random() * 0.5 + 0.3;
                particlesContainer.appendChild(particle);
            }
        }
        
        // Inicializar partículas
        createHologramParticles();
        
        // Função para trocar estado do avatar
        function changeAvatarState(state) {
            const avatarImages = document.querySelectorAll('.avatar-image');
            const statusText = document.getElementById('statusText');
            const statusIndicator = document.getElementById('statusIndicator');
            const buttons = document.querySelectorAll('.hologram-btn');
            
            // Limpar intervalos anteriores
            if (speakingInterval) {
                clearInterval(speakingInterval);
                speakingInterval = null;
            }
            
            // Esconder todas as imagens
            avatarImages.forEach(img => {
                img.classList.add('hidden');
                img.classList.remove('avatar-speaking', 'avatar-breathing', 'avatar-blinking');
            });
            
            // Remover classe active de todos os botões
            buttons.forEach(btn => btn.classList.remove('active'));
            
            currentAvatarState = state;
            
            switch(state) {
                case 'listen':
                    document.getElementById('avatarListening').classList.remove('hidden');
                    document.getElementById('avatarListening').classList.add('avatar-blinking');
                    statusText.textContent = 'Ouvindo sua mensagem...';
                    statusIndicator.style.background = '#00aaff';
                    statusIndicator.style.boxShadow = '0 0 10px #00aaff';
                    buttons[0].classList.add('active');
                    break;
                    
                case 'think':
                    document.getElementById('avatarThinking').classList.remove('hidden');
                    document.getElementById('avatarThinking').classList.add('avatar-breathing');
                    statusText.textContent = 'Processando informações...';
                    statusIndicator.style.background = '#ffaa00';
                    statusIndicator.style.boxShadow = '0 0 10px #ffaa00';
                    buttons[1].classList.add('active');
                    break;
                    
                case 'speak':
                    document.getElementById('avatarSpeaking').classList.remove('hidden');
                    document.getElementById('avatarSpeaking').classList.add('avatar-speaking');
                    statusText.textContent = 'Formulando resposta...';
                    statusIndicator.style.background = '#00ff00';
                    statusIndicator.style.boxShadow = '0 0 10px #00ff00';
                    buttons[2].classList.add('active');
                    
                    // Simular movimento da boca durante a fala
                    speakingInterval = setInterval(() => {
                        const speakingImg = document.getElementById('avatarSpeaking');
                        speakingImg.style.transform = `scaleY(${0.95 + Math.random() * 0.1})`;
                        setTimeout(() => {
                            speakingImg.style.transform = 'scaleY(1)';
                        }, 100);
                    }, 200);
                    break;
                    
                case 'greet':
                    document.getElementById('avatarIdle').classList.remove('hidden');
                    document.getElementById('avatarIdle').classList.add('avatar-breathing');
                    statusText.textContent = 'Olá! Como posso ajudar?';
                    statusIndicator.style.background = '#00ffff';
                    statusIndicator.style.boxShadow = '0 0 10px #00ffff';
                    buttons[3].classList.add('active');
                    break;
                    
                case 'idle':
                default:
                    document.getElementById('avatarIdle').classList.remove('hidden');
                    document.getElementById('avatarIdle').classList.add('avatar-breathing');
                    statusText.textContent = 'Online e pronta para ajudar';
                    statusIndicator.style.background = '#00ffff';
                    statusIndicator.style.boxShadow = '0 0 10px #00ffff';
                    break;
            }
        }
        
        // Função para simular piscadas aleatórias
        function startBlinking() {
            blinkInterval = setInterval(() => {
                if (currentAvatarState === 'idle' || currentAvatarState === 'listen') {
                    const currentImg = currentAvatarState === 'idle' ? 
                        document.getElementById('avatarIdle') : 
                        document.getElementById('avatarListening');
                    
                    currentImg.style.transform = 'scaleY(0.1)';
                    setTimeout(() => {
                        currentImg.style.transform = 'scaleY(1)';
                    }, 150);
                }
            }, 3000 + Math.random() * 2000); // Piscar a cada 3-5 segundos
        }
        
        function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Adicionar mensagem do usuário ao chat
            addMessageToChat(message, 'user');
            input.value = '';
            
            // Sequência de estados do avatar
            changeAvatarState('listen');
            
            // Simular delay de processamento
            setTimeout(() => {
                changeAvatarState('think');
                
                // Enviar mensagem para a API
                fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ mensagem: message })
                })
                .then(response => response.json())
                .then(data => {
                    changeAvatarState('speak');
                    
                    // Simular tempo de fala baseado no tamanho da resposta
                    const speakingTime = Math.max(2000, data.resposta.length * 50);
                    
                    // Adicionar resposta ao chat após um pequeno delay
                    setTimeout(() => {
                        addMessageToChat(data.resposta, 'ai');
                    }, 500);
                    
                    // Voltar ao estado idle após terminar de "falar"
                    setTimeout(() => {
                        changeAvatarState('idle');
                    }, speakingTime);
                })
                .catch(error => {
                    console.error('Erro:', error);
                    addMessageToChat('Desculpe, ocorreu um erro. Tente novamente.', 'ai');
                    changeAvatarState('idle');
                });
            }, 1000);
        }
        
        function addMessageToChat(message, sender) {
            const chatHistory = document.getElementById('chatHistory');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = message;
            chatHistory.appendChild(messageDiv);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        // Inicialização
        document.addEventListener('DOMContentLoaded', function() {
            // Animação inicial de boas-vindas
            setTimeout(() => {
                changeAvatarState('greet');
                setTimeout(() => {
                    changeAvatarState('idle');
                }, 3000);
            }, 1000);
            
            // Iniciar piscadas aleatórias
            startBlinking();
        });
        
        // Efeito de hover no avatar
        document.getElementById('aliciAvatar').addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.02)';
        });
        
        document.getElementById('aliciAvatar').addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    </script>
</body>
</html>
    '''
    return render_template_string(html_content)

# Rota para verificar o status da aplicação
@app.route("/status", methods=["GET"])
def status():
    return {"status": "Alici Avatar Holográfico online 🚀"}

# Rota para processar as mensagens do chat
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    pergunta = data.get("mensagem")

    if not pergunta:
        return jsonify({"erro": "Mensagem vazia"}), 400

    resposta = gerar_resposta(pergunta)
    return jsonify({"resposta": resposta})

# Ponto de entrada da aplicação
if __name__ == "__main__":
    # Obter a porta do ambiente (para o Render) ou usar 5000 como padrão
    port = int(os.environ.get("PORT", 5000))
    # Executar a aplicação Flask
    app.run(host="0.0.0.0", port=port)