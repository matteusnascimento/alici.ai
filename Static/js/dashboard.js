/**
 * dashboard.js — ALICI v3.0 Dashboard Logic
 */

import * as API from '/Static/js/api.js';

// ===== State =====
let currentConvId = null;
let conversations = [];
let userProfile = null;
let isSending = false;

const MAX_CONVERSATION_TITLE_LENGTH = 40;

// ===== DOM helpers =====
const $ = (id) => document.getElementById(id);
const $el = (tag, cls, html = '') => {
  const el = document.createElement(tag);
  if (cls) el.className = cls;
  if (html) el.innerHTML = html;
  return el;
};

// ===== Theme =====
function getTheme() {
  return localStorage.getItem('alici_theme') || 'dark';
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('alici_theme', theme);
  const btn = $('theme-toggle');
  if (btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
}

function toggleTheme() {
  const next = getTheme() === 'dark' ? 'light' : 'dark';
  applyTheme(next);
  // Persist to server (non-blocking)
  API.updateProfile({ tema: next }).catch(() => {});
}

// ===== Auth guard =====
function checkAuth() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    window.location.href = '/login';
    return false;
  }
  return true;
}

// ===== Profile =====
async function loadProfile() {
  const { ok, data } = await API.getProfile();
  if (!ok) return;
  userProfile = data.profile || {};

  // Apply server-stored theme if no local preference
  if (!localStorage.getItem('alici_theme') && userProfile.tema) {
    applyTheme(userProfile.tema);
  }

  // Update usage bar
  updateUsageBar(userProfile.mensagens_hoje, userProfile.limite_diario);

  // Update avatar/name
  const nameEl = $('sidebar-user-name');
  if (nameEl) nameEl.textContent = userProfile.nome || 'Usuário';

  const planEl = $('sidebar-plan-badge');
  if (planEl) planEl.textContent = (userProfile.plano || 'free').toUpperCase();

  if (userProfile.foto_url) {
    const avatarEl = document.querySelector('.sidebar-avatar');
    if (avatarEl) avatarEl.style.backgroundImage = `url(${userProfile.foto_url})`;
  }
}

function updateUsageBar(used, limit) {
  const fill = $('usage-fill');
  const label = $('usage-label');
  if (!fill || !label) return;
  if (!limit) {
    label.textContent = `${used} msgs hoje`;
    fill.style.width = '10%';
    return;
  }
  const pct = Math.min((used / limit) * 100, 100);
  fill.style.width = pct + '%';
  label.textContent = `${used}/${limit}`;
}

// ===== Conversations =====
async function loadConversations() {
  const { ok, data } = await API.listConversations(50);
  if (!ok) return;
  conversations = data.conversations || [];
  renderConversationList();
}

function renderConversationList() {
  const list = $('conv-list');
  if (!list) return;
  list.innerHTML = '';

  if (conversations.length === 0) {
    list.innerHTML = `<div style="padding:12px;font-size:0.8rem;color:var(--text-muted);text-align:center">Nenhuma conversa ainda</div>`;
    return;
  }

  for (const conv of conversations) {
    const item = $el('div', `conv-item${conv.id === currentConvId ? ' active' : ''}`);
    item.dataset.id = conv.id;
    item.innerHTML = `
      <span class="conv-item-icon">💬</span>
      <span class="conv-item-title">${escHtml(conv.titulo || 'Conversa')}</span>
      <span class="conv-item-actions">
        <button class="conv-action-btn" title="Renomear" onclick="event.stopPropagation();renameConv(${conv.id})">✏️</button>
        <button class="conv-action-btn" title="Excluir" onclick="event.stopPropagation();deleteConv(${conv.id})">🗑️</button>
      </span>
    `;
    item.addEventListener('click', () => openConversation(conv.id, conv.titulo));
    list.appendChild(item);
  }
}

async function newChat() {
  clearMessages();
  currentConvId = null;
  setTopbarTitle('Nova conversa');
  updateActiveConv(null);
  showWelcome();
  closeSidebar();
}

async function openConversation(id, titulo) {
  currentConvId = id;
  setTopbarTitle(titulo || 'Conversa');
  updateActiveConv(id);
  clearMessages();
  hideWelcome();
  closeSidebar();

  const { ok, data } = await API.getConversation(id);
  if (!ok) return;

  const msgs = data.messages || [];
  for (const m of msgs) {
    appendMessage(m.role === 'user' ? 'user' : 'ai', m.content);
  }
  scrollToBottom();
}

window.renameConv = async function (id) {
  const conv = conversations.find((c) => c.id === id);
  const newTitle = prompt('Novo nome da conversa:', conv?.titulo || '');
  if (!newTitle || !newTitle.trim()) return;
  await API.renameConversation(id, newTitle.trim());
  await loadConversations();
};

window.deleteConv = async function (id) {
  if (!confirm('Excluir esta conversa?')) return;
  await API.deleteConversation(id);
  if (currentConvId === id) newChat();
  await loadConversations();
};

function updateActiveConv(id) {
  document.querySelectorAll('.conv-item').forEach((el) => {
    el.classList.toggle('active', Number(el.dataset.id) === id);
  });
}

// ===== Messages =====
function clearMessages() {
  const area = $('messages-area');
  if (area) area.innerHTML = '';
}

function showWelcome() {
  const w = $('welcome-screen');
  if (w) w.style.display = 'flex';
  const area = $('messages-area');
  if (area) area.style.display = 'none';
}

function hideWelcome() {
  const w = $('welcome-screen');
  if (w) w.style.display = 'none';
  const area = $('messages-area');
  if (area) area.style.display = 'flex';
}

function appendMessage(role, text) {
  hideWelcome();
  const area = $('messages-area');
  if (!area) return;

  const isUser = role === 'user';
  const row = $el('div', `msg-row ${role}`);
  row.innerHTML = `
    <div class="msg-avatar ${isUser ? 'user-avatar' : ''}">${isUser ? '👤' : 'A'}</div>
    <div class="msg-bubble">${escHtml(text)}</div>
  `;
  area.appendChild(row);
  scrollToBottom();
  return row;
}

function showTyping() {
  const area = $('messages-area');
  if (!area) return null;
  const row = $el('div', 'msg-row ai');
  row.id = 'typing-row';
  row.innerHTML = `
    <div class="msg-avatar">A</div>
    <div class="msg-bubble">
      <div class="typing-indicator">
        <div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>
      </div>
    </div>
  `;
  area.appendChild(row);
  scrollToBottom();
  return row;
}

function removeTyping() {
  const row = $('typing-row');
  if (row) row.remove();
}

function scrollToBottom() {
  const area = $('messages-area');
  if (area) area.scrollTop = area.scrollHeight;
}

// ===== Send message =====
async function sendMessage() {
  if (isSending) return;
  const input = $('user-input');
  if (!input) return;

  const text = input.value.trim();
  if (!text) return;

  isSending = true;
  input.value = '';
  resizeTextarea(input);
  setSendDisabled(true);

  // Create conversation if none selected
  if (!currentConvId) {
    const title = text.slice(0, MAX_CONVERSATION_TITLE_LENGTH) || 'Nova conversa';
    const { ok, data } = await API.createConversation(title);
    if (ok && data.conversation) {
      currentConvId = data.conversation.id;
      conversations.unshift(data.conversation);
      renderConversationList();
      setTopbarTitle(title);
      updateActiveConv(currentConvId);
    }
    hideWelcome();
  }

  appendMessage('user', text);
  const typingRow = showTyping();

  try {
    const { ok, data } = await API.sendMessage(text, false);
    removeTyping();

    if (ok && data.resposta) {
      appendMessage('ai', data.resposta);
      updateUsageBar(data.mensagens_hoje, data.limite_diario);
    } else {
      const msg = data?.message || data?.detail || 'Erro ao obter resposta.';
      appendMessage('ai', `⚠️ ${msg}`);
    }
  } catch (err) {
    removeTyping();
    appendMessage('ai', '⚠️ Erro de conexão. Tente novamente.');
  } finally {
    isSending = false;
    setSendDisabled(false);
    input.focus();
  }
}

function setSendDisabled(disabled) {
  const btn = $('send-btn');
  if (btn) btn.disabled = disabled;
}

function handleInputKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function resizeTextarea(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 140) + 'px';
}

function useSuggestion(text) {
  const input = $('user-input');
  if (!input) return;
  input.value = text;
  input.focus();
  resizeTextarea(input);
}

// ===== Panels =====
function openPanel(id) {
  const panel = $(id);
  if (panel) {
    panel.classList.add('open');
    if (id === 'profile-panel') loadProfilePanel();
    if (id === 'billing-panel') loadBillingPanel();
  }
}

function closePanel(id) {
  const panel = $(id);
  if (panel) panel.classList.remove('open');
}

async function loadProfilePanel() {
  if (!userProfile) await loadProfile();
  const nameEl = $('profile-name-input');
  const themeEl = $('profile-theme-select');
  const avatarEl = $('profile-avatar-preview');
  const planEl = $('profile-plan-display');

  if (nameEl) nameEl.value = userProfile?.nome || '';
  if (themeEl) themeEl.value = getTheme();
  if (planEl) planEl.textContent = (userProfile?.plano || 'free').toUpperCase();
  if (avatarEl && userProfile?.foto_url) {
    avatarEl.innerHTML = `<img src="${userProfile.foto_url}" alt="avatar">`;
  } else if (avatarEl && userProfile?.nome) {
    avatarEl.textContent = userProfile.nome[0].toUpperCase();
  }
}

async function saveProfile() {
  const nome = $('profile-name-input')?.value?.trim();
  const tema = $('profile-theme-select')?.value;
  const errEl = $('profile-error');
  const okEl = $('profile-success');

  if (nome && nome.length < 2) {
    showAlert(errEl, 'Nome muito curto');
    return;
  }

  const updates = {};
  if (nome) updates.nome = nome;
  if (tema) updates.tema = tema;

  const { ok, data } = await API.updateProfile(updates);
  if (ok) {
    if (tema) applyTheme(tema);
    showAlert(okEl, 'Perfil atualizado!');
    await loadProfile();
  } else {
    showAlert(errEl, data?.message || 'Erro ao atualizar');
  }
}

async function changePassword() {
  const curr = $('curr-password')?.value;
  const next = $('new-password')?.value;
  const errEl = $('password-error');
  const okEl = $('password-success');

  if (!curr || !next) { showAlert(errEl, 'Preencha todos os campos'); return; }
  if (next.length < 8) { showAlert(errEl, 'Nova senha deve ter ao menos 8 caracteres'); return; }

  const { ok, data } = await API.changePassword(curr, next);
  if (ok) {
    showAlert(okEl, 'Senha alterada!');
    $('curr-password').value = '';
    $('new-password').value = '';
  } else {
    showAlert(errEl, data?.message || 'Erro ao alterar senha');
  }
}

async function uploadAvatar() {
  const file = $('avatar-file-input')?.files?.[0];
  if (!file) return;
  const errEl = $('profile-error');
  const okEl = $('profile-success');

  const { ok, data } = await API.uploadAvatar(file);
  if (ok) {
    showAlert(okEl, 'Avatar atualizado!');
    if (data.foto_url) {
      const avatarEl = $('profile-avatar-preview');
      if (avatarEl) avatarEl.innerHTML = `<img src="${data.foto_url}" alt="avatar">`;
    }
    await loadProfile();
  } else {
    showAlert(errEl, data?.message || 'Erro ao enviar avatar');
  }
}

async function loadBillingPanel() {
  const { ok, data } = await API.getUsage();
  if (ok) {
    const el = $('billing-usage-info');
    if (el) {
      const pct = data.porcentagem_uso || 0;
      el.innerHTML = `
        <p style="margin-bottom:8px;font-size:0.85rem;color:var(--text-secondary)">
          Mensagens hoje: <strong>${data.mensagens_hoje}</strong> / ${data.limite_diario ?? '∞'}
        </p>
        <div class="usage-bar" style="width:100%;height:8px">
          <div class="usage-fill" style="width:${pct}%"></div>
        </div>
      `;
    }
  }
}

async function checkout(plano) {
  const { ok, data } = await API.createCheckout(plano);
  if (ok && data.checkout_url) {
    window.location.href = data.checkout_url;
  } else {
    alert(data?.message || 'Erro ao iniciar checkout');
  }
}

// ===== Sidebar mobile =====
function openSidebar() {
  const s = $('sidebar');
  const b = $('sidebar-backdrop');
  if (s) s.classList.add('open');
  if (b) b.classList.add('open');
}

function closeSidebar() {
  const s = $('sidebar');
  const b = $('sidebar-backdrop');
  if (s) s.classList.remove('open');
  if (b) b.classList.remove('open');
}

// ===== Utilities =====
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function showAlert(el, msg) {
  if (!el) return;
  el.textContent = msg;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 4000);
}

function setTopbarTitle(title) {
  const el = $('topbar-title');
  if (el) el.textContent = title;
}

// ===== Expose globals needed by inline HTML handlers =====
window.toggleTheme = toggleTheme;
window.newChat = newChat;
window.sendMessage = sendMessage;
window.handleInputKey = handleInputKey;
window.resizeTextarea = resizeTextarea;
window.useSuggestion = useSuggestion;
window.openPanel = openPanel;
window.closePanel = closePanel;
window.saveProfile = saveProfile;
window.changePassword = changePassword;
window.uploadAvatar = uploadAvatar;
window.checkout = checkout;
window.openSidebar = openSidebar;
window.closeSidebar = closeSidebar;

// ===== Logout =====
async function doLogout() {
  await API.logout();
  window.location.href = '/login';
}
window.doLogout = doLogout;

// ===== Init =====
document.addEventListener('DOMContentLoaded', async () => {
  if (!checkAuth()) return;

  applyTheme(getTheme());

  const input = $('user-input');
  if (input) {
    input.addEventListener('input', () => resizeTextarea(input));
  }

  await Promise.all([loadProfile(), loadConversations()]);

  showWelcome();
});
