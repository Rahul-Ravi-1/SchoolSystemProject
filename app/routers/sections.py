from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session

from ..database import get_session
from ..models import Section, SectionCreate, SectionRead, Course, Teacher

router = APIRouter()


@router.get("/", response_model=List[SectionRead])
def list_sections(course_id: Optional[int] = None, teacher_id: Optional[int] = None, session: Session = Depends(get_session)) -> List[Section]:
	query = select(Section)
	if course_id is not None:
		query = query.where(Section.course_id == course_id)
	if teacher_id is not None:
		query = query.where(Section.teacher_id == teacher_id)
	return session.exec(query).all()


@router.post("/", response_model=SectionRead, status_code=status.HTTP_201_CREATED)
def create_section(payload: SectionCreate, session: Session = Depends(get_session)) -> Section:
	course = session.get(Course, payload.course_id)
	teacher = session.get(Teacher, payload.teacher_id)
	if not course:
		raise HTTPException(status_code=404, detail="Course not found")
	if not teacher:
		raise HTTPException(status_code=404, detail="Teacher not found")
	section = Section(**payload.model_dump())
	session.add(section)
	session.commit()
	session.refresh(section)
	return section


@router.get("/{section_id}", response_model=SectionRead)
def get_section(section_id: int, session: Session = Depends(get_session)) -> Section:
	section = session.get(Section, section_id)
	if not section:
		raise HTTPException(status_code=404, detail="Section not found")
	return section


@router.patch("/{section_id}", response_model=SectionRead)
def update_section(section_id: int, payload: SectionCreate, session: Session = Depends(get_session)) -> Section:
	section = session.get(Section, section_id)
	if not section:
		raise HTTPException(status_code=404, detail="Section not found")
	for key, value in payload.model_dump(exclude_unset=True).items():
		setattr(section, key, value)
	session.add(section)
	session.commit()
	session.refresh(section)
	return section


@router.delete("/{section_id}", response_model=None, status_code=status.HTTP_200_OK)
def delete_section(section_id: int, session: Session = Depends(get_session)) -> dict:
	section = session.get(Section, section_id)
	if not section:
		raise HTTPException(status_code=404, detail="Section not found")
	session.delete(section)
	session.commit()
	return {"detail": "Section deleted"}

