/**
 * Módulo de Turmas
 * Gerencia criação e administração de turmas
 */

const ClassesModule = {
    courses: [],
    availableTemplates: [],

    async init() {
        await this.loadData();
        this.render();
        this.setupEventListeners();
    },

    async loadData() {
        try {
            // Fetch courses and templates
            const [courses, templates] = await Promise.all([
                ApiClient.get(API_CONFIG.ENDPOINTS.COURSES.WITH_CLASSES),
                ApiClient.get('/classes/templates')
            ]);
            this.courses = courses;
            this.availableTemplates = templates;
        } catch (error) {
            console.error('Error loading data:', error);
        }
    },

    render() {
        const container = document.getElementById('classes-content');
        if (!container) return;

        container.innerHTML = `
            <div class="module-header">
                <h2>Gerenciamento de Turmas</h2>
                <button class="btn btn-primary" id="btn-create-class" data-require-admin>
                    + Criar Nova Turma
                </button>
            </div>
            <div id="classes-list" class="classes-grid">
                ${this.renderClassesList()}
            </div>
        `;

        AuthManager.updatePermissionBasedUI();
    },

    renderClassesList() {
        if (this.courses.length === 0) return '<p>Nenhum curso encontrado.</p>';

        let html = '';
        this.courses.forEach(course => {
            if (course.classes && course.classes.length > 0) {
                html += `
                    <div class="course-section">
                        <h3>${course.name}</h3>
                        <div class="grid-list">
                            ${course.classes.map(cls => `
                                <div class="card class-card">
                                    <div class="card-header">
                                        <h4>${cls.name}</h4>
                                        <span class="badge ${cls.is_open ? 'badge-success' : 'badge-danger'}">
                                            ${cls.is_open ? 'Aberta' : 'Fechada'}
                                        </span>
                                    </div>
                                    <div class="card-body">
                                        <p><strong>ID:</strong> ${cls.id}</p>
                                        <p><strong>Vagas:</strong> ${cls.available_slots} / ${cls.total_slots}</p>
                                        <p><strong>Período:</strong> ${UI.formatDate(cls.start_date)} - ${UI.formatDate(cls.end_date)}</p>
                                        <button class="btn btn-secondary btn-sm" onclick="ClassesModule.showClassDetails(${cls.id})">
                                            Gerenciar / Detalhes
                                        </button>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
        });

        if (html === '') return '<p>Nenhuma turma cadastrada.</p>';
        return html;
    },

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.id === 'btn-create-class') {
                this.showCreateClassModal();
            }
        });
    },

    async showClassDetails(classId) {
        try {
            const [classDetails, students] = await Promise.all([
                ApiClient.get(API_CONFIG.ENDPOINTS.CLASSES.GET(classId)),
                ApiClient.get(API_CONFIG.ENDPOINTS.CLASSES.STUDENTS(classId))
            ]);

            const formHtml = `
                <div class="tabs">
                    <button class="tab-btn active" onclick="UI.switchTab(event, 'tab-info')">Informações</button>
                    <button class="tab-btn" onclick="UI.switchTab(event, 'tab-students')">Estudantes (${students.length})</button>
                </div>

                <div id="tab-info" class="tab-pane active">
                    <form id="form-edit-class">
                        <input type="hidden" name="id" value="${classDetails.id}">
                        <div class="form-field">
                            <label>ID da Turma</label>
                            <input type="text" value="${classDetails.id}" disabled class="form-control">
                        </div>
                        <div class="form-field">
                            <label>Nome da Turma</label>
                            <input type="text" name="name" value="${classDetails.name}" required class="form-control">
                        </div>
                        <div class="form-field">
                            <label>Total de Vagas</label>
                            <input type="number" name="total_slots" value="${classDetails.total_slots}" required class="form-control">
                        </div>
                        <div class="form-field">
                            <label>Data de Início</label>
                            <input type="date" name="start_date" value="${classDetails.start_date || ''}" class="form-control">
                        </div>
                        <div class="form-field">
                            <label>Data de Término</label>
                            <input type="date" name="end_date" value="${classDetails.end_date || ''}" class="form-control">
                        </div>
                        <div class="form-field">
                            <label>Template do Certificado</label>
                            <select name="certificate_template" required class="form-control">
                                ${this.availableTemplates.map(t =>
                `<option value="${t.id}" ${t.id === classDetails.certificate_template ? 'selected' : ''}>${t.name} (${t.description})</option>`
            ).join('')}
                            </select>
                        </div>
                        <div class="form-field">
                            <label>
                                <input type="checkbox" name="is_open" ${classDetails.is_open ? 'checked' : ''}> Aberta para inscrições
                            </label>
                        </div>
                    </form>
                </div>

                <div id="tab-students" class="tab-pane">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nome</th>
                                <th>Email</th>
                                <th>CPF</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${students.map(s => `
                                <tr>
                                    <td>${s.id}</td>
                                    <td>${s.name}</td>
                                    <td>${s.email}</td>
                                    <td>${s.cpf}</td>
                                    <td>${s.authorized ? '<span class="badge badge-success">Autorizado</span>' : '<span class="badge badge-warning">Pendente</span>'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;

            const footer = `
                <button class="btn btn-success" onclick="ClassesModule.handleBulkCertificates(${classId})">📄 Gerar Certificados em Massa</button>
                <button class="btn btn-danger" style="margin-right: auto;" onclick="ClassesModule.handleDeleteClass(${classId})">Excluir Turma</button>
                <button class="btn btn-secondary" onclick="UI.closeModal(this.closest('.modal-overlay'))">Fechar</button>
                <button class="btn btn-primary" onclick="ClassesModule.handleUpdateClass(${classId})">Salvar Alterações</button>
            `;

            const modal = UI.createModal(`Gerenciar Turma #${classId}`, formHtml, { footer, width: '800px' });
            UI.showModal(modal);

        } catch (error) {
            console.error('Error fetching class details:', error);
            Notifications.error('Erro ao carregar detalhes da turma.');
        }
    },

    async handleUpdateClass(classId) {
        const form = document.getElementById('form-edit-class');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const formData = new FormData(form);
        const data = {
            name: formData.get('name'),
            total_slots: parseInt(formData.get('total_slots')),
            is_open: formData.get('is_open') === 'on',
            start_date: formData.get('start_date') || null,
            end_date: formData.get('end_date') || null,
            certificate_template: formData.get('certificate_template'),
        };

        try {
            await ApiClient.put(API_CONFIG.ENDPOINTS.CLASSES.UPDATE(classId), data);
            Notifications.success('Turma atualizada com sucesso!');

            const modal = document.querySelector('.modal-overlay');
            if (modal) UI.closeModal(modal);

            await this.loadData();
            this.render();
        } catch (error) {
            console.error('Error updating class:', error);
        }
    },

    showCreateClassModal() {
        const formHtml = `
            <form id="form-create-class">
                <div class="form-field">
                    <label>Curso *</label>
                    <select name="course_id" required class="form-control">
                        <option value="">Selecione um curso</option>
                        ${this.courses.map(c => `<option value="${c.id}">${c.name}</option>`).join('')}
                    </select>
                </div>
                <div class="form-field">
                    <label>Nome da Turma *</label>
                    <input type="text" name="name" required class="form-control" placeholder="Turma 2024.1">
                </div>
                <div class="form-field">
                    <label>Total de Vagas *</label>
                    <input type="number" name="total_slots" required class="form-control" min="1" value="30">
                </div>
                <div class="form-field">
                    <label>Data de Início</label>
                    <input type="date" name="start_date" class="form-control">
                </div>
                <div class="form-field">
                    <label>Data de Término</label>
                    <input type="date" name="end_date" class="form-control">
                </div>
                <div class="form-field">
                    <label>Template do Certificado</label>
                    <select name="certificate_template" required class="form-control">
                        ${this.availableTemplates.map(t =>
            `<option value="${t.id}">${t.name} (${t.description})</option>`
        ).join('')}
                    </select>
                </div>
                <div class="form-field">
                    <label>
                        <input type="checkbox" name="is_open" checked> Aberta para inscrições
                    </label>
                </div>
            </form>
        `;

        const footer = `
            <button class="btn btn-secondary" onclick="UI.closeModal(this.closest('.modal-overlay'))">Cancelar</button>
            <button class="btn btn-primary" onclick="ClassesModule.handleCreateClass()">Criar Turma</button>
        `;

        const modal = UI.createModal('Criar Nova Turma', formHtml, { footer });
        UI.showModal(modal);
    },

    async handleCreateClass() {
        const form = document.getElementById('form-create-class');
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const formData = new FormData(form);
        const data = {
            course_id: parseInt(formData.get('course_id')),
            name: formData.get('name'),
            total_slots: parseInt(formData.get('total_slots')),
            is_open: formData.get('is_open') === 'on',
            start_date: formData.get('start_date') || null,
            end_date: formData.get('end_date') || null,
            certificate_template: formData.get('certificate_template'),
        };

        try {
            await ApiClient.post(API_CONFIG.ENDPOINTS.CLASSES.CREATE, data);
            Notifications.success('Turma criada com sucesso!');

            const modal = document.querySelector('.modal-overlay');
            if (modal) UI.closeModal(modal);

            await this.loadData();
            this.render();
        } catch (error) {
            console.error('Error creating class:', error);
        }
    },

    async handleBulkCertificates(classId) {
        if (!confirm('Gerar certificados para todos os alunos autorizados desta turma?')) {
            return;
        }

        try {
            Notifications.info('Gerando certificados... Por favor, aguarde.');

            const token = AuthManager.getToken();
            const response = await fetch(`/api/v1/certificates/bulk-class?class_id=${classId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao gerar certificados');
            }

            // Download do arquivo ZIP
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `certificados_turma_${classId}.zip`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            Notifications.success('Certificados gerados com sucesso! Download iniciado.');
        } catch (error) {
            console.error('Error generating bulk certificates:', error);
            Notifications.error(error.message || 'Erro ao gerar certificados em massa.');
        }
    },

    async handleDeleteClass(classId) {
        if (!confirm('Tem certeza que deseja excluir esta turma?')) {
            return;
        }

        try {
            await ApiClient.delete(API_CONFIG.ENDPOINTS.CLASSES.UPDATE(classId));
            Notifications.success('Turma excluída com sucesso!');

            const modal = document.querySelector('.modal-overlay');
            if (modal) UI.closeModal(modal);

            await this.loadData();
            this.render();
        } catch (error) {
            console.error('Error deleting class:', error);
            Notifications.error('Erro ao excluir turma.');
        }
    }
};

window.ClassesModule = ClassesModule;
