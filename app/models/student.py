from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.mixins import TimestampMixin


class Student(Base, TimestampMixin):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    cpf = Column(String, unique=True, index=True, nullable=False) 
    authorized = Column(Boolean, default=True, nullable=False)
   
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    certificates = relationship("Certificate", back_populates="student")
    enrollments = relationship("Enrollment", back_populates="student")
