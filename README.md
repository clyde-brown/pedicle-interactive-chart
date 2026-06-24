# pedicle-interactive-chart

정형외과 **자연어 차팅을 LLM으로 분석**해, 마스터 데이터(표준 용어)에 매핑하여 **SOAP 구조로 정규화·저장**하는 시스템.

## 개요

의사가 자유 텍스트로 작성한 차팅을 LLM(Claude)이 해석하고, 미리 구축한 마스터 데이터(표준어 사전)에 매핑하여 SOAP 구조의 정형 데이터로 변환한다. 즉 **자유 서술 → 표준화된 구조 데이터**.

```
자연어 차팅 (visit.charting)
      │  LLM 분석 · 표준어 매핑
      ▼
SOAP 구조화 (visit_ccf_s / o / a / p)
   S 주관적 증상   O 객관적 검진   A 진단   P 치료계획
```

## 데이터베이스

**마스터 데이터 (표준어 사전)**
- `mst_body_part` 신체부위 · `mst_exam_item` 검사항목 · `diagnosis` 진단(KCD) · `prescription` 처방
- `mst_*` 신경레벨·MMT·ROM·영상소견·red flag 등 룩업 + `map_alias` 약어·별칭 매핑
- `rel_*` 부위↔진단↔검사 연관관계

**방문 데이터**
- `patient` · `visit`(차팅 원문) · `visit_diagnosis` · `visit_prescription`

**CCF 구조화 결과 (SOAP)**
- `visit_ccf_s` 주관적 증상 (부위·양상·VAS 등)
- `visit_ccf_o` 객관적 검진 (검사/압통 표적)
- `visit_ccf_a` 진단 (확정/감별)
- `visit_ccf_p` 치료 계획 (약/주사/물리·시술)

## 기술 스택

Python · FastAPI · SQLAlchemy 2.0 · PostgreSQL 18 · Anthropic Claude API

## 실행

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경변수 (.env)
#   DATABASE_URL=postgresql+psycopg://<user>@localhost:5433/pedicle
#   ANTHROPIC_API_KEY=sk-ant-...

# 3. 마스터 데이터 적재 (워크북 → DB)
python -m app.seed_master

# 4. 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 8003
```
