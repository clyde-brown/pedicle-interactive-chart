# 다음 할 일 — 마스터 데이터 검토 UI

## 목적

원장님이 DB에 적재된 마스터 데이터를 테이블별로 직접 눈으로 확인하고,
내용이 맞는지 / 빠진 게 있는지 / 수정이 필요한지 판단할 수 있도록
간단한 관리 화면을 만든다.

---

## 구현 범위

### 1. 백엔드 API (FastAPI)

기존 `app/main.py` 에 마스터 조회 라우터 추가.

| 엔드포인트 | 설명 |
|---|---|
| `GET /master/{table}` | 테이블명 지정 → 전체 행 반환 |
| `GET /master` | 조회 가능한 테이블 목록 반환 |

지원할 테이블 목록:
- `laterality`, `mst_value_scale`, `mst_body_part`, `mst_exam_item`
- `mst_neuro_level`, `mst_mmt_grade`, `mst_rom_reference`
- `mst_subjective_vocab`, `mst_red_flag`, `mst_imaging_finding`
- `mst_grading_scale`, `mst_outcome_scale`, `mst_peripheral_nerve`
- `map_alias`
- `rel_diagnosis_exam`, `rel_structure_exam`, `rel_part_diagnosis`

### 2. 프론트엔드 (HTML + Vanilla JS)

FastAPI 의 `StaticFiles` + Jinja2 템플릿 또는 단순 `index.html` 한 파일.
외부 JS 프레임워크 없이 구현해 배포 복잡도 최소화.

**화면 구성:**

```
┌─────────────────────────────────────────────────┐
│  Pedicle 마스터 데이터 검토                      │
├──────────────┬──────────────────────────────────┤
│ 테이블 목록  │  선택된 테이블 데이터             │
│              │                                   │
│ ○ laterality │  ┌────┬──────┬──────┐            │
│ ○ body_part  │  │ id │ name │ ...  │            │
│ ● exam_item  │  ├────┼──────┼──────┤            │
│ ○ neuro_lvl  │  │  1 │ ...  │ ...  │            │
│ ○ red_flag   │  │  2 │ ...  │ ...  │            │
│ ...          │  └────┴──────┴──────┘            │
│              │  총 133건                         │
└──────────────┴──────────────────────────────────┘
```

- 왼쪽: 테이블 선택 사이드바 (한글 이름 + 건수 표시)
- 오른쪽: 선택 테이블 전체 행을 스크롤 가능한 테이블로 표시
- 컬럼 헤더 클릭 → 정렬
- 검색창 → 클라이언트 사이드 필터링

### 3. 실행 방법

```bash
uvicorn app.main:app --reload
# http://localhost:8000/admin 접속
```

---

## 작업 순서

1. `app/routers/master.py` — 마스터 조회 라우터 작성
2. `app/main.py` — 라우터 등록, StaticFiles 마운트
3. `app/static/admin.html` — 단일 페이지 관리 UI
4. 로컬에서 원장님과 함께 화면 확인
5. 피드백 기반 데이터 수정 (`app/seed_master.py` 재실행 또는 직접 UPDATE)

---

## 원장님 검토 포인트

원장님이 각 테이블을 보면서 확인할 항목:

| 테이블 | 확인 포인트 |
|---|---|
| `mst_body_part` | 부위 계층 구조가 실제 차팅 단위와 맞는지 |
| `mst_exam_item` | 검사 항목이 빠진 건 없는지, 이름이 익숙한지 |
| `rel_diagnosis_exam` | 진단별 핵심 검사 매핑이 실제 진료와 일치하는지 |
| `rel_part_diagnosis` | 부위를 누르면 나올 예상 진단 목록이 적절한지 |
| `mst_red_flag` | 레드플래그 항목이 임상적으로 적합한지 |
| `mst_grading_scale` | 등급 척도(Kellgren-Lawrence 등)가 사용하는 것과 맞는지 |

---

## 이후 단계 (검토 완료 후)

- 수정/추가 반영 → seed_master.py 업데이트
- 인터랙티브 차트 UI 본 개발 착수 (body_part 트리 클릭 → 진단/검사 연동)
