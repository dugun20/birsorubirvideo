"""Grumpo & Nibbo — Episode 13: 3 AM Snack Run (hotel room at night, stealth/infiltration, 60 fps).

Day 1 of Grumpo's diet. It's the middle of the night in a hotel room; his stomach growls and all he can
think about is cake. The cake is in the minibar — which has Nibbo's "NO CAKE" sticker on it, right next to
Nibbo's bed. Sleeping Nibbo (eye mask) has set up defences.
  1. A tin-can pyramid tied to Nibbo's finger: Grumpo sucks in his belly to squeeze past, brushes it,
     catches two falling cans in his hands and the third lands on his head... phew. One step later the
     string yanks Nibbo's finger.
  2. Nibbo sits up, lifts the mask — Grumpo has whooshed behind the curtain (a trembling purple bulge).
     Nibbo squints, yawns, lies back down.
  3. A creaky floorboard right under Nibbo's face: Grumpo freezes mid-tiptoe, holding his breath until
     he turns red; Nibbo smacks her lips and rolls over.
  4. The minibar light floods the room — Grumpo plants himself in front of it to block the glow.
He gets the fancy cake box, sits down, unties the ribbon with care, opens it in a golden glow... a single
celery stick with a Nibbo smiley note. Tap on the shoulder: Nibbo, beaming and proud. Grumpo forces a smile
and CRUNCHES the celery, a tear rolling down. His stomach growls so hard that Nibbo's mask snaps over her eyes.
Ending: the prize was worthless (ödül değersiz). Structure: K stealth/infiltration. No counter.
"""
import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow
from hook import overlay, hook_title

W, H, FPS, DUR = 1080, 1920, 60, 25.0
GS = 0.92
GR = 130 * GS
NR = 112
FLOOR = 1700
GY = FLOOR - GR            # grumpo standing centre y
INK = "#1a0a2e"
GFILL = "#9466e0"
NB, NS = "#ffd23c", "#3d2a12"

PYR_X = 1000               # can pyramid centre
CURT = (1150, 1225)        # left curtain panel
WIN = (1240, 1080, 200, 250)
NBED0, NBED1 = 1420, 1900
MAT = 1480
N_LIE = (1790, 1402)
N_SIT = (1760, 1362)
N_HAND = (1645, 1470)
CREAK_X = 1720
MB0, MB1 = 2010, 2210      # minibar
MBT = 1440

# ---- times
T_GROWL = 0.12
T_TH0, T_TH1 = 0.5, 1.5
T_OUT0, T_OUT1 = 3.05, 3.55
T_PY = 5.0                 # arrives at pyramid
T_SUCK0, T_SUCK1 = 5.2, 5.5
T_SIDLE0, T_SIDLE1 = 5.6, 6.8
T_BRUSH = 6.3
T_CA, T_CB, T_CC = 6.85, 7.15, 7.45    # cans fall (caught at +0.18 / +0.22 / +0.3)
T_RELAX = 8.25
T_STEP = 8.45
T_YANK = 8.6
T_ZIP0, T_ZIP1 = 8.7, 8.92
T_NUP0, T_NUP1 = 8.68, 8.98
T_MASK_UP = 9.05
T_YAWN0, T_YAWN1 = 10.3, 10.75
T_MASK_DN = 10.8
T_NDN0, T_NDN1 = 10.9, 11.3
T_PEEK = 11.55
T_OUTC0, T_OUTC1 = 11.8, 12.15
T_TIP2_0, T_TIP2_1 = 12.15, 13.45
T_CREAK = 13.5
T_EXHALE = 14.85
T_TIP3_0, T_TIP3_1 = 15.0, 15.6
T_OPEN0, T_OPEN1 = 15.72, 15.95
T_BLOCK0, T_BLOCK1 = 16.05, 16.3
T_GRAB0, T_GRAB1 = 16.75, 17.2
T_CLOSE0, T_CLOSE1 = 17.65, 17.85
T_SIT = 18.0
T_RIB0, T_RIB1 = 18.15, 18.75
T_LID0, T_LID1 = 18.95, 19.25
T_CEL0, T_CEL1 = 19.45, 19.75
T_SHOCK = 19.85
T_NCOME0, T_NCOME1 = 20.55, 20.95
T_TAP = 21.0
T_JUMP0, T_JUMP1 = 21.05, 21.5
T_HEART = 21.7
T_RAISE0, T_RAISE1 = 22.35, 22.7
T_CRUNCH = 22.8
T_GROWL2 = 24.0
T_MASKSNAP = 24.2

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


def kf(t, keys, ease=eio):
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            p = ease(seg(t, t0, t1))
            if isinstance(v0, tuple):
                return tuple(lerp(a, b, p) for a, b in zip(v0, v1))
            return lerp(v0, v1, p)
    return keys[-1][1]


def squash(t, t0, d=0.3, a=0.22):
    k = t - t0
    if 0 <= k < d:
        s = math.sin(math.pi * k / d)
        return 1 + a * 0.6 * s, 1 - a * s
    return 1.0, 1.0


def arm(x0, y0, x1, y1, col, w=12, sag=20):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    return f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


def hand(x, y, fill, stroke, r=15):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="5"/>'


def zzz(x, y, t, ph=0.0, s=1.0, op=1.0):
    o = []
    for k in range(3):
        p = (t * 0.55 + ph + k / 3) % 1
        xx = x + 60 * p * s + 12 * math.sin(p * 9)
        yy = y - 110 * p * s
        sz = (24 + 28 * p) * s
        o.append(f'<text x="{xx:.0f}" y="{yy:.0f}" font-family="Fredoka" font-weight="700" font-size="{sz:.0f}" text-anchor="middle" '
                 f'fill="#dfe6ff" stroke="{OL}" stroke-width="6" paint-order="stroke" opacity="{op*min(1, (1-p)*2.2, p*6):.2f}">Z</text>')
    return "".join(o)


def growl_lines(x, y, t, amp=1.0):
    o = []
    for k, (dx, dy) in enumerate([(-150, 40), (150, 30), (-140, 100), (140, 95)]):
        w = 8 * math.sin(t * 50 + k)
        d = -1 if dx < 0 else 1
        o.append(f'<path d="M{x+dx:.0f} {y+dy-24:.0f} q{d*18+w:.0f} 12 0 24 q{d*18-w:.0f} 12 0 24" fill="none" stroke="#ffe08a" '
                 f'stroke-width="7" stroke-linecap="round" opacity="{amp:.2f}"/>')
    return "".join(o)


# ---------------------------------------------------------------- props
def cake_slice(x, y, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            f'<path d="M-60 30 L60 30 L60 -10 L-60 -40Z" fill="#8a4a2a" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M-60 -4 L60 16 M-60 -22 L60 3" stroke="#ffd8e8" stroke-width="7"/>'
            f'<path d="M-62 -40 L60 -10 L60 -18 Q 30 -30 -4 -40 Q -40 -52 -62 -46Z" fill="#ffd8e8" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M-40 -44 q6 14 12 0 M0 -34 q6 14 12 0 M34 -24 q6 12 12 0" fill="#ffd8e8" stroke="{OL}" stroke-width="4"/>'
            f'<circle cx="-12" cy="-58" r="14" fill="#e8243a" stroke="{OL}" stroke-width="4"/><path d="M-12 -70 q4 -14 16 -18" stroke="#3a7a2a" stroke-width="4" fill="none"/>'
            f'<ellipse cx="-17" cy="-62" rx="4" ry="3" fill="#fff" opacity="0.7"/></g>')


def no_cake(x, y, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})"><circle r="48" fill="#ffffff" stroke="#e83a2e" stroke-width="11"/>'
            + cake_slice(0, 6, 0.42) +
            f'<line x1="-32" y1="-32" x2="32" y2="32" stroke="#e83a2e" stroke-width="11" stroke-linecap="round"/>'
            f'<circle r="54" fill="none" stroke="{OL}" stroke-width="3"/></g>')


def can(x, y, rot=0.0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            f'<rect x="-25" y="-34" width="50" height="68" rx="6" fill="#c9d2dc" stroke="{OL}" stroke-width="5"/>'
            f'<rect x="-25" y="-14" width="50" height="26" fill="#e8503a"/><path d="M-25 -14 h50 M-25 12 h50" stroke="{OL}" stroke-width="3"/>'
            f'<path d="M-14 -28 v54" stroke="#ffffff" stroke-width="6" opacity="0.55" stroke-linecap="round"/>'
            f'<rect x="-25" y="-34" width="50" height="68" rx="6" fill="none" stroke="{OL}" stroke-width="5"/></g>')


def cake_box(x, y, s=1.0, ribbon=1.0, lid=0.0, rot=0.0):
    """ribbon 1 = tied bow, 0 = removed. lid 0 closed .. 1 flipped back."""
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">',
         f'<rect x="-70" y="-30" width="140" height="74" rx="6" fill="#ff9cc2" stroke="{OL}" stroke-width="6"/>',
         f'<path d="M-62 -18 v54" stroke="#ffffff" stroke-width="8" opacity="0.45" stroke-linecap="round"/>']
    if ribbon > 0.02:
        o.append(f'<g opacity="{min(1, ribbon*1.5):.2f}"><rect x="-9" y="-30" width="18" height="74" fill="#fff6c8" stroke="{OL}" stroke-width="3"/></g>')
    # lid
    la = -172 * lid
    o.append(f'<g transform="translate(-74 -30) rotate({la:.1f})">'
             f'<rect x="0" y="-20" width="148" height="24" rx="6" fill="#ffb4d2" stroke="{OL}" stroke-width="6"/>'
             + (f'<rect x="65" y="-20" width="18" height="24" fill="#fff6c8" stroke="{OL}" stroke-width="3" opacity="{min(1, ribbon*1.5):.2f}"/>' if ribbon > 0.02 else "")
             + '</g>')
    if ribbon > 0.02:
        bx = 0 + 60 * (1 - ribbon)
        by = -50 - 40 * (1 - ribbon)
        k = ribbon
        o.append(f'<g transform="translate({bx:.1f} {by:.1f}) scale({0.5 + 0.5*k:.2f})" opacity="{min(1, k*2):.2f}">'
                 f'<path d="M0 0 C -40 -34 -60 6 -6 6Z M0 0 C 40 -34 60 6 6 6Z" fill="#fff6c8" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>'
                 f'<path d="M-4 6 l-14 26 M4 6 l14 26" stroke="#fff6c8" stroke-width="9" stroke-linecap="round"/>'
                 f'<circle r="8" fill="#ffe680" stroke="{OL}" stroke-width="4"/></g>')
    o.append('</g>')
    return "".join(o)


def celery(x, y, rot=0.0, s=1.0, bite=0.0, note=True):
    """stalk base at (x,y), pointing up (-y). bite 0..1 removes the top."""
    L = 210 * (1 - 0.32 * bite)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">',
         f'<path d="M-16 0 Q -20 {-L*0.5:.0f} -12 {-L:.0f} L12 {-L:.0f} Q 20 {-L*0.5:.0f} 16 0Z" fill="#9ad35a" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>',
         f'<path d="M-4 -10 V{-L+14:.0f} M6 -10 V{-L+14:.0f}" stroke="#6faa3a" stroke-width="4"/>']
    if bite < 0.5:
        o.append(f'<g transform="translate(0 {-L:.0f})"><path d="M-10 0 Q -46 -20 -34 -54 Q -10 -40 -4 -8 Q 0 -60 14 -66 Q 26 -40 6 -6 Q 30 -40 46 -34 Q 40 -6 10 2Z" '
                 f'fill="#5aa947" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/></g>')
    else:
        o.append(f'<path d="M-12 {-L:.0f} l6 -8 l6 6 l6 -8 l6 10" fill="#c8eb8a" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>')
    if note:
        # sticky note with Nibbo smiley + heart
        o.append(f'<g transform="translate(18 {-L*0.45:.0f}) rotate(10)"><rect x="0" y="-34" width="64" height="62" fill="#fff36a" stroke="{OL}" stroke-width="4"/>'
                 f'<circle cx="26" cy="-6" r="17" fill="#ffd23c" stroke="#3d2a12" stroke-width="3"/>'
                 f'<circle cx="20" cy="-9" r="3" fill="#2a1a10"/><circle cx="32" cy="-9" r="3" fill="#2a1a10"/>'
                 f'<path d="M19 -1 q7 6 14 0" fill="none" stroke="#2a1a10" stroke-width="3" stroke-linecap="round"/>'
                 f'<path d="M50 14 c-6 -8 -14 -2 -8 6 l8 8 l8 -8 c6 -8 -2 -14 -8 -6z" fill="#ff5a7a" stroke="{OL}" stroke-width="2"/></g>')
    o.append('</g>')
    return "".join(o)


def heart(x, y, p, s=1.0):
    if p <= 0 or p >= 1:
        return ""
    sc = min(1, p * 5) * (1 + 0.2 * math.sin(min(1, p * 5) * math.pi)) * s
    op = 1 if p < 0.8 else (1 - p) / 0.2
    return (f'<g transform="translate({x:.1f} {y - 40*p:.1f}) scale({sc:.2f})" opacity="{op:.2f}">'
            f'<path d="M0 30 C -60 -10 -40 -60 0 -30 C 40 -60 60 -10 0 30Z" fill="#ff5a7a" stroke="#ffffff" stroke-width="7"/></g>')


def thought(x, y, p, t):
    if p <= 0 or p >= 1:
        return ""
    sc = eback(min(1, p * 5)) if p < 0.85 else (1 - p) / 0.15
    bob = 5 * math.sin(t * 6)
    o = [f'<g transform="translate({x:.1f} {y+bob:.1f}) scale({max(0.01, sc):.3f})">']
    o.append(f'<circle cx="-110" cy="110" r="14" fill="#ffffff" stroke="{OL}" stroke-width="5"/><circle cx="-80" cy="76" r="22" fill="#ffffff" stroke="{OL}" stroke-width="5"/>')
    puffs = [(-60, -10, 52), (-10, -40, 60), (50, -30, 56), (80, 16, 46), (20, 40, 52), (-40, 34, 46)]
    o.append("".join(f'<circle cx="{a}" cy="{b}" r="{r}" fill="#ffffff" stroke="{OL}" stroke-width="6"/>' for a, b, r in puffs))
    o.append("".join(f'<circle cx="{a}" cy="{b}" r="{r-4}" fill="#ffffff"/>' for a, b, r in puffs))
    o.append(cake_slice(10, 4, 1.05))
    o.append('</g>')
    return "".join(o)


# ---------------------------------------------------------------- room
def room(t):
    o = []
    o.append(f'<rect x="-900" y="-900" width="4200" height="{FLOOR+900}" fill="#33366e"/>')
    for x in range(-900, 3300, 120):
        o.append(f'<rect x="{x}" y="-900" width="54" height="{FLOOR+900}" fill="#373b76"/>')
    o.append(f'<rect x="-900" y="960" width="4200" height="18" fill="#2b2d5e"/>')
    # diet poster above Grumpo's bed: broccoli check, cake cross
    o.append(f'<g transform="translate(150 1150)"><rect x="-80" y="-62" width="160" height="124" rx="8" fill="#e8e4f6" stroke="{OL}" stroke-width="6"/>'
             f'<g transform="translate(-40 -18) scale(0.5)"><circle cx="-16" cy="-24" r="22" fill="#4fae4a" stroke="{OL}" stroke-width="5"/><circle cx="16" cy="-26" r="24" fill="#4fae4a" stroke="{OL}" stroke-width="5"/>'
             f'<circle cx="0" cy="-44" r="22" fill="#5cc157" stroke="{OL}" stroke-width="5"/><path d="M-8 -10 L-10 30 H10 L8 -10Z" fill="#a8d878" stroke="{OL}" stroke-width="5"/></g>'
             f'<path d="M14 -24 l12 12 l24 -26" fill="none" stroke="#3aaa4a" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
             + cake_slice(-40, 36, 0.3) +
             f'<path d="M18 24 l26 26 M44 24 l-26 26" stroke="#e83a2e" stroke-width="9" stroke-linecap="round"/></g>')
    # window (night city + moon)
    wx, wy, ww, wh = WIN
    o.append(f'<defs><linearGradient id="nsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0c1238"/><stop offset="1" stop-color="#2c3678"/></linearGradient>'
             f'<clipPath id="wclip"><rect x="{wx}" y="{wy}" width="{ww}" height="{wh}"/></clipPath>'
             f'<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfe0ff" stop-opacity="0.16"/><stop offset="1" stop-color="#cfe0ff" stop-opacity="0.05"/></linearGradient>'
             f'<radialGradient id="fglow"><stop offset="0" stop-color="#fff2b0" stop-opacity="0.85"/><stop offset="0.5" stop-color="#ffd860" stop-opacity="0.35"/><stop offset="1" stop-color="#ffd860" stop-opacity="0"/></radialGradient>'
             f'<linearGradient id="fbeam" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#fff0a0" stop-opacity="0.6"/><stop offset="1" stop-color="#fff0a0" stop-opacity="0"/></linearGradient>'
             f'<radialGradient id="vig" cx="0.5" cy="0.55" r="0.75"><stop offset="0.55" stop-color="#070418" stop-opacity="0"/><stop offset="1" stop-color="#070418" stop-opacity="0.55"/></radialGradient>'
             f'</defs>')
    o.append(f'<rect x="{wx-14}" y="{wy-14}" width="{ww+28}" height="{wh+28}" rx="8" fill="#5a5c96" stroke="{OL}" stroke-width="7"/>')
    city = []
    for k, (bx, bh) in enumerate([(0, 90), (34, 140), (80, 70), (110, 170), (156, 110), (182, 60)]):
        city.append(f'<rect x="{wx+bx}" y="{wy+wh-bh}" width="{34 if k != 3 else 46}" height="{bh}" fill="#1a1f4a"/>')
        for yy in range(wy + wh - bh + 14, wy + wh - 8, 26):
            if (yy + k * 7) % 3:
                city.append(f'<rect x="{wx+bx+8}" y="{yy}" width="8" height="10" fill="#ffd86a" opacity="0.85"/>')
    stars = "".join(f'<circle cx="{wx+sx}" cy="{wy+sy}" r="{r}" fill="#ffffff" opacity="{0.5+0.5*math.sin(t*3+sx):.2f}"/>'
                    for sx, sy, r in [(20, 30, 3), (70, 60, 2.5), (150, 24, 3), (180, 80, 2), (100, 100, 2)])
    o.append(f'<g clip-path="url(#wclip)"><rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" fill="url(#nsky)"/>{stars}'
             f'<circle cx="{wx+140}" cy="{wy+70}" r="34" fill="#fff6d0"/><circle cx="{wx+156}" cy="{wy+60}" r="30" fill="#2a3270"/>'
             + "".join(city) + '</g>')
    o.append(f'<path d="M{wx+ww/2} {wy} V{wy+wh} M{wx} {wy+wh/2} H{wx+ww}" stroke="#5a5c96" stroke-width="10"/>'
             f'<rect x="{wx-14}" y="{wy-14}" width="{ww+28}" height="{wh+28}" rx="8" fill="none" stroke="{OL}" stroke-width="7"/>')
    # curtain rod
    o.append(f'<rect x="{CURT[0]-40}" y="1004" width="{wx+ww+150-CURT[0]}" height="14" rx="7" fill="#b5642a" stroke="{OL}" stroke-width="4"/>')
    # moonlight on floor
    o.append(f'<path d="M{wx} {wy+wh} L{wx+ww} {wy+wh} L{wx+ww+220} {FLOOR+120} L{wx+60} {FLOOR+120}Z" fill="url(#beam)"/>')
    # floor (wood planks)
    o.append(f'<rect x="-900" y="{FLOOR}" width="4200" height="1000" fill="#5e4234"/>')
    for k, y in enumerate(range(FLOOR + 46, FLOOR + 1000, 56)):
        o.append(f'<path d="M-900 {y} H3300" stroke="#4e3529" stroke-width="5"/>')
        for x in range(-900 + (k % 2) * 110, 3300, 220):
            o.append(f'<path d="M{x} {y-56} V{y}" stroke="#4e3529" stroke-width="4"/>')
    o.append(f'<path d="M-900 {FLOOR} H3300" stroke="{OL}" stroke-width="6"/>'
             f'<rect x="-900" y="{FLOOR-22}" width="4200" height="22" fill="#7d79b0" stroke="{OL}" stroke-width="4"/>')
    return "".join(o)


def creak_board(t):
    dip = 0.0
    if T_CREAK <= t < T_EXHALE + 0.3:
        dip = 1.0 if t < T_EXHALE else 1 - seg(t, T_EXHALE, T_EXHALE + 0.3)
    o = [f'<g transform="rotate({3*dip:.2f} {CREAK_X-70} {FLOOR})">'
         f'<rect x="{CREAK_X-70}" y="{FLOOR+2}" width="150" height="42" fill="#6d4c3b" stroke="#3e2a20" stroke-width="4"/>'
         f'<circle cx="{CREAK_X-50}" cy="{FLOOR+22}" r="4" fill="#3e2a20"/><circle cx="{CREAK_X+60}" cy="{FLOOR+22}" r="4" fill="#3e2a20"/></g>']
    if T_CREAK <= t < T_CREAK + 0.7:
        q = seg(t, T_CREAK, T_CREAK + 0.7)
        for k, dx in enumerate((-90, 100)):
            o.append(f'<path d="M{CREAK_X+dx} {FLOOR+10} l{-14 if dx<0 else 14} -10 l{-6 if dx<0 else 6} 14 l{-14 if dx<0 else 14} -10" fill="none" '
                     f'stroke="#ffe08a" stroke-width="6" stroke-linecap="round" opacity="{1-q:.2f}"/>')
    return "".join(o)


def scale_prop():
    return (f'<g transform="translate(640 {FLOOR-14})"><rect x="-62" y="-14" width="124" height="28" rx="10" fill="#cfd6e4" stroke="{OL}" stroke-width="5"/>'
            f'<rect x="-28" y="-10" width="56" height="16" rx="4" fill="#3a4a6a"/><path d="M-14 -2 h28" stroke="#7affb0" stroke-width="4"/></g>')


def bed_grumpo(t):
    o = [f'<rect x="40" y="1180" width="74" height="{FLOOR-1180}" rx="18" fill="#8a5a3a" stroke="{OL}" stroke-width="7"/>',
         f'<path d="M58 1220 V1660" stroke="#a8724a" stroke-width="9" stroke-linecap="round"/>',
         f'<rect x="100" y="{MAT}" width="480" height="100" rx="14" fill="#d6d6ee" stroke="{OL}" stroke-width="6"/>',
         f'<rect x="100" y="{MAT+100}" width="480" height="40" fill="#8a5a3a" stroke="{OL}" stroke-width="6"/>',
         f'<rect x="540" y="{MAT+140}" width="26" height="{FLOOR-MAT-140}" fill="#6e4429" stroke="{OL}" stroke-width="5"/>',
         f'<path d="M116 1430 Q 112 1396 150 1394 H252 Q 282 1398 280 1430 L278 {MAT+6} H118Z" fill="#eeeef8" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>']
    return "".join(o)


def blanket_grumpo(t):
    out = seg(t, T_OUT0, T_OUT1)
    top = lerp(1470, 1484, out)
    hump = 26 * (1 - out)
    return (f'<path d="M190 {top+10:.0f} Q 240 {top-hump:.0f} 300 {top-hump:.0f} Q 380 {top-hump:.0f} 420 {top:.0f} Q 500 {top+6:.0f} 586 {top:.0f} '
            f'L592 {MAT+118} H200 Q 180 {MAT+80} 190 {top+10:.0f}Z" fill="#3aa8a0" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<path d="M196 {top+8:.0f} Q 300 {top-hump-6:.0f} 420 {top-4:.0f} T 586 {top-4:.0f}" fill="none" stroke="#ffffff" stroke-width="10" opacity="0.8"/>'
            + "".join(f'<circle cx="{x}" cy="{MAT+70}" r="8" fill="#ffd23a" opacity="0.7"/>' for x in range(260, 580, 70)))


def bed_nibbo_back():
    o = [f'<rect x="{NBED1-10}" y="1180" width="74" height="{FLOOR-1180}" rx="18" fill="#8a5a3a" stroke="{OL}" stroke-width="7"/>',
         f'<path d="M{NBED1+44} 1220 V1660" stroke="#a8724a" stroke-width="9" stroke-linecap="round"/>',
         f'<rect x="{NBED0}" y="{MAT}" width="{NBED1-NBED0}" height="100" rx="14" fill="#d6d6ee" stroke="{OL}" stroke-width="6"/>',
         f'<rect x="{NBED0}" y="{MAT+100}" width="{NBED1-NBED0}" height="40" fill="#8a5a3a" stroke="{OL}" stroke-width="6"/>',
         f'<rect x="{NBED0+14}" y="{MAT+140}" width="26" height="{FLOOR-MAT-140}" fill="#6e4429" stroke="{OL}" stroke-width="5"/>',
         f'<path d="M{NBED1-16} 1430 Q {NBED1-12} 1396 {NBED1-50} 1394 H{NBED1-160} Q {NBED1-190} 1398 {NBED1-188} 1430 L{NBED1-186} {MAT+6} H{NBED1-18}Z" fill="#eeeef8" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>']
    return "".join(o)


def blanket_nibbo(t, empty=0.0):
    top = 1455 + 30 * empty
    end = lerp(1760, 1600, empty)
    return (f'<path d="M{NBED0-6} {top+20:.0f} Q {NBED0} {top:.0f} {NBED0+30} {top:.0f} H{end-20:.0f} Q {end+10:.0f} {top:.0f} {end+14:.0f} {top+30:.0f} '
            f'L{end+20:.0f} {MAT+118} H{NBED0-6}Z" fill="#e66a9a" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<path d="M{NBED0+20} {top+6:.0f} H{end-10:.0f}" stroke="#ffffff" stroke-width="10" opacity="0.8"/>'
            + "".join(f'<path d="M{x} {MAT+62} c-5 -7 -12 -2 -7 5 l7 7 l7 -7 c5 -7 -2 -12 -7 -5z" fill="#ffd0e0" opacity="0.8"/>' for x in range(NBED0 + 60, int(end), 70)))


def curtain(x0, x1, bulge, t, trem=0.0, right=False):
    """floor-length curtain panel from rod; bulge widens it around a hidden Grumpo."""
    top, bot = 1012, FLOOR - 4
    pts_l, pts_r = [], []
    for k in range(0, 21):
        y = lerp(top, bot, k / 20)
        sh = eio(cl((y - 1320) / 170))
        wob = trem * 4 * math.sin(t * 40 + y / 30)
        pts_l.append((x0 - bulge * 115 * sh + wob, y))
        pts_r.append((x1 + bulge * 100 * sh + wob, y))
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts_l) + " L" + " L".join(f"{x:.1f} {y:.1f}" for x, y in reversed(pts_r)) + "Z"
    col = "#2f8a8a"
    o = [f'<path d="{d}" fill="{col}" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>']
    n = 3
    for i in range(1, n + 1):
        f = i / (n + 1)
        xs = lerp(x0, x1, f)
        xb = lerp(pts_l[-1][0], pts_r[-1][0], f)
        o.append(f'<path d="M{xs:.1f} {top+10} Q {xs:.1f} 1300 {lerp(xs, xb, 0.5):.1f} 1420 T {xb:.1f} {bot-6}" fill="none" stroke="#226a6a" stroke-width="7" stroke-linecap="round"/>')
    o.append(f'<path d="M{x0+8} {top+12} V{bot-40}" stroke="#4fb0ae" stroke-width="6" opacity="0.6" stroke-linecap="round"/>')
    return "".join(o)


def minibar(t, open_=0.0, item=True):
    o = [shadow((MB0 + MB1) / 2, FLOOR + 4, 130),
         f'<rect x="{MB0}" y="{MBT}" width="{MB1-MB0}" height="{FLOOR-MBT}" rx="8" fill="#4a3226" stroke="{OL}" stroke-width="7"/>',
         f'<rect x="{MB0}" y="{MBT-22}" width="{MB1-MB0}" height="26" rx="6" fill="#6e4a36" stroke="{OL}" stroke-width="6"/>']
    # little ice bucket + glasses on top
    o.append(f'<path d="M{MB0+30} {MBT-22} l6 -44 h34 l6 44z" fill="#cfd6e4" stroke="{OL}" stroke-width="5"/>'
             f'<path d="M{MB0+120} {MBT-22} l-4 -40 h28 l-4 40z" fill="#a8c8ff" fill-opacity="0.5" stroke="{OL}" stroke-width="4"/>')
    ix0, ix1, iy0, iy1 = MB0 + 12, MB1 - 12, MBT + 12, FLOOR - 12
    if open_ > 0:
        o.append(f'<rect x="{ix0}" y="{iy0}" width="{ix1-ix0}" height="{iy1-iy0}" fill="#fff3c0" stroke="{OL}" stroke-width="5"/>'
                 f'<rect x="{ix0}" y="{iy0}" width="{ix1-ix0}" height="30" fill="#ffffff" opacity="0.7"/>')
        for sy in (1530, 1610):
            o.append(f'<rect x="{ix0}" y="{sy}" width="{ix1-ix0}" height="8" fill="#cfd6e4" stroke="{OL}" stroke-width="3"/>')
        # bottles + water + juice on shelves
        for k, (bx, c) in enumerate([(ix0 + 24, "#5ab0ff"), (ix0 + 58, "#5ab0ff"), (ix1 - 40, "#ff9a3a")]):
            o.append(f'<rect x="{bx-11}" y="1478" width="22" height="52" rx="6" fill="{c}" stroke="{OL}" stroke-width="4"/><rect x="{bx-5}" y="1468" width="10" height="12" fill="#ffffff" stroke="{OL}" stroke-width="3"/>')
        for bx in (ix0 + 30, ix1 - 34):
            o.append(f'<rect x="{bx-14}" y="1628" width="28" height="44" rx="4" fill="#7be08a" stroke="{OL}" stroke-width="4"/>')
        if item:
            o.append(cake_box((ix0 + ix1) / 2 + 20, 1566, 0.62))
        # door swung open to the right (hinge on the right edge)
        dw = lerp(MB1 - MB0 - 24, 60, eio(open_))
        o.append(f'<path d="M{MB1-12} {iy0} L{MB1-12+dw*0.0 + 70*open_:.1f} {iy0-18*open_:.1f} L{MB1-12+70*open_:.1f} {iy1+18*open_:.1f} L{MB1-12} {iy1}Z" '
                 f'fill="#6a4532" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
                 f'<path d="M{MB1-6+40*open_:.1f} {1500} v{90}" stroke="#d8dce6" stroke-width="8" stroke-linecap="round"/>')
        if open_ < 1:
            o.append(f'<rect x="{ix0}" y="{iy0}" width="{dw:.1f}" height="{iy1-iy0}" fill="#6a4532" stroke="{OL}" stroke-width="5" transform="translate({(ix1-ix0-dw):.1f} 0)" opacity="{1-open_:.2f}"/>')
    else:
        o.append(f'<rect x="{ix0}" y="{iy0}" width="{ix1-ix0}" height="{iy1-iy0}" rx="4" fill="#6a4532" stroke="{OL}" stroke-width="5"/>'
                 f'<path d="M{ix0+20} {1520} v80" stroke="#d8dce6" stroke-width="9" stroke-linecap="round"/>'
                 f'<path d="M{ix0+20} {1520} v80" stroke="{OL}" stroke-width="2" opacity="0.4"/>')
        o.append(no_cake((ix0 + ix1) / 2 + 12, 1560, 0.95))
    return "".join(o)


def pyramid(t, fallen):
    """fallen: set of can ids removed from the pyramid ('A' middle-right, 'B' top, 'C' middle-left)."""
    wob = 0.0
    if T_BRUSH <= t < T_CC + 0.4:
        k = t - T_BRUSH
        wob = 5 * math.exp(-k * 1.2) * math.sin(k * 26)
    o = []
    for dx in (-54, 0, 54):
        o.append(can(PYR_X + dx, FLOOR - 34, wob * 0.2))
    pos = {"C": (PYR_X - 27, FLOOR - 102), "A": (PYR_X + 27, FLOOR - 102), "B": (PYR_X, FLOOR - 170)}
    for key in ("C", "A", "B"):
        if key not in fallen:
            x, y = pos[key]
            sw = wob * (1.6 if key == "B" else 1.0)
            o.append(can(x + sw, y, sw * 1.4))
    return "".join(o), pos


# ---------------------------------------------------------------- characters
def grumpo_extra(x, y, s, rot, sx, sy, kind, t, red=0.0):
    ink = mix_hex(INK, "#3a0505", red)
    base = mix_hex("#9466e0", "#ff6a52", red)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s*sx:.3f} {s*sy:.3f})">']
    worried = f'<path d="M-72 -28 Q -46 -36 -16 -54 M16 -54 Q 46 -36 72 -28" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
    if kind == "hungry":
        o.append(f'<path d="M-72 -42 Q -46 -62 -16 -48 M16 -48 Q 46 -62 72 -42" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<path d="M-38 60 Q 0 112 38 60Z" fill="#4a0a14" stroke="{ink}" stroke-width="8" stroke-linejoin="round"/>'
                 f'<ellipse cx="0" cy="84" rx="16" ry="8" fill="#ff7a90"/>')
        dp = (t * 1.3) % 1
        o.append(f'<path d="M26 {80+dp*40:.0f} q8 14 0 22 q-8 -8 0 -22z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3" opacity="{1-dp:.2f}"/>')
    elif kind == "tense":
        o.append(worried + f'<circle cx="-62" cy="70" r="26" fill="{mix_hex(base, "#ff4a4a", 0.3)}" opacity="0.9"/><circle cx="62" cy="70" r="26" fill="{mix_hex(base, "#ff4a4a", 0.3)}" opacity="0.9"/>'
                 f'<path d="M-20 74 h40" stroke="{ink}" stroke-width="9" stroke-linecap="round"/>')
    elif kind == "worried":
        o.append(worried + f'<path d="M-26 76 q8 -8 16 0 t16 0 t16 0" fill="none" stroke="{ink}" stroke-width="8" stroke-linecap="round"/>'
                 '<path d="M96 -40 q12 18 0 28 q-12 -10 0 -28z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3"/>')
    elif kind == "joy":
        o.append(f'<path d="M-72 -44 Q -46 -66 -16 -50 M16 -50 Q 46 -66 72 -44" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<path d="M-44 56 Q 0 118 44 56Z" fill="#4a0a14" stroke="{ink}" stroke-width="8" stroke-linejoin="round"/>'
                 f'<path d="M-36 60 h72" stroke="#ffffff" stroke-width="10"/>')
    elif kind == "sadsmile":
        o.append(worried + f'<path d="M-42 64 q10 16 21 4 q10 12 21 0 q10 12 21 0 q10 12 21 -6" fill="none" stroke="{ink}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>')
    elif kind == "chew":
        ch = abs(math.sin(t * 14))
        o.append(worried + f'<path d="M-40 {66+4*ch:.1f} q10 {10+8*ch:.1f} 20 2 q10 {10+8*ch:.1f} 20 0 q10 {10+8*ch:.1f} 20 0 q10 {10+8*ch:.1f} 20 -4" fill="none" stroke="{ink}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>'
                 f'<circle cx="-70" cy="{60+6*ch:.1f}" r="16" fill="{base}" stroke="{ink}" stroke-width="3" opacity="0.8"/>')
    o.append('</g>')
    return "".join(o)


def tear(x, y, s, p):
    if p <= 0:
        return ""
    yy = y + 20 * s + 70 * s * min(1, p)
    return (f'<path d="M{x-38*s:.1f} {y+30*s:.1f} Q {x-40*s:.1f} {yy-10*s:.1f} {x-36*s:.1f} {yy:.1f}" stroke="#bfefff" stroke-width="{9*s:.1f}" fill="none" stroke-linecap="round" opacity="0.9"/>'
            f'<path d="M{x-36*s:.1f} {yy:.1f} q{9*s:.1f} {14*s:.1f} 0 {22*s:.1f} q{-9*s:.1f} {-8*s:.1f} 0 {-22*s:.1f}z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3"/>')


def nib_extra(x, y, r, rot, sx, sy, mouth=None, squint=0.0, mask=None, frown=False):
    """drawn on top of a Nibbo; mask = 0 (over eyes) .. 1 (up on forehead) or None."""
    f = r / 48 * 1.05
    d = "#2a1a10"
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx*f:.3f} {sy*f:.3f})">']
    if squint > 0:
        o.append(f'<rect x="-22" y="-16" width="16" height="{12*squint:.1f}" fill="#ffd23c"/><rect x="6" y="-16" width="16" height="{12*squint:.1f}" fill="#ffd23c"/>'
                 f'<path d="M-22 {-16+12*squint:.1f} h16 M6 {-16+12*squint:.1f} h16" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>')
    if mouth == "sleep":
        o.append(f'<ellipse cx="0" cy="14" rx="3.5" ry="4.5" fill="#7a2a1a" stroke="{d}" stroke-width="2.5"/>')
    elif mouth == "smack":
        o.append(f'<path d="M-8 14 q4 -4 8 0 t8 0" fill="none" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>')
    elif mouth == "frown":
        o.append(f'<path d="M-8 17 q8 -7 16 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    elif mouth == "flat":
        o.append(f'<path d="M-7 14 h14" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    elif mouth == "yawn":
        o.append(f'<ellipse cx="0" cy="15" rx="9" ry="12" fill="#7a2a1a" stroke="{d}" stroke-width="3.5"/>')
    if frown and mask is not None and mask < 0.5:
        o.append(f'<path d="M-24 -22 l12 4 M24 -22 l-12 4" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>')
    if mask is not None:
        my = -24 * mask
        o.append(f'<g transform="translate(0 {my:.1f})">'
                 f'<path d="M-44 -6 Q -40 -10 -30 -10 M44 -6 Q 40 -10 30 -10" stroke="#3a2a5a" stroke-width="3" fill="none"/>'
                 f'<path d="M-31 -14 Q -16 -22 0 -14 Q 16 -22 31 -14 Q 36 0 24 6 Q 12 10 0 2 Q -12 10 -24 6 Q -36 0 -31 -14Z" fill="#ff8fc0" stroke="{d}" stroke-width="3" stroke-linejoin="round"/>'
                 f'<path d="M-21 -4 q7 5 14 0 M7 -4 q7 5 14 0" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round"/>'
                 f'<path d="M-22 -6 l-3 -4 M-15 -3 l-1 -4 M22 -6 l3 -4 M15 -3 l1 -4" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/></g>')
    o.append('</g>')
    return "".join(o)


def hops(t, t0, t1, x0, x1, n, h=22):
    p = seg(t, t0, t1)
    k = p * n
    i = min(n - 1, int(k))
    f = k - i
    x = lerp(x0, x1, (i + eio(f)) / n)
    y = -h * math.sin(math.pi * f)
    land = f < 0.18 or f > 0.95
    return x, y, land, f


def grumpo_state(t):
    g = dict(x=290.0, y=1384.0, ex="grumpy", kind=None, sx=1.0, sy=1.0, rot=0.0, look=(0, 0), red=0.0,
             hidden=False, hands=[], tear=0.0, sit=False)
    # ---- in bed
    if t < T_OUT0:
        g["ex"] = "blank"
        g["kind"] = "worried" if t < T_TH0 else "hungry"
        g["look"] = (0.2, -0.6) if t < T_TH0 else (0.8, -0.8)
        if T_TH1 + 0.1 <= t:
            g["look"] = (1, 0)
            g["ex"], g["kind"] = "suspicious", None
        a, b = squash(t, T_GROWL, 0.5, 0.1)
        g["sx"], g["sy"] = a, b
        g["rot"] = 3 * math.sin(t * 40) * (1 - seg(t, T_GROWL, T_GROWL + 0.6)) if t > T_GROWL else 0
        return g
    if t < T_OUT1:
        p = seg(t, T_OUT0, T_OUT1)
        g["x"] = lerp(290, 660, eio(p))
        g["y"] = lerp(1384, GY, eio(p)) - 110 * math.sin(math.pi * p)
        g["rot"] = 25 * math.sin(math.pi * p)
        g["ex"] = "suspicious"
        g["look"] = (1, 0)
        return g
    g["y"] = GY
    g["ex"] = "suspicious"
    g["look"] = (1, 0)
    sneak_hands = True
    if t < T_PY:
        x, dy, land, f = hops(t, T_OUT1 + 0.1, T_PY, 660, 880, 4, 26)
        g["x"], g["y"] = x, GY + dy
        if land:
            g["sx"], g["sy"] = 1.06, 0.94
        g["rot"] = 6 * math.sin(math.pi * f)
    elif t < T_SIDLE0:
        g["x"] = 880
        g["ex"] = "blank"
        g["kind"] = "worried" if t < T_SUCK0 else "tense"
        g["look"] = (1, 0.4)
        k = eio(seg(t, T_SUCK0, T_SUCK1))
        g["sx"], g["sy"] = 1 - 0.24 * k, 1 + 0.1 * k
    elif t < T_RELAX:
        g["ex"] = "blank"
        g["kind"] = "tense"
        g["sx"], g["sy"] = 0.76, 1.1
        if t < T_SIDLE1:
            x, dy, land, f = hops(t, T_SIDLE0, T_SIDLE1, 880, 1100, 6, 8)
            g["x"], g["y"] = x, GY + dy * 0.5 - 10 * 0
            g["look"] = (-1, 0.3)
        else:
            g["x"] = 1100
            # catching
            g["kind"] = "worried"
            g["sx"], g["sy"] = lerp(0.76, 1.0, seg(t, T_SIDLE1, T_SIDLE1 + 0.2)), lerp(1.1, 1.0, seg(t, T_SIDLE1, T_SIDLE1 + 0.2))
            dart = math.sin(t * 9)
            g["look"] = (-1, 0) if t < T_CB + 0.2 else ((-0.6, -0.9) if t < T_CC + 0.4 else (dart, -0.2))
            a, b = squash(t, T_CC + 0.3, 0.3, 0.12)
            g["sx"] *= a
            g["sy"] *= b
        sneak_hands = False
    elif t < T_ZIP0:
        g["x"] = 1100 + 30 * eio(seg(t, T_STEP, T_YANK))
        g["ex"] = "smug" if t < T_YANK else "shock"
        g["kind"] = None
        g["look"] = (1, 0) if t >= T_YANK else (0, 0)
        sneak_hands = False
    elif t < T_OUTC0:
        p = seg(t, T_ZIP0, T_ZIP1)
        g["x"] = lerp(1130, 1195, eout(p))
        g["ex"] = "shock"
        g["hidden"] = True
        g["look"] = (1, 0)
        sneak_hands = False
    elif t < T_TIP2_0:
        p = eio(seg(t, T_OUTC0, T_OUTC1))
        g["x"] = lerp(1195, 1280, p)
        g["hidden"] = p < 0.6
        g["ex"] = "blank"
        g["kind"] = "worried"
        g["look"] = (1, -0.2)
    elif t < T_CREAK:
        x, dy, land, f = hops(t, T_TIP2_0, T_CREAK, 1280, CREAK_X, 5, 24)
        g["x"], g["y"] = x, GY + dy
        if land:
            g["sx"], g["sy"] = 1.06, 0.94
        g["rot"] = 6 * math.sin(math.pi * f)
        g["look"] = (1, -0.3)
    elif t < T_TIP3_0:
        g["x"] = CREAK_X
        g["ex"] = "blank"
        g["kind"] = "tense" if t < T_EXHALE else "worried"
        g["red"] = 0.55 * seg(t, T_CREAK + 0.3, T_EXHALE) * (1 - seg(t, T_EXHALE, T_EXHALE + 0.15))
        a, b = squash(t, T_CREAK, 0.25, 0.12)
        infl = 0.06 * seg(t, T_CREAK + 0.3, T_EXHALE) * (1 - seg(t, T_EXHALE, T_EXHALE + 0.15))
        g["sx"], g["sy"] = a * (1 + infl), b * (1 + infl)
        g["look"] = (0.7, -0.9)
        g["rot"] = -4
        if t >= T_EXHALE:
            g["sx"] *= 1 - 0.08 * math.sin(math.pi * seg(t, T_EXHALE, T_EXHALE + 0.3))
    elif t < T_BLOCK0:
        if t < T_TIP3_1:
            x, dy, land, f = hops(t, T_TIP3_0, T_TIP3_1, CREAK_X, 1935, 2, 24)
            g["x"], g["y"] = x, GY + dy
            g["rot"] = 6 * math.sin(math.pi * f)
        else:
            g["x"] = 1935
        g["look"] = (1, 0.2)
        g["ex"] = "smug" if t < T_OPEN0 + 0.15 else "shock"
        if t >= T_OPEN0 + 0.15:
            g["look"] = (-1, -0.4)
    elif t < T_SIT:
        g["x"] = lerp(1935, 2110, eio(seg(t, T_BLOCK0, T_BLOCK1)))
        g["ex"] = "shock" if t < T_BLOCK1 + 0.3 else "blank"
        g["kind"] = None if t < T_BLOCK1 + 0.3 else ("worried" if t < T_GRAB1 else "joy")
        g["look"] = (-1, -0.4) if t < T_GRAB0 else (0, -0.8)
        a, b = squash(t, T_BLOCK1, 0.25, 0.12)
        g["sx"], g["sy"] = a, b
        sneak_hands = False
        if T_CLOSE0 - 0.1 <= t < T_CLOSE1 + 0.1:
            g["rot"] = 10 * math.sin(math.pi * seg(t, T_CLOSE0 - 0.1, T_CLOSE1 + 0.1))
    else:
        g["x"] = 2110
        g["sit"] = True
        g["y"] = GY + 14
        g["sy"], g["sx"] = 0.94, 1.04
        sneak_hands = False
        g["ex"], g["kind"] = "blank", "hungry"
        g["look"] = (0, 0.9)
        if T_RIB0 + 0.1 <= t < T_RIB1:
            g["look"] = (-1, -0.6) if (t - T_RIB0) % 0.6 < 0.3 else (0, 0.9)
        if t >= T_LID0:
            g["kind"] = "joy"
        if t >= T_SHOCK:
            g["ex"], g["kind"] = "shock", None
            g["look"] = (0, 0.2)
            dro = seg(t, T_SHOCK + 0.3, T_SHOCK + 1.0)
            g["sy"] = 0.94 - 0.07 * eio(dro)
            g["sx"] = 1.04 + 0.05 * eio(dro)
            if t >= T_SHOCK + 0.4:
                g["ex"], g["kind"] = "blank", "worried"
                g["look"] = (0, 0.6)
        if T_JUMP0 <= t < T_JUMP1:
            p = seg(t, T_JUMP0, T_JUMP1)
            g["y"] = GY + 14 - 150 * math.sin(math.pi * p)
            g["ex"], g["kind"] = "shock", None
            g["look"] = (-1, 0)
            g["sy"], g["sx"] = 1.12, 0.92
        elif t >= T_JUMP1:
            a, b = squash(t, T_JUMP1, 0.3, 0.18)
            g["sx"], g["sy"] = 1.04 * a, 0.92 * b
            g["ex"] = "blank"
            g["kind"] = "worried" if t < T_RAISE0 else ("sadsmile" if t < T_CRUNCH else "chew")
            g["look"] = (-1, -0.2) if t < T_RAISE0 else (0, 0.5)
            g["tear"] = seg(t, T_CRUNCH + 0.2, T_CRUNCH + 1.2)
            if t >= T_GROWL2:
                g["rot"] = 4 * math.sin(t * 50) * (1 - seg(t, T_GROWL2, T_GROWL2 + 0.8))
                g["look"] = (0, 0.9)
    g["sneak"] = sneak_hands
    return g


def nibbo_state(t):
    n = dict(x=N_LIE[0], y=N_LIE[1], rot=-10.0, sx=1.0, sy=1.0, ex="none", mouth="sleep", squint=0.0, mask=0.0,
             frown=False, zz=True, inbed=True, light=0.0, hand=N_HAND)
    br = 0.03 * math.sin(t * 2.4)
    n["sx"], n["sy"] = 1 + br, 1 - br * 0.6
    if T_YANK <= t < T_NDN1:
        n["zz"] = False
        up = eout(seg(t, T_NUP0, T_NUP1)) * (1 - eio(seg(t, T_NDN0, T_NDN1)))
        n["x"], n["y"] = lerp(N_LIE[0], N_SIT[0], up), lerp(N_LIE[1], N_SIT[1], up)
        n["rot"] = lerp(-10, 0, up)
        a, b = squash(t, T_NUP1, 0.25, 0.14)
        n["sx"], n["sy"] = a, b
        n["mask"] = eio(seg(t, T_MASK_UP, T_MASK_UP + 0.18)) * (1 - eio(seg(t, T_MASK_DN, T_MASK_DN + 0.15)))
        n["mouth"] = "flat"
        if n["mask"] > 0.6:
            n["ex"] = "wow" if t < T_MASK_UP + 0.45 else "happy"
            if T_MASK_UP + 0.45 <= t < T_YAWN0:
                n["squint"] = 0.55
                n["mouth"] = "flat"
            if T_YAWN0 <= t < T_YAWN1:
                n["ex"], n["mouth"], n["squint"] = "none", "yawn", 0
                n["sy"] *= 1 + 0.08 * math.sin(math.pi * seg(t, T_YAWN0, T_YAWN1))
            if t >= T_YAWN1:
                n["squint"] = 0.75
        else:
            n["ex"] = "none"
        if t < T_NUP0 + 0.05:
            n["mouth"] = "sleep"
        n["hand"] = (lerp(N_HAND[0], 1600, up), lerp(N_HAND[1], 1452, up))
        if T_YANK <= t < T_YANK + 0.25:
            n["hand"] = (n["hand"][0] - 40 * math.sin(math.pi * seg(t, T_YANK, T_YANK + 0.25)), n["hand"][1] + 6)
    if t >= T_NDN1 + 0.2:
        n["zz"] = True
    if T_CREAK <= t < T_EXHALE - 0.2:
        n["zz"] = False
        n["mouth"] = "smack" if (t - T_CREAK) % 0.3 < 0.15 and t < T_CREAK + 0.9 else "sleep"
        rp = eio(seg(t, T_CREAK + 0.9, T_CREAK + 1.25))
        n["rot"] = lerp(-10, 8, rp)
        n["x"] = N_LIE[0] - 10 * rp
    if t >= T_EXHALE - 0.2:
        n["rot"], n["x"] = 8, N_LIE[0] - 10
    # fridge light hits Nibbo
    lit = seg(t, T_OPEN0 + 0.1, T_OPEN1 + 0.05) * (1 - seg(t, T_BLOCK0 + 0.05, T_BLOCK1))
    n["light"] = lit
    if T_OPEN1 <= t < T_BLOCK1 + 0.5:
        n["zz"] = False
        n["frown"] = True
        n["mouth"] = "frown"
        n["rot"] = 8 + 10 * math.sin(math.pi * seg(t, T_OPEN1, T_BLOCK1 + 0.5))
    # leaves bed (off camera) and creeps behind Grumpo
    if t >= 19.95:
        n["inbed"] = False
        n["zz"] = False
        n["mask"] = 1.0
        n["rot"] = 0
        n["ex"], n["mouth"] = "happy", None
        k = eout(seg(t, T_NCOME0, T_NCOME1))
        n["x"], n["y"] = lerp(1660, 1872, k), FLOOR - NR - 22 * abs(math.sin(math.pi * k * 2)) * (1 - k)
        n["sx"], n["sy"] = 1.0, 1.0
        if t >= T_TAP:
            n["ex"] = "joy"
            a, b = squash(t, T_TAP + 0.05, 0.25, 0.14)
            n["sx"], n["sy"] = a, b
        if T_HEART - 0.1 <= t < T_RAISE0:
            n["rot"] = 8 * math.sin((t - T_HEART) * 14)
            n["ex"] = "happy"
        if t >= T_RAISE0:
            n["ex"] = "joy"
            n["rot"] = 0
        if T_CRUNCH + 0.1 <= t < T_CRUNCH + 1.0:
            hop = abs(math.sin((t - T_CRUNCH) * 11))
            n["y"] -= 18 * hop
        if t >= T_MASKSNAP:
            n["mask"] = 1 - eout(seg(t, T_MASKSNAP, T_MASKSNAP + 0.08))
            n["ex"] = "none" if n["mask"] < 0.5 else "wow"
            n["mouth"] = "yawn" if n["mask"] < 0.5 else None
            a, b = squash(t, T_MASKSNAP, 0.3, 0.2)
            n["sx"], n["sy"] = a, b
            n["rot"] = 6 * math.sin((t - T_MASKSNAP) * 30) * math.exp(-(t - T_MASKSNAP) * 3)
        n["y"] += NR * (1 - n["sy"])
    return n


# ---------------------------------------------------------------- camera
CK = [(0.0, (300, 1350, 1.72)), (1.45, (300, 1350, 1.72)), (2.1, (1930, 1420, 1.5)), (2.75, (1930, 1420, 1.5)),
      (3.3, (520, 1430, 1.5)), (3.7, (620, 1440, 1.5)), (T_PY, (880, 1450, 1.55)), (T_SUCK1, (960, 1470, 1.72)),
      (T_CC + 0.4, (1030, 1470, 1.72)), (T_RELAX, (1040, 1470, 1.72)), (T_YANK, (1080, 1460, 1.6)), (T_NUP1 + 0.1, (1455, 1440, 1.26)),
      (T_NDN1, (1455, 1440, 1.26)), (T_OUTC1, (1330, 1450, 1.45)), (T_CREAK - 0.1, (1700, 1440, 1.5)), (T_CREAK + 0.3, (1740, 1440, 1.62)),
      (T_EXHALE, (1740, 1440, 1.62)), (T_TIP3_1, (1930, 1440, 1.5)), (T_OPEN1, (1950, 1440, 1.42)), (T_BLOCK1 + 0.3, (1980, 1450, 1.5)),
      (T_CLOSE1, (2020, 1460, 1.55)), (T_SIT + 0.3, (2095, 1475, 1.78)), (T_CEL1, (2100, 1480, 1.8)), (T_SHOCK, (2105, 1480, 2.05)),
      (T_NCOME0, (2105, 1480, 2.0)), (T_TAP - 0.1, (2030, 1470, 1.6)), (T_RAISE0, (2030, 1470, 1.62)), (T_CRUNCH, (2060, 1475, 1.8)),
      (T_GROWL2 - 0.2, (2040, 1475, 1.66)), (DUR, (2030, 1470, 1.6))]
SHAKES = [(T_GROWL, 7, 0.6), (T_CREAK, 4, 0.25), (T_BLOCK1, 5, 0.2), (T_SHOCK, 7, 0.3), (T_JUMP1, 6, 0.25), (T_CRUNCH, 8, 0.3), (T_GROWL2, 14, 0.8)]


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


# ---------------------------------------------------------------- frame
def can_paths(t, g):
    """world positions of the three loose cans (A,B,C) or None while on the pyramid."""
    pos = {"C": (PYR_X - 27, FLOOR - 102), "A": (PYR_X + 27, FLOOR - 102), "B": (PYR_X, FLOOR - 170)}
    gx, gy = g["x"], g["y"]
    s = GS
    lh = (gx - 150 * s, gy + 20 * s)     # left hand
    rh = (gx + 150 * s, gy - 10 * s)     # right hand
    head = (gx, gy - GR * g["sy"] - 30)
    out = {}
    spec = {"A": (T_CA, 0.18, "L"), "B": (T_CB, 0.22, "R"), "C": (T_CC, 0.3, "H")}
    for key, (t0, d, dest) in spec.items():
        if t < t0:
            continue
        tgt = lh if dest == "L" else (rh if dest == "R" else head)
        if t < t0 + d:
            p = seg(t, t0, t0 + d)
            x0, y0 = pos[key]
            hh = 30 if dest != "H" else 120
            out[key] = (lerp(x0, tgt[0], p), lerp(y0, tgt[1], p) - hh * 4 * p * (1 - p), 200 * p * (1 if key != "C" else -1))
        else:
            k = t - t0 - d
            wob = 0.0
            if dest == "H":
                wob = 14 * math.exp(-k * 2.5) * math.sin(k * 16)
            out[key] = (tgt[0], tgt[1], wob if dest == "H" else (10 if dest == "R" else -10))
    return out, lh, rh


def frame(t):
    ctx = Ctx()
    g = grumpo_state(t)
    n = nibbo_state(t)
    L = [room(t)]
    L.append(scale_prop())
    L.append(bed_grumpo(t))
    if t >= T_OUT0:
        L.append(blanket_grumpo(t))

    # ---- Nibbo's bed + Nibbo
    L.append(bed_nibbo_back())
    if n["inbed"]:
        L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"], rot=n["rot"], sx=n["sx"], sy=n["sy"]))
        L.append(nib_extra(n["x"], n["y"], NR, n["rot"], n["sx"], n["sy"], n["mouth"], n["squint"], n["mask"], n["frown"]))
        if n["light"] > 0:
            L.append(f'<circle cx="{n["x"]:.0f}" cy="{n["y"]:.0f}" r="{NR+30}" fill="#fff0a0" opacity="{0.35*n["light"]:.2f}"/>')
        L.append(blanket_nibbo(t))
        hx, hy = n["hand"]
        L.append(hand(hx, hy, NB, NS, 13))
    else:
        L.append(blanket_nibbo(t, 1.0))
    if n["zz"] and n["inbed"]:
        L.append(zzz(n["x"] - 30, n["y"] - 120, t, 0.3, 0.85))

    L.append(creak_board(t))

    # ---- pyramid + loose cans + string
    fallen = set()
    loose, lh, rh = can_paths(t, g)
    fallen.update(loose.keys())
    pyr, ppos = pyramid(t, fallen)
    L.append(shadow(PYR_X, FLOOR + 4, 100))
    # Grumpo squeezing between bed and pyramid is drawn BEFORE the pyramid
    behind_pyr = T_SIDLE0 <= t < T_SIDLE1 + 0.05

    # string anchor on can B
    if t < T_ZIP0 + 0.1:
        if "B" in loose:
            bx, by, _ = loose["B"]
        else:
            bx, by = ppos["B"]
        hx, hy = n["hand"]
        taut = seg(t, T_STEP, T_YANK)
        sag = 60 * (1 - taut)
        string = (f'<path d="M{bx:.1f} {by-30:.1f} Q {(bx+hx)/2:.1f} {(by+hy)/2+sag:.1f} {hx:.1f} {hy:.1f}" fill="none" stroke="#f4f0e0" stroke-width="4"/>')
    else:
        hx, hy = n["hand"]
        string = (f'<path d="M{hx:.1f} {hy:.1f} q-10 30 -4 60" fill="none" stroke="#f4f0e0" stroke-width="4"/>' if n["inbed"] else "")

    # ---- curtains (left panel hides Grumpo)
    bul = 0.0
    if t >= T_ZIP0 + 0.1:
        bul = eout(seg(t, T_ZIP0 + 0.1, T_ZIP1 + 0.05)) * (1 - eio(seg(t, T_OUTC0, T_OUTC1)))
    trem = 1.0 if T_NUP1 <= t < T_NDN0 else 0.0

    def draw_grumpo():
        o = []
        gx, gy = g["x"], g["y"]
        if not g["hidden"]:
            o.append(shadow(gx, FLOOR + 6, 120, 0.9 if not g["sit"] else 1.0))
        o.append(grumpo(ctx, gx, gy, GS, g["ex"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"], False, 0, None, 0, t))
        if g["kind"]:
            o.append(grumpo_extra(gx, gy, GS, g["rot"], g["sx"], g["sy"], g["kind"], t, g["red"]))
        if g["tear"] > 0:
            o.append(tear(gx, gy, GS, g["tear"]))
        return "".join(o)

    def grumpo_arms(items):
        """items: list of (side, (hx,hy))"""
        ink = mix_hex(INK, "#3a0505", g["red"])
        fill = mix_hex(GFILL, "#ff6a52", g["red"])
        o = []
        for side, (hx, hy) in items:
            sx0 = g["x"] + side * 100 * GS * g["sx"]
            sy0 = g["y"] + 30 * GS
            o.append(arm(sx0, sy0, hx, hy, ink, 13, 18) + hand(hx, hy, fill, OL, 16))
        return "".join(o)

    # arms by phase
    arms = []
    gx, gy = g["x"], g["y"]
    if g.get("sneak") and not g["hidden"] and t >= T_OUT1:
        bob = 6 * math.sin(t * 9)
        arms = [(-1, (gx - 140, gy - 30 + bob)), (1, (gx + 145, gy - 50 - bob))]
    if T_SIDLE0 <= t < T_SIDLE1:
        arms = [(-1, (gx - 120, gy - 70)), (1, (gx + 125, gy - 80))]
    if T_SIDLE1 <= t < T_ZIP0:
        hl = (gx - 150 * GS, gy + 20 * GS) if t >= T_CA else (lerp(gx - 120, gx - 150 * GS, seg(t, T_SIDLE1, T_CA)), lerp(gy - 70, gy + 20 * GS, seg(t, T_SIDLE1, T_CA)))
        hr = (gx + 150 * GS, gy - 10 * GS)
        arms = [(-1, hl), (1, hr)]
    if T_OUTC0 <= t < T_TIP2_0 and not g["hidden"]:
        arms = [(1, (gx + 130, gy - 30))]
    if T_TIP3_1 <= t < T_BLOCK0:
        reach = eio(seg(t, T_TIP3_1, T_OPEN0))
        arms = [(1, (lerp(gx + 130, MB0 + 32, reach), lerp(gy - 30, 1560, reach)))]
        if t >= T_OPEN0:
            arms = [(1, (MB0 + 32 + 60 * seg(t, T_OPEN0, T_OPEN1), 1560))]
    box_pos = None
    if T_BLOCK0 <= t < T_SIT:
        if t < T_GRAB0:
            arms = [(-1, (gx - 150, gy - 60)), (1, (gx + 150, gy - 60))]   # spread wide to block the light
        elif t < T_GRAB1:
            p = eio(seg(t, T_GRAB0, T_GRAB1))
            arms = [(-1, (gx - 150, gy - 60)), (1, (lerp(gx + 150, gx + 60, p), lerp(gy - 60, gy - 150, p) if p < 0.5 else lerp(gy - 150, gy + 20, (p - 0.5) * 2)))]
            if p > 0.5:
                box_pos = (gx + 40, gy + 10 - 60 * (1 - (p - 0.5) * 2))
        else:
            up = eback(seg(t, T_GRAB1, T_GRAB1 + 0.25)) * (1 - eio(seg(t, T_CLOSE1, T_SIT)))
            box_pos = (gx, lerp(gy + 10, gy - 190, up))
            arms = [(-1, (gx - 70, box_pos[1] + 14)), (1, (gx + 70, box_pos[1] + 14))]
    if t >= T_SIT:
        box_pos = (gx, FLOOR - 2)
        arms = [(-1, (gx - 70, FLOOR - 20)), (1, (gx + 70, FLOOR - 20))]
        if T_RIB0 <= t < T_RIB1:
            p = seg(t, T_RIB0, T_RIB1)
            arms = [(-1, (gx - 70, FLOOR - 20)), (1, (gx + 10 + 90 * p, FLOOR - 70 - 60 * p))]
        if T_LID0 - 0.15 <= t < T_LID1:
            p = seg(t, T_LID0 - 0.15, T_LID1)
            arms = [(1, (gx + 70, FLOOR - 20)), (-1, (gx - 60 - 30 * p, FLOOR - 50 - 70 * math.sin(math.pi * p * 0.8)))]
    cel = None
    if t >= T_CEL0:
        p = eout(seg(t, T_CEL0, T_CEL1))
        jy = (g["y"] - (GY + 14)) if T_JUMP0 <= t < T_JUMP1 else 0
        bx0, by0, rot, sc = gx + 70, FLOOR - 20 - 130 * p + jy, 18, 1.0
        bite = 0.0
        if t >= T_RAISE0:
            q = eio(seg(t, T_RAISE0, T_RAISE1))
            bx0, by0 = lerp(gx + 70, gx + 150, q), lerp(FLOOR - 150, gy + 104, q)
            rot, sc = lerp(18, -75, q), lerp(1.0, 0.76, q)
            if t >= T_CRUNCH:
                k = eout(seg(t, T_CRUNCH, T_CRUNCH + 0.25))
                bx0, by0 = lerp(gx + 150, gx + 112, k), lerp(gy + 104, gy + 96, k) + 3 * math.sin(t * 14)
                bite = 1.0
        cel = (bx0, by0, rot, bite, sc)
        if t < T_RAISE0:
            arms = [(1, (bx0 + 14, by0 - 50)), (-1, (gx - 76, FLOOR - 50))]
        else:
            arms = [(1, (bx0 + 4, by0 - 4)), (-1, (gx - 80, gy + 60))]
    if T_JUMP0 <= t < T_JUMP1:
        arms = [(-1, (gx - 150, g["y"] - 120)), (1, (cel[0] + 14, cel[1] - 50))] if cel else [(-1, (gx - 150, g["y"] - 120)), (1, (gx + 150, g["y"] - 130))]

    # ---- draw order
    L.append(string if behind_pyr else "")
    if behind_pyr:
        L.append(draw_grumpo() + grumpo_arms(arms))
    L.append(pyr)

    # loose cans that are NOT on Grumpo's head get drawn with hands
    def loose_cans():
        o = []
        for key, (x, y, r) in loose.items():
            if t >= T_ZIP0:
                continue
            o.append(can(x, y, r))
        return "".join(o)

    # cans left behind the curtain afterwards
    if t >= T_OUTC0:
        for k, x in enumerate((1170, 1215, 1262)):
            L.append(can(x, FLOOR - 34, 0))

    hidden_draw = g["hidden"] or (T_OUTC0 <= t < T_OUTC1)
    if hidden_draw:
        L.append(draw_grumpo())
    L.append(curtain(CURT[0], CURT[1], bul, t, trem))
    L.append(curtain(WIN[0] + WIN[2] + 25, WIN[0] + WIN[2] + 95, 0, t))
    if T_PEEK <= t < T_OUTC0:
        # Grumpo's eyes peek out from the curtain's right edge
        p = eio(seg(t, T_PEEK, T_PEEK + 0.15))
        L.append(f'<g transform="translate({CURT[1] + 70 + 40*p:.0f} 1560)">'
                 f'<ellipse cx="-14" cy="0" rx="17" ry="19" fill="#fff" stroke="{OL}" stroke-width="3"/><ellipse cx="22" cy="0" rx="17" ry="19" fill="#fff" stroke="{OL}" stroke-width="3"/>'
                 f'<circle cx="-8" cy="2" r="8" fill="{INK}"/><circle cx="28" cy="2" r="8" fill="{INK}"/></g>')

    # ---- minibar + light
    open_ = eio(seg(t, T_OPEN0, T_OPEN1)) * (1 - eio(seg(t, T_CLOSE0, T_CLOSE1)))
    L.append(minibar(t, open_, item=t < T_GRAB0 + 0.2))
    block = eio(seg(t, T_BLOCK0, T_BLOCK1))
    if open_ > 0:
        cx_f = (MB0 + MB1) / 2
        L.append(f'<circle cx="{cx_f}" cy="1570" r="{320*open_:.0f}" fill="url(#fglow)" opacity="{open_:.2f}"/>')
        bop = open_ * (1 - 0.85 * block)
        if bop > 0.01:
            L.append(f'<path d="M{MB0+12} {MBT+12} L{MB0+12} {FLOOR-12} L1560 {FLOOR+90} L1560 1230Z" fill="url(#fbeam)" opacity="{bop:.2f}"/>')
        if block > 0:
            L.append(f'<circle cx="{g["x"]:.0f}" cy="{g["y"]:.0f}" r="{150*block:.0f}" fill="#fff4b0" opacity="{0.55*open_:.2f}"/>')

    if not n["inbed"] and t >= T_NCOME0:
        L.append(shadow(n["x"], FLOOR + 6, 100))
        L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"], rot=n["rot"], sx=n["sx"], sy=n["sy"]))
        L.append(nib_extra(n["x"], n["y"], NR, n["rot"], n["sx"], n["sy"], n["mouth"], 0.0, n["mask"]))
    if not behind_pyr and not hidden_draw:
        L.append(draw_grumpo())
    # cans in hands / on head
    if not hidden_draw:
        L.append(loose_cans())
    if not behind_pyr and not hidden_draw:
        L.append(string)
    elif not behind_pyr:
        L.append(string)
    if not behind_pyr and not hidden_draw:
        # box + celery between body and arms
        if box_pos and t < T_CEL0 + 0.1 or (box_pos and t >= T_SIT):
            rib = 1 - seg(t, T_RIB0, T_RIB1)
            lid = eback(seg(t, T_LID0, T_LID1)) if t >= T_LID0 else 0
            if T_JUMP0 <= t < T_JUMP1:
                pass
            L.append(cake_box(box_pos[0], box_pos[1], 0.95 if t >= T_SIT else 0.8, rib, min(1.0, lid)))
            if T_LID0 <= t < T_CEL0 + 0.3:
                q = seg(t, T_LID0, T_CEL0 + 0.3)
                for k in range(7):
                    a = math.radians(-90 + (k - 3) * 22 + 4 * math.sin(t * 6 + k))
                    r0, r1 = 50, 130 + 30 * math.sin(t * 9 + k)
                    L.append(f'<path d="M{box_pos[0]+r0*math.cos(a):.0f} {box_pos[1]-40+r0*math.sin(a):.0f} L{box_pos[0]+r1*math.cos(a):.0f} {box_pos[1]-40+r1*math.sin(a):.0f}" '
                             f'stroke="#ffe680" stroke-width="12" stroke-linecap="round" opacity="{0.8*math.sin(math.pi*q):.2f}"/>')
        if cel:
            L.append(celery(cel[0], cel[1], cel[2], cel[4], cel[3], note=True))
        L.append(grumpo_arms(arms))

    # nibbo behind grumpo at the end (drawn in front for the tap)
    if not n["inbed"] and t >= T_NCOME0:
        # Nibbo arms
        if T_TAP - 0.15 <= t < T_TAP + 0.35:
            p = math.sin(math.pi * seg(t, T_TAP - 0.15, T_TAP + 0.35))
            tx, ty = lerp(n["x"] + 90, g["x"] - 95, p), lerp(n["y"] + 10, g["y"] - 60, p)
            L.append(arm(n["x"] + 80, n["y"] - 10, tx, ty, NS, 10, -10) + hand(tx, ty, NB, NS, 13))
        if T_CRUNCH + 0.1 <= t < T_CRUNCH + 1.0:
            c = abs(math.sin((t - T_CRUNCH) * 11))
            for side in (-1, 1):
                hx2 = n["x"] + side * 40 * c + 10
                L.append(arm(n["x"] + side * 90, n["y"] + 10, hx2, n["y"] - 80, NS, 10, 10) + hand(hx2, n["y"] - 80, NB, NS, 13))

    # ---- effects
    if t < 1.2:
        L.append(growl_lines(290, 1384, t, 1 - seg(t, 0.6, 1.2)))
    if t >= T_GROWL2:
        L.append(growl_lines(g["x"], g["y"], t, 1 - seg(t, T_GROWL2 + 0.4, T_GROWL2 + 0.9)))
    L.append(thought(500, 1200, seg(t, T_TH0, T_TH1), t))
    L.append(symbol(g["x"] + 30, g["y"] - 175, "!", seg(t, T_PY + 0.05, T_PY + 0.5), "#ffb02a"))
    L.append(symbol(n["x"] + 20, n["y"] - 170, "?", seg(t, T_MASK_UP + 0.5, T_YAWN0), "#3a7ad6"))
    L.append(symbol(g["x"] + 20, g["y"] - 180, "!", seg(t, T_YANK, T_YANK + 0.45)))
    L.append(symbol(g["x"] + 40, g["y"] - 180, "!", seg(t, T_OPEN0 + 0.15, T_OPEN0 + 0.6)))
    L.append(symbol(g["x"] + 10, g["y"] - 200, "!", seg(t, T_TAP + 0.03, T_TAP + 0.5)))
    L.append(symbol(g["x"] + 60, g["y"] - 175, "?", seg(t, T_SHOCK + 0.1, T_SHOCK + 0.9), "#3a7ad6"))
    L.append(heart(n["x"] + 30, n["y"] - 150, seg(t, T_HEART, T_HEART + 0.7)))
    L.append(heart(n["x"] + 70, n["y"] - 150, seg(t, T_CRUNCH + 0.15, T_CRUNCH + 0.9), 0.8))
    L.append(heart(n["x"] - 20, n["y"] - 170, seg(t, T_CRUNCH + 0.35, T_CRUNCH + 1.1), 0.7))
    L.append(impact(g["x"] - 60, g["y"] - 60, seg(t, T_TAP, T_TAP + 0.2), "#ffffff"))
    if T_CRUNCH <= t < T_CRUNCH + 0.5:
        q = seg(t, T_CRUNCH, T_CRUNCH + 0.5)
        L.append(impact(g["x"] + 10, g["y"] + 70, q, "#c8eb8a"))
        for k in range(6):
            a = math.radians(-160 + k * 28)
            L.append(f'<rect x="{g["x"]+10+180*q*math.cos(a):.0f}" y="{g["y"]+70+180*q*math.sin(a)+300*q*q:.0f}" width="14" height="10" fill="#9ad35a" stroke="{OL}" stroke-width="3" opacity="{1-q:.2f}"/>')
    if T_ZIP0 <= t < T_ZIP1 + 0.1:
        L.append(speed_lines(g["x"] - 60, g["y"], 0, 1 - seg(t, T_ZIP0, T_ZIP1 + 0.1)))
    if T_YANK <= t < T_YANK + 0.3:
        L.append(f'<path d="M{n["hand"][0]+20:.0f} {n["hand"][1]-30:.0f} l14 -16 M{n["hand"][0]+34:.0f} {n["hand"][1]-6:.0f} l20 -6" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="{1-seg(t, T_YANK, T_YANK+0.3):.2f}"/>')

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g>'
           f'<rect width="{W}" height="{H}" fill="url(#vig)"/></svg>')
    return overlay(svg, hook_title(t + 0.12, "Day 1 of his diet:", "3 AM SNACK RUN"))


def build_sfx():
    sfx(0.0, "rumble", 0.9, 1.3)
    sfx(T_GROWL, "grumble", 0.9, 0.7)
    sfx(0.7, "grumble", 0.5, 0.9)
    sfx(0.3, "snore", 0.3, 1.2)
    sfx(T_TH0, "pop", 0.7, 1.0)
    sfx(T_TH0 + 0.15, "shine", 0.5, 1.0)
    sfx(1.45, "whoosh", 0.7, 0.9)
    sfx(1.9, "snore", 0.45, 1.15)
    sfx(2.1, "fridge_hum", 0.6, 1.0)
    sfx(2.7, "whoosh", 0.6, 1.1)
    sfx(T_OUT0, "slide_down", 0.4, 1.3)
    sfx(T_OUT1, "thud", 0.25, 1.6)
    for k in range(4):
        sfx(T_OUT1 + 0.1 + (k + 1) * (T_PY - T_OUT1 - 0.1) / 4 - 0.05, "tiptoe", 0.7, 1.0 + 0.05 * k)
    sfx(4.0, "snore", 0.4, 1.15)
    sfx(T_PY + 0.05, "blip", 0.5, 1.2)
    sfx(T_SUCK0, "inhale", 0.7, 0.8)
    sfx(T_SUCK0 + 0.1, "squeak", 0.35, 0.7)
    for k in range(6):
        sfx(T_SIDLE0 + (k + 1) * (T_SIDLE1 - T_SIDLE0) / 6 - 0.04, "tiptoe", 0.45, 1.25)
    sfx(5.9, "snore", 0.35, 1.15)
    sfx(T_BRUSH, "can", 0.4, 1.3)
    sfx(T_BRUSH + 0.2, "can", 0.3, 1.5)
    sfx(T_CA, "whoosh", 0.3, 1.8)
    sfx(T_CA + 0.18, "can", 0.6, 1.0)
    sfx(T_CA + 0.2, "squish", 0.3, 1.4)
    sfx(T_CB, "whoosh", 0.3, 1.9)
    sfx(T_CB + 0.22, "can", 0.6, 1.15)
    sfx(T_CC, "whoosh", 0.3, 1.6)
    sfx(T_CC + 0.3, "can", 0.7, 0.9)
    sfx(T_CC + 0.32, "boing", 0.35, 1.6)
    sfx(T_RELAX, "deflate", 0.35, 1.6)
    sfx(T_STEP + 0.05, "tiptoe", 0.6, 1.0)
    sfx(T_YANK, "twang", 0.8, 1.2)
    sfx(T_YANK + 0.02, "gasp", 0.5, 1.2)
    sfx(T_ZIP0, "zip", 0.8, 1.0)
    sfx(T_ZIP0 + 0.05, "whoosh", 0.6, 1.3)
    sfx(T_ZIP1, "rustle", 0.7, 1.0)
    sfx(T_ZIP0 + 0.15, "snap", 0.5, 1.3)
    sfx(T_NUP1, "boing", 0.4, 1.3)
    sfx(T_MASK_UP, "stretch", 0.35, 1.8)
    sfx(T_MASK_UP + 0.18, "click", 0.4, 1.4)
    sfx(T_MASK_UP + 0.55, "suspense", 0.45, 1.0)
    sfx(9.6, "rustle", 0.3, 1.6)
    sfx(10.0, "rustle", 0.3, 1.5)
    sfx(T_YAWN0, "inhale", 0.4, 1.4)
    sfx(T_MASK_DN, "stretch", 0.3, 1.9)
    sfx(T_NDN1, "plop", 0.4, 1.2)
    sfx(11.4, "snore", 0.45, 1.15)
    sfx(T_PEEK, "blip", 0.4, 1.4)
    sfx(T_OUTC0, "rustle", 0.45, 1.3)
    for k in range(5):
        sfx(T_TIP2_0 + (k + 1) * (T_CREAK - T_TIP2_0) / 5 - 0.05, "tiptoe", 0.65, 0.95 + 0.04 * k)
    sfx(12.8, "snore", 0.4, 1.15)
    sfx(T_CREAK, "creak", 1.0, 0.75)
    sfx(T_CREAK + 0.25, "creak", 0.5, 0.9)
    sfx(T_CREAK + 0.3, "inhale", 0.6, 0.9)
    for k in range(3):
        sfx(T_CREAK + 0.25 + k * 0.3, "squish", 0.3, 1.6)
    sfx(T_CREAK + 0.95, "rustle", 0.45, 1.0)
    sfx(T_CREAK + 1.1, "squeak", 0.3, 0.9)
    sfx(T_EXHALE - 0.2, "snore", 0.5, 1.15)
    sfx(T_EXHALE, "deflate", 0.6, 1.3)
    sfx(T_TIP3_0 + 0.25, "tiptoe", 0.6, 1.0)
    sfx(T_TIP3_1 - 0.05, "tiptoe", 0.6, 1.05)
    sfx(T_OPEN0, "click", 0.6, 0.9)
    sfx(T_OPEN0 + 0.05, "creak", 0.4, 1.6)
    sfx(T_OPEN0 + 0.1, "shine", 0.9, 0.9)
    sfx(T_OPEN0 + 0.1, "fridge_hum", 0.6, 1.0)
    sfx(T_OPEN0 + 0.2, "gasp", 0.5, 1.1)
    sfx(T_BLOCK0, "whoosh", 0.5, 1.5)
    sfx(T_BLOCK1, "thud", 0.5, 1.2)
    sfx(16.4, "fridge_hum", 0.5, 1.0)
    sfx(T_GRAB0 + 0.1, "rustle", 0.35, 1.6)
    sfx(T_GRAB1, "ding", 0.6, 1.0)
    sfx(T_GRAB1 + 0.05, "shine", 0.4, 1.2)
    sfx(T_CLOSE1, "click", 0.7, 0.8)
    sfx(T_CLOSE1 + 0.02, "thud", 0.3, 1.5)
    sfx(T_SIT, "plop", 0.4, 0.9)
    sfx(T_RIB0, "stretch", 0.6, 1.4)
    sfx(T_RIB1 - 0.1, "zip", 0.4, 1.6)
    sfx(18.4, "rustle", 0.35, 1.7)
    sfx(18.6, "snore", 0.3, 1.15)
    sfx(T_LID0, "pop", 0.6, 0.9)
    sfx(T_LID0 + 0.05, "shine", 1.0, 1.0)
    sfx(T_CEL0, "slide_up", 0.4, 1.0)
    sfx(T_CEL1, "squeak", 0.4, 0.8)
    sfx(T_SHOCK, "blip_down", 0.8, 0.8)
    sfx(T_SHOCK + 0.05, "gasp", 0.6, 0.9)
    sfx(T_SHOCK + 0.4, "deflate", 0.6, 0.8)
    sfx(T_NCOME0 + 0.1, "tiptoe", 0.4, 1.4)
    sfx(T_NCOME0 + 0.3, "tiptoe", 0.4, 1.5)
    sfx(T_TAP, "tap", 0.9, 1.0)
    sfx(T_TAP + 0.1, "tap", 0.7, 1.1)
    sfx(T_JUMP0, "boing", 0.8, 1.0)
    sfx(T_JUMP0 + 0.03, "gasp", 0.6, 1.3)
    sfx(T_JUMP1, "thud", 0.6, 1.0)
    sfx(T_HEART, "pop", 0.6, 1.4)
    sfx(T_HEART + 0.05, "ding", 0.4, 1.6)
    sfx(T_RAISE0, "slide_up", 0.3, 0.8)
    sfx(T_CRUNCH, "crunch", 1.0, 1.0)
    sfx(T_CRUNCH + 0.2, "munch", 0.6, 1.1)
    for k in range(5):
        sfx(T_CRUNCH + 0.15 + k * 0.18, "tap", 0.6, 1.5 + 0.05 * k)
    sfx(T_CRUNCH + 0.15, "pop", 0.4, 1.6)
    sfx(T_CRUNCH + 0.4, "pop", 0.4, 1.8)
    sfx(T_GROWL2, "rumble", 1.0, 0.9)
    sfx(T_GROWL2 + 0.05, "grumble", 1.0, 0.6)
    sfx(T_MASKSNAP, "stretch", 0.4, 2.0)
    sfx(T_MASKSNAP + 0.08, "boing", 0.7, 1.5)
