from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.certificate import Certificate
from app.models.student import Student
from app.models.course import Course
from app.schemas.certificate import CertificateValidation

router = APIRouter()

@router.get("/{uuid}", response_model=CertificateValidation)
def validate_certificate(
    *,
    db: Session = Depends(get_db),
    uuid: str,
) -> Any:
    """
    Validar autenticidade de um certificado por UUID (PÚBLICO - sem autenticação).
    
    Endpoint público para verificação anti-fraude de certificados.
    Qualquer pessoa pode validar a autenticidade de um certificado usando o UUID.
    
    **Exemplo de uso:**
    ```python
    import requests
    
    uuid_certificado = "550e8400-e29b-41d4-a716-446655440000"
    response = requests.get(
        f"http://localhost:8000/api/v1/validate/{uuid_certificado}"
    )
    
    if response.status_code == 200:
        dados = response.json()
        if dados['valid']:
            print(f"✓ Certificado VÁLIDO")
            print(f"  Aluno: {dados['student']}")
            print(f"  Curso: {dados['course']}")
            print(f"  Emitido em: {dados['issue_date']}")
    else:
        print("✗ Certificado INVÁLIDO ou não encontrado")
    ```
    """
    certificate = db.query(Certificate).filter(Certificate.uuid == uuid).first()
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found or invalid")
    
    student = db.query(Student).filter(Student.id == certificate.student_id).first()
    course = db.query(Course).filter(Course.id == certificate.course_id).first()
    
    return CertificateValidation(
        valid=True,
        student=student.name,
        course=course.name,
        issue_date=certificate.issue_date,
        uuid=certificate.uuid
    )
