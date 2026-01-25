from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session

from ..database import get_session
from ..models import (
	Student,
	StudentCreate,
	StudentRead,
	StudentUpdate,
	Enrollment,
	Section,
	Course,
	Teacher,
	StudentClassWithGrade,
)
from .auth import get_current_student
from ..security import get_password_hash
import secrets
import string

router = APIRouter()


@router.get("/", response_model=List[StudentRead])
def list_students(session: Session = Depends(get_session)) -> List[Student]:
	print("this is my debug statement: list_students", session)
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


@router.patch("/{student_id}", response_model=StudentRead)
def update_student(student_id: int, payload: StudentUpdate, session: Session = Depends(get_session)) -> Student:
	student = session.get(Student, student_id)
	if not student:
		raise HTTPException(status_code=404, detail="Student not found")
	update_data = payload.model_dump(exclude_unset=True)
	for key, value in update_data.items():
		setattr(student, key, value)
	session.add(student)
	session.commit()
	session.refresh(student)
	return student


@router.delete("/{student_id}", status_code=status.HTTP_200_OK)
def delete_student(student_id: int, session: Session = Depends(get_session)) -> dict:
	student = session.get(Student, student_id)
	if not student:
		raise HTTPException(status_code=404, detail="Student not found")
	session.delete(student)
	session.commit()
	return {"detail": "Student deleted"}


@router.get(
	"/by-id/{student_id}/classes-with-grades",
	response_model=List[StudentClassWithGrade],
)
def get_student_classes_with_grades(
	student_id: int, session: Session = Depends(get_session)
) -> List[StudentClassWithGrade]:
	student = session.get(Student, student_id)
	if not student:
		raise HTTPException(status_code=404, detail="Student not found")

	enrollments = session.exec(
		select(Enrollment).where(Enrollment.student_id == student_id)
	).all()
	if not enrollments:
		return []

	section_ids = [e.section_id for e in enrollments]
	sections = session.exec(
		select(Section).where(Section.id.in_(section_ids))
	).all()

	grade_by_section = {e.section_id: e.grade for e in enrollments}

	results: List[StudentClassWithGrade] = []
	for section in sections:
		course = session.get(Course, section.course_id)
		teacher = session.get(Teacher, section.teacher_id)

		if not course or not teacher:
			# Inconsistent data; skip this section instead of crashing
			continue

		results.append(
			StudentClassWithGrade(
				course_title=course.title,
				section_name=section.name,
				section_id=section.id,
				teacher_name=f"{teacher.first_name} {teacher.last_name}",
				teacher_email=teacher.email,
				grade=grade_by_section.get(section.id),
			)
		)

	return results


@router.get(
	"/me/classes-with-grades",
	response_model=List[StudentClassWithGrade],
)
def get_my_classes_with_grades(
	current_student: Student = Depends(get_current_student),
	session: Session = Depends(get_session),
) -> List[StudentClassWithGrade]:
	return get_student_classes_with_grades(
		student_id=current_student.id,  # type: ignore[arg-type]
		session=session,
	)
def generate_temp_password(length: int = 10) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))
@router.post("/{student_id}/reset-password")
def reset_student_password(student_id:int, session: Session = Depends(get_session), ) -> dict:
	student = session.get(Student, student_id)
	if not student:
		raise HTTPException(status_code=404, detail="Student not found")
	new_password = generate_temp_password()
	student.password_hash = get_password_hash(new_password)
	session.add(student)
	session.commit()
	session.refresh(student)
	return {
		"student_id": student.id,
		"new_password": new_password,
	}