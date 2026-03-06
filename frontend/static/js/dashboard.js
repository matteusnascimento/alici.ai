// dashboard.js - Enhanced UX Dashboard
// Connects dashboard UI to backend chat API and history

const API_CHAT = '/api/chat/message';
const API_HISTORY = '/api/chat/conversations';

function getToken() {
    return localStorage.getItem('access_token');
}

function showLoading(show) {
    const ld = document.getElementById('loadingIndicator');
    if (ld) ld.classList.toggle('hidden', !show);
}

function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const iconMap = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };

    toast.innerHTML = `
        <i class="${iconMap[type] || 'fas fa-info-circle'}"></i>
        <div class="toast-message">${message}</div>
        <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    container.appendChild(toast);

    // Auto remove after duration
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
}

async function loadHistory() {
    const token = getToken();
    if (!token) {
        window.location.href = '/login';
        return;
    }
    try {
        const res = await fetch(API_HISTORY + '?limit=100', {
            headers: { Authorization: 'Bearer ' + token },
        });
        const data = await res.json();
        if (res.ok) {
            const hist = Array.isArray(data ? .historico) ?
                data.historico :
                Array.isArray(data ? .history) ?
                data.history :
                [];

            hist.reverse().forEach((h) => {
                const userText = h.pergunta || h.question || h.user;
                const assistantText = h.resposta || h.answer || h.assistant;
                if (userText) addMessage(userText, 'user');
                if (assistantText) addMessage(assistantText, 'assistant');
            });
            updateCharCount();
        } else {
            console.warn('Failed to load history', data);
            showToast('Erro ao carregar histórico', 'error');
        }
    } catch (e) {
        console.error('History fetch error', e);
        showToast('Erro de rede ao carregar histórico', 'error');
    }
}

async function sendChat(question) {
    const token = getToken();
    if (!token) {
        window.location.href = '/login';
        return;
    }

    if (!question.trim()) {
        showToast('Por favor, digite uma mensagem', 'warning');
        return;
    }

    showLoading(true);
    addMessage(question, 'user');

    try {
        const res = await fetch(API_CHAT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token },
            body: JSON.stringify({ message: question }),
        });
        const data = await res.json();
        if (res.ok) {
            const answer = data.content || data.message || data.response || data.resposta || 'Sem resposta do modelo.';
            addMessage(answer, 'assistant');
            showToast('Mensagem enviada com sucesso', 'success', 1500);
        } else {
            const errorMsg = data.detail || 'Erro no servidor';
            addMessage(errorMsg, 'assistant');
            showToast(errorMsg, 'error');
        }
    } catch (e) {
        console.error('Chat send error', e);
        addMessage('Falha de rede. Tente novamente.', 'assistant');
        showToast('Erro de conexão', 'error');
    } finally {
        showLoading(false);
    }
}

function logout() {
    const token = getToken();
    if (token) {
        fetch('/auth/logout', {
            method: 'POST',
            headers: { Authorization: 'Bearer ' + token },
        }).finally(() => {
            localStorage.clear();
            showToast('Logout realizado com sucesso', 'success');
            setTimeout(() => window.location.href = '/login', 1000);
        });
    } else {
        window.location.href = '/login';
    }
}

function addMessage(text, sender) {
    const history = document.getElementById('chatHistory');
    if (!history) return;

    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;

    const timestamp = new Date().toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
    });

    msgDiv.innerHTML = `
        <div class="message-content">${text}</div>
        <div class="timestamp">${timestamp}</div>
    `;

    history.appendChild(msgDiv);
    history.scrollTop = history.scrollHeight;

    // Animate message appearance
    msgDiv.style.opacity = '0';
    msgDiv.style.transform = 'translateY(10px)';
    requestAnimationFrame(() => {
        msgDiv.style.transition = 'all 0.3s ease';
        msgDiv.style.opacity = '1';
        msgDiv.style.transform = 'translateY(0)';
    });
}

function updateCharCount() {
    const input = document.getElementById('chatInput');
    const counter = document.querySelector('.char-count');
    if (input && counter) {
        const count = input.value.length;
        counter.textContent = `${count}/2000`;
        counter.style.color = count > 1800 ? '#ef4444' : count > 1500 ? '#f59e0b' : 'var(--text-muted)';
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const main = document.getElementById('main');
    const toggle = document.getElementById('sidebarToggle');

    if (sidebar && main) {
        const isCollapsed = sidebar.classList.contains('collapsed');

        if (window.innerWidth <= 768) {
            // Mobile behavior
            sidebar.classList.toggle('open');
            document.body.classList.toggle('sidebar-open');
        } else {
            // Desktop behavior
            sidebar.classList.toggle('collapsed');
            if (toggle) {
                toggle.innerHTML = isCollapsed ? '<i class="fas fa-bars"></i>' : '<i class="fas fa-times"></i>';
            }
        }
    }
}

function switchSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Show selected section
    const targetSection = document.getElementById(sectionName + 'Section');
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });

    const activeNav = document.querySelector(`[data-section="${sectionName}"]`);
    if (activeNav) {
        activeNav.classList.add('active');
    }

    // Update page title
    const titles = {
        chat: 'Chat',
        history: 'Histórico',
        profile: 'Perfil',
        billing: 'Cobrança',
        settings: 'Configurações'
    };

    if (titles[sectionName]) {
        document.title = `ALICI™ - ${titles[sectionName]}`;
    }
}

function confirmAction(message, callback) {
    const modal = document.getElementById('confirmModal');
    const messageEl = document.getElementById('confirmMessage');
    const cancelBtn = document.getElementById('confirmCancel');
    const okBtn = document.getElementById('confirmOk');

    if (modal && messageEl) {
        messageEl.textContent = message;
        modal.classList.remove('hidden');

        const closeModal = () => modal.classList.add('hidden');

        cancelBtn.onclick = closeModal;
        document.querySelector('.modal-close').onclick = closeModal;

        okBtn.onclick = () => {
            closeModal();
            callback();
        };

        // Close on outside click
        modal.onclick = (e) => {
            if (e.target === modal) closeModal();
        };
    }
}

function clearChat() {
    confirmAction('Tem certeza que deseja limpar toda a conversa?', () => {
        const history = document.getElementById('chatHistory');
        if (history) {
            history.innerHTML = '';
            showToast('Conversa limpa', 'success');
        }
    });
}

function newChat() {
    confirmAction('Iniciar uma nova conversa?', () => {
        const history = document.getElementById('chatHistory');
        if (history) {
            history.innerHTML = '';
            showToast('Nova conversa iniciada', 'success');
        }
    });
}

// Theme toggle functionality
function toggleTheme() {
    const html = document.documentElement;
    const themeToggle = document.getElementById('themeToggle');

    if (html.hasAttribute('data-theme')) {
        html.removeAttribute('data-theme');
        localStorage.setItem('theme', 'dark');
        if (themeToggle) themeToggle.checked = false;
    } else {
        html.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
        if (themeToggle) themeToggle.checked = true;
    }
}

// Load saved theme
function loadTheme() {
    const savedTheme = localStorage.getItem('theme');
    const themeToggle = document.getElementById('themeToggle');

    if (savedTheme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
        if (themeToggle) themeToggle.checked = true;
    }
}

// Event listeners
window.addEventListener('DOMContentLoaded', () => {
    // Load theme
    loadTheme();

    // Chat form
    const form = document.getElementById('chatForm');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const input = document.getElementById('chatInput');
            if (input && input.value.trim()) {
                const text = input.value.trim();
                sendChat(text);
                input.value = '';
                updateCharCount();
            }
        });
    }

    // Chat input
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('input', updateCharCount);
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                form.dispatchEvent(new Event('submit'));
            }
        });
    }

    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.getAttribute('data-section');
            if (section) {
                switchSection(section);
            }
        });
    });

    // Action buttons
    const newChatBtn = document.getElementById('newChatBtn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', newChat);
    }

    const clearChatBtn = document.getElementById('clearChatBtn');
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', clearChat);
    }

    // Sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }

    // Logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            confirmAction('Tem certeza que deseja sair?', logout);
        });
    }

    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('change', toggleTheme);
    }

    // Settings toggle
    const notificationsToggle = document.getElementById('notificationsToggle');
    if (notificationsToggle) {
        notificationsToggle.addEventListener('change', (e) => {
            const enabled = e.target.checked;
            localStorage.setItem('notifications', enabled);
            showToast(`Notificações ${enabled ? 'ativadas' : 'desativadas'}`, 'info');
        });

        // Load saved setting
        const saved = localStorage.getItem('notifications') === 'true';
        notificationsToggle.checked = saved;
    }

    // Load initial data
    loadHistory();

    // Enable send button when input has content
    const sendBtn = document.getElementById('sendBtn');
    if (chatInput && sendBtn) {
        chatInput.addEventListener('input', () => {
            sendBtn.disabled = !chatInput.value.trim();
        });
    }

    // Mobile sidebar overlay click
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', toggleSidebar);
    }

    // Window resize handling
    window.addEventListener('resize', () => {
        const sidebar = document.getElementById('sidebar');
        if (window.innerWidth > 768 && sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
            document.body.classList.remove('sidebar-open');
        }
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K for new chat
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        newChat();
    }

    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal:not(.hidden)');
        if (openModal) {
            openModal.classList.add('hidden');
        }
    }
});