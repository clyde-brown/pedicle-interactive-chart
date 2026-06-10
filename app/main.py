"""Pedicle interactive chart - FastAPI 진입점."""
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

app = FastAPI(title="Pedicle Interactive Chart")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    """DB 연결 확인."""
    one = db.execute(text("SELECT 1")).scalar_one()
    return {"db": "ok", "result": one}
