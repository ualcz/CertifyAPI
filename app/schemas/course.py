from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class CourseBase(BaseModel):
    name: str
    description: Optional[str] = None
    workload: float


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    """Schema para atualização parcial de curso."""
    name: Optional[str] = None
    description: Optional[str] = None
    workload: Optional[float] = None


class Course(CourseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CourseInfoResponse(CourseBase):
    id: int
    name: str
    description: Optional[str] = None
    workload: float
    is_active: bool
    created_at: datetime
    updated_at: datetime
    


