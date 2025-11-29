from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class EnrollmentBase(BaseModel):
    student_id: int
    class_id: int

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentInDBBase(EnrollmentBase):
    id: int
    enrollment_date: datetime

    class Config:
        from_attributes = True

class Enrollment(EnrollmentInDBBase):
    pass

class EnrollmentResponse(BaseModel):
    message: str
    enrollment_id: Optional[int] = None
    class_id: int
    class_name: str

class EnrollmentDetail(BaseModel):
    enrollment_id: int
    class_id: int
    class_name: str
    course_id: Optional[int]
    course_name: str
    enrollment_date: datetime
    is_open: bool