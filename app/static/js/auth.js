/**
 * Gerenciamento de Autenticação
 * Responsável por armazenar, verificar e gerenciar tokens de autenticação
 */

const AuthManager = {
    /**
     * Armazena o token de autenticação
     */
    setToken(token, userType = 'admin') {
        localStorage.setItem(API_CONFIG.SETTINGS.TOKEN_KEY, token);
        localStorage.setItem(API_CONFIG.SETTINGS.USER_TYPE_KEY, userType);
        localStorage.setItem('token_timestamp', Date.now().toString());
    },

    /**
     * Obtém o token armazenado
     */
    getToken() {
        return localStorage.getItem(API_CONFIG.SETTINGS.TOKEN_KEY);
    },

    /**
     * Obtém o tipo de usuário
     */
    getUserType() {
        return localStorage.getItem(API_CONFIG.SETTINGS.USER_TYPE_KEY) || null;
    },

    /**
     * Verifica se o usuário está autenticado
     */
    isAuthenticated() {
        const token = this.getToken();
        if (!token) return false;

        // Verificar se o token expirou
        const timestamp = localStorage.getItem('token_timestamp');
        if (timestamp) {
            const elapsed = Date.now() - parseInt(timestamp);
            const expiryMs = API_CONFIG.SETTINGS.TOKEN_EXPIRY_MINUTES * 60 * 1000;

            if (elapsed > expiryMs) {
                this.logout();
                return false;
            }
        }

        return true;
    },

    /**
     * Verifica se o usuário é admin
     */
    isAdmin() {
        return this.isAuthenticated() && this.getUserType() === 'admin';
    },

    /**
     * Verifica se o usuário é estudante
     */
    isStudent() {
        return this.isAuthenticated() && this.getUserType() === 'student';
    },

    /**
     * Remove o token (logout)
     */
    logout() {
        localStorage.removeItem(API_CONFIG.SETTINGS.TOKEN_KEY);
        localStorage.removeItem(API_CONFIG.SETTINGS.USER_TYPE_KEY);
        localStorage.removeItem('token_timestamp');

        // Atualizar UI
        this.updateAuthUI();

        // Mostrar notificação
        if (window.Notifications) {
            Notifications.success(API_CONFIG.MESSAGES.SUCCESS.LOGOUT);
        }
    },

    /**
     * Atualiza a interface de autenticação
     */
    updateAuthUI() {
        const authStatus = document.getElementById('auth-status');
        const loginSection = document.getElementById('login-section');
        const logoutBtn = document.getElementById('logout-btn');

        if (!authStatus) return;

        if (this.isAuthenticated()) {
            const userType = this.getUserType();
            const userTypeLabel = userType === 'admin' ? 'Administrador' : 'Estudante';

            authStatus.innerHTML = `
                <span class="auth-badge auth-badge-${userType}">
                    <i class="icon-user"></i>
                    ${userTypeLabel}
                </span>
            `;

            if (loginSection) loginSection.style.display = 'none';
            if (logoutBtn) logoutBtn.style.display = 'inline-block';
        } else {
            authStatus.innerHTML = `
                <span class="auth-badge auth-badge-guest">
                    <i class="icon-user"></i>
                    Visitante
                </span>
            `;

            if (loginSection) loginSection.style.display = 'block';
            if (logoutBtn) logoutBtn.style.display = 'none';
        }

        // Atualizar visibilidade de elementos baseados em permissões
        this.updatePermissionBasedUI();
    },

    /**
     * Atualiza elementos da UI baseados em permissões
     */
    updatePermissionBasedUI() {
        // Elementos que requerem autenticação de admin
        const adminElements = document.querySelectorAll('[data-require-admin]');
        adminElements.forEach(el => {
            el.style.display = this.isAdmin() ? '' : 'none';
        });

        // Elementos que requerem autenticação de estudante
        const studentElements = document.querySelectorAll('[data-require-student]');
        studentElements.forEach(el => {
            el.style.display = this.isStudent() ? '' : 'none';
        });

        // Elementos que requerem qualquer autenticação
        const authElements = document.querySelectorAll('[data-require-auth]');
        authElements.forEach(el => {
            el.style.display = this.isAuthenticated() ? '' : 'none';
        });

        // Elementos visíveis apenas para visitantes
        const guestElements = document.querySelectorAll('[data-guest-only]');
        guestElements.forEach(el => {
            el.style.display = !this.isAuthenticated() ? '' : 'none';
        });
    },

    /**
     * Inicializa o gerenciador de autenticação
     */
    init() {
        // Atualizar UI inicial
        this.updateAuthUI();

        // Configurar botão de logout
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }

        // Verificar token periodicamente (a cada minuto)
        setInterval(() => {
            if (this.isAuthenticated()) {
                // Token ainda válido, atualizar timestamp
                localStorage.setItem('token_timestamp', Date.now().toString());
            }
        }, 60000);
    },
};

// Exportar para uso global
window.AuthManager = AuthManager;

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => AuthManager.init());
} else {
    AuthManager.init();
}
