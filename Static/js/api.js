/**
 * api.js — ALICI v3.0 isolated API client
 * All HTTP calls to the backend go through this module.
 */

const API_BASE = window.location.origin;

function getToken() {
  return localStorage.getItem('access_token');
}

function setTokens(access, refresh) {
  if (access) localStorage.setItem('access_token', access);
  if (refresh) localStorage.setItem('refresh_token', refresh);
}

function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('alici_user');
}

async function _fetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    const refreshed = await _tryRefresh();
    if (refreshed) {
      const newToken = getToken();
      headers['Authorization'] = `Bearer ${newToken}`;
      return fetch(`${API_BASE}${path}`, { ...options, headers });
    }
    clearTokens();
    window.location.href = '/login';
    throw new Error('Sessão expirada');
  }

  return res;
}

async function _tryRefresh() {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) return false;
  try {
    const res = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    setTokens(data.access_token, data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

// Auth
export async function login(email, senha) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, senha }),
  });
  const data = await res.json();
  if (res.ok) {
    setTokens(data.access_token, data.refresh_token);
    if (data.usuario) localStorage.setItem('alici_user', JSON.stringify(data.usuario));
  }
  return { ok: res.ok, data };
}

export async function register(nome, email, senha) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome, email, senha }),
  });
  const data = await res.json();
  return { ok: res.ok, data };
}

export async function logout() {
  try {
    await _fetch('/auth/logout', { method: 'POST' });
  } catch {}
  clearTokens();
}

// Chat
export async function sendMessage(pergunta, incluir_emocao = false) {
  const res = await _fetch('/chat', {
    method: 'POST',
    body: JSON.stringify({ pergunta, incluir_emocao }),
  });
  const data = await res.json();
  return { ok: res.ok, data };
}

// Conversations
export async function listConversations(limit = 50) {
  const res = await _fetch(`/conversations?limit=${limit}`);
  const data = await res.json();
  return { ok: res.ok, data };
}

export async function createConversation(titulo = 'Nova conversa') {
  const res = await _fetch('/conversations', {
    method: 'POST',
    body: JSON.stringify({ titulo }),
  });
  const data = await res.json();
  return { ok: res.ok, data };
}

export async function getConversation(id) {
  const res = await _fetch(`/conversations/${id}`);
  const data = await res.json();
  return { ok: res.ok, data };
}

export async function deleteConversation(id) {
  const res = await _fetch(`/conversations/${id}`, { method: 'DELETE' });
  const data = await res.json();
  return { ok: res.ok, data };
}

export async function renameConversation(id, titulo) {
  const res = await _fetch(`/conversations/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ titulo }),
  });
  const data = await res.json();
  return { ok: res.ok, data };
}

// History
export async function getHistory(limit = 50) {
  const res = await _fetch(`/history?limit=${limit}`);
  const data = await res.json();
  return { ok: res.ok, data };
}

export async function clearHistory() {
  const res = await _fetch('/history', { method: 'DELETE' });
  const data = await res.json();
  return { ok: res.ok, data };
}

// Profile
export async function getProfile() {
  const res = await _fetch('/profile');
  const data = await res.json();
  return { ok: res.ok, data };
}

export async function updateProfile(fields) {
  const res = await _fetch('/profile', {
    method: 'PUT',
    body: JSON.stringify(fields),
  });
  const data = await res.json();
  return { ok: res.ok, data };
}

export async function changePassword(senha_atual, nova_senha) {
  const res = await _fetch('/profile/password', {
    method: 'PUT',
    body: JSON.stringify({ senha_atual, nova_senha }),
  });
  const data = await res.json();
  return { ok: res.ok, data };
}

export async function uploadAvatar(file) {
  const token = getToken();
  const formData = new FormData();
  formData.append('imagem', file);
  const res = await fetch(`${API_BASE}/profile/avatar`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });
  const data = await res.json();
  return { ok: res.ok, data };
}

// Billing
export async function getBillingPlans() {
  const res = await _fetch('/billing/plans');
  const data = await res.json();
  return { ok: res.ok, data };
}

export async function getUsage() {
  const res = await _fetch('/billing/usage');
  const data = await res.json();
  return { ok: res.ok, data };
}

export async function createCheckout(plano) {
  const res = await _fetch('/billing/create-checkout', {
    method: 'POST',
    body: JSON.stringify({ plano }),
  });
  const data = await res.json();
  return { ok: res.ok, data };
}
