# CCF (Create Chart Faster) - SOAP 차팅 요구사항

> 출처: `CCF(Create Chart Faster) - Google Slides.pdf` (15페이지, by pedicle)
> 목적: 환자 진료 차트를 빠르게 작성하기 위한 SOAP 기반 입력 UI 정의

---

## 0. 전체 컨셉

- **탭 기반 부위 선택**: `허리 / 목 / 어깨 / + (추가)` 처럼 호소 부위별 탭 전환
- **칩(chip) 기반 입력**: 자주 쓰는 항목을 버튼으로 미리 만들어두고 선택, `+` 버튼으로 자유 입력 추가
- **SOAP 4분할 레이아웃**: 한 화면에 S(주황) / O(청록) / A(초록) / P(파랑) 영역을 동시에 보여줌
- **차트 클립보드 복사하기** 버튼으로 텍스트 SOAP을 즉시 복사 가능
- 디자인 원칙 (종빈님 참고사항):
  1. 색은 구분될 수 있는 정도로만 사용
  2. 글자/박스는 한눈에 다 보이도록 가장 작은 크기로
- 초진 위주로 먼저 구현, 재진은 다음에 고민

---

## 1. S — Subjective (주관적 호소)

환자가 호소하는 증상을 기록한다.

### 1.1 공통 입력 항목 (복수 선택 가능)

| 항목 | 입력 형태 | 예시 |
|---|---|---|
| 호소 부위 (대분류) | 다중 선택 칩 | 어깨 / 무릎 / 허리 / 목 / 손목 / 발목 / 고관절 / 팔꿈치 / 등 / 손가락 / 발가락 / 골반 / + 더 많은 옵션 |
| 통증 양상 | 다중 선택 칩 | 둔통 / 찌르는 듯 / 쑤시는 통증 / 파르르하는 통증 / 욱신거리는 통증 / 당기는 느낌 / 뻑뻑함 / + 더 많은 옵션 |
| VAS 통증 척도 | 0~10 슬라이더 | 7/10, 저린 느낌 등 보조 태그 |
| 발병 시기 | 칩 선택 + 직접 입력 | 오늘 / 어제 / 3일 전 / 1주일 전 / 2주일 전 / 1주 전 |
| 지속 양상 | 칩 | 지속 / 간헐 / 위장보호제 약간 / 기상 시 / 활동 후 / 야간 |
| 악화 요인 | 칩 | 계단 오르기 / 장시간 앉기 / 무거운 물건 들기 / 회전 동작 / 구부리기 / 기침/재채기 / 보행 시 / 야간 |
| 완화 요인 | 칩 | 안정 / 냉찜질 / 온찜질 / 진통제 복용 / 스트레칭 / 자세 변경 / + 더 많은 옵션 |
| 추가 기록 | 자유 텍스트 | 예: "10일 전 다른병원에서 MRI 촬영 후 신경 차단주사 2회 후 호전됨" |

> ❓ 미해결 과제 (p.11): **환자의 과거 치료 내역을 어떻게 기록할지** — 별도 추가기록 영역 필요

### 1.2 부위별 세부 입력 — 무릎

| 항목 | 선택지 |
|---|---|
| 세부부위 (1) | 오른쪽 / 왼쪽 |
| 세부부위 (2) | 내측 / 외측 / 앞쪽 / 뒤쪽(오금부) |
| 세부부위 (3) — 내측 | Meniscus / MCL / Pes anserius / VMO(vastus medialis obliquus) / Medial patellofemoral ligament |
| 세부부위 (3) — 외측 | Meniscus / LCL / IT band / VLO(vastus lateralis obliquus) / Lateral patellofemoral ligament |
| 세부부위 (3) — 앞쪽 | Quadriceps tendon / Patellar tendon / Fat pad / tibial tuberosity |
| 세부부위 (3) — 뒤쪽(오금부) | Medial hamstring tendon (semitendinosus, semimembranosus) / Lateral hamstring tendon (Biceps femoris) |
| 통증 경위 | 부딪힘 / 많이 걷고 난 후 / 여행 다녀온 후 / 운동하고 난 후 (축구·농구·배드민턴) |
| 언제부터 | 3일 전 / 1주일 전 / 2주일 전 |
| 통증 유발 행동 | 걸으면 / 갑자기 움직일 때 / 양반다리할 때 |

### 1.3 부위별 세부 입력 — 허리

| 항목 | 선택지 |
|---|---|
| 세부부위 (1) | 오른쪽 / 왼쪽 / 중앙 |
| 세부부위 (2) — Lumbar level | L1 / L2 / L3 / L4 / L5 |
| 세부부위 (2) — Sacrum level | Buttock / SI joint |
| 세부부위 (2) — Coccyx level | Coccyx |

---

## 2. O — Objective (객관적 검진)

신체검진과 영상/검사 결과를 기록한다.

### 2.1 공통 항목

- **영상 검사**: x-ray / MRI / CT / 초음파
  - 결과 칩: Mild kyphotic change / Non specific finding / 디스크 팽윤 등
- **검사실 수치** (필요 시 자유 기재)

### 2.2 무릎 — 신체검진

| 항목 | 입력 |
|---|---|
| Gross finding | Swelling / Bruise (+/-) |
| 압통 (Tenderness) | 세부부위(2)(3) 구조물 단위로 (+/-) 체크 (예: Meniscus, MCL, Pes anserius, VMO, MPFL …) |
| **Meniscus 검사** | McMurray test (+/+), ROM (각도/각도 — 예: Flexion 130/130, Flexion contracture 0/0), Thessaly test (+/+), Apley grind test (+/+) |
| **ACL 검사** | Anterior draw test (+/+), Lachman test (+/+), Pivot shift test (+/+) |
| **PCL 검사** | Posterior draw test (+/+), Posterior sag sign (+/+), Quadriceps active test (+/+) |
| **MCL / LCL 검사** | Valgus stress test (+/+), Varus stress test (+/+) |
| **IT band 검사** | Noble compression test (+/+), Ober test (+/+) |
| **슬개골 검사** | Patellar grinding test, Patellar apprehension test, Patellar tracking (J sign), Patellar tilt test (각각 +/+) |

### 2.3 허리 — 신체검진

| 분류 | 항목 |
|---|---|
| Gross finding | (허리는 생략 가능) |
| 압통 (Tenderness) | Lumbar L1~L5 / Sacrum (Buttock, SI joint) / Coccyx 단위 |
| 일반 | SLR test (각도/각도), Claudication 거리 (예: 200m), Babinski's sign (+/-) |
| **Motor** (오른쪽/왼쪽, 각각 v/v 또는 등급) | HF Hip Flexion (L2) / KF Knee Flexion / KE Knee extension (L3) / ADF Ankle dorsi flexion (L4) / BTDF Big toe dorsi flexion (L5) / APF Ankle plantar flexion (S1) — 표기 예: HF (v/v) (v/iv) (iii/iii) (5/5) |
| **Sensory** (Dermatome %) | L1 (100%/30%) / L2 / L3 / L4 / L5 / S1 dermatome |
| **Deep Tendon Reflex** | Achilles tendon, Patellar tendon — 표기 예: DTR (++/++) (++++/++++) |
| **항문 검사** | Anal tone (intact / decreased), Anal sensory (예: 50%) |

### 2.4 Vertebral Level 참고 (UI 도움말로 노출)

| Level | Motor | Sensory | Reflex |
|---|---|---|---|
| L3 | Hip flexion / Knee extension | Medial knee | Patellar |
| L4 | Ankle Dorsiflexion | Medial foot | — |
| L5 | Great toe Extension | Dorsal foot | — |
| S1 | Plantar flexion | Lateral foot | Achilles |

---

## 3. A — Assessment (진단·평가)

진단명을 기록한다. ICD 코드 동반.

### 3.1 공통 동작

- 진단명 칩 (예: HNP / Acute lumbar sprain / Spinal stenosis)
- **R/O (rule out)** 토글
- **레벨/측 지정**: 예) HNP → L3-4 / L4-5, 좌/우 (P 영역의 SNRB 주사와도 연동되어야 함, p.15 참조)

### 3.2 무릎 — 진단 분류

| 분류 | 항목 |
|---|---|
| **염좌 Sprain (인대)** | 내측 측부인대 MCL / 외측 측부인대 LCL / 전방십자인대 ACL (partial, complete) / 후방십자인대 PCL / 슬개인대 Patella ligament / 내측 슬개대퇴인대 MPFL / 외측 슬개대퇴인대 LPFL |
| **긴장 Strain (근육·건)** | Hamstring (외측 Biceps femoris, 내측 Semitendinosus·Semimembranosus) / 대퇴사두근 Quadriceps femoris (Vastus lateralis, Vastus medialis, Rectus femoris, vastus intermedius) / 장경인대 Iliotibial band / 슬와근 Popliteus / 비복근 Gastrocnemius / 가자미근 Soleus |
| **염증** | 슬개건염 Patellar tendinitis / 햄스트링 건염 Hamstring tendinitis / 거위발건염 Pes anserius |
| **파열** | 인대 / 연골판 / 근육 (Partial, complete), Meniscus tear |
| **골절** | patella fracture (transverse type 등) |

### 3.3 허리 — 진단 예시

- HNP (추간판 탈출증, M51.1) — L3-4 / L4-5 등 레벨 + 측 지정
- Acute lumbar sprain
- Spinal stenosis

---

## 4. P — Plan (치료 계획)

### 4.1 약물

| 항목 | 입력 |
|---|---|
| PO medication | NSAIDs (소염진통제) — 예: 200mg 7일, 근이완제, 신경병증성 진통제, 위장보호제 |
| 처방 기간 | 3일 / 1주일 / 2주일 칩 + 직접 입력 |

### 4.2 주사

- **종류 칩**: PO / Injection / 스테로이드 관절 주사
- **SNRB (선택적 신경근 차단술)**: 우측/좌측 선택 + 레벨 지정 (예: L4-5, L4-5-S1) ← p.15 요구사항
- 신경 차단주사, 도수치료 등

### 4.3 물리치료

- 온열치료 / 전기치료 (TENS) / 초음파치료 / 도수치료 / PT

### 4.4 보조기

- 허리 보조기 (코르셋) 등

### 4.5 주의사항 / Follow Up

- 주의사항 칩: 6시간 후 샤워 / 증상 악화 시 / **마비 증상 발생 시 응급 수술 필요성** (p.15)
- F/U: 1주 후 / 2주 후 등

### 4.6 의사가 놓치기 쉬운 설명 추가 영역 (p.15)

자유 텍스트 또는 칩 형태로 환자 교육 내용을 덧붙일 수 있게 함.

---

## 5. SOAP 화면 구성 요구사항

### 5.1 레이아웃

```
┌─────────────────────────┬─────────────────────────┐
│ [허리][목][어깨][+]                               │
├─────────────────────────┼─────────────────────────┤
│ S (주황)                 │ A (초록)                │
│ - 호소 / 시기 / 자세·운동 │ - 진단 / R/O / 레벨      │
├─────────────────────────┼─────────────────────────┤
│ O (청록)                 │ P (파랑)                │
│ - 영상 / Motor·Sensory   │ - 약물·주사·물리·보조기 │
│   ·Reflex                │ - 주의사항 / F/U        │
└─────────────────────────┴─────────────────────────┘
[ 차트 클립보드 복사하기 ]
```

### 5.2 출력 (클립보드 복사 시)

기존 의무기록 양식과 호환되도록 텍스트 SOAP 형태로 출력 (p.7, p.9, p.12 예시 참조):

```
S)
허리통증
우측 엉치부터 다리 당김 통증
1주일전 무거운 것을 들고 가다가 삐끗하면서 통증 발생
3일전 한의원에서 침을 맞았으나 호전 없음

O)
x-ray: mild kyphotic change
Motor: ADF(iv/v) BTDF(iv/v)
Sensory: Rt L5 dermatome dec.
DTR: intact
SLR(45/full)
Barbinski's sign(-)
Tenderness(-)

A)
HNP - r/o
디스크 탈출증일 가능성이 높으니 일단 보존적 치료 해보고 호전 없으면 MRI 촬영 해보겠습니다.

P)
PO medication 1wk
물리치료
신경차단주사 치료
FU 1wk
```

---

## 6. 추가 요구사항 (p.5, p.15)

- **약도/자세한 내용**을 자유롭게 입력할 수 있는 영역
- **진단서·소견서** 자동 작성 기능
- **수정·보완**은 클립보드 복사 후에도 가능하도록
- **환자 생성**은 뒤로 미뤄도 됨 (먼저 차트부터 작성 가능해야 함)
- **재진** 화면은 추후 고민, **초진** 먼저 구현
- **마비 증상 발생 시 응급 수술 필요성** 같은 의사가 놓치기 쉬운 설명을 추가하는 템플릿 제공

---

## 7. 디자인 가이드 (종빈님)

1. 색상: 영역 구분이 가능한 최소한의 채도만 사용
2. 글자/박스: 한 화면에 모두 보이도록 가장 작은 크기로 배치
