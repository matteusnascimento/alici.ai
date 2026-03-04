// dashboard.js
// connect dashboard UI to backend chat API and history

const API_CHAT = '/chat';
const API_HISTORY = '/history';

function getToken() {
    return localStorage.getItem('access_token');
}

function showLoading(show) {
    const ld = document.getElementById('loadingIndicator');
    if (ld) ld.classList.toggle('hidden', !show);
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
            const hist = data.historico || [];
            hist.reverse().forEach((h) => {
                addMessage(h.pergunta, 'user');
                addMessage(h.resposta, 'assistant');
            });
        } else {
            console.warn('failed to load history', data);
        }
    } catch (e) {
        console.error('history fetch error', e);
    }
}

async function sendChat(question) {
    const token = getToken();
    if (!token) {
        window.location.href = '/login';
        return;
    }
    showLoading(true);
    try {
        const res = await fetch(API_CHAT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token },
            body: JSON.stringify({ pergunta: question }),
        });
        const data = await res.json();
        if (res.ok) {
            addMessage(data.resposta, 'assistant');
        } else {
            addMessage(data.detail || 'Erro no servidor', 'assistant');
        }
    } catch (e) {
        addMessage('Falha de rede', 'assistant');
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
            window.location.href = '/login';
        });
    } else {
        window.location.href = '/login';
    }
}

window.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('chatInput');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const input = form.querySelector('input');
            if (input && input.value.trim()) {
                const text = input.value.trim();
                addMessage(text, 'user');
                input.value = '';
                sendChat(text);
            }
        });
    }

    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => { e.preventDefault();
            logout(); });
    }

    loadHistory();
});

function addMessage(text, sender) {
    const history = document.getElementById('chatHistory');
    if (!history) return;
    const msg = document.createElement('div');
    msg.className = 'message ' + sender;
    msg.textContent = text;
    history.appendChild(msg);
    history.scrollTop = history.scrollHeight;
}