import os
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.services.pdf_service import generate_certificate_pdf

from app.api import deps
from app.db.session import get_db
from app.models.student import Student
from app.models.class_model import Class
from app.models.enrollment import Enrollment
from app.models.certificate import Certificate
from app.models.course import Course
from app.schemas.student import (
    Student as StudentSchema, 
    StudentCreate, 
    StudentCertificatesResponse, 
    StudentInfoResponse,
    StudentAuth,
    StudentDashboard,
    EnrollmentInfo,
    StudentCertificateResponse,
    StudentProfileUpdate
)
from app.core import security

router = APIRouter()


def cleanup_file(file_path: str):
    """Remove o arquivo após o download."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✓ Arquivo removido: {file_path}")
    except Exception as e:
        print(f"✗ Erro ao remover arquivo {file_path}: {e}")

# ========== ENDPOINT PÚBLICO DE CONSULTA DE CERTIFICADOS ==========

@router.get("/cpf/{cpf}/certificates", response_model=StudentCertificatesResponse)
def get_certificates_by_cpf(
    *,
    db: Session = Depends(get_db),
    cpf: str,
) -> Any:
    """
    Buscar todos os certificados de um aluno por CPF (PÚBLICO - sem autenticação).
    
    Endpoint público que permite que alunos consultem seus certificados
    usando apenas o CPF, sem necessidade de login.
    
    **Exemplo de uso:**
    ```python
    import requests
    
    cpf = "12345678900"
    response = requests.get(
        f"http://localhost:8000/api/v1/students/cpf/{cpf}/certificates"
    )
    
    if response.status_code == 200:
        dados = response.json()
        print(f"Aluno: {dados['student']['name']}")
        print(f"Total de certificados: {dados['total_certificates']}\n")
        
        for cert in dados['certificates']:
            print(f"- {cert['course_name']}")
            print(f"  Emitido em: {cert['issue_date']}")
            print(f"  Download: {cert['download_url']}")
            print(f"  Validar: /validate/{cert['uuid']}\n")
    else:
        print("CPF não encontrado no sistema")
    ```
    """
    students = db.query(Student).filter(Student.cpf == cpf).all()
    
    if not students:
        raise HTTPException(status_code=404, detail="No student found with this CPF")
    
    all_certificates = []
    student_info = None
    
    for student in students:
        if not student_info:
            student_info = {
                "name": student.name,
                "cpf": student.cpf,
                "email": student.email
            }
        
        certificates = db.query(Certificate).filter(Certificate.student_id == student.id).all()
        for cert in certificates:
            course = db.query(Course).filter(Course.id == cert.course_id).first()
            all_certificates.append({
                "certificate_id": cert.id,
                "uuid": cert.uuid,
                "course_name": course.name if course else "Unknown",
                "course_id": cert.course_id,
                "issue_date": cert.issue_date,
                "download_url": f"/api/v1/certificates/{cert.id}/download"
            })
    
    return StudentCertificatesResponse(
       student=StudentInfoResponse(**student_info),
        certificates=all_certificates,
        total_certificates=len(all_certificates)
    )

# ========== ENDPOINTS PARA ESTUDANTES AUTENTICADOS ==========

@router.get("/me", response_model=StudentAuth)
def get_my_info(
    *,
    db: Session = Depends(get_db),
    current_student: Student = Depends(deps.get_current_active_student),
) -> Any:
    """
    Obter informações do estudante autenticado (ESTUDANTE - requer autenticação).
    
    Retorna os dados do perfil do estudante logado.
    
    **Exemplo de uso:**
    ```python
    import requests
    
    headers = {"Authorization": f"Bearer {student_token}"}
    response = requests.get(
        "http://localhost:8000/api/v1/students/me",
        headers=headers
    )
    
    student = response.json()
    print(f"Nome: {student['name']}")
    print(f"Email: {student['email']}")
    print(f"CPF: {student['cpf']}")
    ```
    """
    return current_student

@router.put("/me", response_model=StudentAuth)
def update_my_profile(
    *,
    db: Session = Depends(get_db),
    student_in: StudentProfileUpdate,
    current_student: Student = Depends(deps.get_current_active_student),
) -> Any:
    """
    Atualizar perfil do estudante (ESTUDANTE - requer autenticação).
    """
    if student_in.email and student_in.email != current_student.email:
        existing_email = db.query(Student).filter(Student.email == student_in.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_student.email = student_in.email
        
    if student_in.name:
        current_student.name = student_in.name
        
    if student_in.password:
        current_student.hashed_password = security.get_password_hash(student_in.password)
        
    db.commit()
    db.refresh(current_student)
    return current_student

@router.get("/me/dashboard", response_model=StudentDashboard)
def get_my_dashboard(
    *,
    db: Session = Depends(get_db),
    current_student: Student = Depends(deps.get_current_active_student),
) -> Any:
    """
    Obter dashboard completo do estudante (ESTUDANTE - requer autenticação).
    
    Retorna informações consolidadas: perfil, inscrições ativas e contagem de certificados.
    
    **Exemplo de uso:**
    ```python
    import requests
    
    headers = {"Authorization": f"Bearer {student_token}"}
    response = requests.get(
        "http://localhost:8000/api/v1/students/me/dashboard",
        headers=headers
    )
    
    dashboard = response.json()
    print(f"Estudante: {dashboard['student']['name']}")
    print(f"Inscrições ativas: {len(dashboard['enrollments'])}")
    print(f"Certificados: {dashboard['certificates_count']}")
    ```
    """

    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == current_student.id
    ).all()
    
    enrollment_infos = []
    for enrollment in enrollments:
        class_obj = db.query(Class).filter(Class.id == enrollment.class_id).first()
        if class_obj:
            course = db.query(Course).filter(Course.id == class_obj.course_id).first()
            enrollment_infos.append(EnrollmentInfo(
                enrollment_id=enrollment.id,
                class_id=class_obj.id,
                class_name=class_obj.name,
                course_id=course.id if course else 0,
                course_name=course.name if course else "Unknown",
                enrollment_date=enrollment.enrollment_date,
                is_open=class_obj.is_open
            ))
    
    certificates_count = db.query(Certificate).filter(
        Certificate.student_id == current_student.id
    ).count()
    
    return StudentDashboard(
        student=StudentAuth.from_orm(current_student),
        enrollments=enrollment_infos,
        certificates_count=certificates_count
    )

@router.get("/me/certificates", response_model=List[StudentCertificateResponse])
def get_my_certificates(
    *,
    db: Session = Depends(get_db),
    current_student: Student = Depends(deps.get_current_active_student),
) -> Any:
    """
    Listar certificados do estudante autenticado (ESTUDANTE - requer autenticação).
    
    Retorna todos os certificados emitidos para o estudante logado.
    
    **Exemplo de uso:**
    ```python
    import requests
    
    headers = {"Authorization": f"Bearer {student_token}"}
    response = requests.get(
        "http://localhost:8000/api/v1/students/me/certificates",
        headers=headers
    )
    
    certificates = response.json()
    for cert in certificates:
        print(f"{cert['course_name']} - Emitido em {cert['issue_date']}")
        print(f"  Download: {cert['download_url']}")
    ```
    """
    certificates = db.query(Certificate).filter(
        Certificate.student_id == current_student.id
    ).all()
    
    result = []
    for cert in certificates:
        course = db.query(Course).filter(Course.id == cert.course_id).first()
        result.append({
            "certificate_id": cert.id,
            "uuid": cert.uuid,
            "course_name": course.name if course else "Unknown",
            "course_id": cert.course_id,
            "issue_date": cert.issue_date,
            "download_url": f"/api/v1/students/me/certificates/{cert.id}/download"
        })
    
    return result

@router.get("/me/certificates/{certificate_id}/download")
def download_my_certificate(
    *,
    db: Session = Depends(get_db),
    certificate_id: int,
    current_student: Student = Depends(deps.get_current_active_student),
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Download de certificado próprio em PDF (ESTUDANTE - requer autenticação).
    O arquivo PDF é automaticamente apagado após o download.
    """

    certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    if certificate.student_id != current_student.id:
        raise HTTPException(
            status_code=403,
            detail="You can only download your own certificates"
        )
    
    course = db.query(Course).filter(Course.id == certificate.course_id).first()
    
    pdf_path = generate_certificate_pdf(certificate, current_student, course)
    
    filename = f"certificado_{course.name.replace(' ', '_')}_{current_student.name.replace(' ', '_')}.pdf" if course else f"certificado_{certificate_id}.pdf"
    
    # Agendar remoção do PDF após o download
    background_tasks.add_task(cleanup_file, pdf_path)
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=filename
    )

