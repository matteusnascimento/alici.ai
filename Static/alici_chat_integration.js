// alici_chat_integration.js
// Integração do chat com o renderer avançado

class AliciChatIntegration {
    constructor(canvasId) {
        this.controller = new AliciAnimationController(canvasId);
        this.mensagemInput = document.getElementById("mensagem-input");
        this.enviarBtn = document.getElementById("enviar-btn");
        this.emojiInfo = document.getElementById("emocao-info");
        
        this.enviarBtn.addEventListener("click", () => this.enviarMensagem());
        this.mensagemInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") this.enviarMensagem();
        });
        
        // Inicial: idle
        this.controller.setState("idle", "neutral", 0.08);
    }
    
    async enviarMensagem() {
        const mensagem = this.mensagemInput.value.trim();
        if (!mensagem) return;
        
        // Mostrar mensagem do usuário
        const chatBox = document.getElementById("chat-box");
        const userDiv = document.createElement("div");
        userDiv.className = "mensagem usuario";
        userDiv.textContent = mensagem;
        chatBox.appendChild(userDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
        
        this.mensagemInput.value = "";
        this.mensagemInput.focus();
        
        // Estado: pensando
        this.controller.setState("thinking", "thinking", 0.08);
        this.updateEmoji("thinking", 0.5);
        
        try {
            const response = await fetch("/api/chat-animado", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mensagem })
            });
            
            const data = await response.json();
            
            // Mapear estado visual
            const estadoMap = {
                "mystical": "mystical",
                "happy": "happy",
                "thinking": "thinking",
                "serious": "serious",
                "neutral": "idle"
            };
            
            const estado = estadoMap[data.emocao] || "talking";
            
            // Estado: respondendo com emoção
            this.controller.setState(
                estado,
                data.emocao || "neutral",
                data.velocidade_animacao || 0.12
            );
            
            this.updateEmoji(data.emocao, data.intensidade);
            
            // Mostrar resposta
            this.mostrarResposta(data.resposta);
            
            // Após 3-4 segundos: volta ao idle
            setTimeout(() => {
                this.controller.setState("idle", "neutral", 0.08);
                this.emojiInfo.innerHTML = "";
            }, 4000);
            
        } catch (error) {
            console.error("Erro:", error);
            this.controller.setState("serious", "serious", 0.10);
            this.mostrarResposta("Desculpe, houve um erro na minha resposta.");
            
            setTimeout(() => {
                this.controller.setState("idle", "neutral", 0.08);
            }, 3000);
        }
    }
    
    updateEmoji(emocao, intensidade) {
        const emojis = {
            "mysterious": "✨ Mistério",
            "happy": "😊 Feliz",
            "thinking": "🤔 Pensando",
            "serious": "⚠️ Atenção",
            "neutral": "😐 Neutro"
        };
        
        this.emojiInfo.innerHTML = `
            <div class="tag">${emojis[emocao] || emojis["neutral"]}</div>
            <div class="tag">Intensidade: ${Math.round(intensidade * 100)}%</div>
        `;
    }
    
    mostrarResposta(resposta) {
        const chatBox = document.getElementById("chat-box");
        const div = document.createElement("div");
        div.className = "mensagem alici";
        div.textContent = resposta;
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

// Iniciar quando página carrega
window.addEventListener("load", () => {
    window.aliciChat = new AliciChatIntegration("alici-canvas");
});
