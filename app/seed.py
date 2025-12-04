from __future__ import annotations

from typing import List
import random

from sqlmodel import Session, select

from .database import engine
from .models import Course, Teacher, Section, Subject, Student, Enrollment
from .security import get_password_hash

FIRST_NAMES = [
	"Ava", "Liam", "Emma", "Noah", "Olivia", "Elijah", "Sophia", "Lucas", "Isabella", "Mason",
	"Mia", "Ethan", "Amelia", "Logan", "Harper", "James", "Evelyn", "Benjamin", "Abigail", "Jacob",
]
LAST_NAMES = [
	"Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
	"Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
]

SUBJECTS: List[Subject] = [Subject.MATH, Subject.ENGLISH, Subject.SOCIAL_SCIENCES, Subject.PE]


def seed() -> None:
	from .database import init_db
	init_db()  # Ensure tables exist
	
	with Session(engine) as session:
		# Courses
		course_by_subject = {}
		for subj in SUBJECTS:
			existing = session.exec(select(Course).where(Course.title == subj.value)).first()
			if existing:
				course_obj = existing
			else:
				course_obj = Course(title=subj.value, description=f"Core {subj.value} course")
				session.add(course_obj)
				session.commit()
				session.refresh(course_obj)
			course_by_subject[subj] = course_obj

		# Teachers (20 total, 5 per subject)
		teachers: List[Teacher] = []
		name_pairs = list(zip(FIRST_NAMES, LAST_NAMES))
		idx = 0
		for subj in SUBJECTS:
			for _ in range(5):
				first, last = name_pairs[idx % len(name_pairs)]
				email = f"{first.lower()}.{last.lower()}@school.edu"
				# Ensure unique email
				if session.exec(select(Teacher).where(Teacher.email == email)).first():
					idx += 1
					continue
				teacher = Teacher(first_name=first, last_name=last, email=email, subject=subj)
				session.add(teacher)
				session.commit()
				session.refresh(teacher)
				teachers.append(teacher)
				idx += 1

		# Sections: 3 per teacher for their course
		for teacher in teachers:
			course = course_by_subject[teacher.subject]
			for n in range(1, 4):
				name = f"{teacher.subject.value} Sec {n} (T{teacher.id})"
				# Avoid duplicates if re-seeding
				if session.exec(
					select(Section).where(
						Section.name == name, Section.teacher_id == teacher.id
					)
				).first():
					continue
				section = Section(name=name, capacity=30, course_id=course.id, teacher_id=teacher.id)
				session.add(section)
				session.commit()

		# Students: create ~100 demo students
		existing_students = session.exec(select(Student)).all()
		if not existing_students:
			idx = 0
			for i in range(100):
				first = FIRST_NAMES[idx % len(FIRST_NAMES)]
				last = LAST_NAMES[idx % len(LAST_NAMES)]
				idx += 1
				email = f"{first.lower()}.{last.lower()}{i}@example.com"
				# Just in case, skip duplicates
				if session.exec(select(Student).where(Student.email == email)).first():
					continue
				# For demo purposes, all seeded students share the same password.
				# Plain-text password: "student123"
				student = Student(
					first_name=first,
					last_name=last,
					email=email,
					password_hash=get_password_hash("student123"),
				)
				session.add(student)
				session.commit()

		# Enrollments: enroll each student in a few random sections
		all_students = session.exec(select(Student)).all()
		all_sections = session.exec(select(Section)).all()

		if all_students and all_sections:
			for student in all_students:
				# 2–4 random sections per student (no duplicates)
				k = min(len(all_sections), random.randint(2, 4))
				for section in random.sample(all_sections, k=k):
					# Skip if this enrollment already exists
					exists = session.exec(
						select(Enrollment).where(
							Enrollment.student_id == student.id,
							Enrollment.section_id == section.id,
						)
					).first()
					if exists:
						continue
					grade = random.choice(["A", "B", "C", "D", None])
					enrollment = Enrollment(
						student_id=student.id,
						section_id=section.id,
						grade=grade,
					)
					session.add(enrollment)
				session.commit()


if __name__ == "__main__":
	from app.database import init_db
	init_db()
	seed()
