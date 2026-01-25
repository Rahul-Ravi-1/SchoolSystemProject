from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session

from ..database import get_session
from ..models import Teacher, TeacherCreate, TeacherRead, TeacherUpdate, Section, SectionRead
from .auth import get_current_teacher

router = APIRouter()


@router.get("/", response_model=List[TeacherRead])
def list_teachers(session: Session = Depends(get_session)) -> List[Teacher]:
	teachers = session.exec(select(Teacher)).all()
	return teachers


@router.post("/", response_model=TeacherRead, status_code=status.HTTP_201_CREATED)
def create_teacher(payload: TeacherCreate, session: Session = Depends(get_session)) -> Teacher:
	teacher = Teacher(**payload.model_dump())
	session.add(teacher)
	session.commit()
	session.refresh(teacher)
	return teacher


@router.get("/{teacher_id}", response_model=TeacherRead)
def get_teacher(teacher_id: int, session: Session = Depends(get_session)) -> Teacher:
	teacher = session.get(Teacher, teacher_id)
	if not teacher:
		raise HTTPException(status_code=404, detail="Teacher not found")
	return teacher


@router.patch("/{teacher_id}", response_model=TeacherRead)
def update_teacher(teacher_id: int, payload: TeacherUpdate, session: Session = Depends(get_session)) -> Teacher:
	teacher = session.get(Teacher, teacher_id)
	if not teacher:
		raise HTTPException(status_code=404, detail="Teacher not found")
	update_data = payload.model_dump(exclude_unset=True)
	for key, value in update_data.items():
		setattr(teacher, key, value)
	session.add(teacher)
	session.commit()
	session.refresh(teacher)
	return teacher


@router.delete("/{teacher_id}", status_code=status.HTTP_200_OK)
def delete_teacher(teacher_id: int, session: Session = Depends(get_session)) -> dict:
	teacher = session.get(Teacher, teacher_id)
	if not teacher:
		raise HTTPException(status_code=404, detail="Teacher not found")
	session.delete(teacher)
	session.commit()
	return {"detail": "Teacher deleted"}


@router.get("/me/sections", response_model=List[SectionRead])
def get_my_sections(
	current_teacher: Teacher = Depends(get_current_teacher),
	session: Session = Depends(get_session)
) -> List[Section]:
	"""Get all sections for the currently logged-in teacher"""
	sections = session.exec(
		select(Section).where(Section.teacher_id == current_teacher.id)
	).all()
	return list(sections)