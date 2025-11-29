/**
 * Componentes UI Reutilizáveis
 * Fornece funções para criar elementos comuns da interface
 */

const UI = {
    loadingOverlay: null,

    /**
     * Cria um card
     */
    createCard(title, content, footer = null, className = '') {
        const card = document.createElement('div');
        card.className = `card ${className}`;

        let html = '';

        if (title) {
            html += `<div class="card-header"><h3>${title}</h3></div>`;
        }

        html += `<div class="card-body">${content}</div>`;

        if (footer) {
            html += `<div class="card-footer">${footer}</div>`;
        }

        card.innerHTML = html;
        return card;
    },

    /**
     * Cria um botão
     */
    createButton(text, onClick, options = {}) {
        const {
            type = 'primary',
            icon = null,
            disabled = false,
            className = '',
        } = options;

        const button = document.createElement('button');
        button.className = `btn btn-${type} ${className}`;
        button.disabled = disabled;

        let html = '';
        if (icon) {
            html += `<i class="${icon}"></i> `;
        }
        html += text;

        button.innerHTML = html;

        if (onClick) {
            button.addEventListener('click', onClick);
        }

        return button;
    },

    /**
     * Cria um campo de formulário
     */
    createFormField(label, type, name, options = {}) {
        const {
            placeholder = '',
            required = false,
            value = '',
            className = '',
        } = options;

        const field = document.createElement('div');
        field.className = `form-field ${className}`;

        let html = `<label for="${name}">${label}${required ? ' *' : ''}</label>`;

        if (type === 'textarea') {
            html += `<textarea 
                id="${name}" 
                name="${name}" 
                placeholder="${placeholder}"
                ${required ? 'required' : ''}
                class="form-control"
            >${value}</textarea>`;
        } else if (type === 'select') {
            const selectOptions = options.options || [];
            html += `<select 
                id="${name}" 
                name="${name}" 
                ${required ? 'required' : ''}
                class="form-control"
            >`;
            selectOptions.forEach(opt => {
                const selected = opt.value === value ? 'selected' : '';
                html += `<option value="${opt.value}" ${selected}>${opt.label}</option>`;
            });
            html += `</select>`;
        } else {
            html += `<input 
                type="${type}" 
                id="${name}" 
                name="${name}" 
                placeholder="${placeholder}"
                value="${value}"
                ${required ? 'required' : ''}
                class="form-control"
            />`;
        }

        field.innerHTML = html;
        return field;
    },

    /**
     * Cria uma tabela
     */
    createTable(headers, rows, options = {}) {
        const {
            className = '',
            emptyMessage = 'Nenhum registro encontrado',
        } = options;

        const table = document.createElement('table');
        table.className = `table ${className}`;

        // Cabeçalho
        let html = '<thead><tr>';
        headers.forEach(header => {
            html += `<th>${header}</th>`;
        });
        html += '</tr></thead>';

        // Corpo
        html += '<tbody>';
        if (rows.length === 0) {
            html += `<tr><td colspan="${headers.length}" class="text-center">${emptyMessage}</td></tr>`;
        } else {
            rows.forEach(row => {
                html += '<tr>';
                row.forEach(cell => {
                    html += `<td>${cell}</td>`;
                });
                html += '</tr>';
            });
        }
        html += '</tbody>';

        table.innerHTML = html;
        return table;
    },

    /**
     * Cria um modal
     */
    createModal(title, content, options = {}) {
        const {
            size = 'medium',
            onClose = null,
            footer = null,
        } = options;

        const modal = document.createElement('div');
        modal.className = 'modal-overlay';

        let html = `
            <div class="modal modal-${size}">
                <div class="modal-header">
                    <h3>${title}</h3>
                    <button class="modal-close" aria-label="Fechar">×</button>
                </div>
                <div class="modal-body">${content}</div>
        `;

        if (footer) {
            html += `<div class="modal-footer">${footer}</div>`;
        }

        html += '</div>';
        modal.innerHTML = html;

        // Configurar botão de fechar
        const closeBtn = modal.querySelector('.modal-close');
        closeBtn.addEventListener('click', () => {
            this.closeModal(modal);
            if (onClose) onClose();
        });

        // Fechar ao clicar fora
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal(modal);
                if (onClose) onClose();
            }
        });

        return modal;
    },

    /**
     * Mostra um modal
     */
    showModal(modal) {
        document.body.appendChild(modal);
        setTimeout(() => {
            modal.classList.add('modal-show');
        }, 10);
    },

    /**
     * Fecha um modal
     */
    closeModal(modal) {
        modal.classList.remove('modal-show');
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    },

    /**
     * Mostra loading overlay
     */
    showLoading(message = 'Carregando...') {
        if (!this.loadingOverlay) {
            this.loadingOverlay = document.createElement('div');
            this.loadingOverlay.className = 'loading-overlay';
            this.loadingOverlay.innerHTML = `
                <div class="loading-spinner">
                    <div class="spinner"></div>
                    <p class="loading-message">${message}</p>
                </div>
            `;
        }

        document.body.appendChild(this.loadingOverlay);
        setTimeout(() => {
            this.loadingOverlay.classList.add('loading-show');
        }, 10);
    },

    /**
     * Esconde loading overlay
     */
    hideLoading() {
        if (this.loadingOverlay && this.loadingOverlay.parentNode) {
            this.loadingOverlay.classList.remove('loading-show');
            setTimeout(() => {
                if (this.loadingOverlay && this.loadingOverlay.parentNode) {
                    this.loadingOverlay.parentNode.removeChild(this.loadingOverlay);
                }
            }, 300);
        }
    },

    /**
     * Cria um badge
     */
    createBadge(text, type = 'default') {
        const badge = document.createElement('span');
        badge.className = `badge badge-${type}`;
        badge.textContent = text;
        return badge;
    },

    /**
     * Formata data para exibição
     */
    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR');
    },

    /**
     * Formata data e hora para exibição
     */
    formatDateTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('pt-BR');
    },

    /**
     * Limpa um container
     */
    clearContainer(container) {
        if (typeof container === 'string') {
            container = document.getElementById(container);
        }
        if (container) {
            container.innerHTML = '';
        }
    },
};

// Exportar para uso global
window.UI = UI;
