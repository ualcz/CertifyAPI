/**
 * Módulo de Autenticação
 * Gerencia login de admin, registro e login de estudantes
 */

const AuthModule = {
    /**
     * Inicializa o módulo
     */
    init() {
        this.setupEventListeners();
        this.renderAuthForms();
    },

    /**
     * Renderiza os formulários de autenticação
     */
    renderAuthForms() {
        const container = document.getElementById('auth-content');
        if (!container) return;

        container.innerHTML = `
            <div class="auth-container">
                <div class="auth-tabs">
                    <button class="auth-tab active" data-tab="admin-login">Login Admin</button>
                    <button class="auth-tab" data-tab="student-login">Login Estudante</button>
                    <button class="auth-tab" data-tab="student-register">Registrar Estudante</button>
                </div>
                
                <div class="auth-forms">
                    <!-- Admin Login -->
                    <div class="auth-form-container active" id="admin-login-form">
                        <h3>Login de Administrador</h3>
                        <form id="form-admin-login">
                            <div class="form-field">
                                <label for="admin-email">Email</label>
                                <input type="email" id="admin-email" name="username" required 
                                       placeholder="admin@example.com" class="form-control">
                            </div>
                            <div class="form-field">
                                <label for="admin-password">Senha</label>
                                <input type="password" id="admin-password" name="password" required 
                                       placeholder="••••••••" class="form-control">
                            </div>
                            <button type="submit" class="btn btn-primary btn-block">
                                Entrar como Admin
                            </button>
                        </form>
                        <p class="form-hint">Credenciais padrão: admin@example.com / admin123</p>
                    </div>
                    
                    <!-- Student Login -->
                    <div class="auth-form-container" id="student-login-form">
                        <h3>Login de Estudante</h3>
                        <form id="form-student-login">
                            <div class="form-field">
                                <label for="student-login-email">Email</label>
                                <input type="email" id="student-login-email" name="email" required 
                                       placeholder="seu@email.com" class="form-control">
                            </div>
                            <div class="form-field">
                                <label for="student-login-password">Senha</label>
                                <input type="password" id="student-login-password" name="password" required 
                                       placeholder="••••••••" class="form-control">
                            </div>
                            <button type="submit" class="btn btn-primary btn-block">
                                Entrar como Estudante
                            </button>
                        </form>
                    </div>
                    
                    <!-- Student Register -->
                    <div class="auth-form-container" id="student-register-form">
                        <h3>Registrar Conta de Estudante</h3>
                        <form id="form-student-register">
                            <div class="form-field">
                                <label for="student-name">Nome Completo</label>
                                <input type="text" id="student-name" name="name" required 
                                       placeholder="João Silva" class="form-control">
                            </div>
                            <div class="form-field">
                                <label for="student-email">Email</label>
                                <input type="email" id="student-email" name="email" required 
                                       placeholder="joao@example.com" class="form-control">
                            </div>
                            <div class="form-field">
                                <label for="student-cpf">CPF (apenas números)</label>
                                <input type="text" id="student-cpf" name="cpf" required 
                                       placeholder="12345678900" pattern="[0-9]{11}" class="form-control">
                            </div>
                            <div class="form-field">
                                <label for="student-password">Senha</label>
                                <input type="password" id="student-password" name="password" required 
                                       placeholder="••••••••" minlength="6" class="form-control">
                            </div>
                            <button type="submit" class="btn btn-primary btn-block">
                                Criar Conta
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        `;

        this.setupTabSwitching();
    },

    /**
     * Configura troca de abas
     */
    setupTabSwitching() {
        const tabs = document.querySelectorAll('.auth-tab');
        const forms = document.querySelectorAll('.auth-form-container');

        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetId = tab.dataset.tab + '-form';

                // Atualizar tabs
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                // Atualizar forms
                forms.forEach(f => f.classList.remove('active'));
                document.getElementById(targetId)?.classList.add('active');
            });
        });
    },

    /**
     * Configura event listeners
     */
    setupEventListeners() {
        // Admin Login
        document.addEventListener('submit', async (e) => {
            if (e.target.id === 'form-admin-login') {
                e.preventDefault();
                await this.handleAdminLogin(e.target);
            }
        });

        // Student Login
        document.addEventListener('submit', async (e) => {
            if (e.target.id === 'form-student-login') {
                e.preventDefault();
                await this.handleStudentLogin(e.target);
            }
        });

        // Student Register
        document.addEventListener('submit', async (e) => {
            if (e.target.id === 'form-student-register') {
                e.preventDefault();
                await this.handleStudentRegister(e.target);
            }
        });
    },

    /**
     * Processa login de admin
     */
    async handleAdminLogin(form) {
        const formData = new FormData(form);

        try {
            const response = await ApiClient.postForm(
                API_CONFIG.ENDPOINTS.AUTH.ADMIN_LOGIN,
                formData
            );

            // Armazenar token
            AuthManager.setToken(response.access_token, 'admin');

            // Mostrar sucesso
            Notifications.success(API_CONFIG.MESSAGES.SUCCESS.LOGIN);

            // Limpar formulário
            form.reset();

            // Redirecionar
            setTimeout(() => {
                window.location.href = '/static/admin.html';
            }, 1000);

        } catch (error) {
            console.error('Admin login error:', error);
        }
    },

    /**
     * Processa login de estudante
     */
    async handleStudentLogin(form) {
        const formData = new FormData(form);
        const data = {
            email: formData.get('email'),
            password: formData.get('password')
        };

        try {
            const response = await ApiClient.post(API_CONFIG.ENDPOINTS.AUTH.STUDENT_LOGIN, data);
            AuthManager.setToken(response.access_token, 'student');

            Notifications.success(API_CONFIG.MESSAGES.SUCCESS.LOGIN);

            // Redirecionar
            setTimeout(() => {
                window.location.href = '/static/student.html';
            }, 1000);

        } catch (error) {
            console.error('Login error:', error);
        }
    },

    /**
     * Processa registro de estudante
     */
    async handleStudentRegister(form) {
        const formData = new FormData(form);
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            cpf: formData.get('cpf'),
            password: formData.get('password'),
        };

        try {
            await ApiClient.post(
                API_CONFIG.ENDPOINTS.AUTH.STUDENT_REGISTER,
                data
            );

            // Mostrar sucesso
            Notifications.success('Conta criada com sucesso! Faça login para continuar.');

            // Limpar formulário
            form.reset();

            // Mudar para aba de login
            setTimeout(() => {
                document.querySelector('[data-tab="student-login"]')?.click();
            }, 1500);

        } catch (error) {
            console.error('Student register error:', error);
        }
    },
};

// Exportar para uso global
window.AuthModule = AuthModule;
