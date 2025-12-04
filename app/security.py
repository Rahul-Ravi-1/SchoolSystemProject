from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import jwt
from passlib.context import CryptContext


# In a real app, move these to environment variables
SECRET_KEY = "change-me-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, password_hash: str) -> bool:
	return pwd_context.verify(plain_password, password_hash)


def get_password_hash(password: str) -> str:
	return pwd_context.hash(password)


def create_access_token(
	data: Dict[str, Any],
	expires_delta: timedelta | None = None,
) -> str:
	to_encode = data.copy()
	now = datetime.now(timezone.utc)
	if expires_delta is None:
		expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	expire = now + expires_delta
	to_encode.update({"exp": expire, "iat": now})
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt



