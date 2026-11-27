"""Grumpo & Nibbo — Episode 19: The Last Pack (supermarket, 60 fps).

Structure J (teamwork that backfires). Ending: the prize is worthless.
Supermarket aisle, every shelf is EMPTY — except ONE glowing pack of toilet paper on the very top shelf.
Both hop for it: way too short. Nibbo's idea: he climbs onto Grumpo's head — still short.
Grumpo's idea: he yanks a shopping cart over and hops in with Nibbo still on his head. Wobbly tower,
Nibbo stretches... GOT IT! A proud moment of teamwork — then the cart rolls away with Grumpo (crash off-screen),
Nibbo drops, the pack bounces to the floor. Both dive for it, tug of war: it bends like paper... RIP!
Each holds half: it was only a flat CARDBOARD DISPLAY. Finally an empty cardboard tube drops on Grumpo's head.
"""
import math, sys, os
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

FLOOR = 1700
GY = FLOOR - GR
NY = FLOOR - NR
SX0, SX1 = 230, 850             # shelf unit uprights
TOP = 950                       # top shelf board (pack stands on it)
SHELVES = [1180, 1410]
PACK_X = 560
PW, PH = 160, 150
RIM = FLOOR - 250               # cart basket rim
CART_X = 540
GX0, NX0 = 380.0, 700.0
TOWER_X = 540.0

# ---- times
T_IN = 0.45
T_UP = 0.5
T_EACH = 0.95
HOP_G = [1.1, 1.6, 2.1]
HOP_N = [1.35, 1.85, 2.3]
HOP_D = 0.42
T_IDEA_N = 2.75
T_POINT0, T_POINT1 = 2.85, 3.25
T_NOD = 3.25
T_SLIDE0, T_SLIDE1 = 3.3, 3.55
T_CLIMB0, T_CLIMB1 = 3.55, 3.95
T_REACH0, T_REACH1 = 3.95, 5.15
T_IDEA_G = 5.2
T_ARM0, T_ARM1 = 5.45, 5.7
T_YANK0, T_YANK1 = 5.75, 6.2
T_JUMP0, T_JUMP1 = 5.9, 6.45
T_TOUCH = 7.35
T_GRAB = 7.85
T_GOT = 8.05
T_ROLL = 8.8
T_GONE = 9.55
T_HANG1 = 9.3
T_FALL1 = 9.7
T_PACK_LAND = 10.2
T_BACK0, T_BACK1 = 10.15, 10.85
T_SEE = 10.9
T_DIVE0, T_DIVE1 = 11.2, 11.45
T_RIP = 12.6
T_LAND2 = 12.95
T_TURN0, T_TURN1 = 13.15, 14.0
T_LOOK = 14.25
T_TUBE0, T_TUBE_HIT, T_TUBE_LAND = 14.75, 15.05, 15.55
DUR = 17.0

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


def squash(t, t0, d=0.3, a=0.22):
    k = t - t0
    if 0 <= k < d:
        s = math.sin(math.pi * k / d)
        return 1 + a * 0.6 * s, 1 - a * s
    return 1.0, 1.0


def bodypt(x, y, s, rot, sx, sy, px, py):
    a = math.radians(rot)
    lx, ly = px * s * sx, py * s * sy
    return x + lx * math.cos(a) - ly * math.sin(a), y + lx * math.sin(a) + ly * math.cos(a)


def arm(x0, y0, x1, y1, col, w=13, sag=20):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    return f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


def hand(x, y, fill, stroke, r=16):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="5"/>'


def lerp2(a, b, p):
    return (lerp(a[0], b[0], p), lerp(a[1], b[1], p))


# ---------------------------------------------------------------- props
def defs():
    return ('<linearGradient id="wallS" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6efe0"/><stop offset="1" stop-color="#efe3c8"/></linearGradient>'
            '<linearGradient id="floorS" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9dde6"/><stop offset="1" stop-color="#b9c0cc"/></linearGradient>'
            '<linearGradient id="wrap" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#e8f6ff" stop-opacity="0.55"/><stop offset="1" stop-color="#9fd0f0" stop-opacity="0.35"/></linearGradient>'
            '<radialGradient id="holy" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff6b0" stop-opacity="0.95"/><stop offset="0.5" stop-color="#fff6b0" stop-opacity="0.35"/><stop offset="1" stop-color="#fff6b0" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="vig" cx="0.5" cy="0.55" r="0.8"><stop offset="0.62" stop-color="#1a2030" stop-opacity="0"/><stop offset="1" stop-color="#1a2030" stop-opacity="0.3"/></radialGradient>'
            '<clipPath id="halfL"><path d="M-90 -90 H2 L-8 -60 L6 -32 L-6 -4 L8 24 L-4 52 L4 90 H-90Z"/></clipPath>'
            '<clipPath id="halfR"><path d="M90 -90 H2 L-8 -60 L6 -32 L-6 -4 L8 24 L-4 52 L4 90 H90Z"/></clipPath>')


def roll(x, y, w=44, h=62):
    return (f'<rect x="{x-w/2:.1f}" y="{y-h/2:.1f}" width="{w}" height="{h}" rx="10" fill="#ffffff" stroke="{OL}" stroke-width="4"/>'
            f'<rect x="{x+w/2-12:.1f}" y="{y-h/2+4:.1f}" width="8" height="{h-8}" rx="4" fill="#dfe6ef"/>'
            f'<path d="M{x-w/2+6:.1f} {y-h/2+16:.1f} h{w-12}" stroke="#e6ecf3" stroke-width="3"/>')


def pack_front():
    """toilet-paper 6-pack, front view, centred at 0,0 (PW x PH)."""
    o = [f'<rect x="-80" y="-75" width="160" height="150" rx="14" fill="#f4f8fc"/>']
    for r in range(2):
        for c in range(3):
            o.append(roll(-50 + c * 50, -38 + r * 72))
    o.append(f'<rect x="-80" y="-14" width="160" height="40" fill="#3a8fd8" stroke="{OL}" stroke-width="4"/>'
             f'<path d="M-80 -14 h160" stroke="#8fd0ff" stroke-width="4"/>'
             f'<path d="M-30 14 q-14 0 -14 -12 q0 -12 14 -12 q4 -10 18 -8 q10 -8 22 0 q14 0 12 12 q0 12 -14 12z" fill="#ffffff" stroke="{OL}" stroke-width="3"/>'
             f'<path d="M30 -4 q6 -8 12 0 q6 -8 12 0 q0 8 -12 16 q-12 -8 -12 -16z" fill="#ff7fa0" stroke="{OL}" stroke-width="3"/>')
    o.append(f'<rect x="-80" y="-75" width="160" height="150" rx="14" fill="url(#wrap)" stroke="{OL}" stroke-width="6"/>'
             f'<path d="M-66 -62 q20 -6 40 0" stroke="#ffffff" stroke-width="7" fill="none" stroke-linecap="round" opacity="0.8"/>'
             f'<path d="M-24 -75 q24 -36 48 0" fill="none" stroke="{OL}" stroke-width="12" stroke-linecap="round"/>'
             f'<path d="M-24 -75 q24 -36 48 0" fill="none" stroke="#dfeefa" stroke-width="6" stroke-linecap="round"/>')
    return "".join(o)


def pack(x, y, rot=0.0, sx=1.0, sy=1.0, skew=0.0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s*sx:.3f} {s*sy:.3f}) skewY({skew:.1f})">'
            + pack_front() + '</g>')


def half_pack(side, x, y, rot, flip, s=1.0):
    """one torn half. flip = cos of the turn angle (1 front, -1 back)."""
    cid = "halfL" if side < 0 else "halfR"
    f = flip if abs(flip) > 0.06 else (0.06 if flip >= 0 else -0.06)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s*f:.3f} {s:.3f}) translate({-44*side} 0)">']
    if flip >= 0:
        o.append(f'<g clip-path="url(#{cid})">{pack_front()}</g>')
        o.append(f'<g clip-path="url(#{cid})"><path d="M2 -90 L-8 -60 L6 -32 L-6 -4 L8 24 L-4 52 L4 90" fill="none" stroke="#c8a070" stroke-width="10"/>'
                 f'<path d="M2 -90 L-8 -60 L6 -32 L-6 -4 L8 24 L-4 52 L4 90" fill="none" stroke="{OL}" stroke-width="4"/></g>')
    else:
        o.append(f'<g clip-path="url(#{cid})"><rect x="-80" y="-75" width="160" height="150" rx="14" fill="#c99a5b" stroke="{OL}" stroke-width="6"/>'
                 + "".join(f'<path d="M-80 {-60 + k*22} h160" stroke="#b0844a" stroke-width="4"/>' for k in range(7)) +
                 f'<path d="M2 -90 L-8 -60 L6 -32 L-6 -4 L8 24 L-4 52 L4 90" fill="none" stroke="{OL}" stroke-width="4"/></g>')
        # fold-out stand (the giveaway)
        sx_ = -44 if side < 0 else 44
        o.append(f'<path d="M{sx_-18} 70 L{sx_} -30 L{sx_+18} 70Z" fill="#dbb07a" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>')
    o.append('</g>')
    # paper-thin edge when nearly side-on
    if abs(flip) < 0.25:
        k = 1 - abs(flip) / 0.25
        o.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})" opacity="{k:.2f}"><rect x="-6" y="{-75*s:.0f}" width="12" height="{150*s:.0f}" rx="3" fill="#c99a5b" stroke="{OL}" stroke-width="4"/></g>')
    return "".join(o)


def tube(x, y, rot=0.0, s=1.35):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<rect x="-16" y="-34" width="32" height="68" rx="6" fill="#c99a5b" stroke="{OL}" stroke-width="5"/>'
            f'<path d="M-16 -10 L16 -22 M-16 14 L16 2" stroke="#a87a42" stroke-width="4"/>'
            f'<ellipse cx="0" cy="-34" rx="16" ry="6" fill="#7a5228" stroke="{OL}" stroke-width="4"/></g>')


def cart_back(x, rot=0.0, lift=0.0):
    """basket interior + frame + wheels (drawn behind a rider)."""
    y = FLOOR - lift
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f} 0 -20)">']
    # frame + wheels
    o.append(f'<path d="M-96 -110 L-80 -26 L96 -26 L110 -110" fill="none" stroke="{OL}" stroke-width="14" stroke-linejoin="round"/>'
             f'<path d="M-96 -110 L-80 -26 L96 -26 L110 -110" fill="none" stroke="#c9d2de" stroke-width="7" stroke-linejoin="round"/>')
    for wx in (-70, 84):
        o.append(f'<circle cx="{wx}" cy="-16" r="18" fill="#3a3f4a" stroke="{OL}" stroke-width="5"/><circle cx="{wx}" cy="-16" r="6" fill="#c9d2de"/>')
    # basket back wall
    o.append(f'<path d="M-130 -250 L130 -250 L110 -110 L-104 -110Z" fill="#9aa6b6" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>')
    o.append('</g>')
    return "".join(o)


def cart_front(x, rot=0.0, lift=0.0):
    """wire mesh front + rim + handle (drawn over a rider)."""
    y = FLOOR - lift
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f} 0 -20)">']
    mesh = []
    for k in range(9):
        xx = -130 + k * 32.5
        xb = -104 + k * 26.75
        mesh.append(f'M{xx:.1f} -250 L{xb:.1f} -110')
    for k in range(1, 4):
        yy = -250 + k * 35
        xl = lerp(-130, -104, k / 4)
        xr = lerp(130, 110, k / 4)
        mesh.append(f'M{xl:.1f} {yy} L{xr:.1f} {yy}')
    o.append(f'<path d="{" ".join(mesh)}" stroke="{OL}" stroke-width="7" fill="none"/>'
             f'<path d="{" ".join(mesh)}" stroke="#dfe6ee" stroke-width="3.5" fill="none"/>')
    o.append(f'<path d="M-130 -250 L130 -250 L110 -110 L-104 -110Z" fill="none" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>')
    o.append(f'<rect x="-138" y="-262" width="276" height="20" rx="8" fill="#e8402e" stroke="{OL}" stroke-width="5"/>'
             f'<path d="M-128 -256 h250" stroke="#ff8a7a" stroke-width="4"/>')
    # handle on the right
    o.append(f'<path d="M126 -250 L170 -300" stroke="{OL}" stroke-width="14" stroke-linecap="round"/><path d="M126 -250 L170 -300" stroke="#c9d2de" stroke-width="7" stroke-linecap="round"/>'
             f'<rect x="156" y="-318" width="34" height="26" rx="9" fill="#e8402e" stroke="{OL}" stroke-width="5"/>')
    o.append('</g>')
    return "".join(o)


def product(x, y, kind, c):
    if kind == 0:
        return (f'<rect x="{x-18}" y="{y-56}" width="36" height="56" rx="6" fill="{c}" stroke="{OL}" stroke-width="3.5"/>'
                f'<rect x="{x-18}" y="{y-40}" width="36" height="16" fill="#ffffff" opacity="0.7"/>')
    if kind == 1:
        return (f'<rect x="{x-10}" y="{y-70}" width="20" height="14" rx="3" fill="#ffffff" stroke="{OL}" stroke-width="3"/>'
                f'<path d="M{x-20} {y} V{y-40} Q{x-20} {y-58} {x-8} {y-58} H{x+8} Q{x+20} {y-58} {x+20} {y-40} V{y}Z" fill="{c}" stroke="{OL}" stroke-width="3.5"/>')
    return (f'<ellipse cx="{x}" cy="{y-24}" rx="24" ry="24" fill="{c}" stroke="{OL}" stroke-width="3.5"/>'
            f'<path d="M{x-10} {y-36} q10 -8 20 0" stroke="#ffffff" stroke-width="4" fill="none" opacity="0.7"/>')


COLS = ["#ff7a3a", "#3a8fd8", "#7ad06a", "#ffcf3a", "#e8508a", "#9a6ae0"]


def bg_shelf(x0, x1, scale_op=1.0):
    """distant fully-stocked shelf (other aisles), hazy."""
    o = [f'<g opacity="0.55">']
    o.append(f'<rect x="{x0}" y="720" width="{x1-x0}" height="{FLOOR-720}" fill="#c8b994"/>')
    for k, y in enumerate(range(860, FLOOR, 170)):
        o.append(f'<rect x="{x0}" y="{y}" width="{x1-x0}" height="14" fill="#9c8c6a"/>')
        for j, x in enumerate(range(x0 + 30, x1 - 20, 52)):
            o.append(product(x, y, (j + k) % 3, COLS[(j * 2 + k) % 6]))
    o.append('</g>')
    return "".join(o)


def store(t):
    o = [f'<rect x="-900" y="-400" width="2900" height="{FLOOR+400}" fill="url(#wallS)"/>']
    o.append(f'<rect x="-900" y="560" width="2900" height="46" fill="#3a8fd8"/><rect x="-900" y="606" width="2900" height="12" fill="#ffcf3a"/>')
    o.append(bg_shelf(-700, 170))
    o.append(bg_shelf(910, 1800))
    # floor
    o.append(f'<rect x="-900" y="{FLOOR}" width="2900" height="900" fill="url(#floorS)"/>')
    for i in range(-12, 26):
        x = i * 120
        o.append(f'<path d="M{x} {FLOOR} L{x + (x-540)*0.8:.0f} {FLOOR+600}" stroke="#aeb6c4" stroke-width="3"/>')
    for y in (FLOOR + 60, FLOOR + 150, FLOOR + 280):
        o.append(f'<path d="M-900 {y} H2000" stroke="#aeb6c4" stroke-width="3"/>')
    o.append(f'<path d="M-900 {FLOOR} H2000" stroke="{OL}" stroke-width="6"/>')
    # main (empty) shelf unit
    o.append(f'<rect x="{SX0}" y="760" width="{SX1-SX0}" height="{FLOOR-760}" fill="#dfe7ee" stroke="{OL}" stroke-width="6"/>')
    for yy in range(790, FLOOR - 40, 44):
        for xx in range(SX0 + 30, SX1 - 10, 44):
            o.append(f'<circle cx="{xx}" cy="{yy}" r="4" fill="#b9c6d2"/>')
    o.append(f'<rect x="{SX0}" y="760" width="{SX1-SX0}" height="{FLOOR-760}" fill="none" stroke="{OL}" stroke-width="6"/>')
    for y in [TOP] + SHELVES:
        o.append(f'<rect x="{SX0-6}" y="{y}" width="{SX1-SX0+12}" height="24" fill="#f2f5f8" stroke="{OL}" stroke-width="5"/>'
                 f'<rect x="{SX0-6}" y="{y+24}" width="{SX1-SX0+12}" height="26" fill="#ffcf3a" stroke="{OL}" stroke-width="5"/>')
        for k, xx in enumerate(range(SX0 + 40, SX1 - 60, 150)):
            o.append(f'<rect x="{xx}" y="{y+29}" width="54" height="16" rx="3" fill="#ffffff" stroke="{OL}" stroke-width="2.5"/>'
                     f'<path d="M{xx+8} {y+37} h{18 + 8*(k%2)}" stroke="#e8402e" stroke-width="5" stroke-linecap="round"/>')
    # dust + crumbs on the empty shelves
    for y in SHELVES:
        for k in range(3):
            xx = SX0 + 90 + k * 210 + (y % 7) * 9
            o.append(f'<ellipse cx="{xx}" cy="{y-4}" rx="10" ry="4" fill="#cfc7b8" opacity="0.8"/>')
    o.append(f'<rect x="{SX0-6}" y="{FLOOR-70}" width="{SX1-SX0+12}" height="70" fill="#3a8fd8" stroke="{OL}" stroke-width="5"/>')
    for x in (SX0, SX1):
        o.append(f'<rect x="{x-18}" y="740" width="36" height="{FLOOR-740}" rx="6" fill="#aeb9c6" stroke="{OL}" stroke-width="5"/>')
    # TP-roll icon tag on the upright (icon only)
    o.append(f'<g transform="translate({SX1} 1060)"><rect x="-44" y="-40" width="88" height="80" rx="12" fill="#ffffff" stroke="{OL}" stroke-width="5"/>'
             + roll(0, 2, 34, 46) + '</g>')
    return "".join(o)


# ---------------------------------------------------------------- faces
def grumpo_extra(x, y, s, rot, sx, sy, kind, t, red=0.0):
    if not kind:
        return ""
    ink = mix_hex(INK, "#3a0505", red)
    base = mix_hex("#9466e0", "#ff6a52", red)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s*sx:.3f} {s*sy:.3f})">']
    if kind == "dizzy":
        for ex in (-38, 38):
            o.append(f'<circle cx="{ex}" cy="16" r="21" fill="#fff" stroke="{ink}" stroke-width="3"/>'
                     f'<path d="M{ex} 16 m-12 0 a12 12 0 1 1 12 12 a8 8 0 1 1 -8 -8 a4 4 0 1 1 4 4" fill="none" stroke="{ink}" stroke-width="4" '
                     f'transform="rotate({t*720:.0f} {ex} 16)"/>')
        o.append(f'<path d="M-30 74 q10 -10 20 0 t20 0 t20 0" fill="none" stroke="{ink}" stroke-width="8" stroke-linecap="round"/>')
    elif kind == "grin":
        o.append(f'<path d="M-60 6 h44 v30 h-44z M16 6 h44 v30 h-44z" fill="{base}"/>'
                 f'<path d="M-58 22 q20 -16 40 0 M18 22 q20 -16 40 0" fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M-72 -30 Q -44 -24 -16 -14 M72 -30 Q 44 -24 16 -14" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<path d="M-40 58 Q 0 100 40 58Z" fill="#4a0a14" stroke="{ink}" stroke-width="8" stroke-linejoin="round"/>'
                 f'<path d="M-30 62 h60" stroke="#fff" stroke-width="8"/>')
    elif kind == "strain":
        o.append(f'<path d="M-76 -40 L -18 -8 M76 -40 L 18 -8" fill="none" stroke="{ink}" stroke-width="18" stroke-linecap="round"/>'
                 f'<rect x="-40" y="58" width="80" height="34" rx="12" fill="#fff" stroke="{ink}" stroke-width="7"/>'
                 f'<path d="M-36 75 h72 M-14 60 v30 M12 60 v30" stroke="{ink}" stroke-width="4"/>')
    elif kind == "flat":
        tw = 4 * math.sin(t * 40) if (int(t * 3) % 2 == 0) else 0
        o.append(f'<path d="M-60 6 h44 v30 h-44z M16 6 h44 v30 h-44z" fill="{base}"/>'
                 f'<path d="M-58 22 h40 M18 {22+tw:.1f} h40" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M-70 -10 Q -44 -14 -16 -8 M70 -10 Q 44 -14 16 -8" fill="none" stroke="{ink}" stroke-width="14" stroke-linecap="round"/>'
                 f'<path d="M-26 76 h52" stroke="{ink}" stroke-width="9" stroke-linecap="round"/>')
    elif kind == "pant":
        o.append(f'<path d="M-72 -30 Q -44 -20 -16 -8 M72 -30 Q 44 -20 16 -8" fill="none" stroke="{ink}" stroke-width="17" stroke-linecap="round"/>'
                 f'<ellipse cx="0" cy="76" rx="{18+4*math.sin(t*30):.1f}" ry="{14+6*math.sin(t*30):.1f}" fill="#4a0a14" stroke="{ink}" stroke-width="7"/>'
                 f'<path d="M86 -60 q8 13 0 18 q-8 -5 0 -18z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3"/>')
    o.append('</g>')
    return "".join(o)


def nib_face(x, y, r, rot, sx, sy, kind, t=0.0):
    if not kind:
        return ""
    f = r / 48 * 1.05
    d = "#2a1a10"
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx*f:.3f} {sy*f:.3f})">']
    if kind in ("lookup", "lookleft", "lookright", "lookdown"):
        dx, dy = {"lookup": (0, -4), "lookleft": (-4, 1), "lookright": (4, 1), "lookdown": (0, 4)}[kind]
        o.append(f'<ellipse cx="-14" cy="-4" rx="7" ry="9" fill="#fff" stroke="{d}" stroke-width="2"/><ellipse cx="14" cy="-4" rx="7" ry="9" fill="#fff" stroke="{d}" stroke-width="2"/>'
                 f'<circle cx="{-14+dx}" cy="{-4+dy}" r="4.5" fill="{d}"/><circle cx="{14+dx}" cy="{-4+dy}" r="4.5" fill="{d}"/>')
        if kind == "lookleft":
            o.append(f'<path d="M-24 -20 l12 5 M24 -20 l-12 5" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                     f'<path d="M-7 16 h14" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
        else:
            o.append(f'<ellipse cx="0" cy="16" rx="5" ry="6" fill="#7a2a1a" stroke="{d}" stroke-width="3"/>')
    elif kind == "effort":
        o.append(f'<path d="M-22 -10 l10 6 l-10 6 M22 -10 l-10 6 l10 6" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
                 f'<rect x="-11" y="10" width="22" height="11" rx="4" fill="#fff" stroke="{d}" stroke-width="3"/>'
                 f'<path d="M26 -24 q7 11 0 15 q-7 -4 0 -15z" fill="#bfefff" stroke="#3a6a8a" stroke-width="2"/>')
    elif kind == "worried":
        o.append(f'<path d="M-24 -18 l12 -5 M24 -18 l-12 -5" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<ellipse cx="-14" cy="-3" rx="7" ry="9" fill="{d}"/><ellipse cx="14" cy="-3" rx="7" ry="9" fill="{d}"/>'
                 '<circle cx="-12" cy="-7" r="2.4" fill="#fff"/><circle cx="16" cy="-7" r="2.4" fill="#fff"/>'
                 f'<ellipse cx="0" cy="17" rx="9" ry="6" fill="#7a2a1a" stroke="{d}" stroke-width="3.5"/>')
    elif kind == "shrug":
        o.append(f'<path d="M-24 -20 l12 4 M24 -14 l-12 -4" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<ellipse cx="-14" cy="-3" rx="6" ry="7" fill="{d}"/><ellipse cx="14" cy="-3" rx="6" ry="7" fill="{d}"/>'
                 f'<path d="M-24 -6 h20" stroke="#ffd23c" stroke-width="7"/><path d="M-24 -4 h20" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<path d="M-12 14 q4 -5 8 0 t8 0 t8 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>'
                 f'<path d="M26 -26 q8 13 0 18 q-8 -5 0 -18z" fill="#bfefff" stroke="#3a6a8a" stroke-width="2.5"/>')
    elif kind == "sparkle":
        o.append(f'<path d="M-21 -2 q7 -10 14 0 M7 -2 q7 -10 14 0" fill="none" stroke="{d}" stroke-width="5" stroke-linecap="round"/>'
                 f'<path d="M-12 8 q12 18 24 0z" fill="#7a2a1a" stroke="{d}" stroke-width="4" stroke-linejoin="round"/>')
    o.append('</g>')
    return "".join(o)


# ---------------------------------------------------------------- states
def cart_x(t):
    if t < T_YANK0:
        return 1250.0
    if t < T_YANK1:
        return lerp(1250, CART_X, eout(seg(t, T_YANK0, T_YANK1)))
    if t < T_ROLL:
        w = seg(t, T_JUMP1, T_JUMP1 + 0.3)
        damp = 1 - 0.5 * seg(t, T_GRAB, T_GOT)
        return CART_X + 22 * math.sin((t - T_JUMP1) * 5.5) * w * damp
    p = seg(t, T_ROLL + 0.15, T_GONE)
    return lerp(CART_X + 22 * math.sin((T_ROLL - T_JUMP1) * 5.5) * 0.5, 1550, ein(p))


def tower_rot(t):
    if T_JUMP1 <= t < T_ROLL:
        w = seg(t, T_JUMP1, T_JUMP1 + 0.3)
        damp = 1 - 0.6 * seg(t, T_GRAB, T_GOT)
        return 5 * math.sin((t - T_JUMP1) * 5.5 + 0.9) * w * damp
    return 0.0


def grumpo_state(t):
    g = dict(x=GX0, y=GY, rot=0.0, sx=1.0, sy=1.0, ex="grumpy", kind=None, look=(1, 0), red=0.0, hR=None, hL=None, half=None, in_cart=False)
    if t < T_IN:
        p = eout(seg(t, -0.35, T_IN))
        g["x"] = lerp(-160, GX0, p)
        g["y"] = GY - 16 * abs(math.sin(t * 15))
        g["rot"] = 8 * (1 - p)
        g["look"] = (0.6, -1)
        return g
    if t < T_EACH:
        g["look"] = (0.6, -1)
        g["ex"] = "shock" if t < T_UP + 0.25 else "grumpy"
        g["sx"], g["sy"] = squash(t, T_IN, 0.3, 0.14)
        return g
    if t < HOP_G[0]:
        g["ex"], g["look"] = "suspicious", (1, 0)
        return g
    if t < T_IDEA_N:
        g["ex"], g["look"] = "angry", (0.6, -1)
        for h in HOP_G:
            if h <= t < h + HOP_D:
                p = seg(t, h, h + HOP_D)
                g["y"] = GY - 170 * math.sin(math.pi * p)
                g["hR"] = (g["x"] + 70, g["y"] - 175 - 30 * math.sin(math.pi * p))
                g["sx"], g["sy"] = 0.92, 1.1
                g["ex"], g["kind"] = "x", "strain"
            elif h + HOP_D <= t < h + HOP_D + 0.15:
                g["sx"], g["sy"] = squash(t, h + HOP_D, 0.15, 0.15)
        if t >= HOP_G[-1] + HOP_D:
            g["ex"], g["kind"] = "x", "pant"
        return g
    if t < T_SLIDE0:
        g["ex"], g["look"] = "suspicious", (1, -0.2)
        if t < T_POINT0:
            g["ex"], g["kind"] = "x", "pant"
        if t >= T_NOD:
            g["sx"], g["sy"] = squash(t, T_NOD, 0.2, 0.12)
        return g
    if t < T_CLIMB1:
        p = eio(seg(t, T_SLIDE0, T_SLIDE1))
        g["x"] = lerp(GX0, TOWER_X, p)
        g["ex"], g["look"] = "grumpy", (1, -0.6)
        g["hL"] = (g["x"] - 80, g["y"] - 140)
        g["hR"] = (g["x"] + 80, g["y"] - 140)
        if t >= T_CLIMB1 - 0.05:
            g["sx"], g["sy"] = 1.1, 0.88
        return g
    g["x"] = TOWER_X
    if t < T_JUMP0:
        g["sx"], g["sy"] = squash(t, T_CLIMB1, 0.3, 0.2)
        g["ex"], g["kind"] = "x", "strain"
        g["red"] = 0.3 * seg(t, T_CLIMB1, T_REACH1)
        g["rot"] = 3 * math.sin(t * 9)
        g["hL"] = (g["x"] - 82, g["y"] - 150)
        g["hR"] = (g["x"] + 82, g["y"] - 150)
        if t >= T_IDEA_G:
            g["ex"], g["kind"] = "grumpy", None
            g["red"] = 0.3 * (1 - seg(t, T_IDEA_G, T_IDEA_G + 0.3))
            g["look"] = (1, 0)
            g["rot"] = 0
            g["hR"] = None
            if t >= T_IDEA_G + 0.15:
                g["ex"], g["kind"] = "x", "grin"
        if t >= T_ARM0:
            cx = cart_x(t)
            hx = lerp(g["x"] + 120, min(1060, cx + 170), eout(seg(t, T_ARM0, T_ARM1)))
            if t >= T_YANK0:
                hx = cx + 170
            g["hR"] = (hx, FLOOR - 300)
            g["ex"], g["kind"] = "x", "strain"
        return g
    if t < T_JUMP1:
        p = seg(t, T_JUMP0, T_JUMP1)
        top = RIM - 55
        g["y"] = lerp(GY, top, p) - 230 * math.sin(math.pi * p)
        g["ex"], g["kind"] = "x", "grin"
        g["hL"] = (g["x"] - 90, g["y"] - 120)
        g["hR"] = (g["x"] + 90, g["y"] - 120)
        g["sx"], g["sy"] = 0.95, 1.06
        return g
    g["in_cart"] = True
    if t < T_ROLL + 0.15:
        cx = cart_x(t)
        g["x"] = cx
        g["rot"] = tower_rot(t)
        g["y"] = RIM - 55
        s1 = squash(t, T_JUMP1, 0.3, 0.2)
        g["sx"], g["sy"] = s1
        g["ex"], g["kind"] = "x", "strain"
        g["red"] = 0.25
        g["look"] = (0, -1)
        g["hL"] = (cx - 118, RIM - 2)
        g["hR"] = (cx + 118, RIM - 2)
        if t >= T_GOT:
            g["kind"] = "grin"
            g["red"] = 0
        if t >= T_ROLL:
            g["ex"], g["kind"] = "shock", None
            g["look"] = (1, 0.5)
        return g
    if t < T_BACK0:
        g["x"] = cart_x(t)
        g["y"] = RIM - 55
        g["ex"] = "shock"
        g["rot"] = -10
        g["hL"] = (g["x"] - 118, RIM - 2)
        g["hR"] = (g["x"] - 40, g["y"] - 200)
        return g
    g["in_cart"] = False
    GXE = 740.0
    if t < T_SEE:
        p = seg(t, T_BACK0, T_BACK1)
        g["x"] = lerp(1250, GXE, eout(p))
        g["y"] = GY - 30 * abs(math.sin(p * math.pi * 3))
        g["rot"] = -20 * math.sin(p * math.pi * 3) * (1 - p)
        g["ex"], g["kind"] = "x", "dizzy"
        return g
    if t < T_DIVE0:
        g["x"] = GXE
        g["ex"], g["look"] = "shock", (-1, 0.7)
        g["sx"], g["sy"] = squash(t, T_SEE, 0.25, 0.12)
        return g
    if t < T_RIP:
        p = eio(seg(t, T_DIVE0, T_DIVE1))
        tug = seg(t, T_DIVE1, T_RIP)
        g["x"] = lerp(GXE, 735, p) + 45 * tug
        g["rot"] = 14 * tug + 3 * math.sin(t * 40) * tug
        g["ex"], g["kind"] = "x", "strain"
        g["red"] = 0.6 * tug
        g["look"] = (-1, 0.5)
        px, _, w = pack_floor(t)
        g["hR"] = (px + w / 2 + 6, FLOOR - 70)
        g["hL"] = (px + w / 2 + 2, FLOOR - 120)
        if t < T_DIVE1:
            g["hR"] = lerp2((g["x"] - 60, g["y"]), g["hR"], p)
            g["hL"] = lerp2((g["x"] - 60, g["y"] - 40), g["hL"], p)
        return g
    # after the rip
    p = seg(t, T_RIP, T_LAND2)
    g["x"] = lerp(780, 825, eout(p))
    g["y"] = GY - 60 * math.sin(math.pi * p)
    g["rot"] = lerp(14, 0, eout(p))
    g["red"] = 0.6 * (1 - p)
    if p >= 1:
        g["sx"], g["sy"] = squash(t, T_LAND2, 0.3, 0.16)
    g["ex"] = "shock"
    g["look"] = (-0.6, 0)
    hx, hy = g["x"] - 125, g["y"] - 50
    if p < 1:
        hx, hy = bodypt(g["x"], g["y"], GS, g["rot"], 1, 1, -150, -40)
    g["hR"] = (hx, hy)
    g["half"] = (hx - 64, hy - 40, 0, turnf(t, T_TURN0))
    if t >= T_TURN0:
        g["look"] = (-1, 0)
    if t >= T_TURN1:
        g["ex"] = "suspicious"
    if t >= T_LOOK:
        g["ex"], g["kind"] = "x", "flat"
        g["look"] = (-1, 0)
        droop = eio(seg(t, T_LOOK, T_LOOK + 0.4))
        g["hR"] = (g["x"] - 125, g["y"] - 50 + 70 * droop)
        g["half"] = (g["x"] - 189, g["y"] - 90 + 90 * droop, -20 * droop, -1)
    if t >= T_TUBE_HIT:
        g["sx"], g["sy"] = squash(t, T_TUBE_HIT, 0.3, 0.15)
        g["ex"], g["kind"] = ("shock", None) if t < T_TUBE_HIT + 0.35 else ("x", "flat")
        g["look"] = (-0.6, 0.6) if t >= T_TUBE_HIT + 0.35 else (0, -1)
    return g


def nibbo_state(t, g):
    n = dict(x=NX0, y=NY, rot=0.0, sx=1.0, sy=1.0, ex="happy", kind=None, hL=None, hR=None, half=None, carry=False)
    if t < T_IN:
        p = eout(seg(t, -0.35, T_IN))
        n["x"] = lerp(1250, NX0, p)
        n["y"] = NY - 14 * abs(math.sin(t * 17))
        n["rot"] = -8 * (1 - p)
        n["ex"], n["kind"] = "blank", "lookup"
        return n
    if t < T_EACH:
        n["ex"], n["kind"] = ("wow", None) if t < T_UP + 0.25 else ("blank", "lookup")
        n["sx"], n["sy"] = squash(t, T_IN, 0.3, 0.16)
        return n
    if t < HOP_N[0]:
        n["ex"], n["kind"] = "blank", "lookleft"
        return n
    if t < T_IDEA_N:
        n["ex"], n["kind"] = "blank", "lookup"
        for h in HOP_N:
            if h <= t < h + HOP_D:
                p = seg(t, h, h + HOP_D)
                n["y"] = NY - 130 * math.sin(math.pi * p)
                n["hL"] = (n["x"] - 60, n["y"] - 165 - 25 * math.sin(math.pi * p))
                n["sx"], n["sy"] = 0.92, 1.1
                n["ex"], n["kind"] = "blank", "effort"
            elif h + HOP_D <= t < h + HOP_D + 0.15:
                n["sx"], n["sy"] = squash(t, h + HOP_D, 0.15, 0.15)
        return n
    if t < T_CLIMB0:
        n["ex"], n["kind"] = "blank", "sparkle"
        n["sx"], n["sy"] = squash(t, T_IDEA_N, 0.25, 0.15)
        if T_POINT0 <= t < T_POINT1:
            q = seg(t, T_POINT0, T_POINT1)
            a = (GX0 + 40, GY - 150)
            b = (n["x"] - 60, n["y"] - 220)
            n["hL"] = lerp2(a, b, eio(cl(q * 2 - 0.6))) if q > 0.3 else lerp2((n["x"] - 90, n["y"] + 20), a, eio(q / 0.3))
            n["ex"], n["kind"] = "happy", None
        return n
    head_y = lambda: GY - GR - NR + 10
    if t < T_CLIMB1:
        p = seg(t, T_CLIMB0, T_CLIMB1)
        n["x"] = lerp(NX0, TOWER_X, eio(p))
        n["y"] = lerp(NY, head_y(), p) - 160 * math.sin(math.pi * p)
        n["rot"] = -360 * eio(p)
        n["ex"] = "joy"
        return n
    if t < T_JUMP0:
        n["x"] = TOWER_X + 6 * math.sin(t * 9)
        n["rot"] = -6 * math.sin(t * 9)
        stretch = 1 + 0.12 * eio(seg(t, T_REACH0, T_REACH0 + 0.5))
        n["sy"], n["sx"] = stretch, 1 / stretch ** 0.5
        base_y = GY - GR + 8
        n["y"] = base_y - NR * n["sy"]
        n["ex"], n["kind"] = "blank", "effort"
        jit = 10 * math.sin(t * 34)
        n["hL"] = (n["x"] - 30, n["y"] - NR * n["sy"] - 100 + jit)
        n["hR"] = (n["x"] + 70, n["y"] - 60)
        if t >= T_REACH1:
            n["sy"], n["sx"] = 1.0, 1.0
            n["y"] = base_y - NR
            n["hL"], n["hR"] = None, None
            n["ex"], n["kind"] = "blank", "lookdown"
            n["rot"] = 0
            n["x"] = TOWER_X
        if t >= T_ARM0:
            n["ex"], n["kind"] = "blank", "lookright"
        return n
    if t < T_JUMP1 + 0.15:
        gtop = g["y"] - GR * g["sy"] + 8
        p = seg(t, T_JUMP0, T_JUMP1 + 0.15)
        n["x"] = g["x"]
        n["y"] = gtop - NR - 70 * math.sin(math.pi * p)
        n["ex"] = "wow"
        n["hL"] = (n["x"] - 110, n["y"] - 60)
        n["hR"] = (n["x"] + 110, n["y"] - 60)
        return n
    if t < T_ROLL + 0.15:
        a = math.radians(g["rot"])
        gtop = (g["x"] + GR * g["sy"] * math.sin(a), g["y"] - GR * g["sy"] * math.cos(a) + 8)
        n["rot"] = g["rot"] - 2.2 * g["rot"]
        reach = eio(seg(t, T_JUMP1 + 0.2, T_TOUCH))
        n["sy"] = 1 + 0.22 * reach
        n["sx"] = 1 / n["sy"] ** 0.5
        n["x"] = gtop[0]
        n["y"] = gtop[1] - NR * n["sy"]
        n["ex"], n["kind"] = "blank", "effort"
        tip = (n["x"] + 10, n["y"] - NR * n["sy"] - 80)
        n["hL"] = (lerp(n["x"] - 60, PACK_X - 20, reach), lerp(n["y"] - 60, TOP + 6, reach))
        n["hR"] = (n["x"] + 80, n["y"] - 20)
        if t >= T_TOUCH:
            n["hL"] = (PACK_X - 22 + 4 * math.sin(t * 30), TOP + 6)
        if t >= T_GRAB:
            q = eio(seg(t, T_GRAB, T_GOT))
            n["hL"] = (PACK_X - 60, lerp(TOP + 6, TOP + 30, q))
            n["hR"] = (PACK_X + 60, lerp(TOP + 6, TOP + 30, q))
            n["carry"] = True
        if t >= T_GOT:
            n["ex"], n["kind"] = "joy", None
            q = eio(seg(t, T_GOT, T_GOT + 0.3))
            n["sy"] = lerp(1.22, 1.0, q)
            n["sx"] = 1 / n["sy"] ** 0.5
            n["y"] = gtop[1] - NR * n["sy"]
            up = n["y"] - NR - 60
            n["hL"] = (n["x"] - 60, lerp(TOP + 30, up, q))
            n["hR"] = (n["x"] + 60, lerp(TOP + 30, up, q))
            n["x"] = n["x"] + 6 * math.sin(t * 12) * q
        return n
    # cart rolled away: cartoon hang, then fall
    hang_x = cart_x(T_ROLL + 0.15)
    hang_y = RIM - 55 - GR + 8 - NR
    if t < T_HANG1:
        n["x"], n["y"] = hang_x, hang_y
        n["ex"], n["kind"] = "blank", "lookdown"
        if t >= T_GONE - 0.1:
            n["ex"], n["kind"] = "uhoh", None
        n["hL"] = (n["x"] - 60, n["y"] - NR - 60)
        n["hR"] = (n["x"] + 60, n["y"] - NR - 60)
        n["carry"] = True
        return n
    if t < T_FALL1:
        p = seg(t, T_HANG1, T_FALL1)
        n["x"] = lerp(hang_x, 420, p)
        n["y"] = lerp(hang_y, NY, ein(p))
        n["ex"] = "wow"
        n["sx"], n["sy"] = 0.9, 1.12
        n["hL"] = (n["x"] - 70, n["y"] - NR - 70)
        n["hR"] = (n["x"] + 50, n["y"] - NR - 70)
        n["carry"] = True
        return n
    NXL = 420.0
    n["x"] = NXL
    if t < T_SEE:
        n["sx"], n["sy"] = squash(t, T_FALL1, 0.35, 0.3)
        n["ex"] = "dizzy" if t < T_BACK1 - 0.2 else "happy"
        if t >= T_BACK1 - 0.2:
            n["ex"], n["kind"] = "blank", "lookright"
        return n
    if t < T_DIVE0:
        n["ex"] = "wow"
        n["sx"], n["sy"] = squash(t, T_SEE, 0.25, 0.14)
        return n
    if t < T_RIP:
        p = eio(seg(t, T_DIVE0, T_DIVE1))
        tug = seg(t, T_DIVE1, T_RIP)
        n["x"] = lerp(NXL, 390, p) - 45 * tug
        n["rot"] = -14 * tug + 3 * math.sin(t * 43) * tug
        n["ex"], n["kind"] = "blank", "effort"
        px, _, w = pack_floor(t)
        n["hL"] = (px - w / 2 - 6, FLOOR - 70)
        n["hR"] = (px - w / 2 - 2, FLOOR - 120)
        if t < T_DIVE1:
            n["hL"] = lerp2((n["x"] + 50, n["y"]), n["hL"], p)
            n["hR"] = lerp2((n["x"] + 50, n["y"] - 40), n["hR"], p)
        return n
    p = seg(t, T_RIP, T_LAND2)
    n["x"] = lerp(345, 298, eout(p))
    n["y"] = NY - 70 * math.sin(math.pi * p)
    n["rot"] = lerp(-14, -360, eout(p))
    if p >= 1:
        n["rot"] = 0
        n["sx"], n["sy"] = squash(t, T_LAND2, 0.3, 0.2)
    n["ex"] = "wow"
    hx, hy = n["x"] + 115, n["y"] - 45
    if p < 1:
        hx, hy = bodypt(n["x"], n["y"], 1, n["rot"], 1, 1, 130, -30)
    n["hR"] = (hx, hy)
    n["half"] = (hx + 64, hy - 40, 0, turnf(t, T_TURN0 + 0.08))
    if t >= T_TURN0:
        n["ex"], n["kind"] = "blank", "lookright"
    if t >= T_LOOK:
        n["ex"], n["kind"] = "blank", "shrug"
    if T_TUBE0 <= t < T_TUBE_LAND + 0.3:
        n["ex"], n["kind"] = "wow", None
    return n


def turnf(t, t0):
    """front -> paper-thin edge (hold) -> cardboard back."""
    a = 0.5 * math.pi * eio(seg(t, t0, t0 + 0.25)) + 0.5 * math.pi * eio(seg(t, t0 + 0.6, t0 + 0.85))
    return math.cos(a)


def pack_floor(t):
    """pack on the floor / during tug: (x centre, y centre, width)."""
    tug = seg(t, T_DIVE1, T_RIP)
    w = PW * (1 + 0.28 * tug)
    return PACK_X, FLOOR - PH / 2 - 4, w


# ---------------------------------------------------------------- camera
CK = [(0.0, (560, 1010, 1.32)), (1.0, (560, 1010, 1.32)), (2.7, (560, 1020, 1.32)), (3.6, (550, 1000, 1.3)),
      (5.2, (570, 990, 1.28)), (5.7, (690, 1000, 1.22)), (6.4, (580, 990, 1.28)), (7.6, (560, 975, 1.33)),
      (8.6, (560, 985, 1.33)), (9.3, (650, 1040, 1.24)), (9.9, (560, 1110, 1.32)), (10.9, (575, 1170, 1.42)),
      (12.5, (566, 1175, 1.42)), (13.3, (566, 1170, 1.4)), (14.5, (566, 1165, 1.4)), (DUR, (566, 1175, 1.42))]
SHAKES = [(T_CLIMB1, 6, 0.2), (T_JUMP1, 10, 0.25), (T_GONE, 18, 0.4), (T_FALL1, 10, 0.25), (T_PACK_LAND, 5, 0.15),
          (T_RIP, 14, 0.3), (T_TUBE_HIT, 6, 0.2)]


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
    g = grumpo_state(t)
    n = nibbo_state(t, g)
    L = [store(t)]

    # holy glow around the last pack while it sits on the shelf
    if t < T_GRAB:
        glow = 0.7 + 0.3 * math.sin(t * 6)
        L.append(f'<circle cx="{PACK_X}" cy="{TOP-75}" r="{190 + 10*math.sin(t*6):.0f}" fill="url(#holy)" opacity="{glow:.2f}"/>')
        for k in range(6):
            a = t * 0.6 + k * math.pi / 3
            L.append(f'<path d="M{PACK_X + 95*math.cos(a):.0f} {TOP-75 + 95*math.sin(a):.0f} L{PACK_X + 170*math.cos(a+0.08):.0f} {TOP-75 + 170*math.sin(a+0.08):.0f} '
                     f'L{PACK_X + 170*math.cos(a-0.08):.0f} {TOP-75 + 170*math.sin(a-0.08):.0f}Z" fill="#fff6b0" opacity="0.45"/>')
    # the pack
    if t < T_GRAB:
        wig = 0
        dx = 0
        if t >= T_TOUCH:
            wig = 6 * math.sin((t - T_TOUCH) * 30)
            dx = 0
        L.append(pack(PACK_X + dx, TOP - 75, wig))
        L.append(star_twinkle(PACK_X + 80, TOP - 140, (t * 0.9) % 1))
        L.append(star_twinkle(PACK_X - 90, TOP - 40, (t * 0.9 + 0.5) % 1))

    # cart
    cx = cart_x(t)
    crot = 0.0
    if T_ROLL <= t < T_GONE:
        crot = -4
    draw_cart = cx < 1450
    if draw_cart:
        L.append(shadow(cx, FLOOR + 6, 150, 1.0))
        L.append(cart_back(cx, crot))
    if T_ROLL + 0.15 <= t < T_GONE:
        L.append(speed_lines(cx - 200, RIM - 60, 0, 0.8))

    # shadows
    if not g["in_cart"] and g["x"] < 1300:
        L.append(shadow(g["x"], FLOOR + 6, 120, 1.0 if g["y"] > GY - 60 else 0.5))
    if n["y"] > NY - 200:
        L.append(shadow(n["x"], FLOOR + 6, 110, 1.0 if n["y"] > NY - 40 else 0.6))

    # Grumpo
    L.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "up", g["look"], g["rot"], g["sx"], g["sy"], drink=False, t=t))
    L.append(grumpo_extra(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], g["kind"], t, g["red"]))
    if draw_cart:
        L.append(cart_front(cx, crot))

    # pack on the floor / tug
    if T_PACK_LAND <= t < T_RIP:
        px, py, w = pack_floor(t)
        tug = seg(t, T_DIVE1, T_RIP)
        sk = 7 * math.sin(t * 23) * tug
        L.append(pack(px, py, 2 * math.sin(t * 31) * tug, w / PW, 1 - 0.08 * tug, sk))
        if tug > 0.5:
            # tear line starting
            k = (tug - 0.5) * 2
            L.append(f'<path d="M{px+2:.0f} {py-75:.0f} l-10 {30*k:.0f} l14 {28*k:.0f} l-12 {28*k:.0f}" fill="none" stroke="{OL}" stroke-width="4" opacity="{k:.2f}"/>')
    # bounce from Nibbo's hands to the floor
    if T_FALL1 <= t < T_PACK_LAND:
        p = seg(t, T_FALL1, T_PACK_LAND)
        x = lerp(420, PACK_X, p)
        y = lerp(NY - NR - 140, FLOOR - PH / 2 - 4, p) - 220 * math.sin(math.pi * p)
        L.append(pack(x, y, 300 * p))
    # landing squash
    if T_PACK_LAND <= t < T_PACK_LAND + 0.2 and t < T_DIVE1:
        pass

    # Nibbo
    L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"] if n["kind"] is None else "blank", rot=n["rot"], sx=n["sx"], sy=n["sy"]))
    L.append(nib_face(n["x"], n["y"], NR, n["rot"], n["sx"], n["sy"], n["kind"], t))
    if n["carry"] and n["hL"] and n["hR"]:
        hx = (n["hL"][0] + n["hR"][0]) / 2
        hy = (n["hL"][1] + n["hR"][1]) / 2
        L.append(pack(hx, hy - 62, 4 * math.sin(t * 10) if t >= T_GOT else 0))

    # torn halves
    if g["half"]:
        x, y, r, f = g["half"]
        L.append(half_pack(1, x, y, r, f, 1.3))
    if n["half"]:
        x, y, r, f = n["half"]
        L.append(half_pack(-1, x, y, r, f, 1.3))
    # ripping debris
    if T_RIP <= t < T_RIP + 0.6:
        q = seg(t, T_RIP, T_RIP + 0.6)
        for k in range(6):
            a = -math.pi / 2 + (k - 2.5) * 0.45
            x = PACK_X + 260 * q * math.cos(a)
            y = FLOOR - 120 + 260 * q * math.sin(a) + 300 * q * q
            L.append(f'<rect x="{x-9:.0f}" y="{y-6:.0f}" width="18" height="12" fill="#c99a5b" stroke="{OL}" stroke-width="3" transform="rotate({q*700+k*60:.0f} {x:.0f} {y:.0f})" opacity="{1-q:.2f}"/>')

    # empty cardboard tube
    if t >= T_TUBE0:
        hx, hy = bodypt(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], 0, -130)
        if t < T_TUBE_HIT:
            p = seg(t, T_TUBE0, T_TUBE_HIT)
            L.append(tube(hx, lerp(TOP + 20, hy - 34, ein(p)), 200 * p))
        elif t < T_TUBE_LAND:
            p = seg(t, T_TUBE_HIT, T_TUBE_LAND)
            x = lerp(hx, 560, p)
            y = lerp(hy - 34, FLOOR - 34, p) - 200 * math.sin(math.pi * p)
            L.append(tube(x, y, lerp(200, 720, p)))
        else:
            q = t - T_TUBE_LAND
            L.append(tube(560, FLOOR - 34, 12 * math.exp(-q * 4) * math.sin(q * 25)))

    # ---- arms + hands
    for side, key in ((1, "hR"), (-1, "hL")):
        if g[key]:
            hx = g[key][0]
            sd = 1 if hx > g["x"] + 10 else (-1 if hx < g["x"] - 10 else side)
            sx_, sy_ = bodypt(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], sd * 112, 30)
            L.append(arm(sx_, sy_, g[key][0], g[key][1], INK, 14, 20))
    for key in ("hR", "hL"):
        if g[key]:
            L.append(hand(*g[key], mix_hex(GFILL, "#ff6a52", g["red"]), OL, 19))
    for side, key in ((-1, "hL"), (1, "hR")):
        if n[key]:
            hx = n[key][0]
            sd = 1 if hx > n["x"] + 10 else (-1 if hx < n["x"] - 10 else side)
            sx_, sy_ = bodypt(n["x"], n["y"], 1, n["rot"], n["sx"], n["sy"], sd * 96, 26)
            L.append(arm(sx_, sy_, n[key][0], n[key][1], NS, 11, 16))
    for key in ("hL", "hR"):
        if n[key]:
            L.append(hand(*n[key], NB, NS, 15))
    # hands over the half they hold
    if g["half"] and g["hR"]:
        L.append(hand(*g["hR"], mix_hex(GFILL, "#ff6a52", g["red"]), OL, 19))
    if n["half"] and n["hR"]:
        L.append(hand(*n["hR"], NB, NS, 15))

    # ---- effects
    L.append(symbol(n["x"], n["y"] - 175, "!", seg(t, T_IDEA_N, T_IDEA_N + 0.55), "#ff9a20"))
    if T_POINT0 <= t < T_POINT1:
        L.append(star_twinkle(GX0 + 40, GY - GR - 60, seg(t, T_POINT0, T_POINT1)))
    L.append(symbol(g["x"] - 175, g["y"] - 40, "!", seg(t, T_IDEA_G, T_IDEA_G + 0.55), "#ff9a20"))
    L.append(impact(TOWER_X, GY - GR, seg(t, T_CLIMB1, T_CLIMB1 + 0.22)))
    if T_REACH0 + 0.4 <= t < T_REACH1:
        # the gap: dashed measure between hand and pack
        hy = n["hL"][1] if n["hL"] else TOP
        L.append(f'<path d="M{n["hL"][0]:.0f} {TOP+40} V{hy-24:.0f}" stroke="#e8402e" stroke-width="7" stroke-dasharray="14 12" stroke-linecap="round"/>')
    L.append(impact(cx, RIM - 40, seg(t, T_JUMP1, T_JUMP1 + 0.25)))
    if T_TOUCH <= t < T_GOT + 0.4:
        L.append(star_twinkle(PACK_X - 40, TOP - 20, seg(t, T_TOUCH, T_TOUCH + 0.5)))
    if T_GOT <= t < T_ROLL:
        q = seg(t, T_GOT, T_ROLL)
        L.append(star_twinkle(n["x"] - 120, n["y"] - 200, (q * 2.2) % 1))
        L.append(star_twinkle(n["x"] + 130, n["y"] - 240, (q * 2.2 + 0.5) % 1))
    L.append(symbol(g["x"] - 150, g["y"] - 120, "!", seg(t, T_ROLL, T_ROLL + 0.5)))
    if T_GONE <= t < T_GONE + 0.5:
        q = seg(t, T_GONE, T_GONE + 0.5)
        L.append(impact(1040, RIM - 40, q, "#fff6a8"))
        for k in range(4):
            a = math.pi + (k - 1.5) * 0.5
            L.append(f'<circle cx="{1030 + 220*q*math.cos(a):.0f}" cy="{RIM - 40 + 220*q*math.sin(a) + 160*q*q:.0f}" r="{14 - 3*k}" fill="{COLS[k]}" stroke="{OL}" stroke-width="3" opacity="{1-q:.2f}"/>')
    if T_HANG1 - 0.35 <= t < T_HANG1:
        L.append(symbol(n["x"] + 120, n["y"] - 120, "?", seg(t, T_HANG1 - 0.5, T_HANG1 + 0.1), "#3a8fd8"))
    L.append(impact(420, FLOOR - 20, seg(t, T_FALL1, T_FALL1 + 0.25)))
    if T_SEE <= t < T_DIVE0 + 0.2:
        L.append(symbol(PACK_X, FLOOR - PH - 90, "!", seg(t, T_SEE, T_SEE + 0.5)))
    L.append(impact(PACK_X, FLOOR - 100, seg(t, T_RIP, T_RIP + 0.3)))
    L.append(symbol(g["x"] + 20, g["y"] - 200, "?", seg(t, T_TURN1 - 0.1, T_TURN1 + 0.5), "#3a8fd8"))
    L.append(symbol(n["x"] + 10, n["y"] - 175, "?", seg(t, T_TURN1, T_TURN1 + 0.6), "#3a8fd8"))
    L.append(impact(g["x"], g["y"] - 120, seg(t, T_TUBE_HIT, T_TUBE_HIT + 0.22)))

    cx_, cy_, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx_:.1f} {-cy_:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{defs()}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g>'
           f'<rect width="{W}" height="{H}" fill="url(#vig)"/></svg>')
    return overlay(svg, hook_title(t + 0.12, "1 pack left. Can they", "REACH IT?"))


def build_sfx():
    sfx(0.0, "whoosh", 0.6, 1.1)
    sfx(0.05, "squeak_slide", 0.5, 1.2)
    sfx(0.1, "squeak_slide", 0.4, 1.5)
    sfx(T_UP, "shine", 0.7, 1.0)
    sfx(T_UP + 0.05, "gasp", 0.5, 1.2)
    sfx(T_EACH, "blip", 0.4, 0.9)
    for h in HOP_G:
        sfx(h, "boing", 0.5, 0.8)
        sfx(h + HOP_D, "thud", 0.4, 1.2)
    for h in HOP_N:
        sfx(h, "hop", 0.5, 1.4)
    sfx(HOP_G[-1] + HOP_D + 0.05, "pant", 0.5, 1.0)
    sfx(T_IDEA_N, "ding", 0.6, 1.3)
    sfx(T_POINT0 + 0.1, "blip", 0.4, 1.4)
    sfx(T_NOD, "grumble", 0.4, 1.1)
    sfx(T_SLIDE0, "squeak_slide", 0.4, 1.0)
    sfx(T_CLIMB0, "boing", 0.6, 1.3)
    sfx(T_CLIMB1, "thunk", 0.6, 1.0)
    sfx(T_REACH0 + 0.1, "stretch", 0.5, 1.2)
    sfx(T_REACH0 + 0.3, "strain", 0.5, 1.4)
    sfx(T_REACH0 + 0.8, "strain", 0.5, 1.2)
    sfx(T_REACH1 - 0.1, "blip_down", 0.5, 1.0)
    sfx(T_IDEA_G, "ding", 0.6, 1.0)
    sfx(T_ARM0, "stretch", 0.5, 1.0)
    sfx(T_YANK0, "zip", 0.6, 1.0)
    sfx(T_YANK0 + 0.02, "cart_rattle", 0.6, 1.2)
    sfx(T_JUMP0, "boing", 0.7, 1.0)
    sfx(T_JUMP1, "clank", 0.7, 1.0)
    sfx(T_JUMP1 + 0.02, "thud", 0.5, 1.0)
    for k in range(4):
        sfx(T_JUMP1 + 0.25 + k * 0.4, "squeak", 0.35, 0.8 + 0.1 * (k % 2))
    sfx(T_JUMP1 + 0.3, "wobble", 0.5, 1.0)
    sfx(T_TOUCH - 0.3, "stretch", 0.5, 1.4)
    sfx(T_TOUCH, "tap", 0.6, 1.0)
    sfx(T_GRAB, "rustle", 0.6, 1.2)
    sfx(T_GOT, "cheer", 0.6, 1.2)
    sfx(T_GOT + 0.05, "shine", 0.6, 1.2)
    sfx(T_ROLL, "squeak", 0.6, 0.7)
    sfx(T_ROLL + 0.1, "gasp", 0.6, 0.9)
    sfx(T_ROLL + 0.15, "cart_rattle", 0.8, 1.0)
    sfx(T_ROLL + 0.2, "zoom", 0.6, 1.0)
    sfx(T_GONE, "metal_crash", 1.0, 1.0)
    sfx(T_GONE + 0.1, "clatter", 0.6, 1.0)
    sfx(T_HANG1 - 0.3, "blip", 0.4, 1.6)
    sfx(T_HANG1, "slide_down", 0.6, 1.2)
    sfx(T_FALL1, "squish", 0.7, 1.1)
    sfx(T_FALL1 + 0.02, "thud", 0.6, 1.0)
    sfx(T_FALL1 + 0.05, "boing", 0.5, 1.5)
    sfx(T_PACK_LAND, "plop", 0.6, 0.9)
    for k in range(3):
        sfx(T_BACK0 + 0.1 + k * 0.22, "hop", 0.35, 0.9)
    sfx(T_SEE, "alert", 0.5, 1.0)
    sfx(T_DIVE0, "whoosh", 0.6, 1.2)
    sfx(T_DIVE1, "thud", 0.5, 1.2)
    sfx(T_DIVE1 + 0.1, "strain", 0.6, 1.0)
    sfx(T_DIVE1 + 0.15, "stretch", 0.5, 0.8)
    sfx(T_DIVE1 + 0.6, "strain", 0.6, 1.3)
    sfx(T_RIP - 0.35, "rip", 0.4, 1.4)
    sfx(T_RIP, "rip", 1.0, 1.0)
    sfx(T_RIP + 0.05, "whoosh", 0.5, 1.2)
    sfx(T_LAND2, "thud", 0.6, 1.0)
    sfx(T_LAND2 + 0.03, "squish", 0.5, 1.3)
    sfx(T_TURN0, "flutter", 0.4, 1.3)
    sfx(T_TURN1, "blip_down", 0.5, 0.9)
    sfx(T_TURN1 + 0.1, "gasp", 0.4, 1.1)
    sfx(T_LOOK + 0.2, "tick", 0.5, 1.0)
    sfx(T_TUBE0, "whoosh", 0.4, 1.6)
    sfx(T_TUBE_HIT, "tube", 0.9, 1.0)
    sfx(T_TUBE_LAND, "tube", 0.5, 1.3)
    sfx(T_TUBE_LAND + 0.15, "tube", 0.3, 1.5)
    sfx(T_TUBE_LAND + 0.6, "deflate", 0.4, 0.9)
