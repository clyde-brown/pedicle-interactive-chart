"""DB 연결 설정 (SQLAlchemy 2.0 + psycopg3)."""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://waonderboy@localhost:5432/pedicle",
)

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI 의존성 주입용 세션 제너레이터."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
