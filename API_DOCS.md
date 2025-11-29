# 📚 Documentação da API CertifyAPI

Esta documentação fornece detalhes técnicos sobre a API RESTful do sistema CertifyAPI.

## 🔗 Links Rápidos

- **Swagger UI (Interativo):** `http://localhost:8000/docs`
- **ReDoc (Estático):** `http://localhost:8000/redoc`
- **Interface de Teste:** `http://localhost:8000/static/index.html`

## 🔐 Autenticação

A API utiliza **OAuth2 com Password Flow** e **JWT (JSON Web Tokens)**. Existem dois tipos de usuários com endpoints de autenticação distintos:

### 1. Administradores
- **Login:** `POST /api/v1/login/access-token`
- **Username:** Email do administrador
- **Password:** Senha do administrador
- **Header:** `Authorization: Bearer <token>`
- **Permissões:** Acesso total ao sistema (criar cursos, turmas, gerar certificados).

### 2. Estudantes
- **Login:** `POST /api/v1/students/login`
- **Username:** Email do estudante
- **Password:** Senha do estudante
- **Header:** `Authorization: Bearer <token>`
- **Permissões:** Acesso aos próprios dados, inscrições e certificados.

## 🚦 Tratamento de Erros

A API utiliza os seguintes códigos de status HTTP padrão:

| Código | Significado | Descrição |
|--------|-------------|-----------|
| `200` | OK | Requisição processada com sucesso. |
| `201` | Created | Recurso criado com sucesso. |
| `400` | Bad Request | Erro de validação ou regra de negócio (ex: turma lotada). |
| `401` | Unauthorized | Token ausente, inválido ou expirado. |
| `403` | Forbidden | Usuário autenticado mas sem permissão para o recurso. |
| `404` | Not Found | Recurso não encontrado (ex: ID inexistente). |
| `422` | Validation Error | Erro no formato dos dados enviados (Pydantic). |
| `500` | Internal Server Error | Erro inesperado no servidor. |

### Formato de Erro
```json
{
  "detail": "Mensagem descritiva do erro"
}
```

## 📦 Recursos Principais

### Cursos (`/courses`)
Gerenciamento do catálogo de cursos.
- **Model:** `Course` (nome, descrição, carga horária)
- **Relação:** Um curso pode ter várias turmas.

### Turmas (`/classes`)
Instâncias de cursos com datas e vagas limitadas.
- **Model:** `Class`
- **Regras:**
  - `total_slots`: Capacidade total.
  - `available_slots`: Vagas restantes (atualizado automaticamente).
  - `is_open`: Controla se aceita novas inscrições.
  - `start_date`: Data de início das aulas (opcional).
  - `end_date`: Data de término das aulas (opcional).
  - `is_active`: Indica se a turma está ativa (soft delete).

### Inscrições (`/enrollments`)
Vínculo entre estudante e turma.
- **Regras:**
  - Estudante não pode se inscrever duas vezes na mesma turma.
  - Não é possível se inscrever se `available_slots` for 0.
  - Cancelamento só permitido se a turma estiver aberta (`is_open=True`).

### Alunos (Students)
- `GET /api/v1/students/me` - Perfil do aluno (aluno auth)
- `PUT /api/v1/students/me` - Atualizar perfil (aluno auth)
- `GET /api/v1/students/me/dashboard` - Dashboard do aluno (aluno auth)
- `GET /api/v1/students/me/certificates` - Meus certificados (aluno auth)
- `GET /api/v1/students/cpf/{cpf}/certificates` - Buscar certificados por CPF (público)

### Certificados (Certificates)
- `POST /api/v1/certificates/bulk-class?class_id={id}` - Gerar em massa e baixar ZIP (admin)
  - **Comportamento:** Gera PDFs para todos os alunos autorizados e retorna um arquivo ZIP. O arquivo é removido do servidor após o download.
- `POST /api/v1/certificates/single` - Gerar certificado individual (admin)
- `GET /api/v1/students/me/certificates/{id}/download` - Download do meu certificado (aluno auth)
- **Validação:** Cada certificado possui um UUID único validável publicamente.

## 🛠️ Desenvolvimento e Testes

### Executar Localmente
```bash
uvicorn app.main:app --reload
```

### Executar Testes
```bash
pytest
```
