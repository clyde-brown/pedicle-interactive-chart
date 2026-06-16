"""visit_timeline.csv → 스타 스키마 적재 ETL.

실행: python -m app.seed [csv경로]
정규표현식으로 진단/처방을 유니크하게 추출해 차원 테이블에 저장하고,
visit(팩트) + 브릿지 테이블을 채운다.
"""
from __future__ import annotations

import re
import sys

import pandas as pd
from sqlalchemy import insert

from app.db import Base, SessionLocal, engine
from app.models import (
    Diagnosis,
    Patient,
    Prescription,
    Visit,
    VisitDiagnosis,
    VisitPrescription,
)

# 진단 항목: 'KCD코드 + 진단명'.  코드는 영문+숫자+밑줄(M2496_KNEE 등) 허용.
DX_RE = re.compile(r'^([A-Z][A-Z0-9_]*)\s+(.*)$')
DX_SEP = " / "
RX_SEP = re.compile(r",\s")  # 처방 구분자: 콤마+공백 (내부 콤마는 공백 없음)


def parse_diagnoses(cell: str) -> list[tuple[str, str]]:
    """진단목록 셀 → [(code, name), ...]."""
    out = []
    if not cell:
        return out
    for item in cell.split(DX_SEP):
        item = item.strip()
        if not item:
            continue
        m = DX_RE.match(item)
        if m:
            code = m.group(1)
            name = m.group(2).strip().strip('"').strip()
        else:  # 코드 패턴 미스 → 항목 전체를 코드로 (희소)
            code, name = item, item
        out.append((code, name))
    return out


def parse_prescriptions(cell: str) -> list[str]:
    """처방목록 셀 → [name, ...] (절단된 원본 이름 기준)."""
    if not cell:
        return []
    return [x.strip() for x in RX_SEP.split(cell) if x.strip()]


def run(csv_path: str = "visit_timeline.csv") -> None:
    df = pd.read_csv(csv_path, encoding="utf-8-sig", dtype=str).fillna("")
    print(f"읽은 행: {len(df)}")

    # 스키마 초기화 (재실행 가능하게 drop & create)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # --- 1차 패스: 차원 유니크 수집 ---
    patients: dict[str, str] = {}        # 환자번호 -> 환자명
    diagnoses: dict[str, str] = {}       # code -> name
    rx_names: set[str] = set()           # 처방명

    parsed_rows = []
    for r in df.itertuples(index=False):
        d = r._asdict() if hasattr(r, "_asdict") else None
        # 컬럼명에 특수문자(·)가 있어 위치 인덱스로 접근
        pno, pname, vdate, rno, rtype, charting, dx_cell, rx_cell, dxn, rxn = r

        patients.setdefault(pno, pname)
        dx_list = parse_diagnoses(dx_cell)
        rx_list = parse_prescriptions(rx_cell)
        for code, name in dx_list:
            diagnoses.setdefault(code, name)
        rx_names.update(rx_list)
        parsed_rows.append((pno, vdate, rno, rtype, charting, dxn, rxn, dx_list, rx_list))

    print(f"유니크 환자: {len(patients)}, 진단: {len(diagnoses)}, 처방: {len(rx_names)}")

    db = SessionLocal()
    try:
        # --- 차원 적재 ---
        db.execute(insert(Patient), [{"patient_no": k, "name": v} for k, v in patients.items()])
        db.execute(insert(Diagnosis), [{"code": k, "name": v} for k, v in diagnoses.items()])
        db.execute(insert(Prescription), [{"name": n} for n in sorted(rx_names)])
        db.commit()

        rx_id = {row.name: row.id for row in db.query(Prescription).all()}

        # --- 팩트 + 브릿지 적재 ---
        visit_rows, vd_rows, vp_rows = [], [], []
        for i, (pno, vdate, rno, rtype, charting, dxn, rxn, dx_list, rx_list) in enumerate(parsed_rows, start=1):
            visit_rows.append({
                "id": i, "patient_no": pno, "visit_date": vdate, "receipt_no": rno,
                "receipt_type": rtype, "charting": charting,
                "dx_count": int(dxn or 0), "rx_count": int(rxn or 0),
            })
            for code, _ in {(c, n) for c, n in dx_list}:  # visit 내 코드 중복 제거
                vd_rows.append({"visit_id": i, "diagnosis_code": code})
            for name in set(rx_list):
                vp_rows.append({"visit_id": i, "prescription_id": rx_id[name]})

        db.execute(insert(Visit), visit_rows)
        if vd_rows:
            db.execute(insert(VisitDiagnosis), vd_rows)
        if vp_rows:
            db.execute(insert(VisitPrescription), vp_rows)
        db.commit()
        print(f"적재 완료 — visit: {len(visit_rows)}, visit_diagnosis: {len(vd_rows)}, visit_prescription: {len(vp_rows)}")
    finally:
        db.close()


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "visit_timeline.csv")
