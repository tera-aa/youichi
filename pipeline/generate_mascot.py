#!/usr/bin/env python3
"""
🔬 マスコット生成 — アニメ調・若い女性博士
出力: pipeline/mascot/mascot.png  (透過PNG 360×480)
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT    = Path(__file__).parent.parent
OUT_DIR = ROOT / "pipeline" / "mascot"
OUT_DIR.mkdir(exist_ok=True)

W, H = 360, 480

# ── カラーパレット ─────────────────────────────────────────────────
SKIN        = (255, 236, 215, 255)
SKIN_SH     = (240, 205, 175, 255)   # 影
SKIN_HL     = (255, 248, 238, 255)   # ハイライト
HAIR        = (30,  18,  10,  255)   # ほぼ黒のダークブラウン
HAIR_SH     = (18,  10,   5,  255)   # 髪の影
HAIR_GL1    = (90,  55,  30,  255)   # 光沢1
HAIR_GL2    = (160, 100,  55,  200)  # 光沢2
EYE_OUT     = (20,  12,  20,  255)   # 目の輪郭
IRIS_TOP    = (15,  40,  90,  255)   # 虹彩（上・暗め）
IRIS_MID    = (40,  90, 170,  255)   # 虹彩（中）
IRIS_BOT    = (90, 155, 220,  255)   # 虹彩（下・明るめ）
IRIS_SHINE  = (140, 200, 245, 255)   # 虹彩内ハイライト
PUPIL       = (8,    5,  15,  255)
HL_BIG      = (255, 255, 255, 255)
HL_SMALL    = (210, 230, 255, 240)
LASH        = (20,  12,  20,  255)
BROW        = (38,  22,  12,  255)
BLUSH       = (255, 145, 130,  70)
NOSE        = (215, 170, 135, 255)
LIP         = (225,  95,  95, 255)
LIP_HL      = (255, 180, 180, 200)
COAT        = (248, 249, 255, 255)
COAT_SH     = (215, 220, 238, 255)
COAT_LINE   = (185, 190, 215, 255)
BTN         = (195, 200, 222, 255)
PEN         = (60,  95, 210, 255)
RIBBON      = (235,  75, 115, 255)
CLIP_Y      = (240, 185,  50, 255)
OUTLINE     = (40,  35,  48,  255)
WHITE       = (255, 255, 255, 255)

img  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

cx = W // 2
hy = 178   # 頭中心Y
hr = 92    # 頭半径

# ════════════════════════════════════════════════════
# ① 白衣ボディ
# ════════════════════════════════════════════════════
bt = hy + hr - 8   # 胴体トップ

# 胴体シルエット
draw.ellipse([cx-115, bt, cx+115, H+60], fill=COAT_SH)
draw.rectangle([cx-115, bt+35, cx+115, H], fill=COAT_SH)
draw.ellipse([cx-112, bt-2, cx+112, H+58], fill=COAT)
draw.rectangle([cx-112, bt+34, cx+112, H], fill=COAT)
draw.line([(cx-112, bt+34),(cx-112, H)], fill=OUTLINE, width=2)
draw.line([(cx+112, bt+34),(cx+112, H)], fill=OUTLINE, width=2)

# 中央ライン
draw.line([(cx, bt+16),(cx, H)], fill=COAT_LINE, width=2)

# ボタン
for i in range(3):
    by = bt + 50 + i * 40
    draw.ellipse([cx-5, by-5, cx+5, by+5], fill=BTN, outline=OUTLINE, width=1)

# ポケット
px, py, pw, ph = cx-82, bt+30, 42, 30
draw.rectangle([px, py, px+pw, py+ph], fill=COAT, outline=COAT_LINE, width=2)
draw.rectangle([px+15, py-8, px+22, py+4], fill=PEN, outline=OUTLINE, width=1)
draw.ellipse([px+13, py-12, px+24, py-5], fill=RIBBON, outline=OUTLINE, width=1)

# 衿
col = [(cx-32,bt+10),(cx,bt+46),(cx+32,bt+10),(cx+16,bt+2),(cx-16,bt+2)]
draw.polygon(col, fill=COAT, outline=OUTLINE, width=2)

# ════════════════════════════════════════════════════
# ② 耳
# ════════════════════════════════════════════════════
for side in [-1, 1]:
    ex = cx + side*(hr-4)
    draw.ellipse([ex-13, hy-12, ex+13, hy+12], fill=SKIN, outline=OUTLINE, width=2)
    draw.ellipse([ex-7, hy-6, ex+7, hy+6], fill=SKIN_SH)
    if side == 1:  # 右耳ピアス
        draw.ellipse([ex+4, hy+8, ex+12, hy+16], fill=RIBBON, outline=OUTLINE, width=1)

# ════════════════════════════════════════════════════
# ③ 首
# ════════════════════════════════════════════════════
draw.rectangle([cx-18, hy+hr-10, cx+18, bt+16], fill=SKIN)
draw.line([(cx-18, hy+hr-10),(cx-18, bt+16)], fill=OUTLINE, width=2)
draw.line([(cx+18, hy+hr-10),(cx+18, bt+16)], fill=OUTLINE, width=2)

# ════════════════════════════════════════════════════
# ④ 後ろ髪（サイドに自然に流れる）
# ════════════════════════════════════════════════════
# 左
lh = [(cx-hr+10, hy-hr+35),(cx-hr-5, hy+15),(cx-hr-12, hy+hr+30),
      (cx-hr+5,  hy+hr+55),(cx-55,   hy+hr+72),(cx-30,  hy+hr+58),
      (cx-hr+20, hy+hr+18),(cx-hr+16, hy+10),(cx-hr+18, hy-hr+48)]
draw.polygon(lh, fill=HAIR)

# 右
rh = [(cx+hr-10, hy-hr+35),(cx+hr+5, hy+15),(cx+hr+12, hy+hr+30),
      (cx+hr-5,  hy+hr+55),(cx+55,   hy+hr+72),(cx+30,  hy+hr+58),
      (cx+hr-20, hy+hr+18),(cx+hr-16, hy+10),(cx+hr-18, hy-hr+48)]
draw.polygon(rh, fill=HAIR)

# ════════════════════════════════════════════════════
# ⑤ 顔（アニメ調：丸めの卵型）
# ════════════════════════════════════════════════════
# 頬のふっくら感（下側を少し広げる）
draw.ellipse([cx-hr, hy-hr, cx+hr, hy+hr+6], fill=SKIN, outline=OUTLINE, width=3)

# 顔の立体感（ハイライト）
hi_img = Image.new("RGBA", (W,H), (0,0,0,0))
hi_d   = ImageDraw.Draw(hi_img)
hi_d.ellipse([cx-48, hy-72, cx+32, hy-10], fill=(*SKIN_HL[:3], 80))
img = Image.alpha_composite(img, hi_img)
draw = ImageDraw.Draw(img)

# ════════════════════════════════════════════════════
# ⑥ 前髪（アニメ調：重めぱっつん）
# ════════════════════════════════════════════════════
# 頭頂部
draw.ellipse([cx-hr+2, hy-hr-14, cx+hr-2, hy-hr+62], fill=HAIR)

# 前髪メイン
bang = [
    (cx-hr+6,  hy-hr+30),
    (cx-hr-4,  hy-hr+52),
    (cx-hr+2,  hy-hr+72),
    (cx-68,    hy-26),
    (cx-42,    hy-46),
    (cx-18,    hy-54),
    (cx+12,    hy-55),
    (cx+35,    hy-48),
    (cx+58,    hy-30),
    (cx+hr-4,  hy-hr+70),
    (cx+hr+2,  hy-hr+50),
    (cx+hr-6,  hy-hr+28),
    (cx,       hy-hr-18),
]
draw.polygon(bang, fill=HAIR, outline=OUTLINE, width=2)

# 前髪の毛束感（少し明るい線）
for ox, oy, ex2, ey2 in [
    (cx-55, hy-hr+60, cx-68, hy-22),
    (cx-28, hy-hr+68, cx-30, hy-50),
    (cx+20, hy-hr+68, cx+22, hy-50),
    (cx+48, hy-hr+62, cx+60, hy-25),
]:
    draw.line([(ox,oy),(ex2,ey2)], fill=HAIR_GL1, width=2)

# 髪の光沢（白っぽいハイライト帯）
gl_img = Image.new("RGBA", (W,H), (0,0,0,0))
gl_d   = ImageDraw.Draw(gl_img)
gl_pts = [(cx-30, hy-hr-10),(cx+18, hy-hr-10),(cx+38, hy-hr+30),(cx+22, hy-hr+44),(cx-12, hy-hr+44),(cx-36, hy-hr+28)]
gl_d.polygon(gl_pts, fill=(*HAIR_GL2[:3], 130))
img = Image.alpha_composite(img, gl_img)
draw = ImageDraw.Draw(img)

# ヘアクリップ
draw.ellipse([cx+48, hy-hr+58, cx+62, hy-hr+68], fill=CLIP_Y, outline=OUTLINE, width=2)

# ════════════════════════════════════════════════════
# ⑦ 眉毛（細め・アーチ）
# ════════════════════════════════════════════════════
for side in [-1, 1]:
    bx = cx + side*30
    # 眉本体
    for t in range(4):
        draw.arc([bx-22, hy-50+t, bx+22, hy-24+t],
                 start=215 if side<0 else 325,
                 end  =325 if side<0 else 360+35,
                 fill=BROW, width=3-t//2)

# ════════════════════════════════════════════════════
# ⑧ 目（アニメ調・大きめ）
# ════════════════════════════════════════════════════
def draw_anime_eye(draw, img, cx_e, cy_e, w, h, side):
    """アニメ調の目を描画"""
    # --- 白目 ---
    draw.ellipse([cx_e-w, cy_e-h, cx_e+w, cy_e+h],
                 fill=WHITE, outline=EYE_OUT, width=2)

    # --- 虹彩グラデーション（上から暗→明） ---
    steps = 14
    for i in range(steps):
        t  = i / steps
        ir = int(IRIS_TOP[0]*(1-t) + IRIS_BOT[0]*t)
        ig = int(IRIS_TOP[1]*(1-t) + IRIS_BOT[1]*t)
        ib = int(IRIS_TOP[2]*(1-t) + IRIS_BOT[2]*t)
        ey_off = int(h*0.88 * (2*t-1))
        ew = int(w*0.82 * math.sqrt(max(0, 1-((ey_off)/(h*0.88))**2)) + 1)
        if ew > 0:
            draw.line([(cx_e-ew, cy_e+ey_off),(cx_e+ew, cy_e+ey_off)],
                      fill=(ir,ig,ib,255), width=2)

    # 虹彩の縁取り
    iw, ih2 = int(w*0.82), int(h*0.88)
    draw.ellipse([cx_e-iw, cy_e-ih2, cx_e+iw, cy_e+ih2],
                 outline=(*IRIS_TOP[:3],200), width=1)

    # --- 瞳孔 ---
    pw2, ph2 = int(w*0.38), int(h*0.52)
    draw.ellipse([cx_e-pw2, cy_e-ph2, cx_e+pw2, cy_e+ph2], fill=PUPIL)

    # --- 虹彩内ハイライト（小さめ） ---
    draw.ellipse([cx_e-pw2+3, cy_e-ph2+2, cx_e-pw2+10, cy_e-ph2+8],
                 fill=IRIS_SHINE)

    # --- 大ハイライト（定番の白い反射） ---
    hx = cx_e + int(w*0.28)*side*(-1)
    hy2 = cy_e - int(h*0.52)
    hw, hh = int(w*0.32), int(h*0.38)
    draw.ellipse([hx-hw, hy2-hh, hx+hw, hy2+hh], fill=HL_BIG)

    # --- 小ハイライト ---
    draw.ellipse([cx_e+int(w*0.15)*side, cy_e+int(h*0.15),
                  cx_e+int(w*0.15)*side+int(w*0.18), cy_e+int(h*0.15)+int(h*0.20)],
                 fill=HL_SMALL)

    # --- 上まつ毛ライン（太め） ---
    draw.arc([cx_e-w-2, cy_e-h-2, cx_e+w+2, cy_e+h+2],
             start=195, end=345, fill=LASH, width=4)

    # --- まつ毛先端（放射状） ---
    lash_count = 8
    for i in range(lash_count):
        ang = math.radians(200 + i * (140/(lash_count-1)))
        sx  = cx_e + int(w*1.02*math.cos(ang))
        sy  = cy_e + int(h*1.02*math.sin(ang))
        ex2 = cx_e + int((w+9)*math.cos(ang))
        ey2 = cy_e + int((h+9)*math.sin(ang))
        draw.line([(sx,sy),(ex2,ey2)], fill=LASH, width=2)

    # --- 下まつ毛（薄め） ---
    draw.arc([cx_e-w+2, cy_e-h+2, cx_e+w-2, cy_e+h-2],
             start=15, end=165, fill=(*LASH[:3],80), width=1)

eye_w, eye_h = 26, 20
for side in [-1, 1]:
    ex = cx + side*30
    ey = hy - 5
    tmp = Image.new("RGBA", (W,H), (0,0,0,0))
    td  = ImageDraw.Draw(tmp)
    draw_anime_eye(td, tmp, ex, ey, eye_w, eye_h, side)
    img = Image.alpha_composite(img, tmp)
draw = ImageDraw.Draw(img)

# ════════════════════════════════════════════════════
# ⑨ 鼻（アニメ調：ほぼ点）
# ════════════════════════════════════════════════════
draw.arc([cx-5, hy+20, cx+5, hy+28], start=30, end=150, fill=NOSE, width=2)

# ════════════════════════════════════════════════════
# ⑩ 口（小さいアーチ笑顔）
# ════════════════════════════════════════════════════
draw.arc([cx-14, hy+32, cx+14, hy+48], start=12, end=168, fill=LIP, width=3)
# 下唇ハイライト
draw.arc([cx-10, hy+38, cx+10, hy+50], start=20, end=160, fill=LIP_HL, width=2)

# ════════════════════════════════════════════════════
# ⑪ ほっぺ（アニメ的・ふわっと）
# ════════════════════════════════════════════════════
bl_img = Image.new("RGBA", (W,H), (0,0,0,0))
bl_d   = ImageDraw.Draw(bl_img)
for side in [-1, 1]:
    bx = cx + side*52
    bl_d.ellipse([bx-20, hy+16, bx+20, hy+34], fill=BLUSH)
img = Image.alpha_composite(img, bl_img)
draw = ImageDraw.Draw(img)

# ════════════════════════════════════════════════════
# ⑫ 保存
# ════════════════════════════════════════════════════
out_main  = OUT_DIR / "mascot.png"
out_small = OUT_DIR / "mascot_small.png"

img.save(out_main, "PNG")
print(f"  ✅ mascot.png → {out_main.relative_to(ROOT)}")

small = img.resize((108, 144), Image.LANCZOS)
small.save(out_small, "PNG")
print(f"  ✅ mascot_small.png → {out_small.relative_to(ROOT)}")
print(f"  open pipeline/mascot/ で確認してください")
