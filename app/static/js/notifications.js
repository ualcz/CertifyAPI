/**
 * Sistema de Notificações Toast
 * Exibe mensagens de sucesso, erro, info e warning
 */

const Notifications = {
    container: null,
    queue: [],

    /**
     * Inicializa o sistema de notificações
     */
    init() {
        // Criar container se não existir
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'notifications-container';
            this.container.className = 'notifications-container';
            document.body.appendChild(this.container);
        }
    },

    /**
     * Mostra uma notificação
     */
    show(message, type = 'info', duration = 5000) {
        this.init();

        // Criar elemento da notificação
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;

        // Ícone baseado no tipo
        const icons = {
            success: '✓',
            error: '✗',
            warning: '⚠',
            info: 'ℹ',
        };

        notification.innerHTML = `
            <span class="notification-icon">${icons[type] || icons.info}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close" aria-label="Fechar">×</button>
        `;

        // Adicionar ao container
        this.container.appendChild(notification);

        // Animar entrada
        setTimeout(() => {
            notification.classList.add('notification-show');
        }, 10);

        // Configurar botão de fechar
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            this.hide(notification);
        });

        // Auto-dismiss
        if (duration > 0) {
            setTimeout(() => {
                this.hide(notification);
            }, duration);
        }

        return notification;
    },

    /**
     * Esconde uma notificação
     */
    hide(notification) {
        notification.classList.remove('notification-show');
        notification.classList.add('notification-hide');

        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    },

    /**
     * Notificação de sucesso
     */
    success(message, duration = 5000) {
        return this.show(message, 'success', duration);
    },

    /**
     * Notificação de erro
     */
    error(message, duration = 7000) {
        return this.show(message, 'error', duration);
    },

    /**
     * Notificação de aviso
     */
    warning(message, duration = 6000) {
        return this.show(message, 'warning', duration);
    },

    /**
     * Notificação de informação
     */
    info(message, duration = 5000) {
        return this.show(message, 'info', duration);
    },

    /**
     * Limpa todas as notificações
     */
    clearAll() {
        if (this.container) {
            const notifications = this.container.querySelectorAll('.notification');
            notifications.forEach(n => this.hide(n));
        }
    },
};

// Exportar para uso global
window.Notifications = Notifications;

// Inicializar quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Notifications.init());
} else {
    Notifications.init();
}
