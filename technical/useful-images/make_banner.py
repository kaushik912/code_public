#!/usr/bin/env python3
"""Generate a LinkedIn background banner (1584x396) with a quote."""
from PIL import Image, ImageDraw, ImageFont
import math

# --- LinkedIn banner size, rendered at 2x then downscaled for crispness ---
W, H = 1584, 396
S = 2
w, h = W * S, H * S

# ---------- Fonts ----------
def font(path, size, index=0):
    return ImageFont.truetype(path, size * S, index=index)

GEORGIA        = "/System/Library/Fonts/Supplemental/Georgia.ttf"
GEORGIA_BOLD   = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
GEORGIA_ITALIC = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
AVENIR         = "/System/Library/Fonts/Avenir Next.ttc"

f_main   = font(GEORGIA, 44)
f_bold   = font(GEORGIA_BOLD, 44)
f_italic = font(GEORGIA_ITALIC, 44)
f_kicker = font(AVENIR, 15, index=0)

# ---------- Colors ----------
def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

TOP_L  = (11, 22, 44)     # deep navy
BOT_R  = (23, 41, 74)     # indigo
GLOW   = (56, 120, 150)   # teal glow
WHITE  = (237, 242, 248)
MUTED  = (150, 167, 190)
ACCENT = (240, 191, 106)  # warm gold

# ---------- Background: diagonal gradient ----------
img = Image.new("RGB", (w, h), TOP_L)
grad = Image.new("RGB", (w, h))
gpx = grad.load()
maxd = w + h
for y in range(h):
    for x in range(0, w, 1):
        pass
# faster gradient via row math using numpy-free approach
import array
for y in range(h):
    row = []
    for x in range(w):
        t = (x + y) / maxd
        row.append(lerp(TOP_L, BOT_R, t))
    for x in range(w):
        gpx[x, y] = row[x]
img = grad
draw = ImageDraw.Draw(img, "RGBA")

# ---------- Radial teal glow on the right ----------
glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
cx, cy = int(w * 0.80), int(h * 0.30)
R = int(h * 1.1)
for r in range(R, 0, -6):
    a = int(48 * (1 - r / R) ** 2)
    gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GLOW + (a,))
img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")

# ---------- Subtle "network / nodes" motif (outsourced thinking) ----------
import random
random.seed(7)
nodes = []
for _ in range(22):
    nx = random.randint(int(w * 0.62), int(w * 0.97))
    ny = random.randint(int(h * 0.10), int(h * 0.90))
    nodes.append((nx, ny))
# connect nearby nodes
for i, (ax, ay) in enumerate(nodes):
    for bx, by in nodes[i + 1:]:
        d = math.hypot(ax - bx, ay - by)
        if d < h * 0.34:
            a = int(26 * (1 - d / (h * 0.34)))
            draw.line([ax, ay, bx, by], fill=(120, 170, 200, a), width=1 * S)
for nx, ny in nodes:
    rr = 3 * S
    draw.ellipse([nx - rr, ny - rr, nx + rr, ny + rr], fill=(150, 195, 220, 70))

# ---------- Text ----------
LX = 150 * S            # left margin
def text_w(s, fnt):
    return draw.textlength(s, font=fnt)

# Kicker
kicker = "T H E   A I   E R A"
draw.text((LX, 92 * S), kicker, font=f_kicker, fill=MUTED)
# small accent rule under kicker
draw.line([LX, 122 * S, LX + 46 * S, 122 * S], fill=ACCENT, width=3 * S)

# Quote — two lines, mixed styling for emphasis
line1_y = 150 * S
line2_y = 214 * S

def draw_runs(runs, y):
    x = LX
    for s, fnt, col in runs:
        draw.text((x, y), s, font=fnt, fill=col)
        x += text_w(s, fnt)

draw_runs([
    ("You can ", f_main, WHITE),
    ("outsource your thinking", f_italic, MUTED),
    (",", f_main, WHITE),
], line1_y)

draw_runs([
    ("but you ", f_main, WHITE),
    ("can’t", f_bold, WHITE),
    (" outsource your ", f_main, WHITE),
    ("understanding", f_bold, ACCENT),
    (".", f_main, WHITE),
], line2_y)

# opening quotation mark accent
f_quote = font(GEORGIA_BOLD, 120)
draw.text((LX - 34 * S, 96 * S), "“", font=f_quote, fill=(240, 191, 106, 40))

# ---------- Downscale ----------
final = img.resize((W, H), Image.LANCZOS)
out = "/Users/kkailasnath/GitHub/tac_code/linkedin_banner.png"
final.save(out, "PNG")
print("saved", out, final.size)
