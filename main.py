from flask import Flask, request, jsonify, render_template_string
from engine import gerar_resposta
import os

app = Flask(__name__)

# Rota para servir a interface web da Alici
@app.route("/")
def home():
    # Interface web embutida
    html_content = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alici - IA com Memória</title>
    <style>
        :root {
            --primary: #6e44ff;
            --secondary: #00e5ff;
            --dark: #0f0c29;
            --darker: #000000;
            --light: #ffffff;
            --accent: #ff2d75;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, var(--darker), var(--dark));
            color: var(--light);
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            padding: 40px 0;
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
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            font-weight: bold;
            box-shadow: 0 0 30px rgba(110, 68, 255, 0.5);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 30px rgba(110, 68, 255, 0.5); }
            50% { box-shadow: 0 0 50px rgba(0, 229, 255, 0.8); }
            100% { box-shadow: 0 0 30px rgba(110, 68, 255, 0.5); }
        }
        
        h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            background: linear-gradient(90deg, var(--secondary), var(--primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(110, 68, 255, 0.3);
        }
        
        .subtitle {
            font-size: 1.2rem;
            opacity: 0.8;
            margin-bottom: 30px;
        }
        
        .chat-container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .chat-history {
            height: 400px;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 15px;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 10px;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .user-message {
            background: linear-gradient(90deg, var(--primary), #8a6eff);
            margin-left: 20%;
            text-align: right;
        }
        
        .ai-message {
            background: rgba(255, 255, 255, 0.1);
            margin-right: 20%;
            border-left: 3px solid var(--secondary);
        }
        
        .input-area {
            display: flex;
            gap: 10px;
        }
        
        input {
            flex: 1;
            padding: 15px 20px;
            border: none;
            border-radius: 50px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 1rem;
            outline: none;
            transition: all 0.3s ease;
        }
        
        input:focus {
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 0 20px rgba(110, 68, 255, 0.3);
        }
        
        button {
            padding: 15px 30px;
            border: none;
            border-radius: 50px;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            color: white;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(255, 45, 117, 0.4);
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(255, 45, 117, 0.6);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }
        
        .feature-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.08);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
            background: linear-gradient(90deg, var(--secondary), var(--primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .feature-title {
            font-size: 1.3rem;
            margin-bottom: 10px;
        }
        
        .feature-desc {
            opacity: 0.7;
            font-size: 0.9rem;
        }
        
        footer {
            text-align: center;
            padding: 30px 0;
            opacity: 0.6;
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .chat-history {
                height: 300px;
            }
            
            .input-area {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-container">
                <div class="logo">A</div>
            </div>
            <h1>Alici 🤖</h1>
            <p class="subtitle">Inteligência Artificial com Memória Persistente</p>
        </header>
        
        <div class="chat-container">
            <div class="chat-history" id="chatHistory">
                <div class="message ai-message">
                    Olá! Eu sou a Alici, sua assistente de IA com memória. Como posso ajudar você hoje?
                </div>
            </div>
            <div class="input-area">
                <input type="text" id="userInput" placeholder="Digite sua mensagem..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Enviar</button>
            </div>
        </div>
        
        <div class="features">
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <h3 class="feature-title">Memória Persistente</h3>
                <p class="feature-desc">Aprendo com cada interação e guardo conhecimento no banco de dados</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🌐</div>
                <h3 class="feature-title">Busca na Web</h3>
                <p class="feature-desc">Quando não sei algo, busco informações atualizadas na internet</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">⚡</div>
                <h3 class="feature-title">Respostas Rápidas</h3>
                <p class="feature-desc">Processo perguntas e gero respostas em milissegundos</p>
            </div>
        </div>
        
        <footer>
            <p>Alici AI v2.0 | Inteligência Artificial com Memória | © 2026</p>
        </footer>
    </div>
    
    <script>
        function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Adicionar mensagem do usuário ao chat
            addMessageToChat(message, 'user');
            input.value = '';
            
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
                addMessageToChat(data.resposta, 'ai');
            })
            .catch(error => {
                console.error('Erro:', error);
                addMessageToChat('Desculpe, ocorreu um erro. Tente novamente.', 'ai');
            });
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
    </script>
</body>
</html>
    '''
    return render_template_string(html_content)

@app.route("/status", methods=["GET"])
def status():
    return {"status": "Alici online 🚀"}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    pergunta = data.get("mensagem")

    if not pergunta:
        return jsonify({"erro": "Mensagem vazia"}), 400

    resposta = gerar_resposta(pergunta)
    return jsonify({"resposta": resposta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))