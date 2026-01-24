/**
 * ALICI™ Chat - Lógica principal
 */

let userInfo = null;

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

document.addEventListener('DOMContentLoaded', async function() {
    // Verificar autenticação
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        window.location.href = '/';
        return;
    }

    // Carregar informações do usuário
    await carregarInfoUsuario();
    
    // Carregar histórico
    await carregarHistorico();
});

// ============================================================================
// AUTENTICAÇÃO
// ============================================================================

async function carregarInfoUsuario() {
    try {
        const response = await fetch('/api/status', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            userInfo = data.usuario;
            
            document.getElementById('userName').textContent = userInfo.nome;
            document.getElementById('userPlan').textContent = 
                userInfo.plano === 'pro' ? 'Plano Pro ⭐' : 'Plano Free';
        } else {
            logout();
        }
    } catch (error) {
        console.error('Erro ao carregar usuário:', error);
    }
}

function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/';
}

// ============================================================================
// CHAT
// ============================================================================

async function enviarMensagem(event) {
    event.preventDefault();

    const input = document.getElementById('messageInput');
    const mensagem = input.value.trim();

    if (!mensagem) return;

    // Adicionar mensagem do usuário ao chat
    adicionarMensagem(mensagem, 'user');
    input.value = '';

    // Atualizar status
    document.getElementById('statusText').textContent = 'Pensando...';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({
                pergunta: mensagem,
                incluir_emocao: true
            })
        });

        if (response.ok) {
            const data = await response.json();
            adicionarMensagem(data.resposta, 'ai');
            document.getElementById('statusText').textContent = 'Pronta para ajudar';
        } else {
            const error = await response.json();
            adicionarMensagem('Desculpe, ocorreu um erro: ' + error.detail, 'ai');
        }
    } catch (error) {
        console.error('Erro:', error);
        adicionarMensagem('Erro de conexão. Tente novamente.', 'ai');
    }
}

function adicionarMensagem(texto, tipo) {
    const container = document.getElementById('messagesContainer');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${tipo}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = `<p>${escapeHtml(texto)}</p>`;
    
    messageDiv.appendChild(contentDiv);
    container.appendChild(messageDiv);

    // Scroll para o final
    container.scrollTop = container.scrollHeight;
}

// ============================================================================
// HISTÓRICO
// ============================================================================

async function carregarHistorico() {
    try {
        const response = await fetch('/history', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            const historyList = document.getElementById('historyList');

            if (data.historico && data.historico.length > 0) {
                historyList.innerHTML = '';
                data.historico.slice(0, 10).forEach(item => {
                    const itemDiv = document.createElement('div');
                    itemDiv.className = 'history-item';
                    itemDiv.textContent = item.pergunta.substring(0, 30);
                    itemDiv.title = item.pergunta;
                    historyList.appendChild(itemDiv);
                });
            }
        }
    } catch (error) {
        console.error('Erro ao carregar histórico:', error);
    }
}

function novoChat() {
    document.getElementById('messagesContainer').innerHTML = `
        <div class="message ai-message">
            <div class="message-content">
                <p>Novo chat iniciado! Como posso ajudá-lo?</p>
            </div>
        </div>
    `;
    document.getElementById('messageInput').focus();
}

// ============================================================================
// UPLOAD DE IMAGEM
// ============================================================================

function uploadImagem() {
    document.getElementById('imageInput').click();
}

async function processarImagem(event) {
    const file = event.target.files[0];
    if (!file) return;

    adicionarMensagem('📷 Analisando imagem...', 'user');
    document.getElementById('statusText').textContent = 'Processando imagem...';

    const formData = new FormData();
    formData.append('imagem', file);

    try {
        const response = await fetch('/chat/image', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            adicionarMensagem(data.resposta, 'ai');
        } else {
            const error = await response.json();
            adicionarMensagem('Erro na análise: ' + error.detail, 'ai');
        }
    } catch (error) {
        console.error('Erro:', error);
        adicionarMensagem('Erro ao processar imagem.', 'ai');
    } finally {
        document.getElementById('statusText').textContent = 'Pronta para ajudar';
        event.target.value = '';
    }
}

// ============================================================================
// UTILITÁRIOS
// ============================================================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
