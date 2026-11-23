"""Grumpo & Nibbo — Episode 12: Shade War (beach, one palm tree, sun time-lapse, 60 fps).

One palm tree, two towels, a scorching day. The palm's shade moves with the sun (time-lapse clock on screen):
  9:00 AM : shade is on Grumpo's side. Sweaty Nibbo inches into the shade edge — Grumpo body-bumps him back.
  -> 12:00: the shade shrinks to a tiny puddle under the tree; Grumpo squeezes paper-thin against the trunk to
            stay inside. Nibbo laughs. A tiny crab pops out of its hole, burns its feet on the hot sand and dives back.
  -> 3:00 PM: the shade swings onto Nibbo. Grumpo pops back round in the sun; he charges in, Nibbo bumps him out.
  Grumpo's idea: he jumps, grabs the palm and bends it over himself like a parasol — shade back on him, smug.
  He forgets he's holding the trunk with his drink hand... one sip and the palm whips back: TWANG!
  All fronds and coconuts fly off; coconuts come down — bonk Grumpo, bonk Nibbo. The palm is bald, no shade at all.
  The last frond flutters down and lands like a tiny parasol over the crab, who relaxes in the only shade on the beach.
Ending: a third party wins (the crab).
"""
import math, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, cloud
from hook import overlay, hook_title, counter

W, H, FPS, DUR = 1080, 1920, 60, 19.8
GS = 0.92
GR = 130 * GS          # ~120
NR = 112
GROUND = 1500
TOWEL = 12
GY = GROUND - TOWEL - GR
NY = GROUND - TOWEL - NR
HORIZON = 1130
SHORE = 1300
PALM_X = 540
GTOWEL, NTOWEL = 775, 300
HOLE = 440
INK = "#1a0a2e"
GPURP = "#9466e0"

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


# ---------------------------------------------------------------- timings
T_SCOOT0, T_SCOOT1 = 1.0, 2.35
T_NOTICE = 2.55
T_BUMP1 = 2.9
LAPSE1 = (3.45, 5.0)
T_CRAB_UP, T_CRAB_DOWN = 5.45, 6.3
LAPSE2 = (6.55, 8.1)
T_POP = 7.05
T_RELAX = 7.75
T_CHARGE, T_BUMP2 = 8.85, 9.15
T_ROLLSTOP = 9.85
T_IDEA = 10.25
T_JUMP0, T_GRAB = 10.75, 11.15
T_BENT = 12.15
T_SIP = 13.3
TR = 13.75                # release -> twang
T_DETACH = TR + 0.11
T_BONK_G, T_BONK_N, T_THUD_C = 15.15, 15.5, 15.85
T_LEAF0, T_LEAF_LAND = 15.95, 17.45
T_CRAB_PEEK = 16.7
T_CRAB_RELAX = 17.75


def hour(t):
    if t < LAPSE1[0]:
        return 9.0
    if t < LAPSE1[1]:
        return lerp(9, 12, eio(seg(t, *LAPSE1)))
    if t < LAPSE2[0]:
        return 12.0
    if t < LAPSE2[1]:
        return lerp(12, 15, eio(seg(t, *LAPSE2)))
    return 15.0


def in_lapse(t):
    return LAPSE1[0] <= t < LAPSE1[1] or LAPSE2[0] <= t < LAPSE2[1]


def clock_text(h):
    hh = int(h + 1e-6)
    mm = int(round((h - hh) * 60 / 5) * 5)
    if mm == 60:
        hh, mm = hh + 1, 0
    ap = "AM" if hh < 12 else "PM"
    return f"{(hh - 1) % 12 + 1}:{mm:02d} {ap}"


def clock_bump(t):
    """last time the displayed hour changed."""
    best = None
    for (a, b, h0) in [(LAPSE1[0], LAPSE1[1], 9), (LAPSE2[0], LAPSE2[1], 12)]:
        if t >= a:
            for k in range(1, 4):
                target = h0 + k
                # invert eio roughly by sampling
                for i in range(200):
                    tt = a + (b - a) * i / 199
                    if hour(tt) >= target - 1e-3:
                        if tt <= t:
                            best = tt
                        break
    return best


def sun_pos(h):
    u = (h - 12) / 3.0
    return 540 + 360 * u, 860 + 90 * u * u


# ---------------------------------------------------------------- palm geometry
REST_T, REST_C = (548, 1045), (566, 1280)
BENT_T, BENT_C = (940, 1150), (590, 1020)


def palm_bend(t):
    if t < T_GRAB:
        return 0.0
    if t < TR:
        b = eio(seg(t, T_GRAB, T_BENT))
        if T_BENT <= t:
            b = 1 + 0.025 * math.sin((t - T_BENT) * 38) * max(0.3, 1 - (t - T_BENT) / 1.2)
        return b
    k = t - TR
    return math.cos(2 * math.pi * 1.9 * k) * math.exp(-2.4 * k)


def palm_ctrl(b, t):
    sway = 4 * math.sin(t * 1.3)
    if b >= 0:
        T = (lerp(REST_T[0] + sway, BENT_T[0], b), lerp(REST_T[1], BENT_T[1], b))
        C = (lerp(REST_C[0], BENT_C[0], b), lerp(REST_C[1], BENT_C[1], b))
    else:
        T = (REST_T[0] + 520 * b, REST_T[1] - 60 * b * b * 0 + 140 * b * b)
        C = (REST_C[0] - 20 * b, REST_C[1] + 200 * b)
    return T, C


def bez(P0, C, P1, u):
    x = (1 - u) ** 2 * P0[0] + 2 * u * (1 - u) * C[0] + u * u * P1[0]
    y = (1 - u) ** 2 * P0[1] + 2 * u * (1 - u) * C[1] + u * u * P1[1]
    return x, y


def bez_tan(P0, C, P1, u):
    dx = 2 * (1 - u) * (C[0] - P0[0]) + 2 * u * (P1[0] - C[0])
    dy = 2 * (1 - u) * (C[1] - P0[1]) + 2 * u * (P1[1] - C[1])
    return math.degrees(math.atan2(dy, dx))


def trunk(T, C):
    base = (PALM_X, GROUND + 4)
    pts_l, pts_r, rings = [], [], []
    N = 22
    for i in range(N + 1):
        u = i / N
        x, y = bez(base, C, T, u)
        a = math.radians(bez_tan(base, C, T, u))
        nx, ny = -math.sin(a), math.cos(a)
        w = lerp(34, 19, u)
        pts_l.append((x + nx * w, y + ny * w))
        pts_r.append((x - nx * w, y - ny * w))
        if 0 < i < N and i % 2 == 0:
            rings.append(f'M{x + nx*w*0.92:.1f} {y + ny*w*0.92:.1f} Q {x - math.cos(a)*9:.1f} {y - math.sin(a)*9:.1f} {x - nx*w*0.92:.1f} {y - ny*w*0.92:.1f}')
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts_l + pts_r[::-1])
    hl = " ".join(f"{lerp(a[0], b[0], 0.62):.1f},{lerp(a[1], b[1], 0.62):.1f}" for a, b in zip(pts_l, pts_r))
    return (f'<polygon points="{poly}" fill="#c98f52" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>'
            f'<polyline points="{hl}" fill="none" stroke="#e3b27a" stroke-width="9" stroke-linecap="round" opacity="0.8"/>'
            f'<path d="{" ".join(rings)}" fill="none" stroke="#8a5a2e" stroke-width="5" stroke-linecap="round"/>')


def frond(x, y, ang, L=230, droop=0.55, s=1.0, col="#3fa34d", col2="#66c25e", curve=None):
    """palm frond: curved midrib from (x,y) at angle ang (deg), with zig-zag leaflets.
    curve=(C, P2) overrides the midrib bezier (relative points)."""
    a = math.radians(ang)
    P0 = (0, 0)
    P2 = (L * math.cos(a), L * math.sin(a) + L * droop * 0.9)
    C = (L * 0.55 * math.cos(a), L * 0.55 * math.sin(a) - L * 0.12)
    if curve is not None:
        C, P2 = curve
    up, dn, mid = [], [], []
    N = 14
    for i in range(N + 1):
        u = i / N
        px, py = bez(P0, C, P2, u)
        ta = math.radians(bez_tan(P0, C, P2, u))
        nx, ny = -math.sin(ta), math.cos(ta)
        w = 46 * math.sin(math.pi * min(1, u * 1.15)) ** 0.6 * (1 - 0.35 * u)
        z = 1.0 if i % 2 == 0 else 0.5
        up.append((px + nx * w * z, py + ny * w * z))
        dn.append((px - nx * w * z, py - ny * w * z))
        mid.append((px, py))
    poly = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in up + dn[::-1])
    hi = " ".join(f"{lerp(m[0], u_[0], 0.5):.1f},{lerp(m[1], u_[1], 0.5):.1f}" for m, u_ in zip(mid, up))
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            f'<polygon points="{poly}" fill="{col}" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<polyline points="{hi}" fill="none" stroke="{col2}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>'
            f'<polyline points="{" ".join(f"{m[0]:.1f},{m[1]:.1f}" for m in mid)}" fill="none" stroke="#2c7a38" stroke-width="5" stroke-linecap="round"/></g>')


FRONDS = [(-168, 250, 0.55), (-140, 230, 0.35), (-112, 200, 0.15), (-68, 200, 0.15), (-40, 230, 0.35), (-12, 250, 0.55), (-90, 170, 0.0)]
COCOS = [(-26, 30), (22, 28), (-2, 44)]


def coconut(x, y, rot=0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<circle r="26" fill="#7a4a24" stroke="{OL}" stroke-width="6"/>'
            '<circle cx="-8" cy="-9" r="9" fill="#9a6a3a"/>'
            '<circle cx="5" cy="8" r="3.5" fill="#3a2010"/><circle cx="12" cy="0" r="3.5" fill="#3a2010"/><circle cx="1" cy="-2" r="3.5" fill="#3a2010"/></g>')


def crown(T, rot, t, alive=True):
    if not alive:
        return ""
    o = []
    for k, (a, L, d) in enumerate(FRONDS):
        wig = 3 * math.sin(t * 2.1 + k)
        o.append(frond(T[0], T[1], a + rot + wig, L * 0.92, d))
    return "".join(o)


# ---------------------------------------------------------------- scenery
rnd = random.Random(12)
SHELLS = [(rnd.uniform(-150, 1250), rnd.uniform(1540, 1900), rnd.choice(["shell", "pebble", "pebble", "star"]), rnd.uniform(0, 360)) for _ in range(16)]
SPECK = [(rnd.uniform(-200, 1300), rnd.uniform(SHORE + 30, 1950), rnd.uniform(2, 5)) for _ in range(120)]
SPARK = [(rnd.uniform(-200, 1300), rnd.uniform(HORIZON + 15, SHORE - 30), rnd.uniform(0, 6.28)) for _ in range(26)]


def scenery(t, h):
    o = []
    warm = seg(h, 12, 15) * 0.6
    o.append('<rect x="-800" y="-800" width="2800" height="2000" fill="url(#sky3)"/>')
    if warm > 0:
        o.append(f'<rect x="-800" y="-800" width="2800" height="2000" fill="#ffb060" opacity="{0.10*warm:.2f}"/>')
    sx, sy = sun_pos(h)
    o.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="230" fill="url(#sunglow)"/>'
             f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="78" fill="#fff3b0" stroke="#ffd35a" stroke-width="8"/>'
             f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="60" fill="#fffbe6"/>')
    # sun rays rotating
    rays = []
    for k in range(12):
        a = math.radians(k * 30 + t * 25)
        rays.append(f'M{sx + 96*math.cos(a):.1f} {sy + 96*math.sin(a):.1f} L{sx + 128*math.cos(a):.1f} {sy + 128*math.sin(a):.1f}')
    o.append(f'<path d="{" ".join(rays)}" stroke="#ffe27a" stroke-width="10" stroke-linecap="round" opacity="0.8"/>')
    speed = 160 if in_lapse(t) else 9
    for (cx0, cy0, s) in [(100, 760, 0.8), (800, 680, 0.65), (1350, 820, 0.7)]:
        xx = (cx0 + clouds_x(t) * s) % 2000 - 500
        o.append(cloud(xx, cy0, s))
    # sea
    o.append(f'<rect x="-800" y="{HORIZON}" width="2800" height="{SHORE - HORIZON + 40}" fill="url(#sea)"/>')
    # island
    o.append(f'<path d="M820 {HORIZON+2} Q 900 {HORIZON-60} 990 {HORIZON-52} Q 1060 {HORIZON-70} 1140 {HORIZON+2}Z" fill="#6fb2a8"/>'
             f'<path d="M965 {HORIZON-54} q-6 -40 6 -70 M971 {HORIZON-124} q-30 -4 -44 12 M971 {HORIZON-124} q30 -8 46 8 M971 {HORIZON-124} q-10 -20 -30 -22 M971 {HORIZON-124} q14 -20 34 -18" '
             f'fill="none" stroke="#5a9a90" stroke-width="7" stroke-linecap="round"/>')
    # sailboat
    bx = 150 + (t * 14) % 900 - 200
    o.append(f'<g transform="translate({bx:.1f} {HORIZON + 22})"><path d="M-34 0 h68 l-12 16 h-44z" fill="#f2f2f2" stroke="#6a8aa8" stroke-width="3"/>'
             '<path d="M0 -4 V-70 L32 -8z" fill="#fff" stroke="#6a8aa8" stroke-width="3"/><path d="M-3 -6 V-56 L-26 -8z" fill="#ff8a6a" stroke="#6a8aa8" stroke-width="3"/></g>')
    # sea glints + wave lines
    for (x, y, ph) in SPARK:
        f = 0.5 + 0.5 * math.sin(t * 3 + ph)
        o.append(f'<path d="M{x-16:.0f} {y:.0f} q8 -6 16 0 q8 -6 16 0" fill="none" stroke="#e8fbff" stroke-width="4" stroke-linecap="round" opacity="{0.35+0.5*f:.2f}"/>')
    # wet sand + foam line (surf)
    surf = 0.5 + 0.5 * math.sin(t * 2.1)
    fy = SHORE - 10 + 22 * surf
    o.append(f'<rect x="-800" y="{SHORE - 20}" width="2800" height="2000" fill="url(#sand)"/>')
    o.append(f'<path d="M-800 {SHORE-20} H2000 V{fy+34:.1f} ' + " ".join(f"Q {x+40} {fy+48:.1f} {x} {fy+30:.1f}" for x in range(1960, -840, -80)) + ' Z" fill="#d9b679" opacity="0.6"/>')
    o.append(f'<path d="M-800 {SHORE-40} H2000 V{fy:.1f} ' + " ".join(f"Q {x+40} {fy+18 + 6*math.sin(x/90 + t*2):.1f} {x} {fy:.1f}" for x in range(1960, -840, -80)) + ' Z" fill="#7fd3ea"/>')
    o.append(f'<path d="M2000 {fy:.1f} ' + " ".join(f"Q {x+40} {fy+18 + 6*math.sin(x/90 + t*2):.1f} {x} {fy:.1f}" for x in range(1960, -840, -80)) + '" fill="none" stroke="#ffffff" stroke-width="10" stroke-linecap="round"/>')
    for (x, y, r) in SPECK:
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#d0a560" opacity="0.55"/>')
    for (x, y, kind, r) in SHELLS:
        if kind == "shell":
            o.append(f'<g transform="translate({x:.0f} {y:.0f}) rotate({r:.0f})"><path d="M-18 8 Q -20 -16 0 -18 Q 20 -16 18 8z" fill="#ffd0c4" stroke="{OL}" stroke-width="4"/>'
                     '<path d="M0 -16 V6 M-9 -12 L-6 6 M9 -12 L6 6" stroke="#e8968a" stroke-width="3"/></g>')
        elif kind == "star":
            pts = " ".join(f"{(20 if k % 2 == 0 else 9)*math.cos(math.radians(k*36-90)):.1f},{(20 if k % 2 == 0 else 9)*math.sin(math.radians(k*36-90)):.1f}" for k in range(10))
            o.append(f'<g transform="translate({x:.0f} {y:.0f}) rotate({r:.0f})"><polygon points="{pts}" fill="#ff9a5a" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/></g>')
        else:
            o.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="13" ry="8" fill="#b8a48a" stroke="{OL}" stroke-width="3"/>')
    # bucket & spade decor (bottom right)
    o.append(f'<g transform="translate(905 1700) rotate(8)"><path d="M-46 -40 h92 l-12 84 h-68z" fill="#ff5a6e" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
             f'<path d="M-46 -40 Q 0 -110 46 -40" fill="none" stroke="{OL}" stroke-width="6"/><path d="M-30 -20 h60" stroke="#ff9aa8" stroke-width="8" stroke-linecap="round"/></g>'
             f'<g transform="translate(990 1690) rotate(-24)"><rect x="-6" y="-110" width="12" height="90" rx="5" fill="#ffd23a" stroke="{OL}" stroke-width="5"/>'
             f'<path d="M-28 -24 h56 l-6 40 q-22 16 -44 0z" fill="#3ac0ff" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/></g>')
    return "".join(o)


def clouds_x(t):
    # integrated cloud drift: slow normally, fast during lapses
    def lap(a, b):
        return max(0.0, min(t, b) - a)
    return t * 9 + 150 * (lap(*LAPSE1) + lap(*LAPSE2))


def towel(x, w, c1, c2):
    y = GROUND - TOWEL
    stripes = "".join(f'<rect x="{x - w/2 + k*w/6:.1f}" y="{y}" width="{w/12:.1f}" height="{TOWEL}" fill="{c2}"/>' for k in range(6))
    return (f'<rect x="{x - w/2:.1f}" y="{y}" width="{w}" height="{TOWEL}" rx="5" fill="{c1}"/>{stripes}'
            f'<rect x="{x - w/2:.1f}" y="{y}" width="{w}" height="{TOWEL}" rx="5" fill="none" stroke="{OL}" stroke-width="5"/>'
            f'<path d="M{x - w/2 - 2:.1f} {y+2} l-12 4 M{x - w/2 - 2:.1f} {y+8} l-12 4 M{x + w/2 + 2:.1f} {y+2} l12 4 M{x + w/2 + 2:.1f} {y+8} l12 4" stroke="{c1}" stroke-width="3"/>')


def ground_shadow(cx, hw, op=1.0):
    if hw <= 2 or op <= 0:
        return ""
    return (f'<ellipse cx="{cx:.1f}" cy="{GROUND + 10}" rx="{hw+18:.1f}" ry="{max(18, hw*0.3):.1f}" fill="#8a5232" opacity="{0.5*op:.2f}"/>'
            f'<ellipse cx="{cx:.1f}" cy="{GROUND + 10}" rx="{hw*0.85:.1f}" ry="{max(13, hw*0.22):.1f}" fill="#5a2e22" opacity="{0.42*op:.2f}"/>')


def shade_amount(x, cx, hw):
    return cl((hw + 25 - abs(x - cx)) / 70)


def sweat(x, y, t, n=3, spread=1.0, ph=0.0):
    o = []
    for k in range(n):
        p = (t * 1.6 + k / n + ph) % 1
        side = -1 if k % 2 == 0 else 1
        dx = side * (60 + 70 * p) * spread
        dy = -40 * math.sin(math.pi * p) + 90 * p * p
        o.append(f'<path d="M{x+dx:.1f} {y+dy-14:.1f} q10 15 0 22 q-10 -7 0 -22z" fill="#bfefff" stroke="#3a7aa8" stroke-width="3" opacity="{(1-p)*0.95:.2f}"/>')
    return "".join(o)


def heat(x, y, t, op=1.0):
    if op <= 0:
        return ""
    o = []
    for k in range(3):
        p = (t * 0.9 + k / 3) % 1
        xx = x + (k - 1) * 46
        yy = y - p * 90
        o.append(f'<path d="M{xx:.1f} {yy:.1f} q10 -12 0 -24 q-10 -12 0 -24" fill="none" stroke="#ffb35a" stroke-width="5" stroke-linecap="round" opacity="{op*0.7*math.sin(math.pi*p):.2f}"/>')
    return "".join(o)


def tint(x, y, r, sx, sy, amt, rot=0):
    if amt <= 0.01:
        return ""
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r*sx:.1f}" ry="{r*sy:.1f}" transform="rotate({rot:.1f} {x:.1f} {y:.1f})" fill="#2a3a8a" opacity="{0.27*amt:.2f}"/>'


def crab(x, y, s=1.0, expr="happy", t=0.0, walk=0.0, clip_y=None, ctx=None, lie=0.0):
    leg = 6 * math.sin(walk * 30)
    rot = -12 * lie
    eyes = ('<circle cx="-12" cy="-38" r="9" fill="#fff" stroke="#221c2e" stroke-width="3"/><circle cx="12" cy="-38" r="9" fill="#fff" stroke="#221c2e" stroke-width="3"/>'
            '<circle cx="-11" cy="-37" r="4" fill="#1a0a2e"/><circle cx="13" cy="-37" r="4" fill="#1a0a2e"/>')
    if expr == "joy":
        eyes = ('<circle cx="-12" cy="-38" r="9" fill="#fff" stroke="#221c2e" stroke-width="3"/><circle cx="12" cy="-38" r="9" fill="#fff" stroke="#221c2e" stroke-width="3"/>'
                '<path d="M-18 -37 q6 -7 12 0 M6 -37 q6 -7 12 0" fill="none" stroke="#1a0a2e" stroke-width="3.5" stroke-linecap="round"/>')
    if expr == "ouch":
        eyes = ('<circle cx="-12" cy="-40" r="11" fill="#fff" stroke="#221c2e" stroke-width="3"/><circle cx="12" cy="-40" r="11" fill="#fff" stroke="#221c2e" stroke-width="3"/>'
                '<circle cx="-12" cy="-40" r="3" fill="#1a0a2e"/><circle cx="12" cy="-40" r="3" fill="#1a0a2e"/>')
    mouth = ('<path d="M-8 4 q8 7 16 0" fill="none" stroke="#5a0a0a" stroke-width="3.5" stroke-linecap="round"/>' if expr in ("happy", "joy")
             else '<ellipse cx="0" cy="5" rx="6" ry="7" fill="#5a0a0a"/>')
    body = (f'<path d="M-30 6 l-16 {14+leg:.1f} M-22 12 l-12 {16-leg:.1f} M30 6 l16 {14-leg:.1f} M22 12 l12 {16+leg:.1f}" stroke="{OL}" stroke-width="9" stroke-linecap="round"/>'
            f'<path d="M-30 6 l-16 {14+leg:.1f} M-22 12 l-12 {16-leg:.1f} M30 6 l16 {14-leg:.1f} M22 12 l12 {16+leg:.1f}" stroke="#e8483a" stroke-width="4.5" stroke-linecap="round"/>'
            '<path d="M-12 -14 v-16 M12 -14 v-16" stroke="#221c2e" stroke-width="5"/>'
            '<path d="M-30 -6 Q -52 -18 -50 -40" fill="none" stroke="#221c2e" stroke-width="9" stroke-linecap="round"/><path d="M-30 -6 Q -52 -18 -50 -40" fill="none" stroke="#e8483a" stroke-width="5" stroke-linecap="round"/>'
            '<path d="M30 -6 Q 52 -18 50 -40" fill="none" stroke="#221c2e" stroke-width="9" stroke-linecap="round"/><path d="M30 -6 Q 52 -18 50 -40" fill="none" stroke="#e8483a" stroke-width="5" stroke-linecap="round"/>'
            '<path d="M-50 -40 q-16 -6 -14 -22 q10 2 14 10 q2 -14 12 -16 q4 16 -12 28z" fill="#ff5a48" stroke="#221c2e" stroke-width="4" stroke-linejoin="round"/>'
            '<path d="M50 -40 q16 -6 14 -22 q-10 2 -14 10 q-2 -14 -12 -16 q-4 16 12 28z" fill="#ff5a48" stroke="#221c2e" stroke-width="4" stroke-linejoin="round"/>'
            '<ellipse cx="0" cy="0" rx="36" ry="22" fill="#ff5a48" stroke="#221c2e" stroke-width="5"/><ellipse cx="-10" cy="-7" rx="12" ry="5" fill="#ffb0a0" opacity="0.8"/>'
            + eyes + mouth)
    g = f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">{body}</g>'
    if clip_y is not None and ctx is not None:
        cid = ctx.uid("cr")
        ctx.defs.append(f'<clipPath id="{cid}"><rect x="{x-200:.0f}" y="{clip_y-400:.0f}" width="400" height="400"/></clipPath>')
        g = f'<g clip-path="url(#{cid})">{g}</g>'
    return g


def hole(x, op=1.0):
    return (f'<ellipse cx="{x}" cy="{GROUND+14}" rx="40" ry="11" fill="#5a3a1e" stroke="{OL}" stroke-width="4" opacity="{op:.2f}"/>'
            f'<path d="M{x-52} {GROUND+12} q12 -12 22 -4 M{x+30} {GROUND+8} q12 -8 22 4" fill="none" stroke="#c99a5a" stroke-width="5" stroke-linecap="round" opacity="{op:.2f}"/>')


def cup(x, y, rot=0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})"><path d="M-20 -30 h40 l-8 60 h-24z" fill="#fff3a8" stroke="{OL}" stroke-width="6"/>'
            '<path d="M-17 -10 h34" stroke="#ff8a2a" stroke-width="18" opacity="0.7"/>'
            '<path d="M6 -30 L22 -70" stroke="#ff5a6e" stroke-width="7" stroke-linecap="round"/><path d="M-22 -34 q10 -14 22 -4" fill="#ff7fa0" stroke="#221c2e" stroke-width="3"/></g>')


def arm(x0, y0, x1, y1, w=12, sag=20, col=INK):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    return f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


def hand(x, y, r=15, fill=GPURP):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{OL}" stroke-width="5"/>'


def lump(x, y, p):
    if p <= 0:
        return ""
    s = eback(min(1, p * 3))
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.2f})"><ellipse cx="0" cy="0" rx="30" ry="24" fill="#ff8fb0" stroke="{OL}" stroke-width="5"/>'
            '<ellipse cx="-8" cy="-8" rx="9" ry="5" fill="#fff" opacity="0.6"/></g>')


def stars_orbit(x, y, t, n=3, rx=70, ry=16):
    o = []
    for k in range(n):
        a = t * 6 + k * 2 * math.pi / n
        o.append(star_twinkle(x + rx * math.cos(a), y + ry * math.sin(a), 0.5))
    return "".join(o)


def ff_icon(t):
    """fast-forward icon (screen coords) shown during time-lapses."""
    op = 0
    for a, b in (LAPSE1, LAPSE2):
        if a <= t < b:
            op = min(1, (t - a) / 0.12, (b - t) / 0.15)
    if op <= 0:
        return ""
    pulse = 1 + 0.08 * math.sin(t * 30)
    return (f'<g transform="translate(540 452) scale({0.8*pulse:.3f})" opacity="{op:.2f}">'
            f'<rect x="-82" y="-46" width="164" height="92" rx="46" fill="{OL}" opacity="0.75"/>'
            f'<path d="M-50 -28 L-4 0 L-50 28Z M4 -28 L50 0 L4 28Z" fill="#ffd23a" stroke="#fff" stroke-width="4" stroke-linejoin="round"/></g>')


# ---------------------------------------------------------------- debris (fronds + coconuts launched at twang)
DEB = [(rnd.uniform(-500, 300), rnd.uniform(-2900, -2300), rnd.uniform(-900, 900)) for _ in FRONDS]
COCO_TARGET = {0: (T_BONK_G, "g"), 1: (T_BONK_N, "n"), 2: (T_THUD_C, (640, GROUND - 26))}


# ---------------------------------------------------------------- camera
C0 = (540, 1150, 1.30)
CAMKEYS = [
    (0.0, (545, 1215, 1.42)), (2.4, (550, 1200, 1.40)), (3.4, C0),
    (4.6, C0), (5.1, (520, 1230, 1.55)), (6.4, (520, 1230, 1.55)), (6.9, C0),
    (8.3, C0), (8.8, (500, 1190, 1.38)), (9.4, (560, 1170, 1.32)),
    (10.6, (600, 1140, 1.28)), (12.4, (660, 1150, 1.24)), (13.5, (660, 1165, 1.27)),
    (13.8, (600, 1110, 1.22)), (14.6, (560, 1100, 1.20)), (15.1, C0), (16.2, C0),
    (17.3, (520, 1250, 1.42)), (18.2, (540, 1300, 1.45)), (DUR, (540, 1300, 1.45)),
]
SHAKES = [(T_BUMP1, 8, 0.2), (T_BUMP2, 10, 0.25), (TR, 18, 0.5), (T_BONK_G, 9, 0.2), (T_BONK_N, 7, 0.2), (T_THUD_C, 5, 0.15)]


def camera(t):
    cx, cy, z = kf(t, CAMKEYS)
    amp = 0
    for t0, a, d in SHAKES:
        if t0 <= t < t0 + d:
            amp = max(amp, a * (1 - (t - t0) / d))
    return cx + amp * math.sin(t * 93), cy + amp * math.cos(t * 79), z


# ---------------------------------------------------------------- character states
def grumpo_state(t, sh):
    """returns dict for grumpo."""
    g = dict(x=GTOWEL, b=GROUND - TOWEL, sx=1.0, sy=1.0, rot=0, expr="smug", look=(-0.5, 0.2), drink=True, sip=0.0,
             glasses="up", hold=None, cup=None, lump=0.0, dizzy=False)
    # morning lounge
    if t < T_NOTICE:
        g["sx"], g["sy"] = 1.06, 0.95
        g["expr"] = "smug"
        g["look"] = (-0.8, 0.1) if t > 1.2 else (-0.3, -0.2)
        if 0.35 <= t < 1.05:
            g["sip"] = math.sin(seg(t, 0.35, 1.05) * math.pi)
    elif t < 3.45:
        # notice + bump
        g["expr"] = "suspicious" if t < 2.7 else "angry"
        g["look"] = (-1, 0.2)
        if t >= 2.7:
            p = seg(t, 2.7, T_BUMP1)
            q = seg(t, T_BUMP1, 3.35)
            if t < T_BUMP1:
                g["x"] = lerp(GTOWEL, 690, ein(p))
                g["rot"] = -14 * p
            else:
                g["x"] = lerp(690, GTOWEL, eout(q))
                g["b"] -= 40 * math.sin(math.pi * q)
                g["rot"] = -14 * (1 - q)
                g["expr"] = "smug"
            sx, sy = squash(t, T_BUMP1, 0.3, 0.2)
            g["sx"], g["sy"] = sx, sy
    elif t < LAPSE1[1]:
        # chase the shrinking shade to the trunk
        p = eio(seg(t, LAPSE1[0] + 0.1, LAPSE1[1] - 0.05))
        g["x"] = lerp(GTOWEL, PALM_X + 6, p)
        thin = eio(seg(t, 3.95, LAPSE1[1]))
        g["sx"], g["sy"] = lerp(1, 0.44, thin), lerp(1, 1.62, thin)
        g["expr"] = "shock" if t < 3.95 else "angry"
        g["look"] = (-1, 0.6) if t < 3.95 else (0.2, 0.3)
        g["b"] -= 10 * abs(math.sin(t * 20)) * (1 - thin)
        g["drink"] = t < 3.9
    elif t < LAPSE2[0] + 0.5:
        # noon: paper-thin in a tiny shade
        g["x"] = PALM_X + 6 + 2 * math.sin(t * 30)
        g["sx"], g["sy"] = 0.44, 1.62
        g["expr"] = "grumpy" if t < T_CRAB_UP else "suspicious"
        g["look"] = (-1, 0) if t < T_CRAB_UP else (-0.8, 1)
        g["drink"] = False
        if t >= LAPSE2[0] + 0.2:
            g["expr"] = "shock"
            g["look"] = (-1, 0.5)
    elif t < T_CHARGE:
        # pop back round in the sun, see Nibbo in the shade
        k = seg(t, LAPSE2[0] + 0.5, T_POP)
        g["x"] = lerp(PALM_X + 6, 600, eio(seg(t, T_POP, T_POP + 0.3)))
        if t < T_POP:
            g["sx"], g["sy"] = 0.44, 1.62
            g["expr"] = "shock"
        else:
            kk = t - T_POP
            w = math.exp(-kk * 5) * math.cos(kk * 26)
            g["sx"], g["sy"] = 1 + 0.4 * w * (1 if w < 0 else 0.5) - 0.0, 1 - 0.4 * w
            g["sx"] = max(0.44, 1 - 0.56 * w) if w > 0 else 1 - 0.3 * w
            g["sy"] = min(1.62, 1 + 0.62 * w) if w > 0 else 1 + 0.3 * w
            g["expr"] = "shock" if t < T_RELAX + 0.3 else "angry"
        g["look"] = (-1, 0.3)
        g["drink"] = False
    elif t < T_ROLLSTOP:
        # charge in, get bumped, roll back onto his towel
        if t < T_BUMP2:
            p = seg(t, T_CHARGE, T_BUMP2)
            g["x"] = lerp(600, 470, ein(p))
            g["rot"] = -18 * p
            g["expr"] = "angry"
        else:
            q = seg(t, T_BUMP2, T_ROLLSTOP)
            g["x"] = lerp(470, GTOWEL, eout(q))
            g["b"] -= 120 * math.sin(math.pi * min(1, q * 1.6)) if q < 0.625 else 0
            g["rot"] = 400 * eout(q)
            g["expr"] = "shock"
        g["look"] = (-1, 0.2)
        g["drink"] = False
        sx, sy = squash(t, T_BUMP2, 0.3, 0.25)
        g["sx"], g["sy"] = sx, sy
    elif t < T_JUMP0:
        sx, sy = squash(t, T_ROLLSTOP, 0.3, 0.2)
        g["sx"], g["sy"] = sx, sy
        g["expr"] = "angry" if t < T_IDEA else "suspicious"
        g["look"] = (-1, 0.2) if t < T_IDEA else (-1, -1)
        g["drink"] = True
    elif t < T_GRAB:
        # jump up to the top of the trunk
        p = seg(t, T_JUMP0, T_GRAB)
        g["x"] = lerp(GTOWEL, 700, p)
        top = 1160 + GR
        g["b"] = lerp(GROUND - TOWEL, top, eout(p)) - 90 * math.sin(math.pi * p)
        g["expr"] = "smug"
        g["look"] = (-1, -1)
        g["drink"] = False
        g["hold"] = "reach"
    elif t < TR:
        b = palm_bend(t)
        p = eio(seg(t, T_GRAB, T_BENT))
        g["x"] = lerp(700, GTOWEL, p)
        g["b"] = lerp(1160 + GR, GROUND - TOWEL, p)
        if t >= T_BENT:
            sx, sy = squash(t, T_BENT, 0.3, 0.18)
            g["sx"], g["sy"] = sx, sy
        g["expr"] = "angry" if t < T_BENT - 0.3 else "smug"
        g["look"] = (-1, 0.3)
        g["drink"] = False
        g["hold"] = "trunk"
        if t >= T_SIP:
            g["hold"] = "sip"
    else:
        # release: falls back on his towel, cup at mouth, looks up
        g["drink"] = False
        g["hold"] = "sipping"
        sx, sy = squash(t, TR + 0.05, 0.35, 0.22)
        g["sx"], g["sy"] = sx, sy
        g["expr"] = "shock"
        g["look"] = (-0.6, -1)
        if t >= T_BONK_G:
            sx, sy = squash(t, T_BONK_G, 0.35, 0.3)
            g["sx"], g["sy"] = sx, sy
            g["lump"] = seg(t, T_BONK_G, T_BONK_G + 0.4)
            g["dizzy"] = t < 16.6
            g["expr"] = "shock" if t < 16.6 else ("grumpy" if t < T_CRAB_RELAX else "angry")
            g["look"] = (0, 0) if t < 16.6 else (-1, 0.8)
            g["hold"] = "dropcup"
    return g


def nibbo_state(t, sh):
    n = dict(x=NTOWEL, b=GROUND - TOWEL, sx=1.0, sy=1.0, rot=0, expr="nervous", lump=0.0, dizzy=False)
    if t < T_SCOOT0:
        n["rot"] = 4 * math.sin(t * 7)
    elif t < T_SCOOT1:
        # three little scoots toward the shade edge
        k = min(2, int((t - T_SCOOT0) / 0.45))
        p = seg(t, T_SCOOT0 + 0.45 * k, T_SCOOT0 + 0.45 * k + 0.3)
        x0 = NTOWEL + k * 62
        n["x"] = lerp(x0, x0 + 62, eio(p))
        n["b"] -= 26 * math.sin(math.pi * p)
        n["rot"] = 8 * math.sin(math.pi * p)
        n["expr"] = "nervous"
    elif t < T_BUMP1:
        n["x"] = NTOWEL + 186
        n["expr"] = "happy" if t < T_NOTICE + 0.1 else "uhoh"
        n["sx"], n["sy"] = (1.06, 0.95) if t < T_NOTICE + 0.1 else (1, 1)
    elif t < 3.5:
        q = seg(t, T_BUMP1, 3.4)
        n["x"] = lerp(NTOWEL + 186, NTOWEL, eout(q))
        n["rot"] = -30 * math.sin(math.pi * q)
        sx, sy = squash(t, T_BUMP1, 0.3, 0.28)
        n["sx"], n["sy"] = sy, sx
        n["expr"] = "wow" if q < 0.6 else "nervous"
    elif t < LAPSE1[1] + 0.05:
        n["expr"] = "nervous"
        n["rot"] = 6 * math.sin(t * 9)
    elif t < LAPSE2[0]:
        # noon: laughing at thin Grumpo
        n["expr"] = "joy"
        n["b"] -= 18 * abs(math.sin((t - LAPSE1[1]) * 11))
        n["rot"] = 8 * math.sin(t * 11)
    elif t < T_RELAX:
        n["expr"] = "nervous" if t < 7.3 else "wow"
    elif t < T_CHARGE + 0.15:
        p = eout(seg(t, T_RELAX, T_RELAX + 0.3))
        n["sx"], n["sy"] = lerp(1, 1.18, p), lerp(1, 0.86, p)
        n["expr"] = "joy"
        n["rot"] = 3 * math.sin(t * 2)
    elif t < 10.0:
        # pop up and bump Grumpo out
        p = seg(t, T_CHARGE + 0.15, T_BUMP2)
        q = seg(t, T_BUMP2, 9.6)
        if t < T_BUMP2:
            n["x"] = lerp(NTOWEL, 345, ein(p))
            n["sx"], n["sy"] = lerp(1.18, 0.9, p), lerp(0.86, 1.1, p)
            n["expr"] = "wow"
        else:
            n["x"] = lerp(345, NTOWEL, eio(q))
            sx, sy = squash(t, T_BUMP2, 0.3, 0.25)
            n["sx"], n["sy"] = sy * lerp(1, 1.18, q), sx * lerp(1, 0.86, q)
            n["expr"] = "cool" if t > 9.45 else "joy"
    elif t < T_GRAB + 0.6:
        n["sx"], n["sy"] = 1.18, 0.86
        n["expr"] = "cool"
    elif t < TR:
        # shade slides away: sits up, upset
        p = eio(seg(t, T_GRAB + 0.6, T_GRAB + 0.9))
        n["sx"], n["sy"] = lerp(1.18, 1, p), lerp(0.86, 1, p)
        n["expr"] = "wow" if t < 12.4 else "uhoh"
        if 12.6 <= t < 13.4:
            k = (t - 12.6) / 0.4
            n["b"] -= 40 * abs(math.sin(math.pi * k))
    else:
        n["expr"] = "wow"
        if t >= T_BONK_N:
            sx, sy = squash(t, T_BONK_N, 0.35, 0.3)
            n["sx"], n["sy"] = sx, sy
            n["lump"] = seg(t, T_BONK_N, T_BONK_N + 0.4)
            n["dizzy"] = t < 16.8
            n["expr"] = "dizzy" if t < 16.8 else ("uhoh" if t < T_CRAB_RELAX else "nervous")
    return n


def palm_state(t):
    b = palm_bend(t)
    T, C = palm_ctrl(b, t)
    base = (PALM_X, GROUND + 4)
    tan = bez_tan(base, C, T, 1.0)
    rot = tan + 90
    return b, T, C, rot


def shadow_now(t, T):
    """(centre x, half width, opacity) of the crown shadow on the sand."""
    h = hour(t)
    a = math.radians((h - 12) * 18)
    Hh = max(60, GROUND - T[1])
    c = T[0] - math.tan(a) * Hh * 0.36
    hw = 55 + 85 * abs(math.tan(a))
    if t >= T_GRAB:
        hw *= lerp(1.0, 1.0, 1)
    op = 1.0
    if t >= T_DETACH:
        op = 0.0
    return c, hw, op


# ---------------------------------------------------------------- frame
def frame(t):
    ctx = Ctx()
    h = hour(t)
    L = [scenery(t, h)]
    b, T, C, rot = palm_state(t)
    c, hw, sop = shadow_now(t, T)
    base = (PALM_X, GROUND + 4)

    # crown shadow + trunk shadow on sand
    L.append(ground_shadow(c, hw, sop))
    tdx = c - PALM_X
    L.append(f'<path d="M{PALM_X} {GROUND+4} L{PALM_X + tdx*0.85:.1f} {GROUND+6}" stroke="#7a4a3a" stroke-width="16" stroke-linecap="round" opacity="0.28"/>')

    # towels + hole
    L.append(towel(NTOWEL, 290, "#ffd23c", "#ff8a2a"))
    L.append(towel(GTOWEL, 300, "#9466e0", "#ffffff"))
    L.append(hole(HOLE))

    g = grumpo_state(t, (c, hw))
    n = nibbo_state(t, (c, hw))

    # ---- palm trunk (Grumpo at noon stands in front of it)
    L.append(trunk(T, C))

    # ---- crab (behind characters, in front of sand)
    CR = []
    if T_CRAB_UP <= t < T_CRAB_DOWN + 0.2:
        k = t - T_CRAB_UP
        rise = eback(seg(t, T_CRAB_UP, T_CRAB_UP + 0.2))
        sink = ein(seg(t, T_CRAB_DOWN, T_CRAB_DOWN + 0.2))
        hopy = 0
        ex = "happy" if k < 0.25 else "ouch"
        if 0.25 <= k < T_CRAB_DOWN - T_CRAB_UP:
            hopy = 34 * abs(math.sin((k - 0.25) * 15))
        y = GROUND + 30 - 58 * rise + 80 * sink - hopy
        CR.append(crab(HOLE, y, 1.0, ex, t, walk=k, clip_y=GROUND + 14, ctx=ctx))
        if 0.3 <= k < T_CRAB_DOWN - T_CRAB_UP:
            for j in range(2):
                p = ((k * 2.2) + j * 0.5) % 1
                CR.append(f'<path d="M{HOLE - 30 + 60*j:.0f} {GROUND - 2 - p*60:.1f} q8 -10 0 -20 q-8 -10 0 -20" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" opacity="{0.8*(1-p):.2f}"/>')
    if t >= T_CRAB_PEEK:
        rise = eback(seg(t, T_CRAB_PEEK, T_CRAB_PEEK + 0.25))
        ex = "happy" if t < T_LEAF_LAND else ("wow" if t < T_CRAB_RELAX else "joy")
        lie = eio(seg(t, T_CRAB_RELAX, T_CRAB_RELAX + 0.3))
        x = HOLE + 22 * eio(seg(t, T_LEAF_LAND + 0.05, T_LEAF_LAND + 0.3))
        y = GROUND + 30 - 58 * rise + 6 * lie
        jit = 0
        if t < T_LEAF_LAND:
            jit = 16 * abs(math.sin((t - T_CRAB_PEEK) * 14)) * seg(t, T_CRAB_PEEK + 0.3, T_CRAB_PEEK + 0.4)
            ex = "ouch" if t > T_CRAB_PEEK + 0.3 else "happy"
        CR.append(crab(x, y - jit - 12 * rise, 1.25, ex, t, walk=(t if t < T_LEAF_LAND else 0), clip_y=GROUND + 14, ctx=ctx, lie=lie))
        if t >= 19.0:
            CR.append(symbol(x + 60, y - 120, "♪", seg(t, 19.0, 19.7), "#ff5a6e"))
    if t >= T_LEAF_LAND:
        k = t - T_LEAF_LAND
        wob = 6 * math.sin(k * 25) * max(0, 1 - k / 0.5)
        L.append(ground_shadow(HOLE + 25, 100, 1.0))
        L.append(frond(590, GROUND + 2, 0, s=1.0, curve=((-10 + wob, -360), (-215 + wob, -165 + wob))))
    L += CR

    # (palm trunk is drawn before the crab layer)
    alive = t < T_DETACH
    # coconuts on tree
    if alive:
        ar = math.radians(rot)
        for (dx, dy) in COCOS:
            x = T[0] + dx * math.cos(ar) - dy * math.sin(ar)
            y = T[1] + dx * math.sin(ar) + dy * math.cos(ar)
            L.append(coconut(x, y, rot))

    # ---- NIBBO
    nx, nb = n["x"], n["b"]
    ny = nb - NR * n["sy"]
    namt = shade_amount(nx, c, hw) * sop
    L.append(f'<ellipse cx="{nx:.1f}" cy="{GROUND - 8}" rx="{100*n["sx"]:.1f}" ry="12" fill="#5a3028" opacity="0.22"/>')
    L.append(bloop(ctx, nx, ny, NR, n["expr"], rot=n["rot"], sx=n["sx"], sy=n["sy"]))
    L.append(tint(nx, ny, NR, n["sx"], n["sy"], namt, n["rot"]))
    nsun = 1 - namt
    if nsun > 0.5 and n["expr"] not in ("cool",) and not (LAPSE1[1] <= t < LAPSE2[0]) and t < T_BONK_N:
        L.append(sweat(nx, ny - 40, t, 3, 1.0))
    if nsun > 0.5 and t < TR + 1.4:
        L.append(heat(nx, ny - NR * n["sy"] - 30, t, nsun))
    if n["lump"] > 0:
        L.append(lump(nx + 10, ny - NR * n["sy"] + 8, n["lump"]))
    if n["dizzy"]:
        L.append(stars_orbit(nx, ny - NR - 40, t))

    # ---- GRUMPO
    gx, gb = g["x"], g["b"]
    gy = gb - GR * g["sy"]
    gamt = shade_amount(gx, c, hw) * sop
    if gb > GROUND - TOWEL - 50:
        L.append(f'<ellipse cx="{gx:.1f}" cy="{GROUND - 8}" rx="{110*g["sx"]:.1f}" ry="13" fill="#5a3028" opacity="0.22"/>')
    arm_svg = ""
    if g["hold"] == "reach":
        hx, hy = bez(base, C, T, 0.84)
        arm_svg = arm(gx - 70, gy - 70, hx + 8, hy, sag=-10) + hand(hx + 8, hy)
    elif g["hold"] in ("trunk", "sip"):
        hx, hy = bez(base, C, T, 0.84)
        if g["hold"] == "sip":
            p = eio(seg(t, T_SIP, TR))
            mx, my = gx + 20, gy + 60
            hx2, hy2 = lerp(hx, mx + 40, p), lerp(hy, my - 10, p)
            arm_svg = arm(gx + 40, gy - 80, hx2, hy2, sag=-14) + cup(hx2 + 6, hy2 - 30, lerp(-10, -50, p), 0.9) + hand(hx2, hy2)
        else:
            arm_svg = arm(gx + 40, gy - 80, hx, hy, sag=-14) + cup(hx + 8, hy - 34, -10, 0.9) + hand(hx, hy)
    elif g["hold"] == "sipping":
        mx, my = gx + 60, gy + 50
        arm_svg = arm(gx + 100, gy + 20, mx, my, sag=10) + cup(mx + 6, my - 30, -50, 0.9) + hand(mx, my)
    elif g["hold"] == "dropcup":
        k = t - T_BONK_G
        if k < 0.5:
            p = seg(t, T_BONK_G, T_BONK_G + 0.5)
            cx_, cy_ = lerp(gx + 66, gx + 180, p), lerp(gy + 20, GROUND - 40, p) - 120 * math.sin(math.pi * p)
            arm_svg = cup(cx_, cy_, -50 + 400 * p, 0.9)
        else:
            arm_svg = cup(gx + 180, GROUND - 26, 90, 0.9) + f'<ellipse cx="{gx + 220:.1f}" cy="{GROUND - 6}" rx="{50*seg(t, T_BONK_G + 0.5, T_BONK_G + 0.9):.1f}" ry="9" fill="#ff8a2a" opacity="0.7"/>'
    L.append(grumpo(ctx, gx, gy, GS, g["expr"], 0.0, g["glasses"], g["look"], g["rot"], g["sx"], g["sy"], g["drink"], g["sip"], None, 0.0, t))
    L.append(tint(gx, gy, GR, g["sx"], g["sy"], gamt, g["rot"]))
    gsun = 1 - gamt
    if gsun > 0.5 and t < T_BONK_G and g["hold"] not in ("reach",) and not (T_CHARGE <= t < T_ROLLSTOP):
        L.append(sweat(gx, gy - 50, t, 3, 1.1, 0.3))
    if gsun > 0.5 and t < TR + 1.4:
        L.append(heat(gx, gy - GR * g["sy"] - 30, t, gsun))
    if LAPSE1[1] - 0.3 <= t < LAPSE2[0] + 0.6:
        L.append(sweat(gx, gy - 40, t * 1.2, 2, 0.55, 0.1))
    L.append(arm_svg)
    if g["lump"] > 0:
        L.append(lump(gx - 10, gy - GR * g["sy"] + 6, g["lump"]))
    if g["dizzy"]:
        L.append(stars_orbit(gx, gy - GR - 40, t))

    # ---- crown in front of everyone
    L.append(crown(T, rot, t, alive))

    # ---- debris after twang
    if t >= T_DETACH:
        tau = t - T_DETACH
        T0, _ = palm_ctrl(palm_bend(T_DETACH), T_DETACH)
        for k, ((a, Lf, d), (vx, vy, sp)) in enumerate(zip(FRONDS, DEB)):
            x = T0[0] + vx * tau
            y = T0[1] + vy * tau + 900 * tau * tau
            if y > -800 and tau < 1.2:
                L.append(frond(x, y, a + sp * tau, Lf, d))
        for k, (dx, dy) in enumerate(COCOS):
            tt, tgt = COCO_TARGET[k]
            if t < T_DETACH + 0.6:
                x = T0[0] + dx + (k - 1) * 120 * tau
                y = T0[1] + dy - 2400 * tau + 900 * tau * tau
                L.append(coconut(x, y, tau * 700))
            else:
                if tgt == "g":
                    tx, ty = GTOWEL, GROUND - TOWEL - 2 * GR - 20
                elif tgt == "n":
                    tx, ty = NTOWEL, GROUND - TOWEL - 2 * NR - 20
                else:
                    tx, ty = tgt
                if t < tt:
                    p = seg(t, tt - 0.55, tt)
                    if p > 0:
                        L.append(coconut(tx, lerp(ty - 900, ty, p * p), 400 * p))
                else:
                    k2 = t - tt
                    if tgt in ("g", "n"):
                        # bounce off the head and land behind
                        p = seg(t, tt, tt + 0.6)
                        side = 1 if tgt == "g" else -1
                        bx = tx + side * 170 * p
                        by = lerp(ty, GROUND - 26, p) - 150 * math.sin(math.pi * p)
                        L.append(coconut(bx, by, 300 * p * side))
                    else:
                        p = seg(t, tt, tt + 0.7)
                        L.append(coconut(tx - 60 * eout(p), ty - 40 * math.sin(math.pi * min(1, p * 2)) * (p < 0.5), -200 * eout(p)))
        L.append(impact(GTOWEL, GROUND - TOWEL - 2 * GR, seg(t, T_BONK_G, T_BONK_G + 0.25)))
        L.append(impact(NTOWEL, GROUND - TOWEL - 2 * NR, seg(t, T_BONK_N, T_BONK_N + 0.25)))
        L.append(impact(640, GROUND - 10, seg(t, T_THUD_C, T_THUD_C + 0.25), "#f2dca8"))
        # launched leaves burst
        L.append(impact(T0[0], T0[1], seg(t, T_DETACH, T_DETACH + 0.3), "#c8f0b0"))

    # ---- hero frond falls and becomes the crab's parasol
    if t >= T_LEAF0:
        if t < T_LEAF_LAND:
            p = seg(t, T_LEAF0, T_LEAF_LAND)
            x = 470 + 150 * math.sin(p * 2 * math.pi * 1.25)
            y = lerp(700, 1380, p)
            ang = -90 + 40 * math.cos(p * 2 * math.pi * 1.25)
            L.append(frond(x, y, ang + 180, 210, 0.35, 1.0))
        else:
            k = t - T_LEAF_LAND
            wob = 6 * math.sin(k * 25) * max(0, 1 - k / 0.5)
            # (landed frond is drawn behind the crab, see LEAFBACK)
            L.append(impact(560, GROUND - 6, seg(t, T_LEAF_LAND, T_LEAF_LAND + 0.25), "#f2dca8"))

    # ---- symbols
    L.append(symbol(GTOWEL - 20, GY - 170, "!", seg(t, T_NOTICE, T_NOTICE + 0.55)))
    L.append(symbol(470, GY - 190, "?", seg(t, 7.3, 7.9), "#ffb020"))
    L.append(symbol(GTOWEL, GY - 190, "!", seg(t, T_IDEA, T_IDEA + 0.5), "#ffb020"))
    L.append(symbol(NTOWEL, NY - 180, "!", seg(t, 12.0, 12.55)))
    L.append(symbol(GTOWEL - 60, GY - 230, "!", seg(t, TR + 0.05, TR + 0.6)))
    L.append(speed_lines(gx + 120, gy, 180, 0.9 * (T_CHARGE <= t < T_BUMP2)))

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    defs = (DEFS2 +
            '<linearGradient id="sky3" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2f8be6"/><stop offset="0.6" stop-color="#6cc0f6"/><stop offset="1" stop-color="#d4f1ff"/></linearGradient>'
            f'<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1f86c8"/><stop offset="1" stop-color="#36c2d8"/></linearGradient>'
            f'<linearGradient id="sand" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3d48e"/><stop offset="1" stop-color="#e6b766"/></linearGradient>'
            '<radialGradient id="vign" cx="0.5" cy="0.55" r="0.75"><stop offset="0.6" stop-color="#000" stop-opacity="0"/>'
            '<stop offset="1" stop-color="#1a1028" stop-opacity="0.3"/></radialGradient>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{defs}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g>'
           f'<rect width="{W}" height="{H}" fill="url(#vign)"/></svg>')
    bt = clock_bump(t)
    return overlay(svg, hook_title(t + 0.12, "1 palm tree, 2 towels", "SHADE WAR!"),
                   counter(t, clock_text(h), "", bump_t=bt), ff_icon(t))


# ---------------------------------------------------------------- sound
def build_sfx():
    for k in range(8):
        sfx(k * 2.6, "surf", 0.32, 1.0 + 0.04 * (k % 3))
    sfx(0.0, "pop", 0.8); sfx(0.05, "ding", 0.4, 1.3)
    sfx(0.4, "slurp", 0.7)
    sfx(0.3, "pant", 0.6)
    for k in range(3):
        sfx(T_SCOOT0 + 0.45 * k, "hop", 0.5, 1.2 + 0.1 * k)
        sfx(T_SCOOT0 + 0.45 * k + 0.25, "tiptoe", 0.5, 1.1)
    sfx(2.4, "ding", 0.5, 1.6)
    sfx(T_NOTICE, "alert", 0.7)
    sfx(2.7, "zip", 0.6, 0.9)
    sfx(T_BUMP1, "bonk", 1.0, 1.1); sfx(T_BUMP1 + 0.02, "boing", 0.7, 1.2)
    sfx(T_BUMP1 + 0.1, "squeak_slide", 0.7)
    sfx(LAPSE1[0], "ffwd", 0.8); sfx(LAPSE1[0] + 0.05, "whirr", 0.4, 1.6)
    sfx(3.55, "gasp", 0.6)
    sfx(3.95, "stretch", 0.8, 1.1); sfx(4.75, "squish", 0.7, 1.2)
    sfx(LAPSE1[1] + 0.05, "ding", 0.5, 1.1)
    sfx(LAPSE1[1] + 0.15, "laugh", 0.8, 1.05)
    sfx(T_CRAB_UP, "pop", 0.6, 1.5)
    sfx(T_CRAB_UP + 0.25, "sizzle", 0.8)
    for k in range(4):
        sfx(T_CRAB_UP + 0.28 + k * 0.21, "tiptoe", 0.5, 1.6)
    sfx(T_CRAB_UP + 0.3, "crab", 0.6)
    sfx(T_CRAB_DOWN, "zip", 0.6, 1.4); sfx(T_CRAB_DOWN + 0.15, "plop", 0.5, 1.4)
    sfx(LAPSE2[0], "ffwd", 0.8, 0.95); sfx(LAPSE2[0] + 0.05, "whirr", 0.4, 1.5)
    sfx(T_POP, "boing", 0.9, 0.9); sfx(T_POP + 0.02, "pop", 0.6, 0.8)
    sfx(7.3, "alert", 0.5, 1.3)
    sfx(T_RELAX, "cool", 0.6); sfx(T_RELAX + 0.05, "squish", 0.5, 1.4)
    sfx(8.3, "grumble", 0.9)
    sfx(T_CHARGE, "zip", 0.8, 0.8); sfx(T_CHARGE + 0.05, "whoosh", 0.5, 1.2)
    sfx(T_BUMP2, "bonk", 1.0, 0.9); sfx(T_BUMP2 + 0.01, "boing", 0.8, 0.8)
    sfx(T_BUMP2 + 0.05, "whoosh", 0.6)
    sfx(9.55, "thud", 0.6, 1.1); sfx(T_ROLLSTOP, "thud", 0.7, 1.0)
    sfx(9.6, "click", 0.6); sfx(9.62, "cool", 0.5)
    sfx(T_IDEA, "ding", 0.8, 1.2)
    sfx(T_JUMP0, "hop", 0.7, 0.9); sfx(T_JUMP0 + 0.05, "slide_up", 0.6, 1.1)
    sfx(T_GRAB, "thunk", 0.6, 1.2)
    sfx(T_GRAB + 0.05, "creak", 0.9); sfx(T_GRAB + 0.1, "stretch", 0.8, 0.8); sfx(T_GRAB + 0.2, "rustle", 0.5, 0.8)
    sfx(T_BENT, "thud", 0.6, 1.2)
    sfx(12.0, "alert", 0.6, 1.1)
    sfx(12.5, "strain", 0.6, 0.9)
    sfx(12.6, "hop", 0.4, 1.4); sfx(13.0, "hop", 0.4, 1.5)
    sfx(T_SIP + 0.15, "slurp", 0.9)
    sfx(TR, "twang", 1.3, 0.7); sfx(TR + 0.01, "whoosh", 0.9, 0.7)
    sfx(T_DETACH, "rustle", 1.0); sfx(T_DETACH + 0.02, "whoosh", 0.8, 1.2)
    sfx(TR + 0.08, "thud", 0.6, 1.1)
    sfx(TR + 0.1, "gasp", 0.6, 0.9)
    sfx(14.55, "slide_down", 0.8, 1.15)
    sfx(T_BONK_G, "coconut", 1.1); sfx(T_BONK_G + 0.01, "bonk", 0.6, 1.0)
    sfx(T_BONK_G + 0.45, "splash_small", 0.4, 1.4)
    sfx(T_BONK_N, "coconut", 1.0, 1.15); sfx(T_BONK_N + 0.01, "boing", 0.5, 1.4)
    sfx(T_THUD_C, "thud", 0.8, 0.9)
    sfx(T_LEAF0, "rustle", 0.35, 1.3)
    for k in range(4):
        sfx(T_LEAF0 + 0.25 + k * 0.32, "flap", 0.3, 1.2 + 0.1 * (k % 2))
    sfx(T_CRAB_PEEK, "pop", 0.5, 1.6)
    sfx(T_CRAB_PEEK + 0.3, "sizzle", 0.5, 1.2)
    sfx(T_LEAF_LAND, "thunk", 0.7, 1.3)
    sfx(T_CRAB_RELAX, "ding", 0.7, 1.5)
    sfx(T_CRAB_RELAX + 0.4, "crab", 0.6)
    sfx(18.4, "grumble", 0.8, 1.05)
    sfx(19.0, "crab", 0.5, 1.1)
