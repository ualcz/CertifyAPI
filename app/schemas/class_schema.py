from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ClassBase(BaseModel):
    course_id: int
    name: str
    total_slots: int
    certificate_template: str = "default"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ClassCreate(ClassBase):
    pass


class ClassUpdate(BaseModel):
    """Schema para atualização parcial de turma."""
    name: Optional[str] = None
    total_slots: Optional[int] = None
    certificate_template: Optional[str] = None
    is_open: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class Class(ClassBase):
    id: int
    available_slots: int
    is_open: bool
    is_active: bool

    class Config:
        from_attributes = True


class ClassWithCourse(Class):
    course_name: str
    enrollment_count: int


class ClassStudent(BaseModel):
    id: int
    name: str
    email: str
    cpf: str
    authorized: bool
    enrollment_date: datetime
    created_at: datetime
    updated_at: datetime
