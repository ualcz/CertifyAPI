/**
 * Módulo de Cursos
 * Gerencia listagem e criação de cursos
 */

const CoursesModule = {
    courses: [],

    /**
     * Inicializa o módulo
     */
    async init() {
        await this.loadCourses();
        this.render();
        this.setupEventListeners();
    },

    /**
     * Carrega cursos da API
     */
    async loadCourses() {
        try {
            this.courses = await ApiClient.get(API_CONFIG.ENDPOINTS.COURSES.WITH_CLASSES);
        } catch (error) {
            console.error('Error loading courses:', error);
            this.courses = [];
        }
    },

    /**
     * Renderiza o módulo
     */
    render() {
        const container = document.getElementById('courses-content');
        if (!container) return;

        container.innerHTML = `
            <div class="module-header">
                <h2>Gerenciamento de Cursos</h2>
                <button class="btn btn-primary" id="btn-create-course" data-require-admin>
                    + Criar Novo Curso
                </button>
            </div>
            
            <div class="courses-grid" id="courses-grid">
                ${this.renderCoursesList()}
            </div>
        `;

        // Atualizar permissões
        AuthManager.updatePermissionBasedUI();
    },

    /**
     * Renderiza lista de cursos
     */
    renderCoursesList() {
        if (this.courses.length === 0) {
            return '<p class="empty-state">Nenhum curso cadastrado ainda.</p>';
        }

        return this.courses.map(course => `
            <div class="course-card card">
                <div class="card-header">
                    <h3>${course.name}</h3>
                    <div class="card-actions">
                        <button class="btn btn-sm btn-secondary" onclick="CoursesModule.showEditCourseModal(${course.id})">✏️</button>
                        <button class="btn btn-sm btn-danger" onclick="CoursesModule.handleDeleteCourse(${course.id})">🗑️</button>
                    </div>
                </div>
                <div class="card-body">
                    <p>${course.description || 'Sem descrição'}</p>
                    <div class="course-info">
                        <span><strong>Carga Horária:</strong> ${course.workload}h</span>
                        <span><strong>Turmas:</strong> ${course.total_classes || 0}</span>
                    </div>
                    ${this.renderClassesList(course.classes || [])}
                </div>
            </div>
        `).join('');
    },

    /**
     * Renderiza lista de turmas de um curso
     */
    renderClassesList(classes) {
        if (!classes || classes.length === 0) {
            return '<p class="text-muted small">Nenhuma turma criada</p>';
        }

        return `
            <div class="classes-list">
                <h4>Turmas:</h4>
                ${classes.map(cls => `
                    <div class="class-item">
                        <span class="class-name">${cls.name}</span>
                        <span class="class-status ${cls.is_open ? 'open' : 'closed'}">
                            ${cls.is_open ? 'Aberta' : 'Fechada'}
                        </span>
                        <span class="class-slots">
                            ${cls.available_slots}/${cls.total_slots} vagas
                        </span>
                    </div>
                `).join('')}
            </div>
        `;
    },

    /**
     * Configura event listeners
     */
    setupEventListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.id === 'btn-create-course') {
                this.showCreateCourseModal();
            }
        });
    },

    showCreateCourseModal() {
        const formHtml = `
            <form id="form-create-course">
                <div class="form-field">
                    <label for="course-name">Nome do Curso *</label>
                    <input type="text" id="course-name" name="name" required class="form-control"
                           placeholder="Ex: Python Avançado">
                </div>
                <div class="form-field">
                    <label for="course-description">Descrição</label>
                    <textarea id="course-description" name="description" class="form-control"
                              placeholder="Descrição do curso" rows="3"></textarea>
                </div>
                <div class="form-field">
                    <label for="course-workload">Carga Horária (horas) *</label>
                    <input type="number" id="course-workload" name="workload" required class="form-control"
                           placeholder="40" min="1">
                </div>
            </form>
        `;

        const footer = `
            <button class="btn btn-secondary" onclick="UI.closeModal(this.closest('.modal-overlay'))">
                Cancelar
            </button>
            <button class="btn btn-primary" onclick="CoursesModule.handleCreateCourse()">
                Criar Curso
            </button>
        `;

        const modal = UI.createModal('Criar Novo Curso', formHtml, { footer });
        UI.showModal(modal);
    },

    /**
     * Processa criação de curso
     */
    async handleCreateCourse() {
        const form = document.getElementById('form-create-course');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const formData = new FormData(form);
        const data = {
            name: formData.get('name'),
            description: formData.get('description'),
            workload: parseFloat(formData.get('workload')),
        };

        try {
            await ApiClient.post(API_CONFIG.ENDPOINTS.COURSES.CREATE, data);

            Notifications.success(API_CONFIG.MESSAGES.SUCCESS.CREATED);

            // Fechar modal
            const modal = document.querySelector('.modal-overlay');
            if (modal) UI.closeModal(modal);

            // Recarregar cursos
            await this.loadCourses();
            this.render();

        } catch (error) {
            console.error('Error creating course:', error);
        }
    },

    showEditCourseModal(courseId) {
        const course = this.courses.find(c => c.id === courseId);
        if (!course) return;

        const formHtml = `
            <form id="form-edit-course">
                <input type="hidden" name="id" value="${course.id}">
                <div class="form-field">
                    <label for="edit-course-name">Nome do Curso *</label>
                    <input type="text" id="edit-course-name" name="name" value="${course.name}" required class="form-control">
                </div>
                <div class="form-field">
                    <label for="edit-course-description">Descrição</label>
                    <textarea id="edit-course-description" name="description" class="form-control" rows="3">${course.description || ''}</textarea>
                </div>
                <div class="form-field">
                    <label for="edit-course-workload">Carga Horária (horas) *</label>
                    <input type="number" id="edit-course-workload" name="workload" value="${course.workload}" required class="form-control" min="1">
                </div>
            </form>
        `;

        const footer = `
            <button class="btn btn-secondary" onclick="UI.closeModal(this.closest('.modal-overlay'))">Cancelar</button>
            <button class="btn btn-primary" onclick="CoursesModule.handleUpdateCourse(${course.id})">Salvar Alterações</button>
        `;

        const modal = UI.createModal('Editar Curso', formHtml, { footer });
        UI.showModal(modal);
    },

    async handleUpdateCourse(courseId) {
        const form = document.getElementById('form-edit-course');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const formData = new FormData(form);
        const data = {
            name: formData.get('name'),
            description: formData.get('description'),
            workload: parseFloat(formData.get('workload')),
        };

        try {
            await ApiClient.put(API_CONFIG.ENDPOINTS.COURSES.UPDATE(courseId), data);
            Notifications.success('Curso atualizado com sucesso!');

            const modal = document.querySelector('.modal-overlay');
            if (modal) UI.closeModal(modal);

            await this.loadCourses();
            this.render();
        } catch (error) {
            console.error('Error updating course:', error);
        }
    },

    async handleDeleteCourse(courseId) {
        if (!confirm('Tem certeza que deseja excluir este curso? As turmas e certificados associados não serão perdidos, mas o curso não aparecerá mais na lista.')) {
            return;
        }

        try {
            await ApiClient.delete(API_CONFIG.ENDPOINTS.COURSES.DELETE(courseId));
            Notifications.success('Curso excluído com sucesso!');
            await this.loadCourses();
            this.render();
        } catch (error) {
            console.error('Error deleting course:', error);
            Notifications.error('Erro ao excluir curso.');
        }
    }
};

// Exportar para uso global
window.CoursesModule = CoursesModule;
