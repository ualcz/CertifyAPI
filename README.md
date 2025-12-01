# 🎓 CertifyAPI

> API REST para gerenciamento de cursos, turmas e emissão de certificados digitais com sistema anti-fraude.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Características

- 🔐 **Autenticação JWT** com dois níveis (Admin e Estudante)
- 📜 **Emissão de Certificados** em PDF com templates customizáveis
- 🔒 **Sistema Anti-fraude** com UUID único
- ✅ **Validação Pública** de certificados
- 📦 **Download em Massa** (ZIP com múltiplos PDFs)
- 🎓 **Gestão Completa** de cursos, turmas e inscrições

---

## 📋 Índice

- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso Rápido](#uso-rápido)
- [Documentação](#documentação)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Tecnologias](#tecnologias)

---

## 🔧 Instalação

### Pré-requisitos

- Python 3.9+
- pip

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/CertifyAPI.git
cd CertifyAPI

# 2. Crie um ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
# Crie um arquivo .env (veja seção Configuração)

# 5. Crie um usuário admin
python create_admin.py

# 6. Execute o servidor
uvicorn app.main:app --reload
```

A API estará disponível em: **http://localhost:8000**

---

## ⚙️ Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
# Database
DATABASE_URL=sqlite:///./certify.db

# Security
SECRET_KEY=seu-secret-key-super-seguro-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

---

## 🎯 Uso Rápido

### 1. Acessar Documentação Interativa

Após iniciar o servidor:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 2. Exemplo de Uso (Estudante)

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Registrar
response = requests.post(f"{BASE_URL}/students/register", json={
    "name": "João Silva",
    "email": "joao@example.com",
    "cpf": "12345678900",
    "password": "senha123"
})

# Login
response = requests.post(f"{BASE_URL}/students/login", json={
    "email": "joao@example.com",
    "password": "senha123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Ver turmas disponíveis
turmas = requests.get(
    f"{BASE_URL}/enrollments/classes/available",
    headers=headers
).json()

# Inscrever-se
requests.post(f"{BASE_URL}/enrollments/?class_id=1", headers=headers)

# Baixar certificado
cert = requests.get(
    f"{BASE_URL}/students/me/certificates/1/download",
    headers=headers
)
with open("certificado.pdf", "wb") as f:
    f.write(cert.content)
```

### 3. Exemplo de Uso (Admin)

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Login admin
response = requests.post(f"{BASE_URL}/login/access-token", data={
    "username": "admin@example.com",
    "password": "admin123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Criar curso
curso = requests.post(f"{BASE_URL}/courses/", headers=headers, json={
    "name": "Python Avançado",
    "description": "Curso de Python avançado",
    "workload": 60
}).json()

# Criar turma
turma = requests.post(f"{BASE_URL}/classes/", headers=headers, json={
    "course_id": curso["id"],
    "name": "Turma 2024.1",
    "total_slots": 30,
    "certificate_template": "modern"
}).json()

# Gerar certificados em massa (retorna ZIP)
response = requests.post(
    f"{BASE_URL}/certificates/bulk-class?class_id={turma['id']}",
    headers=headers
)
with open("certificados.zip", "wb") as f:
    f.write(response.content)
```

---

## 📚 Documentação

Para documentação completa da API, consulte:

- **[API_DOCS.md](API_DOCS.md)** - Documentação detalhada de todos os endpoints
- **[Swagger UI](http://localhost:8000/docs)** - Documentação interativa

### Principais Endpoints

| Método | Endpoint | Descrição | Acesso |
|--------|----------|-----------|--------|
| POST | `/students/register` | Registrar estudante | Público |
| POST | `/students/login` | Login estudante | Público |
| GET | `/courses/with-classes` | Listar cursos e turmas | Público |
| GET | `/enrollments/classes/available` | Turmas disponíveis | Estudante |
| POST | `/enrollments/` | Inscrever-se em turma | Estudante |
| GET | `/students/me/certificates` | Meus certificados | Estudante |
| GET | `/validate/{uuid}` | Validar certificado | Público |
| POST | `/certificates/bulk-class` | Gerar certificados em massa | Admin |

---

## 📂 Estrutura do Projeto

```
CertifyAPI/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py              # Router principal
│   │       └── endpoints/          # Endpoints da API
│   │           ├── auth.py         # Autenticação
│   │           ├── certificates.py # Certificados
│   │           ├── classes.py      # Turmas
│   │           ├── courses.py      # Cursos
│   │           ├── enrollments.py  # Inscrições
│   │           ├── students.py     # Estudantes
│   │           └── validate.py     # Validação
│   ├── core/
│   │   ├── config.py              # Configurações
│   │   └── security.py            # Segurança JWT
│   ├── db/
│   │   └── session.py             # Database session
│   ├── models/                    # Modelos SQLAlchemy
│   ├── schemas/                   # Schemas Pydantic
│   ├── services/
│   │   ├── pdf_service.py         # Geração de PDFs
│   │   └── templates/             # Templates de certificados
│   └── main.py                    # App FastAPI
├── tests/                         # Testes
├── .env                           # Variáveis de ambiente
├── .gitignore
├── API_DOCS.md                    # Documentação completa
├── create_admin.py                # Script criar admin
├── README.md                      # Este arquivo
└── requirements.txt               # Dependências
```

---

## 🛠️ Tecnologias

- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderno
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - ORM Python
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Validação de dados
- **[JWT](https://jwt.io/)** - Autenticação
- **[ReportLab](https://www.reportlab.com/)** - Geração de PDFs
- **[SQLite](https://www.sqlite.org/)** - Banco de dados
- **[Uvicorn](https://www.uvicorn.org/)** - Servidor ASGI

---

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=app tests/

# Testes específicos
pytest tests/test_auth.py
```

---

## 📝 Fluxos Principais

### Fluxo do Estudante
1. Registrar conta → `POST /students/register`
2. Fazer login → `POST /students/login`
3. Ver turmas disponíveis → `GET /enrollments/classes/available`
4. Inscrever-se → `POST /enrollments/`
5. Aguardar aprovação e emissão do certificado
6. Baixar certificado → `GET /students/me/certificates/{id}/download`

### Fluxo do Admin
1. Fazer login → `POST /login/access-token`
2. Criar curso → `POST /courses/`
3. Criar turma → `POST /classes/`
4. Aguardar inscrições dos estudantes
5. Listar alunos → `GET /classes/{id}/students`
6. Gerar certificados → `POST /certificates/bulk-class`
7. Distribuir PDFs aos estudantes

### Validação Pública
1. Obter UUID do certificado (impresso no PDF)
2. Validar → `GET /validate/{uuid}`
3. Verificar informações retornadas

---

## 🔐 Segurança

- ✅ Senhas hasheadas com bcrypt
- ✅ Autenticação via JWT
- ✅ Tokens com expiração configurável
- ✅ Validação de dados com Pydantic
- ✅ CORS configurável
- ✅ Soft delete para preservar histórico

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 📞 Contato

Para dúvidas ou sugestões:

- Documentação: [API_DOCS.md](API_DOCS.md)
- Issues: [GitHub Issues](https://github.com/ualcz/CertifyAPI/issues)
