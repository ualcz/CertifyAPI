/**
 * Módulo de Validação
 * Valida autenticidade de certificados por UUID
 */

const ValidateModule = {
    init() {
        this.render();
        this.setupEventListeners();
    },

    render() {
        const container = document.getElementById('validate-content');
        if (!container) return;

        container.innerHTML = `
            <div class="validate-container">
                <div class="card">
                    <div class="card-header">
                        <h3>Validar Certificado</h3>
                    </div>
                    <div class="card-body">
                        <p>Insira o UUID do certificado para verificar sua autenticidade:</p>
                        <form id="form-validate">
                            <div class="form-field">
                                <label>UUID do Certificado</label>
                                <input type="text" id="validate-uuid" required class="form-control"
                                       placeholder="550e8400-e29b-41d4-a716-446655440000">
                            </div>
                            <button type="submit" class="btn btn-primary">Validar</button>
                        </form>
                        
                        <div id="validation-result" class="mt-4"></div>
                    </div>
                </div>
            </div>
        `;
    },

    setupEventListeners() {
        document.addEventListener('submit', async (e) => {
            if (e.target.id === 'form-validate') {
                e.preventDefault();
                await this.validateCertificate();
            }
        });
    },

    async validateCertificate() {
        const uuid = document.getElementById('validate-uuid').value.trim();
        const resultDiv = document.getElementById('validation-result');

        try {
            const data = await ApiClient.get(API_CONFIG.ENDPOINTS.VALIDATE.CERTIFICATE(uuid));

            if (data.valid) {
                resultDiv.innerHTML = `
                    <div class="validation-success">
                        <div class="validation-icon">✓</div>
                        <h3>Certificado VÁLIDO</h3>
                        <div class="validation-details">
                            <p><strong>Aluno:</strong> ${data.student}</p>
                            <p><strong>Curso:</strong> ${data.course}</p>
                            <p><strong>Data de Emissão:</strong> ${UI.formatDate(data.issue_date)}</p>
                            <p><strong>UUID:</strong> <code>${data.uuid}</code></p>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            resultDiv.innerHTML = `
                <div class="validation-error">
                    <div class="validation-icon">✗</div>
                    <h3>Certificado INVÁLIDO</h3>
                    <p>O UUID fornecido não corresponde a nenhum certificado válido em nosso sistema.</p>
                </div>
            `;
        }
    },
};

window.ValidateModule = ValidateModule;
