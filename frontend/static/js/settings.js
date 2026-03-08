const integrationsCatalog = [
    { key: "whatsapp", label: "WhatsApp", icon: "fa-brands fa-whatsapp" },
    { key: "instagram", label: "Instagram", icon: "fa-brands fa-instagram" },
    { key: "facebook", label: "Facebook", icon: "fa-brands fa-facebook" },
    { key: "telegram", label: "Telegram", icon: "fa-brands fa-telegram" },
    { key: "api", label: "API", icon: "fa-solid fa-code" },
];

function getToken() {
    return localStorage.getItem("access_token") || localStorage.getItem("alici_jwt");
}

async function apiFetch(url, options = {}) {
    const token = getToken();
    const headers = {...(options.headers || {}) };
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        ...options,
        headers,
    });

    let data = {};
    try {
        data = await response.json();
    } catch (_err) {
        data = {};
    }

    if (!response.ok) {
        throw new Error(data.detail || data.message || `Erro ${response.status}`);
    }

    return data;
}

function setFeedback(message, target = "globalFeedback") {
    const el = document.getElementById(target);
    if (el) {
        el.textContent = message;
    }
}

function switchTab(tab) {
    document.querySelectorAll(".menu-item").forEach((item) => {
        item.classList.toggle("active", item.dataset.tab === tab);
    });

    document.querySelectorAll(".tab-panel").forEach((panel) => {
        panel.classList.toggle("active", panel.id === `tab-${tab}`);
    });

    const url = new URL(window.location.href);
    url.searchParams.set("tab", tab);
    window.history.replaceState({}, "", url);
}

function readChecked(name, fallback) {
    const checked = document.querySelector(`input[name="${name}"]:checked`);
    return checked ? checked.value : fallback;
}

async function loadProfile() {
    const data = await apiFetch("/api/user/profile");
    document.getElementById("nameInput").value = data.full_name || "";
    document.getElementById("emailInput").value = data.email || "";
    document.getElementById("phoneInput").value = data.phone || "";
    document.getElementById("planLabel").textContent = data.plan || "Plano Gratis";
    document.getElementById("avatarPreview").src = data.avatar_url || "/static/avatars/default.svg";
}

async function saveProfile() {
    const payload = {
        full_name: document.getElementById("nameInput").value,
        email: document.getElementById("emailInput").value,
        phone: document.getElementById("phoneInput").value,
    };

    await apiFetch("/api/user/update", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    setFeedback("Perfil atualizado com sucesso.");
}

async function uploadAvatar(file) {
    if (!file) {
        return;
    }

    const token = getToken();
    const formData = new FormData();
    formData.append("avatar", file);

    const headers = {};
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const res = await fetch("/api/user/avatar", {
        method: "POST",
        headers,
        body: formData,
    });

    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.detail || "Falha ao enviar avatar");
    }

    document.getElementById("avatarPreview").src = data.avatar_url;
    setFeedback("Avatar atualizado.");
}

async function loadThemeAndLanguage() {
    const data = await apiFetch("/api/settings/theme");

    document.getElementById("languageSelect").value = data.language || "pt-BR";

    const theme = data.theme || "dark";
    const accent = data.accent || "blue";

    const themeInput = document.querySelector(`input[name="theme"][value="${theme}"]`) ||
        document.querySelector('input[name="theme"][value="dark"]');
    if (themeInput) {
        themeInput.checked = true;
    }

    const accentInput = document.querySelector(`input[name="accent"][value="${accent}"]`) ||
        document.querySelector('input[name="accent"][value="blue"]');
    if (accentInput) {
        accentInput.checked = true;
    }
}

async function saveThemeAndLanguage() {
    const payload = {
        language: document.getElementById("languageSelect").value,
        theme: readChecked("theme", "dark"),
        accent: readChecked("accent", "blue"),
    };

    await apiFetch("/api/settings/theme", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    setFeedback("Personalizacao salva.");
}

async function loadNotifications() {
    const data = await apiFetch("/api/settings/notifications");
    document.getElementById("notifChat").checked = !!data.chat_notifications;
    document.getElementById("notifAgents").checked = !!data.agent_activity_notifications;
    document.getElementById("notifSystem").checked = !!data.system_updates_notifications;
    document.getElementById("notifMarketing").checked = !!data.marketing_notifications;
}

async function saveNotifications() {
    const payload = {
        chat_notifications: document.getElementById("notifChat").checked,
        agent_activity_notifications: document.getElementById("notifAgents").checked,
        system_updates_notifications: document.getElementById("notifSystem").checked,
        marketing_notifications: document.getElementById("notifMarketing").checked,
    };

    await apiFetch("/api/settings/notifications", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    setFeedback("Notificacoes salvas.");
}

async function loadAISettings() {
    const data = await apiFetch("/api/settings/ai");
    document.getElementById("aiModel").value = data.default_model || "ALICI Core";
    document.getElementById("aiTemperature").value = data.temperature ?? 0.7;
    document.getElementById("aiMemory").checked = !!data.memory_enabled;
    document.getElementById("aiWebSearch").checked = !!data.web_search_enabled;
}

async function saveAISettings() {
    const payload = {
        default_model: document.getElementById("aiModel").value,
        temperature: Number(document.getElementById("aiTemperature").value || 0.7),
        memory_enabled: document.getElementById("aiMemory").checked,
        web_search_enabled: document.getElementById("aiWebSearch").checked,
    };

    await apiFetch("/api/settings/ai", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    setFeedback("Configuracoes de IA salvas.");
}

async function startUpgradeCheckout() {
    const payload = { plan: "pro" };
    const data = await apiFetch("/api/billing/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    if (data.checkout_url) {
        window.location.href = data.checkout_url;
        return;
    }
    setFeedback("Checkout iniciado sem URL de redirecionamento.");
}

async function saveSecurity() {
    const currentPassword = document.getElementById("currentPasswordInput").value;
    const newPassword = document.getElementById("newPasswordInput").value;
    const confirmPassword = document.getElementById("confirmPasswordInput").value;

    if (!currentPassword || !newPassword) {
        throw new Error("Preencha senha atual e nova senha.");
    }

    if (newPassword !== confirmPassword) {
        throw new Error("Confirmacao de senha nao confere.");
    }

    await apiFetch("/api/user/password", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword,
        }),
    });

    document.getElementById("currentPasswordInput").value = "";
    document.getElementById("newPasswordInput").value = "";
    document.getElementById("confirmPasswordInput").value = "";
    setFeedback("Configuracoes de seguranca atualizadas.");
}

function renderIntegrationCards() {
    const container = document.getElementById("integrationCards");
    if (!container) {
        return;
    }

    container.innerHTML = integrationsCatalog.map((item) => `
        <article class="integration-card">
            <h3><i class="${item.icon}"></i> ${item.label}</h3>
            <p class="tag">Conecte este canal ao seu agente.</p>
            <button class="btn-primary connect-btn" data-platform="${item.key}" type="button">Conectar</button>
        </article>
    `).join("");

    container.querySelectorAll(".connect-btn").forEach((btn) => {
        btn.addEventListener("click", async() => {
            const platform = btn.dataset.platform;
            try {
                await apiFetch("/api/integrations/connect", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ platform }),
                });
                btn.textContent = "Conectado";
                btn.disabled = true;
                setFeedback(`${platform} conectado com sucesso.`);
            } catch (err) {
                setFeedback(`Falha ao conectar ${platform}: ${err.message}`);
            }
        });
    });
}

function renderArchivedChats() {
    const list = document.getElementById("archivedList");
    if (!list) {
        return;
    }

    const items = [
        "Atendimento Cliente",
        "Restaurante Bot",
        "Suporte Loja",
    ];

    list.innerHTML = items.map((item) => `<li>${item}</li>`).join("");
}

async function bindEvents() {
    document.querySelectorAll(".menu-item").forEach((item) => {
        item.addEventListener("click", () => switchTab(item.dataset.tab));
    });

    document.getElementById("saveProfileBtn").addEventListener("click", async() => {
        try {
            await saveProfile();
        } catch (err) {
            setFeedback(`Erro ao salvar perfil: ${err.message}`);
        }
    });

    document.getElementById("avatarUpload").addEventListener("change", async(event) => {
        const file = event.target.files && event.target.files[0];
        try {
            await uploadAvatar(file);
        } catch (err) {
            setFeedback(`Erro no avatar: ${err.message}`);
        }
    });

    document.getElementById("saveThemeBtn").addEventListener("click", async() => {
        try {
            await saveThemeAndLanguage();
        } catch (err) {
            setFeedback(`Erro ao salvar personalizacao: ${err.message}`);
        }
    });

    document.getElementById("saveNotifBtn").addEventListener("click", async() => {
        try {
            await saveNotifications();
        } catch (err) {
            setFeedback(`Erro ao salvar notificacoes: ${err.message}`);
        }
    });

    document.getElementById("saveAiBtn").addEventListener("click", async() => {
        try {
            await saveAISettings();
        } catch (err) {
            setFeedback(`Erro ao salvar IA: ${err.message}`);
        }
    });

    document.getElementById("upgradePlanBtn").addEventListener("click", async() => {
        try {
            await startUpgradeCheckout();
        } catch (err) {
            setFeedback(`Erro ao iniciar upgrade: ${err.message}`);
        }
    });

    document.getElementById("saveSecurityBtn").addEventListener("click", async() => {
        try {
            await saveSecurity();
        } catch (err) {
            setFeedback(`Erro de seguranca: ${err.message}`);
        }
    });

    document.getElementById("clearHistoryBtn").addEventListener("click", () => {
        setFeedback("Historico limpo (placeholder).", "dataFeedback");
    });

    document.getElementById("exportDataBtn").addEventListener("click", async() => {
        try {
            const data = await apiFetch("/api/data/export", { method: "POST" });
            setFeedback(`Exportacao pronta: ${data.download_url}`, "dataFeedback");
        } catch (err) {
            setFeedback(`Erro ao exportar: ${err.message}`, "dataFeedback");
        }
    });

    document.getElementById("deleteDataBtn").addEventListener("click", async() => {
        const confirmed = window.confirm("Tem certeza que deseja excluir os dados de configuracao?");
        if (!confirmed) {
            return;
        }

        try {
            await apiFetch("/api/data/delete", { method: "DELETE" });
            setFeedback("Dados de configuracao resetados.", "dataFeedback");
            await bootstrap();
        } catch (err) {
            setFeedback(`Erro ao excluir: ${err.message}`, "dataFeedback");
        }
    });
}

async function bootstrap() {
    try {
        await loadProfile();
        await loadThemeAndLanguage();
        await loadNotifications();
        await loadAISettings();
    } catch (err) {
        setFeedback(`Falha ao carregar configuracoes: ${err.message}`);
    }

    renderIntegrationCards();
    renderArchivedChats();
}

document.addEventListener("DOMContentLoaded", async() => {
    await bindEvents();
    await bootstrap();

    const params = new URLSearchParams(window.location.search);
    const tab = params.get("tab") || "account";
    switchTab(tab);
});