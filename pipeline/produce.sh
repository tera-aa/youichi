#!/usr/bin/env bash
# 🎬 制作部 — 1コマンド制作スクリプト
# 使い方: ./pipeline/produce.sh Paper12
# 事前: VOICEVOX アプリを起動しておくこと

set -euo pipefail
cd "$(dirname "$0")/.."

PAPER="${1:-}"
if [[ -z "$PAPER" ]]; then
  echo "使い方: $0 <PaperID>  例: $0 Paper12"
  exit 1
fi

echo "========================================"
echo "🎬 制作開始: $PAPER"
echo "========================================"

echo ""
echo "--- ① チャート生成 ---"
python generate-charts.py "$PAPER"

echo ""
echo "--- ② ナレーション生成（通常版） ---"
node generate-voicevox.mjs "$PAPER"

echo ""
echo "--- ③ ナレーション生成（Short版） ---"
node generate-voicevox.mjs "${PAPER}Short"

echo ""
echo "--- ④ 動画レンダリング（通常版） ---"
npx remotion render src/index.ts "$PAPER" \
  "../new_videos/${PAPER}_final.mp4" \
  --codec=h264 --crf=18 --concurrency=4 --log=warn

echo ""
echo "--- ⑤ 動画レンダリング（Short版） ---"
npx remotion render src/index.ts "${PAPER}Short" \
  "../new_videos/${PAPER}Short_final.mp4" \
  --codec=h264 --crf=18 --concurrency=4 --log=warn

echo ""
echo "========================================"
echo "✅ 制作完了: $PAPER"
echo "次のステップ: pipeline/status.md を更新 → 配信部へ連絡"
echo "========================================"
