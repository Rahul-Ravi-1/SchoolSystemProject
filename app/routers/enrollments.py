from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session

from ..database import get_session
from ..models import Enrollment, Student, Section

router = APIRouter()


@router.post("/", response_model=Enrollment, status_code=status.HTTP_201_CREATED)
def enroll_student(student_id: int, section_id: int, session: Session = Depends(get_session)) -> Enrollment:
	student = session.get(Student, student_id)
	section = session.get(Section, section_id)
	if not student:
		raise HTTPException(status_code=404, detail="Student not found")
	if not section:
		raise HTTPException(status_code=404, detail="Section not found")
	# prevent duplicate
	exists = session.exec(select(Enrollment).where(Enrollment.student_id == student_id, Enrollment.section_id == section_id)).first()
	if exists:
		raise HTTPException(status_code=400, detail="Student already enrolled in this section")
	enrollment = Enrollment(student_id=student_id, section_id=section_id)
	session.add(enrollment)
	session.commit()
	session.refresh(enrollment)
	return enrollment


@router.delete("/{enrollment_id}", response_model=None, status_code=status.HTTP_200_OK)
def unenroll(enrollment_id: int, session: Session = Depends(get_session)) -> dict:
	enrollment = session.get(Enrollment, enrollment_id)
	if not enrollment:
		raise HTTPException(status_code=404, detail="Enrollment not found")
	session.delete(enrollment)
	session.commit()
	return {"detail": "Enrollment deleted"}


@router.get("/student/{student_id}", response_model=List[Section])
def list_student_sections(student_id: int, session: Session = Depends(get_session)) -> List[Section]:
	student = session.get(Student, student_id)
	if not student:
		raise HTTPException(status_code=404, detail="Student not found")
	enrollments = session.exec(select(Enrollment).where(Enrollment.student_id == student_id)).all()
	section_ids = [e.section_id for e in enrollments]
	if not section_ids:
		return []
	sections = session.exec(select(Section).where(Section.id.in_(section_ids))).all()
	return sections


@router.get("/section/{section_id}", response_model=List[Student])
def list_section_students(section_id: int, session: Session = Depends(get_session)) -> List[Student]:
	section = session.get(Section, section_id)
	if not section:
		raise HTTPException(status_code=404, detail="Section not found")
	enrollments = session.exec(select(Enrollment).where(Enrollment.section_id == section_id)).all()
	student_ids = [e.student_id for e in enrollments]
	if not student_ids:
		return []
	students = session.exec(select(Student).where(Student.id.in_(student_ids))).all()
	return students

