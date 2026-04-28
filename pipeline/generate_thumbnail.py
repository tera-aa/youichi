#!/usr/bin/env python3
"""
🖼️ サムネイル自動生成スクリプト
使い方: python pipeline/generate_thumbnail.py Paper12
出力:  pipeline/thumbnails/<PaperID>_thumbnail.jpg  (1280×720)
       pipeline/thumbnails/<PaperID>_thumbnail_short.jpg  (1080×1920)
"""

import re
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

PAPER_ID = sys.argv[1] if len(sys.argv) > 1 else None
if not PAPER_ID:
    print("使い方: python pipeline/generate_thumbnail.py <PaperID>")
    sys.exit(1)

ROOT       = Path(__file__).parent.parent
DATA_TS    = ROOT / "src" / "data.ts"
CHARTS_DIR = ROOT / "public" / "charts"
OUT_DIR    = ROOT / "pipeline" / "thumbnails"
OUT_DIR.mkdir(exist_ok=True)

FONT_BOLD   = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"
FONT_MEDIUM = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"

# ── データ取得 ────────────────────────────────────────────────────
text = DATA_TS.read_text()
pattern = rf'\{{\s*id:\s*"{PAPER_ID}".*?(?=\n  \{{\s*id:|$)'
match = re.search(pattern, text, re.DOTALL)
if not match:
    print(f"❌ {PAPER_ID} が data.ts に見つかりません")
    sys.exit(1)

block = match.group(0)

def extract(key):
    m = re.search(rf'{key}:\s*"(.*?)"', block, re.DOTALL)
    return m.group(1).replace("\\n", " ").strip() if m else ""

accent_hex   = extract("accent") or "#00C2FF"
title        = extract("title")
title_short  = extract("titleShort")
emoji        = extract("emoji") or "🔬"
journal      = extract("journal")

# サムネイルブリーフから本文テキストを取得（なければ title から生成）
desc_file = ROOT / "pipeline" / "descriptions" / f"{PAPER_ID}.md"
main_text = ""
sub_text  = ""
if desc_file.exists():
    desc = desc_file.read_text()
    m = re.search(r'\*\*【メインテキスト】\*\*\n(.+)', desc)
    if m:
        main_text = m.group(1).strip()
    m = re.search(r'\*\*【サブテキスト】\*\*\n(.+)', desc)
    if m:
        sub_text = m.group(1).strip()

if not main_text:
    main_text = title_short or title[:10]
if not sub_text:
    sub_text  = title[:28] if len(title) > 10 else title

# チャート画像（_A を優先）
chart_a = CHARTS_DIR / f"{PAPER_ID}_chart_A.png"
chart_b = CHARTS_DIR / f"{PAPER_ID}_chart_B.png"
chart_path = chart_a if chart_a.exists() else (chart_b if chart_b.exists() else None)

# マスコット画像
mascot_path = ROOT / "pipeline" / "mascot" / "mascot.png"

# アクセントカラー → RGB
def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

accent   = hex2rgb(accent_hex)
dark_bg  = tuple(max(0, c - 160) for c in accent)   # 深い暗色
mid_bg   = tuple(max(0, c - 100) for c in accent)    # 中間色

def darken(rgb, factor=0.35):
    return tuple(int(c * factor) for c in rgb)

BG_DARK  = darken(accent, 0.18)
BG_MID   = darken(accent, 0.30)
ACCENT   = accent

# ── Long サムネイル (1280×720) ───────────────────────────────────
def make_long():
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    # 左→右 グラデーション背景
    for x in range(W):
        t = x / W
        r = int(BG_DARK[0] * (1 - t) + BG_MID[0] * t)
        g = int(BG_DARK[1] * (1 - t) + BG_MID[1] * t)
        b = int(BG_DARK[2] * (1 - t) + BG_MID[2] * t)
        draw.line([(x, 0), (x, H)], fill=(r, g, b))

    # チャート画像（右側 45%）
    if chart_path:
        chart = Image.open(chart_path).convert("RGBA")
        chart_w = int(W * 0.48)
        chart_h = int(chart_w * chart.height / chart.width)
        if chart_h > H - 60:
            chart_h = H - 60
            chart_w = int(chart_h * chart.width / chart.height)
        chart = chart.resize((chart_w, chart_h), Image.LANCZOS)

        # 暗めのオーバーレイ（視認性確保）
        overlay = Image.new("RGBA", (chart_w, chart_h), (0, 0, 0, 120))
        chart.paste(overlay, (0, 0), overlay)

        cx = W - chart_w - 30
        cy = (H - chart_h) // 2
        img.paste(chart.convert("RGB"), (cx, cy))

        # チャート左端のグラデーションフェード（左テキストとの境界）
        fade_w = 180
        for i in range(fade_w):
            alpha = int(255 * (1 - i / fade_w))
            t = (cx + i) / W
            r = int(BG_DARK[0] * (1 - t) + BG_MID[0] * t)
            g = int(BG_DARK[1] * (1 - t) + BG_MID[1] * t)
            b = int(BG_DARK[2] * (1 - t) + BG_MID[2] * t)
            draw.line([(cx + i, 0), (cx + i, H)], fill=(r, g, b))

    draw = ImageDraw.Draw(img)

    draw = ImageDraw.Draw(img)

    # アクセントライン（左端）
    draw.rectangle([(0, 0), (8, H)], fill=ACCENT)

    # 下部バー
    bar_h = 72
    draw.rectangle([(0, H - bar_h), (W, H)], fill=ACCENT)
    try:
        font_bar = ImageFont.truetype(FONT_MEDIUM, 30)
        draw.text((32, H - bar_h + 20), f"@sadameasuno  |  {journal}", font=font_bar, fill=(255, 255, 255))
    except Exception:
        pass

    # メインテキスト（マスコット右側・中央上部）
    text_x    = 185   # マスコット幅ぶん右にオフセット
    text_max_w = int(W * 0.50) - 40
    try:
        font_main = ImageFont.truetype(FONT_BOLD, 84)
        chars = list(main_text)
        lines, line = [], ""
        for ch in chars:
            test = line + ch
            bbox = font_main.getbbox(test)
            if bbox[2] > text_max_w:
                lines.append(line)
                line = ch
            else:
                line = test
        if line:
            lines.append(line)

        line_h = 92
        total_h = len(lines) * line_h
        y_start = (H - bar_h - total_h) // 2 - 30

        for i, ln in enumerate(lines):
            draw.text((text_x + 3, y_start + i * line_h + 3), ln, font=font_main, fill=(0, 0, 0, 180))
            draw.text((text_x,     y_start + i * line_h),     ln, font=font_main, fill=(255, 255, 255))
    except Exception as e:
        print(f"  ⚠️  メインテキスト描画エラー: {e}")

    # サブテキスト
    try:
        font_sub = ImageFont.truetype(FONT_MEDIUM, 36)
        sub_lines = textwrap.wrap(sub_text, width=20)
        sy = y_start + len(lines) * line_h + 14
        for j, sl in enumerate(sub_lines[:2]):
            draw.text((text_x + 2, sy + j * 46 + 2), sl, font=font_sub, fill=(0, 0, 0, 160))
            draw.text((text_x,     sy + j * 46),     sl, font=font_sub, fill=(*ACCENT, 255))
    except Exception:
        pass

    # マスコット（左下・チャートと重ならない位置）
    if mascot_path.exists():
        mascot_img = Image.open(mascot_path).convert("RGBA")
        mh = int((H - bar_h) * 0.44)
        mw = int(mh * mascot_img.width / mascot_img.height)
        mascot_img = mascot_img.resize((mw, mh), Image.LANCZOS)
        mx = 12
        my = H - bar_h - mh + 8
        img.paste(mascot_img, (mx, my), mascot_img)

    out = OUT_DIR / f"{PAPER_ID}_thumbnail.jpg"
    img.save(out, "JPEG", quality=95)
    print(f"  ✅ Long サムネイル → {out.relative_to(ROOT)}")


# ── Short サムネイル (1080×1920) ─────────────────────────────────
def make_short():
    W, H = 1080, 1920
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    # 上→下グラデーション
    for y in range(H):
        t = y / H
        r = int(BG_DARK[0] * (1 - t) + BG_MID[0] * t)
        g = int(BG_DARK[1] * (1 - t) + BG_MID[1] * t)
        b = int(BG_DARK[2] * (1 - t) + BG_MID[2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # チャート画像（中央上部）
    if chart_path:
        chart = Image.open(chart_path).convert("RGB")
        cw = int(W * 0.90)
        ch = int(cw * chart.height / chart.width)
        chart = chart.resize((cw, ch), Image.LANCZOS)
        cx = (W - cw) // 2
        cy = int(H * 0.28)
        img.paste(chart, (cx, cy))

        # 下端フェード
        fade = Image.new("RGBA", (cw, 120), (0, 0, 0, 0))
        fd = ImageDraw.Draw(fade)
        for i in range(120):
            alpha = int(255 * (i / 120))
            t = (cy + ch - 120 + i) / H
            r2 = int(BG_DARK[0] * (1 - t) + BG_MID[0] * t)
            fd.line([(0, i), (cw, i)], fill=(r2, r2, r2, alpha))
        img.paste(Image.new("RGB", (cw, 120), BG_MID), (cx, cy + ch - 120),
                  fade.split()[3])

    draw = ImageDraw.Draw(img)

    # 上部バー
    draw.rectangle([(0, 0), (W, 10)], fill=ACCENT)

    # 下部バー
    draw.rectangle([(0, H - 90), (W, H)], fill=ACCENT)
    try:
        font_bar = ImageFont.truetype(FONT_MEDIUM, 34)
        draw.text((40, H - 90 + 26), f"@sadameasuno", font=font_bar, fill=(255, 255, 255))
    except Exception:
        pass

    # メインテキスト（上部 25%）
    try:
        font_main = ImageFont.truetype(FONT_BOLD, 100)
        chars = list(main_text)
        lines, line = [], ""
        for ch in chars:
            test = line + ch
            bbox = font_main.getbbox(test)
            if bbox[2] > W - 80:
                lines.append(line)
                line = ch
            else:
                line = test
        if line:
            lines.append(line)

        line_h = 110
        y_start = int(H * 0.08)
        for i, ln in enumerate(lines):
            bx = font_main.getbbox(ln)[2]
            x = (W - bx) // 2
            draw.text((x + 3, y_start + i * line_h + 3), ln, font=font_main, fill=(0, 0, 0, 180))
            draw.text((x, y_start + i * line_h), ln, font=font_main, fill=(255, 255, 255))
    except Exception as e:
        print(f"  ⚠️  Short メインテキスト描画エラー: {e}")

    # サブテキスト（チャート下）
    try:
        font_sub = ImageFont.truetype(FONT_MEDIUM, 46)
        sy = int(H * 0.72)
        sub_lines = textwrap.wrap(sub_text, width=18)
        for j, sl in enumerate(sub_lines[:3]):
            bx = font_sub.getbbox(sl)[2]
            x = (W - bx) // 2
            draw.text((x + 2, sy + j * 58 + 2), sl, font=font_sub, fill=(0, 0, 0, 160))
            draw.text((x, sy + j * 58), sl, font=font_sub, fill=(*ACCENT, 255))
    except Exception:
        pass

    out = OUT_DIR / f"{PAPER_ID}_thumbnail_short.jpg"
    img.save(out, "JPEG", quality=95)
    print(f"  ✅ Short サムネイル → {out.relative_to(ROOT)}")


print(f"  🖼️  {PAPER_ID} のサムネイルを生成中...")
make_long()
make_short()
print(f"  完了。open pipeline/thumbnails/ で確認してください")
