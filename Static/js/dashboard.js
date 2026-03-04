// dashboard.js
// stubbed interactions for chat

window.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('chatInput');
    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const input = form.querySelector('input');
            if (input && input.value.trim()) {
                addMessage(input.value, 'user');
                input.value = '';
                // TODO: call /api/chat
            }
        });
    }
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