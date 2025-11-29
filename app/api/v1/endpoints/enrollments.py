from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.class_model import Class
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.schemas.class_schema import ClassWithCourse
from app.schemas.enrollment import EnrollmentResponse, EnrollmentDetail

router = APIRouter()

@router.get("/classes/available", response_model=List[ClassWithCourse])
def list_available_classes(
    *,
    db: Session = Depends(get_db),
    current_student: Student = Depends(deps.get_current_active_student),
) -> Any:
    """
    Listar turmas disponíveis para inscrição (ESTUDANTE - requer autenticação).
    
    Retorna apenas turmas que estão abertas para inscrição (is_open=True)
    e que possuem vagas disponíveis (available_slots > 0).
    
    **Exemplo de uso:**
    ```python
    import requests
    
    headers = {"Authorization": f"Bearer {student_token}"}
    response = requests.get(
        "http://localhost:8000/api/v1/enrollments/classes/available",
        headers=headers
    )
    
    turmas = response.json()
    for turma in turmas:
        print(f"{turma['course_name']} - {turma['name']}")
        print(f"  Vagas: {turma['available_slots']}/{turma['total_slots']}")
    ```
    """
    classes = db.query(Class).filter(
        Class.is_open == True,
        Class.available_slots > 0,
        Class.is_active == True
    ).all()
    
    result = []
    for class_obj in classes:
        course = db.query(Course).filter(Course.id == class_obj.course_id).first()
        enrolled_count = db.query(Enrollment).filter(Enrollment.class_id == class_obj.id).count()
        
        result.append({
            **class_obj.__dict__,
            "course_name": course.name if course else "Unknown",
            "enrollment_count": enrolled_count,
            "is_open": class_obj.is_open,
            "available_slots": class_obj.available_slots,
            "total_slots": class_obj.total_slots,
        })
    
    return result

@router.post("/", response_model=EnrollmentResponse)
def enroll_in_class(
    *,
    db: Session = Depends(get_db),
    class_id: int,
    current_student: Student = Depends(deps.get_current_active_student),
) -> Any:
    """
    Inscrever-se em uma turma (ESTUDANTE - requer autenticação).
    
    Permite que um estudante autenticado se inscreva em uma turma aberta.
    Verifica automaticamente se há vagas disponíveis e se o estudante
    já está inscrito.
    
    **Exemplo de uso:**
    ```python
    import requests
    
    headers = {"Authorization": f"Bearer {student_token}"}
    response = requests.post(
        "http://localhost:8000/api/v1/enrollments/?class_id=1",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✓ Inscrição realizada com sucesso!")
    elif response.status_code == 400:
        print(f"✗ {response.json()['detail']}")
    ```
    """

    class_obj = db.query(Class).filter(Class.id == class_id).first()

    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")

    if not class_obj.is_open:
        raise HTTPException(
            status_code=400,
            detail="Class is closed for enrollment"
        )
    

    if class_obj.available_slots <= 0:
        raise HTTPException(
            status_code=400,
            detail="No available slots in this class"
        )
    
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_student.id,
        Enrollment.class_id == class_id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=400,
            detail="You are already enrolled in this class"
        )
    
    enrollment = Enrollment(
        student_id=current_student.id,
        class_id=class_id,
    )
    db.add(enrollment)
    
    class_obj.available_slots -= 1
    
    db.commit()
    db.refresh(enrollment)
    
    return {
        "message": "Successfully enrolled in class",
        "enrollment_id": enrollment.id,
        "class_id": class_id,
        "class_name": class_obj.name
    }

@router.get("/me", response_model=List[EnrollmentDetail])
def list_my_enrollments(
    *,
    db: Session = Depends(get_db),
    current_student: Student = Depends(deps.get_current_active_student),
) -> Any:
    """
    Listar minhas inscrições (ESTUDANTE - requer autenticação).
    
    Retorna todas as inscrições do estudante autenticado com
    informações da turma e curso.
    
    **Exemplo de uso:**
    ```python
    import requests
    
    headers = {"Authorization": f"Bearer {student_token}"}
    response = requests.get(
        "http://localhost:8000/api/v1/enrollments/me",
        headers=headers
    )
    
    enrollments = response.json()
    for enroll in enrollments:
        print(f"{enroll['course_name']} - {enroll['class_name']}")
        print(f"  Inscrito em: {enroll['enrollment_date']}")
    ```
    """

    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == current_student.id
    ).all()
    
    result = []
    for enrollment in enrollments:
        class_obj = db.query(Class).filter(Class.id == enrollment.class_id).first()
        if class_obj:
            course = db.query(Course).filter(Course.id == class_obj.course_id).first()
            result.append({
                "enrollment_id": enrollment.id,
                "class_id": class_obj.id,
                "class_name": class_obj.name,
                "course_id": course.id if course else None,
                "course_name": course.name if course else "Unknown",
                "enrollment_date": enrollment.enrollment_date,
                "is_open": class_obj.is_open,
            })
    
    return result

@router.delete("/{enrollment_id}", response_model=EnrollmentResponse)
def cancel_enrollment(
    *,
    db: Session = Depends(get_db),
    enrollment_id: int,
    current_student: Student = Depends(deps.get_current_active_student),
) -> Any:
    """
    Cancelar inscrição em uma turma (ESTUDANTE - requer autenticação).
    
    Remove a inscrição do estudante em uma turma. Só é permitido
    cancelar se a turma ainda estiver aberta para inscrições (is_open=True).
    
    **Exemplo de uso:**
    ```python
    import requests
    
    headers = {"Authorization": f"Bearer {student_token}"}
    response = requests.delete(
        "http://localhost:8000/api/v1/enrollments/123",
        headers=headers
    )
    
    if response.status_code == 200:
        print("✓ Inscrição cancelada com sucesso!")
    elif response.status_code == 400:
        print(f"✗ {response.json()['detail']}")
    ```
    """

    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    if enrollment.student_id != current_student.id:
        raise HTTPException(
            status_code=403,
            detail="You can only cancel your own enrollments"
        )

    class_obj = db.query(Class).filter(Class.id == enrollment.class_id).first()
    
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    if not class_obj.is_open:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel enrollment in a closed class"
        ) 
 
    db.delete(enrollment)
    
    class_obj.available_slots += 1
    
    db.commit()
    
    return {
        "message": "Enrollment cancelled successfully",
        "class_id": class_obj.id,
        "class_name": class_obj.name
    }
