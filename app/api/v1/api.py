from fastapi import APIRouter
from app.api.v1.endpoints import auth, courses, students, certificates, validate, classes, enrollments

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(classes.router, prefix="/classes", tags=["classes"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])
api_router.include_router(certificates.router, prefix="/certificates", tags=["certificates"])
api_router.include_router(validate.router, prefix="/validate", tags=["validate"])
