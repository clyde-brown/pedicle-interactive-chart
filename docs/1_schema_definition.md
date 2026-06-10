# Pedicle DB 스키마 정의서

> **DB**: PostgreSQL (Windows Server 10, `211.63.197.2:5432`)  
> **접속 유저**: pedicle  
> **총 테이블 수**: 523개  
> **이 문서 범위**: 실제 환자 데이터가 존재하는 `convert_` prefix 테이블 (마이그레이션/변환 데이터)

---

## 데이터 현황 요약

| 테이블 | 설명 | 건수 |
|--------|------|------|
| `convert_ptnt_ord` | 처방·오더 | **79,078** |
| `convert_ptnt_diag` | 진단 | **34,204** |
| `convert_opdin` | 내원 접수 | **12,284** |
| `convert_ptnt_symp` | 증상·의사 차팅 | **9,540** |
| `convert_insp_memo` | 검사 메모 | **820** |
| `convert_error` | 변환 오류 로그 | 100 |
| `convert_chart_lab_result` | 검사결과 (구조만) | 0 |
| `convert_chart_ptnt` | 환자 기본정보 (구조만) | 0 |
| `convert_bit_drug`, `convert_dur`, `convert_nix_ord` 등 | 기타 | 0 |

---

## 테이블 상세 정의

### 1. `convert_opdin` — 내원 접수 (12,284건)

환자가 병원에 방문한 접수 이력. **가장 상위 단위 테이블**로, 다른 테이블과의 조인 기준이 된다.

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `ptnt_no` | varchar | 환자 고유번호 (환자 식별 키) |
| `recept_no` | varchar | 접수번호 (방문 1건 = 1개, 조인 키) |
| `clinic_ymd` | char | 내원일 (YYYYMMDD) |
| `ptnt_prsn_no` | char | 주민등록번호 |
| `ptnt_nm` | varchar | 환자명 |
| `insr_nm` | varchar | 보험사명 |
| `clinic_gb` | varchar | 진료구분 |
| `recept_gb` | varchar | 접수구분 (예: 외래) |
| `close_ymd` | char | 진료 종료일 (YYYYMMDD) |
| `use_yn` | char | 사용여부 (Y/N) |
| `doct_nm` | varchar | 담당의명 |

**샘플**:
```
ptnt_no=4, clinic_ymd=20231207, ptnt_nm=박상민, recept_gb=외래
ptnt_no=17, clinic_ymd=20240122, ptnt_nm=김성일, recept_gb=외래
```

---

### 2. `convert_ptnt_symp` — 증상·의사 차팅 (9,540건)

의사가 진료 시 입력한 자유텍스트 노트. 증상, 소견, 진단 의견, 치료 계획이 모두 하나의 필드에 담겨 있다.

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `ptnt_no` | varchar | 환자번호 (FK → convert_opdin) |
| `recept_no` | varchar | 접수번호 (FK → convert_opdin) |
| `symp_nm` | text | 증상 + 의사 소견 전문 (자유텍스트, `\r` 줄바꿈) |

**실제 데이터 예시** (`ptnt_no=100`):
```
◈  증상 ◈
발음성 고관절
쪼그려 앉았을때 우측 무릎이 아프다.

1년전부터
다른 치료는 안받고 있고
운동은 안하고 있다.
x-ray: no remarkable finding
Snapping hip Rt
Meniscus injury knee Rt

P-T (고관절)
도수치료

FU 1wk
```

> **특이사항**: `symp_nm` 필드 하나에 주소, 증상, 소견, 진단명, 처치 계획이 모두 포함. 파싱 시 `◈  증상 ◈` 헤더를 기준으로 섹션 분리 가능.

---

### 3. `convert_ptnt_diag` — 진단 (34,204건)

KCD 진단코드 기반의 구조화된 진단 정보.

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `ptnt_no` | varchar | 환자번호 (FK → convert_opdin) |
| `recept_no` | varchar | 접수번호 (FK → convert_opdin) |
| `diag_cd` | varchar | KCD 진단코드 (예: M5422, M1000) |
| `diag_nm` | varchar | 진단명 (한국어) |
| `diag_gb` | numeric | 진단구분 (99=상병 등) |

**실제 데이터 예시** (`ptnt_no=4`):
```
B022  - 기타 신경계통 침범을 동반한 대상포진
M1000 - 특발성 통풍, 여러 부위
M1391 - 상세불명의 관절염, 어깨부분
M2551 - 관절통, 어깨부분
M5422 - 경추통, 경부
```

---

### 4. `convert_ptnt_ord` — 처방·오더 (79,078건)

약처방, 시술, 검사, 물리치료 등 모든 오더 내역. 가장 데이터가 많은 테이블.

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `ptnt_no` | varchar | 환자번호 (FK → convert_opdin) |
| `recept_no` | varchar | 접수번호 (FK → convert_opdin) |
| `ord_seq` | numeric | 오더 순서 |
| `ord_cd` | varchar | 오더 코드 |
| `medfee_cd` | varchar | 수가 코드 |
| `ord_nm` | varchar | 오더명 (약품명·처치명·검사명 등) |
| `ord_qty` | varchar | 처방량 |
| `ord_divide` | varchar | 분할 횟수 (1일 몇 번) |
| `ord_day` | varchar | 처방 일수 |
| `ord_method` | varchar | 복용 방법 |
| `proc_dept_cd` | varchar | 처리 부서 코드 |
| `ord_rst1` | text | 오더 결과값 1 (검사결과 텍스트 등) |
| `ord_rst2` | varchar | 오더 결과값 2 |
| `ord_rst3` | varchar | 오더 결과값 3 |
| `out_lab` | varchar | 외부 검사 여부 |

**실제 데이터 예시** (`ptnt_no=4`):
```
초진진찰료-의원  qty=1, day=1
타이레놀정160밀리  qty=1, day=7
경추2매  qty=1, day=1  (X-ray)
견관절3매  qty=1, day=1  (X-ray)
```

**오더 유형 분류** (`ord_nm` 패턴 기준):
- 진찰료: `초진진찰료`, `재진진찰료`
- 약처방: 약품명 + 용량 (예: `타이레놀정`, `리리카캡슐50밀리그램`)
- 영상검사: `경추2매`, `요추2매`, `흉부2매`, `전척추`
- 시술: `경막외신경차단술`, `좌골신경차단술`, `체외충격파`
- 물리치료: `심층열치료`, `표층열치료`, `도수치료`, `간섭파전류치료`

---

### 5. `convert_insp_memo` — 검사 메모 (820건)

월 단위 검사 관련 임상 메모. 자유텍스트 형태.

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `ptnt_no` | varchar | 환자번호 |
| `demand_ym` | char | 해당 년월 (YYYY-MM) |
| `demand_memo` | varchar | 검사 메모 내용 |

**실제 데이터 예시**:
```
ptnt_no=4000, demand_ym=2025-01, demand_memo=OA knee both
ptnt_no=1010, demand_ym=2024-08, demand_memo=SLR (-) / claudication (+)
ptnt_no=1011, demand_ym=2024-04, demand_memo=진찰만함
```

---

### 6. `convert_chart_lab_result` — 검사결과 (현재 0건, 구조만 존재)

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `ptnt_no` | varchar | 환자번호 |
| `recept_no` | varchar | 접수번호 |
| `ord_cd` | varchar | 오더 코드 |
| `ord_nm` | varchar | 검사명 |
| `result` | varchar | 검사 결과값 |

---

### 7. `convert_chart_ptnt` — 환자 기본정보 (현재 0건, 구조만 존재)

환자 마스터 정보. 향후 마이그레이션 대상.

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| `ptnt_no` | varchar | 환자번호 |
| `ptnt_nm` | varchar | 환자명 |
| `ptnt_prsn_no` | varchar | 주민등록번호 |
| `birth_ymd` | char | 생년월일 |
| `addr` | varchar | 주소 |
| `addr_detail` | varchar | 상세주소 |
| `home_tel_no` | varchar | 집 전화번호 |
| `phone_no` | varchar | 휴대폰번호 |
| `email` | varchar | 이메일 |
| `family_nm` | varchar | 보호자명 |
| `family_phone_no` | varchar | 보호자 연락처 |
| `family_relation_gb` | varchar | 보호자 관계 구분 |
| `handicap_gb` | varchar | 장애 구분 |
| `first_visit_ymd` | char | 첫 내원일 |
| `att_doctor` | varchar | 주치의 |
| `att_dept` | varchar | 주치 부서 |
| `opd_memo` | text | 외래 메모 |
| ... | ... | 총 38개 컬럼 |

---

## 테이블 관계도

```
convert_opdin (내원 접수, 12,284건)
    │ ptnt_no + recept_no
    ├──▶ convert_ptnt_symp   (증상·차팅, 9,540건)    1:1 per visit
    ├──▶ convert_ptnt_diag   (진단코드, 34,204건)    1:N per visit (복수진단)
    ├──▶ convert_ptnt_ord    (처방·오더, 79,078건)   1:N per visit (복수오더)
    │
    │ ptnt_no only
    └──▶ convert_insp_memo   (검사메모, 820건)        월단위, recept_no 없음
```

**조인 키**:
- `ptnt_no`: 환자 단위 식별자
- `recept_no`: 방문(접수) 단위 식별자. `convert_opdin`의 PK 역할

---

## 환자별 데이터 추출 쿼리

### 기본 조인: 내원별 진단 + 처방 요약

```sql
-- 특정 환자의 전체 내원 이력 (진단 + 처방 집계)
SELECT
    o.ptnt_no,
    o.ptnt_nm,
    o.clinic_ymd,
    o.recept_no,
    o.doct_nm,
    -- 진단: 쉼표로 이어붙이기
    STRING_AGG(DISTINCT d.diag_nm, ', ') AS 진단목록,
    -- 오더: 쉼표로 이어붙이기
    STRING_AGG(DISTINCT p.ord_nm, ', ') AS 처방오더목록
FROM convert_opdin o
LEFT JOIN convert_ptnt_diag d
    ON o.ptnt_no = d.ptnt_no AND o.recept_no = d.recept_no
LEFT JOIN convert_ptnt_ord p
    ON o.ptnt_no = p.ptnt_no AND o.recept_no = p.recept_no
WHERE o.ptnt_no = '4'          -- 환자번호 지정
GROUP BY o.ptnt_no, o.ptnt_nm, o.clinic_ymd, o.recept_no, o.doct_nm
ORDER BY o.clinic_ymd;
```

### 풀 조인: 증상(차팅) + 진단 + 처방 전체

```sql
-- 특정 환자의 방문 1건에 대한 전체 임상 정보
SELECT
    o.ptnt_no,
    o.ptnt_nm,
    o.clinic_ymd,
    o.recept_gb,
    o.doct_nm,
    s.symp_nm                           AS 의사_차팅,
    d.diag_cd,
    d.diag_nm,
    p.ord_nm,
    p.ord_qty,
    p.ord_day,
    p.ord_method
FROM convert_opdin o
LEFT JOIN convert_ptnt_symp s
    ON o.ptnt_no = s.ptnt_no AND o.recept_no = s.recept_no
LEFT JOIN convert_ptnt_diag d
    ON o.ptnt_no = d.ptnt_no AND o.recept_no = d.recept_no
LEFT JOIN convert_ptnt_ord p
    ON o.ptnt_no = p.ptnt_no AND o.recept_no = p.recept_no
WHERE o.ptnt_no = '4'
ORDER BY o.clinic_ymd, p.ord_seq;
```

### 전체 환자 통계

```sql
-- 환자별 내원 횟수, 진단 수, 처방 수
SELECT
    o.ptnt_no,
    MIN(o.ptnt_nm)              AS 환자명,
    COUNT(DISTINCT o.recept_no) AS 내원횟수,
    MIN(o.clinic_ymd)           AS 첫내원일,
    MAX(o.clinic_ymd)           AS 최근내원일,
    COUNT(DISTINCT d.diag_cd)   AS 진단종류수,
    COUNT(p.ord_nm)             AS 총처방건수
FROM convert_opdin o
LEFT JOIN convert_ptnt_diag d
    ON o.ptnt_no = d.ptnt_no AND o.recept_no = d.recept_no
LEFT JOIN convert_ptnt_ord p
    ON o.ptnt_no = p.ptnt_no AND o.recept_no = p.recept_no
GROUP BY o.ptnt_no
ORDER BY 내원횟수 DESC
LIMIT 20;
```

---

## 데이터 특성 및 주의사항

1. **차팅 필드 구조**: `convert_ptnt_symp.symp_nm`은 자유텍스트로, 증상/소견/진단/치료계획이 혼합되어 있음. `◈  증상 ◈` 헤더 기준으로 섹션 파싱 가능.

2. **`doct_nm` 미입력**: `convert_opdin`의 `doct_nm`이 대부분 공백. 담당의 정보는 원본 EMR 시스템(`hz_mst_empl`) 참조 필요.

3. **진단 없는 방문 존재**: `convert_ptnt_diag`가 없는 `recept_no`도 있음 (물리치료만 받은 경우 등).

4. **`ord_nm` 절삭**: `convert_ptnt_ord.ord_nm`이 일부 잘려서 저장됨 (원본 필드 길이 제한).

5. **`recept_no` 형식**: `YYMMDDN` 패턴 (예: `2312072` = 2023년 12월 07일 두 번째 접수).

6. **환자번호 범위**: `ptnt_no`는 숫자형 문자열, 확인된 범위 4 ~ 4000+.

7. **`convert_insp_memo`는 월단위**: `recept_no` 없이 `demand_ym`(YYYY-MM)으로만 연결되므로 정확한 방문과의 조인 불가.
