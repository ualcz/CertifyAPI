/**
 * Módulo de Certificados
 * Gerencia geração e consulta de certificados
 */

const CertificatesModule = {
    initialized: false,

    async init() {
        if (this.initialized) return;
        this.initialized = true;

        this.render();
        this.setupEventListeners();
    },

    render() {
        const container = document.getElementById('certificates-content');
        if (!container) return;

        container.innerHTML = `
            <div class="certificates-container">
                <!-- Busca por CPF (Público) -->
                <div class="card">
                    <div class="card-header"><h3>Buscar Certificados por CPF</h3></div>
                    <div class="card-body">
                        <form id="form-search-cpf">
                            <div class="form-field">
                                <label>CPF (apenas números)</label>
                                <input type="text" id="search-cpf" pattern="[0-9]{11}" required 
                                       placeholder="12345678900" class="form-control">
                            </div>
                            <button type="submit" class="btn btn-primary">Buscar Certificados</button>
                        </form>
                        <div id="cpf-results" class="mt-3"></div>
                    </div>
                </div>
                
                <!-- Geração em Massa (Admin) -->
                <div class="card" data-require-admin>
                    <div class="card-header"><h3>Gerar Certificados em Massa</h3></div>
                    <div class="card-body">
                        <form id="form-bulk-certificates">
                            <div class="form-field">
                                <label>ID da Turma</label>
                                <input type="number" id="bulk-class-id" required class="form-control" min="1">
                            </div>
                            <button type="submit" class="btn btn-primary">Gerar e Baixar ZIP</button>
                        </form>
                    </div>
                </div>
                
                <!-- Geração Individual (Admin) -->
                <div class="card" data-require-admin>
                    <div class="card-header"><h3>Gerar Certificado Individual</h3></div>
                    <div class="card-body">
                        <form id="form-single-certificate">
                            <div class="form-field">
                                <label>ID do Aluno</label>
                                <input type="number" id="single-student-id" required class="form-control" min="1">
                            </div>
                            <div class="form-field">
                                <label>ID da Turma</label>
                                <input type="number" id="single-class-id" required class="form-control" min="1">
                            </div>
                            <button type="submit" class="btn btn-primary">Gerar Certificado</button>
                        </form>
                        <div id="single-result" class="mt-3"></div>
                    </div>
                </div>
            </div>
        `;

        AuthManager.updatePermissionBasedUI();
    },

    setupEventListeners() {
        document.addEventListener('submit', async (e) => {
            if (e.target.id === 'form-search-cpf') {
                e.preventDefault();
                await this.searchByCPF();
            }
            if (e.target.id === 'form-bulk-certificates') {
                e.preventDefault();
                await this.generateBulk();
            }
            if (e.target.id === 'form-single-certificate') {
                e.preventDefault();
                await this.generateSingle();
            }
        });
    },

    async searchByCPF() {
        const cpf = document.getElementById('search-cpf').value;
        const resultsDiv = document.getElementById('cpf-results');

        try {
            const data = await ApiClient.get(API_CONFIG.ENDPOINTS.STUDENTS.CERTIFICATES_BY_CPF(cpf));

            if (data.certificates.length === 0) {
                resultsDiv.innerHTML = '<p class="text-muted">Nenhum certificado encontrado para este CPF.</p>';
                return;
            }

            resultsDiv.innerHTML = `
                <h4>Certificados de ${data.student.name}</h4>
                <div class="certificates-list">
                    ${data.certificates.map(cert => `
                        <div class="certificate-item card">
                            <h5>${cert.course_name}</h5>
                            <p>Emitido em: ${UI.formatDate(cert.issue_date)}</p>
                            <p>UUID: <code>${cert.uuid}</code></p>
                            <button class="btn btn-sm btn-primary" 
                                    onclick="ApiClient.downloadFile('${cert.download_url}', 'certificado_${cert.certificate_id}.pdf')">
                                Download PDF
                            </button>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (error) {
            resultsDiv.innerHTML = '<p class="text-danger">CPF não encontrado.</p>';
        }
    },

    async generateBulk() {
        const classId = document.getElementById('bulk-class-id').value;

        try {
            await ApiClient.downloadFile(
                API_CONFIG.ENDPOINTS.CERTIFICATES.BULK_CLASS(classId),
                `certificados_turma_${classId}.zip`,
                { method: 'POST' }
            );
        } catch (error) {
            console.error('Error generating bulk certificates:', error);
        }
    },

    async generateSingle() {
        const studentId = document.getElementById('single-student-id').value;
        const classId = document.getElementById('single-class-id').value;
        const resultDiv = document.getElementById('single-result');

        try {
            const certificate = await ApiClient.post(
                API_CONFIG.ENDPOINTS.CERTIFICATES.SINGLE,
                null,
                { student_id: parseInt(studentId), class_id: parseInt(classId) }
            );

            resultDiv.innerHTML = `
                <div class="alert alert-success">
                    <h5>Certificado Gerado com Sucesso!</h5>
                    <p>UUID: <code>${certificate.uuid}</code></p>
                    <p>Aluno: ${certificate.data_snapshot.student_name}</p>
                    <p>Curso: ${certificate.data_snapshot.course_name}</p>
                </div>
            `;

            Notifications.success('Certificado gerado com sucesso!');
        } catch (error) {
            resultDiv.innerHTML = `<div class="alert alert-danger">${error.message || 'Erro ao gerar certificado'}</div>`;
            Notifications.error(error.message || 'Erro ao gerar certificado');
        }
    },
};

window.CertificatesModule = CertificatesModule;
