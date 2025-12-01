# 📚 Documentação da API - CertifyAPI

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Autenticação](#autenticação)
- [Início Rápido](#início-rápido)
- [Endpoints](#endpoints)
  - [Autenticação](#endpoints-autenticação)
  - [Cursos](#endpoints-cursos)
  - [Turmas](#endpoints-turmas)
  - [Estudantes](#endpoints-estudantes)
  - [Inscrições](#endpoints-inscrições)
  - [Certificados](#endpoints-certificados)
  - [Validação](#endpoints-validação)
- [Schemas](#schemas)
- [Códigos de Erro](#códigos-de-erro)

---

## 🎯 Visão Geral

A **CertifyAPI** é uma API REST para gerenciamento de cursos, turmas, inscrições e emissão de certificados digitais com sistema anti-fraude baseado em UUID.

### Características Principais

- 🔐 **Autenticação** - JWT com dois níveis (Admin e Estudante)
- 📜 **Certificados** - Geração em PDF com templates customizáveis
- 🔒 **Anti-fraude** - UUID único para cada certificado
- ✅ **Validação Pública** - Qualquer pessoa pode validar certificados
- 📦 **Download em Massa** - Geração de ZIP com múltiplos certificados
- 🎓 **Gestão Completa** - Cursos, turmas, estudantes e inscrições

### Base URL

```
http://localhost:8000/api/v1
```

---

## 🔐 Autenticação

A API utiliza **JWT (JSON Web Tokens)** para autenticação com dois níveis de acesso:

### 1. **Admin** (Superusuário)
- Acesso completo ao sistema
- Criação/edição de cursos e turmas
- Geração de certificados
- Gerenciamento de estudantes

### 2. **Estudante**
- Consulta de perfil
- Inscrição em turmas
- Download de certificados próprios
- Visualização de dashboard

### Como Autenticar

#### Admin
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/login/access-token",
    data={
        "username": "admin@example.com",
        "password": "senha_admin"
    }
)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
```

#### Estudante
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/students/login",
    json={
        "email": "estudante@example.com",
        "password": "senha123"
    }
)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
```

---

## 🚀 Início Rápido

### 1. Registrar como Estudante

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/students/register",
    json={
        "name": "João Silva",
        "email": "joao@example.com",
        "cpf": "12345678900",
        "password": "senha123"
    }
)

print(response.json())
```

### 2. Fazer Login

```python
response = requests.post(
    "http://localhost:8000/api/v1/students/login",
    json={
        "email": "joao@example.com",
        "password": "senha123"
    }
)

token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
```

### 3. Ver Turmas Disponíveis

```python
response = requests.get(
    "http://localhost:8000/api/v1/enrollments/classes/available",
    headers=headers
)

turmas = response.json()
for turma in turmas:
    print(f"{turma['course_name']} - {turma['name']}")
    print(f"Vagas: {turma['available_slots']}/{turma['total_slots']}\n")
```

### 4. Inscrever-se em uma Turma

```python
response = requests.post(
    "http://localhost:8000/api/v1/enrollments/?class_id=1",
    headers=headers
)

print(response.json()["message"])  # "Successfully enrolled in class"
```

### 5. Baixar Certificado

```python
response = requests.get(
    "http://localhost:8000/api/v1/students/me/certificates/1/download",
    headers=headers
)

with open("certificado.pdf", "wb") as f:
    f.write(response.content)
```

---

## 📍 Endpoints

## <a name="endpoints-autenticação"></a>🔑 Autenticação

### Registro de Estudante
```http
POST /students/register
```

**Acesso:** Público

**Body:**
```json
{
  "name": "João Silva",
  "email": "joao@example.com",
  "cpf": "12345678900",
  "password": "senha123"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "João Silva",
  "email": "joao@example.com",
  "cpf": "12345678900",
  "authorized": true,
  "is_active": true
}
```

---

### Login de Estudante
```http
POST /students/login
```

**Acesso:** Público

**Body:**
```json
{
  "email": "joao@example.com",
  "password": "senha123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

### Login de Admin
```http
POST /login/access-token
```

**Acesso:** Público

**Body (form-data):**
```
username: admin@example.com
password: senha_admin
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

## <a name="endpoints-cursos"></a>📚 Cursos

### Listar Cursos
```http
GET /courses/
```

**Acesso:** Público

**Query Params:**
- `skip` (int, opcional) - Número de registros para pular (padrão: 0)
- `limit` (int, opcional) - Limite de registros (padrão: 100)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Python Básico",
    "description": "Introdução ao Python",
    "workload": 40,
    "is_active": true
  }
]
```

---

### Listar Cursos com Turmas
```http
GET /courses/with-classes
```

**Acesso:** Público

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Python Básico",
    "description": "Introdução ao Python",
    "workload": 40,
    "total_classes": 2,
    "classes": [
      {
        "id": 1,
        "name": "Turma 2024.1",
        "total_slots": 30,
        "available_slots": 15,
        "is_open": true,
        "start_date": "2024-01-15",
        "end_date": "2024-03-15",
        "enrolled_students": 15
      }
    ]
  }
]
```

---

### Criar Curso
```http
POST /courses/
```

**Acesso:** Admin

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Body:**
```json
{
  "name": "Python Avançado",
  "description": "Tópicos avançados em Python",
  "workload": 60
}
```

**Response:** `200 OK`
```json
{
  "id": 2,
  "name": "Python Avançado",
  "description": "Tópicos avançados em Python",
  "workload": 60,
  "is_active": true
}
```

---

### Atualizar Curso
```http
PUT /courses/{course_id}
```

**Acesso:** Admin

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Body:**
```json
{
  "name": "Python Avançado - Atualizado",
  "workload": 80
}
```

**Response:** `200 OK`

---

### Deletar Curso (Soft Delete)
```http
DELETE /courses/{course_id}
```

**Acesso:** Admin

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response:** `200 OK`

---

## <a name="endpoints-turmas"></a>🎓 Turmas

### Listar Templates de Certificados
```http
GET /certificates/templates
```

**Acesso:** Admin

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response:** `200 OK`
```json
[
  {
    "id": "default",
    "name": "Template Padrão",
    "description": "Template padrão azul"
  },
  {
    "id": "modern",
    "name": "Template Moderno",
    "description": "Template moderno com gradiente"
  }
]
```

---

### Criar Turma
```http
POST /classes/
```

**Acesso:** Admin

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Body:**
```json
{
  "course_id": 1,
  "name": "Turma 2024.2",
  "total_slots": 30,
  "certificate_template": "modern",
  "start_date": "2024-06-01",
  "end_date": "2024-08-01"
}
```

**Response:** `200 OK`
```json
{
  "id": 2,
  "course_id": 1,
  "name": "Turma 2024.2",
  "total_slots": 30,
  "available_slots": 30,
  "is_open": true,
  "certificate_template": "modern",
  "start_date": "2024-06-01",
  "end_date": "2024-08-01"
}
```

---

### Ver Detalhes de Turma
```http
GET /classes/{class_id}
```

**Acesso:** Público

**Response:** `200 OK`
```json
{
  "id": 1,
  "course_id": 1,
  "name": "Turma 2024.1",
  "total_slots": 30,
  "available_slots": 15,
  "is_open": true,
  "start_date": "2024-01-15",
  "end_date": "2024-03-15"
}
```

---

### Atualizar Turma
```http
PUT /classes/{class_id}
```

**Acesso:** Admin

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Body:**
```json
{
  "total_slots": 40,
  "certificate_template": "elegant"
}
```

**Response:** `200 OK`

---

### Alternar Status de Inscrições
```http
PUT /classes/{class_id}/toggle
```

**Acesso:** Admin

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "is_open": false
}
```

---

### Listar Alunos da Turma
```http
GET /classes/{class_id}/students
```

**Acesso:** Admin

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "João Silva",
    "email": "joao@example.com",
    "cpf": "12345678900",
    "authorized": true,
    "enrollment_date": "2024-01-10T10:00:00"
  }
]
```

---

### Deletar Turma (Soft Delete)
```http
DELETE /classes/{class_id}
```

**Acesso:** Admin

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response:** `200 OK`

---

## <a name="endpoints-estudantes"></a>👨‍🎓 Estudantes

### Listar Todos os Estudantes
```http
GET /students/
```

**Acesso:** Admin

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Query Params:**
- `skip` (int, opcional) - Padrão: 0
- `limit` (int, opcional) - Padrão: 100

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "João Silva",
    "email": "joao@example.com",
    "cpf": "12345678900",
    "authorized": true,
    "is_active": true
  }
]
```

---

### Buscar Certificados por CPF
```http
GET /students/cpf/{cpf}/certificates
```

**Acesso:** Público

**Response:** `200 OK`
```json
{
  "student": {
    "name": "João Silva",
    "cpf": "12345678900",
    "email": "joao@example.com"
  },
  "total_certificates": 2,
  "certificates": [
    {
      "certificate_id": 1,
      "uuid": "550e8400-e29b-41d4-a716-446655440000",
      "course_name": "Python Básico",
      "course_id": 1,
      "issue_date": "2024-03-20T14:30:00",
      "download_url": "/api/v1/students/me/certificates/1/download"
    }
  ]
}
```

---

### Meu Perfil
```http
GET /students/me
```

**Acesso:** Estudante

**Headers:**
```
Authorization: Bearer {student_token}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "João Silva",
  "email": "joao@example.com",
  "cpf": "12345678900",
  "authorized": true,
  "is_active": true
}
```

---

### Dashboard do Estudante
```http
GET /students/me/dashboard
```

**Acesso:** Estudante

**Headers:**
```
Authorization: Bearer {student_token}
```

**Response:** `200 OK`
```json
{
  "student": {
    "id": 1,
    "name": "João Silva",
    "email": "joao@example.com",
    "cpf": "12345678900"
  },
  "enrollments": [
    {
      "enrollment_id": 1,
      "class_id": 1,
      "class_name": "Turma 2024.1",
      "course_id": 1,
      "course_name": "Python Básico",
      "enrollment_date": "2024-01-10T10:00:00",
      "is_open": false
    }
  ],
  "certificates_count": 2
}
```

---

### Meus Certificados
```http
GET /students/me/certificates
```

**Acesso:** Estudante

**Headers:**
```
Authorization: Bearer {student_token}
```

**Response:** `200 OK`
```json
[
  {
    "certificate_id": 1,
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "course_name": "Python Básico",
    "course_id": 1,
    "issue_date": "2024-03-20T14:30:00",
    "download_url": "/api/v1/students/me/certificates/1/download"
  }
]
```

---

### Download de Certificado
```http
GET /students/me/certificates/{certificate_id}/download
```

**Acesso:** Estudante

**Headers:**
```
Authorization: Bearer {student_token}
```

**Response:** `200 OK` (PDF file)

---

### Atualizar Perfil
```http
PUT /students/me
```

**Acesso:** Estudante

**Headers:**
```
Authorization: Bearer {student_token}
```

**Body:**
```json
{
  "name": "João da Silva",
  "email": "joao.silva@example.com",
  "password": "nova_senha123"
}
```

**Response:** `200 OK`

---

## <a name="endpoints-inscrições"></a>📝 Inscrições

### Turmas Disponíveis
```http
GET /enrollments/classes/available
```

**Acesso:** Estudante

**Headers:**
```
Authorization: Bearer {student_token}
```

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "Turma 2024.1",
    "course_name": "Python Básico",
    "total_slots": 30,
    "available_slots": 15,
    "is_open": true,
    "enrollment_count": 15
  }
]
```

---

### Inscrever-se em Turma
```http
POST /enrollments/?class_id={class_id}
```

**Acesso:** Estudante

**Headers:**
```
Authorization: Bearer {student_token}
```

**Response:** `200 OK`
```json
{
  "message": "Successfully enrolled in class",
  "enrollment_id": 1,
  "class_id": 1,
  "class_name": "Turma 2024.1"
}
```

---

### Minhas Inscrições
```http
GET /enrollments/me
```

**Acesso:** Estudante

**Headers:**
```
Authorization: Bearer {student_token}
```

**Response:** `200 OK`
```json
[
  {
    "enrollment_id": 1,
    "class_id": 1,
    "class_name": "Turma 2024.1",
    "course_id": 1,
    "course_name": "Python Básico",
    "enrollment_date": "2024-01-10T10:00:00",
    "is_open": false
  }
]
```

---

### Cancelar Inscrição
```http
DELETE /enrollments/{enrollment_id}
```

**Acesso:** Estudante

**Headers:**
```
Authorization: Bearer {student_token}
```

**Response:** `200 OK`
```json
{
  "message": "Enrollment cancelled successfully",
  "class_id": 1,
  "class_name": "Turma 2024.1"
}
```

> ⚠️ **Nota:** Só é possível cancelar se a turma ainda estiver aberta (`is_open=true`)

---

## <a name="endpoints-certificados"></a>📜 Certificados

### Gerar Certificado Único
```http
POST /certificates/single?student_id={student_id}&class_id={class_id}
```

**Acesso:** Admin

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "uuid": "550e8400-e29b-41d4-a716-446655440000",
  "student_id": 1,
  "course_id": 1,
  "template_id": "modern",
  "issue_date": "2024-03-20T14:30:00",
  "data_snapshot": {
    "student_name": "João Silva",
    "student_cpf": "12345678900",
    "course_name": "Python Básico",
    "course_workload": 40,
    "class_name": "Turma 2024.1"
  }
}
```

---

### Gerar Certificados em Massa
```http
POST /certificates/bulk-class?class_id={class_id}
```

**Acesso:** Admin

**Headers:**
```
Authorization: Bearer {admin_token}
```

**Response:** `200 OK` (ZIP file)

> 📦 Retorna um arquivo ZIP contendo PDFs de todos os certificados da turma

---

## <a name="endpoints-validação"></a>✅ Validação

### Validar Certificado por UUID
```http
GET /validate/{uuid}
```

**Acesso:** Público

**Response:** `200 OK`
```json
{
  "valid": true,
  "student": "João Silva",
  "course": "Python Básico",
  "issue_date": "2024-03-20T14:30:00",
  "uuid": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:** `404 Not Found`
```json
{
  "detail": "Certificate not found or invalid"
}
```

---

## 📦 Schemas

### Student
```json
{
  "id": "integer",
  "name": "string",
  "email": "string (email format)",
  "cpf": "string (11 dígitos)",
  "authorized": "boolean",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Course
```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "workload": "integer",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Class
```json
{
  "id": "integer",
  "course_id": "integer",
  "name": "string",
  "total_slots": "integer",
  "available_slots": "integer",
  "is_open": "boolean",
  "certificate_template": "string",
  "start_date": "date",
  "end_date": "date",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Certificate
```json
{
  "id": "integer",
  "uuid": "string (UUID v4)",
  "student_id": "integer",
  "course_id": "integer",
  "template_id": "string",
  "data_snapshot": "object",
  "issue_date": "datetime"
}
```

### Enrollment
```json
{
  "id": "integer",
  "student_id": "integer",
  "class_id": "integer",
  "enrollment_date": "datetime",
  "is_active": "boolean"
}
```

---

## ⚠️ Códigos de Erro

### 400 Bad Request
- Dados inválidos no body
- Email ou CPF já cadastrado
- Turma sem vagas disponíveis
- Estudante já inscrito na turma
- Não é possível cancelar (turma fechada)

### 401 Unauthorized
- Token ausente ou inválido
- Token expirado

### 403 Forbidden
- Sem permissão para acessar recurso
- Tentativa de baixar certificado de outro estudante

### 404 Not Found
- Recurso não encontrado
- Certificado inválido/não existe
- Curso/turma/estudante não encontrado

### 500 Internal Server Error
- Erro ao gerar certificado
- Erro no servidor

---

## 💡 Dicas de Uso

### 1. Workflow Completo Admin

```python
# 1. Login como admin
admin_token = login_admin("admin@example.com", "senha")

# 2. Criar curso
course = create_course(admin_token, {
    "name": "Python Básico",
    "description": "Introdução ao Python",
    "workload": 40
})

# 3. Criar turma
class_obj = create_class(admin_token, {
    "course_id": course["id"],
    "name": "Turma 2024.1",
    "total_slots": 30,
    "certificate_template": "modern"
})

# 4. Aguardar inscrições dos estudantes...

# 5. Listar alunos inscritos
students = get_class_students(admin_token, class_obj["id"])

# 6. Gerar certificados em massa
download_zip(admin_token, class_obj["id"], "certificados.zip")
```

### 2. Workflow Completo Estudante

```python
# 1. Registrar
register_student({
    "name": "João Silva",
    "email": "joao@example.com",
    "cpf": "12345678900",
    "password": "senha123"
})

# 2. Login
token = login_student("joao@example.com", "senha123")

# 3. Ver turmas disponíveis
turmas = get_available_classes(token)

# 4. Inscrever-se
enroll(token, class_id=1)

# 5. Ver dashboard
dashboard = get_dashboard(token)

# 6. Baixar certificado (após emissão)
certificates = get_my_certificates(token)
download_certificate(token, certificates[0]["certificate_id"])
```

### 3. Validação Pública

```python
# Validar certificado sem autenticação
uuid = "550e8400-e29b-41d4-a716-446655440000"
result = validate_certificate(uuid)

if result["valid"]:
    print(f"Certificado válido!")
    print(f"Estudante: {result['student']}")
    print(f"Curso: {result['course']}")
else:
    print("Certificado inválido!")
```

---

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Database
DATABASE_URL=sqlite:///./certify.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### Executar API

```bash
# Instalar dependências
pip install -r requirements.txt

# Criar admin (primeira vez)
python create_admin.py

# Executar servidor
uvicorn app.main:app --reload
```

### Acessar Documentação Interativa

Após iniciar o servidor, acesse:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📞 Suporte

Para dúvidas ou problemas, consulte:
- Documentação interativa: `/docs`
- Exemplos de código neste documento
- Logs do servidor para debugging

---

**Versão da API:** 1.0.0  
**Última atualização:** 01/12/2025
