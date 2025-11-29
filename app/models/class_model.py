from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
from app.models.mixins import TimestampMixin, SoftDeleteMixin


class Class(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    name = Column(String, nullable=False)  
    total_slots = Column(Integer, nullable=False) 
    available_slots = Column(Integer, nullable=False)
    certificate_template = Column(String, default="default", nullable=False)
    is_open = Column(Boolean, default=True, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    course = relationship("Course", back_populates="classes")
    enrollments = relationship("Enrollment", back_populates="class_")
