from datetime import datetime
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.class_model import Class
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.schemas.class_schema import Class as ClassSchema, ClassCreate, ClassUpdate, ClassWithCourse, ClassStudent

from app.services.templates.registry import TemplateRegistry

router = APIRouter()


@router.post("/", response_model=ClassSchema)
def create_class(
    *,
    db: Session = Depends(get_db),
    class_in: ClassCreate,
    current_user = Depends(deps.get_current_active_superuser),
    is_open: bool = True,
) -> Any:
    """
    Criar uma nova turma para um curso (ADMIN - requer autenticação).
    
    Permite que administradores criem turmas com controle de vagas.
    As turmas são vinculadas a cursos existentes e gerenciam inscrições de alunos.
    
    **Exemplo de uso:**
    ```python
    import requests
    
    headers = {"Authorization": f"Bearer {token}"}
    turma_data = {
        "course_id": 1,
        "name": "Turma 2024.1",
        "total_slots": 30,
        "is_open": True,
        "start_date": "2024-01-15",
        "end_date": "2024-03-15"
    }
    
    response = requests.post(
        "http://localhost:8000/api/v1/classes/",
        headers=headers,
        json=turma_data
    )
    turma = response.json()
    ```
    """
    course = db.query(Course).filter(Course.id == class_in.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    class_obj = Class(
        course_id=class_in.course_id,
        name=class_in.name,
        total_slots=class_in.total_slots,
        available_slots=class_in.total_slots,  # Inicialmente todas as vagas disponíveis
        certificate_template=class_in.certificate_template,
        is_open=is_open,
        start_date=class_in.start_date,
        end_date=class_in.end_date,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    
    return class_obj


@router.get("/{class_id}", response_model=ClassSchema)
def get_class(
    *,
    db: Session = Depends(get_db),
    class_id: int,
) -> Any:
    """
    Obter detalhes de uma turma específica (PÚBLICO - sem autenticação).
    """
    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    return class_obj

@router.put("/{class_id}", response_model=ClassSchema)
def update_class(
    *,
    db: Session = Depends(get_db),
    class_id: int,
    class_in: ClassUpdate,
    current_user = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Atualizar informações de uma turma (ADMIN - requer autenticação).
    """
    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    update_data = class_in.dict(exclude_unset=True)
    
    if "total_slots" in update_data:
        
        new_total = update_data["total_slots"]
        enrolled = db.query(Enrollment).filter(Enrollment.class_id == class_obj.id).count()
        
        if new_total < enrolled:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reduce slots below enrolled students ({enrolled})"
            )
        class_obj.available_slots = new_total - enrolled
        class_obj.total_slots = new_total
        update_data.pop("total_slots")
    
    for field, value in update_data.items():
        setattr(class_obj, field, value)
    
    db.commit()
    db.refresh(class_obj)
    
    return class_obj

@router.put("/{class_id}/toggle", response_model=ClassSchema)
def toggle_class_status(
    *,
    db: Session = Depends(get_db),
    class_id: int,
    current_user = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Alternar status de inscrições da turma (ADMIN - requer autenticação).
    """
    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    class_obj.is_open = not class_obj.is_open
    db.commit()
    db.refresh(class_obj)
    
    return class_obj

@router.get("/{class_id}/students", response_model=List[ClassStudent])
def get_class_students(
    *,
    db: Session = Depends(get_db),
    class_id: int,
    current_user = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Listar todos os alunos inscritos em uma turma (ADMIN - requer autenticação).
    """
    class_obj = db.query(Class).filter(Class.id == class_id, Class.is_active == True).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    enrollments = db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
    
    students = []
    for enrollment in enrollments:
        student = db.query(Student).filter(Student.id == enrollment.student_id).first()
        if student:
            students.append({
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "cpf": student.cpf,
                "authorized": student.authorized,
                "enrollment_date": enrollment.enrollment_date,
                "created_at": student.created_at,
                "updated_at": student.updated_at 
                
            })
    
    return students

@router.delete("/{class_id}", response_model=ClassSchema)
def delete_class(
    *,
    db: Session = Depends(get_db),
    class_id: int,
    current_user = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Deletar (Soft Delete) uma turma (ADMIN - requer autenticação).
    
    Remove a turma da listagem, mas mantém o registro no banco de dados.
    """
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(status_code=404, detail="Class not found")
    
    class_obj.is_active = False
    db.commit()
    db.refresh(class_obj)
    return class_obj
