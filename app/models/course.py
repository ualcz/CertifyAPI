from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.orm import relationship
from app.db.session import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin


class Course(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    workload = Column(Float, nullable=False) 
    
    certificates = relationship("Certificate", back_populates="course")
    classes = relationship("Class", back_populates="course")
