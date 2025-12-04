from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import students, teachers, courses, sections, enrollments, auth

app = FastAPI(title="School System API", version="0.3.0")

# Allow the frontend (opened from file:// or another origin) to call this API
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
	init_db()


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(students.router, prefix="/students", tags=["students"])
app.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
app.include_router(courses.router, prefix="/courses", tags=["courses"])
app.include_router(sections.router, prefix="/sections", tags=["sections"])
app.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])
