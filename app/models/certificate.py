import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(Integer, ForeignKey("students.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    template_id = Column(String, nullable=True)
    data_snapshot = Column(JSON, nullable=True)
    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    
    student = relationship("Student", back_populates="certificates")
    course = relationship("Course", back_populates="certificates")
