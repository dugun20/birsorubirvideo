"""Grumpo & Nibbo — Episode 11: Hold the Door! (apartment elevator, misunderstanding + loop, 60 fps).

Front cut-away of a 4-storey apartment block: elevator shaft on the left, stairwell on the right.
Grumpo hops into the elevator — and his keyring (purple Grumpo tag) drops out behind him.
Nibbo finds the keys and runs to give them back, but Grumpo thinks Nibbo just wants to ride along:
  F1 lobby : Grumpo smashes CLOSE, the doors squeeze Nibbo thin and spit him out.
  F2       : Nibbo (who raced up the stairs) is already waiting — Grumpo inflates like a balloon to
             block the doorway, Nibbo bounces off into the stairwell, Grumpo deflates zooming around.
  F3       : the car opens "empty" — Grumpo is flattened against the ceiling; his sweat drop lands
             on Nibbo, he presses CLOSE just in time... THUD (he fell).
  F4       : nobody waiting. Grumpo struts to his own door — no keys! Exhausted Nibbo crawls out of
             the stairwell holding them. Grumpo blushes; Nibbo tosses the keys, Grumpo fumbles them,
             they skid into the gap under the elevator and fall all the way down the shaft (tink tink tink).
Twist ending: Nibbo was helping all along; Grumpo's own trick costs him the keys. Nibbo faints,
Grumpo sags under a tiny rain cloud.
"""
import math, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow, sky, cloud, hills
from hook import overlay, hook_title

W, H, FPS, DUR = 1080, 1920, 60, 21.0
GS = 0.92
GR = 130 * GS          # ~120
NR = 112
FH = 620
FL = {1: 2600, 2: 1980, 3: 1360, 4: 740, 5: 120}   # floor top y (5 = roof slab)
SH0, SH1 = 180, 600     # shaft
CAR0, CAR1, CARX = 200, 580, 390
OP0, OP1 = 220, 560     # door opening
CH = 430                # car outer height
PART = 860              # stairwell partition (left edge)
ST0, ST1 = 900, 1240    # stair flight x range
PIT = 2890
PANEL = (537, -165)     # close button relative to car floor
INK = "#1a0a2e"
GPURP = "#9466e0"

WALL = {1: ("#f1e2c4", "#e6d2ad", "#b89a6a"), 2: ("#cfeee0", "#bde3d1", "#6fae94"),
        3: ("#d6e6fb", "#c3d8f4", "#7a9cc8"), 4: ("#e6dbf8", "#d8c9f2", "#9a84c8")}

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
        s = math.sin(math.pi * k / d) * (1 - k / d)
        return 1 + a * s, 1 - a * s
    return 1.0, 1.0


def hop(t, t0, t1, x0, x1, h):
    p = seg(t, t0, t1)
    return lerp(x0, x1, p), -h * math.sin(math.pi * p), p


def arm(x0, y0, x1, y1, w=12, sag=20, col=INK):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    return f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


def hand(x, y, r=15, fill=GPURP):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{OL}" stroke-width="5"/>'


def sy_of(k):
    return FL[k] - 12


# ---------------------------------------------------------------- timings
T_PRESS1 = 1.80
T_POP = 2.38
T_LAND1 = 2.75
T_INFL0, T_INFL1 = 4.50, 4.80
T_BOING = 4.85
T_PRESS2 = 5.15
T_DEFL0, T_DEFL1 = 5.20, 5.70
T_DRIP0, T_DRIP1 = 8.22, 8.50
T_PRESS3 = 8.60
T_THUD = 9.30
T_TOSS = 14.90
T_CATCH = 15.30
T_FLOOR = 15.65
T_GAP = 15.95
G_FALL = 2600.0
T_PIT = T_GAP + math.sqrt(2 * (PIT - 10 - FL[4]) / G_FALL)
T_FAINT0, T_FAINT1 = 18.80, 19.10
T_SAG0, T_SAG1 = 19.30, 20.30
T_RAIN = 19.85

CAR_KEYS = [(0, FL[1]), (2.7, FL[1]), (3.8, FL[2]), (5.9, FL[2]), (6.9, FL[3]), (9.55, FL[3]), (10.55, FL[4])]
ARRIVALS = [3.8, 6.9, 10.55]
DEPARTS = [2.7, 5.9, 9.55]


def car_y(t):
    y = kf(t, CAR_KEYS)
    for a in ARRIVALS:
        if a <= t < a + 0.35:
            k = t - a
            y += -7 * math.sin(k * 28) * (1 - k / 0.35)
    if T_THUD <= t < T_THUD + 0.4:
        k = t - T_THUD
        y += 16 * math.sin(k * 30) * (1 - k / 0.4)
    return y


def car_floor(t):
    y = kf(t, CAR_KEYS)
    return min(FL.items(), key=lambda kv: abs(kv[1] - y))[0]


def door(t):
    """1 = open, 0 = closed."""
    if t < 1.9:
        d = 1.0
    elif t < 3.9:
        d = 1 - eio(seg(t, 1.9, 2.45))
        if t < T_POP:
            d = max(d, 78 / 340)
        else:
            d = min(d, (78 / 340) * (1 - seg(t, T_POP, T_POP + 0.06)))
    elif t < 5.35:
        d = eio(seg(t, 3.9, 4.3))
    elif t < 7.0:
        d = 1 - eio(seg(t, 5.35, 5.8))
    elif t < 8.65:
        d = eio(seg(t, 7.0, 7.4))
    elif t < 10.65:
        d = 1 - eio(seg(t, 8.65, 9.1))
    elif t < 12.4:
        d = eio(seg(t, 10.65, 11.05))
    else:
        d = 1 - eio(seg(t, 12.4, 12.85))
    return cl(d)


# ---------------------------------------------------------------- props
def keyring(x, y, rot=0.0, s=1.3):
    """hanging keyring; (x,y) = ring top (hold point)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<circle cx="0" cy="12" r="12" fill="none" stroke="{OL}" stroke-width="7"/>'
            f'<circle cx="0" cy="12" r="12" fill="none" stroke="#d9dee6" stroke-width="3"/>'
            # gold key
            f'<g transform="translate(-6 22) rotate(18)"><path d="M-3 0 h6 v34 l6 0 v6 l-6 0 v5 l4 0 v6 h-10z" fill="#f2c14e" stroke="{OL}" stroke-width="3.5" stroke-linejoin="round"/>'
            f'<circle cx="0" cy="-4" r="10" fill="#f2c14e" stroke="{OL}" stroke-width="3.5"/><circle cx="0" cy="-4" r="3.5" fill="{OL}"/></g>'
            # silver key
            f'<g transform="translate(6 22) rotate(-24)"><path d="M-3 0 h6 v30 l5 0 v5 l-5 0 v6 h-6z" fill="#cfd6de" stroke="{OL}" stroke-width="3.5" stroke-linejoin="round"/>'
            f'<rect x="-9" y="-14" width="18" height="16" rx="5" fill="#cfd6de" stroke="{OL}" stroke-width="3.5"/></g>'
            # purple Grumpo tag
            f'<g transform="translate(16 40)"><circle r="15" fill="{GPURP}" stroke="{OL}" stroke-width="3.5"/>'
            f'<path d="M-9 -4 l6 3 M9 -4 l-6 3" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>'
            f'<circle cx="-5" cy="3" r="2.4" fill="#fff"/><circle cx="5" cy="3" r="2.4" fill="#fff"/>'
            f'<path d="M-5 10 q5 -4 10 0" stroke="{INK}" stroke-width="2.5" fill="none" stroke-linecap="round"/></g>'
            '</g>')


def thought(x, y, p):
    if p <= 0 or p >= 1:
        return ""
    sc = eback(min(1, p * 5)) * (1 if p < 0.85 else (1 - p) / 0.15)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) scale({max(0.01, sc):.3f})">']
    o.append(f'<circle cx="-70" cy="120" r="12" fill="#fff" stroke="{OL}" stroke-width="5"/><circle cx="-40" cy="80" r="18" fill="#fff" stroke="{OL}" stroke-width="5"/>')
    pts = [(-70, 0, 52), (-20, -30, 60), (40, -22, 56), (78, 10, 44), (30, 34, 50), (-34, 32, 46)]
    o.append('<g stroke="#221c2e" stroke-width="10">' + "".join(f'<circle cx="{a}" cy="{b}" r="{r}" fill="#fff"/>' for a, b, r in pts) + '</g>')
    o.append("".join(f'<circle cx="{a}" cy="{b}" r="{r}" fill="#fff"/>' for a, b, r in pts))
    o.append(keyring(-14, -62, 0, 1.55))
    o.append('<path d="M-52 -46 L52 52 M52 -46 L-52 52" stroke="#e8303a" stroke-width="11" stroke-linecap="round" opacity="0.85"/>')
    o.append('</g>')
    return "".join(o)


def rain_cloud(x, y, t, p):
    if p <= 0:
        return ""
    sc = eback(min(1, p * 4))
    o = [f'<g transform="translate({x:.1f} {y:.1f}) scale({sc:.3f})">']
    for k in range(7):
        q = (t * 2.2 + k / 7) % 1
        dx = -60 + k * 20
        o.append(f'<path d="M{dx} {30 + q*150:.1f} q6 11 0 16 q-6 -5 0 -16z" fill="#9be6ff" stroke="#2a86cf" stroke-width="2.5" opacity="{1-q:.2f}"/>')
    pts = [(-50, 0, 36), (-10, -22, 44), (36, -10, 38), (64, 10, 26), (0, 14, 36), (-70, 16, 24)]
    o.append(f'<g stroke="{OL}" stroke-width="10">' + "".join(f'<circle cx="{a}" cy="{b}" r="{r}" fill="#8f96a6"/>' for a, b, r in pts) + '</g>')
    o.append("".join(f'<circle cx="{a}" cy="{b}" r="{r}" fill="#8f96a6"/>' for a, b, r in pts))
    o.append('<circle cx="-18" cy="-30" r="16" fill="#b4bac7"/><circle cx="28" cy="-16" r="10" fill="#b4bac7"/>')
    o.append('</g>')
    return "".join(o)


def sweat(x, y, s=1.0, op=1.0):
    return (f'<path d="M{x:.1f} {y:.1f} q{10*s:.1f} {16*s:.1f} 0 {24*s:.1f} q{-10*s:.1f} {-8*s:.1f} 0 {-24*s:.1f}z" '
            f'fill="#bfefff" stroke="#3a6a8a" stroke-width="3" opacity="{op:.2f}"/>')


def dust(x, y, p, s=1.0, d=1):
    if p <= 0 or p >= 1:
        return ""
    o = []
    for k in range(5):
        a = math.radians(180 + k * 10 if d > 0 else k * -10)
        dd = 30 + 130 * p
        o.append(f'<circle cx="{x + d*-dd*abs(math.cos(a))*s:.1f}" cy="{y - 20*p - k*6:.1f}" r="{(18 + 22*p)*s:.1f}" fill="#f4ecdc" stroke="#cdbf9f" stroke-width="4" opacity="{1-p:.2f}"/>')
    return "".join(o)


def stars_orbit(x, y, t, n=3, rx=80, ry=20):
    o = []
    for k in range(n):
        a = t * 7 + k * 2 * math.pi / n
        o.append(star_twinkle(x + rx * math.cos(a), y + ry * math.sin(a), 0.5))
    return "".join(o)


# ---------------------------------------------------------------- building
def flight(x0, y0, x1, y1, n=8):
    """stair flight from (x0,y0) (lower) to (x1,y1) (upper); x0<x1 or x0>x1."""
    d = 1 if x1 > x0 else -1
    run = abs(x1 - x0) / n
    rise = (y0 - y1) / n
    pts = [(x0, y0)]
    x, y = x0, y0
    for i in range(n):
        y -= rise
        pts.append((x, y))
        x += d * run
        pts.append((x, y))
    th = 46
    pts += [(x1, y1 + th + 10), (x0, y0 + th)]
    poly = " ".join(f"{a:.0f},{b:.0f}" for a, b in pts)
    o = [f'<polygon points="{poly}" fill="#cdc4b4" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>']
    x, y = x0, y0
    for i in range(n):
        y -= rise
        o.append(f'<path d="M{x:.0f} {y+5:.0f} h{d*run:.0f}" stroke="#e9e2d4" stroke-width="5"/>')
        x += d * run
    # handrail
    o.append(f'<path d="M{x0 + d*10:.0f} {y0-110:.0f} L{x1 - d*10:.0f} {y1-110:.0f}" stroke="{OL}" stroke-width="13" stroke-linecap="round"/>'
             f'<path d="M{x0 + d*10:.0f} {y0-110:.0f} L{x1 - d*10:.0f} {y1-110:.0f}" stroke="#c0773c" stroke-width="6" stroke-linecap="round"/>')
    for k in (0.15, 0.5, 0.85):
        px, py = lerp(x0, x1, k), lerp(y0, y1, k)
        o.append(f'<path d="M{px:.0f} {py-108:.0f} V{py - rise*0.5:.0f}" stroke="{OL}" stroke-width="5"/>')
    return "".join(o)


def window(x0, y0, w, h):
    return (f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="6" fill="none" stroke="{OL}" stroke-width="8"/>'
            f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="6" fill="none" stroke="#f7f3ea" stroke-width="3"/>'
            f'<path d="M{x0 + w/2} {y0} V{y0+h} M{x0} {y0+h/2} H{x0+w}" stroke="{OL}" stroke-width="7"/>'
            f'<path d="M{x0 + w/2} {y0} V{y0+h} M{x0} {y0+h/2} H{x0+w}" stroke="#f7f3ea" stroke-width="3"/>'
            f'<rect x="{x0-10}" y="{y0+h}" width="{w+20}" height="14" rx="4" fill="#f7f3ea" stroke="{OL}" stroke-width="5"/>'
            f'<path d="M{x0+14} {y0+16} l26 -0 M{x0+14} {y0+28} l14 0" stroke="#fff" stroke-width="5" opacity="0.7" stroke-linecap="round"/>')


def floor_back(k, t):
    """back wall of floor k (corridor part), with window hole."""
    Y = FL[k]
    top = FL[k + 1] + 40
    base, alt, dark = WALL[k]
    wx0, wy0, ww, wh = 30, Y - 440, 130, 220
    o = [f'<path d="M-200 {top} H{PART} V{Y} H-200Z M{wx0} {wy0} v{wh} h{ww} v{-wh}Z" fill="{base}" fill-rule="evenodd"/>']
    # wallpaper pattern
    if k == 1:
        for yy in range(top + 40, Y - 40, 90):
            o.append(f'<path d="M-200 {yy} H{PART}" stroke="{alt}" stroke-width="4"/>')
    elif k == 2:
        for xx in range(-180, PART, 70):
            o.append(f'<path d="M{xx} {top} V{Y - 40}" stroke="{alt}" stroke-width="14"/>')
    elif k == 3:
        for xx in range(-160, PART, 90):
            for yy in range(top + 50, Y - 60, 90):
                o.append(f'<circle cx="{xx + (45 if (yy // 90) % 2 else 0)}" cy="{yy}" r="9" fill="{alt}"/>')
    else:
        for xx in range(-160, PART, 80):
            for yy in range(top + 40, Y - 60, 80):
                o.append(f'<path d="M{xx} {yy-10} l10 10 l-10 10 l-10 -10z" fill="{alt}"/>')
    o.append(f'<path d="M{wx0} {wy0} v{wh} h{ww} v{-wh}Z" fill="none" stroke="{OL}" stroke-width="2"/>')
    o.append(window(wx0, wy0, ww, wh))
    # baseboard + floor band
    o.append(f'<rect x="-200" y="{Y-40}" width="{PART+200}" height="28" fill="{dark}" stroke="{OL}" stroke-width="4"/>')
    o.append(f'<rect x="-200" y="{Y-14}" width="{PART+200}" height="14" fill="#b98250"/>')
    # wall lamp
    o.append(f'<path d="M680 {Y-470} a40 40 0 0 1 80 0z" fill="#fff6c8" stroke="{OL}" stroke-width="5"/>'
             f'<ellipse cx="720" cy="{Y-470}" rx="120" ry="60" fill="#fff8d8" opacity="0.25"/>')
    return "".join(o)


def floor_props(k, t):
    Y = FL[k]
    o = []
    # call panel + indicator
    cf = car_floor(t)
    moving = any(d <= t < a for d, a in zip(DEPARTS, ARRIVALS))
    o.append(f'<rect x="604" y="{Y-372}" width="64" height="50" rx="8" fill="#2a2433" stroke="{OL}" stroke-width="5"/>')
    o.append(f'<text x="645" y="{Y-334}" font-family="DejaVu Sans" font-weight="bold" font-size="34" text-anchor="middle" fill="#ff6a3a">{cf}</text>')
    if moving or (cf == k and door(t) < 0.05 and t > 0.1):
        o.append(f'<path d="M614 {Y-336} l10 -18 l10 18z" fill="#7dff8a"/>')
    o.append(f'<rect x="614" y="{Y-290}" width="44" height="80" rx="10" fill="#c8ced6" stroke="{OL}" stroke-width="5"/>'
             f'<circle cx="636" cy="{Y-268}" r="10" fill="#f4f6f9" stroke="{OL}" stroke-width="3"/><path d="M630 {Y-265} l6 -8 l6 8" fill="none" stroke="{OL}" stroke-width="3"/>'
             f'<circle cx="636" cy="{Y-232}" r="10" fill="#f4f6f9" stroke="{OL}" stroke-width="3"/><path d="M630 {Y-235} l6 8 l6 -8" fill="none" stroke="{OL}" stroke-width="3"/>')
    if k == 1:
        # plant
        x = 775
        o.append(f'<g stroke="{OL}" stroke-width="5">'
                 f'<path d="M{x} {Y-130} q-70 -40 -80 -130 q60 30 80 120z" fill="#4f9e4c"/>'
                 f'<path d="M{x} {Y-130} q60 -60 50 -170 q-50 50 -50 160z" fill="#5aa957"/>'
                 f'<path d="M{x} {Y-130} q-10 -90 10 -200 q30 90 -10 190z" fill="#6dbb5f"/>'
                 f'<path d="M{x-46} {Y-140} h92 l-12 128 h-68z" fill="#e0764a"/></g>'
                 f'<path d="M{x-40} {Y-118} h80" stroke="#b3502c" stroke-width="6"/>')
        # mailboxes
        o.append(f'<rect x="210" y="{Y-560}" width="0" height="0"/>')
    elif k == 2:
        o.append(f'<rect x="700" y="{Y-430}" width="120" height="96" rx="4" fill="#ffb36b" stroke="{OL}" stroke-width="6"/>'
                 f'<circle cx="760" cy="{Y-370}" r="22" fill="#fff3b0"/><path d="M706 {Y-350} q30 -30 60 -6 q30 -20 48 4 v14 h-108z" fill="#6aa86a"/>'
                 f'<rect x="700" y="{Y-430}" width="120" height="96" rx="4" fill="none" stroke="#8a5a2a" stroke-width="5"/>')
    elif k == 3:
        a1 = t * 0.5
        a2 = t * 6
        o.append(f'<circle cx="760" cy="{Y-410}" r="44" fill="#fffdf6" stroke="{OL}" stroke-width="7"/>'
                 f'<path d="M760 {Y-410} l{22*math.sin(a1):.1f} {-22*math.cos(a1):.1f}" stroke="{OL}" stroke-width="6" stroke-linecap="round"/>'
                 f'<path d="M760 {Y-410} l{32*math.sin(a2):.1f} {-32*math.cos(a2):.1f}" stroke="#e8303a" stroke-width="4" stroke-linecap="round"/>'
                 f'<circle cx="760" cy="{Y-410}" r="5" fill="{OL}"/>')
    elif k == 4:
        # Grumpo's own door
        o.append(f'<rect x="652" y="{Y-336}" width="176" height="324" rx="8" fill="#6a41ba" stroke="{OL}" stroke-width="7"/>'
                 f'<rect x="674" y="{Y-312}" width="132" height="120" rx="8" fill="#7c52cc" stroke="{OL}" stroke-width="4"/>'
                 f'<rect x="674" y="{Y-176}" width="132" height="140" rx="8" fill="#7c52cc" stroke="{OL}" stroke-width="4"/>'
                 f'<circle cx="806" cy="{Y-190}" r="11" fill="#f2c14e" stroke="{OL}" stroke-width="4"/>'
                 f'<rect x="798" y="{Y-170}" width="14" height="26" rx="5" fill="#f2c14e" stroke="{OL}" stroke-width="3.5"/><path d="M805 {Y-163} v10" stroke="{OL}" stroke-width="4"/>'
                 f'<g transform="translate(740 {Y-262})"><circle r="30" fill="{GPURP}" stroke="{OL}" stroke-width="5"/>'
                 f'<path d="M-19 -9 l13 6 M19 -9 l-13 6" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
                 f'<circle cx="-10" cy="5" r="5" fill="#fff"/><circle cx="10" cy="5" r="5" fill="#fff"/>'
                 f'<path d="M-10 19 q10 -7 20 0" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round"/></g>'
                 f'<rect x="644" y="{Y-22}" width="192" height="14" rx="5" fill="#5b2fa6" stroke="{OL}" stroke-width="4"/>')
    return "".join(o)


def stairwell(k):
    Y = FL[k]
    top = FL[k + 1] + 40
    o = [f'<rect x="{PART}" y="{top}" width="{1400-PART}" height="{Y-top}" fill="#e4ddd2"/>']
    for yy in range(top + 60, Y, 60):
        off = 0 if (yy // 60) % 2 else 50
        for xx in range(PART + off, 1400, 100):
            o.append(f'<rect x="{xx}" y="{yy-56}" width="96" height="56" fill="none" stroke="#d3cabd" stroke-width="3"/>')
    o.append(f'<text x="1120" y="{Y-330}" font-family="Fredoka" font-weight="700" font-size="180" text-anchor="middle" fill="#cfc4b3">{k}</text>')
    # mid landing (right) + floor landing (left)
    o.append(f'<rect x="{ST1-20}" y="{Y-FH/2:.0f}" width="200" height="34" fill="#bfb5a4" stroke="{OL}" stroke-width="5"/>')
    o.append(flight(ST0, Y, ST1, Y - FH / 2))
    o.append(flight(ST1, Y - FH / 2, ST0, Y - FH))
    return "".join(o)


def partition(k):
    Y = FL[k]
    top = FL[k + 1] + 40
    o = [f'<rect x="{PART}" y="{top}" width="34" height="{Y-310-top}" fill="#bdb3a3" stroke="{OL}" stroke-width="5"/>',
         f'<rect x="{PART-8}" y="{Y-318}" width="50" height="16" rx="4" fill="#a89c88" stroke="{OL}" stroke-width="4"/>',
         # exit sign
         f'<rect x="{PART-28}" y="{Y-384}" width="92" height="50" rx="8" fill="#2fb36a" stroke="{OL}" stroke-width="5"/>',
         f'<path d="M{PART-12} {Y-346} h12 v-10 h12 v-10 h12 v-10" fill="none" stroke="#fff" stroke-width="5" stroke-linejoin="round"/>',
         f'<path d="M{PART+30} {Y-359} h20 l-7 -7 m7 7 l-7 7" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>']
    return "".join(o)


def slab(k):
    Y = FL[k]
    o = [f'<rect x="-300" y="{Y}" width="1800" height="40" fill="#c6bdb0" stroke="{OL}" stroke-width="6"/>']
    for xx in range(-280, 1500, 46):
        o.append(f'<circle cx="{xx + (k*13) % 23}" cy="{Y + 14 + (xx // 46 % 3) * 6}" r="3" fill="#a59b8c"/>')
    # elevator sill
    o.append(f'<rect x="{SH0+10}" y="{Y-6}" width="{SH1-SH0-20}" height="12" rx="3" fill="#9aa3b0" stroke="{OL}" stroke-width="4"/>')
    if k <= 4:
        o.append(f'<rect x="{ST0-30}" y="{Y-4}" width="0" height="0"/>')
    return "".join(o)


def shaft():
    o = [f'<rect x="{SH0}" y="{FL[5]}" width="{SH1-SH0}" height="{PIT-FL[5]+12}" fill="#2f2940"/>',
         f'<rect x="{SH0}" y="{FL[5]}" width="40" height="{PIT-FL[5]}" fill="#262035"/>',
         f'<rect x="{SH1-40}" y="{FL[5]}" width="40" height="{PIT-FL[5]}" fill="#3a3350"/>']
    for x in (SH0 + 14, SH1 - 14):
        o.append(f'<path d="M{x} {FL[5]} V{PIT}" stroke="#141020" stroke-width="12"/><path d="M{x} {FL[5]} V{PIT}" stroke="#7a7690" stroke-width="5"/>')
        for y in range(FL[5] + 80, PIT, 160):
            o.append(f'<circle cx="{x}" cy="{y}" r="6" fill="#9a96b0" stroke="#141020" stroke-width="3"/>')
    # pit: floor + buffers
    o.append(f'<rect x="{SH0}" y="{PIT}" width="{SH1-SH0}" height="40" fill="#8d8f9c" stroke="{OL}" stroke-width="5"/>')
    for bx in (265, 515):
        o.append(f'<rect x="{bx-26}" y="{PIT-14}" width="52" height="16" rx="3" fill="#5b6b7c" stroke="{OL}" stroke-width="4"/>'
                 f'<path d="M{bx-16} {PIT-14} l32 -12 l-32 -12 l32 -12 l-32 -12 l32 -12" fill="none" stroke="#d5dbe3" stroke-width="6"/>'
                 f'<rect x="{bx-22}" y="{PIT-98}" width="44" height="22" rx="8" fill="#2a2a30" stroke="{OL}" stroke-width="4"/>')
    return "".join(o)


def basement():
    o = [f'<rect x="-400" y="{FL[1]+40}" width="2200" height="1500" fill="url(#dirt2)"/>']
    rnd = random.Random(11)
    for k in range(60):
        x = rnd.uniform(-380, 1700)
        y = rnd.uniform(FL[1] + 80, FL[1] + 1300)
        o.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rnd.uniform(7,16):.0f}" ry="{rnd.uniform(4,9):.0f}" fill="#6e4429" opacity="0.6"/>')
    for (x, y, rx, ry) in [(860, 2820, 54, 32), (1180, 2980, 70, 40), (40, 2900, 40, 26)]:
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#8d8f9c" stroke="{OL}" stroke-width="5"/><ellipse cx="{x-rx*0.3:.0f}" cy="{y-ry*0.35:.0f}" rx="{rx*0.35:.0f}" ry="{ry*0.25:.0f}" fill="#c3c6d0"/>')
    o.append(f'<path d="M700 {FL[1]+40} V2760 a40 40 0 0 0 40 40 H1500" fill="none" stroke="{OL}" stroke-width="60"/>'
             f'<path d="M700 {FL[1]+40} V2760 a40 40 0 0 0 40 40 H1500" fill="none" stroke="#aab4c0" stroke-width="46"/>')
    return "".join(o)


def car(ctx, yb, d, inside, t, press=0.0):
    """elevator car; yb = car floor y. inside = svg drawn in the cabin (behind doors)."""
    top = yb - CH
    o = []
    # cables
    o.append(f'<path d="M370 {FL[5]} V{top} M410 {FL[5]} V{top}" stroke="#111" stroke-width="7"/>'
             f'<path d="M370 {FL[5]} V{top} M410 {FL[5]} V{top}" stroke="#8a8aa0" stroke-width="2.5"/>')
    o.append(f'<rect x="330" y="{top-34}" width="120" height="36" rx="6" fill="#5b6b7c" stroke="{OL}" stroke-width="5"/>')
    # body
    o.append(f'<rect x="{CAR0}" y="{top}" width="{CAR1-CAR0}" height="{CH+22}" rx="10" fill="#8f99a8" stroke="{OL}" stroke-width="7"/>')
    # cabin
    o.append(f'<rect x="{OP0}" y="{top+30}" width="{OP1-OP0}" height="{CH-30}" fill="#f3e2c2"/>')
    for xx in range(OP0 + 40, OP1, 60):
        o.append(f'<path d="M{xx} {top+30} V{yb}" stroke="#e5cfa6" stroke-width="4"/>')
    o.append(f'<rect x="{OP0}" y="{top+30}" width="{OP1-OP0}" height="26" fill="#fffbe6"/>'
             f'<rect x="{OP0}" y="{top+56}" width="{OP1-OP0}" height="10" fill="#e8d6b0"/>')
    o.append(f'<path d="M{OP0+10} {yb-150} H{OP1-10}" stroke="{OL}" stroke-width="12" stroke-linecap="round"/><path d="M{OP0+10} {yb-150} H{OP1-10}" stroke="#d9dee6" stroke-width="5" stroke-linecap="round"/>')
    o.append(f'<rect x="{OP0}" y="{yb-16}" width="{OP1-OP0}" height="16" fill="#9b8a72"/>')
    # inner panel
    px, py = PANEL[0], yb + PANEL[1]
    o.append(f'<rect x="{px-24}" y="{py-112}" width="48" height="146" rx="8" fill="#c8ced6" stroke="{OL}" stroke-width="4"/>')
    for j in range(4):
        o.append(f'<circle cx="{px}" cy="{py-92 + j*24}" r="8" fill="#f4f6f9" stroke="{OL}" stroke-width="3"/>')
    glow = press
    bc = mix_hex("#f4f6f9", "#ffd23a", glow)
    o.append(f'<circle cx="{px}" cy="{py+10}" r="{17 - 3*glow:.1f}" fill="{bc}" stroke="{OL}" stroke-width="4"/>'
             f'<path d="M{px-12} {py+3} l7 7 l-7 7z M{px+12} {py+3} l-7 7 l7 7z" fill="{OL}"/><path d="M{px} {py+1} v18" stroke="{OL}" stroke-width="2.5"/>')
    if glow > 0.05:
        o.append(f'<circle cx="{px}" cy="{py+10}" r="{30*glow:.1f}" fill="#fff6a8" opacity="{0.5*glow:.2f}"/>')
    o.append(inside)
    # doors
    cid = ctx.uid("dr")
    ctx.defs.append(f'<clipPath id="{cid}"><rect x="{OP0}" y="{top+30}" width="{OP1-OP0}" height="{CH-30}"/></clipPath>')
    half = (OP1 - OP0) / 2
    sl = half * d
    dd = []
    for side in (-1, 1):
        if side < 0:
            x0 = OP0 - sl
        else:
            x0 = CARX + sl
        dd.append(f'<rect x="{x0:.1f}" y="{top+30}" width="{half:.1f}" height="{CH-30}" fill="#b9c2cd" stroke="{OL}" stroke-width="5"/>'
                  f'<rect x="{x0 + (half*0.18 if side < 0 else half*0.58):.1f}" y="{top+50}" width="{half*0.24:.1f}" height="{CH-70}" fill="#d8dee6" opacity="0.8"/>'
                  f'<path d="M{x0 + (half - 6 if side < 0 else 6):.1f} {top+30} V{yb}" stroke="#8f99a8" stroke-width="4"/>')
    o.append(f'<g clip-path="url(#{cid})">{"".join(dd)}</g>')
    # frame
    o.append(f'<rect x="{OP0}" y="{top+30}" width="{OP1-OP0}" height="{CH-30}" fill="none" stroke="{OL}" stroke-width="8"/>')
    o.append(f'<rect x="{CAR0+8}" y="{top+6}" width="{CAR1-CAR0-16}" height="18" rx="5" fill="#a9b3c0" stroke="{OL}" stroke-width="4"/>')
    o.append(f'<path d="M{CAR0+18} {top+12} h80" stroke="#fff" stroke-width="5" opacity="0.6" stroke-linecap="round"/>')
    return "".join(o)


# ---------------------------------------------------------------- Nibbo path on stairs
def stair_path(k, x_start, x_end):
    Y = FL[k]
    return [(x_start, Y), (ST0, Y), (ST1, Y - FH / 2), (ST0, Y - FH), (x_end, Y - FH)]


def along(pts, p):
    segs = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    tot = sum(segs)
    d = p * tot
    for (a, b), L in zip(zip(pts, pts[1:]), segs):
        if d <= L or L == segs[-1] and (a, b) == (pts[-2], pts[-1]):
            q = d / L if L > 0 else 0
            q = cl(q)
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            return lerp(a[0], b[0], q), lerp(a[1], b[1], q), ang
        d -= L
    a, b = pts[-2], pts[-1]
    return b[0], b[1], 0


# ---------------------------------------------------------------- characters
def nibbo_state(t):
    """returns dict or None. y = contact (bottom) point; draw center = y - NR*sy."""
    n = dict(x=0, b=sy_of(1), rot=0, sx=1, sy=1, expr="happy", keys=True, vis=True, speed=0, sweat=0)
    Y1, Y2, Y3, Y4 = sy_of(1), sy_of(2), sy_of(3), sy_of(4)
    if t < 0.75:
        n["vis"] = False
        return n
    if t < 1.15:
        n["keys"] = False
        x, dy, p = hop(t, 0.6, 0.92, -200, 25, 120)
        n.update(x=x, b=Y1 + dy, rot=10 * math.sin(math.pi * p))
        if t >= 0.92:
            n["sx"], n["sy"] = squash(t, 0.92, 0.22, 0.2)
            n["expr"] = "wow"
        return n
    if t < 1.45:
        n["keys"] = t >= 1.33
        x, dy, p = hop(t, 1.15, 1.33, 25, 150, 60)
        n.update(x=x, b=Y1 + dy, expr="happy")
        if t >= 1.33:
            n["sx"], n["sy"] = squash(t, 1.33, 0.12, 0.2)
        return n
    if t < 2.2:
        if t < 1.95:
            x, dy, p = hop(t, 1.5, 1.75, 150, 175, 50)
        else:
            x, dy, p = hop(t, 1.95, 2.2, 175, CARX, 90)
        n.update(x=x, b=Y1 + dy, expr="happy")
        return n
    if t < T_POP:
        gap = 340 * door(t)
        sx = cl(gap / (2 * NR), 0.35, 1)
        n.update(x=CARX, b=Y1, sx=sx, sy=min(1.55, 1 / math.sqrt(sx)), expr="wow" if sx > 0.6 else "nervous")
        return n
    if t < T_LAND1:
        p = seg(t, T_POP, T_LAND1)
        n.update(x=lerp(CARX, 210, p), b=Y1 - 230 * math.sin(math.pi * p), rot=-540 * p, expr="dizzy")
        if p < 0.15:
            n["sx"], n["sy"] = lerp(0.4, 1, p / 0.15), lerp(1.5, 1, p / 0.15)
        return n
    if t < 3.1:
        n.update(x=210, b=Y1, expr="dizzy" if t < 2.98 else "happy")
        n["sx"], n["sy"] = squash(t, T_LAND1, 0.3, 0.3)
        if 2.98 <= t < 3.1:
            n["rot"] = 12 * math.sin((t - 2.98) * 50)
        return n
    if t < 3.8:
        p = eio(seg(t, 3.1, 3.78))
        pts = [(210, FL[1])] + stair_path(1, 700, 780)[1:]
        x, y, ang = along(pts, p)
        n.update(x=x, b=y - 12, expr="joy", speed=1, rot=8)
        return n
    # ----- floor 2
    if t < 4.55:
        n.update(x=780, b=Y2, expr="nervous", sweat=1)
        br = 0.05 * math.sin(t * 26)
        n["sx"], n["sy"] = 1 - br * 0.5, 1 + br
        if t < 3.9:
            n["sx"], n["sy"] = squash(t, 3.78, 0.25, 0.25)
        if 4.32 <= t:
            n["rot"] = -14 * math.sin(math.pi * seg(t, 4.32, 4.55))
            n["expr"] = "happy"
        return n
    if t < T_BOING:
        x, dy, p = hop(t, 4.55, T_BOING, 780, 692, 90)
        n.update(x=x, b=Y2 + dy, expr="happy")
        return n
    if t < 5.3:
        p = seg(t, T_BOING, 5.3)
        n.update(x=lerp(692, 1180, eout(p)), b=Y2 - 70 * math.sin(math.pi * p), rot=720 * p, expr="wow")
        if p < 0.12:
            n["sx"], n["sy"] = 0.7, 1.25
        return n
    if t < 5.95:
        n["vis"] = False
        return n
    if t < 6.72:
        p = eio(seg(t, 5.95, 6.7))
        pts = [(1000, FL[2] - (1000 - ST0) * (FH / 2) / (ST1 - ST0)), (ST1, FL[2] - FH / 2), (ST0, FL[3]), (740, FL[3])]
        x, y, ang = along(pts, p)
        n.update(x=x, b=y - 12, expr="joy", speed=1, rot=-8)
        return n
    # ----- floor 3
    if t < 7.9:
        n.update(x=740, b=Y3, expr="happy", sweat=0.6)
        n["sx"], n["sy"] = squash(t, 6.72, 0.25, 0.25)
        if t >= 7.42:
            n["expr"] = "wow"
        return n
    if t < 8.2:
        x, dy, p = hop(t, 7.9, 8.2, 740, 565, 60)
        n.update(x=x, b=Y3 + dy, expr="happy", rot=-10 * p)
        return n
    if t < 8.65:
        n.update(x=565, b=Y3, expr="happy", rot=-10)
        if t >= T_DRIP1:
            n["sx"], n["sy"] = squash(t, T_DRIP1, 0.25, 0.2)
            n["expr"] = "wow"
            n["sy"] *= 1 + 0.06 * seg(t, T_DRIP1 + 0.05, 8.65)
        return n
    if t < 8.85:
        x, dy, p = hop(t, 8.65, 8.85, 565, 700, 70)
        n.update(x=x, b=Y3 + dy, expr="wow")
        return n
    if t < 9.62:
        n.update(x=700, b=Y3, expr="wow" if t < 9.5 else "happy")
        if T_THUD <= t < T_THUD + 0.2:
            n["b"] = Y3 - 60 * math.sin(math.pi * (t - T_THUD) / 0.2)
        return n
    if t < 10.55:
        if t < 9.85:
            p = eio(seg(t, 9.62, 9.85))
            n.update(x=lerp(700, ST0 + 10, p), b=Y3, expr="happy", speed=1)
        else:
            p = 0.35 * seg(t, 9.85, 10.55)
            x = lerp(ST0, ST1, p)
            y = lerp(FL[3], FL[3] - FH / 2, p)
            n.update(x=x + 10, b=y - 6, expr="nervous", sx=1.2, sy=0.72, rot=-30, sweat=1)
            n["x"] += 3 * math.sin(t * 30)
        return n
    if t < 13.4:
        n["vis"] = False
        return n
    # ----- floor 4
    if t < 14.4:
        x = lerp(1070, 905, eout(seg(t, 13.4, 14.0)))
        n.update(x=x + 4 * math.sin(t * 25) * (t < 14.0), b=Y4, expr="nervous", sx=1.22, sy=0.7, sweat=1)
        return n
    if t < T_TOSS + 0.05:
        p = eback(seg(t, 14.4, 14.6))
        n.update(x=905, b=Y4, sx=lerp(1.22, 1, p), sy=lerp(0.7, 1, p), expr="happy", sweat=0.5)
        if t >= 14.75:
            q = seg(t, 14.75, T_TOSS + 0.05)
            n["rot"] = -22 * math.sin(math.pi * q * 1.2)
        n["keys"] = t < T_TOSS
        return n
    n["keys"] = False
    if t < T_FAINT0:
        n.update(x=905, b=Y4, expr="happy" if t < 15.5 else "wow")
        if t >= 18.15:
            n["expr"] = "nervous"
            n["b"] = Y4 - 10 * abs(math.sin((t - 18.15) * 9))
        return n
    p = seg(t, T_FAINT0, T_FAINT1)
    n.update(x=905 + 40 * eio(p), b=Y4, rot=95 * ein(p), expr="dizzy")
    if t >= T_FAINT1:
        n["sx"], n["sy"] = squash(t, T_FAINT1, 0.3, 0.25)
    return n


def grumpo_state(t):
    g = dict(x=CARX, b=sy_of(1), inf=1.0, rot=0, sx=1, sy=1, expr="smug", look=(0, 0), red=0.0, layer="in",
             vis=True, arm=None, blush=0.0, stars=False, sweat=0)
    Y1, Y2, Y3, Y4 = sy_of(1), sy_of(2), sy_of(3), sy_of(4)
    yb = car_y(t) - 12
    if t < 0.45:
        x, dy, p = hop(t, -0.12, 0.45, 100, CARX, 150)
        g.update(x=x, b=Y1 + dy, look=(1, 0), rot=8 * math.sin(math.pi * p))
        return g
    g["b"] = yb
    if t < 3.9:
        g["sx"], g["sy"] = squash(t, 0.45, 0.3, 0.2)
        g["look"] = (0.3, 0)
        if 1.38 <= t < 1.6:
            g.update(expr="suspicious", look=(-1, 0.2))
        elif t >= 1.6:
            g.update(expr="smug", look=(-1, 0.1))
        if 1.6 <= t < 2.12:
            reach = eout(seg(t, 1.6, T_PRESS1)) * (1 - eio(seg(t, 1.95, 2.12)))
            g["arm"] = reach
        if 2.2 <= t:
            g["sy"] *= 1 + 0.03 * math.sin(t * 30)
        return g
    if t < 7.0:
        if t < 4.3:
            g.update(expr="smug", look=(-0.6, 0))
        elif t < T_INFL0:
            g.update(expr="shock", look=(1, 0))
        else:
            g.update(expr="angry", look=(1, 0.1))
        inf = 1 + 0.55 * eback(seg(t, T_INFL0, T_INFL1))
        if t >= T_DEFL0:
            p = seg(t, T_DEFL0, T_DEFL1)
            inf = 1 + 0.55 * (1 - eio(p))
            g["expr"] = "shock"
            if p < 1:
                g["x"] = CARX + 55 * math.sin(t * 41) * (1 - p)
                g["b"] = yb - 120 * abs(math.sin(t * 23)) * (1 - p)
                g["rot"] = 720 * eio(p)
        if T_INFL0 <= t < T_DEFL0:
            g["red"] = 0.25
            if t >= 4.95:
                g["expr"] = "smug"
        g["inf"] = inf
        if T_BOING <= t < T_BOING + 0.25:
            g["sx"], g["sy"] = squash(t, T_BOING, 0.25, -0.1)
        if 5.0 <= t < T_DEFL0:
            g["arm"] = math.sin(math.pi * seg(t, 5.02, T_DEFL0))
        return g
    if t < 9.3:
        # flattened against the ceiling
        top = car_y(t) - CH + 30
        g.update(sx=1.28, sy=0.6, expr="suspicious", look=(0.8, 1), sweat=1)
        g["b"] = top + 2 * GR * 0.6 + 2
        g["x"] = CARX + 3 * math.sin(t * 20)
        if 8.42 <= t < 8.85:
            g["arm"] = ("ceil", math.sin(math.pi * seg(t, 8.42, 8.85)))
        return g
    if t < 10.65:
        g.update(expr="angry", look=(0, 0))
        return g
    if t < 11.85:
        g.update(expr="grumpy", look=(0, 0), stars=t < 11.25)
        if t >= 11.05:
            p = eio(seg(t, 11.05, 11.25))
            g["x"] = lerp(CARX, 465, p)
            g["rot"] = -8 * p
            g["expr"] = "suspicious"
            g["look"] = (-1, 0) if t < 11.42 else (1, 0)
        if t >= 11.72:
            g.update(expr="smug", look=(1, 0))
        return g
    g["layer"] = "out"
    if t < 12.3:
        x, dy, p = hop(t, 11.85, 12.3, 465, 720, 140)
        g.update(x=x, b=Y4 + dy, expr="smug", look=(1, 0))
        return g
    g.update(x=720, b=Y4)
    if t < 13.0:
        g["sx"], g["sy"] = squash(t, 12.3, 0.3, 0.2)
        if t >= 12.5:
            g.update(expr="suspicious", look=(0, 1))
            g["x"] += 10 * math.sin(t * 45)
            g["arm"] = ("pat", (t - 12.5) * 12)
        return g
    if t < 14.0:
        g.update(expr="shock", look=(0, 0.2))
        return g
    if t < 15.1:
        g.update(expr="shock", look=(1, 0.1))
        b = eio(seg(t, 14.3, 14.7))
        g["blush"] = b
        g["red"] = 0.35 * b
        g["sx"] = g["sy"] = 1 - 0.07 * b
        return g
    if t < 15.95:
        g.update(expr="shock", red=0.35, blush=1, sx=0.93, sy=0.93)
        g["look"] = (1, -0.6) if t < T_CATCH else kf(t, [(T_CATCH, (0, -1)), (T_FLOOR, (-1, 0.6)), (15.95, (-1, 1))])
        if t < 15.55:
            g["arm"] = ("catch", eout(seg(t, 15.08, T_CATCH)), seg(t, T_CATCH, 15.55))
        return g
    if t < T_SAG0:
        g.update(expr="shock", red=0.45, blush=1, look=(-1, 0.9))
        if t >= 18.1:
            j = math.sin(t * 61) * math.sin(t * 7.3)
            g["look"] = (-1 + 0.25 * j, 0.9)
            if int(t * 7) % 3 == 0:
                g["sx"], g["sy"] = 1.03, 0.97
        return g
    p = eio(seg(t, T_SAG0, T_SAG1))
    g.update(expr="grumpy", red=lerp(0.45, 0.1, p), blush=1 - p, look=(0, 1), sx=lerp(1, 1.16, p), sy=lerp(1, 0.78, p))
    return g


def draw_grumpo(ctx, g, t):
    s = GS * g["inf"]
    r = 130 * s * g["sy"]
    cx, cy = g["x"], g["b"] - r
    o = []
    o.append(grumpo(ctx, cx, cy, s, g["expr"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"], False, 0, None, 0, t))
    if g["blush"] > 0.01:
        o.append(f'<g opacity="{0.8*g["blush"]:.2f}"><ellipse cx="{cx-70*s*g["sx"]:.1f}" cy="{cy+52*s*g["sy"]:.1f}" rx="{24*s:.1f}" ry="{11*s:.1f}" fill="#ff5f8a"/>'
                 f'<ellipse cx="{cx+70*s*g["sx"]:.1f}" cy="{cy+52*s*g["sy"]:.1f}" rx="{24*s:.1f}" ry="{11*s:.1f}" fill="#ff5f8a"/>'
                 f'<path d="M{cx-86*s:.1f} {cy+50*s:.1f} l10 -8 M{cx-70*s:.1f} {cy+50*s:.1f} l10 -8 M{cx+58*s:.1f} {cy+50*s:.1f} l10 -8 M{cx+74*s:.1f} {cy+50*s:.1f} l10 -8" stroke="#c8306a" stroke-width="3" stroke-linecap="round"/></g>')
    if g["sweat"]:
        o.append(sweat(cx + 112 * s * g["sx"], cy - 70 * s, 1.4))
    a = g["arm"]
    if a is not None:
        if isinstance(a, float) or isinstance(a, int):
            sx0, sy0 = cx + 100 * s, cy + 40 * s
            ex, ey = lerp(sx0 + 10, PANEL[0] - 4, a), lerp(sy0, car_y(t) + PANEL[1] + 10, a)
            o.append(arm(sx0, sy0, ex, ey, 13, 10) + hand(ex, ey, 16))
        elif a[0] == "ceil":
            k = a[1]
            sx0, sy0 = cx + 120, cy + 20
            ex, ey = lerp(sx0, PANEL[0] - 2, k), lerp(sy0 + 20, car_y(t) + PANEL[1] + 10, k)
            o.append(arm(sx0, sy0, ex, ey, 13, -10) + hand(ex, ey, 16))
        elif a[0] == "pat":
            ph = a[1]
            for side in (-1, 1):
                sx0, sy0 = cx + side * 112 * s, cy + 30 * s
                ex = sx0 + side * 18
                ey = sy0 + 40 + 18 * math.sin(ph + side)
                o.append(arm(sx0, sy0, ex, ey, 12, 0) + hand(ex, ey, 14))
        elif a[0] == "catch":
            k, f = a[1], a[2]
            sx0, sy0 = cx + 100 * s, cy - 10 * s
            ex, ey = lerp(sx0 + 10, 830, k), lerp(sy0, FL[4] - 230, k)
            ex += 16 * math.sin(f * 40) * (f > 0) * (1 - f)
            ey += 10 * math.cos(f * 40) * (f > 0) * (1 - f)
            o.append(arm(sx0, sy0, ex, ey, 13, 14) + hand(ex, ey, 16))
    if g["stars"]:
        o.append(stars_orbit(cx, cy - 120 * s, t, 3, 90, 18))
    return "".join(o), (cx, cy, s)


def draw_nibbo(ctx, n, t):
    if not n["vis"]:
        return "", None
    cx, cy = n["x"], n["b"] - NR * n["sy"]
    o = []
    if n["speed"]:
        o.append(speed_lines(cx - 60, cy, 0, 0.8))
        o.append(speed_lines(cx - 40, cy + 40, 0, 0.5))
    o.append(bloop(ctx, cx, cy, NR, n["expr"], rot=n["rot"], sx=n["sx"], sy=n["sy"]))
    if n["keys"]:
        a = math.radians(n["rot"])
        mx, my = 0, 40 * n["sy"]
        kx = cx + mx * math.cos(a) - my * math.sin(a)
        ky = cy + mx * math.sin(a) + my * math.cos(a)
        sw = 14 * math.sin(t * 9) + (25 if n["speed"] else 0) * math.sin(t * 20)
        o.append(f'<rect x="{kx-14:.1f}" y="{ky-6:.1f}" width="28" height="10" rx="5" fill="#7a2a1a"/>')
        o.append(keyring(kx, ky - 6, sw, 1.3))
    if n["sweat"]:
        for k in range(2):
            q = (t * 1.6 + k * 0.5) % 1
            o.append(sweat(cx + (60 + 30 * q) * (1 if k else -1), cy - 90 + q * 60, 1.1, n["sweat"] * (1 - q)))
    return "".join(o), (cx, cy)


def keys_state(t, n, g):
    """(layer, x, y, rot) ; layer: 'front' | 'shaft' | None (in mouth handled by nibbo)."""
    Y1 = sy_of(1)
    if t < 0.1:
        return None
    if t < 0.55:
        p = seg(t, 0.1, 0.4)
        x = lerp(210, 155, p)
        y = lerp(Y1 - 200, Y1 - 20, p) - 110 * math.sin(math.pi * p)
        q = 0
        if t >= 0.4:
            q = seg(t, 0.4, 0.55)
            y = Y1 - 20 - 22 * math.sin(math.pi * q)
            x = 155
        return ("front", x, y, -630 * p if t < 0.4 else -90 + 20 * math.sin(math.pi * q))
    if t < 1.33:
        return ("front", 155, Y1 - 20, -90)
    if t < T_TOSS:
        return None
    Y4 = sy_of(4)
    if t < T_CATCH:
        p = seg(t, T_TOSS, T_CATCH)
        return ("front", lerp(905, 830, p), lerp(Y4 - 90, Y4 - 250, p) - 200 * math.sin(math.pi * p), -500 * p)
    if t < T_FLOOR:
        p = seg(t, T_CATCH, T_FLOOR)
        return ("front", lerp(830, 560, p), lerp(Y4 - 250, Y4 - 62, p) - 210 * math.sin(math.pi * p), -500 - 700 * p)
    if t < T_GAP:
        p = eout(seg(t, T_FLOOR, T_GAP))
        return ("front", lerp(560, 420, p), Y4 - 62, 90 + 360 * p)
    if t < T_PIT:
        k = t - T_GAP
        y = FL[4] - 50 + 0.5 * G_FALL * k * k
        return ("shaft", 420 + 22 * math.sin(k * 14), y, 90 + 800 * k)
    k = t - T_PIT
    return ("shaft", 420, PIT - 66 - 26 * abs(math.sin(k * 14)) * max(0, 1 - k / 0.35), 80)


# ---------------------------------------------------------------- camera
CY = 290
CF = {1: (440, FL[1] - CY, 1.45), 2: (520, FL[2] - CY, 1.45), 3: (510, FL[3] - CY, 1.45)}
C4 = (520, FL[4] - CY, 1.45)
C4B = (650, FL[4] - CY, 1.34)
CAMKEYS = [
    (0.0, (310, FL[1] - CY, 1.42)), (1.45, (310, FL[1] - CY, 1.42)), (1.72, (515, FL[1] - 200, 2.4)),
    (1.95, (515, FL[1] - 200, 2.4)), (2.14, CF[1]),
    (2.7, CF[1]), (3.25, (640, (FL[1] + FL[2]) / 2 - CY, 1.2)), (3.8, CF[2]),
    (5.9, CF[2]), (6.4, (660, (FL[2] + FL[3]) / 2 - CY, 1.2)), (6.9, CF[3]),
    (9.55, CF[3]), (10.05, (720, (FL[3] + FL[4]) / 2 - 200, 1.2)), (10.55, C4),
    (11.8, C4), (12.4, C4B), (T_GAP, C4B),
]
SHAKES = [(T_PRESS1, 6, 0.15), (2.43, 5, 0.15), (T_LAND1, 6, 0.2), (T_BOING, 7, 0.2), (T_THUD, 14, 0.3),
          (T_PIT, 5, 0.15), (T_FAINT1, 7, 0.2)]


def camera(t):
    if t < T_GAP:
        cx, cy, z = kf(t, CAMKEYS)
    else:
        def dive(tt):
            ks = keys_state(tt, None, None)
            return (430, max(FL[4] - CY, min(PIT - 230, ks[2] - 120)), 1.45)
        if t < T_PIT + 0.45:
            d = dive(min(t, T_PIT))
            if t < T_GAP + 0.2:
                p = eio(seg(t, T_GAP, T_GAP + 0.2))
                d = tuple(lerp(a, b, p) for a, b in zip(C4B, d))
            cx, cy, z = d
        else:
            start = (430, PIT - 230, 1.45)
            cx, cy, z = kf(t, [(T_PIT + 0.45, start), (T_PIT + 0.85, C4B), (DUR, (715, FL[4] - CY + 10, 1.4))])
    amp = 0
    for t0, a, d in SHAKES:
        if t0 <= t < t0 + d:
            amp = max(amp, a * (1 - (t - t0) / d))
    return cx + amp * math.sin(t * 93), cy + amp * math.cos(t * 79), z


# ---------------------------------------------------------------- frame
OUTSIDE = None


def frame(t):
    ctx = Ctx()
    L = [sky(-400, 1800)]
    for (cx0, cy0, s) in [(100, 300, 1.0), (40, 900, 0.8), (130, 1500, 0.9), (60, 2050, 0.8)]:
        L.append(cloud(cx0 + 20 * math.sin(t * 0.3 + cy0), cy0, s))
    L.append(hills(-400, 1800, FL[1] + 40))
    L.append(basement())
    for k in (1, 2, 3, 4):
        L.append(floor_back(k, t))
        L.append(stairwell(k))
    L.append(shaft())

    g = grumpo_state(t)
    n = nibbo_state(t)
    ks = keys_state(t, n, g)
    yb = car_y(t)
    d = door(t)

    # keys falling in shaft (behind car + slabs)
    if ks and ks[0] == "shaft":
        L.append(keyring(ks[1], ks[2], ks[3], 1.3))
        if t < T_PIT:
            L.append(speed_lines(ks[1], ks[2] - 30, -90, 0.7))

    # car + inside content
    inside = ""
    gsvg, gpos = draw_grumpo(ctx, g, t)
    if g["layer"] == "in" and t >= 0.3:
        inside = gsvg
    press = 0.0
    for tp in (T_PRESS1, T_PRESS2, T_PRESS3):
        if tp <= t < tp + 0.5:
            press = 1 - seg(t, tp + 0.2, tp + 0.5)
    L.append(car(ctx, yb, d, inside, t, press))
    for tp in (T_PRESS1, T_PRESS2, T_PRESS3):
        L.append(impact(PANEL[0], yb + PANEL[1] + 10, seg(t, tp, tp + 0.18)))

    for k in (1, 2, 3, 4):
        L.append(floor_props(k, t))
        L.append(partition(k))
    for k in (1, 2, 3, 4, 5):
        L.append(slab(k))

    # shadows
    if n["vis"] and n["b"] > 0:
        fl = min((v for v in FL.values() if v >= n["b"] - 2), default=FL[1])
        L.append(shadow(n["x"], fl - 8, 100, cl(1 - (fl - 12 - n["b"]) / 400, 0.3, 1)))
    if g["layer"] == "out" or t < 0.3:
        L.append(shadow(g["x"], FL[4 if t > 5 else 1] - 8, 120, cl(1 - (FL[4 if t > 5 else 1] - 12 - g["b"]) / 400, 0.3, 1)))
        L.append(gsvg)

    # nibbo
    nsvg, npos = draw_nibbo(ctx, n, t)
    L.append(nsvg)
    if ks and ks[0] == "front":
        L.append(keyring(ks[1], ks[2], ks[3], 1.3))

    # effects
    Y1, Y2, Y3, Y4 = sy_of(1), sy_of(2), sy_of(3), sy_of(4)
    L.append(impact(160, Y1 - 30, seg(t, 0.4, 0.58), "#fff6a8"))
    L.append(symbol(25, Y1 - 270, "!", seg(t, 0.95, 1.45), "#ffb020"))
    L.append(impact(CARX, Y1 - 120, seg(t, T_POP, T_POP + 0.2), "#ffffff"))
    L.append(dust(210, Y1, seg(t, T_LAND1, T_LAND1 + 0.5)))
    if 2.75 <= t < 2.98:
        L.append(stars_orbit(210, Y1 - 240, t))
    L.append(symbol(240, Y1 - 280, "!", seg(t, 3.0, 3.4), "#ffb020"))
    L.append(dust(240, Y1, seg(t, 3.1, 3.6), 1.0, 1))
    # floor 2
    L.append(dust(780, Y2, seg(t, 3.78, 4.2), 1.0, -1))
    L.append(symbol(CARX, Y2 - 300, "!", seg(t, 4.3, 4.75)))
    L.append(impact(600, Y2 - 130, seg(t, T_BOING, T_BOING + 0.25), "#ffffff"))
    if T_DEFL0 <= t < T_DEFL1:
        L.append(f'<g opacity="{1-seg(t, T_DEFL0, T_DEFL1):.2f}">' + "".join(
            f'<path d="M{g["x"] + 140*math.cos(a):.0f} {g["b"] - 120 + 140*math.sin(a):.0f} l{30*math.cos(a):.0f} {30*math.sin(a):.0f}" stroke="#fff" stroke-width="7" stroke-linecap="round"/>'
            for a in [t * 9 + j * 1.3 for j in range(5)]) + '</g>')
    # floor 3
    L.append(symbol(740, Y3 - 280, "?", seg(t, 7.45, 8.0), "#3a7ad6"))
    if T_DRIP0 <= t < T_DRIP1:
        p = ein(seg(t, T_DRIP0, T_DRIP1))
        L.append(sweat(lerp(512, 548, p), lerp(yb - 330, Y3 - 226, p), 1.6))
    L.append(impact(548, Y3 - 224, seg(t, T_DRIP1, T_DRIP1 + 0.2), "#bfefff"))
    L.append(symbol(565, Y3 - 300, "?", seg(t, T_DRIP1 + 0.02, 8.9), "#3a7ad6"))
    if T_THUD <= t < T_THUD + 0.35:
        L.append(impact(CARX, yb - CH - 10, seg(t, T_THUD, T_THUD + 0.35), "#ffffff"))
    L.append(symbol(700, Y3 - 270, "!", seg(t, T_THUD, T_THUD + 0.45), "#ffb020"))
    # floor 4
    L.append(thought(800, Y4 - 430, seg(t, 13.0, 14.3)))
    L.append(symbol(760, Y4 - 300, "!", seg(t, 14.05, 14.55)))
    if T_CATCH <= t < T_CATCH + 0.2:
        L.append(impact(830, Y4 - 240, seg(t, T_CATCH, T_CATCH + 0.2)))
    L.append(impact(560, Y4 - 40, seg(t, T_FLOOR, T_FLOOR + 0.18), "#ffffff"))
    if T_FLOOR <= t < T_GAP:
        L.append(speed_lines(ks[1] + 50, ks[2] + 30, 180, 0.7))
    if T_PIT <= t < T_PIT + 0.4:
        L.append(impact(420, PIT - 30, seg(t, T_PIT, T_PIT + 0.3), "#ffffff"))
    if t >= T_FAINT1 and npos:
        L.append(stars_orbit(npos[0] + 20, npos[1] - 90, t, 3, 70, 16))
    L.append(dust(950, Y4, seg(t, T_FAINT1, T_FAINT1 + 0.5), 0.8, -1))
    if t >= T_RAIN:
        L.append(rain_cloud(g["x"], g["b"] - 2 * GR * g["sy"] - 150, t, seg(t, T_RAIN, T_RAIN + 0.6) + 0.01))

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}<radialGradient id="vign" cx="0.5" cy="0.55" r="0.75"><stop offset="0.6" stop-color="#000" stop-opacity="0"/>'
           f'<stop offset="1" stop-color="#1a1028" stop-opacity="0.35"/></radialGradient>{"".join(ctx.defs)}</defs>'
           f'<g transform="{tr}">{"".join(L)}</g><rect width="{W}" height="{H}" fill="url(#vign)"/></svg>')
    return overlay(svg, hook_title(t + 0.12, "Grumpo, please", "HOLD THE DOOR!"))


# ---------------------------------------------------------------- sound
def build_sfx():
    sfx(0.0, "hop", 0.6, 0.85)
    sfx(0.1, "keys", 0.8); sfx(0.4, "keys", 0.9, 0.9); sfx(0.45, "thud", 0.5, 1.3)
    sfx(0.6, "boing", 0.4, 1.5)
    sfx(0.95, "alert", 0.6, 1.1); sfx(1.15, "hop", 0.5, 1.3); sfx(1.33, "keys", 0.9)
    sfx(1.38, "suspense", 0.4, 1.2)
    sfx(1.5, "hop", 0.4, 1.3); sfx(1.95, "hop", 0.5, 1.35)
    sfx(1.62, "whoosh", 0.4, 1.4)
    sfx(T_PRESS1, "click", 1.0); sfx(T_PRESS1 + 0.01, "bonk", 0.5, 1.6)
    sfx(1.9, "lift_door", 0.9)
    sfx(2.2, "squish", 0.9); sfx(2.24, "stretch", 0.6, 1.4)
    sfx(T_POP, "pop", 1.0, 0.8); sfx(T_POP + 0.02, "slide_up", 0.6, 1.2)
    sfx(2.44, "clank", 0.6, 0.8)
    sfx(2.55, "ding", 0.7)
    sfx(T_LAND1, "thud", 0.9, 1.1)
    sfx(2.7, "lift_hum", 0.8)
    sfx(3.0, "alert", 0.5, 1.4); sfx(3.1, "zip", 0.8, 0.9)
    for k in range(12):
        sfx(3.25 + k * 0.045, "tiptoe", 0.5, 1.3 + 0.03 * k)
    # floor 2
    sfx(3.8, "ding", 0.8, 1.05); sfx(3.9, "lift_door", 0.8)
    sfx(3.8, "pant", 0.9)
    sfx(4.32, "keys", 0.8)
    sfx(4.3, "gasp", 0.7)
    sfx(T_INFL0, "inhale", 0.7); sfx(T_INFL0 + 0.05, "balloon", 0.8)
    sfx(4.55, "hop", 0.4, 1.3)
    sfx(T_BOING, "boing", 1.1, 0.8); sfx(T_BOING + 0.02, "slide_up", 0.6, 1.0)
    sfx(5.28, "thud", 0.5, 1.2)
    sfx(T_PRESS2, "click", 0.9)
    sfx(T_DEFL0, "deflate", 1.0)
    sfx(5.35, "lift_door", 0.8)
    sfx(5.85, "ding", 0.6, 1.1)
    sfx(5.9, "lift_hum", 0.7, 1.05)
    for k in range(12):
        sfx(5.98 + k * 0.055, "tiptoe", 0.5, 1.35 + 0.03 * k)
    # floor 3
    sfx(6.9, "ding", 0.8, 1.1); sfx(7.0, "lift_door", 0.8)
    sfx(6.75, "pant", 0.6, 1.1)
    sfx(7.45, "squeak", 0.5, 1.2)
    sfx(7.9, "hop", 0.4, 1.3)
    sfx(T_DRIP1, "plop", 0.9, 1.6)
    sfx(T_PRESS3, "click", 0.9)
    sfx(8.65, "lift_door", 0.8); sfx(8.66, "hop", 0.4, 1.4)
    sfx(T_THUD, "thud", 1.2, 0.7); sfx(T_THUD + 0.02, "clank", 0.6, 0.7)
    sfx(9.5, "ding", 0.6, 1.15)
    sfx(9.55, "lift_hum", 0.7, 1.1)
    sfx(9.85, "pant", 0.8, 0.9)
    sfx(9.9, "strain", 0.5, 1.2)
    # floor 4
    sfx(10.55, "ding", 0.8, 1.2); sfx(10.65, "lift_door", 0.8)
    sfx(10.7, "twang", 0.3, 1.6)
    sfx(11.1, "sneak", 0.5)
    sfx(11.72, "cool", 0.4); sfx(11.85, "hop", 0.6, 0.85)
    sfx(12.3, "thud", 0.4, 1.3)
    sfx(12.4, "lift_door", 0.6)
    sfx(12.5, "shaker", 0.6, 1.2)
    sfx(13.0, "alert", 0.9, 0.9); sfx(13.02, "gasp", 0.8)
    sfx(13.4, "drag", 0.7, 1.2); sfx(13.5, "pant", 0.9); sfx(13.6, "keys", 0.5)
    sfx(14.05, "ding", 0.6, 1.6)
    sfx(14.3, "slide_down", 0.5, 1.4)
    sfx(14.4, "boing", 0.5, 1.6)
    sfx(T_TOSS, "whoosh", 0.6, 1.3); sfx(T_TOSS, "keys", 0.8)
    sfx(T_CATCH, "keys", 1.0, 1.1); sfx(T_CATCH + 0.01, "tap", 0.8)
    sfx(T_FLOOR, "keys", 0.9, 0.95)
    sfx(T_FLOOR + 0.02, "squeak_slide", 0.4, 1.6)
    sfx(T_GAP, "tink", 1.0); sfx(T_GAP + 0.05, "slide_down", 0.7, 1.2)
    for yy, gn in ((FL[3], 0.9), (FL[2], 0.8), (FL[1], 0.7)):
        tt = T_GAP + math.sqrt(2 * (yy - FL[4] + 50) / G_FALL)
        sfx(tt, "tink", gn, 1.0 + 0.05 * (FL[1] - yy) / FH)
    sfx(T_PIT, "keys", 0.8, 0.8); sfx(T_PIT + 0.01, "tink", 0.6, 0.85)
    sfx(T_PIT + 0.45, "whoosh", 0.7, 0.9)
    sfx(18.2, "squeak", 0.5, 1.0)
    sfx(T_FAINT0, "slide_down", 0.6, 1.1); sfx(T_FAINT1, "thud", 0.9, 1.2)
    sfx(T_SAG0, "deflate", 0.6, 0.55); sfx(T_SAG0 + 0.1, "grumble", 0.8)
    sfx(T_RAIN, "pop", 0.6, 0.7); sfx(T_RAIN + 0.1, "rain", 0.35)


if __name__ == "__main__":
    import json
    build_sfx()
    print(len(EV))
