// alici_animator.js
// State Machine + Animação fluida da Alici

class AliciAnimator {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        
        // Estado atual
        this.estado = "idle";
        this.emocao = "neutral";
        this.intensidade = 0;
        this.cor_aura = "#06b6d4";
        this.velocidade = 1.0;
        
        // Animação
        this.frame = 0;
        this.frameVelocidade = 0.3;
        this.animacionRodando = true;
        
        // Dimensões
        this.centerX = this.canvas.width / 2;
        this.centerY = this.canvas.height / 2;
        
        // Inicia loop
        this.animate();
    }
    
    setState(novoEstado, emocao = "neutral", intensidade = 0, cor = "#06b6d4", velocidade = 1.0) {
        if (this.estado !== novoEstado) {
            console.log(`🎭 Alici: ${this.estado} → ${novoEstado}`);
            this.estado = novoEstado;
            this.frame = 0; // Reset animação
        }
        
        this.emocao = emocao;
        this.intensidade = intensidade;
        this.cor_aura = cor;
        this.velocidade = velocidade;
        this.frameVelocidade = 0.3 * velocidade;
    }
    
    animate() {
        // Limpar canvas
        this.ctx.fillStyle = "rgba(0, 0, 0, 0.1)";
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Desenhar aura
        this.desenharAura();
        
        // Desenhar personagem base
        this.desenharCorpo();
        
        // Desenhar expressão/animação
        switch(this.estado) {
            case "idle":
                this.desenharIdle();
                break;
            case "thinking":
                this.desenharThinking();
                break;
            case "talking":
                this.desenharTalking();
                break;
            case "happy":
                this.desenharHappy();
                break;
            case "serious":
                this.desenharSerious();
                break;
            case "mystical":
                this.desenharMystical();
                break;
        }
        
        // Incrementar frame
        this.frame += this.frameVelocidade;
        if (this.frame > 100) this.frame = 0;
        
        // Continuar animação
        if (this.animacionRodando) {
            requestAnimationFrame(() => this.animate());
        }
    }
    
    desenharAura() {
        const intensity = this.intensidade * 30;
        const pulse = Math.sin(this.frame * 0.05) * 5;
        
        // Aura externa (pulsante)
        this.ctx.fillStyle = this.cor_aura + "40"; // 25% opacity
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY, 80 + intensity + pulse, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Aura média
        this.ctx.fillStyle = this.cor_aura + "60";
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY, 60 + intensity, 0, Math.PI * 2);
        this.ctx.fill();
    }
    
    desenharCorpo() {
        // Cabeça (estilo anime mystical)
        this.ctx.fillStyle = "#fff5e6";
        this.ctx.beginPath();
        this.ctx.ellipse(this.centerX, this.centerY - 20, 30, 35, 0, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Cabelo fluido (efeito de levitação)
        this.ctx.fillStyle = "#8b5cf6";
        const cabelo_wave = Math.sin(this.frame * 0.08) * 3;
        this.ctx.beginPath();
        this.ctx.moveTo(this.centerX - 30, this.centerY - 40);
        this.ctx.quadraticCurveTo(this.centerX, this.centerY - 55 + cabelo_wave, this.centerX + 30, this.centerY - 40);
        this.ctx.quadraticCurveTo(this.centerX, this.centerY - 35, this.centerX - 30, this.centerY - 40);
        this.ctx.fill();
        
        // Corpo etéreo
        this.ctx.fillStyle = "rgba(139, 92, 246, 0.3)";
        this.ctx.beginPath();
        this.ctx.ellipse(this.centerX, this.centerY + 15, 25, 40, 0, 0, Math.PI * 2);
        this.ctx.fill();
    }
    
    desenharOlhos() {
        const offsetOlho = 10;
        const tamanho = 4;
        
        // Olhos
        this.ctx.fillStyle = "#000";
        this.ctx.beginPath();
        this.ctx.arc(this.centerX - offsetOlho, this.centerY - 30, tamanho, 0, Math.PI * 2);
        this.ctx.fill();
        
        this.ctx.beginPath();
        this.ctx.arc(this.centerX + offsetOlho, this.centerY - 30, tamanho, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Brilho nos olhos
        this.ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
        this.ctx.beginPath();
        this.ctx.arc(this.centerX - offsetOlho - 1, this.centerY - 31, 1.5, 0, Math.PI * 2);
        this.ctx.fill();
        
        this.ctx.beginPath();
        this.ctx.arc(this.centerX + offsetOlho - 1, this.centerY - 31, 1.5, 0, Math.PI * 2);
        this.ctx.fill();
    }
    
    desenharIdle() {
        // Respiração suave
        const respiration = Math.sin(this.frame * 0.04) * 2;
        
        this.desenharOlhos();
        
        // Boca neutro
        this.ctx.strokeStyle = "#000";
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY + 5, 8, 0, Math.PI);
        this.ctx.stroke();
        
        // Texto de status
        this.desenharTexto("Esperando...", 0.3);
    }
    
    desenharThinking() {
        // Piscada de pensamento
        const blink = Math.sin(this.frame * 0.06) * 3;
        
        if (Math.abs(blink) > 2) {
            // Olhos fechados
            this.ctx.strokeStyle = "#000";
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.moveTo(this.centerX - 10, this.centerY - 30);
            this.ctx.lineTo(this.centerX - 10 + 8, this.centerY - 30);
            this.ctx.stroke();
            
            this.ctx.beginPath();
            this.ctx.moveTo(this.centerX + 10, this.centerY - 30);
            this.ctx.lineTo(this.centerX + 10 + 8, this.centerY - 30);
            this.ctx.stroke();
        } else {
            this.desenharOlhos();
        }
        
        // Boca em "hmm"
        this.ctx.strokeStyle = "#000";
        this.ctx.lineWidth = 1.5;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY + 8, 6, 0, Math.PI);
        this.ctx.stroke();
        
        // Ponto de interrogação flutuando
        const floatY = Math.sin(this.frame * 0.08) * 10;
        this.ctx.fillStyle = "#fbbf24";
        this.ctx.font = "bold 16px Arial";
        this.ctx.fillText("?", this.centerX + 25, this.centerY - 40 + floatY);
        
        this.desenharTexto("Pensando...", 0.5);
    }
    
    desenharTalking() {
        this.desenharOlhos();
        
        // Boca animada (falando)
        const mouth = Math.abs(Math.sin(this.frame * 0.15)) * 8;
        this.ctx.fillStyle = "#ff69b4";
        this.ctx.beginPath();
        this.ctx.ellipse(this.centerX, this.centerY + 8, 6, 2 + mouth, 0, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Linhas de fala
        for (let i = 0; i < 3; i++) {
            const offset = Math.sin(this.frame * 0.1 + i) * 15;
            this.ctx.strokeStyle = `rgba(0, 255, 170, ${0.5 - i * 0.15})`;
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.arc(this.centerX + 30 + offset, this.centerY - 10 + i * 8, 8, 0, Math.PI * 2);
            this.ctx.stroke();
        }
        
        this.desenharTexto("Respondendo...", 0.4);
    }
    
    desenharHappy() {
        this.desenharOlhos();
        
        // Sorriso radiante
        this.ctx.strokeStyle = "#000";
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY + 8, 8, 0, Math.PI);
        this.ctx.stroke();
        
        // Linha de brilho ao redor
        this.ctx.strokeStyle = this.cor_aura;
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY - 20, 40 + Math.sin(this.frame * 0.1) * 5, 0, Math.PI * 2);
        this.ctx.stroke();
        
        // Sparkles ✨
        for (let i = 0; i < 3; i++) {
            const angle = (this.frame * 0.08 + i * Math.PI * 2 / 3);
            const x = this.centerX + Math.cos(angle) * 50;
            const y = this.centerY - 30 + Math.sin(angle) * 30;
            
            this.ctx.fillStyle = "#fbbf24";
            this.ctx.font = "16px Arial";
            this.ctx.fillText("✨", x, y);
        }
        
        this.desenharTexto("Feliz! 😊", 0.6);
    }
    
    desenharSerious() {
        // Olhos sérios (sobrancelhas)
        this.ctx.strokeStyle = "#8b5cf6";
        this.ctx.lineWidth = 2.5;
        
        // Sobrancelha esquerda
        this.ctx.beginPath();
        this.ctx.moveTo(this.centerX - 15, this.centerY - 38);
        this.ctx.lineTo(this.centerX - 5, this.centerY - 42);
        this.ctx.stroke();
        
        // Sobrancelha direita
        this.ctx.beginPath();
        this.ctx.moveTo(this.centerX + 5, this.centerY - 42);
        this.ctx.lineTo(this.centerX + 15, this.centerY - 38);
        this.ctx.stroke();
        
        this.desenharOlhos();
        
        // Boca séria (reta)
        this.ctx.strokeStyle = "#000";
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(this.centerX - 8, this.centerY + 8);
        this.ctx.lineTo(this.centerX + 8, this.centerY + 8);
        this.ctx.stroke();
        
        // Aura vermelha pulsante
        this.ctx.strokeStyle = "#ef4444";
        this.ctx.lineWidth = 2;
        for (let i = 0; i < 2; i++) {
            this.ctx.beginPath();
            this.ctx.arc(this.centerX, this.centerY - 20, 45 + i * 10 + Math.sin(this.frame * 0.08) * 5, 0, Math.PI * 2);
            this.ctx.stroke();
        }
        
        this.desenharTexto("⚠️ ATENÇÃO", 0.7);
    }
    
    desenharMystical() {
        // Olhos místicos (brilhando)
        this.ctx.fillStyle = "#8b5cf6";
        const glowIntensity = Math.sin(this.frame * 0.1) * 0.5 + 0.5;
        
        this.ctx.globalAlpha = 0.6 + glowIntensity * 0.4;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX - 10, this.centerY - 30, 6, 0, Math.PI * 2);
        this.ctx.fill();
        
        this.ctx.beginPath();
        this.ctx.arc(this.centerX + 10, this.centerY - 30, 6, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.globalAlpha = 1.0;
        
        this.desenharOlhos();
        
        // Boca em "O" místico
        this.ctx.strokeStyle = "#000";
        this.ctx.lineWidth = 1.5;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY + 8, 4, 0, Math.PI * 2);
        this.ctx.stroke();
        
        // Runas flutuando
        const runas = ["✨", "🌟", "💫"];
        for (let i = 0; i < runas.length; i++) {
            const angle = this.frame * 0.06 + i * Math.PI * 2 / 3;
            const x = this.centerX + Math.cos(angle) * 60;
            const y = this.centerY + Math.sin(angle) * 50;
            
            this.ctx.fillStyle = "#8b5cf6";
            this.ctx.font = "18px Arial";
            this.ctx.globalAlpha = 0.7 + Math.sin(this.frame * 0.1 + i) * 0.3;
            this.ctx.fillText(runas[i], x, y);
            this.ctx.globalAlpha = 1.0;
        }
        
        this.desenharTexto("Mistério... ✨", 0.5);
    }
    
    desenharTexto(texto, opacidade = 1.0) {
        this.ctx.globalAlpha = opacidade;
        this.ctx.fillStyle = "#00ffaa";
        this.ctx.font = "12px 'Courier New'";
        this.ctx.textAlign = "center";
        this.ctx.fillText(texto, this.centerX, this.centerY + 70);
        this.ctx.globalAlpha = 1.0;
    }
    
    stop() {
        this.animacionRodando = false;
    }
}

// Integração com chat
class AliciChatIntegration {
    constructor(canvasId, apiUrl) {
        this.animator = new AliciAnimator(canvasId);
        this.apiUrl = apiUrl;
        this.mensagemInput = document.getElementById("mensagem-input");
        this.enviarBtn = document.getElementById("enviar-btn");
        this.emojiInfo = document.getElementById("emocao-info");
        
        this.enviarBtn.addEventListener("click", () => this.enviarMensagem());
        this.mensagemInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") this.enviarMensagem();
        });
        
        // Inicial: idle
        this.animator.setState("idle");
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
        
        // Estado: pensando
        this.animator.setState("thinking", "thinking", 0.5, "#fbbf24", 1.0);
        this.updateEmoji("thinking", 0.5);
        
        try {
            const response = await fetch("/api/chat-animado", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ mensagem })
            });
            
            const data = await response.json();
            
            // Estado: respondendo com emoção
            this.animator.setState(
                data.estado_visual || "talking",
                data.emocao || "neutral",
                data.intensidade || 0.5,
                data.cor_aura || "#06b6d4",
                data.velocidade_animacao || 1.0
            );
            
            this.updateEmoji(data.emocao, data.intensidade);
            
            // Mostrar resposta
            this.mostrarResposta(data.resposta);
            
            // Após 3 segundos: volta ao idle
            setTimeout(() => {
                this.animator.setState("idle");
                this.emojiInfo.innerHTML = "";
            }, 3000);
            
        } catch (error) {
            console.error("Erro:", error);
            this.animator.setState("serious");
            this.mostrarResposta("Desculpe, houve um erro na minha resposta.");
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
