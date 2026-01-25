from __future__ import annotations

from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship


class Subject(str, Enum):
	MATH = "Math"
	ENGLISH = "English"
	SOCIAL_SCIENCES = "Social Sciences"
	PE = "PE"


class StudentBase(SQLModel):
	first_name: str
	last_name: str
	email: str


class Student(StudentBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	password_hash: Optional[str] = Field(default=None, nullable=True)


class StudentRead(StudentBase):
	id: int


class StudentCreate(StudentBase):
	pass


class StudentUpdate(SQLModel):
	first_name: Optional[str] = None
	last_name: Optional[str] = None
	email: Optional[str] = None


class StudentLogin(SQLModel):
	student_id: int
	password: str


class TeacherLogin(SQLModel):
	teacher_id: int
	password: str


class TeacherBase(SQLModel):
	first_name: str
	last_name: str
	email: str
	subject: Subject


class Teacher(TeacherBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	password_hash: Optional[str] = Field(default=None, nullable=True)


class TeacherRead(TeacherBase):
	id: int


class TeacherCreate(TeacherBase):
	pass


class TeacherUpdate(SQLModel):
	first_name: Optional[str] = None
	last_name: Optional[str] = None
	email: Optional[str] = None
	subject: Optional[Subject] = None


class CourseBase(SQLModel):
	title: str
	description: Optional[str] = None


class Course(CourseBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)


class CourseRead(CourseBase):
	id: int


class CourseCreate(CourseBase):
	pass


class CourseUpdate(SQLModel):
	title: Optional[str] = None
	description: Optional[str] = None


class SectionBase(SQLModel):
	name: str
	capacity: Optional[int] = None


class Section(SectionBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	course_id: int = Field(foreign_key="course.id")
	teacher_id: int = Field(foreign_key="teacher.id")


class SectionRead(SectionBase):
	id: int
	course_id: int
	teacher_id: int


class SectionCreate(SectionBase):
	course_id: int
	teacher_id: int


class Enrollment(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	student_id: int = Field(foreign_key="student.id")
	section_id: int = Field(foreign_key="section.id")
	grade: Optional[str] = None


class StudentClassWithGrade(SQLModel):
	course_title: str
	section_name: str
	section_id: int
	teacher_name: str
	teacher_email: str
	grade: Optional[str] = None


class StudentInSection(SQLModel):
	"""Student with their enrollment and grade info for a specific section"""
	student_id: int
	enrollment_id: int
	first_name: str
	last_name: str
	email: str
	grade: Optional[str] = None


class Token(SQLModel):
	access_token: str
	token_type: str = "bearer"
