"""Grumpo & Nibbo — Episode 4: The Snack Machine (office break corner, common enemy, 60 fps).

Grumpo's candy bar gets stuck in the vending machine. Nibbo's coin-trick buys a can that
wedges on top of it. They team up: shake, then Grumpo's body-slam rocks the machine and
EVERYTHING drops. They bonk heads racing to the tray, the snacks spill on the floor ...
and a robot vacuum slurps up every single one. The refund coin rolls out — the vacuum
zips back for that too. The machine's coin light blinks for more. Third party wins.
"""
import math, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow
from hook import overlay, hook_title

W, H, FPS, DUR = 1080, 1920, 60, 22.8
FLOOR = 1700
NR = 112
NG = FLOOR - NR
GS = 0.92
GY = FLOOR - 120

# vending machine (machine coords == world coords when upright)
MX0, MX1, MY0 = 430, 810, 980
GLASS = (540, 1012, 252, 438)
SHELF = [1150, 1290, 1430]
COLS = [588, 666, 744]
BTN_TARGET = (504, 1180)
BTN_COIN = (474, 1130)
SLOT = (488, 1325)
RETURN = (488, 1412)
TRAY = (560, 1492, 210, 108)

T_PRESS = 0.0
T_STUCK = 1.3
T_COIN = 5.5
T_CLICK = 5.95
T_SLOT = 6.15
T_CAN0, T_CAN1 = 6.25, 7.1
SHAKE0, SHAKE1 = 8.6, 10.2
T_SLAM = 11.7
T_THUNK = 13.45
T_BONK = 15.15
T_FLAP = 15.5
V0, V1 = 16.3, 19.0          # vacuum first pass (right -> left)
T_DING = 19.4
V2, V3 = 20.35, 20.85        # vacuum second pass (left -> right)
T_BLINK = 21.6

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


def kf(t, keys):
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return lerp(v0, v1, eio(seg(t, t0, t1)))
    return keys[-1][1]


def pick(t, keys, default):
    v = default
    for t0, val in keys:
        if t >= t0:
            v = val
    return v


def squash(t, t0, d=0.3, a=0.22):
    k = t - t0
    if 0 <= k < d:
        s = math.sin(math.pi * k / d)
        return 1 + a * 0.6 * s, 1 - a * s
    return 1.0, 1.0


def arm(x0, y0, x1, y1, col, w=10, sag=30):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    return f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


def hand(x, y, fill, stroke, r=13):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="5"/>'


def sweat(x, y, p=1.0):
    return f'<path d="M{x:.1f} {y:.1f} q12 20 0 28 q-12 -8 0 -28z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3" opacity="{p:.2f}"/>'


# ---------------------------------------------------------------- snacks
def can(x, y, rot, col, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            f'<rect x="-23" y="-40" width="46" height="80" rx="9" fill="{col}" stroke="{OL}" stroke-width="5"/>'
            f'<rect x="-23" y="-40" width="46" height="12" rx="5" fill="#d9dee6" stroke="{OL}" stroke-width="4"/>'
            f'<rect x="-23" y="28" width="46" height="12" rx="5" fill="#b9c0cc" stroke="{OL}" stroke-width="4"/>'
            '<rect x="-23" y="-8" width="46" height="18" fill="#ffffff" opacity="0.85"/>'
            f'<circle cx="0" cy="1" r="6" fill="{col}"/>'
            '<rect x="-16" y="-26" width="6" height="50" rx="3" fill="#ffffff" opacity="0.45"/></g>')


def bar(x, y, rot, col, s=1.0, star=False):
    o = (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
         f'<path d="M-27 -44 l6 -6 l6 6 l6 -6 l6 6 l6 -6 l6 6 l6 -6 l6 6 L27 44 l-6 6 l-6 -6 l-6 6 l-6 -6 l-6 6 l-6 -6 l-6 6 l-6 -6Z" '
         f'fill="{col}" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
         '<rect x="-27" y="-14" width="54" height="26" fill="#5a2a12" opacity="0.85"/>'
         '<rect x="-20" y="-34" width="8" height="66" rx="4" fill="#ffffff" opacity="0.35"/>')
    if star:
        pts = []
        for k in range(10):
            a = math.radians(k * 36 - 90)
            rr = 11 if k % 2 == 0 else 4.5
            pts.append(f"{rr*math.cos(a):.1f},{rr*math.sin(a)-1:.1f}")
        o += f'<polygon points="{" ".join(pts)}" fill="#ffe14a" stroke="{OL}" stroke-width="2.5"/>'
    return o + '</g>'


def chips(x, y, rot, col, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            f'<path d="M-30 -42 l5 -6 l5 6 l5 -6 l5 6 l5 -6 l5 6 l5 -6 l5 6 l5 -6 l5 6 l5 -6 l0 0 '
            f'Q 40 0 30 44 l-5 5 l-5 -5 l-5 5 l-5 -5 l-5 5 l-5 -5 l-5 5 l-5 -5 l-5 5 l-5 -5 l-5 5 Q -40 0 -30 -42Z" '
            f'fill="{col}" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<ellipse cx="0" cy="4" rx="17" ry="13" fill="#ffe08a" stroke="{OL}" stroke-width="3"/>'
            '<path d="M-8 2 q8 -8 16 0" stroke="#c98a2a" stroke-width="3" fill="none"/>'
            '<rect x="-22" y="-30" width="7" height="56" rx="3.5" fill="#ffffff" opacity="0.35"/></g>')


SNACKS = [  # kind, color, col index, row
    ("can", "#e8454a", 0, 0), ("can", "#3a8be0", 1, 0), ("can", "#46b86a", 2, 0),
    ("bar", "#8a5ad8", 0, 1), ("bar", "#ff8a1e", 1, 1), ("bar", "#ff6fa8", 2, 1),
    ("chips", "#ffcf3a", 0, 2), ("chips", "#2ec4b6", 1, 2), ("chips", "#ff6a3d", 2, 2),
]
HALF = {"can": 40, "bar": 46, "chips": 48}
TARGET = 4   # orange bar
CAN1 = 1     # blue can (Nibbo's)


def snack(kind, x, y, rot, col, s=1.0, star=False):
    if kind == "can":
        return can(x, y, rot, col, s)
    if kind == "bar":
        return bar(x, y, rot, col, s, star)
    return chips(x, y, rot, col, s)


def rest_pos(i):
    kind, col, c, r = SNACKS[i]
    return COLS[c], SHELF[r] - HALF[kind] - 4


DROP_DELAY = {4: 0.0, 1: 0.03, 3: 0.12, 5: 0.18, 0: 0.24, 2: 0.3, 6: 0.36, 7: 0.42, 8: 0.48}


def impulses(t):
    """damped wobble of the stuck pair."""
    w = 0.0
    for t0, a in [(T_STUCK, 7), (2.3, 3), (2.65, 3), (3.15, 9), (T_CAN1, 6), (T_SLAM, 10)]:
        if t >= t0:
            k = t - t0
            w += a * math.exp(-k * 3.2) * math.sin(2 * math.pi * 3.2 * k)
    if SHAKE0 <= t < SHAKE1:
        w += 7 * math.sin(t * 38)
    return w


def snack_state(i, t):
    """returns (x, y, rot) in machine coords, or None once fallen into the tray."""
    x, y = rest_pos(i)
    rot = 0.0
    if t >= T_THUNK + DROP_DELAY[i]:
        k = t - T_THUNK - DROP_DELAY[i]
        if i == TARGET:
            x, y, rot = 672, 1272, 24
        if i == CAN1:
            x, y, rot = 660, 1204, 78
        y += 0.5 * 4200 * k * k
        rot += 260 * k * (1 if i % 2 else -1)
        if y > GLASS[1] + GLASS[3] + 80:
            return None
        return x, y, rot
    if i == TARGET and t >= T_PRESS + 0.35:
        p = eout(seg(t, 0.35, T_STUCK))
        w = impulses(t)
        return x + 6 * p, y + 28 * p, 24 * p + w
    if i == CAN1 and t >= T_CAN0:
        p1 = eio(seg(t, T_CAN0, T_CAN0 + 0.5))
        if t < T_CAN0 + 0.5:
            return x, y + 10 * p1, 18 * p1
        p2 = seg(t, T_CAN0 + 0.5, T_CAN1)
        x1, y1, r1 = 660, 1204, 78
        if p2 < 1:
            return lerp(x, x1, p2), lerp(y + 10, y1, ein(p2)), lerp(18, r1, p2)
        return x1, y1 + 2 * math.sin(math.radians(impulses(t)) * 3), r1 + impulses(t) * 0.6
    if SHAKE0 <= t < SHAKE1:
        return x + 2 * math.sin(t * 41 + i), y - abs(3 * math.sin(t * 37 + i * 2)), 3 * math.sin(t * 29 + i)
    return x, y, rot


def coil(x, y, phase):
    o = [f'<g transform="translate({x:.1f} {y:.1f})">']
    for k in range(5):
        cx = -32 + ((k * 16 + phase * 16) % 80)
        if cx > 34:
            continue
        o.append(f'<ellipse cx="{cx:.1f}" cy="-8" rx="7" ry="13" fill="none" stroke="#9aa3b2" stroke-width="4"/>')
    o.append('</g>')
    return "".join(o)


# ---------------------------------------------------------------- machine
def machine_body(t, ctx):
    gx, gy, gw, gh = GLASS
    o = []
    # body
    o.append(f'<rect x="{MX0+14}" y="{FLOOR-14}" width="40" height="16" rx="4" fill="{OL}"/>'
             f'<rect x="{MX1-54}" y="{FLOOR-14}" width="40" height="16" rx="4" fill="{OL}"/>')
    o.append(f'<rect x="{MX0}" y="{MY0}" width="{MX1-MX0}" height="{FLOOR-MY0-10}" rx="24" fill="#c92f3c" stroke="{OL}" stroke-width="8"/>')
    o.append(f'<rect x="{MX0+12}" y="{MY0+8}" width="{MX1-MX0-24}" height="{FLOOR-MY0-30}" rx="18" fill="#e8454f"/>')
    o.append(f'<path d="M{MX0+20} {MY0+30} V{FLOOR-40}" stroke="#ff8a90" stroke-width="10" stroke-linecap="round" opacity="0.7"/>')
    # glass interior
    cid = ctx.uid("gl")
    ctx.defs.append(f'<clipPath id="{cid}"><rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="10"/></clipPath>')
    o.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="10" fill="#1f3550"/>')
    inner = [f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" fill="#26405f"/>']
    # back row (darker duplicates)
    for i, (kind, col, c, r) in enumerate(SNACKS):
        x, y = rest_pos(i)
        inner.append(f'<g opacity="0.55">{snack(kind, x + 6, y - 8, 0, col, 0.9)}</g>')
    inner.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" fill="#0d1a2e" opacity="0.35"/>')
    # shelves + coils
    for r, sy in enumerate(SHELF):
        inner.append(f'<rect x="{gx}" y="{sy}" width="{gw}" height="12" fill="#c9d1dc" stroke="{OL}" stroke-width="3"/>')
        for c, cx in enumerate(COLS):
            ph = 0.0
            if r == 1 and c == 1:
                ph = 2.2 * seg(t, 0.35, T_STUCK)
            if r == 0 and c == 1:
                ph = 2.0 * seg(t, T_CAN0, T_CAN0 + 0.7)
            inner.append(coil(cx, sy, ph))
            inner.append(f'<rect x="{cx-14}" y="{sy+2}" width="28" height="8" rx="2" fill="{["#ffd23a", "#7be08a", "#6fd0ff"][c]}"/>')
    # front snacks (stuck ones last so they sit on top)
    order = [k for k in range(9) if k not in (TARGET, CAN1)] + [TARGET, CAN1]
    for i in order:
        st = snack_state(i, t)
        if st is None:
            continue
        kind, col, c, r = SNACKS[i]
        inner.append(snack(kind, st[0], st[1], st[2], col, 1.0, star=(i == TARGET)))
    o.append(f'<g clip-path="url(#{cid})">{"".join(inner)}</g>')
    # glass reflections + frame
    flash = max(0.0, 1 - (t - 3.15) / 0.25) if 3.15 <= t < 3.4 else 0.0
    o.append(f'<g clip-path="url(#{cid})" opacity="0.5"><path d="M{gx+30} {gy+gh} L{gx+150} {gy} L{gx+190} {gy} L{gx+70} {gy+gh}Z" fill="#ffffff" opacity="0.35"/>'
             f'<path d="M{gx+200} {gy+gh} L{gx+260} {gy+gh-140} L{gx+260} {gy+gh-90} L{gx+225} {gy+gh}Z" fill="#ffffff" opacity="0.3"/></g>')
    o.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="10" fill="#ffffff" fill-opacity="{0.25*flash:.2f}" stroke="{OL}" stroke-width="7"/>')
    # control panel
    o.append(f'<rect x="448" y="1012" width="80" height="438" rx="10" fill="#3a3a48" stroke="{OL}" stroke-width="6"/>')
    # display
    o.append(f'<rect x="458" y="1026" width="60" height="44" rx="6" fill="#123a2a" stroke="{OL}" stroke-width="4"/>'
             '<circle cx="488" cy="1048" r="11" fill="#3ae08a" opacity="0.55"/>')
    # keypad
    for (bx, by) in [(474, 1130), (504, 1130), (474, 1180), (504, 1180), (474, 1230), (504, 1230)]:
        lit = (bx, by) == BTN_TARGET and t < 0.5 or (bx, by) == BTN_COIN and T_CLICK <= t < T_CLICK + 0.4
        press = 3 if lit else 0
        o.append(f'<rect x="{bx-11}" y="{by-11+press}" width="22" height="22" rx="6" fill="{"#ffe14a" if lit else "#d9dee6"}" stroke="{OL}" stroke-width="3.5"/>')
    o.append('<rect x="460" y="1094" width="56" height="10" rx="4" fill="#ffffff" opacity="0.25"/>')
    # coin slot + 'insert coin' light
    blink = 0.0
    if t >= T_BLINK:
        blink = 1.0 if math.sin((t - T_BLINK) * 14) > -0.2 else 0.15
    o.append(f'<rect x="466" y="1290" width="44" height="64" rx="8" fill="#c9ccd6" stroke="{OL}" stroke-width="4"/>'
             f'<rect x="484" y="1300" width="8" height="44" rx="4" fill="{OL}"/>')
    lc = mix_hex("#6a5a2a", "#ffd23a", blink)
    if blink > 0.5:
        o.append('<circle cx="488" cy="1272" r="36" fill="#ffd23a" opacity="0.35"/>')
    o.append(f'<circle cx="488" cy="1272" r="14" fill="{lc}" stroke="{OL}" stroke-width="3.5"/>'
             f'<circle cx="488" cy="1272" r="7" fill="none" stroke="{mix_hex("#4a3a1a", "#e8961a", blink)}" stroke-width="2.5"/>')
    # coin return cup
    o.append(f'<rect x="466" y="1392" width="44" height="40" rx="8" fill="#1a1a22" stroke="{OL}" stroke-width="4"/>'
             '<path d="M470 1398 h36" stroke="#5a5a6a" stroke-width="4"/>')
    # brand stripe (icon only)
    o.append(f'<rect x="{MX0+24}" y="{MY0+14}" width="{MX1-MX0-48}" height="0" fill="none"/>')
    # tray
    tx, ty, tw, th = TRAY
    o.append(f'<rect x="{tx-10}" y="{ty-10}" width="{tw+20}" height="{th+20}" rx="12" fill="#3a3a48" stroke="{OL}" stroke-width="6"/>')
    o.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="8" fill="#0f0f16"/>')
    # items piled in tray once dropped (visible when flap open)
    if t >= T_THUNK + 0.3:
        rnd = random.Random(4)
        pile = []
        for i, (kind, col, c, r) in enumerate(SNACKS):
            if t >= T_FLAP + 0.05 + i * 0.05:
                continue
            pile.append(snack(kind, tx + 30 + i * 19, ty + th - 26 - (i % 3) * 14, rnd.uniform(-70, 70), col, 0.62))
        pc = ctx.uid("tc")
        ctx.defs.append(f'<clipPath id="{pc}"><rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="8"/></clipPath>')
        o.append(f'<g clip-path="url(#{pc})">{"".join(pile)}</g>')
    op = eout(seg(t, T_FLAP, T_FLAP + 0.18))
    fh = (th - 14) * (1 - 0.85 * op)
    o.append(f'<rect x="{tx+4}" y="{ty+4}" width="{tw-8}" height="{fh:.1f}" rx="6" fill="#55556a" stroke="{OL}" stroke-width="4"/>'
             f'<rect x="{tx+tw/2-30}" y="{ty+4+fh-16:.1f}" width="60" height="9" rx="4" fill="#8a8aa0"/>')
    return "".join(o)


def machine_angle(t):
    a = 0.0
    dx = 0.0
    if 3.15 <= t < 3.4:
        dx = 4 * math.sin(t * 90) * (1 - (t - 3.15) / 0.25)
    if SHAKE0 <= t < SHAKE1:
        env = min(1, (t - SHAKE0) / 0.15, (SHAKE1 - t) / 0.15)
        a = 2.6 * math.sin(2 * math.pi * 4 * (t - SHAKE0)) * env
        return a, (620, FLOOR), dx
    if T_SLAM <= t < 12.2:
        a = 14 * eout(seg(t, T_SLAM, 12.2))
    elif 12.2 <= t < 12.7:
        a = 14 + 1.5 * math.sin((t - 12.2) * 30)
    elif 12.7 <= t < 13.1:
        a = lerp(14, -8, eio(seg(t, 12.7, 13.1)))
    elif 13.1 <= t < T_THUNK:
        a = lerp(-8, 0, ein(seg(t, 13.1, T_THUNK)))
    elif T_THUNK <= t < T_THUNK + 0.35:
        k = t - T_THUNK
        a = 1.5 * math.sin(k * 40) * (1 - k / 0.35)
    piv = (MX1, FLOOR) if a >= 0 else (MX0, FLOOR)
    return a, piv, dx


def mpoint(x, y, t):
    """machine-local point -> world point."""
    a, (px, py), dx = machine_angle(t)
    r = math.radians(a)
    xx, yy = x - px, y - py
    return px + xx * math.cos(r) - yy * math.sin(r) + dx, py + xx * math.sin(r) + yy * math.cos(r)


# ---------------------------------------------------------------- room
def room(t):
    o = [f'<rect x="-900" y="-900" width="3200" height="{FLOOR+900}" fill="#cfe4e8"/>']
    for x in range(-900, 2300, 120):
        o.append(f'<rect x="{x}" y="-900" width="56" height="{FLOOR+900}" fill="#c4dde2"/>')
    # wainscot
    o.append(f'<rect x="-900" y="1420" width="3200" height="{FLOOR-1420}" fill="#9cc3cc"/>'
             f'<rect x="-900" y="1408" width="3200" height="18" fill="#f4f7f8" stroke="{OL}" stroke-width="4"/>')
    for x in range(-880, 2300, 150):
        o.append(f'<rect x="{x}" y="1450" width="120" height="{FLOOR-1480}" rx="6" fill="none" stroke="#86b0ba" stroke-width="4"/>')
    # window with blinds (left)
    o.append(f'<rect x="60" y="860" width="300" height="380" rx="10" fill="#bfe8ff" stroke="{OL}" stroke-width="7"/>')
    for k in range(9):
        y = 880 + k * 38
        o.append(f'<rect x="72" y="{y}" width="276" height="22" rx="4" fill="#f4f1ea" stroke="#b9b2a2" stroke-width="2.5"/>')
    o.append(f'<path d="M210 860 V1240" stroke="#b9b2a2" stroke-width="3"/>')
    # wall clock
    a1 = t * 30
    o.append(f'<g transform="translate(250 1320)"><circle r="44" fill="#ffffff" stroke="{OL}" stroke-width="6"/>'
             f'<circle r="34" fill="none" stroke="#9cc3cc" stroke-width="4"/>'
             f'<path d="M0 0 V-26" stroke="{OL}" stroke-width="6" stroke-linecap="round" transform="rotate({a1:.1f})"/>'
             f'<path d="M0 0 H18" stroke="{OL}" stroke-width="6" stroke-linecap="round" transform="rotate({a1/12:.1f})"/>'
             f'<circle r="5" fill="{OL}"/></g>')
    # cork board (right) with pinned notes (no text)
    o.append(f'<rect x="870" y="1010" width="250" height="200" rx="8" fill="#d9a466" stroke="{OL}" stroke-width="7"/>'
             f'<rect x="884" y="1024" width="222" height="172" rx="4" fill="#e7b97c"/>')
    for (nx_, ny_, c, r) in [(905, 1040, "#fff27a", -6), (975, 1060, "#8fe0ff", 5), (1040, 1036, "#ffb3cf", -3), (930, 1120, "#b8f0a0", 4), (1010, 1125, "#ffffff", -5)]:
        o.append(f'<g transform="rotate({r} {nx_+30} {ny_+30})"><rect x="{nx_}" y="{ny_}" width="60" height="58" fill="{c}" stroke="{OL}" stroke-width="3"/>'
                 f'<path d="M{nx_+10} {ny_+22} h40 M{nx_+10} {ny_+34} h30 M{nx_+10} {ny_+46} h36" stroke="#8a8a9a" stroke-width="3"/>'
                 f'<circle cx="{nx_+30}" cy="{ny_+6}" r="6" fill="#e8454a" stroke="{OL}" stroke-width="2"/></g>')
    # potted plant (far left)
    o.append(f'<path d="M110 1500 Q 40 1380 70 1300 M120 1500 Q 150 1360 210 1320 M115 1500 Q 100 1400 140 1260" stroke="#2f8a4a" stroke-width="10" fill="none" stroke-linecap="round"/>')
    for (lx, ly, rr) in [(70, 1300, -30), (210, 1320, 30), (140, 1260, 0), (85, 1400, -50), (170, 1390, 40)]:
        o.append(f'<ellipse cx="{lx}" cy="{ly}" rx="34" ry="16" fill="#4cbf68" stroke="{OL}" stroke-width="4" transform="rotate({rr} {lx} {ly})"/>')
    o.append(f'<path d="M60 1500 h120 l-14 {FLOOR-1500} h-92z" fill="#e8834a" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
             f'<rect x="52" y="1490" width="136" height="24" rx="6" fill="#ff9a5a" stroke="{OL}" stroke-width="5"/>')
    # water cooler (far right)
    o.append(f'<rect x="1040" y="1440" width="120" height="{FLOOR-1440}" rx="10" fill="#eef3f7" stroke="{OL}" stroke-width="6"/>'
             f'<path d="M1060 1300 Q 1050 1440 1100 1440 Q 1150 1440 1140 1300 Q 1140 1250 1100 1250 Q 1060 1250 1060 1300Z" fill="#8fd4ff" fill-opacity="0.85" stroke="{OL}" stroke-width="6"/>'
             '<path d="M1074 1290 V1400" stroke="#ffffff" stroke-width="8" stroke-linecap="round" opacity="0.7"/>'
             f'<rect x="1050" y="1500" width="20" height="16" rx="3" fill="#5ab0ff" stroke="{OL}" stroke-width="3"/>')
    # floor: carpet tiles
    o.append(f'<rect x="-900" y="{FLOOR}" width="3200" height="900" fill="#7d8aa6"/>')
    for r, y in enumerate(range(FLOOR, FLOOR + 900, 70)):
        for c, x in enumerate(range(-900, 2300, 140)):
            if (r + c) % 2 == 0:
                o.append(f'<rect x="{x}" y="{y}" width="140" height="70" fill="#7381a0"/>')
    o.append(f'<rect x="-900" y="{FLOOR-22}" width="3200" height="22" fill="#f4f7f8" stroke="{OL}" stroke-width="5"/>')
    o.append(f'<line x1="-900" y1="{FLOOR}" x2="2300" y2="{FLOOR}" stroke="{OL}" stroke-width="6"/>')
    return "".join(o)


# ---------------------------------------------------------------- floor spill + vacuum
def _spill():
    rnd = random.Random(11)
    out = []
    xs = [480, 520, 560, 598, 636, 676, 714, 752, 792, 832, 870]
    order = list(range(9))
    for k, x in enumerate(xs[:9]):
        i = order[k]
        out.append((i, x + rnd.uniform(-8, 8), 1724 + rnd.uniform(0, 34), rnd.choice([-1, 1]) * rnd.uniform(60, 100), T_FLAP + 0.05 + i * 0.05))
    return out


SPILL = _spill()


def vac_x(t):
    if V0 <= t < V1:
        return lerp(1260, -280, (t - V0) / (V1 - V0)), -1
    if V2 <= t < V3:
        return lerp(-280, 1380, (t - V2) / (V3 - V2)), 1
    return None, 0


def suck_time(x):
    # first pass: vacuum front (left edge) reaches x
    return V0 + (1260 - 80 - x) / (1260 + 280) * (V1 - V0)


COIN_X = 652
COIN_SUCK = V2 + (COIN_X - 80 + 280) / (1380 + 280) * (V3 - V2)


def vacuum(x, d, t):
    y = 1742
    s = 1 if d < 0 else -1
    led = "#5af0ff" if math.sin(t * 20) > 0 else "#2a8ab0"
    br = t * 1400
    return (f'<g transform="translate({x:.1f} {y}) scale({1.25*s} 1.25)">'
            f'<ellipse cx="0" cy="26" rx="100" ry="10" fill="#1a1028" opacity="0.25"/>'
            f'<rect x="-92" y="-24" width="184" height="46" rx="22" fill="#e9edf2" stroke="{OL}" stroke-width="6"/>'
            f'<rect x="-92" y="-2" width="184" height="24" rx="12" fill="#4a4f60" stroke="{OL}" stroke-width="5"/>'
            f'<ellipse cx="0" cy="-22" rx="70" ry="9" fill="#cfd6df" stroke="{OL}" stroke-width="4"/>'
            f'<circle cx="-58" cy="-8" r="7" fill="{led}" stroke="{OL}" stroke-width="3"/>'
            f'<circle cx="-52" cy="24" r="9" fill="{OL}"/><circle cx="52" cy="24" r="9" fill="{OL}"/>'
            f'<g transform="translate(-92 18) rotate({br:.0f})"><path d="M-16 0 H16 M0 -16 V16 M-11 -11 L11 11 M-11 11 L11 -11" stroke="#7a8296" stroke-width="4" stroke-linecap="round"/></g>'
            '</g>')


def coin(x, y, sx=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({sx:.3f} 1)"><circle r="17" fill="#ffc21a" stroke="{OL}" stroke-width="4.5"/>'
            '<circle r="10" fill="none" stroke="#e8961a" stroke-width="3"/><ellipse cx="-6" cy="-7" rx="4" ry="2.5" fill="#fff6c0"/></g>')


# ---------------------------------------------------------------- characters
GXK = [(0, 400), (8.45, 400), (8.6, 392), (10.2, 392), (10.35, 392), (10.9, 235), (11.25, 235), (T_SLAM, 392),
       (T_SLAM + 0.05, 392), (12.05, 345), (14.6, 345), (T_BONK, 552), (T_BONK + 0.05, 552), (15.6, 385),
       (20.4, 385), (20.6, 425), (DUR, 425)]
NXK = [(0, 1260), (3.6, 1260), (4.3, 860), (8.45, 860), (8.6, 845), (10.2, 845), (10.9, 900), (T_SLAM, 900),
       (12.0, 868), (14.6, 868), (T_BONK, 778), (T_BONK + 0.05, 778), (15.6, 865), (20.4, 865), (20.6, 835), (DUR, 835)]


def look_at(gx, tx):
    return 1 if tx > gx + 40 else (-1 if tx < gx - 40 else 0)


def grumpo_state(t):
    g = dict(x=kf(t, GXK), y=GY, ex="smug", look=(1, -1), sx=1.0, sy=1.0, red=0.0, rot=0.0)
    ex = pick(t, [(0, "smug"), (0.9, "suspicious"), (1.35, "shock"), (2.2, "grumpy"), (3.1, "angry"), (4.0, "grumpy"),
                  (5.2, "suspicious"), (5.9, "shock"), (6.3, "smug"), (T_CAN1, "shock"), (7.4, "angry"), (8.3, "grumpy"),
                  (8.6, "angry"), (10.2, "grumpy"), (10.35, "angry"), (11.75, "shock"), (13.45, "shock"), (14.1, "smug"),
                  (T_BONK, "shock"), (16.2, "smug"), (16.45, "shock"), (19.0, "grumpy"), (19.45, "suspicious"),
                  (19.8, "smug"), (20.5, "shock"), (21.0, "grumpy"), (22.0, "angry")], "smug")
    g["ex"] = ex
    lk = pick(t, [(0, (1, -1)), (4.0, (1, 0)), (4.4, (1, -1)), (5.2, (1, 0)), (5.9, (0.6, -1)), (6.3, (1, -1)),
                  (7.4, (1, 0)), (8.3, (1, 0.2)), (8.6, (1, -0.3)), (10.2, (1, -1)), (10.35, (1, 0)), (11.75, (1, -1)),
                  (12.6, (0.3, -1)), (13.45, (1, -1)), (14.1, (1, -0.5)), (14.6, (1, 0.4)), (T_BONK, (0, 0)), (16.2, (1, 0.7))], (1, -1))
    g["look"] = lk
    if 16.45 <= t < 19.0:
        vx, _ = vac_x(t)
        g["look"] = (look_at(g["x"], vx), 0.7)
    if 19.0 <= t < 19.45:
        g["look"] = (-1, 0.2)
    if 19.45 <= t < 20.5:
        g["look"] = (1, 1)
    if 20.5 <= t < 21.0:
        vx, _ = vac_x(t)
        g["look"] = (look_at(g["x"], vx if vx is not None else 1200), 0.7)
    if 21.0 <= t < 22.0:
        g["look"] = (0.4, 0.6)
    if t >= 22.0:
        g["look"] = (0.4, -0.6)
    # red
    if 2.9 <= t < 4.6:
        g["red"] = 0.4 * seg(t, 2.9, 3.3) * (1 - seg(t, 4.0, 4.6))
    if 7.4 <= t < 8.4:
        g["red"] = 0.35 * seg(t, 7.4, 7.7) * (1 - seg(t, 8.1, 8.4))
    if 10.35 <= t < T_SLAM:
        g["red"] = 0.3 * seg(t, 10.35, 10.8)
    if t >= 22.0:
        g["red"] = 0.55 * seg(t, 22.0, 22.5)
        g["x"] += 4 * math.sin(t * 70)
    # body motion
    if t < 0.4:
        g["sx"], g["sy"] = squash(t, 0.0, 0.35, 0.08)
    if 3.15 <= t < 3.45:
        g["sx"], g["sy"] = squash(t, 3.15, 0.3, 0.12)
    if 8.6 <= t < 10.2:
        g["y"] = GY - abs(math.sin(t * 19)) * 6
        g["rot"] = 4 * math.sin(t * 25)
    if 10.35 <= t < 10.9:
        g["y"] = GY - abs(math.sin(t * 16)) * 10
    if 11.25 <= t < T_SLAM:
        g["rot"] = 14 * seg(t, 11.25, 11.4)
        g["sx"], g["sy"] = 1.08, 0.94
    if T_SLAM <= t < 12.1:
        g["sx"], g["sy"] = squash(t, T_SLAM, 0.3, 0.25)
        g["rot"] = -10 * (1 - seg(t, T_SLAM, 12.1))
    if 12.7 <= t < T_THUNK:
        k = seg(t, 12.7, 13.0)
        g["sx"], g["sy"] = 1 + 0.08 * k, 1 - 0.14 * k
    if 14.1 <= t < 14.6:
        g["y"] = GY - abs(math.sin((t - 14.1) * 12.6)) * 40
    if 14.6 <= t < T_BONK:
        g["rot"] = 12
        g["y"] = GY - abs(math.sin(t * 18)) * 12
    if T_BONK <= t < 15.6:
        g["sx"], g["sy"] = squash(t, T_BONK, 0.3, 0.2)
        g["rot"] = -8
    if T_BONK <= t < 16.2:
        g["rot"] = 6 * math.sin(t * 9)
    if 20.1 <= t < 20.4:
        k = seg(t, 20.1, 20.25)
        g["sx"], g["sy"] = 1 + 0.06 * k, 1 - 0.1 * k
    if 20.4 <= t < 20.6:
        g["rot"] = 12
    if t >= 21.0:
        k = eio(seg(t, 21.0, 21.8))
        g["sx"], g["sy"] = 1 + 0.1 * k, 1 - 0.16 * k
        g["y"] = GY + 120 * 0.16 * k * GS
    return g


def nibbo_state(t):
    n = dict(x=kf(t, NXK), y=NG, ex="happy", rot=0.0, sx=1.0, sy=1.0)
    n["ex"] = pick(t, [(0, "happy"), (4.4, "wow"), (5.0, "joy"), (5.5, "joy"), (5.75, "happy"), (6.3, "joy"),
                       (T_CAN1, "uhoh"), (7.4, "nervous"), (8.0, "happy"), (8.6, "nervous"), (10.2, "uhoh"), (10.35, "nervous"),
                       (11.75, "wow"), (14.1, "joy"), (14.6, "happy"), (T_BONK, "dizzy"), (16.2, "joy"), (16.45, "wow"),
                       (19.0, "uhoh"), (19.45, "wow"), (20.5, "uhoh"), (21.0, "nervous")], "happy")
    if 3.6 <= t < 4.3:
        n["y"] = NG - abs(math.sin((t - 3.6) * math.pi / 0.7 * 3)) * 70
    if 5.5 <= t < 5.8:
        n["sx"], n["sy"] = squash(t, 5.5, 0.3, 0.18)
    if 8.0 <= t < 8.55:
        n["rot"] = 14 * math.sin((t - 8.0) * 30)   # mimes 'shake it!'
    if 8.6 <= t < 10.2:
        n["y"] = NG - abs(math.sin(t * 19 + 1)) * 6
        n["rot"] = -4 * math.sin(t * 25)
    if 10.35 <= t < 10.9:
        n["y"] = NG - abs(math.sin(t * 16)) * 10
    if 11.95 <= t < 12.75:
        n["sx"], n["sy"] = 1.1, 0.88
        n["y"] = NG + 13
        n["rot"] = -10 + 3 * math.sin(t * 40)
    if 14.1 <= t < 14.6:
        n["y"] = NG - abs(math.sin((t - 14.1) * 12.6)) * 50
    if 14.6 <= t < T_BONK:
        n["rot"] = -12
        n["y"] = NG - abs(math.sin(t * 18 + 1)) * 12
    if T_BONK <= t < 15.6:
        n["sx"], n["sy"] = squash(t, T_BONK, 0.3, 0.22)
    if T_BONK <= t < 16.2:
        n["rot"] = -8 * math.sin(t * 9)
    if 16.45 <= t < 19.0:
        vx, _ = vac_x(t)
        n["rot"] = 10 * look_at(n["x"], vx)
    if 19.45 <= t < 20.5:
        n["rot"] = -14
    if 20.1 <= t < 20.4:
        n["sx"], n["sy"] = 1.08, 0.9
    if t >= 21.0:
        n["rot"] = -10
    return n


# ---------------------------------------------------------------- camera
CK = [(0.0, (616, 1195, 1.5)), (0.45, (616, 1195, 1.5)), (1.2, (650, 1235, 1.75)), (2.05, (650, 1235, 1.75)),
      (2.6, (616, 1195, 1.5)), (6.2, (616, 1195, 1.5)), (6.9, (650, 1200, 1.65)), (7.45, (650, 1200, 1.65)),
      (8.1, (616, 1195, 1.5)), (10.2, (616, 1195, 1.5)), (10.9, (620, 1080, 1.25)), (13.6, (620, 1080, 1.25)),
      (14.2, (618, 1195, 1.5)), (16.2, (618, 1195, 1.5)), (16.7, (622, 1250, 1.45)), (21.0, (622, 1250, 1.45)),
      (21.6, (620, 1260, 1.6)), (DUR, (620, 1260, 1.6))]
SHAKES = [(3.15, 6, 0.2), (T_SLAM, 20, 0.35), (T_THUNK, 26, 0.45), (T_BONK, 10, 0.25), (T_THUNK + 0.25, 8, 0.4)]


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
    g = grumpo_state(t)
    n = nibbo_state(t)

    # machine (tilts / shakes)
    a, (px, py), dx = machine_angle(t)
    L.append(shadow(620 + a * 6, FLOOR + 6, 230))
    L.append(f'<g transform="translate({dx:.1f} 0) rotate({a:.2f} {px} {py})">{machine_body(t, ctx)}</g>')

    if T_THUNK <= t < T_THUNK + 0.6:
        p = seg(t, T_THUNK, T_THUNK + 0.6)
        for k in range(5):
            cx = 450 + k * 80 + 90 * p * (k - 2)
            L.append(f'<circle cx="{cx:.0f}" cy="{FLOOR - 30 - 60*p:.0f}" r="{40 + 40*p:.0f}" fill="#f1f4f8" stroke="#b8c0cc" stroke-width="4" opacity="{0.85*(1-p):.2f}"/>')
    ink = mix_hex("#1a0a2e", "#3a0505", g["red"])
    gfill = mix_hex("#9466e0", "#ff6a52", g["red"])

    # ---- Grumpo
    L.append(shadow(g["x"], FLOOR + 4, 120))
    L.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"],
                    False, 0, None, 0, t))
    sh = (g["x"] + 88, g["y"] - 30)
    tgt = None
    if t < 0.55:
        e = 1 - eio(seg(t, 0.25, 0.55))
        tgt = (lerp(sh[0] + 20, BTN_TARGET[0], e), lerp(sh[1] - 10, BTN_TARGET[1], e))
    elif 2.15 <= t < 3.45:
        k = t - 2.15
        poke = 0.0
        for t0 in (2.3, 2.65, 3.15):
            if t0 - 0.12 <= t < t0 + 0.12:
                poke = math.sin(math.pi * (t - t0 + 0.12) / 0.24)
        gp = mpoint(560, 1270, t)
        e = eio(seg(t, 2.15, 2.3)) * (1 - eio(seg(t, 3.3, 3.45)))
        tgt = (lerp(sh[0], gp[0] - 40 + 40 * poke, e), lerp(sh[1], gp[1], e))
    elif 4.4 <= t < 5.25:
        e = eio(seg(t, 4.4, 4.6)) * (1 - eio(seg(t, 5.05, 5.25)))
        tgt = (lerp(sh[0], 600, e), lerp(sh[1], 1300 + 8 * math.sin(t * 20), e))
    elif SHAKE0 - 0.1 <= t < SHAKE1:
        p1 = mpoint(MX0 + 4, 1440, t)
        p2 = mpoint(MX0 + 4, 1560, t)
        L.append(arm(g["x"] + 70, g["y"] - 60, p1[0], p1[1], ink, 12, 10) + hand(p1[0], p1[1], gfill, OL, 15))
        tgt = p2
    if tgt is not None:
        L.append(arm(sh[0], sh[1], tgt[0], tgt[1], ink, 12, 18 if t < 8 else 0))
        L.append(hand(tgt[0], tgt[1], gfill, OL, 15))
    if T_BONK <= t < 16.2:
        for k in range(3):
            ang = t * 5 + k * 2.1
            L.append(star_twinkle(g["x"] + 95 * math.cos(ang), g["y"] - 140 + 22 * math.sin(ang), 0.35 + 0.3 * ((t * 2 + k * 0.33) % 1)))

    # ---- Nibbo
    if t >= 3.55:
        L.append(shadow(n["x"], FLOOR + 4, 105, max(0.2, 1 - (NG - n["y"]) / 300)))
        L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"], rot=n["rot"], sx=n["sx"], sy=n["sy"]))
        NB, NS = "#ffd23c", "#3d2a12"
        if 3.55 <= t < T_COIN + 0.05:
            cx_, cy_ = n["x"], n["y"] - 168
            L.append(arm(n["x"] - 70, n["y"] - 60, cx_ - 22, cy_ + 10, NS, 10, -10) + arm(n["x"] + 70, n["y"] - 60, cx_ + 22, cy_ + 10, NS, 10, -10))
            L.append(hand(cx_ - 22, cy_ + 10, NB, NS, 12) + hand(cx_ + 22, cy_ + 10, NB, NS, 12))
            L.append(coin(cx_, cy_ - 8))
            L.append(star_twinkle(cx_ + 30, cy_ - 30, ((t - 3.6) * 1.3) % 1))
        if SHAKE0 - 0.1 <= t < SHAKE1:
            p1 = mpoint(MX1 - 4, 1440, t)
            p2 = mpoint(MX1 - 4, 1560, t)
            L.append(arm(n["x"] - 70, n["y"] - 60, p1[0], p1[1], NS, 10, 10) + arm(n["x"] - 80, n["y"] - 10, p2[0], p2[1], NS, 10, 0))
            L.append(hand(p1[0], p1[1], NB, NS, 12) + hand(p2[0], p2[1], NB, NS, 12))
        if 11.95 <= t < 12.75:
            p1 = mpoint(MX1, 1380, t)
            p2 = mpoint(MX1, 1480, t)
            L.append(arm(n["x"] - 60, n["y"] - 70, p1[0], p1[1], NS, 10, 10) + arm(n["x"] - 80, n["y"] - 20, p2[0], p2[1], NS, 10, 0))
            L.append(hand(p1[0], p1[1], NB, NS, 12) + hand(p2[0], p2[1], NB, NS, 12))
        if n["ex"] == "nervous":
            L.append(sweat(n["x"] + 92, n["y"] - 80 + 30 * ((t * 1.5) % 1)))
        if n["ex"] == "dizzy":
            for k in range(3):
                ang = -t * 5 + k * 2.1
                L.append(star_twinkle(n["x"] + 90 * math.cos(ang), n["y"] - 130 + 20 * math.sin(ang), 0.35 + 0.3 * ((t * 2 + k * 0.33) % 1)))

    # ---- coin flick + ricochet
    if T_COIN <= t < T_SLOT:
        if t < T_CLICK:
            p = seg(t, T_COIN, T_CLICK)
            x0, y0 = 860, NG - 176
            x = lerp(x0, BTN_COIN[0], p)
            y = lerp(y0, BTN_COIN[1], p) - 170 * 4 * p * (1 - p)
        else:
            p = seg(t, T_CLICK, T_SLOT)
            x = lerp(BTN_COIN[0], SLOT[0], p) - 30 * math.sin(math.pi * p)
            y = lerp(BTN_COIN[1], SLOT[1] - 30, p)
        L.append(coin(x, y, abs(math.cos(t * 30)) * 0.8 + 0.2))
    # ---- floor spill
    vx, vd = vac_x(t)
    for (i, fx, fy, fr, t0) in SPILL:
        if t < t0:
            continue
        kind, col, c, r = SNACKS[i]
        ts = suck_time(fx)
        if t >= ts + 0.14:
            continue
        p = seg(t, t0, t0 + 0.35)
        sx0, sy0 = 665, 1560
        x = lerp(sx0, fx, eout(p))
        y = lerp(sy0, fy, p) - 90 * math.sin(math.pi * p)
        rot = fr * p
        s = 0.8
        if t >= ts:
            q = seg(t, ts, ts + 0.14)
            x = lerp(fx, vx - 80, q)
            y = lerp(fy, 1738, q)
            s = 0.8 * (1 - q)
            rot = fr + 300 * q
        if s > 0.02:
            L.append(snack(kind, x, y, rot, col, s, star=(i == TARGET)))
    # ---- refund coin
    if T_DING <= t:
        cs = COIN_SUCK
        if t < cs + 0.12:
            if t < T_DING + 0.35:
                p = seg(t, T_DING, T_DING + 0.35)
                x = lerp(RETURN[0], 520, p)
                y = lerp(RETURN[1], 1732, ein(p)) - 60 * math.sin(math.pi * p)
                sx = abs(math.cos(t * 25))
            elif t < 20.0:
                p = eout(seg(t, T_DING + 0.35, 20.0))
                x = lerp(520, COIN_X, p)
                y = 1732 - abs(math.sin(p * 9)) * 18 * (1 - p)
                sx = 0.35 + 0.65 * abs(math.cos(t * 18))
            else:
                k = seg(t, 20.0, 20.45)
                x, y = COIN_X, 1732 + 10 * k
                sx = max(0.15, abs(math.cos((t - 20.0) * 30 * (1 - k * 0.5)))) if k < 1 else 1.0
                if k >= 1:
                    sx = 1.0
            if t >= cs:
                q = seg(t, cs, cs + 0.12)
                x = lerp(COIN_X, vx + 80, q)
                sx *= (1 - q)
            if k_flat := (t >= 20.45 and t < cs):
                L.append(f'<ellipse cx="{COIN_X}" cy="1742" rx="27" ry="9" fill="#ffc21a" stroke="{OL}" stroke-width="4"/>')
            elif sx > 0.02:
                L.append(f'<g transform="translate({x:.1f} {y:.1f}) scale(1.35)">{coin(0, 0, sx)}</g>')
    # ---- vacuum
    if vx is not None:
        L.append(vacuum(vx, vd, t))
        if V2 <= t < V3:
            L.append(speed_lines(vx - 120, 1735, 0, 0.9))
        # suction swirl at its mouth
        L.append(f'<g opacity="0.55"><path d="M{vx + 100*vd:.0f} 1740 q{-20*vd} -18 {-40*vd} 0 q{-20*vd} 18 {-40*vd} 0" stroke="#ffffff" stroke-width="4" fill="none"/></g>')

    # ---- effects
    L.append(symbol(g["x"] + 20, GY - 170, "!", seg(t, 1.35, 2.05)))
    L.append(symbol(n["x"] - 120, NG - 120, "?", seg(t, 4.4, 5.05), "#3a7ad6"))
    L.append(star_twinkle(n["x"] + 60, NG - 200, seg(t, 5.0, 5.5)))
    L.append(symbol(g["x"] + 10, GY - 170, "!", seg(t, T_CAN1, T_CAN1 + 0.6)))
    L.append(symbol(n["x"] - 20, NG - 160, "!", seg(t, 11.85, 12.5)))
    L.append(symbol(g["x"] + 10, GY - 170, "!", seg(t, 12.75, 13.35)))
    L.append(symbol(n["x"], NG - 170, "!", seg(t, 16.45, 17.05)))
    L.append(symbol(g["x"], GY - 170, "?", seg(t, 19.0, 19.5), "#3a7ad6"))
    L.append(symbol(560, 1440, "!", seg(t, T_DING + 0.05, T_DING + 0.6), "#ffb020"))
    L.append(symbol(1000, 1600, "♥", seg(t, 20.9, 21.6), "#ff4d7a"))
    L.append(symbol(g["x"] + 20, GY - 170, "!", seg(t, 21.65, 22.25)))
    L.append(impact(*mpoint(560, 1270, t), seg(t, 3.15, 3.35)))
    L.append(impact(490, 1480, seg(t, T_SLAM, T_SLAM + 0.25)))
    L.append(impact(668, 1520, seg(t, T_BONK, T_BONK + 0.22)))
    L.append(impact(BTN_COIN[0], BTN_COIN[1], seg(t, T_CLICK, T_CLICK + 0.18), "#ffe14a"))
    if 11.2 <= t < T_SLAM:
        L.append(speed_lines(g["x"] - 120, g["y"] - 10, 0, 0.9))
    if 7.4 <= t < 8.3 or 10.35 <= t < 11.2:
        L.append(f'<path d="M{g["x"]+70:.0f} {GY-110} l18 -8 l-6 18 M{g["x"]+88:.0f} {GY-92} l18 -8 l-6 18" stroke="#e8303a" stroke-width="6" fill="none" stroke-linecap="round"/>')
    if 13.5 <= t < 14.3:
        # 'clatter' motion lines behind glass
        p = seg(t, 13.5, 14.3)
        for k in range(3):
            L.append(f'<path d="M{600 + k*60} {1180 + 200*p:.0f} v40" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="{0.7*(1-p):.2f}"/>')

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g></svg>')
    return overlay(svg, hook_title(t + 0.12, "Who gets", "THE SNACKS?"))


def build_sfx():
    sfx(0.0, "click", 0.8, 1.2)
    sfx(0.3, "whirr", 0.8, 1.0)
    sfx(T_STUCK, "thunk", 0.5, 1.6)
    sfx(1.35, "alert", 0.5, 1.0)
    sfx(1.5, "gasp", 0.4, 1.1)
    sfx(2.3, "tap", 0.8, 1.0)
    sfx(2.65, "tap", 0.8, 1.05)
    sfx(3.15, "bonk", 0.8, 1.0)
    sfx(3.17, "clank", 0.4, 1.5)
    sfx(3.4, "grumble", 0.6, 1.0)
    for k in range(3):
        sfx(3.62 + k * 0.233, "hop", 0.6, 1.3)
    sfx(4.0, "coin", 0.25, 1.3)
    sfx(4.45, "squeak", 0.5, 1.1)
    sfx(5.0, "ding", 0.45, 1.5)
    sfx(T_COIN, "whoosh", 0.6, 1.4)
    sfx(T_CLICK, "click", 0.8, 1.3)
    sfx(T_CLICK, "coin", 0.6, 1.0)
    sfx(T_SLOT, "coin", 0.7, 0.85)
    sfx(T_CAN0, "whirr", 0.8, 1.1)
    sfx(T_CAN0 + 0.5, "slide_down", 0.4, 1.4)
    sfx(T_CAN1, "clank", 0.8, 1.1)
    sfx(T_CAN1 + 0.05, "error_beep", 0.35)
    sfx(7.45, "grumble", 0.7, 0.95)
    sfx(7.6, "gulp", 0.5, 1.2)
    sfx(8.0, "boing", 0.4, 1.5)
    sfx(8.35, "pop", 0.4, 1.0)
    for k in range(8):
        sfx(SHAKE0 + k * 0.2, "clank", 0.45, 0.9 + 0.08 * (k % 3))
    sfx(SHAKE0, "shaker", 0.6, 0.9)
    sfx(SHAKE0 + 0.6, "rumble", 0.5, 1.2)
    sfx(SHAKE0 + 0.5, "strain", 0.6, 1.0)
    sfx(SHAKE1 + 0.05, "blip_down", 0.4, 0.9)
    sfx(10.4, "grumble", 0.6, 0.85)
    for k in range(3):
        sfx(10.4 + k * 0.17, "tiptoe", 0.45, 0.8)
    sfx(11.0, "inhale", 0.5, 1.0)
    sfx(11.25, "zip", 0.7, 0.9)
    sfx(11.3, "whoosh", 0.6, 1.0)
    sfx(T_SLAM, "bonk", 1.0, 0.75)
    sfx(T_SLAM, "thud", 0.8, 0.9)
    sfx(T_SLAM + 0.1, "creak", 0.8, 0.8)
    sfx(11.9, "gasp", 0.5, 1.3)
    sfx(12.0, "strain", 0.8, 1.3)
    sfx(12.7, "creak", 0.8, 1.0)
    sfx(12.75, "slide_down", 0.5, 0.8)
    sfx(T_THUNK, "thud", 1.0, 0.7)
    sfx(T_THUNK, "thunk", 0.9, 0.7)
    sfx(T_THUNK + 0.05, "clatter", 0.9, 1.0)
    sfx(T_THUNK + 0.35, "clatter", 0.8, 0.85)
    sfx(14.1, "cheer", 0.5, 1.2)
    sfx(14.15, "boing", 0.5, 1.2)
    sfx(14.65, "zip", 0.6, 1.2)
    sfx(T_BONK, "bonk", 1.0, 0.9)
    sfx(T_BONK + 0.05, "boing", 0.5, 0.8)
    sfx(T_FLAP, "pop", 0.6, 0.9)
    sfx(T_FLAP + 0.05, "clatter", 0.8, 1.15)
    sfx(T_FLAP + 0.4, "slide_down", 0.3, 1.6)
    sfx(16.2, "ding", 0.4, 1.8)
    sfx(V0, "robot_beep", 0.6)
    sfx(V0 + 0.1, "vacuum", 0.7)
    sfx(V0 + 1.3, "vacuum", 0.6, 1.02)
    for (i, fx, fy, fr, t0) in SPILL:
        sfx(suck_time(fx), "suck", 0.55, 0.9 + 0.05 * (i % 5))
    sfx(16.5, "gasp", 0.5, 1.0)
    sfx(18.9, "robot_beep", 0.35, 1.2)
    sfx(19.1, "blip_down", 0.3, 0.7)
    sfx(T_DING, "ding", 0.6, 1.3)
    sfx(T_DING + 0.35, "coin", 0.7, 0.95)
    sfx(T_DING + 0.5, "coin", 0.35, 1.05)
    sfx(20.0, "wobble", 0.35, 2.4)
    sfx(20.1, "inhale", 0.4, 1.2)
    sfx(V2 - 0.05, "zoom", 0.7, 1.2)
    sfx(V2, "vacuum", 0.6, 1.3)
    sfx(COIN_SUCK, "suck", 0.8, 1.3)
    sfx(COIN_SUCK + 0.02, "coin", 0.4, 1.4)
    sfx(20.95, "robot_beep", 0.6, 1.1)
    sfx(21.2, "blip_down", 0.35, 0.8)
    sfx(21.3, "grumble", 0.6, 0.85)
    for k in range(4):
        sfx(T_BLINK + 0.05 + k * 0.45, "blip", 0.5, 1.0)
    sfx(22.05, "rumble", 0.5, 1.4)
