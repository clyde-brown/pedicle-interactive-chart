"""스타 스키마 모델 (SQLAlchemy 2.0).

차원: patient, diagnosis, prescription
팩트: visit (증상·차팅 중앙 테이블)
브릿지: visit_diagnosis, visit_prescription (M:N)
"""
from __future__ import annotations

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Patient(Base):
    __tablename__ = "patient"

    patient_no: Mapped[str] = mapped_column(String(32), primary_key=True)  # 환자번호
    name: Mapped[str] = mapped_column(String(64))                          # 환자명 (중복 가능)

    visits: Mapped[list["Visit"]] = relationship(back_populates="patient")


class Diagnosis(Base):
    __tablename__ = "diagnosis"

    code: Mapped[str] = mapped_column(String(32), primary_key=True)  # KCD 코드
    name: Mapped[str] = mapped_column(String(255))                   # 진단명


class Prescription(Base):
    __tablename__ = "prescription"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)  # 처방명(원본에서 절단됨)


class Visit(Base):
    """증상·차팅 중앙(팩트) 테이블 — 1행 = 1회 내원."""

    __tablename__ = "visit"
    __table_args__ = (
        UniqueConstraint("patient_no", "visit_date", "receipt_no", name="uq_visit_natural"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_no: Mapped[str] = mapped_column(ForeignKey("patient.patient_no"), index=True)
    visit_date: Mapped[str] = mapped_column(String(32))   # 내원일
    receipt_no: Mapped[str] = mapped_column(String(32))   # 접수번호
    receipt_type: Mapped[str] = mapped_column(String(32))  # 접수구분
    charting: Mapped[str] = mapped_column(Text)            # 증상·차팅
    dx_count: Mapped[int] = mapped_column(Integer, default=0)  # 진단수
    rx_count: Mapped[int] = mapped_column(Integer, default=0)  # 처방수

    patient: Mapped["Patient"] = relationship(back_populates="visits")


class VisitDiagnosis(Base):
    __tablename__ = "visit_diagnosis"

    visit_id: Mapped[int] = mapped_column(ForeignKey("visit.id"), primary_key=True)
    diagnosis_code: Mapped[str] = mapped_column(ForeignKey("diagnosis.code"), primary_key=True)


class VisitPrescription(Base):
    __tablename__ = "visit_prescription"

    visit_id: Mapped[int] = mapped_column(ForeignKey("visit.id"), primary_key=True)
    prescription_id: Mapped[int] = mapped_column(ForeignKey("prescription.id"), primary_key=True)
