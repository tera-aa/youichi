#!/usr/bin/env python3
"""
🔬 マスコット生成スクリプト — 若い女性博士キャラ
出力: pipeline/mascot/mascot.png         (透過PNG 400×520)
     pipeline/mascot/mascot_small.png    (透過PNG 120×156)
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT    = Path(__file__).parent.parent
OUT_DIR = ROOT / "pipeline" / "mascot"
OUT_DIR.mkdir(exist_ok=True)

W, H = 400, 520

# ── カラーパレット ─────────────────────────────────────────────────
SKIN        = (255, 224, 196, 255)
SKIN_DARK   = (235, 195, 160, 255)
HAIR        = (45,  28,  18,  255)   # ダークブラウン
HAIR_MID    = (75,  48,  32,  255)
HAIR_HIGH   = (95,  62,  42,  255)   # ハイライト
COAT        = (248, 248, 252, 255)
COAT_DARK   = (210, 215, 230, 255)
COAT_LINE   = (185, 190, 210, 255)
EYE_WHITE   = (255, 255, 255, 255)
IRIS        = (80,  115, 170, 255)
PUPIL       = (15,  15,  25,  255)
LASH        = (30,  20,  15,  255)
BROW        = (55,  35,  22,  255)
BLUSH       = (255, 155, 140,  90)
LIP         = (210,  90,  95, 255)
LIP_DARK    = (175,  60,  65, 255)
OUTLINE     = (45,  40,  50,  255)
COLLAR      = (255, 255, 255, 255)
BTN         = (200, 205, 220, 255)
POCKET_LINE = (185, 190, 210, 255)
PEN_BODY    = (70,  100, 200, 255)
PEN_TIP     = (40,   40,  40, 255)
CLIP        = (220, 180,  50, 255)   # ヘアクリップ（黄色）
WHITE       = (255, 255, 255, 255)
RIBBON      = (230,  80, 120, 255)   # リボン（ピンク）

img  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

cx = W // 2
hy = 190   # 頭の中心Y
hr = 100   # 頭の半径

# ── ① 白衣ボディ ─────────────────────────────────────────────────
body_top = hy + hr - 8
draw.ellipse([cx-125, body_top, cx+125, H+80], fill=COAT, outline=OUTLINE, width=2)
draw.rectangle([cx-125, body_top+38, cx+125, H], fill=COAT)
draw.line([(cx-125, body_top+38), (cx-125, H)], fill=OUTLINE, width=2)
draw.line([(cx+125, body_top+38), (cx+125, H)], fill=OUTLINE, width=2)

# 中央ライン
draw.line([(cx, body_top+18), (cx, H)], fill=COAT_LINE, width=2)

# ボタン
for i in range(3):
    by = body_top + 52 + i * 40
    draw.ellipse([cx-5, by-5, cx+5, by+5], fill=BTN, outline=OUTLINE, width=1)

# 胸ポケット
px, py, pw, ph = cx-88, body_top+32, 46, 34
draw.rectangle([px, py, px+pw, py+ph], fill=COAT, outline=POCKET_LINE, width=2)
# ペン
draw.rectangle([px+17, py-10, px+24, py+6], fill=PEN_BODY, outline=OUTLINE, width=1)
draw.ellipse([px+15, py-14, px+26, py-6], fill=RIBBON, outline=OUTLINE, width=1)

# 衿（V字）
collar_pts = [
    (cx-35, body_top+12), (cx, body_top+50),
    (cx+35, body_top+12), (cx+18, body_top+4), (cx-18, body_top+4),
]
draw.polygon(collar_pts, fill=COAT, outline=OUTLINE, width=2)

# ── ② 耳 ─────────────────────────────────────────────────────────
for side in [-1, 1]:
    ex = cx + side * (hr - 6)
    draw.ellipse([ex-14, hy-14, ex+14, hy+14], fill=SKIN, outline=OUTLINE, width=2)
    draw.ellipse([ex-8,  hy-8,  ex+8,  hy+8 ], fill=SKIN_DARK)
    # ピアス（右耳のみ）
    if side == 1:
        draw.ellipse([ex+6, hy+10, ex+14, hy+18], fill=RIBBON, outline=OUTLINE, width=1)

# ── ③ 首 ─────────────────────────────────────────────────────────
draw.rectangle([cx-20, hy+hr-10, cx+20, body_top+18], fill=SKIN)
draw.line([(cx-20, hy+hr-10), (cx-20, body_top+18)], fill=OUTLINE, width=2)
draw.line([(cx+20, hy+hr-10), (cx+20, body_top+18)], fill=OUTLINE, width=2)

# ── ④ 後ろ髪（サイドに流れる）──────────────────────────────────
# 左サイドの垂れ髪
left_hair = [
    (cx-hr+15, hy-hr+40),
    (cx-hr-10, hy+10),
    (cx-hr-18, hy+hr+20),
    (cx-hr+5,  hy+hr+60),
    (cx-60,    hy+hr+80),
    (cx-hr+25, hy+hr+10),
    (cx-hr+20, hy),
    (cx-hr+22, hy-hr+50),
]
draw.polygon(left_hair, fill=HAIR, outline=None)

# 右サイドの垂れ髪
right_hair = [
    (cx+hr-15, hy-hr+40),
    (cx+hr+10, hy+10),
    (cx+hr+18, hy+hr+20),
    (cx+hr-5,  hy+hr+60),
    (cx+60,    hy+hr+80),
    (cx+hr-25, hy+hr+10),
    (cx+hr-20, hy),
    (cx+hr-22, hy-hr+50),
]
draw.polygon(right_hair, fill=HAIR, outline=None)

# ── ⑤ 顔 ─────────────────────────────────────────────────────────
draw.ellipse([cx-hr, hy-hr, cx+hr, hy+hr], fill=SKIN, outline=OUTLINE, width=3)

# ── ⑥ 前髪・トップ ───────────────────────────────────────────────
# 頭頂部
draw.ellipse([cx-hr+2, hy-hr-12, cx+hr-2, hy-hr+65], fill=HAIR, outline=None)

# 前髪（ぱっつん気味のナチュラルバング）
bang_pts = [
    (cx-hr+8,  hy-hr+35),
    (cx-hr-5,  hy-hr+58),
    (cx-55,    hy-35),
    (cx-20,    hy-50),
    (cx+15,    hy-52),
    (cx+48,    hy-38),
    (cx+hr+2,  hy-hr+58),
    (cx+hr-8,  hy-hr+35),
    (cx,       hy-hr-16),
]
draw.polygon(bang_pts, fill=HAIR, outline=OUTLINE, width=2)

# 前髪のハイライト
draw.arc([cx-25, hy-hr-5, cx+42, hy-hr+38], start=210, end=330, fill=HAIR_HIGH, width=3)

# ヘアクリップ（右サイド）
clip_x, clip_y = cx+55, hy-hr+62
draw.ellipse([clip_x-10, clip_y-5, clip_x+10, clip_y+5], fill=CLIP, outline=OUTLINE, width=2)

# ── ⑦ 眉毛 ───────────────────────────────────────────────────────
for side in [-1, 1]:
    bx = cx + side * 33
    # 細めのアーチ眉
    for w in range(3):
        draw.arc([bx-22, hy-45+w, bx+22, hy-18+w],
                 start=210 if side < 0 else 330,
                 end  =330 if side < 0 else 360+30,
                 fill=BROW, width=2)

# ── ⑧ 目（大きめ、女性的）───────────────────────────────────────
for side in [-1, 1]:
    ex = cx + side * 33
    ey = hy - 8

    # 白目（横長の楕円）
    draw.ellipse([ex-17, ey-13, ex+17, ey+13], fill=EYE_WHITE, outline=OUTLINE, width=2)

    # 虹彩
    draw.ellipse([ex-10, ey-10, ex+10, ey+10], fill=IRIS)

    # 瞳孔
    draw.ellipse([ex-5, ey-6, ex+5, ey+4], fill=PUPIL)

    # ハイライト（2点）
    draw.ellipse([ex+2, ey-8, ex+6, ey-4], fill=WHITE)
    draw.ellipse([ex-6, ey-2, ex-3, ey+1], fill=(255,255,255,180))

    # 上まつ毛（ライン）
    lash_pts = [(ex-17, ey-10), (ex+17, ey-10)]
    draw.line(lash_pts, fill=LASH, width=3)
    # まつ毛の先端（放射状）
    for i, (lx, ly, ang) in enumerate([
        (ex-16, ey-12, -70), (ex-10, ey-15, -80), (ex-3, ey-16, -90),
        (ex+5,  ey-15, -100),(ex+12, ey-13, -110),(ex+17, ey-10, -120),
    ]):
        rad = math.radians(ang)
        draw.line([(lx, ly), (int(lx+6*math.cos(rad)), int(ly+6*math.sin(rad)))],
                  fill=LASH, width=2)

    # 下まつ毛（薄め）
    draw.line([(ex-14, ey+11), (ex+14, ey+11)], fill=(*LASH[:3], 120), width=1)

# ── ⑨ 鼻（さりげなく）───────────────────────────────────────────
draw.arc([cx-7, hy+12, cx+7, hy+24], start=20, end=160, fill=SKIN_DARK, width=2)

# ── ⑩ 口（ナチュラルスマイル）───────────────────────────────────
# 上唇
draw.arc([cx-18, hy+28, cx+18, hy+44], start=195, end=345, fill=LIP_DARK, width=2)
# 下唇（ぷっくり）
draw.arc([cx-16, hy+30, cx+16, hy+50], start=15, end=165, fill=LIP, width=4)
# 口角のえくぼ
for side in [-1, 1]:
    draw.arc([cx+side*18-4, hy+30, cx+side*18+4, hy+38],
             start=270 if side<0 else 270, end=360 if side<0 else 360,
             fill=SKIN_DARK, width=2)

# ── ⑪ ほっぺ ─────────────────────────────────────────────────────
blush_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
blush_draw = ImageDraw.Draw(blush_img)
for side in [-1, 1]:
    bx = cx + side * 58
    blush_draw.ellipse([bx-24, hy+10, bx+24, hy+32], fill=BLUSH)
img = Image.alpha_composite(img, blush_img)
draw = ImageDraw.Draw(img)

# ── ⑫ 保存 ───────────────────────────────────────────────────────
out_main  = OUT_DIR / "mascot.png"
out_small = OUT_DIR / "mascot_small.png"

img.save(out_main, "PNG")
print(f"  ✅ mascot.png    → {out_main.relative_to(ROOT)}")

small = img.resize((120, 156), Image.LANCZOS)
small.save(out_small, "PNG")
print(f"  ✅ mascot_small.png → {out_small.relative_to(ROOT)}")
print(f"\n  open pipeline/mascot/ で確認してください")
