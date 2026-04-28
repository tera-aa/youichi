#!/usr/bin/env python3
"""
🔬 マスコット生成スクリプト — 博士キャラ
出力: pipeline/mascot/mascot.png         (透過PNG 400×500)
     pipeline/mascot/mascot_small.png    (透過PNG 120×150)
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT    = Path(__file__).parent.parent
OUT_DIR = ROOT / "pipeline" / "mascot"
OUT_DIR.mkdir(exist_ok=True)

W, H = 400, 500

# ── カラーパレット ─────────────────────────────────────────────────
SKIN        = (255, 218, 180, 255)
SKIN_DARK   = (230, 190, 150, 255)
HAIR        = (230, 230, 230, 255)      # 白髪
HAIR_DARK   = (190, 190, 190, 255)
COAT        = (248, 248, 252, 255)      # 白衣
COAT_DARK   = (210, 215, 230, 255)
COAT_LINE   = (180, 185, 200, 255)
GLASSES_F   = (50,  50,  60,  255)     # メガネフレーム
LENS        = (200, 225, 245, 160)     # レンズ（半透明）
EYE         = (40,  40,  50,  255)
PUPIL       = (10,  10,  20,  255)
BROW        = (100, 100, 110, 255)
BLUSH       = (255, 170, 150, 120)
MOUTH       = (180,  80,  80, 255)
OUTLINE     = (50,  50,  60,  255)
TIE         = (80, 130, 200, 255)
TIE_DARK    = (50, 100, 170, 255)
POCKET_LINE = (180, 185, 200, 255)
PEN         = (60,  80, 160, 255)
WHITE       = (255, 255, 255, 255)

img  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

cx = W // 2      # 中央X
hy = 185         # 頭の中心Y
hr = 108         # 頭の半径

# ── ① 白衣（ボディ）─────────────────────────────────────────────
# 胴体
body_top = hy + hr - 10
draw.ellipse([cx-130, body_top, cx+130, H+60], fill=COAT, outline=OUTLINE, width=2)
draw.rectangle([cx-130, body_top+40, cx+130, H], fill=COAT)
draw.line([(cx-130, body_top+40), (cx-130, H)], fill=OUTLINE, width=2)
draw.line([(cx+130, body_top+40), (cx+130, H)], fill=OUTLINE, width=2)

# 白衣の中央ライン
draw.line([(cx, body_top+20), (cx, H)], fill=COAT_LINE, width=2)

# 白衣のボタン（3個）
for i in range(3):
    by = body_top + 55 + i * 38
    draw.ellipse([cx-5, by-5, cx+5, by+5], fill=COAT_DARK, outline=OUTLINE, width=1)

# 胸ポケット（左側）
px, py, pw, ph = cx - 90, body_top + 35, 48, 36
draw.rectangle([px, py, px+pw, py+ph], fill=COAT, outline=POCKET_LINE, width=2)
# ポケットのペン
draw.rectangle([px+18, py-8, px+26, py+8], fill=PEN, outline=OUTLINE, width=1)
draw.ellipse([px+16, py-12, px+28, py-4], fill=(255,80,80,255), outline=OUTLINE, width=1)

# 白衣の衿（V字）
collar_pts = [
    (cx - 38, body_top + 15),
    (cx,      body_top + 55),
    (cx + 38, body_top + 15),
    (cx + 20, body_top + 5),
    (cx - 20, body_top + 5),
]
draw.polygon(collar_pts, fill=COAT, outline=OUTLINE, width=2)

# ネクタイ（青）
tie_pts = [
    (cx - 12, body_top + 18),
    (cx + 12, body_top + 18),
    (cx + 16, body_top + 50),
    (cx,      body_top + 68),
    (cx - 16, body_top + 50),
]
draw.polygon(tie_pts, fill=TIE, outline=TIE_DARK, width=2)
# ネクタイのノット
draw.ellipse([cx-10, body_top+12, cx+10, body_top+26], fill=TIE_DARK, outline=OUTLINE, width=1)

# ── ② 耳 ─────────────────────────────────────────────────────────
for side in [-1, 1]:
    ex = cx + side * (hr - 5)
    draw.ellipse([ex - 16, hy - 18, ex + 16, hy + 18], fill=SKIN, outline=OUTLINE, width=2)
    draw.ellipse([ex - 9, hy - 10, ex + 9, hy + 10], fill=SKIN_DARK, outline=None)

# ── ③ 首 ─────────────────────────────────────────────────────────
draw.rectangle([cx-22, hy+hr-12, cx+22, body_top+20], fill=SKIN, outline=None)
draw.line([(cx-22, hy+hr-12), (cx-22, body_top+20)], fill=OUTLINE, width=2)
draw.line([(cx+22, hy+hr-12), (cx+22, body_top+20)], fill=OUTLINE, width=2)

# ── ④ 頭（顔） ───────────────────────────────────────────────────
draw.ellipse([cx-hr, hy-hr, cx+hr, hy+hr], fill=SKIN, outline=OUTLINE, width=3)

# ── ⑤ 白髪（ふわふわ）───────────────────────────────────────────
hair_blobs = [
    # (中心x, 中心y, 半径x, 半径y)
    (cx,       hy - hr + 2,  70, 52),   # 頭頂
    (cx - 55,  hy - hr + 28, 50, 44),   # 左上
    (cx + 55,  hy - hr + 28, 50, 44),   # 右上
    (cx - 80,  hy - hr + 62, 40, 38),   # 左側
    (cx + 80,  hy - hr + 62, 40, 38),   # 右側
    (cx - 50,  hy - hr + 10, 42, 38),   # 左中
    (cx + 50,  hy - hr + 10, 42, 38),   # 右中
]
# 影
for (bx, by, rw, rh) in hair_blobs:
    draw.ellipse([bx-rw+4, by-rh+4, bx+rw+4, by+rh+4], fill=HAIR_DARK)
# 本体
for (bx, by, rw, rh) in hair_blobs:
    draw.ellipse([bx-rw, by-rh, bx+rw, by+rh], fill=HAIR, outline=OUTLINE, width=2)

# ── ⑥ 眉毛 ───────────────────────────────────────────────────────
for side in [-1, 1]:
    bx = cx + side * 36
    draw.arc([bx - 20, hy - 38, bx + 20, hy - 14],
             start=200 if side < 0 else 320,
             end  =340 if side < 0 else 360+20,
             fill=BROW, width=4)

# ── ⑦ 目 ─────────────────────────────────────────────────────────
for side in [-1, 1]:
    ex = cx + side * 35
    ey = hy - 10
    # 白目
    draw.ellipse([ex-14, ey-14, ex+14, ey+14], fill=WHITE, outline=OUTLINE, width=2)
    # 虹彩
    draw.ellipse([ex-8, ey-8, ex+8, ey+8], fill=(80, 130, 200, 255))
    # 瞳孔
    draw.ellipse([ex-4, ey-5, ex+4, ey+3], fill=PUPIL)
    # ハイライト
    draw.ellipse([ex+1, ey-8, ex+5, ey-4], fill=WHITE)

# ── ⑧ メガネ ─────────────────────────────────────────────────────
lens_r = 26
for side in [-1, 1]:
    gx = cx + side * 35
    gy = hy - 10
    # レンズ（半透明）
    lens_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lens_draw = ImageDraw.Draw(lens_img)
    lens_draw.ellipse([gx-lens_r, gy-lens_r, gx+lens_r, gy+lens_r], fill=LENS)
    img = Image.alpha_composite(img, lens_img)
    draw = ImageDraw.Draw(img)
    # フレーム
    draw.ellipse([gx-lens_r, gy-lens_r, gx+lens_r, gy+lens_r],
                 outline=GLASSES_F, width=3)
    # フレーム上部の太め強調
    draw.arc([gx-lens_r, gy-lens_r, gx+lens_r, gy+lens_r],
             start=200, end=340, fill=GLASSES_F, width=4)

# メガネブリッジ
draw.line([(cx - lens_r + 4, hy - 12), (cx + lens_r - 4, hy - 12)],
          fill=GLASSES_F, width=3)
# テンプル（耳へのアーム）
for side in [-1, 1]:
    gx = cx + side * 35
    draw.line([(gx + side * lens_r, hy - 10),
               (gx + side * (lens_r + 36), hy - 2)],
              fill=GLASSES_F, width=3)

# ── ⑨ 鼻 ─────────────────────────────────────────────────────────
draw.arc([cx-10, hy+8, cx+10, hy+26], start=30, end=150, fill=SKIN_DARK, width=2)

# ── ⑩ 口（笑顔）─────────────────────────────────────────────────
draw.arc([cx-22, hy+22, cx+22, hy+48], start=10, end=170, fill=MOUTH, width=3)
# 歯（白い部分）
draw.arc([cx-18, hy+24, cx+18, hy+44], start=15, end=165, fill=WHITE, width=5)

# ── ⑪ ほっぺ（赤み）─────────────────────────────────────────────
blush_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
blush_draw = ImageDraw.Draw(blush_img)
for side in [-1, 1]:
    bx = cx + side * 62
    blush_draw.ellipse([bx-22, hy+12, bx+22, hy+36], fill=BLUSH)
img = Image.alpha_composite(img, blush_img)
draw = ImageDraw.Draw(img)

# ── ⑫ 保存 ───────────────────────────────────────────────────────
out_main  = OUT_DIR / "mascot.png"
out_small = OUT_DIR / "mascot_small.png"

img.save(out_main, "PNG")
print(f"  ✅ mascot.png    → {out_main.relative_to(ROOT)}")

small = img.resize((120, 150), Image.LANCZOS)
small.save(out_small, "PNG")
print(f"  ✅ mascot_small.png → {out_small.relative_to(ROOT)}")

print(f"\n  open pipeline/mascot/ で確認してください")
