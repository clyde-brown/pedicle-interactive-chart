# CCF 마스터 스키마 정의서

> **DB**: PostgreSQL (로컬 homebrew postgresql@18)
> **범위**: 기존 star schema(`patient/diagnosis/prescription/visit`) 위에 얹은 **CCF SOAP 구조화 레이어**
> **DDL**: `app/sql/ccf_master_schema.sql` (데이터 미적재 — 테이블·관계만)
> **설계 근거**: [[CCF_master_table_strategy_2026-06-10]] / [[CCF_extraction_PoC_result_2026-06-10]]
> **상태**: 2026-06-10 로컬 DB 적용 완료 (13개 테이블, FK 22개, 전부 빈 상태)

---

## 0. 레이어 구조

```
[기존 star schema]                [CCF 레이어 — 본 정의서]
patient                           laterality        (T2 lookup)
diagnosis   ──(T3 재사용)──┐      mst_value_scale   (T6 lookup)
prescription──(T4 재사용)──┤      mst_body_part     (T1 셀프계층)
visit       ──(부모)───────┤      mst_exam_item     (T5)
visit_diagnosis            │      map_alias         (G1 사전)
visit_prescription         │      rel_*  × 4        (연관/지식그래프)
                           └────  visit_ccf_s/o/a/p (방문결과/인스턴스)
```

- **마스터(`mst_*`,`laterality`)** = 어휘·구조 고정
- **연관(`rel_*`)** = 마스터 사이 임상 지식 (M:N 엣지)
- **방문결과(`visit_ccf_*`)** = 차팅 추출 인스턴스 (마스터 FK + 실제 값)
- **사전(`map_alias`)** = 표기 변이 정규화
- `diagnosis`/`prescription`은 **신규 생성 안 함** — 기존 테이블에 컬럼만 보강(§1).

---

## 1. 기존 마스터 보강 (재사용)

신규 생성 대신 `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`로 컬럼만 추가.

### `diagnosis` (= T3 진단 마스터, KCD-8)
| 컬럼 | 타입 | 설명 |
|---|---|---|
| `code` (PK) | varchar | KCD 코드 *(기존)* |
| `name` | varchar | 진단명 *(기존)* |
| `category` | varchar(32) | **추가** — 코드접두 분류(근골격/손상/소화기…) |
| `freq` | integer | **추가** — 데이터 등장 빈도 |

### `prescription` (= T4 처방·시술 마스터)
| 컬럼 | 타입 | 설명 |
|---|---|---|
| `id` (PK) | integer | *(기존)* |
| `name` | varchar | 오더명(원본 절삭형) *(기존)* |
| `order_type` | varchar(16) | **추가** — 약/주사/물리·시술/영상/진찰료 |
| `medfee_cd` | varchar(32) | **추가** — 심평원 수가코드 (절삭 복원 키) |
| `freq` | integer | **추가** — 빈도 |

---

## 2. 마스터 테이블

### 2.1 `laterality` — 측 lookup (T2)
| 컬럼 | 타입 | 설명 |
|---|---|---|
| `code` (PK) | char(1) | L / R / B / C |
| `label` | varchar(8) | 좌 / 우 / 양측 / 중앙 |
> 좌/우는 부위의 자식이 아니라 **직교 축** → 계층 미포함, 별도 lookup.

### 2.2 `mst_value_scale` — 검사값 척도 lookup (T6)
| 컬럼 | 타입 | 설명 |
|---|---|---|
| `value_type` (PK) | varchar(16) | `+/-`,`+/+`,`각도/각도`,`grade(v/v)`,`%/%`,`+/++/+++`,`거리(m)` |
| `pattern` | varchar(64) | 표기 형식 |
| `example` | varchar(64) | 예: `45/full`, `(100%/30%)` |

### 2.3 `mst_body_part` — 부위 계층 (T1, **셀프계층 adjacency list**)
| 컬럼 | 타입 | 설명 |
|---|---|---|
| `id` (PK) | integer IDENTITY | 노드 고유 |
| `parent_id` (FK→self) | integer | 상위 노드, 루트=NULL **(1:N, N단 깊이)** |
| `name` | varchar(64) | 노드명 |
| `node_type` | varchar(16) CHECK | `부위`/`영역`/`레벨`/`구조물` |
| `name_en` | varchar(64) | 영문 |
- **인덱스**: `ix_body_part_parent(parent_id)`
- 부위마다 깊이 가변 흡수(무릎=구조물 깊이 / 허리=레벨 깊이).

### 2.4 `mst_exam_item` — 검진 카탈로그 (T5)
| 컬럼 | 타입 | 설명 |
|---|---|---|
| `item_id` (PK) | integer IDENTITY | |
| `category` | varchar(16) CHECK | `gross`/`special_test`/`motor`/`sensory`/`reflex` |
| `name` | varchar(128) | 검사명 (Mcmurray, SLR…) |
| `target_part` (FK→mst_body_part) | integer | 적용 부위 |
| `target_node` (FK→mst_body_part) | integer | 표적 구조물/레벨 (NULL 허용) |
| `value_type` (FK→mst_value_scale) | varchar(16) | 값 척도 |
> **tenderness(압통)는 여기 없음** — `mst_body_part` 노드를 직접 참조(`visit_ccf_o.node_id`)하여 어휘 중복 제거.

### 2.5 `map_alias` — 표기 변이 통합 사전 (G1, **다형 참조**)
| 컬럼 | 타입 | 설명 |
|---|---|---|
| `surface` (PK) | varchar(128) | 표면 표기 (오십견, Lt, Mc, 절삭형…) |
| `canonical_id` | varchar(64) | 표준 코드/노드 id |
| `target_table` | varchar(32) CHECK | `mst_diagnosis`/`mst_order`/`mst_exam_item`/`mst_body_part`/`laterality` |
| `alias_type` | varchar(16) CHECK | 동의어/약어/약식/절삭/brand |
| `source` | varchar(8) CHECK | std(범용) / learned(데이터) |
| `confidence` | real | 0.0~1.0 |
> `canonical_id`는 가리키는 테이블이 `target_table`에 따라 달라 **단일 FK 미설정(의도된 polymorphic)**. 무결성은 애플리케이션/검증 레이어 책임.

---

## 3. 연관 테이블 (`rel_*`) — 임상 지식 그래프 (M:N)

### 3.1 `rel_part_diagnosis` — 부위 ↔ 진단
| 컬럼 | 타입 | 설명 |
|---|---|---|
| `body_part_id` (PK,FK) | integer | → mst_body_part |
| `diagnosis_code` (PK,FK) | varchar | → diagnosis |
| `support` | real | 동시출현 비율 |

### 3.2 `rel_diagnosis_exam` — 진단 ↔ 검사 *(CCF PDF, 범용)*
| 컬럼 | 타입 | 설명 |
|---|---|---|
| `diagnosis_code` (PK,FK) | varchar | → diagnosis |
| `item_id` (PK,FK) | integer | → mst_exam_item |
| `source` | varchar(8) | std/learned |
> 차팅 누락 알림의 근거 (예: HNP인데 SLR 미기재).

### 3.3 `rel_diagnosis_order` — 진단 ↔ 처방 *(데이터 채굴, 병원 고유)*
| 컬럼 | 타입 | 설명 |
|---|---|---|
| `diagnosis_code` (PK,FK) | varchar | → diagnosis |
| `prescription_id` (PK,FK) | integer | → prescription |
| `support` | real | co-occurrence (예: S3350→심층열치료 0.73) |
> 청구 적정성 검증·처방 패턴 분석의 근거.

### 3.4 `rel_structure_exam` — 구조물/레벨 ↔ 검사
| 컬럼 | 타입 | 설명 |
|---|---|---|
| `node_id` (PK,FK) | integer | → mst_body_part |
| `item_id` (PK,FK) | integer | → mst_exam_item |
> 예: Meniscus → Mcmurray test.

---

## 4. 방문결과 테이블 (`visit_ccf_*`) — 추출 인스턴스

> 전부 `visit(id)`의 자식. S=1:1, O/A/P=1:N. 마스터 FK + 실제 값 저장. 모두 `ix_ccf_*_visit(visit_id)` 인덱스 보유.

### 4.1 `visit_ccf_s` — Subjective
| 컬럼 | 타입 | 설명 |
|---|---|---|
| `id` (PK) | integer IDENTITY | |
| `visit_id` (FK→visit) | integer | 내원 |
| `body_part_id` (FK→mst_body_part) | integer | 부위 |
| `laterality` (FK→laterality) | char(1) | 측 |
| `sub_region` | varchar(64) | 세부부위 원문 |
| `onset` | varchar(64) | 발병 시기 |
| `mechanism` | varchar(255) | 발병/유발 경위 |
| `pain_quality` | varchar(64) | 통증 양상 |
| `vas` | varchar(16) | 통증 강도 |
| `aggravating` | varchar(255) | 악화 요인 |
| `chief_complaint` | text | 주호소 요약 |

### 4.2 `visit_ccf_o` — Objective
| 컬럼 | 타입 | 설명 |
|---|---|---|
| `id` (PK) | integer IDENTITY | |
| `visit_id` (FK→visit) | integer | |
| `category` | varchar(16) CHECK | gross/special_test/motor/sensory/reflex/**tenderness**/imaging |
| `item_id` (FK→mst_exam_item) | integer | 검사 항목 (있으면) |
| `node_id` (FK→mst_body_part) | integer | 압통/표적 구조물 (있으면) |
| `result` | varchar(64) | `+/-`, `45/full`, `v/v` … |
| `raw_text` | varchar(255) | 원문 보존 |

### 4.3 `visit_ccf_a` — Assessment
| 컬럼 | 타입 | 설명 |
|---|---|---|
| `id` (PK) | integer IDENTITY | |
| `visit_id` (FK→visit) | integer | |
| `diagnosis_code` (FK→diagnosis) | varchar | KCD (미분류 시 NULL) |
| `dx_text` | varchar(255) | 진단명 원문 |
| `status` | varchar(16) CHECK | confirmed / r/o / '' |

### 4.4 `visit_ccf_p` — Plan
| 컬럼 | 타입 | 설명 |
|---|---|---|
| `id` (PK) | integer IDENTITY | |
| `visit_id` (FK→visit) | integer | |
| `order_type` | varchar(16) | 약/주사/물리·시술/영상계획 |
| `prescription_id` (FK→prescription) | integer | 오더 (미매핑 시 NULL) |
| `detail` | varchar(255) | 상세 (예: L4-5-S1 Lt) |
| `followup` | varchar(64) | 추적 (FU 1wk) |

---

## 5. 관계 요약 (FK 22개)

```
mst_body_part.parent_id      → mst_body_part.id      (셀프계층 1:N)
mst_exam_item.target_part    → mst_body_part.id
mst_exam_item.target_node    → mst_body_part.id
mst_exam_item.value_type     → mst_value_scale.value_type

rel_part_diagnosis           → mst_body_part / diagnosis
rel_diagnosis_exam           → diagnosis / mst_exam_item
rel_diagnosis_order          → diagnosis / prescription
rel_structure_exam           → mst_body_part / mst_exam_item

visit_ccf_s                  → visit / mst_body_part / laterality
visit_ccf_o                  → visit / mst_exam_item / mst_body_part
visit_ccf_a                  → visit / diagnosis
visit_ccf_p                  → visit / prescription
```
> ERD 다이어그램: [[CCF_master_table_strategy_2026-06-10]] §5

---

## 6. 데이터 적재 순서 (향후)

> 본 정의서는 **구조만**. 적재는 별도. 권장 순서(FK 의존성):

1. `laterality`, `mst_value_scale` — 고정 lookup 수기/시드
2. `diagnosis.category/freq`, `prescription.order_type/freq` — `visit_timeline.csv`에서 자동 채굴
3. `mst_body_part`, `mst_exam_item` — CCF PDF에서 추출
4. `map_alias` — 차팅 추출 부산물 + 큐레이션
5. `rel_diagnosis_order` — 방문 co-occurrence 집계 / `rel_diagnosis_exam` — PDF
6. `visit_ccf_*` — 차팅 LLM 추출 결과(`poc/ccf_extracted.json` 형태) 적재

---

## 7. 주의사항

1. **데이터 미적재**: 모든 CCF 테이블 현재 0행 (구조만 생성).
2. **`map_alias` 다형 참조**: `canonical_id`에 DB FK 없음 → 적재·검증 시 `target_table` 기준 무결성 확인 필요.
3. **`diagnosis`/`prescription` 공유**: 기존 star schema와 같은 테이블 사용 → CCF가 기존 데이터(KCD·오더)를 그대로 마스터로 활용.
4. **tenderness 비대칭**: O섹션에서 압통은 `mst_exam_item`이 아니라 `mst_body_part` 노드(`node_id`)를 가리킴.
5. **IDENTITY PK**: 신규 테이블은 `GENERATED ALWAYS AS IDENTITY` (PG10+). 기존 `visit` 등은 SQLAlchemy autoincrement.
