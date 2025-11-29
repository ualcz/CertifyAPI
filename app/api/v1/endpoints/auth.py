from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.models.student import Student
from app.schemas.token import Token
from app.schemas.student import StudentRegister, StudentLogin, StudentAuth

router = APIRouter()

# ========== ENDPOINTS DE ADMIN ==========

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Realizar login e obter token JWT de acesso.
    
    Este endpoint implementa autenticação OAuth2 compatível. Use o token retornado
    para acessar endpoints protegidos (ADMIN) incluindo o header:
    `Authorization: Bearer {access_token}`
    
    **Exemplo de uso:**
    ```python
    import requests
    
    response = requests.post(
        "http://localhost:8000/api/v1/login/access-token",
        data={"username": "admin@example.com", "password": "admin13"}
    )
    token = response.json()["access_token"]
    ```
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

# ========== ENDPOINTS DE ESTUDANTES ==========

@router.post("/students/register", response_model=StudentAuth)
def register_student(
    *,
    db: Session = Depends(get_db),
    student_in: StudentRegister,
) -> Any:
    """
    Registrar um novo estudante no sistema (PÚBLICO - sem autenticação).
    
    Cria uma conta de estudante com email e senha. O CPF e email devem ser únicos.
    Após o registro, o estudante pode fazer login para acessar a área autenticada.
    
    **Exemplo de uso:**
    ```python
    import requests
    
    student_data = {
        "name": "João Silva",
        "email": "joao.silva@example.com",
        "cpf": "12345678900",
        "password": "senha123"
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/students/register",
        json=student_data
    )
    
    if response.status_code == 200:
        student = response.json()
        print(f"✓ Conta criada com sucesso! ID: {student['id']}")
    elif response.status_code == 400:
        print(f"✗ {response.json()['detail']}")
    ```
    """

    existing_email = db.query(Student).filter(Student.email == student_in.email).first()
    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    existing_cpf = db.query(Student).filter(Student.cpf == student_in.cpf).first()
    if existing_cpf:
        raise HTTPException(
            status_code=400,
            detail="CPF already registered"
        )
    
    student = Student(
        name=student_in.name,
        email=student_in.email,
        cpf=student_in.cpf,
        hashed_password=security.get_password_hash(student_in.password),
        authorized=True,
        is_active=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    
    return student

@router.post("/students/login", response_model=Token)
def login_student(
    *,
    db: Session = Depends(get_db),
    login_data: StudentLogin,
) -> Any:
    """
    Realizar login de estudante e obter token JWT (PÚBLICO - sem autenticação).
    
    Autentica um estudante com email e senha. Use o token retornado
    para acessar endpoints protegidos de estudante incluindo o header:
    `Authorization: Bearer {access_token}`
    
    **Exemplo de uso:**
    ```python
    import requests
    
    login_data = {
        "email": "joao.silva@example.com",
        "password": "senha123"
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/students/login",
        json=login_data
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✓ Login realizado com sucesso!")
        
        # Usar o token nas próximas requisições
        headers = {"Authorization": f"Bearer {token}"}
        # ...
    else:
        print(f"✗ {response.json()['detail']}")
    ```
    """

    student = db.query(Student).filter(Student.email == login_data.email).first()
    
    if not student or not student.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    if not security.verify_password(login_data.password, student.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    if not student.is_active:
        raise HTTPException(status_code=400, detail="Inactive student account")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        student.id, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
