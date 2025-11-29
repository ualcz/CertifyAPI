/**
 * Configuração centralizada da API
 * Este arquivo contém todas as URLs e configurações globais da aplicação
 */

const API_CONFIG = {
    // URL base da API
    BASE_URL: window.location.origin,
    API_VERSION: '/api/v1',

    // Endpoints da API organizados por módulo
    ENDPOINTS: {
        // Autenticação
        AUTH: {
            ADMIN_LOGIN: '/login/access-token',
            STUDENT_REGISTER: '/students/register',
            STUDENT_LOGIN: '/students/login',
        },

        // Cursos
        COURSES: {
            LIST: '/courses/',
            CREATE: '/courses/',
            GET: (id) => `/courses/${id}`,
            UPDATE: (id) => `/courses/${id}`,
            DELETE: (id) => `/courses/${id}`,
            WITH_CLASSES: '/courses/with-classes',
        },

        // Turmas
        CLASSES: {
            CREATE: '/classes/',
            GET: (id) => `/classes/${id}`,
            UPDATE: (id) => `/classes/${id}`,
            TOGGLE: (id) => `/classes/${id}/toggle`,
            BY_COURSE: (courseId) => `/classes/course/${courseId}`,
            STUDENTS: (id) => `/classes/${id}/students`,
        },

        // Estudantes
        STUDENTS: {
            ME: '/students/me',
            UPDATE_PROFILE: '/students/me',
            DASHBOARD: '/students/me/dashboard',
            MY_CERTIFICATES: '/students/me/certificates',
            CERTIFICATES_BY_CPF: (cpf) => `/students/cpf/${cpf}/certificates`,
        },

        // Inscrições
        ENROLLMENTS: {
            AVAILABLE: '/enrollments/classes/available',
            ENROLL: (classId) => `/enrollments/?class_id=${classId}`,
            MY_ENROLLMENTS: '/enrollments/me',
            CANCEL: (enrollmentId) => `/enrollments/${enrollmentId}`,
        },

        // Certificados
        CERTIFICATES: {
            BULK_CLASS: (classId) => `/certificates/bulk-class?class_id=${classId}`,
            SINGLE: '/certificates/single',
            DOWNLOAD: (id) => `/certificates/${id}/download`,
            MY_DOWNLOAD: (id) => `/certificates/me/${id}/download`,
        },

        // Validação
        VALIDATE: {
            CERTIFICATE: (uuid) => `/validate/${uuid}`,
        },
    },

    // Configurações globais
    SETTINGS: {
        TOKEN_KEY: 'certify_api_token',
        USER_TYPE_KEY: 'certify_user_type', // 'admin' ou 'student'
        TOKEN_EXPIRY_MINUTES: 30,
        REQUEST_TIMEOUT: 30000, // 30 segundos
    },

    // Templates de certificados disponíveis
    CERTIFICATE_TEMPLATES: [
        { value: 'default', label: 'Padrão (Profissional)' },
        { value: 'modern', label: 'Moderno (Tecnologia)' },
        { value: 'classic', label: 'Clássico (Acadêmico)' },
    ],

    // Mensagens padrão
    MESSAGES: {
        SUCCESS: {
            LOGIN: 'Login realizado com sucesso!',
            LOGOUT: 'Logout realizado com sucesso!',
            CREATED: 'Criado com sucesso!',
            UPDATED: 'Atualizado com sucesso!',
            DELETED: 'Removido com sucesso!',
            ENROLLED: 'Inscrição realizada com sucesso!',
        },
        ERROR: {
            NETWORK: 'Erro de conexão. Verifique sua internet.',
            UNAUTHORIZED: 'Você precisa estar autenticado para realizar esta ação.',
            FORBIDDEN: 'Você não tem permissão para realizar esta ação.',
            NOT_FOUND: 'Recurso não encontrado.',
            SERVER: 'Erro no servidor. Tente novamente mais tarde.',
            VALIDATION: 'Dados inválidos. Verifique os campos.',
        },
    },
};

// Função auxiliar para construir URL completa
API_CONFIG.buildUrl = function (endpoint) {
    if (endpoint.startsWith('http')) return endpoint;
    if (endpoint.startsWith(this.API_VERSION)) return `${this.BASE_URL}${endpoint}`;
    return `${this.BASE_URL}${this.API_VERSION}${endpoint}`;
};

// Exportar configuração
window.API_CONFIG = API_CONFIG;
