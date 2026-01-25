from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlmodel import Session

from ..database import get_session
from ..models import Student, StudentLogin, Teacher, TeacherLogin, Token
from ..security import (
	ALGORITHM,
	SECRET_KEY,
	create_access_token,
	get_password_hash,
	verify_password,
)


router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=Token)
def student_login(
	payload: StudentLogin, session: Session = Depends(get_session)
) -> Token:
	student = session.get(Student, payload.student_id)
	if not student or not student.password_hash:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid credentials",
		)

	if not verify_password(payload.password, student.password_hash):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid credentials",
		)

	access_token_expires = timedelta(minutes=60)
	access_token = create_access_token(
		data={"sub": str(student.id), "role": "student"},
		expires_delta=access_token_expires,
	)
	return Token(access_token=access_token, token_type="bearer")


def get_current_student(
	credentials: HTTPAuthorizationCredentials = Depends(security),
	session: Session = Depends(get_session),
) -> Student:
	token = credentials.credentials
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
	)

	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		sub: str | None = payload.get("sub")
		role: str | None = payload.get("role")
		if sub is None or role != "student":
			raise credentials_exception
	except JWTError:
		raise credentials_exception

	try:
		student_id = int(sub)  # type: ignore[arg-type]
	except (TypeError, ValueError):
		raise credentials_exception

	student = session.get(Student, student_id)
	if not student:
		raise credentials_exception

	return student


@router.post("/teacher-login", response_model=Token)
def teacher_login(
	payload: TeacherLogin, session: Session = Depends(get_session)
) -> Token:
	teacher = session.get(Teacher, payload.teacher_id)
	if not teacher or not teacher.password_hash:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid credentials",
		)

	if not verify_password(payload.password, teacher.password_hash):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid credentials",
		)

	access_token_expires = timedelta(minutes=60)
	access_token = create_access_token(
		data={"sub": str(teacher.id), "role": "teacher"},
		expires_delta=access_token_expires,
	)
	return Token(access_token=access_token, token_type="bearer")


def get_current_teacher(
	credentials: HTTPAuthorizationCredentials = Depends(security),
	session: Session = Depends(get_session),
) -> Teacher:
	token = credentials.credentials
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
	)

	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		sub: str | None = payload.get("sub")
		role: str | None = payload.get("role")
		if sub is None or role != "teacher":
			raise credentials_exception
	except JWTError:
		raise credentials_exception

	try:
		teacher_id = int(sub)  # type: ignore[arg-type]
	except (TypeError, ValueError):
		raise credentials_exception

	teacher = session.get(Teacher, teacher_id)
	if not teacher:
		raise credentials_exception

	return teacher



