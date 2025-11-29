from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.course import Course
from app.schemas.course import Course as CourseSchema, CourseCreate, CourseUpdate

router = APIRouter()

@router.get("/", response_model=List[CourseSchema])
def read_courses(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Listar todos os cursos disponíveis (PÚBLICO - sem autenticação).
    """
    courses = db.query(Course).filter(Course.is_active == True).offset(skip).limit(limit).all()
    return courses

@router.post("/", response_model=CourseSchema)
def create_course(
    *,
    db: Session = Depends(get_db),
    course_in: CourseCreate,
    current_user = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Criar um novo curso (ADMIN - requer autenticação).
    """
    course = Course(
        name=course_in.name,
        description=course_in.description,
        workload=course_in.workload,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.get("/with-classes")
def read_courses_with_classes(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Listar todos os cursos com suas turmas disponíveis (PÚBLICO - sem autenticação).
    """
    from app.models.class_model import Class
    from app.models.enrollment import Enrollment
    
    courses = db.query(Course).filter(Course.is_active == True).offset(skip).limit(limit).all()
    result = []
    
    for course in courses:
        classes = db.query(Class).filter(
            Class.course_id == course.id,
            Class.is_active == True
        ).all()
        
        classes_data = []
        for class_obj in classes:
            enrolled_count = db.query(Enrollment).filter(
                Enrollment.class_id == class_obj.id
            ).count()
            
            classes_data.append({
                "id": class_obj.id,
                "name": class_obj.name,
                "total_slots": class_obj.total_slots,
                "available_slots": class_obj.available_slots,
                "is_open": class_obj.is_open,
                "start_date": class_obj.start_date,
                "end_date": class_obj.end_date,
                "enrolled_students": enrolled_count
            })
        
        result.append({
            "id": course.id,
            "name": course.name,
            "description": course.description,
            "workload": course.workload,
            "classes": classes_data,
            "total_classes": len(classes_data)
        })
    
    return result

@router.get("/{course_id}", response_model=CourseSchema)
def read_course(
    *,
    db: Session = Depends(get_db),
    course_id: int,
) -> Any:
    """
    Obter detalhes de um curso específico (PÚBLICO - sem autenticação).
    """
    course = db.query(Course).filter(Course.id == course_id, Course.is_active == True).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/{course_id}", response_model=CourseSchema)
def update_course(
    *,
    db: Session = Depends(get_db),
    course_id: int,
    course_in: CourseUpdate,
    current_user = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Atualizar um curso (ADMIN - requer autenticação).
    """
    course = db.query(Course).filter(Course.id == course_id, Course.is_active == True).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    update_data = course_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    return course

@router.delete("/{course_id}", response_model=CourseSchema)
def delete_course(
    *,
    db: Session = Depends(get_db),
    course_id: int,
    current_user = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Deletar (Soft Delete) um curso (ADMIN - requer autenticação).
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    course.is_active = False
    db.commit()
    db.refresh(course)
    return course
