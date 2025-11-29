/**
 * Cliente HTTP centralizado para todas as requisições à API
 * Fornece métodos auxiliares e tratamento de erros padronizado
 */

const ApiClient = {
    /**
     * Realiza uma requisição HTTP genérica
     */
    async request(endpoint, options = {}) {
        const url = API_CONFIG.buildUrl(endpoint);

        // Configurações padrão
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: API_CONFIG.SETTINGS.REQUEST_TIMEOUT,
        };

        // Adicionar token de autenticação se disponível
        const token = AuthManager.getToken();
        if (token && !options.skipAuth) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }

        // Mesclar opções
        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...(options.headers || {}),
            },
        };

        try {
            // Mostrar loading se disponível
            if (window.UI && window.UI.showLoading) {
                UI.showLoading();
            }

            const response = await fetch(url, finalOptions);

            // Esconder loading
            if (window.UI && window.UI.hideLoading) {
                UI.hideLoading();
            }

            // Tratar resposta
            return await this.handleResponse(response);

        } catch (error) {
            // Esconder loading em caso de erro
            if (window.UI && window.UI.hideLoading) {
                UI.hideLoading();
            }

            throw this.handleError(error);
        }
    },

    /**
     * Trata a resposta da API
     */
    async handleResponse(response) {
        // Se for download de arquivo (blob)
        const contentType = response.headers.get('content-type');
        if (contentType && (contentType.includes('application/pdf') || contentType.includes('application/zip'))) {
            if (!response.ok) {
                throw new Error('Erro ao baixar arquivo');
            }
            return await response.blob();
        }

        // Tentar parsear JSON
        let data;
        try {
            const text = await response.text();
            data = text ? JSON.parse(text) : {};
        } catch (e) {
            data = {};
        }

        // Verificar status da resposta
        if (!response.ok) {
            // Tratar erros específicos
            if (response.status === 401) {
                // Token inválido ou expirado
                AuthManager.logout();
                throw new Error(API_CONFIG.MESSAGES.ERROR.UNAUTHORIZED);
            } else if (response.status === 403) {
                throw new Error(API_CONFIG.MESSAGES.ERROR.FORBIDDEN);
            } else if (response.status === 404) {
                throw new Error(data.detail || API_CONFIG.MESSAGES.ERROR.NOT_FOUND);
            } else if (response.status >= 500) {
                throw new Error(API_CONFIG.MESSAGES.ERROR.SERVER);
            } else {
                throw new Error(data.detail || API_CONFIG.MESSAGES.ERROR.VALIDATION);
            }
        }

        return data;
    },

    /**
     * Trata erros da requisição
     */
    handleError(error) {
        console.error('API Error:', error);

        // Erro de rede
        if (error.name === 'TypeError' || error.message.includes('fetch')) {
            const networkError = new Error(API_CONFIG.MESSAGES.ERROR.NETWORK);

            if (window.Notifications) {
                Notifications.error(networkError.message);
            }

            return networkError;
        }

        // Mostrar notificação de erro
        if (window.Notifications) {
            Notifications.error(error.message);
        }

        return error;
    },

    /**
     * Método GET
     */
    async get(endpoint, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'GET',
        });
    },

    /**
     * Método POST
     */
    async post(endpoint, data = null, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'POST',
            body: data ? JSON.stringify(data) : undefined,
        });
    },

    /**
     * Método POST para form data (usado em login OAuth2)
     */
    async postForm(endpoint, formData, options = {}) {
        const url = API_CONFIG.buildUrl(endpoint);

        try {
            if (window.UI && window.UI.showLoading) {
                UI.showLoading();
            }

            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                ...options,
            });

            if (window.UI && window.UI.hideLoading) {
                UI.hideLoading();
            }

            return await this.handleResponse(response);

        } catch (error) {
            if (window.UI && window.UI.hideLoading) {
                UI.hideLoading();
            }
            throw this.handleError(error);
        }
    },

    /**
     * Método PUT
     */
    async put(endpoint, data = null, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'PUT',
            body: data ? JSON.stringify(data) : undefined,
        });
    },

    /**
     * Método DELETE
     */
    async delete(endpoint, options = {}) {
        return this.request(endpoint, {
            ...options,
            method: 'DELETE',
        });
    },

    /**
     * Download de arquivo
     */
    /**
     * Download de arquivo
     */
    async downloadFile(endpoint, filename, options = {}) {
        try {
            const method = options.method || 'GET';
            const body = options.body || null;

            let blob;
            if (method === 'GET') {
                blob = await this.get(endpoint);
            } else {
                blob = await this.request(endpoint, {
                    method: method,
                    body: body ? JSON.stringify(body) : undefined,
                });
            }

            // Criar link temporário para download
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();

            // Limpar
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            if (window.Notifications) {
                Notifications.success('Download iniciado com sucesso!');
            }

        } catch (error) {
            console.error('Download error:', error);
            if (window.Notifications) {
                Notifications.error('Erro ao fazer download do arquivo');
            }
        }
    },
};

// Exportar para uso global
window.ApiClient = ApiClient;
