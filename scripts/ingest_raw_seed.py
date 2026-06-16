"""raw_seed_data → 워크북 100% 병합.

pain_data.md(부위+측성)와 diagnosis_icdcode_map_data.md(진단+ICD)를 직접 파싱해
build_master_workbook.py가 만든 워크북에서 누락된 항목을 모두 추가한다.
build 스크립트가 노출하는 sheets 딕셔너리를 재사용한다.
실행: python scripts/ingest_raw_seed.py
"""
from __future__ import annotations

import re

import pandas as pd

import importlib.util, os
# build 스크립트의 sheets/df들을 그대로 import (재실행해 최신 상태 확보)
spec = importlib.util.spec_from_file_location("bmw", os.path.join(os.path.dirname(__file__), "build_master_workbook.py"))
bmw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bmw)  # 워크북 1차 생성 + df 객체 보유

OUT = bmw.OUT

# 부위 섹션 헤더 → (region, parent_id)
PAIN_REGION = {
    "1": ("척추", 1), "2": ("어깨", 2), "3": ("팔꿈치", 3), "4": ("수부", 4),
    "5": ("고관절", 5), "6": ("무릎", 6), "7": ("족부", 7),
}
LAT_MAP = {"중앙": "C", "양측": "B", "좌": "L", "우": "R"}


def parse_lat(text: str) -> set[str]:
    s = set()
    for k, v in LAT_MAP.items():
        if k in text:
            s.add(v)
    return s or {"B", "L", "R"}


def guess_node_type(name: str, lat: set[str]) -> str:
    if "후관절" in name or "관절선" in name or "관절부" in name or "관절(" in name:
        return "레벨"
    if lat == {"C"}:
        return "구조물"
    return "구조물"


# ---------------- pain_data.md 파싱 ----------------
pain = open("raw_seed_data/pain_data.md", encoding="utf-8").read().splitlines()
region, parent = "척추", 1
parsed_parts = []  # (name_ko, name_en, region, parent, node_type, midline, lat_set)
cur_lat_default = {"B", "L", "R"}
for ln in pain:
    mh = re.match(r"^##\s*(\d)\)", ln)
    if mh:
        region, parent = PAIN_REGION.get(mh.group(1), (region, parent))
        continue
    # 그룹 단위 측성 선언 (예: 측성(모든 항목 동일): 양측, 좌, 우)
    mg = re.search(r"측성[^:：]*[:：]\s*([가-힣,\s]+)$", ln.strip())
    if mg and "(" not in ln:
        cur_lat_default = parse_lat(mg.group(1))
    # 항목: 한글(영문) — ... 측성: ...
    m = re.match(r"^\*?\s*([^()\n*][^()\n]*?)\(([A-Za-z][^)]*)\)\s*(.*)$", ln.strip())
    if not m:
        continue
    name_ko = m.group(1).strip(" *-")
    name_en = m.group(2).strip()
    rest = m.group(3)
    if not name_ko or len(name_ko) > 40:
        continue
    lat = parse_lat(rest) if "측성" in rest else cur_lat_default
    nt = guess_node_type(name_ko, lat)
    parsed_parts.append((name_ko, name_en, region, parent, nt, lat == {"C"}, lat))

# ---------------- 워크북 body_part 병합 ----------------
df_bp = bmw.df_bp.copy()
existing_ko = set(df_bp.name_ko.astype(str))
existing_en = " ".join(df_bp.name_en.astype(str)).lower()
next_id = 3000
node_lat = {}  # new_id -> lat set
add_rows = []
for name_ko, name_en, reg, par, nt, midline, lat in parsed_parts:
    en_core = re.split(r"[ ,/;]", name_en)[0].lower()
    if name_ko in existing_ko or (len(en_core) > 3 and en_core in existing_en):
        continue
    add_rows.append({
        "id": next_id, "parent_id": par, "name_ko": name_ko, "name_en": name_en,
        "node_type": nt, "region": reg, "midline": midline,
        "필요이유": ("정중선 구조 압통 국소화 — 좌우 입력 차단" if midline else "손/발가락·세부 구조물 압통 위치 지정"),
        "description": f"{name_en} ({nt}) [raw_seed]",
    })
    node_lat[next_id] = lat
    existing_ko.add(name_ko)
    next_id += 1
df_bp_merged = pd.concat([df_bp, pd.DataFrame(add_rows)], ignore_index=True)

# part_laterality 재생성 (parsed 측성 우선)
pl_rows = []
for r in df_bp_merged.itertuples(index=False):
    lats = node_lat.get(r.id)
    if lats is None:
        lats = {"C"} if r.midline else {"B", "L", "R"}
    for code in sorted(lats):
        pl_rows.append((r.id, r.name_ko, code,
                        "중앙만" if code == "C" and lats == {"C"} else "raw_seed" if r.id in node_lat else ""))
df_pl_merged = pd.DataFrame(pl_rows, columns=["body_part_id", "body_part_name", "laterality", "note", "필요이유"][:4])
df_pl_merged["필요이유"] = ["정중선 좌우 오입력 방지" if c == "C" else "허용 측성" for c in df_pl_merged.laterality]

# ---------------- diagnosis_map.md 파싱 ----------------
dxmd = open("raw_seed_data/diagnosis_icdcode_map_data.md", encoding="utf-8").read().splitlines()
DX_REGION = {"1": "척추", "2": "무릎", "3": "고관절", "4": "어깨", "5": "수부", "6": "족부", "7": "소아", "8": "기타"}
region = "기타"
parsed_dx = []  # (name_ko, name_en, icd10, icd11, region)
for ln in dxmd:
    mh = re.match(r"^###\s*(\d)\.", ln)
    if mh:
        region = DX_REGION.get(mh.group(1), region)
        continue
    if not ln.strip().startswith("|"):
        continue
    cells = [c.strip() for c in ln.strip().strip("|").split("|")]
    # 표1형식: 번호|한글|ICD-10|ICD-11   /  제미나이: 분류|한글|영문|ICD-10|ICD-11
    icd10 = icd11 = name_ko = name_en = ""
    if len(cells) >= 4 and re.match(r"^\d+$", cells[0]):
        name_ko, icd10, icd11 = cells[1], cells[2], cells[3]
    elif len(cells) >= 5 and re.search(r"[가-힣]", cells[0]) and re.match(r"^[A-Z]\d", cells[3]):
        region = cells[0]
        name_ko, name_en, icd10, icd11 = cells[1], cells[2], cells[3], cells[4]
    else:
        continue
    icd10 = re.sub(r"[\\*\s]", "", icd10)
    if not re.match(r"^[A-Z]\d", icd10):
        continue
    parsed_dx.append((name_ko, name_en, icd10, icd11.strip("* "), region))

df_dx = bmw.df_dx.copy()
have_codes = set(df_dx.kcd_icd10.str.extract(r"([A-Z]\d{2})")[0].dropna())
have_names = set(df_dx.name_ko.astype(str))
add_dx = []
for name_ko, name_en, icd10, icd11, reg in parsed_dx:
    c3 = re.match(r"([A-Z]\d{2})", icd10).group(1)
    if name_ko in have_names:
        continue
    # 같은 3자리 코드가 이미 2개 이상이면 스킵(중복 진단명 폭증 방지), 신규 코드는 무조건 추가
    if c3 in have_codes and sum(df_dx.kcd_icd10.str.startswith(c3)) >= 2:
        continue
    add_dx.append({
        "name_ko": name_ko, "name_en": name_en or "", "kcd_icd10": icd10,
        "icd11": icd11 or "(미조회)", "region": reg, "icd11_src": "raw",
        "필요이유": f"{reg} 진단(raw_seed 보강) — KCD 코드 표준화",
    })
    have_names.add(name_ko)
    have_codes.add(c3)
df_dx_merged = pd.concat([df_dx, pd.DataFrame(add_dx)], ignore_index=True)

# ---------------- 재저장 ----------------
sheets = dict(bmw.sheets)
sheets["body_part"] = df_bp_merged
sheets["part_laterality"] = df_pl_merged
sheets["diagnosis"] = df_dx_merged
with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
    for name, df in sheets.items():
        df.to_excel(xw, sheet_name=name, index=False)

print(f"raw 병합 완료 → {OUT}")
print(f"  body_part: {len(df_bp)} → {len(df_bp_merged)} (+{len(add_rows)} raw 부위)")
print(f"  part_laterality: {len(df_pl_merged)} 행")
print(f"  diagnosis: {len(df_dx)} → {len(df_dx_merged)} (+{len(add_dx)} raw 진단)")
