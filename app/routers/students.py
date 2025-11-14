from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session

from ..database import get_session
from ..models import Student, StudentCreate, StudentRead

router = APIRouter()


@router.get("/", response_model=List[StudentRead])
def list_students(session: Session = Depends(get_session)) -> List[Student]:
	students = session.exec(select(Student)).all()
	return students


@router.post("/", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate, session: Session = Depends(get_session)) -> Student:
	try:
		student = Student(**payload.model_dump())
		session.add(student)
		session.commit()
		session.refresh(student)
		return student
	except Exception as e:
		session.rollback()
		raise HTTPException(status_code=500, detail=f"Error creating student: {str(e)}")


@router.get("/{student_id}", response_model=StudentRead)
def get_student(student_id: int, session: Session = Depends(get_session)) -> Student:
	student = session.get(Student, student_id)
	if not student:
		raise HTTPException(status_code=404, detail="Student not found")
	return student
