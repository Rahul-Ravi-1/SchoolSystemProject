from __future__ import annotations

from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import Mapped


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
	enrollments: Mapped[List["Enrollment"]] = Relationship(back_populates="student")


class StudentRead(StudentBase):
	id: int


class StudentCreate(StudentBase):
	pass


class TeacherBase(SQLModel):
	first_name: str
	last_name: str
	email: str
	subject: Subject


class Teacher(TeacherBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	sections: Mapped[List["Section"]] = Relationship(back_populates="teacher")


class TeacherRead(TeacherBase):
	id: int


class TeacherCreate(TeacherBase):
	pass


class CourseBase(SQLModel):
	title: str
	description: Optional[str] = None


class Course(CourseBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	sections: Mapped[List["Section"]] = Relationship(back_populates="course")


class CourseRead(CourseBase):
	id: int


class CourseCreate(CourseBase):
	pass


class SectionBase(SQLModel):
	name: str
	capacity: Optional[int] = None


class Section(SectionBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	course_id: int = Field(foreign_key="course.id")
	teacher_id: int = Field(foreign_key="teacher.id")

	course: Mapped[Optional["Course"]] = Relationship(back_populates="sections")
	teacher: Mapped[Optional["Teacher"]] = Relationship(back_populates="sections")
	enrollments: Mapped[List["Enrollment"]] = Relationship(back_populates="section")


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

	student: Mapped[Optional["Student"]] = Relationship(back_populates="enrollments")
	section: Mapped[Optional["Section"]] = Relationship(back_populates="enrollments")
