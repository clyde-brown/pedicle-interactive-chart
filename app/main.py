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


@app.get("/visits")
def visits(
    patient_no: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """v_visit_timeline 뷰 조회 — visit_timeline.csv 형태로 반환.

    patient_no 지정 시 해당 환자만 필터링.
    """
    where = 'WHERE "환자번호" = :pno' if patient_no else ""
    sql = text(
        f'SELECT * FROM v_visit_timeline {where} '
        "ORDER BY \"환자번호\", \"내원일\", \"접수번호\" "
        "LIMIT :limit OFFSET :offset"
    )
    params = {"limit": limit, "offset": offset}
    if patient_no:
        params["pno"] = patient_no
    rows = db.execute(sql, params).mappings().all()
    return {"count": len(rows), "rows": [dict(r) for r in rows]}
