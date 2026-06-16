-- =====================================================================
-- CCF 마스터 스키마 (DDL only — 데이터 미적재)
-- PostgreSQL. 기존 star schema(patient/diagnosis/prescription/visit) 위에
-- CCF SOAP 구조화 레이어(마스터 + 연관 + 방문결과)를 얹는다.
--
-- 적용:  psql "$DATABASE_URL" -f app/sql/ccf_master_schema.sql
-- 정의서: docs/2_ccf_master_schema_definition.md
-- 설계:   docs/CCF_master_table_strategy_2026-06-10.md
-- =====================================================================

-- ---------------------------------------------------------------------
-- 0. 기존 마스터 보강 (diagnosis=T3, prescription=T4 재사용 — 중복 생성 안 함)
-- ---------------------------------------------------------------------
ALTER TABLE diagnosis    ADD COLUMN IF NOT EXISTS category   VARCHAR(32);   -- 코드접두 분류
ALTER TABLE diagnosis    ADD COLUMN IF NOT EXISTS freq       INTEGER DEFAULT 0;
ALTER TABLE prescription ADD COLUMN IF NOT EXISTS order_type VARCHAR(16);   -- 약/주사/물리·시술/영상/진찰료
ALTER TABLE prescription ADD COLUMN IF NOT EXISTS medfee_cd  VARCHAR(32);   -- 심평원 수가코드
ALTER TABLE prescription ADD COLUMN IF NOT EXISTS freq       INTEGER DEFAULT 0;

-- ---------------------------------------------------------------------
-- T2. laterality — 측 lookup (직교 축, 계층 아님)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS laterality (
    code  CHAR(1)    PRIMARY KEY,          -- L / R / B / C
    label VARCHAR(8) NOT NULL              -- 좌 / 우 / 양측 / 중앙
);

-- ---------------------------------------------------------------------
-- T6. mst_value_scale — 검사값 척도 lookup
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mst_value_scale (
    value_type VARCHAR(16) PRIMARY KEY,    -- +/- , +/+ , 각도/각도 , grade(v/v) , %/% , +/++/+++ , 거리(m)
    pattern    VARCHAR(64),                -- 표기 형식
    example    VARCHAR(64)                 -- 예시
);

-- ---------------------------------------------------------------------
-- T1. mst_body_part — 부위 계층 (adjacency list, 셀프 FK)
--   부위 → 영역 → 레벨/구조물. 부위마다 깊이 가변(무릎=구조물 / 허리=레벨).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mst_body_part (
    id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    parent_id INTEGER REFERENCES mst_body_part(id),   -- 셀프 참조, 루트=NULL (1:N)
    name      VARCHAR(64) NOT NULL,
    node_type VARCHAR(16) NOT NULL
              CHECK (node_type IN ('부위','영역','레벨','구조물')),
    name_en   VARCHAR(64)
);
CREATE INDEX IF NOT EXISTS ix_body_part_parent ON mst_body_part(parent_id);

-- ---------------------------------------------------------------------
-- T5. mst_exam_item — 검진 카탈로그 (gross/special_test/motor/sensory/reflex)
--   tenderness 는 여기 없음 — mst_body_part 노드를 직접 참조(visit_ccf_o.node_id).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mst_exam_item (
    item_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category    VARCHAR(16) NOT NULL
                CHECK (category IN ('gross','special_test','motor','sensory','reflex')),
    name        VARCHAR(128) NOT NULL,
    target_part INTEGER REFERENCES mst_body_part(id),   -- 적용 부위
    target_node INTEGER REFERENCES mst_body_part(id),   -- 표적 구조물/레벨 (없으면 NULL)
    value_type  VARCHAR(16) REFERENCES mst_value_scale(value_type)
);

-- ---------------------------------------------------------------------
-- G1. map_alias — 표기 변이 통합 사전 (다형 참조: target_table 로 분기)
--   canonical_id 는 가리키는 테이블이 가변이라 단일 FK 불가(의도된 polymorphic).
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS map_alias (
    surface      VARCHAR(128) PRIMARY KEY,  -- 표면 표기 (오십견, Lt, Mc, 절삭형…)
    canonical_id VARCHAR(64)  NOT NULL,     -- 표준 코드/노드 id
    target_table VARCHAR(32)  NOT NULL
                 CHECK (target_table IN ('mst_diagnosis','mst_order','mst_exam_item','mst_body_part','laterality')),
    alias_type   VARCHAR(16)  CHECK (alias_type IN ('동의어','약어','약식','절삭','brand')),
    source       VARCHAR(8)   CHECK (source IN ('std','learned')),
    confidence   REAL DEFAULT 1.0
);

-- =====================================================================
-- 연관(rel_*) — 임상 지식 그래프 (M:N junction)
-- =====================================================================

-- 부위 ↔ 진단
CREATE TABLE IF NOT EXISTS rel_part_diagnosis (
    body_part_id   INTEGER     REFERENCES mst_body_part(id),
    diagnosis_code VARCHAR(32) REFERENCES diagnosis(code),
    support        REAL,                              -- 동시출현 비율
    PRIMARY KEY (body_part_id, diagnosis_code)
);

-- 진단 ↔ 검사 (CCF PDF, 범용)  예: [ACL]→Lachman
CREATE TABLE IF NOT EXISTS rel_diagnosis_exam (
    diagnosis_code VARCHAR(32) REFERENCES diagnosis(code),
    item_id        INTEGER     REFERENCES mst_exam_item(item_id),
    source         VARCHAR(8)  CHECK (source IN ('std','learned')),
    PRIMARY KEY (diagnosis_code, item_id)
);

-- 진단 ↔ 처방 (데이터 채굴, 병원 고유)  support=co-occurrence
CREATE TABLE IF NOT EXISTS rel_diagnosis_order (
    diagnosis_code  VARCHAR(32) REFERENCES diagnosis(code),
    prescription_id INTEGER     REFERENCES prescription(id),
    support         REAL,
    PRIMARY KEY (diagnosis_code, prescription_id)
);

-- 구조물/레벨 ↔ 검사  예: Meniscus→Mcmurray
CREATE TABLE IF NOT EXISTS rel_structure_exam (
    node_id INTEGER REFERENCES mst_body_part(id),
    item_id INTEGER REFERENCES mst_exam_item(item_id),
    PRIMARY KEY (node_id, item_id)
);

-- =====================================================================
-- 방문결과(visit_ccf_*) — 추출 인스턴스. visit(id) 자식, 마스터 FK 참조.
--   S=1:1, O/A/P=1:N (방문당 여러 행)
-- =====================================================================

-- S — 환자 호소
CREATE TABLE IF NOT EXISTS visit_ccf_s (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    visit_id        INTEGER NOT NULL REFERENCES visit(id),
    body_part_id    INTEGER REFERENCES mst_body_part(id),
    laterality      CHAR(1) REFERENCES laterality(code),
    sub_region      VARCHAR(64),
    onset           VARCHAR(64),
    mechanism       VARCHAR(255),
    pain_quality    VARCHAR(64),
    vas             VARCHAR(16),
    aggravating     VARCHAR(255),
    chief_complaint TEXT
);
CREATE INDEX IF NOT EXISTS ix_ccf_s_visit ON visit_ccf_s(visit_id);

-- O — 객관적 검진 (item_id=검사 / node_id=압통 표적)
CREATE TABLE IF NOT EXISTS visit_ccf_o (
    id        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    visit_id  INTEGER NOT NULL REFERENCES visit(id),
    category  VARCHAR(16) NOT NULL
              CHECK (category IN ('gross','special_test','motor','sensory','reflex','tenderness','imaging')),
    item_id   INTEGER REFERENCES mst_exam_item(item_id),   -- 검사 항목(있으면)
    node_id   INTEGER REFERENCES mst_body_part(id),        -- 압통/표적 구조물(있으면)
    result    VARCHAR(64),                                 -- +/- , 45/full , v/v …
    raw_text  VARCHAR(255)                                 -- 원문 보존
);
CREATE INDEX IF NOT EXISTS ix_ccf_o_visit ON visit_ccf_o(visit_id);

-- A — 진단 (확정/감별). 미분류 시 diagnosis_code NULL + dx_text 보존
CREATE TABLE IF NOT EXISTS visit_ccf_a (
    id             INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    visit_id       INTEGER NOT NULL REFERENCES visit(id),
    diagnosis_code VARCHAR(32) REFERENCES diagnosis(code),
    dx_text        VARCHAR(255),
    status         VARCHAR(16) CHECK (status IN ('confirmed','r/o',''))
);
CREATE INDEX IF NOT EXISTS ix_ccf_a_visit ON visit_ccf_a(visit_id);

-- P — 치료 계획 (약/주사/물리·시술/영상계획). 미매핑 시 prescription_id NULL
CREATE TABLE IF NOT EXISTS visit_ccf_p (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    visit_id        INTEGER NOT NULL REFERENCES visit(id),
    order_type      VARCHAR(16),
    prescription_id INTEGER REFERENCES prescription(id),
    detail          VARCHAR(255),
    followup        VARCHAR(64)
);
CREATE INDEX IF NOT EXISTS ix_ccf_p_visit ON visit_ccf_p(visit_id);
