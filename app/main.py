from __future__ import annotations

from fastapi import FastAPI
from .database import init_db
from .routers import students, teachers, courses
from .routers import sections, enrollments

app = FastAPI(title="School System API", version="0.2.0")


@app.on_event("startup")
def on_startup() -> None:
	init_db()


app.include_router(students.router, prefix="/students", tags=["students"])
app.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
app.include_router(courses.router, prefix="/courses", tags=["courses"])
app.include_router(sections.router, prefix="/sections", tags=["sections"])
app.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])
