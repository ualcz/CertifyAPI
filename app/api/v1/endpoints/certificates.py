import os
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.certificate import Certificate
from app.models.student import Student
from app.models.course import Course
from app.models.class_model import Class
from app.models.enrollment import Enrollment
from app.schemas.certificate import Certificate as CertificateSchema
from app.services.pdf_service import generate_certificate_pdf, generate_bulk_certificates_zip

router = APIRouter()


def cleanup_file(file_path: str):
    """Remove o arquivo após o download."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✓ Arquivo removido: {file_path}")
    except Exception as e:
        print(f"✗ Erro ao remover arquivo {file_path}: {e}")


@router.post("/bulk-class")
def create_certificates_by_class(
    *,
    db: Session = Depends(get_db),
    class_id: int,
    current_user = Depends(deps.get_current_active_superuser),
    background_tasks: BackgroundTasks,
) -> Any:
    """
    Gerar certificados em massa para uma turma e retornar ZIP com PDFs (ADMIN - requer autenticação).
    
    Gera certificados simultaneamente para todos os alunos autorizados de uma turma
    e retorna um arquivo ZIP contendo todos os PDFs para download.
    O arquivo ZIP é automaticamente apagado após o download.
    
    **Exemplo de uso:**
    ```python
    import requests
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        "http://localhost:8000/api/v1/certificates/bulk-class?class_id=1",
        headers=headers
    )
    
    if response.status_code == 200:
        # Salvar ZIP
        with open("certificados_turma_1.zip", "wb") as f:
            f.write(response.content)
        print("✓ Certificados gerados com sucesso!")
    elif response.status_code == 400:
        erro = response.json()
        print(f"✗ {erro['detail']}")
        # Ex: "No authorized students in this class. 15 students need authorization."
    ```
    
    **Fluxo recomendado:**
    1. Listar alunos da turma: `GET /classes/{id}/students`
    2. Autorizar alunos aprovados individualmente
    3. Gerar certificados em massa: `POST /certificates/bulk-class`
    4. Download do ZIP (arquivo é apagado automaticamente após o download)
    5. Distribuir PDFs individuais aos alunos
    """
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    course = db.query(Course).filter(Course.id == class_obj.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    enrollments = db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
    
    if not enrollments:
        raise HTTPException(status_code=404, detail="No students enrolled in this class")
    
    certificates = []
    
    for enrollment in enrollments:
        student = db.query(Student).filter(Student.id == enrollment.student_id).first()
        
        if not student:
            continue
        
        existing_cert = db.query(Certificate).filter(
            Certificate.student_id == student.id,
            Certificate.course_id == class_obj.course_id
        ).first()
        
        if existing_cert:
            certificates.append(existing_cert)
        else:
            snapshot = {
                "student_name": student.name,
                "student_cpf": student.cpf,
                "course_name": course.name,
                "course_workload": course.workload,
                "class_name": class_obj.name
            }
            
            certificate = Certificate(
                student_id=student.id,
                course_id=class_obj.course_id,
                template_id=class_obj.certificate_template,
                data_snapshot=snapshot
            )
            db.add(certificate)
            db.commit()
            db.refresh(certificate)
            certificates.append(certificate)
    
    if not certificates:
        raise HTTPException(
            status_code=400, 
            detail="No certificates could be generated for this class."
        )
    
    zip_path = generate_bulk_certificates_zip(certificates, db, class_id)
    
    # Agendar remoção do arquivo ZIP após o download
    background_tasks.add_task(cleanup_file, zip_path)
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"certificados_turma_{class_id}.zip"
    )

@router.post("/single", response_model=CertificateSchema)
def create_single_certificate(
    *,
    db: Session = Depends(get_db),
    student_id: int,
    class_id: int,
    current_user = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Gerar um único certificado para um aluno específico (ADMIN - requer autenticação).
    """

    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student_id,
        Enrollment.class_id == class_id
    ).first()
    
    if not enrollment:
        raise HTTPException(status_code=400, detail="Student is not enrolled in this class")
        
    course = db.query(Course).filter(Course.id == class_obj.course_id).first()
    
    existing_cert = db.query(Certificate).filter(
        Certificate.student_id == student.id,
        Certificate.course_id == class_obj.course_id
    ).first()
    
    if existing_cert:
        return existing_cert
        
    snapshot = {
        "student_name": student.name,
        "student_cpf": student.cpf,
        "course_name": course.name,
        "course_workload": course.workload,
        "class_name": class_obj.name
    }
    
    certificate = Certificate(
        student_id=student.id,
        course_id=class_obj.course_id,
        template_id=class_obj.certificate_template,
        data_snapshot=snapshot
    )
    db.add(certificate)
    db.commit()
    db.refresh(certificate)
    
    return certificate


