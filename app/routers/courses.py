from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session

from ..database import get_session
from ..models import Course, CourseCreate, CourseRead

router = APIRouter()


@router.get("/", response_model=List[CourseRead])
def list_courses(session: Session = Depends(get_session)) -> List[Course]:
	courses = session.exec(select(Course)).all()
	return courses


@router.post("/", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(payload: CourseCreate, session: Session = Depends(get_session)) -> Course:
	course = Course(**payload.model_dump())
	session.add(course)
	session.commit()
	session.refresh(course)
	return course


@router.get("/{course_id}", response_model=CourseRead)
def get_course(course_id: int, session: Session = Depends(get_session)) -> Course:
	course = session.get(Course, course_id)
	if not course:
		raise HTTPException(status_code=404, detail="Course not found")
	return course

