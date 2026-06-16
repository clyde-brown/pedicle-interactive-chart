"""정형외과 마스터 데이터 워크북 빌더.

현재 스키마의 마스터 테이블을 도메인 지식 + 웹검증(ICD-11)으로 채워
하나의 xlsx에 시트별로 저장한다.
실행: python scripts/build_master_workbook.py
출력: master_data/orthopedic_master_data.xlsx
"""
from __future__ import annotations

import os

import pandas as pd

OUT_DIR = "master_data"
OUT = os.path.join(OUT_DIR, "orthopedic_master_data.xlsx")

# =====================================================================
# 1. laterality — 측성 마스터
# =====================================================================
laterality = [
    ("L", "좌", "Left", "좌측"),
    ("R", "우", "Right", "우측"),
    ("B", "양측", "Bilateral", "양쪽 모두"),
    ("C", "중앙", "Central/Midline", "정중선(좌우 구분 없음)"),
]
df_lat = pd.DataFrame(laterality, columns=["code", "label_ko", "label_en", "note"])

# =====================================================================
# 2. value_scale — 검사값 척도
# =====================================================================
value_scale = [
    ("+/-", "단일 양/음", "(+)", "양성/음성 단일 결과"),
    ("+/+", "좌우 양/음", "(+/-)", "좌/우 각각 양음 (special test)"),
    ("각도/각도", "좌우 관절가동범위", "45/full", "ROM 좌/우 각도"),
    ("grade(v/v)", "도수근력 좌/우", "4/5", "MMT 0~5등급 좌/우"),
    ("%/%", "감각 좌/우", "80%/100%", "dermatome 감각 비율"),
    ("+/++/+++", "심부건반사 등급", "++", "DTR 0~4+ (감소~항진)"),
    ("거리(m)", "보행거리", "100m", "신경인성 파행(claudication) 거리"),
    ("VAS(0-10)", "통증 강도", "7/10", "Visual Analog Scale"),
    ("cm", "둘레/길이 차", "2cm", "근위축 둘레차, 하지장 차 등"),
    ("grade(0-3)", "부종/삼출 등급", "2+", "swelling/effusion trace~3+"),
    ("modality", "감각 양식", "LT/PP", "light touch/pinprick/proprioception"),
    ("quality", "통증 양상", "쑤심/찌릿", "dull/sharp/burning/tingling"),
]
df_vs = pd.DataFrame(value_scale, columns=["value_type", "pattern", "example", "description"])

# =====================================================================
# 3. body_part — 정형외과 부위 트리 (id, parent_id, name, name_en, node_type, region, midline)
#    midline=True → 정중선(중앙만), False → 좌/우/양측
# =====================================================================
# (id, parent_id, name_ko, name_en, node_type, region, midline)
body_part = [
    # ---- 최상위 부위 ----
    (1, None, "척추", "Spine", "부위", "척추", False),
    (2, None, "어깨/견갑대", "Shoulder girdle", "부위", "어깨", False),
    (3, None, "팔꿈치", "Elbow", "부위", "팔꿈치", False),
    (4, None, "손목/손", "Wrist/Hand", "부위", "수부", False),
    (5, None, "골반/고관절", "Pelvis/Hip", "부위", "고관절", False),
    (6, None, "무릎", "Knee", "부위", "무릎", False),
    (7, None, "발목/발", "Ankle/Foot", "부위", "족부", False),
    # ---- 척추 영역 ----
    (10, 1, "경추", "Cervical spine", "영역", "척추", False),
    (11, 1, "흉추", "Thoracic spine", "영역", "척추", False),
    (12, 1, "요추", "Lumbar spine", "영역", "척추", False),
    (13, 1, "천추/미추", "Sacrum/Coccyx", "영역", "척추", False),
    # 경추 극돌기(정중선)
    (100, 10, "C2 극돌기", "Spinous process C2", "구조물", "척추", True),
    (101, 10, "C3 극돌기", "Spinous process C3", "구조물", "척추", True),
    (102, 10, "C4 극돌기", "Spinous process C4", "구조물", "척추", True),
    (103, 10, "C5 극돌기", "Spinous process C5", "구조물", "척추", True),
    (104, 10, "C6 극돌기", "Spinous process C6", "구조물", "척추", True),
    (105, 10, "C7 극돌기", "Spinous process C7", "구조물", "척추", True),
    # 경추 후관절(좌우)
    (110, 10, "C2-C3 후관절", "Facet joint C2-C3", "레벨", "척추", False),
    (111, 10, "C3-C4 후관절", "Facet joint C3-C4", "레벨", "척추", False),
    (112, 10, "C4-C5 후관절", "Facet joint C4-C5", "레벨", "척추", False),
    (113, 10, "C5-C6 후관절", "Facet joint C5-C6", "레벨", "척추", False),
    (114, 10, "C6-C7 후관절", "Facet joint C6-C7", "레벨", "척추", False),
    (115, 10, "C7-T1 후관절", "Facet joint C7-T1", "레벨", "척추", False),
    # 경추 척추주위
    (120, 10, "상부 경추 척추주위", "Upper cervical paraspinal", "영역", "척추", False),
    (121, 10, "중부 경추 척추주위", "Mid cervical paraspinal", "영역", "척추", False),
    (122, 10, "하부 경추 척추주위", "Lower cervical paraspinal", "영역", "척추", False),
    # 요추 극돌기(정중선)
    (130, 12, "L1 극돌기", "Spinous process L1", "구조물", "척추", True),
    (131, 12, "L2 극돌기", "Spinous process L2", "구조물", "척추", True),
    (132, 12, "L3 극돌기", "Spinous process L3", "구조물", "척추", True),
    (133, 12, "L4 극돌기", "Spinous process L4", "구조물", "척추", True),
    (134, 12, "L5 극돌기", "Spinous process L5", "구조물", "척추", True),
    (135, 12, "요천추 정중(L5-S1)", "L5-S1 midline", "구조물", "척추", True),
    # 요추 후관절
    (140, 12, "L1-L2 후관절", "Facet joint L1-L2", "레벨", "척추", False),
    (141, 12, "L2-L3 후관절", "Facet joint L2-L3", "레벨", "척추", False),
    (142, 12, "L3-L4 후관절", "Facet joint L3-L4", "레벨", "척추", False),
    (143, 12, "L4-L5 후관절", "Facet joint L4-L5", "레벨", "척추", False),
    (144, 12, "L5-S1 후관절", "Facet joint L5-S1", "레벨", "척추", False),
    # 요추 척추주위
    (150, 12, "상부 요추 척추주위", "Upper lumbar paraspinal", "영역", "척추", False),
    (151, 12, "하부 요추 척추주위", "Lower lumbar paraspinal", "영역", "척추", False),
    # 천추/미추
    (160, 13, "천장관절(SI joint)", "Sacroiliac joint", "레벨", "척추", False),
    (161, 13, "천골", "Sacrum", "구조물", "척추", True),
    (162, 13, "미골/꼬리뼈", "Coccyx", "구조물", "척추", True),
    # ---- 어깨 구조물 ----
    (200, 2, "견봉쇄골관절(AC joint)", "Acromioclavicular joint", "구조물", "어깨", False),
    (201, 2, "흉쇄관절(SC joint)", "Sternoclavicular joint", "구조물", "어깨", False),
    (202, 2, "견봉", "Acromion", "구조물", "어깨", False),
    (203, 2, "오훼돌기", "Coracoid process", "구조물", "어깨", False),
    (204, 2, "상완골 대결절", "Greater tuberosity", "구조물", "어깨", False),
    (205, 2, "이두근고랑", "Bicipital groove", "구조물", "어깨", False),
    (206, 2, "회전근개", "Rotator cuff", "구조물", "어깨", False),
    (207, 2, "관절와순", "Glenoid labrum", "구조물", "어깨", False),
    # ---- 팔꿈치 ----
    (300, 3, "외측상과", "Lateral epicondyle", "구조물", "팔꿈치", False),
    (301, 3, "내측상과", "Medial epicondyle", "구조물", "팔꿈치", False),
    (302, 3, "주두", "Olecranon", "구조물", "팔꿈치", False),
    (303, 3, "요골두", "Radial head", "구조물", "팔꿈치", False),
    # ---- 손목/손 ----
    (400, 4, "요골 경상돌기", "Radial styloid", "구조물", "수부", False),
    (401, 4, "척골 경상돌기", "Ulnar styloid", "구조물", "수부", False),
    (402, 4, "해부학적 코담배갑", "Anatomical snuffbox", "구조물", "수부", False),
    (403, 4, "TFCC 부위", "TFCC region", "구조물", "수부", False),
    (404, 4, "수근관", "Carpal tunnel", "구조물", "수부", False),
    (405, 4, "엄지 CMC 관절", "Thumb CMC joint", "구조물", "수부", False),
    (406, 4, "MCP 관절선", "MCP joint line", "레벨", "수부", False),
    (407, 4, "PIP 관절선", "PIP joint line", "레벨", "수부", False),
    (408, 4, "DIP 관절선", "DIP joint line", "레벨", "수부", False),
    (409, 4, "A1 활차", "A1 pulley", "구조물", "수부", False),
    # ---- 골반/고관절 ----
    (500, 5, "서혜부", "Inguinal/groin", "구조물", "고관절", False),
    (501, 5, "대전자", "Greater trochanter", "구조물", "고관절", False),
    (502, 5, "전상장골극(ASIS)", "ASIS", "구조물", "고관절", False),
    (503, 5, "후상장골극(PSIS)", "PSIS", "구조물", "고관절", False),
    (504, 5, "좌골결절", "Ischial tuberosity", "구조물", "고관절", False),
    (505, 5, "치골결합", "Pubic symphysis", "구조물", "고관절", True),
    # ---- 무릎 ----
    (600, 6, "내측 관절선", "Medial joint line", "레벨", "무릎", False),
    (601, 6, "외측 관절선", "Lateral joint line", "레벨", "무릎", False),
    (602, 6, "슬개골", "Patella", "구조물", "무릎", False),
    (603, 6, "슬개건", "Patellar tendon", "구조물", "무릎", False),
    (604, 6, "경골조면", "Tibial tuberosity", "구조물", "무릎", False),
    (605, 6, "거위발", "Pes anserine", "구조물", "무릎", False),
    (606, 6, "비골두", "Fibular head", "구조물", "무릎", False),
    (607, 6, "전방십자인대(ACL)", "ACL", "구조물", "무릎", False),
    (608, 6, "후방십자인대(PCL)", "PCL", "구조물", "무릎", False),
    (609, 6, "내측측부인대(MCL)", "MCL", "구조물", "무릎", False),
    (610, 6, "외측측부인대(LCL)", "LCL", "구조물", "무릎", False),
    (611, 6, "내측반월상연골", "Medial meniscus", "구조물", "무릎", False),
    (612, 6, "외측반월상연골", "Lateral meniscus", "구조물", "무릎", False),
    # ---- 발목/발 ----
    (700, 7, "내과(내측복사)", "Medial malleolus", "구조물", "족부", False),
    (701, 7, "외과(외측복사)", "Lateral malleolus", "구조물", "족부", False),
    (702, 7, "전거비인대(ATFL)", "ATFL", "구조물", "족부", False),
    (703, 7, "아킬레스건 부착부", "Achilles insertion", "구조물", "족부", False),
    (704, 7, "아킬레스건 중간부", "Achilles midsubstance", "구조물", "족부", False),
    (705, 7, "종골 내측결절", "Medial calcaneal tubercle", "구조물", "족부", False),
    (706, 7, "주상골 조면", "Navicular tuberosity", "구조물", "족부", False),
    (707, 7, "제5중족골 기저부", "Base of 5th metatarsal", "구조물", "족부", False),
    (708, 7, "제1MTP 관절선", "1st MTP joint", "레벨", "족부", False),
    (709, 7, "족저근막", "Plantar fascia", "구조물", "족부", False),
    # ====== [보강] 두경부/TMJ (원본 visit_timeline에 측두하악관절 존재) ======
    (8, None, "두경부/악관절", "Head/Neck/TMJ", "부위", "두경부", False),
    (800, 8, "측두하악관절(TMJ)", "Temporomandibular joint", "구조물", "두경부", False),
    (801, 8, "후두하부", "Suboccipital region", "영역", "두경부", False),
    (802, 8, "후두-환추 관절부(AO)", "Atlanto-occipital joint", "레벨", "두경부", False),
    (803, 8, "환추-축추 관절부(AA)", "Atlanto-axial joint", "레벨", "두경부", False),
    # ====== [보강] 흉곽/늑골 ======
    (9, None, "흉곽/늑골", "Chest wall/Rib", "부위", "흉곽", False),
    (900, 9, "늑연골 접합부", "Costochondral junction", "구조물", "흉곽", False),
    (901, 9, "흉골", "Sternum", "구조물", "흉곽", True),
    (902, 9, "늑골", "Rib", "구조물", "흉곽", False),
    # ====== [보강] 흉추 극돌기(정중선) T1~T12 ======
    (170, 11, "T1 극돌기", "Spinous process T1", "구조물", "척추", True),
    (171, 11, "T2 극돌기", "Spinous process T2", "구조물", "척추", True),
    (172, 11, "T3 극돌기", "Spinous process T3", "구조물", "척추", True),
    (173, 11, "T4 극돌기", "Spinous process T4", "구조물", "척추", True),
    (174, 11, "T5 극돌기", "Spinous process T5", "구조물", "척추", True),
    (175, 11, "T6 극돌기", "Spinous process T6", "구조물", "척추", True),
    (176, 11, "T7 극돌기", "Spinous process T7", "구조물", "척추", True),
    (177, 11, "T8 극돌기", "Spinous process T8", "구조물", "척추", True),
    (178, 11, "T9 극돌기", "Spinous process T9", "구조물", "척추", True),
    (179, 11, "T10 극돌기", "Spinous process T10", "구조물", "척추", True),
    (180, 11, "T11 극돌기", "Spinous process T11", "구조물", "척추", True),
    (181, 11, "T12 극돌기", "Spinous process T12", "구조물", "척추", True),
    # 흉추 후관절(대표 레벨) + 척추주위
    (185, 11, "상부 흉추 후관절(T1-T4)", "Upper thoracic facet", "레벨", "척추", False),
    (186, 11, "중부 흉추 후관절(T5-T8)", "Mid thoracic facet", "레벨", "척추", False),
    (187, 11, "하부 흉추 후관절(T9-T12)", "Lower thoracic facet", "레벨", "척추", False),
    (188, 11, "흉추 척추주위", "Thoracic paraspinal", "영역", "척추", False),
    # ====== [보강] 어깨 견갑 구조물 ======
    (208, 2, "견갑극", "Scapular spine", "구조물", "어깨", False),
    (209, 2, "견갑골 하각", "Inferior angle of scapula", "구조물", "어깨", False),
    (210, 2, "상완이두건 장두", "Long head of biceps tendon", "구조물", "어깨", False),
    # ====== [보강] 상완/전완 골간 ======
    (310, 3, "상완골 간부", "Humeral shaft", "구조물", "팔꿈치", False),
    (311, 3, "전완 골간(요/척골)", "Forearm shaft", "구조물", "팔꿈치", False),
    (312, 3, "주관절 척골신경구(cubital)", "Cubital tunnel", "구조물", "팔꿈치", False),
    # ====== [보강] 하퇴 ======
    (620, 6, "하퇴(경/비골 간부)", "Lower leg shaft", "구조물", "무릎", False),
    (621, 6, "비복근/장딴지", "Gastrocnemius/Calf", "근육", "무릎", False),
    (622, 6, "정강이(전경골부)", "Shin (anterior tibia)", "구조물", "무릎", False),
    # ====== [보강] 족부 세부 ======
    (710, 7, "종골(발뒤꿈치뼈)", "Calcaneus", "구조물", "족부", False),
    (711, 7, "거골", "Talus", "구조물", "족부", False),
    (712, 7, "중족부(midfoot)", "Midfoot", "영역", "족부", False),
    (713, 7, "후족부(rearfoot)", "Hindfoot", "영역", "족부", False),
    (714, 7, "족근관(tarsal tunnel)", "Tarsal tunnel", "구조물", "족부", False),
    # ====== [보강] 통증클리닉 핵심 근육(MPS/압통점) ======
    (1000, None, "근육(MPS/압통점)", "Muscle/Trigger point", "부위", "근육", False),
    (1001, 1000, "상부 승모근", "Upper trapezius", "근육", "근육", False),
    (1002, 1000, "견갑거근", "Levator scapulae", "근육", "근육", False),
    (1003, 1000, "능형근", "Rhomboid", "근육", "근육", False),
    (1004, 1000, "극상근/극하근", "Supra/Infraspinatus", "근육", "근육", False),
    (1005, 1000, "요방형근", "Quadratus lumborum", "근육", "근육", False),
    (1006, 1000, "이상근", "Piriformis", "근육", "근육", False),
    (1007, 1000, "둔근(대/중/소)", "Gluteus muscles", "근육", "근육", False),
    (1008, 1000, "척추기립근", "Erector spinae", "근육", "근육", False),
    (1009, 1000, "흉쇄유돌근", "Sternocleidomastoid", "근육", "근육", False),
]
df_bp = pd.DataFrame(body_part, columns=["id", "parent_id", "name_ko", "name_en", "node_type", "region", "midline"])

# =====================================================================
# 4. part_laterality — 부위별 허용 측성 (midline 규칙으로 생성)
# =====================================================================
pl_rows = []
for r in body_part:
    bid, _, name, _, _, _, midline = r
    if midline:
        pl_rows.append((bid, name, "C", "중앙만"))
    else:
        for code, note in [("B", ""), ("L", ""), ("R", "")]:
            pl_rows.append((bid, name, code, note))
df_pl = pd.DataFrame(pl_rows, columns=["body_part_id", "body_part_name", "laterality", "note"])

# =====================================================================
# 5. exam_item — 정형외과 검사 (category, name, name_full, target_part, target_structure, value_type, tests_for)
# =====================================================================
exam = [
    # ===== 경추 =====
    ("special_test", "Spurling test", "Spurling's compression test", "경추", "신경근", "+/+", "경추 신경근 압박(radiculopathy)"),
    ("special_test", "Cervical distraction", "Distraction test", "경추", "신경근", "+/-", "신경근 증상 완화 여부"),
    ("special_test", "Hoffman sign", "Hoffmann's reflex", "경추", "척수", "+/-", "경수증(myelopathy) 상위운동신경원"),
    ("special_test", "Lhermitte sign", "Lhermitte's sign", "경추", "척수", "+/-", "척수병증 전기충격감"),
    # ===== 어깨 =====
    ("special_test", "Neer test", "Neer impingement test", "어깨", "회전근개", "+/+", "견봉하 충돌"),
    ("special_test", "Hawkins test", "Hawkins-Kennedy test", "어깨", "회전근개", "+/+", "극상근 충돌"),
    ("special_test", "Empty can test", "Jobe's empty can test", "어깨", "극상근", "+/+", "극상근 파열/건병증"),
    ("special_test", "Drop arm test", "Drop arm test", "어깨", "회전근개", "+/+", "대형 회전근개 파열"),
    ("special_test", "Lift-off test", "Gerber lift-off test", "어깨", "견갑하근", "+/+", "견갑하근 파열"),
    ("special_test", "Belly press test", "Belly press test", "어깨", "견갑하근", "+/+", "견갑하근 기능"),
    ("special_test", "ER lag sign", "External rotation lag sign", "어깨", "극하근", "+/+", "극하근/소원근 파열"),
    ("special_test", "Speed test", "Speed's test", "어깨", "이두건", "+/+", "상완이두건 장두 병변"),
    ("special_test", "Yergason test", "Yergason's test", "어깨", "이두건", "+/+", "이두건 장두/SLAP"),
    ("special_test", "O'Brien test", "Active compression test", "어깨", "관절와순", "+/+", "SLAP 병변/AC 관절"),
    ("special_test", "Apprehension test", "Anterior apprehension", "어깨", "관절와순", "+/+", "전방 불안정성"),
    ("special_test", "Cross-body adduction", "Cross-arm test", "어깨", "AC joint", "+/+", "견봉쇄골관절 병변"),
    # ===== 팔꿈치 =====
    ("special_test", "Cozen test", "Cozen's test", "팔꿈치", "외측상과", "+/+", "외측상과염(테니스엘보)"),
    ("special_test", "Mill test", "Mill's test", "팔꿈치", "외측상과", "+/+", "외측상과염"),
    ("special_test", "Golfer elbow test", "Medial epicondylitis test", "팔꿈치", "내측상과", "+/+", "내측상과염(골프엘보)"),
    ("special_test", "Elbow valgus stress", "Valgus stress test", "팔꿈치", "MCL(UCL)", "+/+", "내측측부인대 손상"),
    # ===== 손목/손 =====
    ("special_test", "Phalen test", "Phalen's maneuver", "손목/손", "정중신경", "+/+", "수근관증후군"),
    ("special_test", "Tinel sign (wrist)", "Tinel's sign", "손목/손", "정중신경", "+/+", "수근관증후군"),
    ("special_test", "Finkelstein test", "Finkelstein's test", "손목/손", "1구획건", "+/+", "드꿰르뱅 건초염"),
    ("special_test", "Watson test", "Scaphoid shift test", "손목/손", "주상골", "+/+", "주상월상 불안정"),
    ("special_test", "Froment sign", "Froment's sign", "손목/손", "척골신경", "+/+", "척골신경 마비"),
    # ===== 요추 =====
    ("special_test", "SLR test", "Straight leg raise", "요추", "좌골신경", "각도/각도", "요추 신경근 자극/HNP"),
    ("special_test", "Crossed SLR", "Crossed straight leg raise", "요추", "좌골신경", "+/+", "중심성 추간판탈출(특이도 높음)"),
    ("special_test", "Bragard test", "Bragard's sign", "요추", "좌골신경", "+/+", "신경근 자극 확인"),
    ("special_test", "Slump test", "Slump test", "요추", "신경", "+/+", "신경긴장 검사"),
    ("special_test", "Femoral nerve stretch", "Femoral n. stretch test", "요추", "대퇴신경", "+/+", "상위 요추(L2-4) 신경근"),
    ("special_test", "Schober test", "Modified Schober", "요추", "", "cm", "요추 굴곡 가동성(강직성척추염)"),
    ("special_test", "Claudication", "Neurogenic claudication", "요추", "", "거리(m)", "신경인성 파행거리(협착증)"),
    # ===== 고관절 =====
    ("special_test", "FABER test", "Patrick's test", "고관절", "고관절/SI", "+/+", "고관절/천장관절 병변"),
    ("special_test", "FADIR test", "Impingement test", "고관절", "고관절", "+/+", "대퇴비구충돌(FAI)/관절순"),
    ("special_test", "Thomas test", "Thomas test", "고관절", "장요근", "+/+", "고관절 굴곡구축"),
    ("special_test", "Trendelenburg", "Trendelenburg sign", "고관절", "중둔근", "+/+", "중둔근 기능/외전근"),
    ("special_test", "Ober test", "Ober's test", "고관절", "장경인대", "+/+", "장경인대 긴장"),
    # ===== 무릎 =====
    ("special_test", "McMurray test", "McMurray's test", "무릎", "반월상연골", "+/+", "반월상연골 파열"),
    ("special_test", "Apley grind test", "Apley compression", "무릎", "반월상연골", "+/+", "반월상연골 파열"),
    ("special_test", "Thessaly test", "Thessaly test", "무릎", "반월상연골", "+/+", "반월상연골 파열"),
    ("special_test", "Lachman test", "Lachman test", "무릎", "ACL", "+/+", "전방십자인대 파열(가장 민감)"),
    ("special_test", "Anterior drawer", "Anterior drawer test", "무릎", "ACL", "+/+", "전방십자인대 파열"),
    ("special_test", "Pivot shift test", "Pivot shift test", "무릎", "ACL", "+/+", "ACL 회전 불안정"),
    ("special_test", "Posterior drawer", "Posterior drawer test", "무릎", "PCL", "+/+", "후방십자인대 파열"),
    ("special_test", "Posterior sag sign", "Godfrey test", "무릎", "PCL", "+/+", "후방십자인대 파열"),
    ("special_test", "Valgus stress test", "Valgus stress (MCL)", "무릎", "MCL", "+/+", "내측측부인대 손상"),
    ("special_test", "Varus stress test", "Varus stress (LCL)", "무릎", "LCL", "+/+", "외측측부인대 손상"),
    ("special_test", "Patellar apprehension", "Patellar apprehension", "무릎", "슬개골", "+/+", "슬개골 불안정/탈구"),
    ("special_test", "Patellar grind test", "Clarke's sign", "무릎", "슬개골", "+/+", "슬개대퇴 통증증후군"),
    ("special_test", "Ballottement test", "Patellar tap", "무릎", "", "+/-", "관절삼출(effusion)"),
    # ===== 발목/발 =====
    ("special_test", "Ankle anterior drawer", "Anterior drawer (ankle)", "발목/발", "ATFL", "+/+", "전거비인대 손상"),
    ("special_test", "Talar tilt test", "Talar tilt", "발목/발", "CFL", "+/+", "종비인대 손상"),
    ("special_test", "Thompson test", "Simmonds-Thompson", "발목/발", "아킬레스건", "+/-", "아킬레스건 완전파열"),
    ("special_test", "Squeeze test", "Squeeze test", "발목/발", "원위경비인대", "+/-", "고위 발목염좌(syndesmosis)"),
    ("special_test", "Windlass test", "Windlass test", "발목/발", "족저근막", "+/+", "족저근막염"),
    ("special_test", "Mulder click", "Mulder's sign", "발목/발", "지간신경", "+/-", "모르톤 신경종"),
    # ===== Gross (시진/촉진) =====
    ("gross", "Swelling", "부종", "공통", "", "+/-", "관절/연부조직 부종"),
    ("gross", "Effusion", "관절삼출", "공통", "", "+/-", "관절강 내 삼출"),
    ("gross", "Ecchymosis", "반상출혈/멍", "공통", "", "+/-", "타박/출혈"),
    ("gross", "Deformity", "변형", "공통", "", "+/-", "골절/탈구 변형"),
    ("gross", "Muscle atrophy", "근위축", "공통", "", "cm", "근위축 둘레차"),
    ("gross", "Tenderness", "압통", "공통", "", "+/-", "국소 압통(부위 지정)"),
    ("gross", "ROM", "관절가동범위", "공통", "", "각도/각도", "능동/수동 ROM"),
    ("gross", "LOM", "가동범위 제한", "공통", "", "+/-", "Limitation of motion"),
    # ===== Motor (요추 myotome) =====
    ("motor", "Hip flexion", "장요근(L2)", "요추", "L2", "grade(v/v)", "L2 근력"),
    ("motor", "Knee extension", "대퇴사두근(L3)", "요추", "L3", "grade(v/v)", "L3 근력"),
    ("motor", "Ankle dorsiflexion", "전경골근(L4)", "요추", "L4", "grade(v/v)", "L4 근력"),
    ("motor", "Big toe extension", "무지신전근(L5)", "요추", "L5", "grade(v/v)", "L5 근력"),
    ("motor", "Ankle plantarflexion", "비복근(S1)", "요추", "S1", "grade(v/v)", "S1 근력"),
    # ===== Motor (경추 myotome) =====
    ("motor", "Shoulder abduction", "삼각근(C5)", "경추", "C5", "grade(v/v)", "C5 근력"),
    ("motor", "Elbow flexion", "이두근(C6)", "경추", "C6", "grade(v/v)", "C6 근력"),
    ("motor", "Elbow extension", "삼두근(C7)", "경추", "C7", "grade(v/v)", "C7 근력"),
    ("motor", "Finger flexion", "수지굴곡(C8)", "경추", "C8", "grade(v/v)", "C8 근력"),
    ("motor", "Finger abduction", "골간근(T1)", "경추", "T1", "grade(v/v)", "T1 근력"),
    # ===== Sensory (dermatome) =====
    ("sensory", "L4 dermatome", "L4 피부분절", "요추", "L4", "%/%", "내측 하퇴 감각"),
    ("sensory", "L5 dermatome", "L5 피부분절", "요추", "L5", "%/%", "족배/무지 감각"),
    ("sensory", "S1 dermatome", "S1 피부분절", "요추", "S1", "%/%", "외측 족부 감각"),
    ("sensory", "C6 dermatome", "C6 피부분절", "경추", "C6", "%/%", "엄지 감각"),
    ("sensory", "C7 dermatome", "C7 피부분절", "경추", "C7", "%/%", "중지 감각"),
    ("sensory", "C8 dermatome", "C8 피부분절", "경추", "C8", "%/%", "소지 감각"),
    # ===== Reflex (DTR) =====
    ("reflex", "Biceps DTR", "이두건 반사(C5-6)", "경추", "C6", "+/++/+++", "C5-6 반사"),
    ("reflex", "Triceps DTR", "삼두건 반사(C7)", "경추", "C7", "+/++/+++", "C7 반사"),
    ("reflex", "Patellar DTR", "슬개건 반사(L4)", "요추", "L4", "+/++/+++", "L4 반사"),
    ("reflex", "Achilles DTR", "아킬레스건 반사(S1)", "요추", "S1", "+/++/+++", "S1 반사"),
    ("reflex", "Babinski sign", "바빈스키 징후", "공통", "", "+/-", "상위운동신경원 병변"),
    ("reflex", "Ankle clonus", "발목 간대성경련", "공통", "", "+/-", "상위운동신경원 병변"),
    ("reflex", "Hoffmann reflex", "호프만 반사", "경추", "", "+/-", "경수증(상위운동신경원)"),
    # ===== [보강] 경추/흉곽출구 =====
    ("special_test", "Jackson compression", "Jackson compression test", "경추", "신경근", "+/+", "경추 신경근 압박"),
    ("special_test", "ULTT", "Upper limb tension test", "경추", "상완신경총", "+/+", "신경 긴장(상지 방사통)"),
    ("special_test", "Adson test", "Adson's test", "경추", "흉곽출구", "+/+", "흉곽출구증후군(혈관성)"),
    ("special_test", "Roos test", "EAST / Roos test", "경추", "흉곽출구", "+/+", "흉곽출구증후군(3분 거상)"),
    # ===== [보강] 어깨 =====
    ("special_test", "Full can test", "Full can test", "어깨", "극상근", "+/+", "극상근(통증 적은 변형)"),
    ("special_test", "Painful arc", "Painful arc sign", "어깨", "회전근개", "+/+", "60-120도 충돌 통증호"),
    ("special_test", "Sulcus sign", "Sulcus sign", "어깨", "관절막", "+/+", "하방 불안정성"),
    ("special_test", "Relocation test", "Jobe relocation test", "어깨", "관절와순", "+/+", "전방 불안정 확인"),
    ("special_test", "Bear hug test", "Bear hug test", "어깨", "견갑하근", "+/+", "견갑하근 상부 파열"),
    ("special_test", "Scarf test", "Cross-body / Scarf test", "어깨", "AC joint", "+/+", "견봉쇄골관절 병변"),
    # ===== [보강] 팔꿈치/주관절 =====
    ("special_test", "Tinel (elbow)", "Tinel's sign at elbow", "팔꿈치", "척골신경", "+/+", "주관절증후군(cubital)"),
    ("special_test", "Elbow flexion test", "Elbow flexion test", "팔꿈치", "척골신경", "+/+", "주관절증후군"),
    ("special_test", "Moving valgus stress", "Moving valgus stress test", "팔꿈치", "UCL", "+/+", "내측측부인대 손상"),
    # ===== [보강] 손목/손 =====
    ("special_test", "Durkan test", "Carpal compression test", "손목/손", "정중신경", "+/+", "수근관증후군(가장 민감)"),
    ("special_test", "Reverse Phalen", "Reverse Phalen test", "손목/손", "정중신경", "+/+", "수근관증후군"),
    ("special_test", "Allen test", "Allen's test", "손목/손", "요/척골동맥", "+/-", "손 혈류 개존성"),
    ("special_test", "CMC grind test", "Thumb CMC grind test", "손목/손", "엄지 CMC", "+/+", "엄지 기저부 관절염"),
    ("special_test", "TFCC load test", "Ulnar grind/load test", "손목/손", "TFCC", "+/+", "TFCC 손상"),
    # ===== [보강] 요추/천장관절(SI) =====
    ("special_test", "Kemp test", "Kemp's / extension-rotation", "요추", "후관절", "+/+", "요추 후관절성 통증"),
    ("special_test", "Milgram test", "Milgram test", "요추", "", "+/-", "추간판/경막내 병변"),
    ("special_test", "Gaenslen test", "Gaenslen's test", "천장관절", "SI joint", "+/+", "천장관절 유발검사"),
    ("special_test", "SI compression", "SI joint compression", "천장관절", "SI joint", "+/+", "천장관절 유발검사"),
    ("special_test", "SI distraction", "SI joint distraction", "천장관절", "SI joint", "+/+", "천장관절 유발검사"),
    ("special_test", "Thigh thrust", "Thigh thrust test", "천장관절", "SI joint", "+/+", "천장관절 유발(가장 민감)"),
    ("special_test", "Sacral thrust", "Sacral thrust test", "천장관절", "SI joint", "+/+", "천장관절 유발검사"),
    # ===== [보강] 고관절 =====
    ("special_test", "Log roll test", "Log roll test", "고관절", "고관절", "+/+", "고관절 관절내 병변(특이도↑)"),
    ("special_test", "Stinchfield test", "Resisted SLR (Stinchfield)", "고관절", "고관절", "+/+", "고관절 관절내 병변"),
    ("special_test", "Scour test", "Quadrant/Scour test", "고관절", "관절순", "+/+", "고관절순/연골 병변"),
    ("special_test", "Piriformis test", "Piriformis / FAIR test", "고관절", "이상근", "+/+", "이상근증후군"),
    ("special_test", "Ely test", "Ely's test", "고관절", "대퇴직근", "+/+", "대퇴직근 긴장"),
    # ===== [보강] 무릎 =====
    ("special_test", "Dial test", "Dial test", "무릎", "후외측", "+/+", "후외측 회전 불안정(PLC)"),
    ("special_test", "Sweep test", "Brush/Bulge test", "무릎", "", "+/-", "소량 관절삼출"),
    ("special_test", "Noble test", "Noble compression test", "무릎", "장경인대", "+/+", "장경인대 마찰증후군"),
    ("special_test", "Patellar tilt/glide", "Patellar tilt & glide", "무릎", "슬개골", "+/+", "슬개골 정렬/불안정"),
    ("special_test", "Wilson test", "Wilson test", "무릎", "", "+/+", "박리성 골연골염(OCD)"),
    # ===== [보강] 발목/발 =====
    ("special_test", "Kleiger test", "External rotation test", "발목/발", "원위경비인대", "+/+", "고위 발목염좌(syndesmosis)"),
    ("special_test", "Single heel raise", "Single leg heel raise", "발목/발", "후경골건/아킬레스", "+/-", "후경골건 기능부전/아킬레스"),
    ("special_test", "Tinel (tarsal)", "Tinel at tarsal tunnel", "발목/발", "후경골신경", "+/+", "족근관증후군"),
    # ===== [보강] 보행/전신/비기질적 =====
    ("gross", "Gait analysis", "보행분석", "공통", "", "+/-", "antalgic/Trendelenburg/steppage"),
    ("gross", "Romberg test", "롬버그 검사", "공통", "", "+/-", "고유감각/평형(척수후주)"),
    ("gross", "Waddell signs", "Waddell 비기질적 징후", "요추", "", "+/-", "비기질적 요통(과장 평가)"),
]
df_exam = pd.DataFrame(exam, columns=["category", "name", "name_full", "target_part", "target_structure", "value_type", "tests_for"])

# =====================================================================
# 6. diagnosis — 정형외과 진단 ICD-10(KCD)/ICD-11/영문
#    icd11_src: web=웹검증, kb=도메인지식(미검증)
# =====================================================================
diagnosis = [
    # 척추
    ("요추 추간판탈출증", "Lumbar disc herniation", "M51.2", "FA80.0", "척추", "web"),
    ("기타 추간판 장애", "Other intervertebral disc disorders", "M51.9", "FA80", "척추", "web"),
    ("경추 추간판장애", "Cervical disc disorder", "M50.2", "FA80", "척추", "web"),
    ("척추관 협착증", "Spinal stenosis", "M48.0", "FA82", "척추", "web"),
    ("척추전방전위증", "Spondylolisthesis", "M43.1", "FA84", "척추", "web"),
    ("척추분리증", "Spondylolysis", "M43.0", "FA81", "척추", "web"),
    ("경추통", "Cervicalgia", "M54.2", "ME84.2", "척추", "kb"),
    ("요통(비특이성)", "Low back pain", "M54.5", "ME84.2", "척추", "kb"),
    ("좌골신경통 동반 요통", "Low back pain with sciatica", "M54.4", "ME84.2", "척추", "web"),
    ("흉추통", "Thoracic back pain", "M54.6", "ME84.2", "척추", "kb"),
    ("경추 염좌 및 긴장", "Sprain/strain of cervical spine", "S13.4", "NA23", "척추", "web"),
    ("요추 염좌 및 긴장", "Sprain/strain of lumbar spine", "S33.5", "NA23", "척추", "web"),
    ("강직성 척추염", "Ankylosing spondylitis", "M45", "FA20.0", "척추", "web"),
    ("퇴행성 척추증(요추)", "Lumbar spondylosis", "M47.8", "FA8Z", "척추", "kb"),
    ("골다공증성 압박골절", "Osteoporotic compression fracture", "M80.88", "FB83.1", "척추", "kb"),
    # 어깨
    ("동결견(오십견)", "Adhesive capsulitis", "M75.0", "FB53.0", "어깨", "web"),
    ("회전근개 파열", "Rotator cuff tear", "M75.1", "FB53.1", "어깨", "web"),
    ("어깨 충돌증후군", "Shoulder impingement syndrome", "M75.4", "FB53.2", "어깨", "web"),
    ("석회성 건염", "Calcific tendinitis of shoulder", "M75.3", "FB53.3", "어깨", "web"),
    ("상완이두건염", "Bicipital tendinitis", "M75.2", "FB53", "어깨", "kb"),
    ("견관절 탈구", "Dislocation of shoulder", "S43.0", "NC13", "어깨", "web"),
    ("견봉쇄골관절 손상", "AC joint injury", "S43.1", "NC13", "어깨", "kb"),
    # 팔꿈치
    ("외측상과염(테니스엘보)", "Lateral epicondylitis", "M77.1", "FB51.0", "팔꿈치", "web"),
    ("내측상과염(골프엘보)", "Medial epicondylitis", "M77.0", "FB51.1", "팔꿈치", "web"),
    ("주두 점액낭염", "Olecranon bursitis", "M70.2", "FB50", "팔꿈치", "kb"),
    # 손목/손
    ("수근관증후군", "Carpal tunnel syndrome", "G56.0", "8C10", "수부", "web"),
    ("드꿰르뱅 건초염", "De Quervain tenosynovitis", "M65.4", "FB40.0", "수부", "web"),
    ("방아쇠수지", "Trigger finger", "M65.3", "FB40.3", "수부", "web"),
    ("결절종", "Ganglion cyst", "M67.4", "FB41.0", "수부", "web"),
    ("원위 요골골절(Colles)", "Distal radius fracture", "S52.5", "NC12.5", "수부", "web"),
    ("주상골 골절", "Scaphoid fracture", "S62.0", "NC13", "수부", "kb"),
    ("엄지 CMC 관절염", "Thumb CMC OA", "M18.0", "FA21", "수부", "kb"),
    # 고관절
    ("고관절 골관절염", "Coxarthrosis", "M16.1", "FA00", "고관절", "web"),
    ("대퇴골두 무혈성괴사", "AVN of femoral head", "M87.0", "FB81.0", "고관절", "web"),
    ("대퇴비구충돌(FAI)", "Femoroacetabular impingement", "M24.85", "FA2Z", "고관절", "kb"),
    ("대퇴경부 골절", "Femoral neck fracture", "S72.0", "NC72.0", "고관절", "web"),
    ("대퇴전자간 골절", "Pertrochanteric fracture", "S72.1", "NC72.1", "고관절", "web"),
    ("대전자 점액낭염", "Trochanteric bursitis", "M70.6", "FB50", "고관절", "kb"),
    # 무릎
    ("무릎 골관절염(일측)", "Gonarthrosis, unilateral", "M17.1", "FA01.0", "무릎", "web"),
    ("무릎 골관절염(양측)", "Gonarthrosis, bilateral", "M17.0", "FA01.0", "무릎", "web"),
    ("반월상연골 파열(급성)", "Tear of meniscus, current", "S83.2", "NC33.2", "무릎", "web"),
    ("반월상연골 파열(퇴행성)", "Derangement of meniscus", "M23.2", "FA33", "무릎", "web"),
    ("전방십자인대 파열", "ACL rupture", "S83.5", "NC33.3", "무릎", "web"),
    ("내측측부인대 손상", "MCL injury", "S83.4", "NC33", "무릎", "kb"),
    ("슬개골 연골연화증", "Chondromalacia patellae", "M22.4", "FB13.1", "무릎", "web"),
    ("베이커 낭종", "Baker's cyst", "M71.2", "FB54.2", "무릎", "web"),
    ("거위발 건염", "Pes anserine tendinitis", "M76.8", "FB52", "무릎", "kb"),
    # 발목/발
    ("발목 염좌", "Ankle sprain", "S93.4", "NC93", "족부", "web"),
    ("아킬레스건 파열", "Achilles tendon rupture", "S86.0", "NC93", "족부", "kb"),
    ("아킬레스건염", "Achilles tendinitis", "M76.6", "FB52.0", "족부", "web"),
    ("족저근막염", "Plantar fasciitis", "M72.2", "FB55.2", "족부", "web"),
    ("무지외반증", "Hallux valgus", "M20.1", "FA30", "족부", "web"),
    ("지간신경종(모르톤)", "Morton neuroma", "G57.6", "8C12", "족부", "web"),
    ("중족골 골절", "Metatarsal fracture", "S92.3", "NC95", "족부", "kb"),
    # 전신/기타
    ("골다공증", "Osteoporosis", "M81.0", "FB83.1", "기타", "web"),
    ("통풍성 관절염", "Gouty arthritis", "M10.9", "FA25", "기타", "web"),
    ("류마티스 관절염", "Rheumatoid arthritis", "M06.9", "FA20", "기타", "web"),
    ("패혈성 관절염", "Septic arthritis", "M00.9", "FA12", "기타", "kb"),
    ("근막동통증후군(MPS)", "Myofascial pain syndrome", "M79.1", "MG30.02", "기타", "web"),
    # ====== [보강] 통증클리닉/신경 ======
    ("대상포진", "Herpes zoster", "B02.9", "1E91", "기타", "kb"),
    ("대상포진후신경통(PHN)", "Postherpetic neuralgia", "B02.2", "MG30.51/1E91.5", "기타", "web"),
    ("신경계 침범 대상포진", "Zoster w/ nervous system involvement", "B02.2", "1E91.4", "기타", "kb"),
    ("섬유근통", "Fibromyalgia", "M79.7", "MG30.01", "기타", "web"),
    ("이상근증후군", "Piriformis syndrome", "G57.0", "8C11.00", "고관절", "web"),
    ("흉곽출구증후군(TOS)", "Thoracic outlet syndrome", "G54.0", "8C1Z", "어깨", "kb"),
    ("경추성 두통", "Cervicogenic headache", "G44.84", "8A8A", "두경부", "kb"),
    ("측두하악관절장애(TMD)", "TMJ disorder", "K07.6", "DA0E", "두경부", "kb"),
    ("주관절증후군(척골신경)", "Cubital tunnel syndrome", "G56.2", "8C10.1", "팔꿈치", "kb"),
    # ====== [보강] 척추 신경근/천장관절 ======
    ("요추 신경근병증(좌골신경통)", "Lumbar radiculopathy/sciatica", "M54.1", "ME84.2", "척추", "kb"),
    ("경추 신경근병증", "Cervical radiculopathy", "M54.1", "ME84.2", "척추", "kb"),
    ("천장관절 기능장애/통증", "SI joint dysfunction", "M53.3", "FA83", "척추", "kb"),
    ("경추 염좌(편타성손상)", "Whiplash / cervical sprain", "S13.4", "NA23", "척추", "kb"),
    ("흉추 압박골절", "Thoracic compression fracture", "S22.0", "NA20", "척추", "kb"),
    # ====== [보강] 흉곽/늑골 ======
    ("늑골 골절", "Rib fracture", "S22.3", "NA82.0", "흉곽", "kb"),
    ("늑연골염(티체증후군)", "Costochondritis (Tietze)", "M94.0", "FB56.1", "흉곽", "kb"),
    # ====== [보강] 일반 정형(부위 비특이/원본 빈출코드) ======
    ("관절통(어깨 등)", "Arthralgia", "M25.5", "FA8Z", "기타", "kb"),
    ("윤활낭염(점액낭염)", "Bursitis, unspecified", "M71.9", "FB50", "기타", "kb"),
    ("연조직염", "Cellulitis", "L03.9", "1B70", "기타", "kb"),
    ("건염(부위 미상)", "Tendinitis, unspecified", "M77.9", "FB52", "기타", "kb"),
    ("활액막염/건초염", "Synovitis/Tenosynovitis", "M65.9", "FB40", "기타", "kb"),
    # ====== [보강] 발/족지 ======
    ("무지강직", "Hallux rigidus", "M20.2", "FA30", "족부", "kb"),
    ("망치족지/갈퀴족지", "Hammer/Claw toe", "M20.4", "FA31", "족부", "kb"),
    ("발목 불안정증", "Chronic ankle instability", "M25.37", "FA2Z", "족부", "kb"),
    ("족지 골절", "Toe fracture", "S92.4", "NC95", "족부", "kb"),
    # ====== [보강] 수술후/처치후 상태 ======
    ("관절치환술 후 상태(슬관절)", "Status post knee arthroplasty", "Z96.65", "QB50", "기타", "kb"),
    ("내고정물 합병증", "Internal fixation complication", "T84.6", "NE51", "기타", "kb"),
    # ====== [보강] 종양(원본 빈출) ======
    ("지방종", "Lipoma", "D17.9", "2E80", "기타", "kb"),
    ("골연골종(양성골종양)", "Osteochondroma", "D16.9", "2E83", "기타", "kb"),
]
df_dx = pd.DataFrame(diagnosis, columns=["name_ko", "name_en", "kcd_icd10", "icd11", "region", "icd11_src"])

# =====================================================================
# 7. order_type — 처방/오더 유형 (prescription 마스터 분류)
# =====================================================================
order_type = [
    ("약(PO)", "경구약", "NSAIDs, 근이완제, 위장약 등", "펠루비정, 오티렌정, 케이캡정"),
    ("주사(IM/IV)", "근육/정맥 주사", "진통소염, 영양, 스테로이드", "태반주사, 겐타마이신"),
    ("관절강내주사", "관절내 주사", "스테로이드/히알루론산", "관절강내 주사"),
    ("물리치료", "물리치료(modality)", "표층열/심층열/전기/견인", "표층열치료, 심층열치료, ICT, TENS"),
    ("도수치료", "manual therapy", "도수/운동치료", "도수치료"),
    ("체외충격파(ESWT)", "extracorporeal shockwave", "건병증/족저근막염", "체외충격파치료"),
    ("영상검사", "imaging", "X-ray/초음파/MRI/CT", "흉부직접촬영, MRI, 초음파"),
    ("처치/주사시술", "procedure", "신경차단, 천자, 주사시술", "신경총차단, 관절천자"),
    ("진찰료", "consultation fee", "초진/재진 진찰료", "초진진찰료, 재진진찰료"),
    ("보장구/기타", "supplies", "보조기, 의약품관리료 등", "외래환자 의약품관리료"),
    # ====== [보강] 통증의학과 중재시술 ======
    ("신경차단술", "nerve block", "경막외/신경근/교감신경 차단", "경막외차단(TFESI), 성상신경절차단"),
    ("증식치료", "prolotherapy", "인대/건 증식주사(고농도포도당)", "증식치료(prolo)"),
    ("IMS/FIMS", "intramuscular stimulation", "근육내자극술", "IMS, 근막내자극"),
    ("PDRN/DNA주사", "regenerative injection", "연부조직 재생주사", "PDRN, 콜라겐주사"),
    # ====== [보강] 약물 세부분류 ======
    ("약-NSAIDs", "NSAIDs", "비스테로이드소염진통제", "펠루비정, 오티렌정"),
    ("약-근이완제", "muscle relaxant", "근이완제", "에페리손, 세페리손정"),
    ("약-신경병증약", "neuropathic agent", "가바펜틴/프레가발린", "리리카, 뉴론틴"),
    ("약-진통제", "analgesic", "아세트아미노펜/트라마돌", "타이레놀, 울트라셋"),
    ("약-위장보호제", "GI protectant", "PPI/위장약", "케이캡정, 위장약"),
    ("약-스테로이드", "steroid", "단기 경구/주사 스테로이드", "소론도, 트리암"),
    # ====== [보강] 진단검사 ======
    ("전기진단검사", "EMG/NCV", "근전도/신경전도검사", "EMG, NCV"),
    ("골밀도검사", "BMD", "골다공증 골밀도", "BMD(DEXA)"),
    ("혈액검사", "lab", "염증/대사 혈액검사", "CRP, ESR, 요산"),
    # ====== [보강] 보조기/고정 ======
    ("석고/부목", "cast/splint", "골절 고정", "단하지석고, 수지부목"),
    ("보조기", "brace/orthosis", "관절 보조기", "무릎보조기, 허리보조기"),
]
df_ot = pd.DataFrame(order_type, columns=["order_type", "name_en", "description", "example"])

# =====================================================================
# 8. charting_abbrev — 의료차팅 약어/용어
# =====================================================================
abbrev = [
    # 일반/문서
    ("일반", "Sx", "Symptom", "증상"),
    ("일반", "Dx", "Diagnosis", "진단"),
    ("일반", "Tx", "Treatment", "치료"),
    ("일반", "Hx", "History", "병력"),
    ("일반", "Px", "Physical exam / Prognosis", "신체검진/예후"),
    ("일반", "Fx", "Fracture", "골절"),
    ("일반", "c/o", "complains of", "~을 호소함"),
    ("일반", "r/o", "rule out", "감별 대상(배제 위함)"),
    ("일반", "f/u, FU", "follow up", "추적관찰"),
    ("일반", "ROS", "review of systems", "계통 문진"),
    ("일반", "NTD", "nothing to do / not detected", "특이소견 없음"),
    ("일반", "WNL", "within normal limits", "정상 범위"),
    ("일반", "NAD", "no abnormality detected", "이상소견 없음"),
    ("일반", "s/p", "status post", "~수술/처치 후 상태"),
    ("일반", "VAS", "visual analog scale", "통증 척도(0-10)"),
    ("일반", "NRS", "numeric rating scale", "숫자 통증척도"),
    # 측성/방향
    ("측성", "Lt", "Left", "좌측"),
    ("측성", "Rt", "Right", "우측"),
    ("측성", "Both, B/L", "Bilateral", "양측"),
    ("측성", "(+)", "positive", "양성"),
    ("측성", "(-)", "negative", "음성/없음"),
    # 진찰 소견
    ("소견", "ROM", "range of motion", "관절가동범위"),
    ("소견", "LOM", "limitation of motion", "가동범위 제한"),
    ("소견", "TTP", "tenderness to palpation", "촉진시 압통"),
    ("소견", "T/S", "tenderness/swelling", "압통/부종"),
    ("소견", "TP", "tender point / trigger point", "압통점/통증유발점"),
    ("소견", "MT", "muscle tightness/tenderness", "근긴장/압통"),
    ("소견", "Sw", "swelling", "부종"),
    ("소견", "Def", "deformity", "변형"),
    ("소견", "Ecchymosis", "ecchymosis", "반상출혈/멍"),
    ("소견", "Crepitus", "crepitus", "마찰음/염발음"),
    ("소견", "Eff", "effusion", "관절삼출"),
    # 신경학
    ("신경", "MMT", "manual muscle test", "도수근력검사(0-5)"),
    ("신경", "DTR", "deep tendon reflex", "심부건반사"),
    ("신경", "SLR", "straight leg raise", "하지직거상검사"),
    ("신경", "Sensory", "sensory", "감각검사(dermatome)"),
    ("신경", "Motor", "motor", "운동검사(myotome)"),
    ("신경", "G/W", "gait/weakness", "보행/근력저하"),
    ("신경", "Numbness", "numbness/tingling", "저림/감각이상"),
    ("신경", "Radiating pain", "radiating pain", "방사통"),
    # 진단 약어
    ("진단", "OA", "osteoarthritis", "골관절염(퇴행성)"),
    ("진단", "RA", "rheumatoid arthritis", "류마티스 관절염"),
    ("진단", "HNP", "herniated nucleus pulposus", "추간판탈출증(디스크)"),
    ("진단", "IVDP", "intervertebral disc protrusion", "추간판 돌출"),
    ("진단", "DDD", "degenerative disc disease", "퇴행성 디스크"),
    ("진단", "MPS", "myofascial pain syndrome", "근막동통증후군"),
    ("진단", "RC tear", "rotator cuff tear", "회전근개 파열"),
    ("진단", "FS", "frozen shoulder", "동결견(오십견)"),
    ("진단", "ACL/PCL", "ant./post. cruciate ligament", "전/후방십자인대"),
    ("진단", "MCL/LCL", "med./lat. collateral ligament", "내/외측측부인대"),
    ("진단", "CTS", "carpal tunnel syndrome", "수근관증후군"),
    ("진단", "AVN", "avascular necrosis", "무혈성괴사"),
    ("진단", "Spondy", "spondylosis/spondylolisthesis", "척추증/전방전위증"),
    ("진단", "Sprain", "sprain", "염좌(인대 손상)"),
    ("진단", "Strain", "strain", "긴장(근/건 손상)"),
    ("진단", "Contusion", "contusion", "타박상"),
    ("진단", "LBP", "low back pain", "요통"),
    # 처치/처방
    ("처치", "P-T", "physical therapy", "물리치료"),
    ("처치", "PO", "per os (by mouth)", "경구투여"),
    ("처치", "IM", "intramuscular", "근육주사"),
    ("처치", "IV", "intravenous", "정맥주사"),
    ("처치", "IA", "intra-articular", "관절강내주사"),
    ("처치", "NB", "nerve block", "신경차단술"),
    ("처치", "TPI", "trigger point injection", "통증유발점주사"),
    ("처치", "ESWT", "extracorporeal shockwave therapy", "체외충격파"),
    ("처치", "ICT", "interferential current therapy", "간섭파전류치료"),
    ("처치", "TENS", "transcutaneous elec. nerve stim.", "경피신경전기자극"),
    ("처치", "HP/CP", "hot pack/cold pack", "온/냉찜질"),
    ("처치", "US", "ultrasound therapy", "초음파치료"),
    ("처치", "NSAIDs", "non-steroidal anti-inflammatory", "비스테로이드소염제"),
    ("처치", "MRI/CT", "MRI/CT", "자기공명/전산화단층"),
    ("처치", "X-ray", "radiography", "단순방사선촬영"),
    ("처치", "Inj", "injection", "주사"),
    ("처치", "Op", "operation", "수술"),
    ("처치", "Conservative Tx", "conservative treatment", "보존적 치료"),
    # ====== [보강] 병력/문서 ======
    ("일반", "CC", "chief complaint", "주호소"),
    ("일반", "HPI / PI", "history of present illness", "현병력"),
    ("일반", "PHx", "past history", "과거력"),
    ("일반", "FHx", "family history", "가족력"),
    ("일반", "SHx", "social history", "사회력(음주/흡연/직업)"),
    ("일반", "NKDA", "no known drug allergy", "알려진 약물 알레르기 없음"),
    ("일반", "POD", "post-operative day", "수술 후 ~일째"),
    ("일반", "#", "fracture / number", "골절/번호"),
    # ====== [보강] 체중부하/재활 ======
    ("재활", "WB", "weight bearing", "체중부하"),
    ("재활", "NWB", "non-weight bearing", "비체중부하"),
    ("재활", "PWB", "partial weight bearing", "부분체중부하"),
    ("재활", "FWB", "full weight bearing", "완전체중부하"),
    ("재활", "TTWB", "toe-touch weight bearing", "발끝 접촉 체중부하"),
    ("재활", "AROM", "active range of motion", "능동 가동범위"),
    ("재활", "PROM", "passive range of motion", "수동 가동범위"),
    ("재활", "ADL", "activities of daily living", "일상생활동작"),
    # ====== [보강] 운동/방향 ======
    ("방향", "Flex/Ext", "flexion/extension", "굴곡/신전"),
    ("방향", "Abd/Add", "abduction/adduction", "외전/내전"),
    ("방향", "IR/ER", "internal/external rotation", "내회전/외회전"),
    ("방향", "Pron/Sup", "pronation/supination", "회내/회외"),
    ("방향", "Inv/Ev", "inversion/eversion", "내번/외번"),
    ("방향", "DF/PF", "dorsiflexion/plantarflexion", "배측/족저굴곡"),
    # ====== [보강] 신경/반사 추가 ======
    ("신경", "KJ", "knee jerk", "슬개건반사"),
    ("신경", "AJ", "ankle jerk", "아킬레스건반사"),
    ("신경", "Paresthesia", "paresthesia", "이상감각(저림)"),
    ("신경", "UMN/LMN", "upper/lower motor neuron", "상위/하위운동신경원"),
    ("신경", "Hypesthesia", "hypoesthesia", "감각저하"),
    # ====== [보강] 처방 용법 ======
    ("용법", "qd", "once a day", "1일 1회"),
    ("용법", "bid", "twice a day", "1일 2회"),
    ("용법", "tid", "three times a day", "1일 3회"),
    ("용법", "prn", "as needed", "필요시"),
    ("용법", "hs", "at bedtime", "취침시"),
    ("용법", "ac/pc", "before/after meal", "식전/식후"),
    # ====== [보강] 검사/영상 ======
    ("검사", "EMG/NCV", "electromyography / nerve conduction", "근전도/신경전도"),
    ("검사", "BMD", "bone mineral density", "골밀도(T-score)"),
    ("검사", "CRP/ESR", "inflammatory markers", "염증수치"),
    ("검사", "U/S", "ultrasonography", "초음파"),
    ("검사", "C-spine/L-spine", "cervical/lumbar spine", "경추/요추 영상"),
]
df_abbr = pd.DataFrame(abbrev, columns=["category", "abbrev", "full_term", "korean"])

# =====================================================================
# 9. table_relations — 테이블 간 연관관계 요약
# =====================================================================
relations = [
    ("patient", "1:N", "visit", "환자 1명이 여러 내원", "patient_no"),
    ("visit", "M:N", "diagnosis", "visit_diagnosis 브릿지 경유", "visit_diagnosis"),
    ("visit", "M:N", "prescription", "visit_prescription 브릿지 경유", "visit_prescription"),
    ("mst_body_part", "1:N(self)", "mst_body_part", "부위 셀프계층(parent_id)", "parent_id"),
    ("mst_body_part", "M:N", "laterality", "part_laterality(부위별 허용측성, 신규)", "mst_part_laterality"),
    ("mst_body_part", "1:N", "mst_exam_item", "검사의 적용부위/표적구조물", "target_part/target_node"),
    ("mst_value_scale", "1:N", "mst_exam_item", "검사값 척도 참조", "value_type"),
    ("diagnosis", "1:N", "mst_icd_crosswalk", "KCD↔ICD-11 매핑(신규 권장)", "kcd_code"),
    ("diagnosis", "M:N", "mst_body_part", "rel_part_diagnosis(부위↔진단)", "rel_part_diagnosis"),
    ("diagnosis", "M:N", "mst_exam_item", "rel_diagnosis_exam(진단↔검사)", "rel_diagnosis_exam"),
    ("diagnosis", "M:N", "prescription", "rel_diagnosis_order(진단↔처방)", "rel_diagnosis_order"),
    ("mst_body_part", "M:N", "mst_exam_item", "rel_structure_exam(구조물↔검사)", "rel_structure_exam"),
    ("visit", "1:1", "visit_ccf_s", "SOAP-Subjective", "visit_id"),
    ("visit", "1:N", "visit_ccf_o", "SOAP-Objective(검사소견)", "visit_id"),
    ("visit", "1:N", "visit_ccf_a", "SOAP-Assessment(진단)", "visit_id"),
    ("visit", "1:N", "visit_ccf_p", "SOAP-Plan(처방)", "visit_id"),
    ("map_alias", "다형참조", "*", "표기변이→표준코드(target_table별)", "canonical_id"),
]
df_rel = pd.DataFrame(relations, columns=["from_table", "cardinality", "to_table", "description", "via_key"])

# =====================================================================
# 10. neuro_level — 척수신경 레벨별 근절/피부분절/반사 (척추 차팅 핵심 레퍼런스)
# =====================================================================
neuro = [
    ("C5", "삼각근(어깨 외전)", "외측 상완", "이두건반사(C5-6)", "경추"),
    ("C6", "이두근/손목신전(손목 펴기)", "엄지", "상완요골근반사(C6)", "경추"),
    ("C7", "삼두근/손목굴곡/수지신전", "중지", "삼두건반사(C7)", "경추"),
    ("C8", "수지굴곡(쥐기)", "소지", "(없음)", "경추"),
    ("T1", "수지외전(골간근)", "내측 전완", "(없음)", "경추"),
    ("L2", "장요근(고관절 굴곡)", "전대퇴", "(없음)", "요추"),
    ("L3", "대퇴사두근(무릎 폄)", "내측 대퇴/무릎", "슬개건반사(L3-4)", "요추"),
    ("L4", "전경골근(발목 배측굴곡)", "내측 하퇴/복사", "슬개건반사(L4)", "요추"),
    ("L5", "무지신전근(엄지 들기)", "족배/제1지간", "(내측슬괵건)", "요추"),
    ("S1", "비복근/비골근(발목 족저굴곡)", "외측 족부/발바닥", "아킬레스건반사(S1)", "요추"),
    ("S2", "슬괵근(무릎 굽힘)", "후대퇴", "(없음)", "요추"),
]
df_neuro = pd.DataFrame(neuro, columns=["nerve_root", "myotome_근절", "dermatome_피부분절", "reflex_반사", "region"])

# =====================================================================
# 11. mmt_rom_reference — 도수근력 등급 + 관절별 정상 ROM
# =====================================================================
mmt = [
    ("MMT 0", "Zero", "근수축 전혀 없음"),
    ("MMT 1", "Trace", "근수축 감지되나 관절운동 없음"),
    ("MMT 2", "Poor", "중력 제거 시 전 범위 운동"),
    ("MMT 3", "Fair", "중력에 대항해 전 범위 운동"),
    ("MMT 4", "Good", "중력+약간의 저항에 대항"),
    ("MMT 5", "Normal", "중력+완전한 저항에 대항(정상)"),
]
df_mmt = pd.DataFrame(mmt, columns=["grade", "label", "description"])

rom_ref = [
    ("경추", "굴곡/신전", "50° / 60°"),
    ("경추", "측방굴곡/회전", "45° / 80°"),
    ("요추", "굴곡/신전", "60° / 25°"),
    ("어깨", "굴곡/외전", "180° / 180°"),
    ("어깨", "외회전/내회전", "90° / 70°"),
    ("팔꿈치", "굴곡/신전", "150° / 0°"),
    ("전완", "회내/회외", "80° / 80°"),
    ("손목", "굴곡/신전", "80° / 70°"),
    ("고관절", "굴곡/신전", "120° / 30°"),
    ("고관절", "외전/내전", "45° / 30°"),
    ("고관절", "내회전/외회전", "45° / 45°"),
    ("무릎", "굴곡/신전", "135° / 0°"),
    ("발목", "배측/족저굴곡", "20° / 50°"),
]
df_rom = pd.DataFrame(rom_ref, columns=["joint", "motion", "normal_ROM"])

# =====================================================================
# 12. subjective_vocab — S(주관적) 섹션 표준 용어 (onset/mechanism/quality 등)
# =====================================================================
subj = [
    ("onset", "급성", "acute", "수일 이내 발생"),
    ("onset", "아급성", "subacute", "수주"),
    ("onset", "만성", "chronic", "3개월 이상"),
    ("onset", "재발성", "recurrent", "반복 발생"),
    ("mechanism", "외상 없음", "atraumatic", "특별한 외상 없이"),
    ("mechanism", "낙상", "fall", "넘어짐"),
    ("mechanism", "교통사고", "MVA/TA", "교통사고"),
    ("mechanism", "들다가(거상)", "lifting", "물건 들다가"),
    ("mechanism", "비틀림", "twisting", "삐끗/회전 손상"),
    ("mechanism", "반복사용", "overuse", "반복 동작/과사용"),
    ("mechanism", "스포츠손상", "sports injury", "운동 중 손상"),
    ("pain_quality", "쑤심/뻐근", "dull/aching", "둔통"),
    ("pain_quality", "찌릿/방사", "sharp/radiating", "예리/방사통"),
    ("pain_quality", "화끈거림", "burning", "작열통(신경병증)"),
    ("pain_quality", "저림/감각이상", "tingling/numb", "이상감각"),
    ("pain_quality", "쥐어짜는", "cramping", "경련성"),
    ("aggravating", "기침/재채기", "cough/sneeze", "추간판/신경근(Valsalva)"),
    ("aggravating", "보행 시", "with walking", "협착증/관절"),
    ("aggravating", "기상 시(조조강직)", "morning stiffness", "염증성/퇴행성"),
    ("aggravating", "앉아있을 때", "with sitting", "추간판성"),
    ("aggravating", "야간통", "night pain", "종양/염증/회전근개"),
    ("relieving", "휴식 시", "with rest", "기계적 통증"),
    ("relieving", "자세 변경", "position change", "신경성/관절성"),
]
df_subj = pd.DataFrame(subj, columns=["axis", "term_ko", "term_en", "note"])

# =====================================================================
# 13. red_flag — 위험징후 마스터 (환자안전·진료 의뢰 판단)
# =====================================================================
red_flag = [
    ("마미증후군", "안장마비/배뇨·배변장애/양측 하지마비·진행성", "응급 MRI + 즉시 척추수술 의뢰", "놓치면 영구 신경손상 — 응급 1순위"),
    ("척수병증", "보행장애·손 기민성저하·Hoffmann/Babinski 양성", "경추 MRI + 신경외과 의뢰", "경추 압박성 척수증 조기진단"),
    ("악성종양 전이", "50세↑ 신규통증·암 과거력·체중감소·야간통·안정시통증", "영상 + 종양 평가 의뢰", "전이성 척추종양 선별"),
    ("척추 감염", "발열·야간발한·면역저하·IV약물·정맥주사력", "CRP/ESR·혈액배양·MRI", "화농성 척추염/경막외농양"),
    ("골절(취약/외상)", "고에너지 외상·골다공증·장기 스테로이드·국소 극심통", "영상(필요시 CT/MRI)", "압박골절/잠복골절 누락 방지"),
    ("복부대동맥류(AAA)", "박동성 복부종괴·요통+복통·고령 흡연", "응급 초음파/CT", "파열 시 치명 — 요통 감별"),
    ("화농성 관절염", "단일관절 급성 발적·열감·발열·체중부하 불가", "관절천자·혈액검사·응급의뢰", "수시간 내 연골파괴"),
    ("신경학적 진행", "근력 급속 악화·foot drop·다분절 신경증상", "조기 영상 + 의뢰", "수술적 감압 시기 결정"),
]
df_rf = pd.DataFrame(red_flag, columns=["category", "sign_징후", "action_조치", "필요이유"])

# =====================================================================
# 14. imaging_findings — 영상소견 표준어휘 (O/A 섹션 구조화)
# =====================================================================
imaging = [
    ("X-ray", "관절간격 협소(JSN)", "joint space narrowing", "퇴행성 관절염 중증도(KL grade 근거)"),
    ("X-ray", "골극(osteophyte)", "osteophyte/spur", "골관절염 소견"),
    ("X-ray", "연골하 경화", "subchondral sclerosis", "퇴행성 변화"),
    ("X-ray", "정렬이상/전위", "malalignment/listhesis", "전방전위증·골절 전위"),
    ("X-ray", "골절선", "fracture line", "골절 진단"),
    ("MRI-척추", "추간판 팽윤", "disc bulge", "광범위 디스크 변화"),
    ("MRI-척추", "추간판 돌출", "disc protrusion", "국소 추간판탈출(경증)"),
    ("MRI-척추", "추간판 탈출", "disc extrusion", "신경근 압박 추간판탈출"),
    ("MRI-척추", "수핵 분리", "sequestration", "유리된 수핵 조각"),
    ("MRI-척추", "Modic 변화", "Modic change type 1-3", "종판/골수 변화(통증 연관)"),
    ("MRI-척추", "신경공 협착", "foraminal stenosis", "신경근 압박"),
    ("MRI-척추", "황색인대 비후", "ligamentum flavum hypertrophy", "중심성 협착"),
    ("MRI-관절", "회전근개 전층파열", "full-thickness RC tear", "수술 적응 판단"),
    ("MRI-관절", "회전근개 부분파열", "partial-thickness tear", "보존치료 대상"),
    ("MRI-관절", "반월상연골 파열", "meniscal tear", "무릎 internal derangement"),
    ("MRI-관절", "골수 부종", "bone marrow edema", "잠복골절/골좌상/염증"),
    ("MRI-관절", "연골 결손", "cartilage defect", "Outerbridge grade 근거"),
    ("US", "관절 삼출", "joint effusion", "활액막염/염증"),
    ("US", "건병증/석회화", "tendinopathy/calcification", "건 병변·석회성건염"),
]
df_img = pd.DataFrame(imaging, columns=["modality", "finding_소견", "term_en", "필요이유"])

# =====================================================================
# 15. grading_scale — 정형외과 등급분류 체계 (중증도 표준화)
# =====================================================================
grading = [
    ("Kellgren-Lawrence", "무릎 등 관절 OA(X-ray)", "0~4", "골관절염 방사선 중증도 표준", "web"),
    ("Outerbridge", "연골 손상(관절경)", "0~4", "연골 손상 깊이 등급", "web"),
    ("Pfirrmann", "추간판 퇴행(MRI)", "I~V", "디스크 퇴행 정도", "kb"),
    ("Modic", "추간판 종판/골수 변화", "1~3", "종판 변화 유형", "kb"),
    ("Garden", "대퇴경부 골절", "I~IV", "전위 정도→치료방침(고정 vs 치환)", "kb"),
    ("Danis-Weber", "발목 골절(외과)", "A/B/C", "비골 골절 위치→안정성", "kb"),
    ("Salter-Harris", "소아 성장판 골절", "I~V", "성장판 침범→예후/성장장애", "kb"),
    ("Neer", "상완골 근위부 골절", "1~4 part", "골편 수→수술 적응", "kb"),
    ("ASIA", "척수손상", "A~E", "신경학적 손상 완전성", "kb"),
    ("Tönnis", "고관절 OA(X-ray)", "0~3", "고관절염 중증도", "kb"),
    ("MRC(영국)", "도수근력", "0~5", "근력 등급(=MMT)", "kb"),
    ("House-Brackmann", "안면신경(참고)", "I~VI", "신경마비 등급(타과 참고)", "kb"),
]
df_grade = pd.DataFrame(grading, columns=["scale", "적용", "grades", "필요이유", "src"])

# =====================================================================
# 16. outcome_scale — 기능평가 척도(PROM)
# =====================================================================
outcome = [
    ("VAS/NRS", "통증(전부위)", "0~10", "통증 강도 추적의 기본 지표"),
    ("ODI (Oswestry)", "요추", "0~100%", "요통 기능장애 표준 PROM"),
    ("NDI", "경추", "0~100%", "목 장애 지수"),
    ("Roland-Morris", "요추", "0~24", "요통 기능 설문(간이)"),
    ("WOMAC", "무릎/고관절 OA", "0~96", "관절염 통증·기능"),
    ("KOOS", "무릎", "0~100", "무릎 손상/관절염 결과"),
    ("Lysholm", "무릎(인대)", "0~100", "무릎 인대손상 기능"),
    ("HOOS", "고관절", "0~100", "고관절 결과 점수"),
    ("Constant-Murley", "어깨", "0~100", "어깨 종합 기능"),
    ("ASES", "어깨", "0~100", "어깨 통증·기능"),
    ("DASH/QuickDASH", "상지 전체", "0~100", "상지 장애 설문"),
    ("AOFAS", "발/발목", "0~100", "족부 기능 점수"),
]
df_outcome = pd.DataFrame(outcome, columns=["scale", "적용부위", "범위", "필요이유"])

# =====================================================================
# 17. medication — 정형/통증과 상용 약물 마스터 (성분·계열)
# =====================================================================
medication = [
    ("NSAID", "아세클로페낙", "에어탈", "소염진통 1차 — 근골격계 통증"),
    ("NSAID", "펠루비프로펜", "펠루비", "원본 데이터 빈출 NSAID"),
    ("NSAID", "세레콕시브(COX-2)", "쎄레브렉스", "위장장애 위험군 선택적 COX-2"),
    ("NSAID", "록소프로펜", "록소닌", "급성 통증 상용"),
    ("NSAID", "멜록시캄", "모빅", "1일 1회 NSAID"),
    ("근이완제", "에페리손", "뮤렉스/엑소페린", "근경직·근막통 동반 시"),
    ("근이완제", "톨페리손", "미도카", "중추성 근이완"),
    ("신경병증약", "프레가발린", "리리카", "신경병증통증·방사통(PHN·신경근병증)"),
    ("신경병증약", "가바펜틴", "뉴론틴", "신경병증통증"),
    ("신경병증약", "둘록세틴", "심발타", "만성 근골격통·신경병증"),
    ("진통제", "아세트아미노펜", "타이레놀", "기본 진통(원본 빈출)"),
    ("진통제", "트라마돌/AAP", "울트라셋", "중등도 통증 복합진통"),
    ("위장보호", "P-CAB(테고프라잔)", "케이캡", "NSAID 병용 위장보호(원본 빈출)"),
    ("위장보호", "레바미피드", "무코스타", "위점막 보호"),
    ("스테로이드", "트리암시놀론", "트리암", "관절강내/국소주사"),
    ("스테로이드", "프레드니솔론", "소론도", "단기 경구 항염"),
    ("골다공증약", "알렌드로네이트", "포사맥스", "골다공증 1차(비스포스포네이트)"),
    ("골다공증약", "데노수맙", "프롤리아", "6개월 1회 주사"),
    ("골다공증약", "테리파라타이드", "포스테오", "중증 골다공증 골형성촉진"),
    ("혈류개선", "리마프로스트", "오팔몬", "척추관협착증 신경인성 파행"),
    ("주사(관절)", "히알루론산", "히루안/시노비안", "관절강내 점탄성보충"),
    ("주사(재생)", "PDRN", "리쥬비넥스", "연부조직 재생주사"),
]
df_med = pd.DataFrame(medication, columns=["class_계열", "ingredient_성분", "brand_예시", "필요이유"])

# =====================================================================
# 18. rel_diagnosis_exam — 진단↔핵심검사 표준 매핑 (차팅 누락 알림 근거)
# =====================================================================
dx_exam = [
    ("요추 신경근병증(HNP)", "SLR test", "양성(하지직거상 통증)", "HNP인데 SLR 미기재 시 누락 알림"),
    ("척추관 협착증", "Neurogenic claudication", "보행거리 단축", "협착 차팅 핵심 지표"),
    ("경추 신경근병증", "Spurling test", "양성(방사통 재현)", "경추 radiculopathy 확인"),
    ("동결견(오십견)", "ROM(외회전)", "수동/능동 모두 제한", "오십견 진단의 정의적 소견"),
    ("회전근개 파열", "Empty can / Drop arm", "양성", "파열 선별 핵심검사"),
    ("어깨 충돌증후군", "Neer / Hawkins", "양성", "충돌 확인"),
    ("외측상과염", "Cozen / Mill", "양성", "테니스엘보 진단"),
    ("수근관증후군", "Phalen / Tinel / Durkan", "양성", "CTS 유발검사"),
    ("드꿰르뱅 건초염", "Finkelstein", "양성", "1구획 건초염 진단"),
    ("반월상연골 파열", "McMurray / Apley", "양성(clicking/통증)", "연골 파열 선별"),
    ("전방십자인대 파열", "Lachman / Anterior drawer", "양성(전방 이완)", "ACL 손상 핵심검사"),
    ("내측측부인대 손상", "Valgus stress", "양성", "MCL 손상"),
    ("발목 외측인대 손상", "Anterior drawer / Talar tilt", "양성", "발목염좌 등급"),
    ("족저근막염", "Windlass test", "양성", "족저근막염 유발"),
    ("이상근증후군", "Piriformis / FAIR", "양성", "이상근성 좌골신경통"),
    ("천장관절통", "SI provocation cluster", "3개 이상 양성", "SI관절 기원 통증 진단"),
    ("고관절 관절내병변", "FADIR / Log roll", "양성", "FAI/관절순 병변"),
]
df_dxex = pd.DataFrame(dx_exam, columns=["diagnosis", "key_exam", "positive_소견", "필요이유"])

# =====================================================================
# 19. peripheral_nerve — 말초신경 포착/손상 마스터
# =====================================================================
nerve = [
    ("정중신경", "수근관(손목)", "무지~중지 저림·무지구 위축", "Phalen/Tinel/Durkan", "수근관증후군"),
    ("척골신경", "주관절(cubital)/Guyon관", "4-5지 저림·골간근 위축·Froment", "Tinel(elbow)/Froment", "주관절증후군"),
    ("요골신경", "나선구/회외근증후군", "wrist drop·손등 감각저하", "근력검사", "요골신경마비"),
    ("좌골신경", "이상근/둔부", "둔부~하지 후면 방사통", "Piriformis/FAIR", "이상근증후군"),
    ("총비골신경", "비골두", "foot drop·족배 감각저하", "근력(배측굴곡)", "비골신경마비"),
    ("후경골신경", "족근관(내과 후방)", "발바닥 저림·작열통", "Tinel(tarsal)", "족근관증후군"),
    ("대퇴신경", "L2-4/서혜부", "무릎 신전약화·전대퇴 감각", "FNST", "대퇴신경병증"),
    ("외측대퇴피신경", "서혜인대", "외측 대퇴 작열통(감각만)", "감각검사", "감각이상성 대퇴신경통"),
    ("지간신경(족부)", "중족골두 사이", "전족부 통증·Mulder click", "Mulder sign", "모르톤 신경종"),
]
df_nerve = pd.DataFrame(nerve, columns=["nerve_신경", "site_포착부위", "symptom_증상", "exam_검사", "관련진단"])
df_nerve["필요이유"] = [f"{r.site_포착부위} 포착 시 '{r.관련진단}' — 신경분포 패턴으로 감별" for r in df_nerve.itertuples(index=False)]

# =====================================================================
# [공통] 각 시트에 '필요이유'/설명 컬럼 부여
# =====================================================================
def add_reason(df, reason_fn, col="필요이유"):
    if col not in df.columns:
        df[col] = [reason_fn(r) for r in df.itertuples(index=False)]
    return df

# body_part: 노드 유형/부위별 임상적 필요이유 + description
def _bp_desc(r):
    return f"{r.name_en} ({r.node_type})"
def _bp_reason(r):
    if r.node_type == "근육":
        return "MPS·근막통 차팅 및 압통점(트리거포인트) 주사 위치 지정"
    if "극돌기" in r.name_ko or r.midline:
        return "정중선 구조 압통(골절/염좌) 국소화 — 좌우 입력 차단"
    if "후관절" in r.name_ko:
        return "후관절성 통증·중재시술(내측지차단) 표적 레벨"
    if r.node_type in ("부위", "영역"):
        return "통증 부위 대분류 — 트리/네비게이션 상위 노드"
    return "국소 압통/병변 부위를 구조물 단위로 정확히 지정"
df_bp = add_reason(df_bp, _bp_reason)
if "description" not in df_bp.columns:
    df_bp["description"] = [_bp_desc(r) for r in df_bp.itertuples(index=False)]

df_lat = add_reason(df_lat, lambda r: "병변 위치의 좌/우/정중 구분 — 진단·청구·UI 선택 표준화")
df_vs = add_reason(df_vs, lambda r: "검사 결과를 일관된 형식으로 저장·해석하기 위한 값 척도")
df_pl = add_reason(df_pl, lambda r: ("정중선 구조에 좌/우 오입력 방지(무결성)" if r.laterality == "C" else "관절/구조물의 좌우·양측 측성 허용"))
df_exam = add_reason(df_exam, lambda r: f"양성 시 '{r.tests_for}' 시사 — O섹션 이학적 소견 구조화")
df_dx = add_reason(df_dx, lambda r: f"{r.region} 주요 진단 — KCD↔ICD-11 표준화로 청구·통계·연구 일관성")
df_ot = add_reason(df_ot, lambda r: "처방/오더를 유형별 분류 — P섹션 구조화·청구패턴 분석")
df_abbr = add_reason(df_abbr, lambda r: "차팅 원문의 약어를 표준 의미로 해석 — LLM 추출 정확도 향상")
df_neuro = add_reason(df_neuro, lambda r: f"{r.nerve_root} 신경학적 진찰(근력/감각/반사)을 분절로 매핑 — HNP·협착 레벨 국소화")
df_mmt = add_reason(df_mmt, lambda r: "도수근력 등급 기준 — motor 검사값 해석의 정답지")
df_rom = add_reason(df_rom, lambda r: "정상 가동범위 기준 — ROM 측정값의 제한 여부 판정")
df_subj = add_reason(df_subj, lambda r: f"S(주관적) 섹션 '{r.axis}' 표준어휘 — 문진 구조화·red flag 단서")
df_rel = add_reason(df_rel, lambda r: f"{r.from_table}↔{r.to_table} 관계 — 조인/무결성 설계 근거")

# =====================================================================
# 20. sheet_guide — 시트별 설명·필요이유 (워크북 메타)
# =====================================================================
sheet_guide = [
    ("laterality", "측성 마스터", "L/R/B/C 4값", "모든 병변의 좌우·정중 표준화(필수 lookup)"),
    ("value_scale", "검사값 척도", "결과 표기 형식", "이학적 검사값을 일관 저장·해석"),
    ("body_part", "부위 트리", "셀프계층 부위/구조물/근육", "통증·압통·병변의 해부학적 위치 마스터"),
    ("part_laterality", "부위별 허용측성", "노드×측성", "정중선 오입력 차단(데이터 무결성)"),
    ("exam_item", "검사 카탈로그", "special test·근력·감각·반사", "O섹션 이학적 검사 구조화"),
    ("diagnosis", "진단 마스터", "KCD/ICD-11/영문", "A섹션 진단 코드 표준화"),
    ("order_type", "오더 유형", "약·주사·물리·중재·검사", "P섹션 처방 분류"),
    ("charting_abbrev", "차팅 약어", "실제 사용 약어 113개", "원문 약어→표준의미(추출 정확도)"),
    ("neuro_level", "신경분절 매핑", "근절/피부분절/반사", "척추 신경학적 진찰의 레퍼런스"),
    ("mmt_grade", "근력 등급", "0~5", "근력 검사값 해석 기준"),
    ("rom_reference", "정상 ROM", "관절별 각도", "가동범위 제한 판정 기준"),
    ("subjective_vocab", "S섹션 어휘", "onset/mechanism/quality", "문진 구조화·red flag 단서"),
    ("red_flag", "위험징후", "마미·종양·감염·골절 등", "환자안전·응급 의뢰 판단(필수)"),
    ("imaging_findings", "영상소견 어휘", "X-ray/MRI/US 표준소견", "O/A섹션 영상결과 구조화"),
    ("grading_scale", "등급분류", "KL/Outerbridge/Garden 등", "중증도 표준화·치료방침 결정"),
    ("outcome_scale", "기능평가척도", "ODI/NDI/WOMAC 등 PROM", "치료 전후 기능 추적"),
    ("medication", "약물 마스터", "성분·계열·브랜드", "처방 풀네임/계열 매핑(절단 보강)"),
    ("rel_diagnosis_exam", "진단↔검사 매핑", "진단별 핵심검사", "차팅 누락 알림 근거(CCF)"),
    ("peripheral_nerve", "말초신경", "포착부위·증상·검사", "신경포착증후군 진단 지원"),
    ("table_relations", "테이블 관계", "FK·카디널리티", "스키마 조인/무결성 설계"),
]
df_guide = pd.DataFrame(sheet_guide, columns=["sheet", "한글명", "description", "필요이유"])

# =====================================================================
# README 시트
# =====================================================================
readme = [
    ("목적", "현재 스키마의 정형외과 마스터 테이블을 도메인지식+웹검증으로 채운 시드 데이터"),
    ("작성", "2026-06-11"),
    ("ICD-11 출처", "FA80/FA82/FA84/FB53.x/FA01.x 등 주요코드 WHO ICD-11 MMS 웹검증(findacode 등)"),
    ("icd11_src 컬럼", "web=웹검증, kb=도메인지식(미검증, 공식 브라우저 재확인 권장)"),
    ("주의", "ICD-11 일부 하위코드는 근사치 — 실제 청구/통계 전 WHO ICD-11 브라우저 필수 재확인"),
    ("시트: laterality", "측성 마스터 (L/R/B/C)"),
    ("시트: value_scale", "검사값 척도"),
    ("시트: body_part", "부위 트리(셀프계층) — id/parent_id/midline"),
    ("시트: part_laterality", "부위별 허용 측성(신규 제안 테이블)"),
    ("시트: exam_item", "정형외과 검사/special test 카탈로그"),
    ("시트: diagnosis", "정형외과 진단 KCD(ICD-10)/ICD-11/영문"),
    ("시트: order_type", "처방/오더 유형 분류"),
    ("시트: charting_abbrev", "실제 차팅 약어/용어"),
    ("시트: neuro_level", "척수신경 레벨별 근절/피부분절/반사(척추 차팅 핵심)"),
    ("시트: mmt_grade", "도수근력 0~5등급 기준"),
    ("시트: rom_reference", "관절별 정상 가동범위 참조값"),
    ("시트: subjective_vocab", "S(주관적)섹션 표준용어(onset/mechanism/quality)"),
    ("시트: table_relations", "테이블 간 연관관계 요약"),
    ("보강(2차)", "흉추전체·TMJ·늑골·근육 / SI관절·TOS검사 / PHN·섬유근통·이상근 / IMS·신경차단 / 신경레벨·ROM 레퍼런스 추가"),
]
df_readme = pd.DataFrame(readme, columns=["항목", "내용"])

# =====================================================================
# 저장
# =====================================================================
os.makedirs(OUT_DIR, exist_ok=True)
sheets = {
    "README": df_readme,
    "sheet_guide": df_guide,
    "laterality": df_lat,
    "value_scale": df_vs,
    "body_part": df_bp,
    "part_laterality": df_pl,
    "exam_item": df_exam,
    "diagnosis": df_dx,
    "order_type": df_ot,
    "charting_abbrev": df_abbr,
    "neuro_level": df_neuro,
    "mmt_grade": df_mmt,
    "rom_reference": df_rom,
    "subjective_vocab": df_subj,
    "red_flag": df_rf,
    "imaging_findings": df_img,
    "grading_scale": df_grade,
    "outcome_scale": df_outcome,
    "medication": df_med,
    "rel_diagnosis_exam": df_dxex,
    "peripheral_nerve": df_nerve,
    "table_relations": df_rel,
}
with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
    for name, df in sheets.items():
        df.to_excel(xw, sheet_name=name, index=False)

print(f"저장: {OUT}")
for name, df in sheets.items():
    print(f"  - {name}: {len(df)} 행 x {len(df.columns)} 열")
