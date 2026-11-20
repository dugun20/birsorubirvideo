"""Grumpo & Nibbo — Episode 3: The Pancake Tower (kitchen, escalating counter, 60 fps).

Grumpo flips pancakes onto Nibbo's plate, doubling every round (1,2,4,8,16,32).
Nibbo never gets a bite; one pancake sticks to the wall; the 62-high tower
sways, falls and buries BOTH. Final: the wall pancake drops on Grumpo's head (STACK 1).
"""
import math, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow
from hook import overlay, hook_title, counter

W, H, FPS, DUR = 1080, 1920, 60, 22.0
FLOOR = 1700
NR = 112
NG = FLOOR - NR          # nibbo centre y
NX0 = 380
GS = 0.92
GY = FLOOR - 120
GX0 = 720
PAN_REST = (935, 1440)
PAN_UP = (905, 1335)
TH = 11                  # pancake thickness in a stack
WALL_X, WALL_Y = 640, 1130   # where the stray pancake sticks

# rounds: flip time, batch size, flight duration, apex height, target nibbo x
ROUNDS = [
    (0.35, 1, 0.80, 240, NX0),
    (2.25, 2, 0.85, 280, NX0),
    (3.95, 4, 0.95, 200, NX0 + 100),   # under-flip: lands short, nibbo dashes
    (5.95, 8, 0.95, 170, NX0),   # top one escapes and sticks to the wall
    (8.35, 16, 1.00, 230, NX0),
    (13.30, 32, 1.15, 250, NX0),
]
STRAY_T0, STRAY_T1 = 5.95 + 0.95 * 0.5, 6.62
CRASH = 17.05
FALL0 = 16.2
DROP0, DROP1 = 19.6, 20.1

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


def bump(t, t0, d=0.25):
    return math.sin(math.pi * seg(t, t0, t0 + d)) if t0 <= t < t0 + d else 0.0


# ---------------------------------------------------------------- props
def pancake(x, y, rot=0.0, s=1.0, sq=1.0, butter=False):
    o = (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f} {s*sq:.3f})">'
         f'<ellipse cx="0" cy="0" rx="66" ry="15" fill="#c97a2c" stroke="{OL}" stroke-width="5"/>'
         f'<ellipse cx="0" cy="-5" rx="62" ry="12" fill="#f5c063" stroke="{OL}" stroke-width="3.5"/>'
         '<ellipse cx="-14" cy="-8" rx="26" ry="3.5" fill="#ffe2a0" opacity="0.9"/>')
    if butter:
        o += (f'<path d="M-16 -18 l18 -8 l20 6 l-18 9z" fill="#fff3a0" stroke="{OL}" stroke-width="3.5" stroke-linejoin="round"/>'
              f'<path d="M-16 -18 v6 l18 9 v-6z M20 -20 v6 l-18 9" fill="#ffe066" stroke="{OL}" stroke-width="3.5" stroke-linejoin="round"/>')
    return o + '</g>'


def stack_pts(x0, y0, n, base=0.0, bend=0.0, th=TH):
    """positions/angles for n pancakes stacked from (x0,y0) upward; angles in radians."""
    pts = []
    x, y = x0, y0
    for j in range(n):
        a = base + bend * (j / max(1, n - 1)) if n > 1 else base
        pts.append((x, y, a))
        x += th * math.sin(a)
        y -= th * math.cos(a)
    return pts


def draw_stack(pts, butter=True):
    o = []
    for k, (x, y, a) in enumerate(pts):
        o.append(pancake(x, y, math.degrees(a), butter=butter and k == len(pts) - 1))
    return "".join(o)


def pan(x, y, rot=0.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">'
            f'<rect x="-165" y="-9" width="90" height="18" rx="9" fill="#2a2a33" stroke="{OL}" stroke-width="4"/>'
            '<rect x="-160" y="-5" width="34" height="5" rx="2" fill="#5a5a6a"/>'
            f'<path d="M-92 -6 Q -86 26 0 26 Q 86 26 92 -6Z" fill="#3a3a46" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<ellipse cx="0" cy="-6" rx="92" ry="16" fill="#55556a" stroke="{OL}" stroke-width="6"/>'
            '<ellipse cx="0" cy="-5" rx="74" ry="10" fill="#2f2f3a"/>'
            '<path d="M-60 12 Q 0 22 60 12" stroke="#6a6a80" stroke-width="4" fill="none" opacity="0.8"/></g>')


def pan_grip(x, y, rot):
    a = math.radians(rot)
    return x + (-155) * math.cos(a), y + (-155) * math.sin(a)


def pan_surface(x, y, rot, h=-10):
    a = math.radians(rot)
    return x - h * math.sin(a), y + h * math.cos(a)


def plate(x, y, rot=0.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">'
            f'<ellipse cx="0" cy="4" rx="92" ry="19" fill="#d7e4f2" stroke="{OL}" stroke-width="5"/>'
            f'<ellipse cx="0" cy="0" rx="90" ry="17" fill="#ffffff" stroke="{OL}" stroke-width="5"/>'
            '<ellipse cx="0" cy="0" rx="60" ry="10" fill="#eaf2fb" stroke="#9cc0e0" stroke-width="3"/></g>')


def room(t):
    o = [f'<rect x="-900" y="-900" width="3200" height="{FLOOR+900}" fill="#fbe7c6"/>']
    for x in range(-900, 2300, 90):
        o.append(f'<rect x="{x}" y="-900" width="30" height="{FLOOR+900}" fill="#f7dcb2"/>')
    # backsplash tiles behind stove/counter
    o.append(f'<rect x="760" y="1190" width="1200" height="280" fill="#d6f0ea"/>')
    for x in range(760, 1960, 56):
        o.append(f'<line x1="{x}" y1="1190" x2="{x}" y2="1470" stroke="#b5dcd4" stroke-width="4"/>')
    for y in range(1190, 1470, 56):
        o.append(f'<line x1="760" y1="{y}" x2="1960" y2="{y}" stroke="#b5dcd4" stroke-width="4"/>')
    o.append(f'<rect x="760" y="1190" width="1200" height="280" fill="none" stroke="{OL}" stroke-width="5"/>')
    # upper cabinets
    for cx in (820, 1000, 1180):
        o.append(f'<rect x="{cx}" y="800" width="170" height="280" rx="10" fill="#7fc6a4" stroke="{OL}" stroke-width="6"/>'
                 f'<rect x="{cx+18}" y="818" width="134" height="244" rx="8" fill="#93d4b4" stroke="{OL}" stroke-width="3"/>'
                 f'<rect x="{cx+132}" y="1010" width="10" height="40" rx="5" fill="#f4d27a" stroke="{OL}" stroke-width="3"/>')
    # fridge
    o.append(f'<rect x="-140" y="1010" width="330" height="{FLOOR-1010}" rx="22" fill="#e9f3fb" stroke="{OL}" stroke-width="7"/>'
             f'<path d="M-140 1240 H190" stroke="{OL}" stroke-width="6"/>'
             f'<rect x="150" y="1080" width="16" height="110" rx="8" fill="#b9c7d6" stroke="{OL}" stroke-width="4"/>'
             f'<rect x="150" y="1290" width="16" height="170" rx="8" fill="#b9c7d6" stroke="{OL}" stroke-width="4"/>'
             '<path d="M-110 1040 V1210" stroke="#ffffff" stroke-width="10" stroke-linecap="round" opacity="0.8"/>'
             f'<circle cx="40" cy="1120" r="16" fill="#ff6b6b" stroke="{OL}" stroke-width="4"/>'
             f'<rect x="70" y="1300" width="40" height="30" rx="5" fill="#ffd23a" stroke="{OL}" stroke-width="4" transform="rotate(-8 90 1315)"/>'
             f'<circle cx="0" cy="1330" r="13" fill="#5aa9ff" stroke="{OL}" stroke-width="4"/>')
    # wall clock above fridge
    a1 = t * 30
    o.append(f'<g transform="translate(40 900)"><circle r="58" fill="#ffffff" stroke="{OL}" stroke-width="7"/>'
             f'<circle r="46" fill="none" stroke="#f4b860" stroke-width="5"/>'
             f'<path d="M0 0 V-34" stroke="{OL}" stroke-width="7" stroke-linecap="round" transform="rotate({a1:.1f})"/>'
             f'<path d="M0 0 H24" stroke="{OL}" stroke-width="7" stroke-linecap="round" transform="rotate({a1/12:.1f})"/>'
             f'<circle r="6" fill="{OL}"/></g>')
    # counter cabinets right of stove
    o.append(f'<rect x="1035" y="1470" width="900" height="{FLOOR-1470}" fill="#7fc6a4" stroke="{OL}" stroke-width="6"/>'
             f'<rect x="1025" y="1452" width="920" height="26" rx="6" fill="#f2efe8" stroke="{OL}" stroke-width="6"/>'
             f'<rect x="1060" y="1500" width="160" height="170" rx="8" fill="#93d4b4" stroke="{OL}" stroke-width="3"/>')
    # floor (checker)
    o.append(f'<rect x="-900" y="{FLOOR}" width="3200" height="900" fill="#f3efe6"/>')
    for r, y in enumerate(range(FLOOR, FLOOR + 900, 74)):
        for c, x in enumerate(range(-900, 2300, 92)):
            if (r + c) % 2 == 0:
                o.append(f'<rect x="{x + (r % 2) * 0}" y="{y}" width="92" height="74" fill="#8fb6dc"/>')
    o.append(f'<rect x="-900" y="{FLOOR-26}" width="3200" height="26" fill="#ffffff" stroke="{OL}" stroke-width="5"/>')
    o.append(f'<line x1="-900" y1="{FLOOR}" x2="2300" y2="{FLOOR}" stroke="{OL}" stroke-width="6"/>')
    return "".join(o)


def stove(t, flame):
    o = [f'<rect x="845" y="1470" width="172" height="{FLOOR-1470}" fill="#eef2f6" stroke="{OL}" stroke-width="6"/>',
         f'<rect x="861" y="1540" width="140" height="110" rx="10" fill="#3a3040" stroke="{OL}" stroke-width="5"/>',
         f'<rect x="872" y="1552" width="118" height="86" rx="6" fill="#ff9a4a" opacity="0.55"/>',
         f'<rect x="861" y="1500" width="140" height="14" rx="7" fill="#c9d3dd" stroke="{OL}" stroke-width="3"/>',
         f'<rect x="836" y="1452" width="190" height="24" rx="6" fill="#2a2a33" stroke="{OL}" stroke-width="5"/>']
    for kx in (875, 915, 955, 995):
        o.append(f'<circle cx="{kx}" cy="1488" r="8" fill="#ffffff" stroke="{OL}" stroke-width="3"/>')
    if flame > 0:
        for k in range(5):
            fx = 885 + k * 25
            hh = (16 + 6 * math.sin(t * 30 + k * 2)) * flame
            o.append(f'<path d="M{fx-8} 1454 Q {fx} {1454-hh*2:.1f} {fx+8} 1454Z" fill="#5ab0ff" stroke="#2a6ad0" stroke-width="2"/>')
    return "".join(o)


def wall_cake(x, y, rot=0.0, sx=1.0, sy=1.0):
    """pancake seen face-on (stuck flat on the wall)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx:.3f} {sy:.3f})">'
            f'<path d="M-62 -6 Q -60 -60 0 -62 Q 64 -60 62 0 Q 66 40 30 56 Q 0 66 -34 54 Q -66 40 -62 -6Z" fill="#e3a24a" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            '<path d="M-48 -4 Q -46 -46 0 -48 Q 48 -46 48 0 Q 50 30 22 42 Q 0 50 -26 40 Q -50 30 -48 -4Z" fill="#f5c063"/>'
            '<circle cx="-18" cy="-16" r="5" fill="#d9913a"/><circle cx="16" cy="6" r="4" fill="#d9913a"/><circle cx="-6" cy="24" r="4.5" fill="#d9913a"/>'
            '<circle cx="24" cy="-24" r="3.5" fill="#d9913a"/>'
            '<path d="M-30 -36 Q -10 -46 12 -42" stroke="#ffe2a0" stroke-width="6" fill="none" stroke-linecap="round"/></g>')


def steam_puffs(x, y, t, amt):
    if amt <= 0:
        return ""
    o = []
    for k, (dx, ph) in enumerate([(-40, 0), (10, 0.33), (50, 0.66)]):
        p = (t * 1.4 + ph) % 1
        o.append(f'<circle cx="{x+dx+math.sin(p*6+k)*12:.1f}" cy="{y-p*150:.1f}" r="{14+p*26:.1f}" fill="#ffffff" '
                 f'stroke="#d8d8e0" stroke-width="3" opacity="{amt*(1-p)*0.85:.2f}"/>')
    return "".join(o)


def sweat(x, y, p):
    if p <= 0:
        return ""
    return (f'<path d="M{x} {y} q12 20 0 28 q-12 -8 0 -28z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3" opacity="{p:.2f}"/>')


def arm(x0, y0, x1, y1, col, w=10, sag=30):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    return f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


# ---------------------------------------------------------------- pile (deterministic)
def _pile():
    rnd = random.Random(7)
    back, front = [], []
    for i in range(70):
        x = rnd.uniform(260, 1080)
        h = 300 * math.exp(-((x - 560) / 210) ** 2) + 140 * math.exp(-((x - 900) / 130) ** 2) + 30
        y = rnd.uniform(FLOOR - h, FLOOR - 8)
        back.append((x, y, rnd.uniform(-25, 25), rnd.uniform(0.85, 1.08), rnd.uniform(0, 0.35)))
    for i in range(80):
        x = rnd.uniform(250, 1090)
        h = 70 * math.exp(-((x - 560) / 45) ** 2) + 110 * math.exp(-((x - 900) / 110) ** 2) \
            + 70 * math.exp(-((x - 300) / 60) ** 2) + 14
        near = min(abs(x - 450), abs(x - 670))
        rot = rnd.uniform(-18, 18) if near < 120 else rnd.uniform(-30, 30)
        y = rnd.uniform(FLOOR - h, FLOOR - 2)
        front.append((x, y, rot, rnd.uniform(0.85, 1.05), rnd.uniform(0.05, 0.45)))
    back.sort(key=lambda p: p[1])
    front.sort(key=lambda p: p[1])
    return back, front


PILE_BACK, PILE_FRONT = _pile()


def draw_pile(t, items):
    o = []
    for (x, y, r, s, d) in items:
        t0 = CRASH + d
        if t < t0:
            continue
        p = seg(t, t0, t0 + 0.18)
        yy = lerp(y - 320, y, ein(p) if p < 1 else 1)
        sq = 1.0
        if p >= 1:
            k = t - t0 - 0.18
            if k < 0.15:
                sq = 1 - 0.35 * math.sin(math.pi * k / 0.15)
        o.append(pancake(x, yy, r + (1 - p) * 90, s, sq))
    return "".join(o)


# ---------------------------------------------------------------- state helpers
def landed_count(t):
    n = 0
    for k, (tf, b, fd, ap, tx) in enumerate(ROUNDS):
        if t >= tf + fd:
            n += b - (1 if k == 3 else 0)
    return n


def last_land(t):
    lt = None
    for k, (tf, b, fd, ap, tx) in enumerate(ROUNDS):
        if t >= tf + fd:
            lt = tf + fd
    return lt


def sway(t):
    """returns (bend L, nibbo dx) for the tower during idle/balance/sway phases."""
    L, dx = 0.0, 0.0
    # gentle idle wobble once tall
    n = landed_count(t)
    if n >= 7:
        L += 0.02 * math.sin(t * 5)
    # balancing after round 5
    if 9.35 <= t < 11.4:
        k = t - 9.35
        A = 0.32 * math.exp(-k * 1.2)
        L += A * math.sin(2 * math.pi * 1.4 * k)
        dx += 70 * math.exp(-k * 1.2) * math.sin(2 * math.pi * 1.4 * k + 0.5)
    if 11.4 <= t < 13.3:
        L += 0.05 * math.sin(t * 3)
    # round 6 sway, growing
    if 14.6 <= t < FALL0:
        k = t - 14.6
        A = lerp(0.12, 0.5, k / (FALL0 - 14.6))
        f = 0.78
        L += A * math.sin(2 * math.pi * f * k)
        dx += 60 * (A / 0.5) * math.sin(2 * math.pi * f * k)
    return L, dx


def nibbo_state(t):
    n = dict(x=NX0, y=NG, ex="happy", rot=0.0, sx=1.0, sy=1.0)
    plate_up = (0.0, -150.0, 0.0)
    bite = (150.0, -5.0, -35.0)
    b = 0.0
    if t < 0.35:
        n["ex"] = "joy"
    elif t < 1.2:
        n["ex"] = "happy"
    if 1.3 <= t < 2.6:
        b = eio(seg(t, 1.3, 1.6)) - eio(seg(t, 2.25, 2.5))
        n["ex"] = "wow" if t < 2.25 else "uhoh"
    if 2.6 <= t < 3.2:
        n["ex"] = "nervous"
    if 3.2 <= t < 3.95:
        n["ex"] = "happy"
    # round 3 dash right
    if 3.95 <= t < 5.7:
        go = eio(seg(t, 4.3, 4.65))
        back = eio(seg(t, 5.15, 5.6))
        n["x"] = NX0 + 100 * go - 100 * back
        n["ex"] = "wow" if t < 4.9 else "joy"
        if 4.3 <= t < 4.65 or 5.15 <= t < 5.6:
            n["y"] = NG - abs(math.sin(t * 22)) * 10
    if 5.7 <= t < 6.5:
        n["ex"] = "happy"
    if 6.5 <= t < 7.9:
        n["ex"] = "wow"
    if 7.9 <= t < 9.35:
        n["ex"] = "happy" if t < 8.35 else "wow"
    if 9.35 <= t < 11.4:
        n["ex"] = "nervous"
    if 11.4 <= t < 12.0:
        n["ex"] = "uhoh"
    if 12.0 <= t < 13.3:
        n["ex"] = "nervous"
        n["rot"] = 10 * math.sin((t - 12.0) * 16) * (1 - seg(t, 12.9, 13.3))   # 'no no no'
    if 13.3 <= t < 14.45:
        n["ex"] = "uhoh"
    if 14.45 <= t < FALL0:
        n["ex"] = "nervous"
        k = t - 14.45
        if k < 0.3:
            s = math.sin(math.pi * k / 0.3)
            n["sy"], n["sx"] = 1 - 0.22 * s, 1 + 0.14 * s
    L, dx = sway(t)
    n["x"] += dx
    if t < 9.35 and 0 <= t:
        pass
    # balancing shuffle bounce
    if 9.35 <= t < 11.4 or 14.6 <= t < FALL0:
        n["y"] = NG - abs(math.sin(t * 16)) * 8
    # fall: pulled by the tower
    if FALL0 <= t < CRASH:
        p = seg(t, FALL0, CRASH)
        x0 = NX0 + sway(FALL0 - 1e-3)[1]
        n["x"] = lerp(x0, 450, eio(p))
        n["y"] = NG - 140 * math.sin(math.pi * p)
        n["rot"] = 45 * math.sin(math.pi * p)
        n["ex"] = "wow"
    if t >= CRASH:
        n["x"], n["y"] = 450, NG + 40
        k = t - CRASH
        if k < 0.3:
            s = math.sin(math.pi * k / 0.3)
            n["sy"], n["sx"] = 1 - 0.25 * s, 1 + 0.15 * s
        n["ex"] = "dizzy" if t < 18.4 else ("nervous" if t < 20.35 else ("joy" if math.sin(t * 9) > -0.4 else "happy"))
        if t >= 20.35:
            n["y"] = NG + 40 - abs(math.sin(t * 12)) * 5
    # plate pose
    if t < FALL0:
        px = lerp(plate_up[0], bite[0], b)
        py = lerp(plate_up[1], bite[1], b)
        pr = lerp(plate_up[2], bite[2], b)
        n["plate"] = (n["x"] + px, n["y"] + py, pr)
    elif t < CRASH:
        n["plate"] = (n["x"] + 10, n["y"] - 150, n["rot"] * 0.6)
    else:
        n["plate"] = None
    return n


def grumpo_state(t):
    g = dict(x=GX0, y=GY, ex="smug", look=(-1, -0.2), sx=1.0, sy=1.0, red=0.0, steam=0.0, pan=True, rot=0.0)
    # laugh bounce at start / during balancing
    if 9.6 <= t < 10.8:
        g["y"] = GY - 8 * abs(math.sin(t * 18))
        g["look"] = (-1, -0.6)
    if 6.55 <= t < 7.8:
        g["ex"], g["look"] = "suspicious", (-0.6, -1)
    if 11.3 <= t < 12.2:
        g["ex"], g["look"] = "smug", (1, -0.6)
    if 12.2 <= t < 13.3:
        g["ex"] = "angry"
        g["red"] = 0.45 * seg(t, 12.2, 12.6)
        g["x"] = GX0 + 5 * math.sin(t * 70)
        g["sy"], g["sx"] = 0.94, 1.04
        g["look"] = (1, -0.4)
    if 13.3 <= t < 13.7:
        g["red"] = 0.45 * (1 - seg(t, 13.3, 13.7))
        g["sy"], g["sx"] = 1.08, 0.95
        g["ex"] = "shock"
        g["look"] = (-0.6, -1)
    if 13.7 <= t < 15.3:
        g["ex"], g["look"] = "smug", (-0.8, -1)
    if 15.3 <= t < FALL0:
        g["pan"] = False
        p = eio(seg(t, 15.3, 15.9))
        g["x"] = lerp(GX0, 670, p)
        g["y"] = GY - (abs(math.sin(t * 14)) * 10 if p < 1 else 0)
        g["ex"], g["look"] = "smug", (-0.5, -1)
    if FALL0 <= t < CRASH:
        g["pan"] = False
        g["x"] = 670
        g["ex"], g["look"] = "shock", (-0.3, -1)
        g["sy"] = 1 + 0.05 * math.sin(t * 40)
    if t >= CRASH:
        g["pan"] = False
        g["x"] = 670
        g["y"] = GY + 40
        k = t - CRASH
        if k < 0.3:
            s = math.sin(math.pi * k / 0.3)
            g["sy"], g["sx"] = 1 - 0.2 * s, 1 + 0.12 * s
        if t < 17.6:
            g["ex"], g["look"] = "shock", (0, 0)
        elif t < DROP1:
            g["ex"], g["look"] = "angry", (-1, 0.1)
        else:
            g["ex"], g["look"] = "grumpy", (0, -1)
    # small flip bounce each round
    for (tf, b, fd, ap, tx) in ROUNDS[:5]:
        if tf - 0.1 <= t < tf + 0.25:
            k = seg(t, tf - 0.1, tf + 0.25)
            g["sy"] = 1 + 0.06 * math.sin(math.pi * k)
    return g


def pan_state(t):
    """pan centre + rotation; stays on stove when grumpo leaves."""
    x, y = PAN_REST
    rot = 0.0
    for (tf, b, fd, ap, tx) in ROUNDS:
        up = eio(seg(t, tf - 0.22, tf)) - eio(seg(t, tf + 0.1, tf + 0.5))
        if up > 0:
            big = b == 32
            ux, uy = PAN_UP
            if big:
                uy -= 30
            x, y = lerp(PAN_REST[0], ux, up), lerp(PAN_REST[1], uy, up)
            rot = -32 * up
    if 12.2 <= t < 13.08:
        y += 18 * seg(t, 12.2, 12.5) + 4 * math.sin(t * 60)
    return x, y, rot


def batch_in_pan(t):
    """how many pancakes are cooking in the pan + their growth scale."""
    prev_end = -10
    for k, (tf, b, fd, ap, tx) in enumerate(ROUNDS):
        if t < tf:
            if k == 0:
                return b, 1.0
            if k == 5:
                n = 1 + int(31 * eio(seg(t, 11.3, 12.1)))
                return n, 1.0 if t >= 11.3 else 0.0
            c0 = prev_end + 0.55
            gsc = eout(seg(t, c0, c0 + 0.35))
            return b, gsc
        prev_end = tf
    return 0, 0.0


def flight(t):
    """active flying batch: (cx, cy, spin_deg, n) or None, plus stray state."""
    for k, (tf, b, fd, ap, tx) in enumerate(ROUNDS):
        if tf <= t < tf + fd:
            p = (t - tf) / fd
            sx, sy = pan_surface(PAN_UP[0], PAN_UP[1] - (30 if b == 32 else 0), -32)
            before = landed_count(tf)
            n = b
            if k == 3 and t >= STRAY_T0:
                n = b - 1
            h = n * TH
            tx_, ty_ = tx, NG - 150 - 7 - before * TH - h / 2 + 6
            x = lerp(sx, tx_, p)
            y = lerp(sy - h / 2, ty_, p) - ap * 4 * p * (1 - p)
            spin = -360 * eio(p)
            return (x, y, spin, n, h)
    return None


# ---------------------------------------------------------------- camera
CK = [(0.0, (632, 1272, 1.45)), (1.2, (632, 1259, 1.45)), (8.5, (632, 1259, 1.45)), (9.5, (630, 1190, 1.20)),
      (12.9, (630, 1190, 1.20)), (13.7, (620, 1010, 1.0)), (CRASH, (620, 1010, 1.0)), (17.75, (600, 1247, 1.5)),
      (DUR, (600, 1247, 1.5))]
SHAKES = [(14.45, 14, 0.3), (CRASH, 22, 0.45), (DROP1, 6, 0.2)]


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
def frame(t):
    ctx = Ctx()
    L = [room(t)]
    # stray stuck on the wall (peels before dropping)
    if STRAY_T1 <= t < DROP0:
        k = t - STRAY_T1
        sq = 1 - 0.3 * math.sin(math.pi * min(1, k / 0.18)) if k < 0.18 else 1.0
        peel = seg(t, DROP0 - 0.7, DROP0)
        wob = 4 * math.sin(t * 40) * peel
        L.append(wall_cake(WALL_X, WALL_Y + 26 * eio(peel), wob, 1 / sq if k < 0.18 else 1.0, sq * (1 - 0.15 * peel)))

    g = grumpo_state(t)
    n = nibbo_state(t)
    px, py, prot = pan_state(t)
    cooking, gsc = batch_in_pan(t)
    flame = 1.0 if (t < FALL0 and abs(py - PAN_REST[1]) < 30) else (0.6 if t < FALL0 else 0.0)
    L.append(stove(t, flame))

    # back pile
    if t >= CRASH:
        L.append(draw_pile(t, PILE_BACK))

    # ---- Nibbo
    L.append(shadow(n["x"], FLOOR + 4, 105, max(0.2, 1 - (NG - n["y"]) / 300)))
    L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"], rot=n["rot"], sx=n["sx"], sy=n["sy"]))
    if n["ex"] == "nervous" and (9.35 <= t < 14.45 or t >= 18.4):
        L.append(sweat(n["x"] - 95, n["y"] - 80 + 30 * ((t * 1.5) % 1), 1.0))

    # ---- Grumpo
    L.append(shadow(g["x"], FLOOR + 4, 120))
    L.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"],
                    False, 0, None, 0, t))

    # ---- tower on plate (before crash)
    tower = ""
    count = landed_count(t)
    if n["plate"] is not None:
        qx, qy, qr = n["plate"]
        if count > 0:
            lt = last_land(t)
            th = TH
            if lt is not None and t - lt < 0.3:
                th = TH * (1 - (0.45 if count > 40 else 0.3) * math.sin(math.pi * (t - lt) / 0.3))
            Lb, _ = sway(t)
            base = math.radians(qr)
            if FALL0 <= t < CRASH:
                p = seg(t, FALL0, CRASH)
                base += 1.45 * ein(p)
                Lb = lerp(0.5, 0.25, p)
            bx = qx - 7 * math.sin(math.radians(qr))
            by = qy - 7 * math.cos(math.radians(qr))
            tower = draw_stack(stack_pts(bx, by, count, base, Lb, th))
        # nibbo arms holding plate
        a = math.radians(qr)
        lx_, ly_ = qx - 80 * math.cos(a), qy - 80 * math.sin(a) + 6
        rx_, ry_ = qx + 80 * math.cos(a), qy + 80 * math.sin(a) + 6
        arms = (arm(n["x"] - 78, n["y"] - 60, lx_, ly_, "#3d2a12", 10, -10) + arm(n["x"] + 78, n["y"] - 60, rx_, ry_, "#3d2a12", 10, -10)
                + f'<circle cx="{lx_:.1f}" cy="{ly_:.1f}" r="12" fill="#ffd23c" stroke="#3d2a12" stroke-width="4"/>'
                + f'<circle cx="{rx_:.1f}" cy="{ry_:.1f}" r="12" fill="#ffd23c" stroke="#3d2a12" stroke-width="4"/>')
        L.append(plate(qx, qy, qr))
        L.append(tower)
        L.append(arms)

    # ---- pan + grumpo arm
    if cooking and gsc > 0 and t < FALL0:
        sx_, sy_ = pan_surface(px, py, prot, -8)
        pts = stack_pts(sx_, sy_, cooking, math.radians(prot), 0.0, TH * gsc)
        L.append(pan(px, py, prot) if False else "")
        L.append(pan(px, py, prot))
        L.append(draw_stack(pts, butter=False))
    else:
        L.append(pan(px, py, prot))
    if g["pan"]:
        gx_, gy_ = pan_grip(px, py, prot)
        ink = mix_hex("#1a0a2e", "#3a0505", g["red"])
        L.append(arm(g["x"] + 95, g["y"] + 15, gx_, gy_, ink, 12, 20))
        L.append(f'<circle cx="{gx_:.1f}" cy="{gy_:.1f}" r="15" fill="#9466e0" stroke="{OL}" stroke-width="6"/>')
    # steam from pan while cooking
    cook_amt = 0.0
    for k, (tf, b, fd, ap, tx) in enumerate(ROUNDS):
        if tf - 1.3 <= t < tf - 0.2:
            cook_amt = 1.0
    if t < 0.3:
        cook_amt = 1.0
    if t < FALL0:
        L.append(steam_puffs(px, py - 40 - cooking * TH, t, cook_amt))

    # ---- flying batch
    f = flight(t)
    if f:
        x, y, spin, nb, h = f
        L.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({spin:.1f})">' +
                 draw_stack(stack_pts(0, h / 2 - 6, nb, 0, 0), butter=False) + '</g>')
        tf = [r[0] for r in ROUNDS if r[0] <= t][-1]
        if t - tf < 0.25:
            L.append(speed_lines(x + 80, y + 20, 200, 0.8 * (1 - (t - tf) / 0.25)))
    # stray flying to the wall
    if STRAY_T0 <= t < STRAY_T1:
        p = seg(t, STRAY_T0, STRAY_T1)
        tf, b, fd, ap, tx = ROUNDS[3]
        q = (STRAY_T0 - tf) / fd
        sx, sy = pan_surface(PAN_UP[0], PAN_UP[1], -32)
        before = landed_count(tf)
        h = 8 * TH
        x0 = lerp(sx, tx, q)
        y0 = lerp(sy - h / 2, NG - 157 - before * TH - h / 2, q) - ap * 4 * q * (1 - q) - h / 2
        x = lerp(x0, WALL_X, eout(p))
        y = lerp(y0, WALL_Y, eout(p)) - 70 * math.sin(math.pi * p)
        if p < 0.6:
            L.append(pancake(x, y, -300 * p, 1 - 0.2 * p))
        else:
            q = (p - 0.6) / 0.4
            L.append(wall_cake(x, y, 0, 0.8 + 0.2 * q, 0.3 + 0.7 * q))

    # ---- falling tower → crash cloud
    if CRASH <= t < CRASH + 0.6:
        p = seg(t, CRASH, CRASH + 0.6)
        for k in range(7):
            cx = 330 + k * 110 + 40 * p * (k - 3)
            L.append(f'<circle cx="{cx:.0f}" cy="{FLOOR - 60 - 70*p:.0f}" r="{40 + 50*p:.0f}" fill="#fff4dc" stroke="#e0c890" stroke-width="5" opacity="{1-p:.2f}"/>')

    # front pile + plate stuck in it
    if t >= CRASH:
        L.append(draw_pile(t, PILE_FRONT))
        if t >= CRASH + 0.2:
            L.append(plate(320, 1668, -18))

    # stray drop onto grumpo's head
    if DROP0 <= t:
        p = seg(t, DROP0, DROP1)
        hx, hy = 670, GY + 40 - 116
        if p < 1:
            x = lerp(WALL_X, hx, eio(p))
            y = lerp(WALL_Y + 26, hy, ein(p))
            if p < 0.3:
                L.append(wall_cake(x, y, 20 * p, 1.0, 0.85 - 2.0 * p))
            else:
                L.append(pancake(x, y, -120 * (1 - p)))
        else:
            k = t - DROP1
            sq = 1 - 0.4 * math.sin(math.pi * min(1, k / 0.15)) if k < 0.15 else 1.0
            dr = eout(seg(t, DROP1 + 0.15, DROP1 + 1.0))
            if dr > 0:
                L.append(f'<path d="M{hx-40} {hy+8} Q {hx-44} {hy+8+40*dr:.0f} {hx-34} {hy+14+46*dr:.0f} Q {hx-26} {hy+8+40*dr:.0f} {hx-24} {hy+8} '
                         f'M{hx+18} {hy+10} Q {hx+16} {hy+10+70*dr:.0f} {hx+26} {hy+16+76*dr:.0f} Q {hx+36} {hy+10+70*dr:.0f} {hx+34} {hy+8}Z" '
                         f'fill="#a8581a" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>')
            L.append(pancake(hx - 6, hy + 6 * (1 - sq), -14, 1.18, sq, butter=True))
            if dr > 0:
                L.append(f'<path d="M{hx-60} {hy-14} Q {hx-6} {hy-30} {hx+50} {hy-20} Q {hx+20} {hy-6} {hx-60} {hy-14}Z" fill="#a8581a" stroke="{OL}" stroke-width="3" opacity="{dr:.2f}"/>')

    # ---- effects
    for k, (tf, b, fd, ap, tx) in enumerate(ROUNDS):
        lt = tf + fd
        before = landed_count(tf)
        top = NG - 157 - (before + b) * TH
        L.append(impact(tx, top + 30, seg(t, lt, lt + 0.22 + 0.1 * (b >= 16)), "#fff6a8"))
    L.append(symbol(NX0 + 20, NG - 320, "!", seg(t, 2.1, 2.7)))
    L.append(symbol(NX0 + 130, NG - 310, "!", seg(t, 4.1, 4.6)))
    L.append(symbol(NX0 + 10, NG - 330, "?", seg(t, 6.85, 7.7), "#3a7ad6"))
    L.append(symbol(NX0 - 10, 1080, "!", seg(t, 11.45, 12.05)))
    L.append(symbol(670, GY - 230, "!", seg(t, FALL0 + 0.05, FALL0 + 0.7)))
    if 11.3 <= t < 12.1:
        # sparkle as the pan stack magically rises
        L.append(star_twinkle(PAN_REST[0] + 70, PAN_REST[1] - 40 - 352 * eio(seg(t, 11.3, 12.1)), seg(t, 11.3, 12.1)))
    if 12.2 <= t < 13.3:
        L.append(f'<g opacity="0.85">{steam_puffs(GX0, GY - 140, t, 0.9)}</g>')
    if 17.6 <= t < DROP1:
        # grumpo anger marks
        L.append(f'<path d="M{770} {GY-60} l18 -8 l-6 18 M{786} {GY-44} l18 -8 l-6 18" stroke="#e8303a" stroke-width="6" fill="none" stroke-linecap="round"/>')
    L.append(impact(670, GY - 70, seg(t, DROP1, DROP1 + 0.2), "#fff6a8"))

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g></svg>')

    # ---- overlays
    val = count
    bt = last_land(t)
    step = sum(1 for r in ROUNDS if t >= r[0] + r[2])
    if t >= CRASH + 0.15:
        val, bt = 0, CRASH + 0.15
    if t >= DROP1:
        val, bt = 1, DROP1
    return overlay(svg, hook_title(t + 0.12, "How tall can", "THE STACK GO?"),
                   counter(t, val, "STACK", step, 6, bump_t=bt))


def build_sfx():
    sfx(0.0, "sizzle", 0.7)
    for k, (tf, b, fd, ap, tx) in enumerate(ROUNDS):
        sfx(tf - 0.05, "flap", 0.8 + 0.05 * k, 1.1 - 0.06 * k)
        sfx(tf, "whoosh", 0.5 + 0.06 * k, 1.4 - 0.1 * k)
        lt = tf + fd
        if b <= 2:
            sfx(lt, "pancake", 0.9, 1.1)
        else:
            for j in range(min(b, 8)):
                sfx(lt + j * 0.025, "pancake", 0.55, 0.9 + 0.05 * j)
            sfx(lt, "thud", 0.5 + 0.06 * k, 1.3 - 0.06 * k)
        sfx(lt + 0.02, "ding", 0.35, 1.6 + 0.08 * k)   # counter tick
        # cooking sizzle for next batch
        if k < 4:
            sfx(tf + 0.6, "sizzle", 0.6, 1.0 + 0.05 * k)
            sfx(tf + 0.6, "pop", 0.4, 1.3)
    sfx(1.3, "slide_down", 0.35, 1.6)
    sfx(1.6, "gulp", 0.5, 1.3)
    sfx(2.1, "alert", 0.6)
    sfx(2.25, "zip", 0.5, 1.3)
    sfx(4.1, "alert", 0.5, 1.15)
    sfx(4.3, "zip", 0.6, 1.1)
    for k in range(4):
        sfx(4.32 + k * 0.08, "tiptoe", 0.5, 1.1)
    sfx(5.15, "zip", 0.5, 0.95)
    sfx(STRAY_T0, "slide_up", 0.6, 1.2)
    sfx(STRAY_T1, "splat", 0.7, 1.4)
    sfx(STRAY_T1 + 0.02, "pancake", 0.6, 0.85)
    sfx(6.9, "suspense", 0.45, 1.2)
    sfx(9.4, "wobble", 0.7)
    for k in range(10):
        sfx(9.5 + k * 0.18, "tiptoe", 0.45, 1.0 + 0.1 * (k % 2))
    sfx(9.7, "laugh", 0.5, 0.85)
    for k in range(10):
        sfx(11.3 + k * 0.08, "pop", 0.35, 0.9 + 0.06 * k)
    sfx(11.45, "alert", 0.6, 0.9)
    sfx(12.0, "shaker", 0.4, 1.4)
    sfx(12.2, "strain", 0.8)
    sfx(12.25, "rumble", 0.35, 1.3)
    sfx(13.3, "boing", 0.6, 0.7)
    sfx(13.35, "slide_up", 0.6, 0.8)
    sfx(14.45, "squish", 0.8, 0.8)
    sfx(14.6, "wobble", 0.8, 0.9)
    sfx(15.3, "creak", 0.6, 0.9)
    for k in range(4):
        sfx(15.32 + k * 0.15, "tiptoe", 0.45, 0.8)
    sfx(15.75, "wobble", 0.8, 0.8)
    sfx(FALL0, "creak", 0.8, 0.7)
    sfx(FALL0 + 0.1, "gasp", 0.6)
    sfx(FALL0 + 0.15, "slide_down", 0.7, 0.8)
    sfx(CRASH, "splat", 1.0, 0.8)
    sfx(CRASH, "thud", 1.0, 0.8)
    for k in range(12):
        sfx(CRASH + 0.03 + k * 0.04, "pancake", 0.5, 0.8 + 0.04 * (k % 5))
    sfx(CRASH + 0.15, "blip_down", 0.6, 0.8)
    sfx(17.7, "grumble", 0.7)
    sfx(18.6, "gulp", 0.5, 1.1)
    sfx(19.25, "creak", 0.6, 1.5)
    sfx(DROP0, "slide_down", 0.5, 1.5)
    sfx(DROP1, "pancake", 1.0, 0.9)
    sfx(DROP1 + 0.02, "ding", 0.5, 2.0)
    sfx(20.4, "laugh", 0.6, 1.3)
    sfx(21.2, "grumble", 0.5, 0.9)
