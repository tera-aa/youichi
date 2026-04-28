#!/usr/bin/env bash
# 🔍 品質管理部 — 動画QCスクリプト
# 使い方: ./pipeline/qc.sh Paper12
# 出力: pipeline/qc_frames/<PaperID>/ にフレーム画像 + pipeline/qc_report.md に結果追記

set -euo pipefail
cd "$(dirname "$0")/.."

PAPER="${1:-}"
if [[ -z "$PAPER" ]]; then
  echo "使い方: $0 <PaperID>  例: $0 Paper12"
  exit 1
fi

VIDEO_DIR="../new_videos"
VIDEO="${VIDEO_DIR}/${PAPER}_final.mp4"
SHORT="${VIDEO_DIR}/${PAPER}Short_final.mp4"
FRAMES_DIR="pipeline/qc_frames/${PAPER}"
REPORT="pipeline/qc_report.md"

echo "========================================"
echo "🔍 QC開始: $PAPER"
echo "========================================"

mkdir -p "$FRAMES_DIR"

# ── ① 動画ファイルの存在確認 ──────────────────────────────────
check_file() {
  local f="$1" label="$2"
  if [[ ! -f "$f" ]]; then
    echo "  ❌ $label が見つかりません: $f"
    return 1
  fi
  echo "  ✅ $label 存在確認OK"
}

echo ""
echo "--- ① ファイル確認 ---"
LONG_OK=true
SHORT_OK=true
check_file "$VIDEO" "通常版" || LONG_OK=false
check_file "$SHORT" "Short版" || SHORT_OK=false

# ── ② メタデータ検証 ──────────────────────────────────────────
echo ""
echo "--- ② メタデータ検証 ---"

validate_video() {
  local f="$1" label="$2" expect_w="$3" expect_h="$4"
  if [[ ! -f "$f" ]]; then return; fi

  local info
  info=$(ffprobe -v error -select_streams v:0 \
    -show_entries stream=width,height,r_frame_rate,duration \
    -of default=noprint_wrappers=1 "$f" 2>/dev/null)

  local width height fps duration
  width=$(echo "$info" | grep "^width=" | cut -d= -f2)
  height=$(echo "$info" | grep "^height=" | cut -d= -f2)
  fps_raw=$(echo "$info" | grep "^r_frame_rate=" | cut -d= -f2)
  duration=$(echo "$info" | grep "^duration=" | cut -d= -f2 | xargs printf "%.1f")
  fps=$(python3 -c "n,d=map(int,'$fps_raw'.split('/')); print(round(n/d))" 2>/dev/null || echo "?")

  echo "  $label:"
  echo "    解像度: ${width}×${height} (期待値: ${expect_w}×${expect_h})"
  echo "    FPS:    $fps (期待値: 30)"
  echo "    尺:     ${duration}秒"

  # 解像度チェック
  [[ "$width" == "$expect_w" && "$height" == "$expect_h" ]] \
    && echo "    ✅ 解像度OK" || echo "    ❌ 解像度NG"
  # FPSチェック
  [[ "$fps" == "30" ]] \
    && echo "    ✅ FPS OK" || echo "    ⚠️  FPS: $fps"
  # 尺の妥当性（60秒以上 360秒以下）
  python3 -c "
d=$duration
if 60 <= d <= 360:
    print('    ✅ 尺OK')
elif d < 60:
    print('    ❌ 尺が短すぎます（60秒未満）')
else:
    print('    ⚠️  尺が長すぎます（360秒超）')
" 2>/dev/null
}

validate_video "$VIDEO" "通常版" 1280 720
validate_video "$SHORT" "Short版" 1080 1920

# ── ③ フレーム抽出（各シーンの代表フレーム）─────────────────────
echo ""
echo "--- ③ フレーム抽出 ---"

extract_frames() {
  local f="$1" label="$2" prefix="$3"
  if [[ ! -f "$f" ]]; then return; fi

  local duration
  duration=$(ffprobe -v error -select_streams v:0 \
    -show_entries stream=duration -of default=noprint_wrappers=1:nokey=1 "$f" 2>/dev/null | head -1)

  # 9シーン分のタイムスタンプを均等に計算
  python3 - "$duration" "$FRAMES_DIR" "$prefix" "$f" <<'PYEOF'
import subprocess, sys, os
duration = float(sys.argv[1])
out_dir   = sys.argv[2]
prefix    = sys.argv[3]
video     = sys.argv[4]

scenes = ["cover","background","findings","mechanism",
          "chart1","relevance","action","chart2","source"]

for i, name in enumerate(scenes):
    t = duration * (i + 0.5) / len(scenes)
    out = os.path.join(out_dir, f"{prefix}_{i+1:02d}_{name}.jpg")
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(t), "-i", video,
        "-vframes", "1", "-q:v", "2", out
    ], capture_output=True)

print(f"  ✅ {prefix}: {len(scenes)}フレーム抽出 → {out_dir}/")
PYEOF
}

extract_frames "$VIDEO" "通常版" "long"
extract_frames "$SHORT" "Short版" "short"

# ── ④ data.ts コンテンツ検証 ────────────────────────────────────
echo ""
echo "--- ④ data.ts コンテンツ検証 ---"
python3 pipeline/qc_data.py "$PAPER"

# ── ⑤ QCレポート出力 ────────────────────────────────────────────
echo ""
echo "--- ⑤ QCレポート出力 ---"

DATE=$(date +"%Y-%m-%d %H:%M")

cat >> "$REPORT" <<REPORT_EOF

## $PAPER — QC実施: $DATE

### 目視チェックリスト（フレームを確認してください）
フレーム場所: \`pipeline/qc_frames/${PAPER}/\`

| シーン | ファイル | 文字サイズ | 文字切れ | アニメ | カラー |
|--------|---------|-----------|---------|-------|-------|
| Cover | long_01_cover.jpg | ⬜ | ⬜ | ⬜ | ⬜ |
| Background | long_02_background.jpg | ⬜ | ⬜ | ⬜ | ⬜ |
| Findings | long_03_findings.jpg | ⬜ | ⬜ | ⬜ | ⬜ |
| Mechanism | long_04_mechanism.jpg | ⬜ | ⬜ | ⬜ | ⬜ |
| Chart1 | long_05_chart1.jpg | ⬜ | ⬜ | ⬜ | ⬜ |
| Relevance | long_06_relevance.jpg | ⬜ | ⬜ | ⬜ | ⬜ |
| Action | long_07_action.jpg | ⬜ | ⬜ | ⬜ | ⬜ |
| Chart2 | long_08_chart2.jpg | ⬜ | ⬜ | ⬜ | ⬜ |
| Source | long_09_source.jpg | ⬜ | ⬜ | ⬜ | ⬜ |

### よくある不具合チェック
- [ ] 文字が小さすぎて読めないシーンがない
- [ ] テキストがフレーム外にはみ出していない
- [ ] グラフの軸ラベルが正しく表示されている
- [ ] BGMとナレーションのバランスが適切
- [ ] Short版でテキストが縦長フレームに収まっている
- [ ] フェードトランジションが滑らか

### 判定
- [ ] ✅ 合格（アップロード可）
- [ ] 🔄 要修正（内容を記入）
- [ ] ❌ 再レンダリング必要

### 修正内容（あれば）
（ここに記入）

---
REPORT_EOF

echo "  ✅ QCレポートを追記しました: $REPORT"

echo ""
echo "========================================"
echo "✅ QC完了: $PAPER"
echo ""
echo "次のステップ:"
echo "  1. pipeline/qc_frames/${PAPER}/ のフレームを目視確認"
echo "  2. pipeline/qc_report.md のチェックリストを記入"
echo "  3. 合格したら pipeline/status.md の distribution 列を更新"
echo "========================================"
