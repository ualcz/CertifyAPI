from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.student import StudentInfoResponse
from app.schemas.course import CourseInfoResponse

class CertificateBase(BaseModel):
    student_id: int
    course_id: int


class CertificateCreate(CertificateBase):
    pass


class Certificate(CertificateBase):
    id: int
    uuid: str
    issue_date: datetime
    template_id: Optional[str] = None
    data_snapshot: Optional[dict] = None

    class Config:
        from_attributes = True


class CertificateValidation(BaseModel):
    valid: bool
    student: StudentInfoResponse
    course: CourseInfoResponse
    issue_date: datetime
    uuid: str