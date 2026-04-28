#!/usr/bin/env python3
"""
⑦ タイトル・概要・ハッシュタグ生成スクリプト
使い方: python pipeline/generate_description.py Paper12
出力:  pipeline/descriptions/<PaperID>.md
"""

import re
import subprocess
import sys
from pathlib import Path

PAPER_ID = sys.argv[1] if len(sys.argv) > 1 else None
if not PAPER_ID:
    print("使い方: python pipeline/generate_description.py <PaperID>")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
DATA_TS = ROOT / "src" / "data.ts"
OUT_DIR = ROOT / "pipeline" / "descriptions"
OUT_DIR.mkdir(exist_ok=True)
OUT_FILE = OUT_DIR / f"{PAPER_ID}.md"

text = DATA_TS.read_text()

# 対象論文ブロックを抽出
pattern = rf'\{{\s*id:\s*"{PAPER_ID}".*?(?=\n  \{{\s*id:|$)'
match = re.search(pattern, text, re.DOTALL)
if not match:
    print(f"❌ {PAPER_ID} が data.ts に見つかりません")
    sys.exit(1)

block = match.group(0)

def extract(key):
    m = re.search(rf'{key}:\s*"(.*?)"', block, re.DOTALL)
    return m.group(1).replace("\\n", " ").strip() if m else ""

def extract_list_field(section_key, field):
    section_m = re.search(rf'{section_key}:\s*\[(.*?)\]', block, re.DOTALL)
    if not section_m:
        return []
    return re.findall(rf'{field}:\s*"([^"]*)"', section_m.group(1))

# ── 論文データ抽出 ──────────────────────────────────────────────
title          = extract("title")
title_short    = extract("titleShort")
journal        = extract("journal")
bg_context     = extract("bgContext")
bg_problem     = extract("bgProblem")
bg_importance  = extract("bgImportance")
finding_headline = extract("findingHeadline")
action_summary = extract("actionSummary")
src_journal    = extract("srcJournal")
src_note       = extract("srcNote")

finding_titles  = extract_list_field("findings", "title")
finding_details = extract_list_field("findings", "detail")
action_actions  = extract_list_field("actions", "action")
chart_titles    = re.findall(r'file:.*?title:\s*"([^"]+)"', block, re.DOTALL)

# ── プロンプト構築 ──────────────────────────────────────────────
prompt = f"""あなたはYouTubeチャンネル「@sadameasuno」の配信担当です。
以下の論文解説動画データをもとに、YouTube投稿用の資料を生成してください。

チャンネル情報:
- URL: https://www.youtube.com/@sadameasuno
- ターゲット: 健康意識が高い日本人（30〜50代）
- テーマ: 生物学・健康・食事・老化・腸内細菌の最新科学

論文データ ({PAPER_ID}):
- タイトル: {title}
- 短縮タイトル: {title_short}
- 掲載誌: {journal}
- 背景: {bg_context}
- 問題: {bg_problem}
- 重要性: {bg_importance}
- 最大の発見: {finding_headline}
- 発見ポイント: {', '.join(finding_titles)}
- 行動まとめ: {action_summary}
- 推奨行動: {', '.join(action_actions)}
- チャートテーマ: {', '.join(chart_titles)}
- 出典: {src_journal} / {src_note}

以下の形式で出力してください（マークダウン）:

## {PAPER_ID} | [テーマ短縮タイトル]

### 🎬 Long動画（1280×720）

**【タイトル】**
（60〜70文字。数字・驚き・具体的ベネフィットを含める。例:「〇〇を食べると△△が30%改善！最新研究が明かす驚きの仕組み」）

**【説明文】**
（1段落: 研究概要を2〜3文）

（2段落: この動画で学べること。視聴者の行動変容につながる具体的ベネフィット）

✅ [発見ポイント1]
✅ [発見ポイント2]
✅ [発見ポイント3]
✅ [発見ポイント4]

📄 出典: {src_journal}

🔔 チャンネル登録で最新の健康科学をお届けします
👉 https://www.youtube.com/@sadameasuno

**【ハッシュタグ】**（15個）
#健康 #ダイエット #腸活 #科学 #最新研究 ... （論文テーマに合わせて追加）

---

### 📱 Short動画（1080×1920）

**【Shortsタイトル】**（40〜50文字。最初の3秒で引き込む問いかけ形式）

**【Shorts説明文】**（3〜4行。フック→発見→CTAの流れ）
🔔 詳しくはチャンネルで → @sadameasuno

**【Shortsハッシュタグ】**（5個）
#Shorts #健康 #[テーマ] #科学 #豆知識

---

### 🖼️ サムネイルブリーフ

**【メインテキスト】**（5〜8文字、大きく表示）
**【サブテキスト】**（15〜20文字）
**【推奨ビジュアル】**
**【カラーテーマ】**
"""

# ── Claude CLI 呼び出し ──────────────────────────────────────────
print(f"  🤖 Claude でタイトル・概要・ハッシュタグを生成中...")

result = subprocess.run(
    ["claude", "--print", prompt],
    capture_output=True,
    text=True,
    timeout=120,
)

if result.returncode != 0:
    print(f"  ❌ Claude CLI エラー: {result.stderr[:200]}")
    sys.exit(1)

output = result.stdout.strip()

# ── ファイル保存 ────────────────────────────────────────────────
OUT_FILE.write_text(output, encoding="utf-8")
print(f"  ✅ 生成完了 → pipeline/descriptions/{PAPER_ID}.md")

# descriptions.md（統合ファイル）にも追記
combined = ROOT / "pipeline" / "descriptions.md"
existing = combined.read_text(encoding="utf-8") if combined.exists() else ""
if PAPER_ID not in existing:
    with combined.open("a", encoding="utf-8") as f:
        f.write(f"\n\n{output}\n")
    print(f"  ✅ pipeline/descriptions.md にも追記しました")
else:
    print(f"  ℹ️  pipeline/descriptions.md には既に {PAPER_ID} が存在します（スキップ）")
