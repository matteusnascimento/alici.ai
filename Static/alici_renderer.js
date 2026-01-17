// alici_renderer.js
// Renderização melhorada da Alici baseada no avatar cyberpunk

class AliciRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = 500;
        this.canvas.height = 600;
        
        // Centro do canvas
        this.centerX = this.canvas.width / 2;
        this.centerY = this.canvas.height / 2;
        
        // Estado
        this.estado = "idle";
        this.emocao = "neutral";
        this.frame = 0;
        this.velocidade = 0.12;
        
        // Cores
        this.cores = {
            pele: "#f0e6d2",
            cabelo_primario: "#00ffff",
            cabelo_secundario: "#00dddd",
            olho_iris: "#0099ff",
            olho_brilho: "#ffffff",
            aura: "#8b5cf6"
        };
    }
    
    setState(estado, emocao = "neutral", velocidade = 0.12) {
        this.estado = estado;
        this.emocao = emocao;
        this.velocidade = velocidade;
        this.frame = 0;
        
        // Atualizar cores baseado na emoção
        switch(emocao) {
            case "thinking":
                this.cores.aura = "#fbbf24";
                break;
            case "happy":
                this.cores.aura = "#00ffaa";
                break;
            case "serious":
                this.cores.aura = "#ef4444";
                break;
            case "mysterious":
                this.cores.aura = "#8b5cf6";
                break;
            default:
                this.cores.aura = "#06b6d4";
        }
    }
    
    render() {
        // Limpar canvas com fade
        this.ctx.fillStyle = "rgba(15, 23, 42, 0.2)";
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Desenhar em ordem (background to foreground)
        this.desenharAura();
        this.desenharParticulas();
        this.desenharCorpo();
        this.desenharCabelo();
        this.desenharRosto();
        this.desenharOlhos();
        this.desenharBoca();
        
        this.frame += this.velocidade;
        if (this.frame > 360) this.frame = 0;
    }
    
    // ============ AURA ============
    desenharAura() {
        const pulse = Math.sin(this.frame * 0.05) * 5;
        const intensity = this.emocao === "happy" ? 40 : 30;
        
        // Aura externa (grande)
        const gradient1 = this.ctx.createRadialGradient(
            this.centerX, this.centerY, 60,
            this.centerX, this.centerY, 150 + intensity
        );
        gradient1.addColorStop(0, this.cores.aura + "80");
        gradient1.addColorStop(1, this.cores.aura + "00");
        this.ctx.fillStyle = gradient1;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY, 150 + intensity + pulse, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Aura média
        const gradient2 = this.ctx.createRadialGradient(
            this.centerX, this.centerY, 50,
            this.centerX, this.centerY, 100
        );
        gradient2.addColorStop(0, this.cores.aura + "60");
        gradient2.addColorStop(1, this.cores.aura + "20");
        this.ctx.fillStyle = gradient2;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY, 100 + (pulse * 0.5), 0, Math.PI * 2);
        this.ctx.fill();
        
        // Círculo de aura com brilho
        this.ctx.strokeStyle = this.cores.aura + "40";
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY, 85, 0, Math.PI * 2);
        this.ctx.stroke();
    }
    
    // ============ PARTÍCULAS ============
    desenharParticulas() {
        if (this.estado === "thinking") {
            this.desenharParticulas_Thinking();
        } else if (this.estado === "happy") {
            this.desenharParticulas_Happy();
        } else if (this.estado === "serious") {
            this.desenharParticulas_Serious();
        } else if (this.estado === "mystical") {
            this.desenharParticulas_Mystical();
        }
    }
    
    desenharParticulas_Thinking() {
        // Números/símbolos orbitais
        const simbolos = ["∫", "∞", "√", "π", "ψ"];
        for (let i = 0; i < 3; i++) {
            const angle = (this.frame * 0.1 + i * Math.PI * 2 / 3) * Math.PI / 180;
            const x = this.centerX + Math.cos(angle) * 80;
            const y = this.centerY - 100 + Math.sin(angle) * 40;
            
            this.ctx.fillStyle = "#00ff88";
            this.ctx.font = "16px monospace";
            this.ctx.globalAlpha = 0.6 + Math.sin(this.frame * 0.1) * 0.3;
            this.ctx.fillText(simbolos[i], x, y);
            this.ctx.globalAlpha = 1.0;
        }
    }
    
    desenharParticulas_Happy() {
        // Sparkles explosivos
        const sparkles = ["✨", "⭐", "💫"];
        const numSparkles = 6;
        
        for (let i = 0; i < numSparkles; i++) {
            const angle = (this.frame * 0.15 + i * Math.PI * 2 / numSparkles) * Math.PI / 180;
            const radius = 60 + Math.sin(this.frame * 0.12) * 20;
            const x = this.centerX + Math.cos(angle) * radius;
            const y = this.centerY - 50 + Math.sin(angle) * radius;
            
            this.ctx.fillStyle = "#fbbf24";
            this.ctx.font = "18px Arial";
            this.ctx.globalAlpha = 0.7 + Math.sin(this.frame * 0.1 + i) * 0.3;
            this.ctx.fillText(sparkles[i % 3], x, y);
            this.ctx.globalAlpha = 1.0;
        }
    }
    
    desenharParticulas_Serious() {
        // Raios de alerta
        const numRaios = 4;
        for (let i = 0; i < numRaios; i++) {
            const angle = (this.frame * 0.2 + i * Math.PI * 2 / numRaios) * Math.PI / 180;
            const x1 = this.centerX;
            const y1 = this.centerY - 30;
            const x2 = this.centerX + Math.cos(angle) * 70;
            const y2 = this.centerY - 30 + Math.sin(angle) * 70;
            
            this.ctx.strokeStyle = "#ff0000" + Math.floor((Math.abs(Math.sin(this.frame * 0.15)) * 255)).toString(16).padStart(2, '0');
            this.ctx.lineWidth = 2;
            this.ctx.beginPath();
            this.ctx.moveTo(x1, y1);
            this.ctx.lineTo(x2, y2);
            this.ctx.stroke();
        }
    }
    
    desenharParticulas_Mystical() {
        // Runas cósmicas
        const runas = ["✧", "✦", "❖", "◇"];
        const numRunas = 8;
        
        for (let i = 0; i < numRunas; i++) {
            const angle = (this.frame * 0.08 + i * Math.PI * 2 / numRunas) * Math.PI / 180;
            const x = this.centerX + Math.cos(angle) * 100;
            const y = this.centerY + Math.sin(angle) * 100;
            
            this.ctx.fillStyle = "#8b5cf6";
            this.ctx.font = "16px Arial";
            this.ctx.globalAlpha = 0.5 + Math.sin(this.frame * 0.08 + i) * 0.3;
            this.ctx.fillText(runas[i % 4], x, y);
            this.ctx.globalAlpha = 1.0;
        }
    }
    
    // ============ CORPO ============
    desenharCorpo() {
        const breathe = Math.sin(this.frame * 0.04) * 2;
        const bodyMove = Math.sin(this.frame * 0.06) * 3;
        
        // Corpo principal (forma etérea)
        this.ctx.fillStyle = "rgba(139, 92, 246, 0.15)";
        this.ctx.beginPath();
        this.ctx.ellipse(
            this.centerX + bodyMove,
            this.centerY + 60 + breathe,
            35,
            50,
            0,
            0,
            Math.PI * 2
        );
        this.ctx.fill();
        
        // Ombros/pescoço
        this.ctx.fillStyle = this.cores.pele;
        this.ctx.beginPath();
        this.ctx.ellipse(
            this.centerX,
            this.centerY,
            40,
            15,
            0,
            0,
            Math.PI * 2
        );
        this.ctx.fill();
    }
    
    // ============ CABELO ============
    desenharCabelo() {
        const waveAmount = Math.sin(this.frame * 0.08) * 5;
        const moveX = Math.sin(this.frame * 0.06) * 3;
        
        // Cabelo principal (fluxo de luz)
        const gradient = this.ctx.createLinearGradient(
            this.centerX - 40,
            this.centerY - 70,
            this.centerX + 40,
            this.centerY - 70
        );
        gradient.addColorStop(0, this.cores.cabelo_primario);
        gradient.addColorStop(0.5, "#00eeee");
        gradient.addColorStop(1, this.cores.cabelo_primario);
        
        this.ctx.fillStyle = gradient;
        this.ctx.beginPath();
        
        // Topo ondulante
        this.ctx.moveTo(this.centerX - 40 + moveX, this.centerY - 65);
        this.ctx.quadraticCurveTo(
            this.centerX - 20,
            this.centerY - 80 + waveAmount,
            this.centerX,
            this.centerY - 75
        );
        this.ctx.quadraticCurveTo(
            this.centerX + 20,
            this.centerY - 80 + waveAmount,
            this.centerX + 40 - moveX,
            this.centerY - 65
        );
        
        // Lados fluindo
        this.ctx.quadraticCurveTo(
            this.centerX + 45,
            this.centerY - 20,
            this.centerX + 35,
            this.centerY + 30
        );
        this.ctx.quadraticCurveTo(
            this.centerX + 20,
            this.centerY + 20,
            this.centerX + 10,
            this.centerY
        );
        
        this.ctx.quadraticCurveTo(
            this.centerX - 20,
            this.centerY + 20,
            this.centerX - 35,
            this.centerY + 30
        );
        this.ctx.quadraticCurveTo(
            this.centerX - 45,
            this.centerY - 20,
            this.centerX - 40 + moveX,
            this.centerY - 65
        );
        
        this.ctx.fill();
        
        // Efeito de brilho (glow)
        this.ctx.strokeStyle = this.cores.cabelo_primario + "60";
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, this.centerY - 50, 50, 0, Math.PI * 2);
        this.ctx.stroke();
    }
    
    // ============ ROSTO ============
    desenharRosto() {
        // Forma do rosto
        this.ctx.fillStyle = this.cores.pele;
        this.ctx.beginPath();
        this.ctx.ellipse(this.centerX, this.centerY - 25, 32, 40, 0, 0, Math.PI * 2);
        this.ctx.fill();
        
        // Efeito de sombra/contorno
        this.ctx.strokeStyle = this.cores.pele + "40";
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.ellipse(this.centerX, this.centerY - 25, 32, 40, 0, 0, Math.PI * 2);
        this.ctx.stroke();
    }
    
    // ============ OLHOS ============
    desenharOlhos() {
        const offsetOlho = 12;
        const tamanhoOlho = 8;
        
        // Desenhar cada olho
        for (let lado of [-1, 1]) {
            const xOlho = this.centerX + lado * offsetOlho;
            const yOlho = this.centerY - 35;
            
            // Branco do olho
            this.ctx.fillStyle = "#ffffff";
            this.ctx.beginPath();
            this.ctx.ellipse(xOlho, yOlho, tamanhoOlho * 0.8, tamanhoOlho, 0, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Íris (azul ciano)
            const pupilMove = Math.sin(this.frame * 0.08) * 2;
            this.ctx.fillStyle = this.cores.olho_iris;
            this.ctx.beginPath();
            this.ctx.arc(xOlho + pupilMove, yOlho, tamanhoOlho * 0.6, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Pupila (preta)
            this.ctx.fillStyle = "#000000";
            this.ctx.beginPath();
            this.ctx.arc(xOlho + pupilMove, yOlho, tamanhoOlho * 0.35, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Brilho (reflexo cyberpunk)
            const reflexoX = xOlho + lado * 2;
            const reflexoY = yOlho - 2;
            
            const reflexoGradient = this.ctx.createRadialGradient(
                reflexoX, reflexoY, 0,
                reflexoX, reflexoY, 4
            );
            reflexoGradient.addColorStop(0, "#ffffff");
            reflexoGradient.addColorStop(1, "#ffffff00");
            
            this.ctx.fillStyle = reflexoGradient;
            this.ctx.beginPath();
            this.ctx.arc(reflexoX, reflexoY, 4, 0, Math.PI * 2);
            this.ctx.fill();
            
            // Efeito de laser (quando sério)
            if (this.estado === "serious") {
                this.ctx.strokeStyle = "#ff0000";
                this.ctx.lineWidth = 1.5;
                this.ctx.beginPath();
                this.ctx.moveTo(xOlho, yOlho);
                this.ctx.lineTo(xOlho + lado * 40, yOlho + 30);
                this.ctx.stroke();
            }
        }
    }
    
    // ============ BOCA ============
    desenharBoca() {
        const boca_y = this.centerY + 5;
        
        switch(this.estado) {
            case "idle":
                this.desenharBoca_Neutra(boca_y);
                break;
            case "talking":
                this.desenharBoca_Falando(boca_y);
                break;
            case "happy":
                this.desenharBoca_Feliz(boca_y);
                break;
            case "thinking":
                this.desenharBoca_Pensando(boca_y);
                break;
            case "serious":
                this.desenharBoca_Seria(boca_y);
                break;
            case "mystical":
                this.desenharBoca_Mistico(boca_y);
                break;
        }
    }
    
    desenharBoca_Neutra(y) {
        this.ctx.strokeStyle = "#000000";
        this.ctx.lineWidth = 1.5;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, y, 8, 0, Math.PI);
        this.ctx.stroke();
    }
    
    desenharBoca_Falando(y) {
        const falaFrame = Math.sin(this.frame * 0.2) * 0.5 + 0.5;
        this.ctx.fillStyle = "#ff69b4";
        this.ctx.beginPath();
        this.ctx.ellipse(this.centerX, y, 7, 3 + falaFrame * 4, 0, 0, Math.PI * 2);
        this.ctx.fill();
    }
    
    desenharBoca_Feliz(y) {
        this.ctx.strokeStyle = "#000000";
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, y, 9, 0, Math.PI);
        this.ctx.stroke();
    }
    
    desenharBoca_Pensando(y) {
        this.ctx.strokeStyle = "#000000";
        this.ctx.lineWidth = 1.5;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, y, 6, 0, Math.PI);
        this.ctx.stroke();
    }
    
    desenharBoca_Seria(y) {
        this.ctx.strokeStyle = "#000000";
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(this.centerX - 8, y);
        this.ctx.lineTo(this.centerX + 8, y);
        this.ctx.stroke();
    }
    
    desenharBoca_Mistico(y) {
        // Boca em forma de O místico
        this.ctx.strokeStyle = "#8b5cf6";
        this.ctx.lineWidth = 1.5;
        this.ctx.beginPath();
        this.ctx.arc(this.centerX, y, 5, 0, Math.PI * 2);
        this.ctx.stroke();
    }
}

// Classe de animação fluida
class AliciAnimationController {
    constructor(canvas) {
        this.renderer = new AliciRenderer(canvas);
        this.isAnimating = true;
        this.animationLoop();
    }
    
    setState(estado, emocao, velocidade) {
        this.renderer.setState(estado, emocao, velocidade);
    }
    
    animationLoop() {
        this.renderer.render();
        if (this.isAnimating) {
            requestAnimationFrame(() => this.animationLoop());
        }
    }
    
    stop() {
        this.isAnimating = false;
    }
}
