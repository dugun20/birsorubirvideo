"""Grumpo & Nibbo — Episode 16: The Tallest Snowman (snowy field, 60 fps).

Structure G (race, parallel lanes): Grumpo (left lane) and Nibbo (right lane) race to build the TALLEST snowman;
a striped pole with a flag stands between them as the height mark.
  - Both roll their base balls in (Grumpo's is gigantic). Nibbo, quick and neat: middle ball + head with hops,
    then eyes, carrot, smile, twig arms, scarf.
  - Grumpo's second ball is too heavy: he hoists it, wobbles, it slips and flattens him like a pancake. Nibbo giggles.
  - Nibbo hops a bucket onto his snowman: it reaches the flag (sparkle). Grumpo, furious, gets an idea.
  - Grumpo pushes his giant ball up the snowy hill, lets it roll down: it hits a snowy rock ramp, flies and lands
    PERFECTLY on his base. The thump shakes the field: Nibbo's bucket and carrot pop off.
  - Grumpo sleds down on his bottom, launches off the same ramp; mid-air the bucket lands on his head, he grabs
    the carrot, and lands on top of his stack as the HEAD. Carrot on the face, smug pose — way above the flag.
Final: Nibbo hops on his own snowman's head to copy him — still far shorter. Ending: Grumpo wins.
"""
import math, sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow
from hook import overlay, hook_title

W, H, FPS = 1080, 1920, 60
GS = 0.92
GR = 130 * GS
NR = 112
INK = "#1a0a2e"
GFILL = "#9466e0"
NB, NS = "#ffd23c", "#3d2a12"

GROUND = 1700
POLE_X, POLE_H = 600, 420
# Nibbo's snowman (right lane)
NX = 1020
NB_R, NM_R, NH_R = 85, 64, 46
NB_Y = GROUND - NB_R
NM_Y = GROUND - 2 * NB_R - NM_R + 12
NH_Y = NM_Y - NM_R - NH_R + 10
NHOME = NX - NB_R - NR * 0.85
# Grumpo's snowman (left lane)
GX = 230
GB_R, G2_R = 150, 130
GB_Y = GROUND - GB_R
G2_Y = GROUND - 2 * GB_R - G2_R + 14
GTOP_Y = G2_Y - G2_R - GR + 14          # Grumpo sitting as the head
GHOME = GX + GB_R + GR * 0.82
G2_PARK = GX - GB_R - G2_R - 10
# hill (left): plateau + slope down, snowy rock ramp near the bottom
PLAT_Y = 1260
SLOPE_A = (-1010.0, PLAT_Y)
SLOPE_B = (-460.0, GROUND)
RAMP_X = -330

# ---- times
T_IN1 = 1.5
T_CUT1 = 1.55
T_N2_0, T_N2_1 = 1.65, 2.15
T_NHOP0, T_NHOP1, T_NPLACE = 2.3, 2.85, 2.58
T_NH_0, T_NH_1 = 2.95, 3.25
T_NHHOP0, T_NHHOP1, T_NHPLACE = 3.3, 3.8, 3.55
T_DEC = [3.88, 4.0, 4.12, 4.24, 4.36]   # eyes, carrot, smile, arms, scarf
T_GHOP0, T_GHOP1 = 1.6, 2.15
T_CUT2 = 4.5
T_G2_0, T_G2_1 = 4.5, 5.35
T_GLIFT0, T_GLIFT1 = 5.5, 6.35
T_SLIP = 6.5
T_FLAT = 6.72
T_CUT3 = 7.2
T_GIGGLE0, T_GIGGLE1 = 7.25, 7.95
T_POP = 7.9
T_NLOOK = 8.0
T_BKT0, T_BKT1, T_BKTPLACE = 8.4, 8.9, 8.66
T_REACH = 8.95
T_CUT4 = 9.6
T_GSEE = 9.75
T_IDEA = 10.4
T_UP0, T_UP1 = 10.75, 13.0
T_HOPOVER0, T_HOPOVER1 = 13.1, 13.5
T_PUSH = 13.6
T_ROLL0, T_ROLL1 = 13.7, 14.5
T_FLY1 = 15.25
T_LANDBALL = T_FLY1
T_POPOFF = 15.45
T_SLED0, T_SLED1 = 15.65, 16.35
T_GFLY1 = 17.3
T_BUCKET_ON = 16.95
T_CARROT_GRAB = 16.8
T_NOSE0, T_NOSE1 = 17.55, 17.9
T_POSE = 18.0
T_NCOPY0, T_NCOPY1 = 19.1, 19.65
T_NSAD = 20.05
T_WINK = 20.75
DUR = 22.0

EV = []


def sfx(t, name, gain=1.0, pitch=1.0):
    EV.append({"t": round(t, 3), "name": name, "gain": gain, "pitch": pitch})


def cl(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def seg(t, a, b):
    return cl((t - a) / (b - a)) if b > a else float(t >= a)


def eio(p):
    return p * p * (3 - 2 * p)


def eout(p):
    return 1 - (1 - p) ** 3


def ein(p):
    return p ** 3


def eback(p, s=1.7):
    p -= 1
    return p * p * ((s + 1) * p + s) + 1


def squash(t, t0, d=0.3, a=0.22):
    k = t - t0
    if 0 <= k < d:
        s = math.sin(math.pi * k / d)
        return 1 + a * 0.6 * s, 1 - a * s
    return 1.0, 1.0


def wob(t, t0, d=0.6, a=10.0, f=18.0):
    k = t - t0
    if 0 <= k < d:
        return a * math.exp(-k * 5) * math.sin(k * f)
    return 0.0


def bodypt(x, y, s, rot, sx, sy, px, py):
    a = math.radians(rot)
    lx, ly = px * s * sx, py * s * sy
    return x + lx * math.cos(a) - ly * math.sin(a), y + lx * math.sin(a) + ly * math.cos(a)


def arm(x0, y0, x1, y1, col, w=13, sag=20):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    return f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


def hand(x, y, fill, stroke, r=16):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="5"/>'


def slope_y(x):
    """hill height at x (without the ramp rock)."""
    if x <= SLOPE_A[0]:
        return PLAT_Y
    if x >= SLOPE_B[0]:
        return GROUND
    p = (x - SLOPE_A[0]) / (SLOPE_B[0] - SLOPE_A[0])
    return lerp(PLAT_Y, GROUND, p * p * (3 - 2 * p) * 0.35 + p * 0.65)


RAMP_H, RAMP_W = 72, 125


def ground_y(x):
    y = slope_y(x)
    d = (x - RAMP_X) / RAMP_W
    if abs(d) < 1:
        y -= RAMP_H * (1 - d * d)
    return y


def on_slope(x, r):
    """centre of a ball of radius r resting on the ground at x (approx normal offset)."""
    dx = 4
    sl = (ground_y(x + dx) - ground_y(x - dx)) / (2 * dx)
    n = math.hypot(1, sl)
    return x + r * sl / n, ground_y(x) - r / n


# ---------------------------------------------------------------- props
def defs():
    return ('<linearGradient id="skyS" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fb8e6"/><stop offset="0.6" stop-color="#c4dcf4"/><stop offset="1" stop-color="#eef5fd"/></linearGradient>'
            '<radialGradient id="snowB" cx="0.38" cy="0.32" r="0.75"><stop offset="0" stop-color="#ffffff"/><stop offset="0.65" stop-color="#f1f6fc"/><stop offset="1" stop-color="#c9d9ec"/></radialGradient>'
            '<linearGradient id="snowG" gradientUnits="userSpaceOnUse" x1="0" y1="1250" x2="0" y2="2300"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#dde8f5"/></linearGradient>'
            '<radialGradient id="vig" cx="0.5" cy="0.55" r="0.8"><stop offset="0.62" stop-color="#1a2a50" stop-opacity="0"/><stop offset="1" stop-color="#1a2a50" stop-opacity="0.3"/></radialGradient>')


def snowball(x, y, r, ang=0.0, sx=1.0, sy=1.0):
    """white ball with shade + rotating speckles (ang in degrees)."""
    o = [f'<g transform="translate({x:.1f} {y:.1f}) scale({sx:.3f} {sy:.3f})">',
         f'<circle r="{r:.1f}" fill="url(#snowB)" stroke="{OL}" stroke-width="{min(7, 3 + r*0.03):.1f}"/>']
    o.append(f'<g transform="rotate({ang:.1f})">')
    for k in range(7):
        a = math.radians(k * 51 + 13)
        rr = r * (0.35 + 0.45 * ((k * 37) % 10) / 10)
        o.append(f'<ellipse cx="{rr*math.cos(a):.1f}" cy="{rr*math.sin(a):.1f}" rx="{r*0.08:.1f}" ry="{r*0.05:.1f}" fill="#c7d8ec" transform="rotate({k*40} {rr*math.cos(a):.1f} {rr*math.sin(a):.1f})"/>')
    o.append(f'<path d="M{-r*0.55:.1f} {r*0.2:.1f} q{r*0.2:.1f} {r*0.25:.1f} {r*0.45:.1f} {r*0.3:.1f}" fill="none" stroke="#b9cde6" stroke-width="{r*0.05:.1f}" stroke-linecap="round"/>')
    o.append('</g>')
    o.append(f'<ellipse cx="{-r*0.38:.1f}" cy="{-r*0.45:.1f}" rx="{r*0.22:.1f}" ry="{r*0.11:.1f}" fill="#fff" transform="rotate(-35 {-r*0.38:.1f} {-r*0.45:.1f})"/>')
    o.append('</g>')
    return "".join(o)


def carrot(x, y, rot=0.0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<path d="M0 -9 L46 0 L0 9 Q -6 0 0 -9Z" fill="#ff8a1e" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M14 -4 l2 6 M26 -2 l2 4" stroke="#c45a08" stroke-width="3" stroke-linecap="round"/></g>')


def bucket(x, y, rot=0.0, s=1.0):
    """bucket hat; (x,y) = rim centre."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<path d="M-46 0 L-34 -62 L34 -62 L46 0Z" fill="#5f86c8" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<path d="M-40 -14 L40 -14" stroke="#86a9e0" stroke-width="7"/>'
            f'<rect x="-52" y="-6" width="104" height="14" rx="6" fill="#4a6eb0" stroke="{OL}" stroke-width="5"/>'
            f'<path d="M-30 -56 l-6 42" stroke="#a9c4ee" stroke-width="6" stroke-linecap="round" opacity="0.8"/>'
            f'<path d="M-46 -2 Q 0 40 46 -2" fill="none" stroke="#7d8898" stroke-width="4"/></g>')


def twig(x, y, ang, L=90):
    a = math.radians(ang)
    ex, ey = x + L * math.cos(a), y + L * math.sin(a)
    fx, fy = x + L * 0.62 * math.cos(a), y + L * 0.62 * math.sin(a)
    b = a - 0.6
    return (f'<path d="M{x:.1f} {y:.1f} L{ex:.1f} {ey:.1f} M{fx:.1f} {fy:.1f} l{26*math.cos(b):.1f} {26*math.sin(b):.1f}" '
            f'stroke="{OL}" stroke-width="11" stroke-linecap="round" fill="none"/>'
            f'<path d="M{x:.1f} {y:.1f} L{ex:.1f} {ey:.1f} M{fx:.1f} {fy:.1f} l{26*math.cos(b):.1f} {26*math.sin(b):.1f}" '
            f'stroke="#8a5a34" stroke-width="5" stroke-linecap="round" fill="none"/>')


def flag_pole(t, glow=0.0):
    top = GROUND - POLE_H
    o = [f'<rect x="{POLE_X-9}" y="{top}" width="18" height="{POLE_H+4}" rx="6" fill="#ffffff" stroke="{OL}" stroke-width="5"/>']
    for k in range(0, POLE_H, 60):
        o.append(f'<rect x="{POLE_X-6}" y="{top+k+6}" width="12" height="30" fill="#e8475e"/>')
    wv = 8 * math.sin(t * 6)
    o.append(f'<path d="M{POLE_X+8} {top+4} Q {POLE_X+50} {top+14+wv:.1f} {POLE_X+96} {top+28} Q {POLE_X+50} {top+40-wv:.1f} {POLE_X+8} {top+54}Z" fill="#ffcf2e" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>')
    o.append(f'<circle cx="{POLE_X}" cy="{top-6}" r="13" fill="#ffcf2e" stroke="{OL}" stroke-width="5"/>')
    if glow > 0:
        o.append(f'<circle cx="{POLE_X}" cy="{top+28}" r="{60+60*glow:.0f}" fill="none" stroke="#fff6a8" stroke-width="{10*(1-glow):.1f}" opacity="{1-glow:.2f}"/>')
    return "".join(o)


def pine(x, y, s=1.0, far=False):
    c1 = "#5f9c8c" if far else "#3f8a62"
    c2 = "#7bb3a2" if far else "#58a77a"
    sw = 0 if far else 5
    o = [f'<rect x="{x-8*s:.0f}" y="{y-40*s:.0f}" width="{16*s:.0f}" height="{42*s:.0f}" fill="#7a5236" stroke="{OL}" stroke-width="{sw}"/>']
    for k, (w, h, dy) in enumerate([(110, 90, 0), (90, 80, -60), (64, 70, -116)]):
        yy = y - 30 * s + dy * s
        o.append(f'<path d="M{x-w*s:.0f} {yy:.0f} L{x:.0f} {yy-h*s*1.4:.0f} L{x+w*s:.0f} {yy:.0f}Z" fill="{c1}" stroke="{OL}" stroke-width="{sw}" stroke-linejoin="round"/>')
        o.append(f'<path d="M{x-w*s*0.55:.0f} {yy-h*s*0.62:.0f} L{x:.0f} {yy-h*s*1.4:.0f} L{x+w*s*0.55:.0f} {yy-h*s*0.62:.0f} Q {x+w*s*0.2:.0f} {yy-h*s*0.5:.0f} {x:.0f} {yy-h*s*0.66:.0f} Q {x-w*s*0.25:.0f} {yy-h*s*0.48:.0f} {x-w*s*0.55:.0f} {yy-h*s*0.62:.0f}Z" fill="#ffffff" stroke="{OL}" stroke-width="{sw*0.7:.1f}" stroke-linejoin="round"/>')
        o.append(f'<path d="M{x+w*s*0.1:.0f} {yy-4:.0f} L{x+w*s:.0f} {yy:.0f}" stroke="{c2}" stroke-width="{6*s:.0f}" opacity="0.6"/>')
    return "".join(o)


def world(t):
    o = [f'<rect x="-1600" y="-400" width="4000" height="3000" fill="url(#skyS)"/>']
    # pale sun
    o.append('<circle cx="1050" cy="640" r="150" fill="#ffffff" opacity="0.35"/><circle cx="1050" cy="640" r="70" fill="#fffdf2" opacity="0.8"/>')
    # far mountains
    o.append(f'<path d="M-1600 {GROUND-300} L-1250 {GROUND-760} L-1000 {GROUND-470} L-700 {GROUND-860} L-380 {GROUND-500} L-80 {GROUND-780} L260 {GROUND-430} L620 {GROUND-820} L960 {GROUND-480} L1320 {GROUND-760} L1700 {GROUND-380} L2200 {GROUND-600} V{GROUND} H-1600Z" fill="#b8cde6"/>')
    for (px, py) in [(-1250, GROUND - 760), (-700, GROUND - 860), (-80, GROUND - 780), (620, GROUND - 820), (1320, GROUND - 760)]:
        o.append(f'<path d="M{px-90} {py+110} L{px} {py} L{px+90} {py+110} L{px+50} {py+90} L{px+20} {py+120} L{px-20} {py+92} L{px-55} {py+118}Z" fill="#f4f8fd"/>')
    o.append(f'<rect x="-1600" y="{GROUND-520}" width="4000" height="420" fill="#eef5fd" opacity="0.45"/>')
    # far pines row
    for k in range(-12, 16):
        x = k * 150 + 40 * math.sin(k * 1.3)
        o.append(pine(x, GROUND - 250 + 18 * math.cos(k), 0.55, far=True))
    # mid snow band
    o.append(f'<path d="M-1600 {GROUND-180} Q -1000 {GROUND-300} -400 {GROUND-200} Q 300 {GROUND-120} 900 {GROUND-220} Q 1500 {GROUND-300} 2400 {GROUND-180} V{GROUND+40} H-1600Z" fill="#e3edf8" stroke="#c4d6ea" stroke-width="4"/>')
    for x, s in [(1040, 0.9), (1210, 1.15), (-1000, 1.1), (-1180, 0.85), (980, 0.7)]:
        o.append(pine(x, GROUND - 120, s))
    # the hill (left)
    pts = " ".join(f"L{x:.0f} {slope_y(x):.1f}" for x in range(int(SLOPE_A[0]), int(SLOPE_B[0]) + 1, 20))
    o.append(f'<path d="M-1700 {PLAT_Y+12} Q -1300 {PLAT_Y-30} {SLOPE_A[0]-40:.0f} {PLAT_Y:.0f} {pts} L{SLOPE_B[0]+40:.0f} {GROUND} V{GROUND+600} H-1700Z" fill="url(#snowG)" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>')
    o.append(f'<path d="M-1600 {PLAT_Y+40} Q -1200 {PLAT_Y+10} {SLOPE_A[0]-40:.0f} {PLAT_Y+30:.0f}" fill="none" stroke="#c9d9ec" stroke-width="10" stroke-linecap="round"/>')
    o.append(pine(-1080, PLAT_Y + 6, 1.0))
    o.append(pine(-860, PLAT_Y + 4, 0.8))
    # ground
    o.append(f'<rect x="{SLOPE_B[0]}" y="{GROUND}" width="3000" height="700" fill="url(#snowG)"/>')
    o.append(f'<path d="M{SLOPE_B[0]+40} {GROUND} H3000" stroke="{OL}" stroke-width="6"/>')
    o.append(f'<rect x="-1700" y="{GROUND+60}" width="4800" height="30" fill="#d4e2f2" opacity="0.7"/>')
    for k in range(-20, 40):
        x = k * 90 + 30 * math.sin(k * 2.3)
        o.append(f'<path d="M{x:.0f} {GROUND+120+40*(k%3)} q24 -10 48 0" fill="none" stroke="#c9d9ec" stroke-width="5" stroke-linecap="round"/>')
    # ramp rock (snow-capped hump)
    pts = " ".join(f"L{x:.0f} {ground_y(x):.1f}" for x in range(RAMP_X - RAMP_W, RAMP_X + RAMP_W + 1, 10))
    o.append(f'<path d="M{RAMP_X-RAMP_W} {GROUND+4} {pts} L{RAMP_X+RAMP_W} {GROUND+4}Z" fill="#8d93a6" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>')
    pts2 = " ".join(f"L{x:.0f} {ground_y(x)-4:.1f}" for x in range(RAMP_X - RAMP_W + 10, RAMP_X + RAMP_W - 9, 10))
    o.append(f'<path d="M{RAMP_X-RAMP_W+10} {GROUND-2} {pts2} Q {RAMP_X+40} {GROUND-RAMP_H*0.45:.0f} {RAMP_X-40} {GROUND-RAMP_H*0.35:.0f} Q {RAMP_X-80} {GROUND-14} {RAMP_X-RAMP_W+10} {GROUND-2}Z" fill="#ffffff" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>')
    return "".join(o)


def tracks(x0, x1, w, op=0.7):
    a, b = min(x0, x1), max(x0, x1)
    if b - a < 4:
        return ""
    return f'<rect x="{a:.0f}" y="{GROUND+2}" width="{b-a:.0f}" height="{w:.0f}" rx="{w/2:.0f}" fill="#c4d6ea" opacity="{op:.2f}"/>'


def snowflakes(t, cx, cy, z):
    o = []
    rnd = random.Random(4)
    for k in range(70):
        x0 = rnd.uniform(-700, 700)
        y0 = rnd.uniform(-1100, 1100)
        sp = rnd.uniform(60, 140)
        rr = rnd.uniform(3, 8)
        x = cx + ((x0 + 30 * math.sin(t * 1.3 + k) + 700) % 1400) - 700
        y = cy + ((y0 + t * sp + 1100) % 2200) - 1100
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rr:.1f}" fill="#ffffff" opacity="0.85"/>')
    return "".join(o)


# ---------------------------------------------------------------- faces
def grumpo_extra(x, y, s, rot, sx, sy, kind, t, red=0.0):
    if not kind:
        return ""
    ink = mix_hex(INK, "#3a0505", red)
    base = mix_hex("#9466e0", "#ff6a52", red)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s*sx:.3f} {s*sy:.3f})">']
    if kind == "strain":
        o.append(f'<path d="M-76 -40 L -18 -8 M76 -40 L 18 -8" fill="none" stroke="{ink}" stroke-width="18" stroke-linecap="round"/>'
                 f'<rect x="-40" y="58" width="80" height="34" rx="12" fill="#fff" stroke="{ink}" stroke-width="7"/>'
                 f'<path d="M-36 75 h72 M-14 60 v30 M12 60 v30" stroke="{ink}" stroke-width="4"/>'
                 f'<path d="M98 -20 q12 18 0 28 q-12 -10 0 -28z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3"/>')
    elif kind == "flat":
        o.append(f'<path d="M-72 -40 Q -40 -64 -8 -44 M8 -44 Q 40 -64 72 -40" fill="none" stroke="{ink}" stroke-width="16" stroke-linecap="round"/>'
                 f'<path d="M-24 78 q8 -10 16 0 t16 0 t16 0" fill="none" stroke="{ink}" stroke-width="8" stroke-linecap="round"/>')
    elif kind == "dizzy":
        for ex in (-38, 38):
            o.append(f'<circle cx="{ex}" cy="16" r="21" fill="#fff" stroke="{ink}" stroke-width="3"/>'
                     f'<path d="M{ex} 16 m-12 0 a12 12 0 1 1 12 12 a8 8 0 1 1 -8 -8 a4 4 0 1 1 4 4" fill="none" stroke="{ink}" stroke-width="4" '
                     f'transform="rotate({t*720:.0f} {ex} 16)"/>')
        o.append(f'<path d="M-30 74 q10 -10 20 0 t20 0 t20 0" fill="none" stroke="{ink}" stroke-width="8" stroke-linecap="round"/>')
    elif kind == "grin":     # proud closed-eye grin
        o.append(f'<path d="M-60 6 h44 v30 h-44z M16 6 h44 v30 h-44z" fill="{base}"/>'
                 f'<path d="M-58 22 q20 -16 40 0 M18 22 q20 -16 40 0" fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M-72 -30 Q -44 -24 -16 -14 M72 -30 Q 44 -24 16 -14" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<path d="M-40 58 Q 0 100 40 58Z" fill="#4a0a14" stroke="{ink}" stroke-width="8" stroke-linejoin="round"/>'
                 f'<path d="M-30 62 h60" stroke="#fff" stroke-width="8"/>')
    elif kind == "wink":
        o.append(f'<path d="M-60 2 h46 v34 h-46z" fill="{base}"/>'
                 f'<path d="M-58 20 q20 -14 40 0" fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M-72 -26 Q -44 -22 -16 -14 M72 -36 Q 44 -30 16 -18" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<path d="M-30 64 q34 24 64 -8" fill="none" stroke="{ink}" stroke-width="10" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


def nib_face(x, y, r, rot, sx, sy, kind):
    if not kind:
        return ""
    f = r / 48 * 1.05
    d = "#2a1a10"
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx*f:.3f} {sy*f:.3f})">']
    if kind == "giggle":
        o.append(f'<path d="M-21 -2 q7 -10 14 0 M7 -2 q7 -10 14 0" fill="none" stroke="{d}" stroke-width="5" stroke-linecap="round"/>'
                 f'<path d="M-6 10 q6 8 12 0" fill="#7a2a1a" stroke="{d}" stroke-width="3.5"/>'
                 f'<path d="M-30 -8 q-4 6 0 10" fill="none" stroke="{d}" stroke-width="3" opacity="0.0"/>')
    elif kind == "proud":
        o.append(f'<path d="M-21 -2 q7 -10 14 0 M7 -2 q7 -10 14 0" fill="none" stroke="{d}" stroke-width="5" stroke-linecap="round"/>'
                 f'<path d="M-12 8 q12 18 24 0z" fill="#7a2a1a" stroke="{d}" stroke-width="4" stroke-linejoin="round"/>')
    elif kind == "sad":
        o.append(f'<path d="M-24 -16 l12 -4 M24 -16 l-12 -4" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<ellipse cx="-14" cy="-3" rx="6" ry="7" fill="{d}"/><ellipse cx="14" cy="-3" rx="6" ry="7" fill="{d}"/>'
                 '<circle cx="-12" cy="-6" r="2" fill="#fff"/><circle cx="16" cy="-6" r="2" fill="#fff"/>'
                 f'<path d="M-9 17 q9 -8 18 0" fill="none" stroke="{d}" stroke-width="4.5" stroke-linecap="round"/>'
                 f'<path d="M-18 6 v8" stroke="#8fd8ff" stroke-width="4" stroke-linecap="round"/>')
    elif kind == "lookup":
        o.append(f'<ellipse cx="-14" cy="-8" rx="6" ry="8" fill="{d}"/><ellipse cx="14" cy="-8" rx="6" ry="8" fill="{d}"/>'
                 '<circle cx="-12" cy="-12" r="2.2" fill="#fff"/><circle cx="16" cy="-12" r="2.2" fill="#fff"/>'
                 f'<path d="M-24 -20 q8 -6 16 -2 M8 -22 q8 -4 16 2" fill="none" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<path d="M-6 12 q6 4 12 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


def nib_snowman_face(t, cx, cy, items):
    """coal eyes / carrot / smile / arms / scarf on Nibbo's snowman head (cx, cy)."""
    o = []
    e, c, sm, ar, sc = items
    if ar > 0:
        o.append(f'<g opacity="{min(1, ar*3):.2f}">' + twig(NX - NM_R + 6, NM_Y - 10, 200 - 20 * (1 - ar), 90 * min(1, ar * 1.5)) +
                 twig(NX + NM_R - 6, NM_Y - 10, -20 + 20 * (1 - ar), 90 * min(1, ar * 1.5)) + '</g>')
    if sc > 0:
        k = eback(min(1, sc), 2)
        o.append(f'<g transform="translate({NX} {NH_Y+NH_R-8}) scale({k:.2f})"><path d="M-50 -10 Q 0 8 50 -10 L52 10 Q 0 28 -52 10Z" fill="#e8475e" stroke="{OL}" stroke-width="5"/>'
                 f'<path d="M24 6 L34 60 L54 56 L44 4Z" fill="#e8475e" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
                 f'<path d="M-30 2 l0 14 M-10 6 l0 14 M10 6 l0 14" stroke="#ffffff" stroke-width="5"/></g>')
    if e > 0:
        k = eback(min(1, e), 2)
        o.append(f'<circle cx="{cx-17}" cy="{cy-10}" r="{7*k:.1f}" fill="#2a2430"/><circle cx="{cx+17}" cy="{cy-10}" r="{7*k:.1f}" fill="#2a2430"/>')
    if sm > 0:
        k = min(1, sm)
        for i in range(5):
            a = math.radians(200 + i * 35)
            o.append(f'<circle cx="{cx+24*math.cos(math.radians(30+i*30)):.1f}" cy="{cy+10+10*math.sin(math.radians(30+i*30)):.1f}" r="{4*k:.1f}" fill="#2a2430"/>')
    return "".join(o)


# ---------------------------------------------------------------- states
def nib_items(t):
    """per item 'pop' progress for Nibbo's snowman decorations."""
    return [seg(t, d, d + 0.25) for d in T_DEC]


def _nib_scoop_hop(n, t, s0, s1, h0, h1, tp, r, target_y, hop_h):
    """scoop a ball overhead (s0..s1), then hop and drop it onto the snowman (h0..h1, placed at tp)."""
    hx = NHOME
    over = GROUND - 2 * NR + 10
    if t < h0:
        p = seg(t, s0, s1)
        br = lerp(8, r, eout(p))
        n["carry"] = (hx + 6, over - br + 26 * (1 - p), br, 0)
        n["hL"] = (hx + 6 - br + 4, n["carry"][1] + br * 0.4)
        n["hR"] = (hx + 6 + br - 4, n["carry"][1] + br * 0.4)
        n["ex"], n["kind"] = "blank", "proud"
        n["sx"], n["sy"] = 1 + 0.05 * math.sin(t * 40) * (1 - p), 1 - 0.05 * math.sin(t * 40) * (1 - p)
        return n
    p = seg(t, h0, h1)
    n["x"] = hx + 60 * math.sin(math.pi * p)
    n["y"] = GROUND - NR - hop_h * math.sin(math.pi * p)
    n["ex"] = "joy"
    if t < tp:
        q = eio(seg(t, h0, tp))
        cx_ = lerp(hx + 6, NX, q)
        cy_ = lerp(n["y"] - NR - r + 26, target_y, q)
        n["carry"] = (cx_, cy_, r, 0)
        n["hL"] = (cx_ - r + 4, cy_ + r * 0.4)
        n["hR"] = (cx_ + r - 4, cy_ + r * 0.4)
    if t >= h1:
        n["sx"], n["sy"] = squash(t, h1, 0.2, 0.12)
    return n


def nibbo_state(t):
    n = dict(x=NHOME, y=GROUND - NR, rot=0.0, sx=1.0, sy=1.0, ex="happy", kind=None, hL=None, hR=None, carry=None)
    if t < T_IN1:
        p = eout(seg(t, -0.25, T_IN1))
        bx = lerp(899, NX, p)
        br = lerp(40, NB_R, p)
        n["x"] = bx - br - NR * 0.78
        n["y"] = GROUND - NR + 6 * abs(math.sin(t * 14))
        n["rot"] = 8
        n["hL"] = (bx - br * 0.85, GROUND - br * 0.9)
        n["hR"] = (bx - br * 0.75, GROUND - br * 0.45)
        return n
    if t < T_N2_0:
        n["ex"], n["kind"] = "blank", "proud"
        n["sx"], n["sy"] = squash(t, T_IN1, 0.25, 0.1)
        return n
    if t < T_NH_0:
        return _nib_scoop_hop(n, t, T_N2_0, T_N2_1, T_NHOP0, T_NHOP1, T_NPLACE, NM_R, NM_Y, 300)
    if t < T_DEC[0]:
        return _nib_scoop_hop(n, t, T_NH_0, T_NH_1, T_NHHOP0, T_NHHOP1, T_NHPLACE, NH_R, NH_Y, 380)
    if t < T_GIGGLE0:
        k = sum(1 for d in T_DEC if t >= d)
        n["ex"], n["kind"] = "blank", "proud"
        n["x"] = NHOME + 40
        n["y"] = GROUND - NR - 70 * abs(math.sin((t - T_DEC[0]) * 10))
        n["hR"] = (NX - 50 + 8 * math.sin(t * 30), NH_Y + 18 if k % 2 == 0 else NM_Y - 10)
        n["rot"] = 6
        if t >= T_DEC[-1] + 0.3:
            n["hR"] = None
            n["ex"], n["kind"] = "joy", None
            n["y"] = GROUND - NR - 30 * abs(math.sin((t - T_DEC[-1]) * 8))
        return n
    if t < T_NLOOK:
        n["ex"], n["kind"] = "blank", "giggle"
        n["rot"] = 6 * math.sin(t * 22)
        n["y"] = GROUND - NR - 10 * abs(math.sin(t * 11))
        n["hR"] = (n["x"] + 60, GROUND - NR + 40)
        n["look_left"] = True
        return n
    if t < T_BKT0:
        n["ex"], n["kind"] = "blank", "lookup"
        n["rot"] = 10 * seg(t, T_NLOOK, T_NLOOK + 0.2)
        if t >= T_BKT0 - 0.15:
            n["sx"], n["sy"] = 1.1, 0.9
        return n
    if t < T_REACH + 0.05:
        p = seg(t, T_BKT0, T_BKT1)
        hx = NHOME
        n["x"] = hx + 60 * math.sin(math.pi * p)
        n["y"] = GROUND - NR - 470 * math.sin(math.pi * p)
        n["ex"] = "joy"
        if t < T_BKTPLACE:
            q = eio(seg(t, T_BKT0, T_BKTPLACE))
            bx = lerp(hx, NX, q)
            by = lerp(n["y"] - NR - 4, NH_Y - NH_R + 8, q)
            n["carry"] = ("bucket", bx, by)
            n["hL"] = (bx - 44, by - 20)
            n["hR"] = (bx + 44, by - 20)
        if t >= T_BKT1:
            n["sx"], n["sy"] = squash(t, T_BKT1, 0.2, 0.12)
        return n
    if t < T_POPOFF:
        n["ex"], n["kind"] = "blank", "proud"
        n["y"] = GROUND - NR - 60 * abs(math.sin((t - T_REACH) * 7)) * (1 - seg(t, T_REACH + 0.9, T_REACH + 1.1))
        n["hL"] = (n["x"] - 80, n["y"] - 120)
        n["hR"] = (n["x"] + 80, n["y"] - 120)
        if t >= T_REACH + 1.1:
            n["hL"], n["hR"] = None, None
            n["ex"], n["kind"] = "happy", None
        if t >= T_FLY1 - 0.1:
            n["ex"], n["kind"] = "wow", None
        return n
    if t < T_NCOPY0:
        n["ex"], n["kind"] = "wow", None
        n["sx"], n["sy"] = squash(t, T_POPOFF, 0.25, 0.15)
        if t >= T_POSE + 0.1:
            n["ex"], n["kind"] = "blank", "lookup"
        if t >= T_POSE + 0.7:
            n["ex"], n["kind"] = "blank", "sad"
        return n
    p = seg(t, T_NCOPY0, T_NCOPY1)
    top_y = NH_Y - NH_R - NR + 14
    if t < T_NCOPY1:
        n["x"] = lerp(NHOME, NX, eio(p))
        n["y"] = lerp(GROUND - NR, top_y, p) - 220 * math.sin(math.pi * p)
        n["ex"] = "joy"
        return n
    n["x"], n["y"] = NX, top_y
    n["sx"], n["sy"] = squash(t, T_NCOPY1, 0.25, 0.14)
    n["ex"], n["kind"] = "blank", "proud"
    n["hL"] = (NX - 80, top_y - 90)
    n["hR"] = (NX + 80, top_y - 90)
    if t >= T_NSAD:
        n["ex"], n["kind"] = "blank", "lookup"
        n["hL"], n["hR"] = None, None
    if t >= T_NSAD + 0.5:
        n["ex"], n["kind"] = "blank", "sad"
    return n


R2B = G2_R + 6


def g2_ball(t):
    """Grumpo's second ball: (x, y, r, ang[, squash])"""
    if t < T_G2_0:
        return None
    if t < T_G2_1:
        p = eout(seg(t, T_G2_0, T_G2_1))
        x = lerp(-440, G2_PARK, p)
        r = lerp(50, G2_R, p)
        return (x, GROUND - r, r, (x + 440) / r * 57.3)
    if t < T_GLIFT0:
        return (G2_PARK, GROUND - G2_R, G2_R, (G2_PARK + 440) / G2_R * 57.3)
    top = GROUND - 2 * GR * 1.08 - G2_R + 14
    if t < T_SLIP:
        p = eio(seg(t, T_GLIFT0, T_GLIFT1))
        x = lerp(G2_PARK, G2_PARK + 70, p) + 10 * math.sin(t * 20) * p
        y = lerp(GROUND - G2_R, top, p)
        return (x, y, G2_R, 140 + 6 * math.sin(t * 18) * p)
    if t < T_POP:
        p = ein(seg(t, T_SLIP, T_FLAT))
        x = lerp(G2_PARK + 70, G2_PARK + 30, p)
        y = lerp(top, GROUND - G2_R - 36, p)
        return (x, y, G2_R, 140 - 30 * p)
    x_after = G2_PARK - 70
    if t < T_UP0:
        p = eout(seg(t, T_POP, T_POP + 0.5))
        x = lerp(G2_PARK + 30, x_after, p)
        cx, cy = on_slope(x, G2_R)
        return (cx, cy, G2_R, 110 - (G2_PARK + 30 - x) / G2_R * 57.3)
    top_x = SLOPE_A[0] - 60
    if t < T_UP1:
        p = eio(seg(t, T_UP0, T_UP1))
        x = lerp(x_after, top_x, p)
        r = lerp(G2_R, R2B, p)
        cx, cy = on_slope(x, r)
        return (cx, cy, r, 20 - (x - x_after) / r * 57.3)
    r = R2B
    if t < T_ROLL0:
        x = top_x + 14 * seg(t, T_PUSH, T_ROLL0)
        cx, cy = on_slope(x, r)
        return (cx, cy, r, 20 - (x - x_after) / r * 57.3)
    if t < T_ROLL1:
        p = seg(t, T_ROLL0, T_ROLL1)
        x = lerp(top_x + 14, RAMP_X, p ** 1.8)
        cx, cy = on_slope(x, r)
        return (cx, cy, r, 20 - (x - x_after) / r * 57.3)
    x0, y0 = on_slope(RAMP_X, r)
    if t < T_FLY1:
        p = seg(t, T_ROLL1, T_FLY1)
        x = lerp(x0, GX, p)
        y = lerp(y0, G2_Y, p) - 380 * math.sin(math.pi * p)
        return (x, y, r, 20 - (x - x_after) / r * 57.3)
    k = t - T_FLY1
    sxv = 1 + 0.12 * math.exp(-k * 6) * math.sin(k * 30)
    return (GX, G2_Y, r, 20 - (GX - x_after) / r * 57.3, sxv)


def grumpo_state(t):
    g = dict(x=GHOME, y=GROUND - GR, rot=0.0, sx=1.0, sy=1.0, ex="grumpy", kind=None, look=(-1, 0), red=0.0,
             hR=None, hL=None, bucket=False, carrot=None, front=False)
    if t < T_IN1:
        p = eout(seg(t, -0.25, T_IN1))
        bx = lerp(382, GX, p)
        br = lerp(60, GB_R, p)
        g["x"] = bx + br + GR * 0.82
        g["y"] = GROUND - GR + 6 * abs(math.sin(t * 11))
        g["rot"] = -10
        g["ex"], g["kind"] = "x", "strain"
        g["red"] = 0.2
        g["look"] = (-1, 0)
        g["hR"] = (bx + br * 0.85, GROUND - br * 0.9)
        g["hL"] = (bx + br * 0.75, GROUND - br * 0.45)
        return g
    if t < T_G2_0:
        # hop over the base and walk off to the left (off camera)
        p = seg(t, T_GHOP0, T_GHOP1)
        g["x"] = lerp(GHOME, -60, eio(p)) - 500 * seg(t, T_GHOP1, T_G2_0)
        g["y"] = GROUND - GR - 360 * math.sin(math.pi * p)
        g["ex"] = "smug"
        return g
    b = g2_ball(t)
    if t < T_G2_1 + 0.1:
        bx, by, br = b[0], b[1], b[2]
        g["x"] = bx - br - GR * 0.82
        g["y"] = GROUND - GR + 6 * abs(math.sin(t * 11))
        g["rot"] = 10
        g["ex"], g["kind"] = "x", "strain"
        g["look"] = (1, 0)
        g["hR"] = (bx - br * 0.85, by - br * 0.1)
        g["hL"] = (bx - br * 0.75, by + br * 0.45)
        return g
    if t < T_GLIFT0:
        p = eio(seg(t, T_G2_1 + 0.1, T_GLIFT0))
        g["x"] = lerp(G2_PARK - G2_R - GR * 0.82, G2_PARK, p)
        g["y"] = GROUND - GR - 60 * math.sin(math.pi * p)
        g["look"] = (0, -1)
        return g
    if t < T_SLIP:
        bx, by, br = b[0], b[1], b[2]
        p = eio(seg(t, T_GLIFT0, T_GLIFT1))
        g["x"] = bx - 6
        g["sy"] = lerp(1.0, 1.08, p) + 0.02 * math.sin(t * 30)
        g["sx"] = 2 - g["sy"]
        g["y"] = GROUND - GR * g["sy"]
        g["ex"], g["kind"] = "x", "strain"
        g["red"] = 0.5 * p
        g["rot"] = 4 * math.sin(t * 16) * p
        g["hR"] = (bx + br * 0.8, by + br * 0.55)
        g["hL"] = (bx - br * 0.8, by + br * 0.55)
        return g
    if t < T_POP:
        p = seg(t, T_SLIP, T_FLAT)
        g["x"] = lerp(G2_PARK + 64, G2_PARK + 30, p)
        g["ex"] = "shock"
        g["look"] = (0, -1)
        g["red"] = 0.5 * (1 - p)
        if t >= T_FLAT:
            k = t - T_FLAT
            g["sy"] = 0.3 + 0.04 * math.exp(-k * 6) * math.sin(k * 40)
            g["sx"] = 1.55
            g["y"] = GROUND - GR * g["sy"]
            g["ex"], g["kind"] = "x", "flat"
        else:
            g["sy"] = lerp(1.0, 0.3, ein(p))
            g["sx"] = lerp(1.0, 1.55, ein(p))
            g["y"] = GROUND - GR * g["sy"]
            g["hR"] = (g["x"] + 120, GROUND - 2 * GR * g["sy"])
            g["hL"] = (g["x"] - 120, GROUND - 2 * GR * g["sy"])
        return g
    stand_x = G2_PARK - 70 + G2_R + GR * 0.85
    if t < T_IDEA:
        p = seg(t, T_POP, T_POP + 0.3)
        k = math.sin(p * math.pi * 2.5) * math.exp(-p * 3) if p < 1 else 0
        g["x"] = lerp(G2_PARK + 30, stand_x, eout(p))
        g["sy"] = lerp(0.3, 1.0, eout(p)) + 0.2 * k
        g["sx"] = lerp(1.55, 1.0, eout(p)) - 0.2 * k
        g["y"] = GROUND - GR * g["sy"] - 80 * math.sin(math.pi * p)
        g["ex"] = "angry"
        g["red"] = 0.55
        g["look"] = (-1, 0)
        g["rot"] = 4 * math.sin(t * 18)
        if t >= T_GSEE:
            g["ex"] = "shock"
            g["red"] = 0.2
            g["look"] = (1, -0.6)
            g["rot"] = 0
            g["sx"], g["sy"] = squash(t, T_GSEE, 0.25, 0.12)
            g["y"] = GROUND - GR
        if t >= T_GSEE + 0.35:
            g["ex"] = "angry"
            g["red"] = 0.6
        return g
    if t < T_UP0:
        g["x"] = stand_x
        g["ex"] = "smug"
        g["red"] = 0.6 * (1 - seg(t, T_IDEA, T_IDEA + 0.3))
        g["look"] = (-1, -0.5)
        g["sx"], g["sy"] = squash(t, T_IDEA, 0.25, 0.12)
        return g
    if t < T_UP1:
        bx, by, br = b[0], b[1], b[2]
        gx = bx + br + GR * 0.8
        gxs, gys = on_slope(gx, GR)
        g["x"], g["y"] = gxs, gys + 4 * abs(math.sin(t * 11))
        sl = (ground_y(gx + 4) - ground_y(gx - 4)) / 8
        g["rot"] = -10 + math.degrees(math.atan(sl)) * 0.6
        g["ex"], g["kind"] = "x", "strain"
        g["red"] = 0.35
        g["look"] = (-1, 0)
        g["hR"] = (bx + br * 0.93, by + br * 0.05)
        g["hL"] = (bx + br * 0.78, by + br * 0.5)
        return g
    if t < T_PUSH:
        bx, by, br = b[0], b[1], b[2]
        p = seg(t, T_HOPOVER0, T_HOPOVER1)
        start = on_slope(bx + br + GR * 0.8, GR)
        end = (bx - br - GR * 0.85, PLAT_Y - GR)
        if t < T_HOPOVER0:
            g["x"], g["y"] = start
            g["ex"] = "smug"
            g["look"] = (-1, -0.3)
            return g
        g["x"] = lerp(start[0], end[0], eio(p))
        g["y"] = lerp(start[1], end[1], p) - 280 * math.sin(math.pi * p)
        g["rot"] = -360 * eio(p)
        g["ex"] = "smug"
        if t >= T_HOPOVER1:
            g["sx"], g["sy"] = squash(t, T_HOPOVER1, 0.2, 0.12)
        return g
    plat = (SLOPE_A[0] - 60 - R2B - GR * 0.85, PLAT_Y - GR)
    if t < T_SLED0:
        g["x"], g["y"] = plat
        g["ex"] = "smug"
        g["look"] = (1, 0.3)
        if t < T_ROLL0 + 0.1:
            q = seg(t, T_PUSH - 0.1, T_ROLL0)
            g["hR"] = (plat[0] + 110 + 50 * q, plat[1] + 10)
            g["hL"] = (plat[0] + 100 + 50 * q, plat[1] + 50)
            g["ex"], g["kind"] = "x", "strain"
            g["rot"] = 10
        if t >= T_ROLL1:
            g["look"] = (1, -0.5)
            g["ex"] = "shock"
        if t >= T_LANDBALL + 0.05:
            g["ex"], g["kind"] = "x", "grin"
            g["y"] = plat[1] - 40 * abs(math.sin((t - T_LANDBALL) * 9))
        return g
    g["front"] = True
    if t < T_SLED1:
        p = seg(t, T_SLED0, T_SLED1)
        x = lerp(plat[0] + 40, RAMP_X, p ** 1.6)
        g["x"], g["y"] = on_slope(x, GR)
        g["rot"] = 28 * seg(t, T_SLED0, T_SLED0 + 0.2)
        g["ex"], g["kind"] = "x", "grin"
        g["sx"], g["sy"] = 1.08, 0.92
        return g
    if t < T_GFLY1:
        p = seg(t, T_SLED1, T_GFLY1)
        x0, y0 = on_slope(RAMP_X, GR)
        g["x"] = lerp(x0, GX, p)
        g["y"] = lerp(y0, GTOP_Y, p) - 330 * math.sin(math.pi * p)
        g["rot"] = lerp(28, 0, eio(p)) - 360 * eio(p)
        g["ex"] = "shock" if p < 0.4 else "smug"
        g["look"] = (0.6, -0.6)
        g["bucket"] = t >= T_BUCKET_ON
        if t >= T_CARROT_GRAB:
            g["hR"] = (g["x"] + 140, g["y"] - 10)
            g["carrot"] = ("hand", g["hR"][0], g["hR"][1], -30)
        return g
    g["x"], g["y"] = GX, GTOP_Y
    g["bucket"] = True
    g["sx"], g["sy"] = squash(t, T_GFLY1, 0.3, 0.2)
    g["ex"] = "smug"
    g["look"] = (0.5, 0)
    if t < T_NOSE1:
        q = eio(seg(t, T_NOSE0, T_NOSE1))
        hx, hy = lerp(GX + 140, GX + 10, q), lerp(GTOP_Y - 10, GTOP_Y + 40, q)
        g["hR"] = (hx, hy)
        g["carrot"] = ("hand", hx, hy, lerp(-30, 0, q))
        return g
    g["carrot"] = ("nose",)
    g["ex"], g["kind"] = "x", "grin"
    g["sx"], g["sy"] = squash(t, T_NOSE1, 0.25, 0.1)
    if t >= T_POSE:
        g["hR"] = (GX + 60, GTOP_Y + 96)
        g["hL"] = (GX - 60, GTOP_Y + 100)
    if t >= T_POSE + 0.9:
        g["ex"], g["kind"] = "smug", None
        g["look"] = (1, 0.4)
    if t >= T_WINK:
        g["ex"], g["kind"] = "x", "wink"
    return g


# ---------------------------------------------------------------- camera
def _cut(t0, a, b):
    return [(t0 - 0.001, a), (t0, b)]


CK = ([(0.0, (610, 1290, 1.3)), (T_IN1, (610, 1300, 1.34))] + _cut(T_CUT1, (610, 1300, 1.34), (880, 1300, 1.5)) +
      [(T_NPLACE, (900, 1260, 1.45)), (T_NHPLACE, (920, 1250, 1.45)), (T_DEC[-1], (960, 1260, 1.55)), (T_CUT2 - 0.001, (960, 1260, 1.55))] +
      [(T_CUT2, (-200, 1300, 1.4)), (T_G2_1, (-80, 1300, 1.45)), (T_GLIFT1, (-90, 1280, 1.45)), (T_FLAT + 0.1, (-90, 1320, 1.6)),
       (T_CUT3 - 0.001, (-90, 1330, 1.64))] +
      [(T_CUT3, (880, 1290, 1.5)), (T_BKT0, (900, 1260, 1.42)), (T_REACH, (930, 1220, 1.42)), (T_REACH + 0.4, (800, 1240, 1.28)),
       (T_CUT4 - 0.001, (790, 1245, 1.26))] +
      [(T_CUT4, (-60, 1300, 1.45)), (T_IDEA, (-90, 1290, 1.45)), (T_UP0 + 0.6, (-300, 1280, 1.3)), (T_UP1, (-800, 1200, 1.25)),
       (T_PUSH, (-1000, 1190, 1.3)), (T_ROLL1, (-330, 1290, 1.1)), (T_FLY1, (40, 1210, 1.05)), (T_POPOFF + 0.1, (60, 1210, 1.05))] +
      _cut(T_SLED0, (60, 1210, 1.05), (-760, 1210, 1.2)) +
      [(T_SLED1, (-320, 1280, 1.15)), (T_GFLY1, (120, 1130, 1.1)), (T_NOSE1, (180, 1090, 1.25)), (T_POSE + 0.4, (200, 1090, 1.25)),
       (T_NCOPY0 - 0.2, (600, 1110, 1.0)), (T_WINK - 0.2, (600, 1110, 1.0)), (DUR, (380, 1060, 1.12))])
SHAKES = [(T_IN1, 5, 0.2), (T_FLAT, 14, 0.35), (T_POP, 6, 0.2), (T_BKTPLACE, 4, 0.15), (T_FLY1, 24, 0.55), (T_GFLY1, 12, 0.3),
          (T_NCOPY1, 5, 0.2)]


def camera(t):
    k0 = CK[0]
    cx, cy, z = CK[-1][1]
    for k1 in CK[1:]:
        if t <= k1[0]:
            p = eio(seg(t, k0[0], k1[0]))
            a, b = k0[1], k1[1]
            cx, cy, z = lerp(a[0], b[0], p), lerp(a[1], b[1], p), lerp(a[2], b[2], p)
            break
        k0 = k1
    amp = 0
    for t0, a, d in SHAKES:
        if t0 <= t < t0 + d:
            amp = max(amp, a * (1 - (t - t0) / d))
    return cx + amp * math.sin(t * 93), cy + amp * math.cos(t * 79), z


def arm_anchor(c, key, side, py0=30):
    """attach the arm on the side of the body the hand is on (no arms across the face)."""
    hx = c[key][0]
    sd = 1 if hx > c["x"] + 10 else (-1 if hx < c["x"] - 10 else side)
    other = "hL" if key == "hR" else "hR"
    if c[other]:
        ox = c[other][0]
        osd = 1 if ox > c["x"] + 10 else (-1 if ox < c["x"] - 10 else -side)
        if osd == sd and key == "hR":
            return sd, py0 - 50
    return sd, py0


# ---------------------------------------------------------------- frame
def frame(t):
    ctx = Ctx()
    g = grumpo_state(t)
    n = nibbo_state(t)
    L = [world(t)]
    # rolling tracks
    L.append(tracks(382, lerp(382, GX, eout(seg(t, -0.25, T_IN1))) + 40, 34))
    L.append(tracks(899, lerp(899, NX, eout(seg(t, -0.25, T_IN1))) - 40, 26))
    if t >= T_G2_0:
        L.append(tracks(-440, lerp(-440, G2_PARK, eout(seg(t, T_G2_0, T_G2_1))) - 20, 30))
    L.append(flag_pole(t, seg(t, T_REACH, T_REACH + 0.6) if t < T_REACH + 0.6 else 0))

    # ---- Nibbo's snowman
    shake = wob(t, T_FLY1 + 0.05, 1.0, 7, 22)
    L.append(shadow(NX, GROUND + 6, 120))
    L.append(snowball(NX, NB_Y, NB_R))
    if t >= T_NPLACE:
        a, b_ = squash(t, T_NPLACE, 0.2, 0.12)
        L.append(snowball(NX + shake * 0.5, NM_Y, NM_R, 0, a, b_))
    items = nib_items(t)
    if t >= T_NHPLACE:
        a, b_ = squash(t, T_NHPLACE, 0.2, 0.12)
        hx = NX + shake
        L.append(nib_snowman_face(t, hx, NH_Y, [0, 0, 0, items[3], items[4]]))
        L.append(snowball(hx, NH_Y, NH_R, 0, a, b_))
        L.append(nib_snowman_face(t, hx, NH_Y, [items[0], 0, items[2], 0, 0]))
        # carrot stays until pop-off
        if items[1] > 0 and t < T_POPOFF:
            L.append(carrot(hx + 4, NH_Y + 2, 8, eback(min(1, items[1]), 2)))
        if T_BKTPLACE <= t < T_POPOFF:
            L.append(bucket(hx, NH_Y - NH_R + 8, -4 + shake, 0.85))
    for k, d in enumerate(T_DEC):
        L.append(star_twinkle(NX + 60 - 30 * (k % 3), NH_Y - 30 + 30 * (k % 2), seg(t, d, d + 0.4)))
    # bucket lying on the ground before Nibbo grabs it
    if t < T_BKT0:
        L.append(bucket(NHOME - 170, GROUND - 4, -100, 0.85))

    # ---- Grumpo's snowman
    gb_r = lerp(60, GB_R, eout(seg(t, -0.25, T_IN1)))
    gbx = lerp(382, GX, eout(seg(t, -0.25, T_IN1)))
    L.append(shadow(gbx, GROUND + 6, gb_r * 1.1))
    L.append(snowball(gbx, GROUND - gb_r, gb_r, (gbx - 382) / gb_r * 57.3, *squash(t, T_FLY1, 0.3, 0.1)))
    b = g2_ball(t)

    def draw_g():
        out = []
        if g["carrot"] and g["carrot"][0] == "hand":
            pass
        out.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "up" if not g["bucket"] else "none", g["look"], g["rot"], g["sx"], g["sy"], drink=False, t=t))
        out.append(grumpo_extra(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], g["kind"], t, g["red"]))
        if g["carrot"] and g["carrot"][0] == "nose":
            out.append(carrot(g["x"] + 2, g["y"] + 40 * GS * g["sy"], 6, 1.5))
        if g["bucket"]:
            bx_, by_ = bodypt(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], 0, -108)
            out.append(bucket(bx_, by_, g["rot"] - 6, 1.15))
        return "".join(out)

    # ball behind/in front of Grumpo depending on phase
    grumpo_drawn = False
    if b:
        bx, by, br, ang = b[:4]
        sxv = b[4] if len(b) > 4 else 1.0
        if T_SLIP <= t < T_POP:
            L.append(draw_g())
            grumpo_drawn = True
        L.append(snowball(bx, by, br, ang, sxv, 2 - sxv))
    if not grumpo_drawn:
        L.append(draw_g())

    # Nibbo
    L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"] if n["kind"] is None else "blank", rot=n["rot"], sx=n["sx"], sy=n["sy"]))
    L.append(nib_face(n["x"], n["y"], NR, n["rot"], n["sx"], n["sy"], n["kind"]))
    if n["carry"]:
        if n["carry"][0] == "bucket":
            L.append(bucket(n["carry"][1], n["carry"][2], 0, 0.85))
        else:
            cx_, cy_, cr, ca = n["carry"]
            L.append(snowball(cx_, cy_, cr, ca))

    # ---- arms + hands
    for side, key in ((1, "hR"), (-1, "hL")):
        if g[key]:
            sd, py = arm_anchor(g, key, side)
            sx_, sy_ = bodypt(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], sd * 112, py)
            L.append(arm(sx_, sy_, g[key][0], g[key][1], INK, 14, 20))
    if g["carrot"] and g["carrot"][0] == "hand":
        L.append(carrot(g["carrot"][1] - 10, g["carrot"][2], g["carrot"][3], 1.5))
    for key in ("hR", "hL"):
        if g[key]:
            L.append(hand(*g[key], mix_hex(GFILL, "#ff6a52", g["red"]), OL, 19))
    for side, key in ((-1, "hL"), (1, "hR")):
        if n[key]:
            sd, py = arm_anchor(n, key, side, 26)
            sx_, sy_ = bodypt(n["x"], n["y"], 1, n["rot"], n["sx"], n["sy"], sd * 96, py)
            L.append(arm(sx_, sy_, n[key][0], n[key][1], NS, 11, 16))
    for key in ("hL", "hR"):
        if n[key]:
            L.append(hand(*n[key], NB, NS, 15))

    # ---- flying bucket + carrot (popped off Nibbo's snowman)
    if T_POPOFF <= t < T_BUCKET_ON:
        p = seg(t, T_POPOFF, T_BUCKET_ON)
        tx, ty = bodypt(*[lerp(RAMP_X - 30, GX, seg(T_BUCKET_ON, T_SLED1, T_GFLY1))], 0, GS, 0, 1, 1, 0, 0) if False else (None, None)
        gp = seg(T_BUCKET_ON, T_SLED1, T_GFLY1)
        x0_, y0_ = on_slope(RAMP_X, GR)
        gx_, gy_ = lerp(x0_, GX, gp), lerp(y0_, GTOP_Y, gp) - 330 * math.sin(math.pi * gp) - 108 * GS
        x = lerp(NX, gx_, p)
        y = lerp(NH_Y - NH_R, gy_, p) - 520 * math.sin(math.pi * p)
        L.append(bucket(x, y, 540 * p, 0.85 + 0.3 * p))
    if T_POPOFF <= t < T_CARROT_GRAB:
        p = seg(t, T_POPOFF, T_CARROT_GRAB)
        gp = seg(T_CARROT_GRAB, T_SLED1, T_GFLY1)
        x0_, y0_ = on_slope(RAMP_X, GR)
        gx_, gy_ = lerp(x0_, GX, gp) + 140, lerp(y0_, GTOP_Y, gp) - 330 * math.sin(math.pi * gp) - 10
        x = lerp(NX + 10, gx_, p)
        y = lerp(NH_Y, gy_, p) - 600 * math.sin(math.pi * p)
        L.append(carrot(x, y, 900 * p, 1.2 + 0.3 * p))

    # ---- effects
    if t < T_IN1:
        L.append(speed_lines(gbx + gb_r + 230, GROUND - 120, 180, 0.7))
        L.append(speed_lines(n["x"] - 140, GROUND - 100, 0, 0.7))
    L.append(impact(GX, GROUND - 30, seg(t, T_IN1 - 0.05, T_IN1 + 0.2), "#ffffff"))
    L.append(impact(NX, NM_Y + NM_R - 10, seg(t, T_NPLACE, T_NPLACE + 0.2), "#ffffff"))
    L.append(impact(NX, NH_Y + NH_R - 10, seg(t, T_NHPLACE, T_NHPLACE + 0.2), "#ffffff"))
    if T_GLIFT0 <= t < T_SLIP:
        for k in range(3):
            q = ((t - T_GLIFT0) * 2.2 + k / 3) % 1
            L.append(f'<path d="M{g["x"]+130+20*k:.0f} {g["y"]-60+40*q:.0f} q8 14 0 22 q-8 -8 0 -22z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3" opacity="{1-q:.2f}"/>')
    L.append(impact(G2_PARK + 30, GROUND - 40, seg(t, T_FLAT, T_FLAT + 0.3), "#ffffff"))
    if T_FLAT <= t < T_FLAT + 0.6:
        q = seg(t, T_FLAT, T_FLAT + 0.6)
        for k in range(8):
            a = math.radians(-170 + k * 22)
            L.append(f'<circle cx="{G2_PARK+30+260*q*math.cos(a):.0f}" cy="{GROUND-20+160*q*math.sin(a)+200*q*q:.0f}" r="{12*(1-q)+4:.0f}" fill="#ffffff" stroke="#b9cde6" stroke-width="3"/>')
    L.append(symbol(n["x"] + 10, n["y"] - 170, "?", seg(t, T_NLOOK, T_NLOOK + 0.6), "#3a8fd8"))
    L.append(impact(NX, NH_Y - NH_R, seg(t, T_BKTPLACE, T_BKTPLACE + 0.2), "#ffffff"))
    L.append(star_twinkle(POLE_X + 50, GROUND - POLE_H, seg(t, T_REACH, T_REACH + 0.6)))
    L.append(star_twinkle(POLE_X - 40, GROUND - POLE_H + 40, seg(t, T_REACH + 0.15, T_REACH + 0.7)))
    L.append(symbol(g["x"] + 30, g["y"] - 170, "!", seg(t, T_GSEE, T_GSEE + 0.5)))
    L.append(symbol(g["x"] + 30, g["y"] - 170, "!", seg(t, T_IDEA, T_IDEA + 0.6), "#ffb02a"))
    if T_IDEA <= t < T_IDEA + 0.6:
        L.append(star_twinkle(g["x"] - 60, g["y"] - 140, seg(t, T_IDEA, T_IDEA + 0.6)))
    if b and T_ROLL0 <= t < T_FLY1:
        L.append(speed_lines(b[0] - b[2] - 20, b[1], -20 if t < T_ROLL1 else -50, 0.8))
    if T_ROLL1 - 0.05 <= t < T_ROLL1 + 0.4:
        q = seg(t, T_ROLL1 - 0.05, T_ROLL1 + 0.4)
        for k in range(7):
            a = math.radians(-120 + k * 18)
            L.append(f'<circle cx="{RAMP_X+200*q*math.cos(a):.0f}" cy="{GROUND-RAMP_H+160*q*math.sin(a)+160*q*q:.0f}" r="{12*(1-q)+4:.0f}" fill="#ffffff" stroke="#b9cde6" stroke-width="3"/>')
    L.append(impact(GX, G2_Y + G2_R - 20, seg(t, T_FLY1, T_FLY1 + 0.35)))
    if T_FLY1 <= t < T_FLY1 + 0.7:
        q = seg(t, T_FLY1, T_FLY1 + 0.7)
        for k in range(10):
            a = math.radians(-180 + k * 20)
            L.append(f'<circle cx="{GX+300*q*math.cos(a):.0f}" cy="{G2_Y+G2_R+200*q*math.sin(a)+240*q*q:.0f}" r="{16*(1-q)+5:.0f}" fill="#ffffff" stroke="#b9cde6" stroke-width="3"/>')
    if T_SLED0 <= t < T_GFLY1:
        L.append(speed_lines(g["x"] - 100, g["y"] + 40, 20 if t < T_SLED1 else -50, 0.85))
    if T_SLED0 <= t < T_SLED1:
        q = (t * 4) % 1
        L.append(f'<circle cx="{g["x"]-90-60*q:.0f}" cy="{g["y"]+100-30*q:.0f}" r="{18*(1-q):.0f}" fill="#ffffff" stroke="#b9cde6" stroke-width="3"/>')
    L.append(impact(GX, GTOP_Y + GR - 10, seg(t, T_GFLY1, T_GFLY1 + 0.3)))
    if T_POSE <= t:
        L.append(star_twinkle(GX + 120, GTOP_Y - 160, seg(t, T_POSE, T_POSE + 0.7)))
        L.append(star_twinkle(GX - 110, GTOP_Y - 60, seg(t, T_POSE + 0.25, T_POSE + 0.95)))
    if t >= T_WINK:
        L.append(star_twinkle(GX + 70, GTOP_Y - 20, seg(t, T_WINK, T_WINK + 0.6)))

    cx, cy, z = camera(t)
    L.append(snowflakes(t, cx, cy, z))
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{defs()}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g>'
           f'<rect width="{W}" height="{H}" fill="url(#vig)"/></svg>')
    return overlay(svg, hook_title(t + 0.12, "Who builds the tallest", "SNOWMAN?"))


def build_sfx():
    # soft winter wind bed
    k = 0.0
    while k < DUR:
        sfx(k, "wind", 0.18, 1.2)
        k += 1.6
    sfx(0.0, "whoosh", 0.6, 1.1)
    for k in range(5):
        sfx(0.05 + k * 0.28, "crunch", 0.35, 1.3 + 0.05 * (k % 2))
        sfx(0.15 + k * 0.28, "crunch", 0.3, 1.6)
    sfx(0.3, "strain", 0.6, 1.0)
    sfx(T_IN1 - 0.03, "thud", 0.8, 0.8)
    sfx(T_IN1, "plop", 0.5, 1.3)
    for k in range(3):
        sfx(T_N2_0 + k * 0.28, "crunch", 0.3, 1.7)
        sfx(T_G2_0 + k * 0.45, "crunch", 0.35, 1.1)
    sfx(T_G2_0 + 0.2, "strain", 0.6, 1.1)
    sfx(T_N2_0, "squish", 0.4, 1.6)
    sfx(T_N2_1, "hop", 0.5, 1.4)
    sfx(T_GHOP0, "boing", 0.5, 0.9)
    sfx(T_FLAT + 0.3, "wobble", 0.4, 1.0)
    sfx(T_NHOP0, "boing", 0.5, 1.4)
    sfx(T_NPLACE, "plop", 0.8, 1.2)
    sfx(T_NH_0, "squish", 0.4, 1.8)
    sfx(T_NHHOP0, "boing", 0.5, 1.6)
    sfx(T_NHPLACE, "plop", 0.8, 1.5)
    for k, d in enumerate(T_DEC):
        sfx(d, "pop", 0.5, 1.2 + 0.12 * k)
    sfx(T_DEC[-1] + 0.1, "shine", 0.5, 1.3)
    sfx(T_GLIFT0, "strain", 0.9, 0.95)
    sfx(T_GLIFT0 + 0.5, "strain", 0.9, 1.1)
    sfx(T_GLIFT0 + 0.3, "creak", 0.4, 1.3)
    sfx(T_SLIP, "slide_down", 0.8, 0.8)
    sfx(T_SLIP + 0.05, "gasp", 0.6, 0.9)
    sfx(T_FLAT, "squish", 1.0, 0.7)
    sfx(T_FLAT, "thud", 1.0, 0.7)
    sfx(T_FLAT + 0.05, "crunch", 0.6, 0.8)
    sfx(T_GIGGLE0, "laugh", 0.7, 1.4)
    sfx(T_POP, "boing", 1.0, 0.8)
    sfx(T_POP + 0.1, "grumble", 0.6, 1.0)
    sfx(T_NLOOK, "blip", 0.4, 1.3)
    sfx(T_BKT0, "boing", 0.6, 1.5)
    sfx(T_BKTPLACE, "clank", 0.7, 1.2)
    sfx(T_REACH, "ding", 0.7, 1.3)
    sfx(T_REACH + 0.05, "shine", 0.6, 1.1)
    sfx(T_REACH + 0.15, "cheer", 0.5, 1.5)
    sfx(T_GSEE, "gasp", 0.7, 0.9)
    sfx(T_GSEE + 0.4, "grumble", 0.7, 0.85)
    sfx(T_IDEA, "ding", 0.7, 1.0)
    sfx(T_IDEA + 0.05, "shine", 0.5, 1.0)
    sfx(T_UP0, "strain", 0.8, 0.9)
    for k in range(6):
        sfx(T_UP0 + 0.1 + k * 0.42, "crunch", 0.45, 0.9 + 0.05 * (k % 2))
    sfx(T_UP0 + 1.3, "strain", 0.8, 1.0)
    sfx(T_HOPOVER0, "boing", 0.6, 1.1)
    sfx(T_HOPOVER0 + 0.05, "whoosh", 0.5, 1.2)
    sfx(T_HOPOVER1, "crunch", 0.5, 1.0)
    sfx(T_PUSH, "strain", 0.6, 1.2)
    sfx(T_ROLL0, "rumble", 0.7, 1.0)
    sfx(T_ROLL0 + 0.3, "zoom", 0.5, 0.8)
    sfx(T_ROLL1, "thunk", 0.8, 0.9)
    sfx(T_ROLL1 + 0.02, "whoosh", 0.8, 0.8)
    sfx(T_ROLL1 + 0.2, "slide_up", 0.6, 0.8)
    sfx(T_FLY1 - 0.25, "slide_down", 0.5, 0.9)
    sfx(T_FLY1, "thud", 1.0, 0.6)
    sfx(T_FLY1, "crunch", 0.9, 0.7)
    sfx(T_FLY1 + 0.03, "rumble", 0.7, 1.2)
    sfx(T_POPOFF, "pop", 0.8, 1.0)
    sfx(T_POPOFF + 0.05, "whoosh", 0.6, 1.4)
    sfx(T_LANDBALL + 0.1, "laugh", 0.5, 0.8)
    sfx(T_SLED0, "whoosh", 0.6, 1.0)
    sfx(T_SLED0 + 0.05, "squeak_slide", 0.7, 0.8)
    sfx(T_SLED1, "boing", 0.7, 0.9)
    sfx(T_SLED1 + 0.03, "zoom", 0.6, 1.0)
    sfx(T_CARROT_GRAB, "pop", 0.6, 1.5)
    sfx(T_BUCKET_ON, "clank", 0.8, 1.0)
    sfx(T_GFLY1, "thud", 0.9, 0.9)
    sfx(T_GFLY1 + 0.02, "crunch", 0.6, 1.0)
    sfx(T_NOSE1, "pop", 0.7, 1.0)
    sfx(T_POSE, "ding", 0.6, 1.2)
    sfx(T_POSE + 0.05, "cheer", 0.6, 1.0)
    sfx(T_POSE + 0.6, "gasp", 0.4, 1.4)
    sfx(T_NCOPY0, "boing", 0.6, 1.5)
    sfx(T_NCOPY1, "plop", 0.6, 1.4)
    sfx(T_NSAD, "blip_down", 0.6, 1.0)
    sfx(T_NSAD + 0.5, "deflate", 0.4, 1.4)
    sfx(T_WINK, "cool", 0.6, 1.0)
    sfx(T_WINK + 0.05, "ding", 0.4, 1.8)
