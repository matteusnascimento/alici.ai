/**
 * chat.js — ChatGPT-style multi-conversation UI for ALICI™
 *
 * Depends on: /static/js/api.js (AliciAPI export)
 */

import { api } from "/static/js/api.js";

// ─── State ──────────────────────────────────────────────────────────────────
let currentConvId = null;
let sending = false;

// ─── Bootstrap ───────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  const token = api.getToken();
  if (!token) {
    window.location.href = "/";
    return;
  }

  applyTheme();
  initNeuralBg();
  bindUI();
  loadConversations();
});

// ─── Theme ───────────────────────────────────────────────────────────────────
function applyTheme() {
  const saved = localStorage.getItem("alici_theme") || "dark";
  document.documentElement.setAttribute("data-theme", saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "dark";
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("alici_theme", next);

  if (window.NeuralBg) window.NeuralBg.updateTheme();

  // Persist on server
  api.put("/auth/profile", { tema: next }).catch(() => {});
}

// ─── Neural background ───────────────────────────────────────────────────────
function initNeuralBg() {
  const canvas = document.getElementById("neuralCanvas");
  if (canvas && window.NeuralBg) {
    window.NeuralBg.init(canvas);
  }
}

// ─── UI binding ──────────────────────────────────────────────────────────────
function bindUI() {
  document.getElementById("btnNewChat").addEventListener("click", newConversation);
  document.getElementById("btnSend").addEventListener("click", sendMessage);
  document.getElementById("btnTheme").addEventListener("click", toggleTheme);
  document.getElementById("btnProfile").addEventListener("click", openProfileModal);
  document.getElementById("btnLogout").addEventListener("click", logout);
  document.getElementById("btnMenuToggle").addEventListener("click", toggleMobileSidebar);
  document.getElementById("sidebarOverlay").addEventListener("click", closeMobileSidebar);

  const input = document.getElementById("msgInput");
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  input.addEventListener("input", autoResize);

  // Profile modal actions
  document.getElementById("btnProfileSave").addEventListener("click", saveProfile);
  document.getElementById("btnProfileCancel").addEventListener("click", closeProfileModal);
  document.getElementById("profilePhotoInput").addEventListener("change", uploadPhoto);
}

function autoResize() {
  const el = document.getElementById("msgInput");
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 180) + "px";
}

// ─── Conversations ────────────────────────────────────────────────────────────
async function loadConversations() {
  try {
    const data = await api.get("/conversations");
    renderConversationList(data.conversations || []);
  } catch {
    renderConversationList([]);
  }
}

function renderConversationList(conversations) {
  const list = document.getElementById("conversationList");
  list.innerHTML = "";

  if (!conversations.length) {
    list.innerHTML = '<p style="color:var(--text-muted);font-size:13px;padding:12px 10px;">Sem conversas. Crie uma nova!</p>';
    return;
  }

  conversations.forEach((conv) => {
    const item = document.createElement("div");
    item.className = "conv-item" + (conv.id === currentConvId ? " active" : "");
    item.dataset.id = conv.id;

    const title = document.createElement("span");
    title.className = "conv-title";
    title.textContent = conv.titulo || "Nova conversa";

    const delBtn = document.createElement("button");
    delBtn.className = "btn-del-conv";
    delBtn.title = "Excluir";
    delBtn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>`;
    delBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      deleteConversation(conv.id);
    });

    item.appendChild(title);
    item.appendChild(delBtn);
    item.addEventListener("click", () => openConversation(conv.id, conv.titulo));

    list.appendChild(item);
  });
}

async function newConversation() {
  try {
    const data = await api.post("/conversations", {});
    if (data.conversation) {
      currentConvId = data.conversation.id;
      clearMessages();
      updateConvTitle("Nova conversa");
      await loadConversations();
      closeMobileSidebar();
    }
  } catch {
    showStatus("Erro ao criar conversa", "error");
  }
}

async function openConversation(convId, title) {
  currentConvId = convId;
  clearMessages();
  updateConvTitle(title || "Conversa");
  setActiveConvItem(convId);
  closeMobileSidebar();

  try {
    const data = await api.get(`/conversations/${convId}/messages`);
    const msgs = data.messages || [];
    if (msgs.length === 0) {
      showEmptyState(true);
    } else {
      showEmptyState(false);
      msgs.forEach((m) => appendMessage(m.content, m.role === "user" ? "user" : "ai"));
    }
  } catch {
    showStatus("Erro ao carregar mensagens", "error");
  }
}

async function deleteConversation(convId) {
  if (!confirm("Excluir esta conversa?")) return;
  try {
    await api.delete(`/conversations/${convId}`);
    if (currentConvId === convId) {
      currentConvId = null;
      clearMessages();
      updateConvTitle("Selecione uma conversa");
      showEmptyState(true);
    }
    await loadConversations();
  } catch {
    showStatus("Erro ao excluir conversa", "error");
  }
}

// ─── Messaging ────────────────────────────────────────────────────────────────
async function sendMessage() {
  if (sending) return;

  const input = document.getElementById("msgInput");
  const text = input.value.trim();
  if (!text) return;

  // Ensure a conversation exists
  if (!currentConvId) {
    await newConversation();
    if (!currentConvId) return;
  }

  sending = true;
  input.value = "";
  autoResize();
  document.getElementById("btnSend").disabled = true;

  showEmptyState(false);
  appendMessage(text, "user");
  setStatus("process");
  const typingEl = showTyping();

  try {
    const data = await api.post(`/conversations/${currentConvId}/messages`, { content: text });
    removeTyping(typingEl);

    const reply = data.message?.content || "Sem resposta.";
    appendMessage(reply, "ai");
    setStatus("online");

    // Update conversation title in sidebar after first message
    await loadConversations();
    setActiveConvItem(currentConvId);
  } catch {
    removeTyping(typingEl);
    appendMessage("Erro ao obter resposta. Tente novamente.", "ai");
    setStatus("online");
  } finally {
    sending = false;
    document.getElementById("btnSend").disabled = false;
    input.focus();
  }
}

// ─── DOM helpers ─────────────────────────────────────────────────────────────
function appendMessage(text, role) {
  const container = document.getElementById("messages");
  const div = document.createElement("div");
  div.className = `message ${role}-message`;
  div.textContent = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function showTyping() {
  const container = document.getElementById("messages");
  const el = document.createElement("div");
  el.className = "message ai-message";
  el.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
  container.appendChild(el);
  container.scrollTop = container.scrollHeight;
  return el;
}

function removeTyping(el) {
  if (el && el.parentNode) el.parentNode.removeChild(el);
}

function clearMessages() {
  document.getElementById("messages").innerHTML = "";
  showEmptyState(true);
}

function showEmptyState(show) {
  const es = document.getElementById("emptyState");
  const msgs = document.getElementById("messages");
  if (show) {
    es.style.display = "flex";
    msgs.style.display = "none";
  } else {
    es.style.display = "none";
    msgs.style.display = "flex";
  }
}

function updateConvTitle(title) {
  const el = document.getElementById("convTitle");
  if (el) el.textContent = title;
}

function setActiveConvItem(convId) {
  document.querySelectorAll(".conv-item").forEach((el) => {
    el.classList.toggle("active", parseInt(el.dataset.id) === convId);
  });
}

function setStatus(state) {
  const states = {
    analyze:  { color: "#ff0099", label: "Analisando" },
    process:  { color: "#00ff66", label: "Processando" },
    learn:    { color: "#ffcc00", label: "Aprendendo" },
    respond:  { color: "#00ffff", label: "Respondendo" },
    online:   { color: "#22d3ee", label: "Online" },
    error:    { color: "#ef4444", label: "Erro" },
  };
  const s = states[state] || states.online;
  const dot = document.getElementById("statusDot");
  const label = document.getElementById("statusLabel");
  if (dot) { dot.style.background = s.color; dot.style.boxShadow = `0 0 8px ${s.color}`; }
  if (label) label.textContent = s.label;
}

function showStatus(msg, type) {
  console.warn(`[ALICI] ${type}: ${msg}`);
}

function showToast(msg, type = "info") {
  const colors = { error: "#ef4444", success: "#22d3ee", info: "#6b7280" };
  const toast = document.createElement("div");
  toast.style.cssText = `
    position:fixed;bottom:24px;right:24px;z-index:200;
    background:var(--bg-tertiary);color:var(--text-primary);
    border-left:3px solid ${colors[type] || colors.info};
    padding:12px 18px;border-radius:8px;font-size:14px;
    box-shadow:0 4px 16px rgba(0,0,0,0.3);
    transition:opacity 0.3s;max-width:320px;
  `;
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => { toast.style.opacity = "0"; setTimeout(() => toast.remove(), 350); }, 3000);
}

// ─── Mobile sidebar ───────────────────────────────────────────────────────────
function toggleMobileSidebar() {
  document.getElementById("chatApp").classList.toggle("sidebar-open");
}

function closeMobileSidebar() {
  document.getElementById("chatApp").classList.remove("sidebar-open");
}

// ─── Profile modal ────────────────────────────────────────────────────────────
async function openProfileModal() {
  document.getElementById("profileModal").classList.add("open");
  try {
    const data = await api.get("/auth/profile");
    document.getElementById("profileName").value = data.nome || "";
    document.getElementById("profileEmail").value = data.email || "";

    const photoEl = document.getElementById("profilePhoto");
    if (photoEl && data.foto_url) photoEl.src = data.foto_url;
  } catch {}
}

function closeProfileModal() {
  document.getElementById("profileModal").classList.remove("open");
}

async function saveProfile() {
  const nome = document.getElementById("profileName").value.trim();
  const senhaAtual = document.getElementById("profileCurrentPassword").value;
  const novaSenha = document.getElementById("profileNewPassword").value;

  const payload = {};
  if (nome) payload.nome = nome;
  if (novaSenha) { payload.senha_atual = senhaAtual; payload.nova_senha = novaSenha; }

  try {
    await api.put("/auth/profile", payload);
    closeProfileModal();
    showToast("Perfil atualizado com sucesso!", "success");
  } catch {
    showToast("Erro ao atualizar perfil. Tente novamente.", "error");
  }
}

async function uploadPhoto() {
  const file = document.getElementById("profilePhotoInput").files[0];
  if (!file) return;

  const fd = new FormData();
  fd.append("foto", file);

  try {
    const data = await api.postForm("/auth/profile/photo", fd);
    const photoEl = document.getElementById("profilePhoto");
    if (photoEl && data.foto_url) photoEl.src = data.foto_url;
    showToast("Foto atualizada com sucesso!", "success");
  } catch {
    showToast("Erro ao enviar foto. Verifique o tamanho (máx. 5MB).", "error");
  }
}

// ─── Logout ───────────────────────────────────────────────────────────────────
async function logout() {
  try { await api.post("/auth/logout", {}); } catch {}
  api.clearTokens();
  window.location.href = "/";
}
