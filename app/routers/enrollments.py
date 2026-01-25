from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from pydantic import BaseModel

from ..database import get_session
from ..models import Enrollment, Student, Section, StudentInSection, Teacher
from .auth import get_current_teacher

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


@router.get("/section/{section_id}", response_model=List[StudentInSection])
def list_section_students(section_id: int, session: Session = Depends(get_session)) -> List[StudentInSection]:
	"""Get all students in a section along with their enrollment IDs and grades"""
	section = session.get(Section, section_id)
	if not section:
		raise HTTPException(status_code=404, detail="Section not found")
	
	enrollments = session.exec(select(Enrollment).where(Enrollment.section_id == section_id)).all()
	if not enrollments:
		return []
	
	student_ids = [e.student_id for e in enrollments]
	students = session.exec(select(Student).where(Student.id.in_(student_ids))).all()
	
	# Create lookup map
	student_map = {s.id: s for s in students}
	
	results: List[StudentInSection] = []
	for enrollment in enrollments:
		student = student_map.get(enrollment.student_id)
		if student:
			results.append(StudentInSection(
				student_id=student.id,  # type: ignore[arg-type]
				enrollment_id=enrollment.id,  # type: ignore[arg-type]
				first_name=student.first_name,
				last_name=student.last_name,
				email=student.email,
				grade=enrollment.grade
			))
	
	return results


class GradeUpdate(BaseModel):
	grade: Optional[str] = None


@router.patch("/{enrollment_id}/grade", response_model=Enrollment)
def update_enrollment_grade(
	enrollment_id: int,
	payload: GradeUpdate,
	current_teacher: Teacher = Depends(get_current_teacher),
	session: Session = Depends(get_session)
) -> Enrollment:
	"""Update the grade for a specific enrollment - TEACHERS ONLY"""
	enrollment = session.get(Enrollment, enrollment_id)
	if not enrollment:
		raise HTTPException(status_code=404, detail="Enrollment not found")
	
	# Security check: Verify teacher teaches this section
	section = session.get(Section, enrollment.section_id)
	if not section:
		raise HTTPException(status_code=404, detail="Section not found")
	
	if section.teacher_id != current_teacher.id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="You can only update grades for sections you teach"
		)
	
	enrollment.grade = payload.grade
	session.add(enrollment)
	session.commit()
	session.refresh(enrollment)
	return enrollment

