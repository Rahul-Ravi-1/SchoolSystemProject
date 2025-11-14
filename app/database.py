from __future__ import annotations

from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from pathlib import Path

DB_PATH = Path("./school.db").resolve()
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db() -> None:
	# Import models so SQLModel is aware before creating tables
	from . import models  # noqa: F401
	SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
	with Session(engine) as session:
		yield session

