#!/usr/bin/env python3
"""data.ts のコンテンツ品質を自動検証するスクリプト。
使い方: python pipeline/qc_data.py Paper12
"""

import re
import sys
from pathlib import Path

PAPER_ID = sys.argv[1] if len(sys.argv) > 1 else None
DATA_TS = Path(__file__).parent.parent / "src" / "data.ts"

# ── テキスト長の上限値（経験則） ──────────────────────────────────
LIMITS = {
    "title":           20,   # 改行込みで20文字以内
    "titleShort":      15,
    "bgContext":      120,
    "bgProblem":      120,
    "bgImportance":   100,
    "findingHeadline": 40,
    "finding_title":   18,
    "finding_detail":  60,
    "mechStep_title":  18,
    "mechStep_detail": 60,
    "relIntro":        80,
    "relCard_heading": 10,
    "relCard_body":    50,
    "actionSummary":   40,
    "action_action":   20,
    "action_note":     60,
    "chart_title":     28,
    "chart_subtitle":  40,
    "point_label":     25,
    "point_value":     25,
}

# ── 推奨件数 ──────────────────────────────────────────────────────
COUNTS = {
    "findings":    (3, 5),
    "mechSteps":   (4, 7),
    "relCards":    (3, 5),
    "actions":     (3, 4),
    "chartPoints": (3, 5),
}

def check_len(field: str, value: str, limit: int) -> list[str]:
    clean = value.replace("\\n", "\n").replace("\n", "")
    if len(clean) > limit:
        return [f"  ⚠️  {field}: {len(clean)}文字（上限 {limit}文字）— 「{clean[:30]}…」"]
    return []

def run():
    text = DATA_TS.read_text()
    issues = []

    if PAPER_ID:
        # 対象 PaperID のブロックだけ抽出
        pattern = rf'id:\s*"{PAPER_ID}".*?(?=\{{\s*id:|$)'
        match = re.search(pattern, text, re.DOTALL)
        if not match:
            print(f"  ❌ {PAPER_ID} が data.ts に見つかりません")
            sys.exit(1)
        block = match.group(0)
        papers = [PAPER_ID]
    else:
        block = text
        papers = re.findall(r'id:\s*"(Paper\d+)"', text)

    def extract(key, src=block):
        m = re.search(rf'{key}:\s*"(.*?)"', src, re.DOTALL)
        return m.group(1).strip() if m else ""

    def extract_list(pattern, src=block):
        return re.findall(pattern, src, re.DOTALL)

    paper_label = PAPER_ID or "全論文"
    print(f"  📋 {paper_label} のコンテンツ検証:")

    # ── 基本フィールド長チェック ──
    for field, limit in [
        ("title",           LIMITS["title"]),
        ("titleShort",      LIMITS["titleShort"]),
        ("bgContext",       LIMITS["bgContext"]),
        ("bgProblem",       LIMITS["bgProblem"]),
        ("bgImportance",    LIMITS["bgImportance"]),
        ("findingHeadline", LIMITS["findingHeadline"]),
        ("actionSummary",   LIMITS["actionSummary"]),
        ("relIntro",        LIMITS["relIntro"]),
    ]:
        val = extract(field)
        issues += check_len(field, val, limit)

    # ── findings 件数と各フィールド ──
    finding_blocks = re.findall(
        r'\{[^}]*icon:\s*"[^"]*"[^}]*title:\s*"([^"]*)"[^}]*detail:\s*"([^"]*)"[^}]*\}',
        block
    )
    n = len(finding_blocks)
    lo, hi = COUNTS["findings"]
    if not (lo <= n <= hi):
        issues.append(f"  ⚠️  findings: {n}件（推奨 {lo}〜{hi}件）")
    for i, (title, detail) in enumerate(finding_blocks, 1):
        issues += check_len(f"findings[{i}].title",  title,  LIMITS["finding_title"])
        issues += check_len(f"findings[{i}].detail", detail, LIMITS["finding_detail"])

    # ── mechSteps 件数と各フィールド ──
    mech_blocks = re.findall(
        r'mechSteps.*?(?=relIntro)', block, re.DOTALL
    )
    if mech_blocks:
        mech_titles = re.findall(r'title:\s*"([^"]*)"', mech_blocks[0])
        mech_details = re.findall(r'detail:\s*"([^"]*)"', mech_blocks[0])
        n = len(mech_titles)
        lo, hi = COUNTS["mechSteps"]
        if not (lo <= n <= hi):
            issues.append(f"  ⚠️  mechSteps: {n}件（推奨 {lo}〜{hi}件）")
        for i, (t, d) in enumerate(zip(mech_titles, mech_details), 1):
            issues += check_len(f"mechSteps[{i}].title",  t, LIMITS["mechStep_title"])
            issues += check_len(f"mechSteps[{i}].detail", d, LIMITS["mechStep_detail"])

    # ── actions 件数 ──
    action_blocks = re.findall(r'timing:\s*"[^"]*"', block)
    n = len(action_blocks)
    lo, hi = COUNTS["actions"]
    if not (lo <= n <= hi):
        issues.append(f"  ⚠️  actions: {n}件（推奨 {lo}〜{hi}件）")

    # ── chart ファイルの存在確認 ──
    chart_files = re.findall(r'file:\s*"([^"]+\.png)"', block)
    charts_dir = Path(__file__).parent.parent / "public" / "charts"
    for cf in chart_files:
        path = charts_dir / cf
        if not path.exists():
            issues.append(f"  ❌ チャート画像が見つかりません: public/charts/{cf}")
        else:
            issues.append(f"  ✅ チャート画像OK: {cf}")

    # ── chart タイトル・subtitle 長 ──
    chart_titles   = re.findall(r'(?<=charts:).*?title:\s*"([^"]+)"', block, re.DOTALL)
    chart_subtitles = re.findall(r'subtitle:\s*"([^"]+)"', block)
    for i, t in enumerate(chart_titles, 1):
        issues += check_len(f"chart[{i}].title", t, LIMITS["chart_title"])
    for i, s in enumerate(chart_subtitles, 1):
        issues += check_len(f"chart[{i}].subtitle", s, LIMITS["chart_subtitle"])

    # ── 必須フィールドの空欄チェック ──
    required = ["title","titleShort","journal","emoji","bgContext","bgProblem",
                "bgImportance","findingHeadline","actionSummary","srcTitle",
                "srcJournal","srcUrl"]
    for field in required:
        val = extract(field)
        if not val:
            issues.append(f"  ❌ 必須フィールドが空: {field}")

    if issues:
        for i in issues:
            print(i)
    else:
        print("  ✅ コンテンツ検証: すべてOK")

if __name__ == "__main__":
    run()
