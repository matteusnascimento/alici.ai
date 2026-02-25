/**
 * ALICI™ Login JavaScript
 * Sistema de autenticação com validação e API integration
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos do DOM
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    // ========================================================================
    // SISTEMA DE ABAS (TABS)
    // ========================================================================

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');

            // Remove active de todos os botões e conteúdos
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Adiciona active ao selecionado
            this.classList.add('active');
            document.querySelector(`.tab-content[data-tab="${tabName}"]`).classList.add('active');
        });
    });

    // ========================================================================
    // FORMULÁRIO DE LOGIN
    // ========================================================================

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const email = document.getElementById('login-email').value.trim();
        const password = document.getElementById('login-password').value;
        const msgDiv = document.getElementById('login-msg');
        const submitBtn = loginForm.querySelector('.submit-btn');

        // Validação básica
        if (!email || !password) {
            showMessage(msgDiv, 'Por favor, preencha todos os campos', 'error');
            return;
        }

        if (!isValidEmail(email)) {
            showMessage(msgDiv, 'Email inválido', 'error');
            return;
        }

        try {
            // Mostrar loading
            showMessage(msgDiv, 'Autenticando...', 'loading');
            submitBtn.disabled = true;

            // Fazer requisição de login
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    senha: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Sucesso
                showMessage(msgDiv, '✓ Login realizado! Redirecionando...', 'success');
                
                // Armazenar token
                localStorage.setItem('access_token', data.access_token);
                
                // Redirecionar após 1 segundo
                setTimeout(() => {
                    window.location.href = '/chat';
                }, 1000);
            } else {
                // Erro
                const errorMsg = data.message || data.detail || 'Erro ao fazer login. Tente novamente.';
                showMessage(msgDiv, errorMsg, 'error');
                submitBtn.disabled = false;
            }
        } catch (error) {
            console.error('Erro:', error);
            showMessage(msgDiv, 'Erro de conexão. Verifique sua internet.', 'error');
            submitBtn.disabled = false;
        }
    });

    // ========================================================================
    // FORMULÁRIO DE CADASTRO
    // ========================================================================

    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const nome = document.getElementById('register-name').value.trim();
        const email = document.getElementById('register-email').value.trim();
        const password = document.getElementById('register-password').value;
        const confirm = document.getElementById('register-confirm').value;
        const msgDiv = document.getElementById('register-msg');
        const submitBtn = registerForm.querySelector('.submit-btn');

        // Validação
        if (!nome || !email || !password || !confirm) {
            showMessage(msgDiv, 'Por favor, preencha todos os campos', 'error');
            return;
        }

        if (!isValidEmail(email)) {
            showMessage(msgDiv, 'Email inválido', 'error');
            return;
        }

        if (password.length < 8) {
            showMessage(msgDiv, 'Senha deve ter pelo menos 8 caracteres', 'error');
            return;
        }

        const passwordBytes = new TextEncoder().encode(password).length;
        if (passwordBytes > 72) {
            showMessage(msgDiv, 'Senha muito longa (max 72 bytes)', 'error');
            return;
        }

        if (password !== confirm) {
            showMessage(msgDiv, 'As senhas não conferem', 'error');
            return;
        }

        try {
            // Mostrar loading
            showMessage(msgDiv, 'Criando conta...', 'loading');
            submitBtn.disabled = true;

            // Fazer requisição de registro
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    nome: nome,
                    email: email,
                    senha: password
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Sucesso
                showMessage(msgDiv, '✓ Conta criada! Redirecionando para login...', 'success');
                
                // Limpar formulário
                registerForm.reset();
                
                // Mudar para aba de login após 1.5 segundo
                setTimeout(() => {
                    document.querySelector('[data-tab="login"]').click();
                    // Preencher email
                    document.getElementById('login-email').value = email;
                    document.getElementById('login-email').focus();
                }, 1500);
                
                submitBtn.disabled = false;
            } else {
                // Erro
                const errorMsg = data.message || data.detail || 'Erro ao criar conta. Email pode estar em uso.';
                showMessage(msgDiv, errorMsg, 'error');
                submitBtn.disabled = false;
            }
        } catch (error) {
            console.error('Erro:', error);
            showMessage(msgDiv, 'Erro de conexão. Verifique sua internet.', 'error');
            submitBtn.disabled = false;
        }
    });
});

// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

/**
 * Validar email
 */
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Mostrar mensagem (erro/sucesso/loading)
 */
function showMessage(element, message, type) {
    element.textContent = message;
    element.classList.remove('error', 'success', 'loading');
    element.classList.add(type, 'show');
}

/**
 * Limpar mensagem
 */
function clearMessage(element) {
    element.textContent = '';
    element.classList.remove('show', 'error', 'success', 'loading');
}

/**
 * Hash da senha no cliente (opcional, complementar ao servidor)
 */
function hashPassword(password) {
    // NOTA: Isso é apenas para exemplo. 
    // A criptografia REAL deve ser feita no SERVIDOR (bcrypt)
    // Use isto apenas como camada adicional de segurança no trânsito
    return btoa(password); // Base64 encoding apenas
}

/**
 * Verificar token JWT
 */
function getToken() {
    return localStorage.getItem('access_token');
}

/**
 * Remover token (logout)
 */
function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/';
}

// ============================================================================
// EVENT LISTENERS GLOBAIS
// ============================================================================

// Enter no input dispara submit
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && this.form) {
            this.form.dispatchEvent(new Event('submit'));
        }
    });
});
