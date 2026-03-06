const state = { currentSection: 'dashboard', chart: null, theme: localStorage.getItem('alici_theme') || 'dark', sidebarCollapsed: false };
document.addEventListener('DOMContentLoaded', () => initializeApp());

function initializeApp() {
    initializeTheme();
    bindUI();
    initializeParticles();
    initializeChart();
    initializeLucide();
    bootLoader()
}

function initializeLucide() { if (window.lucide) { window.lucide.createIcons() } }

function bootLoader() {
    const loader = document.getElementById('appLoader');
    setTimeout(() => loader.classList.add('hide'), 900)
}

function bindUI() {
    const loginForm = document.getElementById('loginForm');
    const chatForm = document.getElementById('chatForm');
    const themeToggle = document.getElementById('themeToggle');
    const notifyBtn = document.getElementById('notifyBtn');
    const openSidebarBtn = document.getElementById('openSidebarBtn');
    const closeSidebarBtn = document.getElementById('closeSidebarBtn');
    const collapseSidebarBtn = document.getElementById('toggleSidebarBtn');
    const overlay = document.getElementById('sidebarOverlay');
    document.querySelectorAll('.nav-item').forEach(item => item.addEventListener('click', () => { showSection(item.dataset.section); if (window.innerWidth <= 768) { closeMobileSidebar() } }));
    loginForm.addEventListener('submit', e => {
        e.preventDefault();
        login()
    });
    chatForm.addEventListener('submit', e => {
        e.preventDefault();
        sendMessage()
    });
    document.getElementById('chatInput').addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage()
        }
    });
    themeToggle.addEventListener('click', toggleTheme);
    notifyBtn.addEventListener('click', () => showNotification('Você está com tudo sincronizado.'));
    openSidebarBtn.addEventListener('click', () => {
        if (window.innerWidth <= 768) { document.getElementById('app').classList.add('sidebar-open'); return }
        toggleSidebar()
    });
    closeSidebarBtn.addEventListener('click', closeMobileSidebar);
    overlay.addEventListener('click', closeMobileSidebar);
    collapseSidebarBtn.addEventListener('click', toggleSidebar);
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) logoutBtn.addEventListener('click', logout);
    window.addEventListener('resize', () => { if (window.innerWidth > 768) { closeMobileSidebar() } });
    if (localStorage.getItem('alici_jwt')) {
        unlockApp();
        showNotification('Sessão restaurada com JWT local.')
    }
}

function login() {
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();
    if (!email || !password) { showNotification('Preencha e-mail e senha para continuar.', 'warning'); return }
    localStorage.setItem('alici_jwt', `alici.jwt.${Date.now()}`);
    unlockApp();
    showNotification('Login concluído. Bem-vindo(a) à ALICI!')
}

function unlockApp() {
    document.getElementById('loginScreen').classList.add('hidden');
    document.getElementById('app').classList.remove('hidden');
    autoScroll()
}

function logout() {
    localStorage.removeItem('alici_jwt');
    document.getElementById('loginScreen').classList.remove('hidden');
    document.getElementById('app').classList.add('hidden');
    document.getElementById('email').value = '';
    document.getElementById('password').value = '';
    showNotification('Você foi desconectado.');
}

function closeMobileSidebar() { document.getElementById('app').classList.remove('sidebar-open') }

function toggleSidebar() {
    const app = document.getElementById('app');
    state.sidebarCollapsed = !state.sidebarCollapsed;
    app.classList.toggle('sidebar-collapsed', state.sidebarCollapsed)
}

function showSection(sectionId) {
    state.currentSection = sectionId;
    document.querySelectorAll('.app-section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(i => { i.classList.remove('active'); if (i.dataset.section === sectionId) { i.classList.add('active') } });
    const active = document.getElementById(sectionId);
    if (active) { active.classList.add('active') }
    const title = document.getElementById('sectionTitle');
    title.textContent = { dashboard: 'Dashboard', chat: 'Chat IA', models: 'Modelos', analytics: 'Analytics', settings: 'Configurações', billing: 'Planos & Faturamento' }[sectionId] || 'ALICI';
    if (sectionId === 'chat') { autoScroll() }
}

function appendMessage(content, role = 'assistant') {
    const messages = document.getElementById('chatMessages');
    const el = document.createElement('article');
    el.className = `message ${role==='user'?'user-message':'assistant-message'}`;
    const paragraph = document.createElement('p');
    paragraph.textContent = content;
    el.appendChild(paragraph);
    messages.appendChild(el);
    autoScroll()
}

function createTypingLoader() {
    const messages = document.getElementById('chatMessages');
    const loader = document.createElement('article');
    loader.className = 'message assistant-message';
    loader.id = 'typingLoader';
    loader.innerHTML = '<div class="loading-message"><span></span><span></span><span></span></div>';
    messages.appendChild(loader);
    autoScroll()
}

function removeTypingLoader() { const loader = document.getElementById('typingLoader'); if (loader) { loader.remove() } }
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const userMessage = input.value.trim();
    if (!userMessage) { return }
    appendMessage(userMessage, 'user');
    input.value = '';
    input.focus();
    createTypingLoader();
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    try {
        const response = await fetch('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: userMessage }), signal: controller.signal });
        let responseText = 'Recebi sua mensagem. Integre o endpoint para resposta em tempo real.';
        if (response.ok) {
            const data = await response.json();
            responseText = data.response || data.reply || data.message || responseText
        } else { responseText = `Erro ${response.status}: não foi possível obter resposta agora.` }
        removeTypingLoader();
        appendMessage(responseText, 'assistant')
    } catch (error) {
        removeTypingLoader();
        appendMessage('Falha de conexão com o servidor. Verifique o backend e tente novamente.', 'assistant');
        showNotification('Erro ao conectar no endpoint /chat.', 'error')
    } finally { clearTimeout(timeout) }
}

function autoScroll() { const messages = document.getElementById('chatMessages'); if (messages) { messages.scrollTo({ top: messages.scrollHeight, behavior: 'smooth' }) } }

function showNotification(message, type = 'success') {
    const container = document.getElementById('notifications');
    const toast = document.createElement('div');
    toast.className = 'toast';
    if (type === 'error') { toast.style.borderColor = 'rgba(239,68,68,.45)' }
    if (type === 'warning') { toast.style.borderColor = 'rgba(245,158,11,.45)' }
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(8px)';
        setTimeout(() => toast.remove(), 200)
    }, 2600)
}

function toggleTheme() {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', state.theme);
    localStorage.setItem('alici_theme', state.theme);
    const icon = document.querySelector('#themeToggle i');
    icon.setAttribute('data-lucide', state.theme === 'dark' ? 'moon' : 'sun');
    initializeLucide();
    if (state.chart) {
        state.chart.destroy();
        initializeChart()
    }
}

function initializeTheme() { document.documentElement.setAttribute('data-theme', state.theme) }

function initializeChart() {
    const canvas = document.getElementById('requestsChart');
    if (!canvas || typeof Chart === 'undefined') { return }
    const light = document.documentElement.getAttribute('data-theme') === 'light';
    const textColor = light ? '#334155' : '#94a3b8';
    const gridColor = light ? 'rgba(148,163,184,.25)' : 'rgba(148,163,184,.16)';
    state.chart = new Chart(canvas, { type: 'line', data: { labels: ['00h', '04h', '08h', '12h', '16h', '20h', '24h'], datasets: [{ label: 'Requisições', data: [210, 340, 440, 620, 740, 680, 510], borderColor: '#22d3ee', backgroundColor: 'rgba(34,211,238,.14)', fill: true, tension: .35, pointRadius: 2 }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: textColor } } }, scales: { x: { ticks: { color: textColor }, grid: { color: gridColor } }, y: { ticks: { color: textColor }, grid: { color: gridColor } } } } })
}

/* ========== PROFILE & BILLING FUNCTIONS ========== */

document.addEventListener('DOMContentLoaded', () => {
    const profileBtn = document.getElementById('profileBtn');
    const closeProfileBtn = document.getElementById('closeProfileBtn');
    const profileModal = document.getElementById('profileModal');
    const modalOverlay = profileModal ? .querySelector('.modal-overlay');

    if (profileBtn) {
        profileBtn.addEventListener('click', openProfileModal);
    }

    if (closeProfileBtn) {
        closeProfileBtn.addEventListener('click', closeProfileModal);
    }

    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeProfileModal);
    }

    const planBtns = document.querySelectorAll('.plan-btn');
    planBtns.forEach(btn => {
        btn.addEventListener('click', (e) => handlePlanSelection(e.target.dataset.plan));
    });

    const saveProfileBtn = document.getElementById('saveProfileBtn');
    if (saveProfileBtn) {
        saveProfileBtn.addEventListener('click', saveProfile);
    }

    const changePasswordBtn = document.getElementById('changePasswordBtn');
    if (changePasswordBtn) {
        changePasswordBtn.addEventListener('click', openChangePassword);
    }
});

function openProfileModal() {
    const modal = document.getElementById('profileModal');
    if (modal) {
        modal.classList.remove('hidden');
        initializeLucide();
    }
}

function closeProfileModal() {
    const modal = document.getElementById('profileModal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

function handlePlanSelection(plan) {
    const plans = { starter: 'Starter', professional: 'Professional', enterprise: 'Enterprise' };
    const planName = plans[plan];

    if (plan === 'starter') {
        showNotification('Você já está no plano Starter.', 'warning');
        return;
    }

    if (plan === 'enterprise') {
        window.location.href = 'mailto:vendas@alici.ai?subject=Interesse em Plano Enterprise';
        return;
    }

    if (plan === 'professional') {
        showNotification(`Redirecionando para checkout do plano ${planName}...`);
        setTimeout(() => {
            window.location.href = '/billing/checkout?plan=professional';
        }, 1200);
    }
}

function saveProfile() {
    const fullName = document.getElementById('profileFullName') ? .value;
    const currentPassword = document.getElementById('profileCurrentPassword') ? .value;
    const newPassword = document.getElementById('profileNewPassword') ? .value;

    if (!fullName || fullName.trim() === '') {
        showNotification('Nome não pode estar vazio.', 'warning');
        return;
    }

    if (newPassword && newPassword.length < 8) {
        showNotification('Senha deve ter no mínimo 8 caracteres.', 'warning');
        return;
    }

    showNotification('Perfil atualizado com sucesso!');
    setTimeout(() => closeProfileModal(), 1200);
}

function openChangePassword() {
    document.getElementById('profileCurrentPassword') ? .focus();
    showNotification('Digite sua senha atual e uma nova senha.');
}

function initializeParticles() {
    const canvas = document.getElementById('particlesCanvas');
    const ctx = canvas.getContext('2d');
    const particles = [];
    const quantity = 80;
    const resize = () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight
    };
    const make = () => ({ x: Math.random() * canvas.width, y: Math.random() * canvas.height, radius: Math.random() * 1.8 + .4, speedX: (Math.random() - .5) * .28, speedY: (Math.random() - .5) * .28, opacity: Math.random() * .6 + .2 });
    const draw = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => {
            p.x += p.speedX;
            p.y += p.speedY;
            if (p.x < 0 || p.x > canvas.width) { p.speedX *= -1 }
            if (p.y < 0 || p.y > canvas.height) { p.speedY *= -1 }
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(34,211,238,${p.opacity})`;
            ctx.fill()
        });
        requestAnimationFrame(draw)
    };
    resize();
    window.addEventListener('resize', resize);
    for (let i = 0; i < quantity; i += 1) { particles.push(make()) }
    draw()
}