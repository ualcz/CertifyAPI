/**
 * Módulo de Inscrições
 * Gerencia inscrições de estudantes em turmas
 */

const EnrollmentsModule = {
    async init() {
        this.render();
        if (AuthManager.isStudent()) {
            await this.loadAvailableClasses();
        }
        this.setupEventListeners();
    },

    async loadAvailableClasses() {
        try {
            const classes = await ApiClient.get(API_CONFIG.ENDPOINTS.ENROLLMENTS.AVAILABLE);
            this.renderAvailableClasses(classes);
        } catch (error) {
            console.error('Error loading classes:', error);
        }
    },

    render() {
        const container = document.getElementById('enrollments-content');
        if (!container) return;

        container.innerHTML = `
            <div class="module-header">
                <h2>Inscrições em Turmas</h2>
            </div>
            
            <div data-require-student>
                <div class="card">
                    <div class="card-header"><h3>Turmas Disponíveis</h3></div>
                    <div class="card-body" id="available-classes-list">
                        <p class="text-muted">Carregando...</p>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-header"><h3>Minhas Inscrições</h3></div>
                    <div class="card-body" id="my-enrollments-list">
                        <button class="btn btn-secondary" onclick="EnrollmentsModule.loadMyEnrollments()">
                            Carregar Minhas Inscrições
                        </button>
                    </div>
                </div>
            </div>
            
            <div data-guest-only>
                <p class="alert alert-info">Faça login como estudante para se inscrever em turmas.</p>
            </div>
        `;

        AuthManager.updatePermissionBasedUI();
    },

    renderAvailableClasses(classes) {
        const container = document.getElementById('available-classes-list');
        if (!container) return;

        if (classes.length === 0) {
            container.innerHTML = '<p class="text-muted">Nenhuma turma disponível no momento.</p>';
            return;
        }

        container.innerHTML = classes.map(cls => `
            <div class="class-card">
                <h4>${cls.course_name} - ${cls.name}</h4>
                <p>Vagas: ${cls.available_slots}/${cls.total_slots}</p>
                <button class="btn btn-primary btn-sm" onclick="EnrollmentsModule.enroll(${cls.id})">
                    Inscrever-se
                </button>
            </div>
        `).join('');
    },

    async enroll(classId) {
        try {
            await ApiClient.post(API_CONFIG.ENDPOINTS.ENROLLMENTS.ENROLL(classId));
            Notifications.success('Inscrição realizada com sucesso!');
            await this.loadAvailableClasses();
        } catch (error) {
            console.error('Error enrolling:', error);
        }
    },

    async loadMyEnrollments() {
        try {
            const enrollments = await ApiClient.get(API_CONFIG.ENDPOINTS.ENROLLMENTS.MY_ENROLLMENTS);
            const container = document.getElementById('my-enrollments-list');

            if (enrollments.length === 0) {
                container.innerHTML = '<p class="text-muted">Você não está inscrito em nenhuma turma.</p>';
                return;
            }

            container.innerHTML = enrollments.map(enroll => `
                <div class="enrollment-card">
                    <h4>${enroll.course_name} - ${enroll.class_name}</h4>
                    <p>Inscrito em: ${UI.formatDate(enroll.enrollment_date)}</p>
                    ${enroll.is_open ? `
                        <button class="btn btn-danger btn-sm" onclick="EnrollmentsModule.cancel(${enroll.enrollment_id})">
                            Cancelar Inscrição
                        </button>
                    ` : '<span class="badge badge-secondary">Turma fechada</span>'}
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading enrollments:', error);
        }
    },

    async cancel(enrollmentId) {
        if (!confirm('Deseja realmente cancelar esta inscrição?')) return;

        try {
            await ApiClient.delete(API_CONFIG.ENDPOINTS.ENROLLMENTS.CANCEL(enrollmentId));
            Notifications.success('Inscrição cancelada com sucesso!');
            await this.loadMyEnrollments();
            await this.loadAvailableClasses();
        } catch (error) {
            console.error('Error canceling enrollment:', error);
        }
    },

    setupEventListeners() {
        // Event listeners já configurados via onclick nos botões
    },
};

window.EnrollmentsModule = EnrollmentsModule;
