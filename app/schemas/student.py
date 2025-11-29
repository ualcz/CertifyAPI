from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from app.core.validators import validate_cpf


class StudentBase(BaseModel):
    name: str
    email: EmailStr
    cpf: Optional[str] = None


class StudentCreate(BaseModel):
    name: str
    email: EmailStr
    cpf: str

    @field_validator('cpf')
    @classmethod
    def validate_cpf_format(cls, v):
        return validate_cpf(v)


class StudentRegister(BaseModel):
    name: str
    email: EmailStr
    cpf: str
    password: str = Field(..., min_length=6, description="Senha com no mínimo 6 caracteres")

    @field_validator('cpf')
    @classmethod
    def validate_cpf_format(cls, v):
        return validate_cpf(v)


class StudentLogin(BaseModel):
    email: EmailStr
    password: str


class StudentUpdate(BaseModel):
    """Schema para atualização de estudante por admin."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    authorized: Optional[bool] = None


class StudentProfileUpdate(BaseModel):
    """Schema para atualização de perfil pelo próprio estudante."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)


class Student(StudentBase):
    id: int
    authorized: bool = False
    is_active: bool = True

    class Config:
        from_attributes = True


class StudentAuth(BaseModel):
    id: int
    name: str
    email: EmailStr
    cpf: str
    authorized: bool
    is_active: bool

    class Config:
        from_attributes = True


class StudentInfoResponse(BaseModel):
    name: str
    cpf: str
    email: EmailStr

    class Config:
        from_attributes = True


class StudentCertificateResponse(BaseModel):
    certificate_id: int
    uuid: str
    course_name: str
    course_id: int
    issue_date: datetime
    download_url: str
    

    class Config:
        from_attributes = True


class StudentCertificatesResponse(BaseModel):
    student: StudentInfoResponse
    certificates: List[StudentCertificateResponse]
    total_certificates: int

    class Config:
        from_attributes = True


class EnrollmentInfo(BaseModel):
    enrollment_id: int
    class_id: int
    class_name: str
    course_id: int
    course_name: str
    enrollment_date: datetime
    is_open: bool

    class Config:
        from_attributes = True


class StudentDashboard(BaseModel):
    student: StudentAuth
    enrollments: List[EnrollmentInfo]
    certificates_count: int

    class Config:
        from_attributes = True