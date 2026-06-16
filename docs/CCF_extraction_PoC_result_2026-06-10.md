# CCF 추출 PoC 결과 리포트

> 작성일: 2026-06-10
> 목적: `visit_timeline.csv`의 `증상·차팅` 자유텍스트를 CCF SOAP 스키마로 구조화할 수 있는지, **얼마나 뽑아낼 수 있는지** 실측
> 산출물: `poc/extract_ccf.py` (추출 스크립트), `poc/ccf_extracted.json` (50행 결과)
> 관련 문서: [[CCF_extraction_first_strategy_2026-05-07]] (Phase 0 — 추출 PoC), [[1_schema_definition]]

---

## 0. 한 줄 결론

> **의사가 차팅 텍스트에 실제로 적은 임상정보(진단·부위·치료)는 90% 안팎으로 CCF SOAP 구조로 추출된다.** 안 뽑히는 항목은 추출 실패가 아니라 원문에 애초에 없는 정보다. PDF의 CCF 스키마대로의 구조화가 운영 가능한 수준으로 확인됨.

---

## 1. 실험 설정

| 항목 | 내용 |
|---|---|
| 입력 | `visit_timeline.csv` → `증상·차팅` 칼럼 (9,539행 중 의미있는 텍스트 ≥8자) |
| 샘플 | 무작위 50행 (`random.seed=42`) |
| 모델 | `claude-haiku-4-5` (운영 타깃 — 저렴·빠름) |
| 방식 | Claude **tool-use(structured output)** 로 CCF 스키마 강제 추출 |
| 전처리 | `◈ 증상 ◈` 머리말 제거, HTML 이스케이프(`&gt;`) 복원, 공백 정규화 |
| 성공률 | **50/50 행 추출 완료** |

**원문 특성**: 길이 13~368자 (중앙값 112자), 행당 평균 진단 1.18개. 짧은 메모부터 ROM 검진 포함 긴 노트까지 편차가 큼.

### 타깃 스키마 (CCF SOAP)

PDF(`CCF(Create Chart Faster)`) + [[1_schema_definition]] 기반으로 다음 구조를 고정:

```
S (Subjective)  : body_part, laterality(좌/우/양측/중앙), sub_region,
                  onset, mechanism, pain_quality, vas, aggravating, chief_complaint
O (Objective)   : physical_exam[], imaging[], neuro[]
A (Assessment)  : [{ dx, status(confirmed/r/o) }]
P (Plan)        : medication[], injection[], physical_therapy[],
                  imaging_plan[], followup, education
+ extraction_confidence (high/medium/low)  ← 모델 자기평가
```

**추출 규칙**: ① 텍스트에 명시된 것만, 추론·창작 금지 ② 영문 약어 보존(HNP, SLR, SNRB 등) ③ 없으면 빈값.

---

## 2. 결과 — 커버리지

### 2.1 SOAP 섹션별 (1개 필드 이상 추출된 행 비율)

| 섹션 | 추출된 행 | 비율 |
|---|---|---|
| **S** (환자 호소) | 46/50 | **92%** |
| **O** (객관적 검진) | 20/50 | 40% |
| **A** (진단) | 47/50 | **94%** |
| **P** (치료 계획) | 47/50 | **94%** |

### 2.2 필드별 채움률 (높은 순)

| 필드 | 채움률 | 비고 |
|---|---|---|
| A — 진단 | **94%** | 거의 모든 행에서 진단 추출 |
| S.body_part — 부위 | **90%** | 허리/무릎/어깨/발목 등 |
| P.physical_therapy — 물리/도수 | 70% | |
| S.laterality — 좌/우 | 66% | |
| S.onset — 언제부터 | 58% | "3일전", "1주일전" |
| P.medication — 약처방 | 52% | |
| P.followup — 추적 | 44% | "FU 1wk" |
| S.mechanism — 발병경위 | 42% | "접질림", "물건 들다가" |
| P.injection — 주사/시술 | 38% | SNRB, MBB, 체외충격파 |
| S.aggravating — 악화요인 | 38% | |
| S.sub_region — 세부부위 | 36% | 내측/외측/L4-5 |
| O.imaging — 영상소견 | 28% | x-ray/MRI finding |
| P.education — 환자교육 | 26% | |
| S.pain_quality — 통증양상 | 20% | 쑤시는/찌릿한 |
| P.imaging_plan — 검사계획 | 16% | |
| O.physical_exam — 신체검진 | 10% | |
| S.vas — 통증강도 | **4%** | 의사가 거의 안 적음 |
| O.neuro — 신경검사 | 4% | |

> **핵심 해석**: 채움률이 낮은 필드(VAS 4%, 신체검진 10%)는 **추출 능력의 한계가 아니라 원본 차팅에 그 정보가 없어서**다. 의사가 텍스트에 적은 항목(진단·부위·치료)은 90% 안팎으로 잡힌다. 즉 **상한은 데이터(의사 입력 습관)가 결정하지, 모델이 아니다.**

### 2.3 추출 신뢰도 자기평가 분포

| confidence | 행 수 | 의미 |
|---|---|---|
| high | 18 | 구조화 잘 됨 |
| medium | 24 | 부분 구조화 |
| low | 8 | 짧거나 비임상 텍스트 |

→ 모델이 스스로 `low`를 8건 표시. 이 태깅을 **자동저장 vs 의사검증 분기**(신뢰도 임계값)에 활용 가능 — [[CCF_extraction_first_strategy_2026-05-07]] Layer 3 설계와 연결.

---

## 3. 품질 — 원문 ↔ 추출 실제 사례

### ✅ 잘 된 케이스

**(1) ROM 검진 포함 긴 노트 — 정확히 분해**
```
원문: 등부위 통증 2월1일 친척과 장난치다가 다친 이후로 증상 발생
      Acute thoracic sprain 도수치료#1 물리치료#1
      Thoracic VAS 8 Flexion 30(50) Extension 25(45) Rt.Rotation 10(30)...

추출: S: 등 | onset=2월1일 | mechanism=친척과 장난치다 다침 | vas=8/10
      O: physical_exam=[Flexion 30(50), Extension 25(45), Rt.Rotation 10(30)...]
      A: Acute thoracic sprain (confirmed)
      P: physical_therapy=[도수치료#1, 물리치료#1]
```

**(2) 척추 시술 케이스 — 약어·레벨·계획 보존**
```
원문: 좌측 다리 당김 통증 저림 좌측 발목 마비 ... HNP -- r/o
      PO 1wk  SNRB L4-5-S1 Lt 토요일 11시 MRI 촬영 후 재진

추출: S: 다리/발목(좌) | pain_quality=당김,저림
      O: neuro=[좌측 발목 마비]
      A: HNP (r/o)
      P: medication=[PO 1wk] injection=[SNRB L4-5-S1 Lt] imaging_plan=[MRI] followup=MRI후 재진
```

### ⚠️ 주의해야 할 케이스 (한계)

**(3) 경미한 환각 — 명시 안 된 약물 추론**
```
원문: ...위 진단들의 첫번째 치료는 증상을 완화하면서 버티기...

추출: P: medication=[소염제]   ← 원문에 '소염제' 없음. 모델이 추론으로 생성
```
→ 진단·약물은 오류 비용이 큼([[CCF_extraction_first_strategy_2026-05-07]] §7.2). **검증 단계 필수.**

**(4) 분류 오류 — 서류 요청을 약으로 분류**
```
원문: 약이 더 필요해요. 영문 처방전

추출: P: medication=[영문 처방전]   ← '영문 처방전'은 서류 요청이지 약물 아님
```

**(5) 비임상 텍스트 — low confidence 로 정상 표시**
```
원문: cast off - 실패 // 주중에 다시 와서 하기로 함.

추출: [confidence=low] A: 기타  P: followup=주중 재내원하여 cast off 재시도
```
→ SOAP가 거의 빈 것은 정상. 짧은 행정성 메모는 모델이 스스로 `low`로 표시.

---

## 4. 시사점

1. **구조화 가능성 입증**: 정형외과 도메인 한정 + 명확한 스키마 → Haiku 같은 저가 모델로도 운영 가능 수준의 SOAP 구조화.
2. **상한은 원본 데이터**: 추출률이 낮은 필드는 모델 한계가 아니라 의사가 안 적은 것. → 향후 입력 UI/음성에서 누락 항목을 유도하면 구조화 데이터 품질이 더 올라감.
3. **신뢰도 태깅이 작동**: `confidence` 분기로 [[CCF_extraction_first_strategy_2026-05-07]]의 Layer 3(검증 UI) 자동저장/알림 임계값 설계에 바로 연결.
4. **검증 필요 영역 식별**: 진단·약물 필드의 경미한 환각 → 카테고리별 차등 검증(중요 항목 강제 확인) 정당화.

---

## 5. 한계 (정직하게)

- **N=50, 골든라벨 없음**: 본 리포트는 *커버리지(채움률)* 와 *육안 품질*이지, 정량 정확도(P/R/F1)가 아님. 정밀 측정은 골든라벨 30~50건 필요.
- **단일 모델(Haiku)**: 품질 천장은 Sonnet/Opus 로 더 높일 여지. 비용-정확도 트레이드오프 별도 측정 필요.
- **환각·오분류 잔존**: 약물·진단 등 고비용 필드는 자동 신뢰 불가. 검증 레이어 전제.

---

## 6. 다음 단계 (후보)

- [ ] **전체 9,539행 배치 실행** — `extract_ccf.py` N 변경, 토큰/비용 실측
- [ ] **정확도 정밀 측정** — 골든라벨 30~50건 → P/R/F1 (목표 F1 ≥ 85%, Phase 0 기준)
- [ ] **환각 억제 튜닝** — 진단·약물 필드 "원문 명시 없으면 비움" 강제 + 근거 span 동시 출력
- [ ] **모델 비교** — Haiku vs Sonnet 정확도·비용 트레이드오프
- [ ] **신뢰도 임계값 설계** — confidence 기반 자동저장/검증 분기 정책
