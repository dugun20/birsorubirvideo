"""Grumpo & Nibbo — Episode 20: The Golden Sushi (conveyor-belt sushi bar, 60 fps).

Structure M (loop: the belt brings the plate around again, one detail changes each lap) + LAP counter 1/3 -> 3/3.
Ending: a third party wins (the sushi bar's cat).
LAP 1: the golden sushi rolls by; both reach with chopsticks — a chopstick sword fight; the plate slips past.
       Nibbo hops on the belt and rides into the tunnel; Grumpo smugly moves his seat right next to the exit.
LAP 2: out comes Nibbo dressed as a nigiri (salmon slice hat, nori belt) carrying the golden plate on his head.
       Grumpo plucks the sushi and opens wide — Nibbo leaps up and snatches it off the chopsticks, CLACK on empty sticks.
       Grumpo charges along the belt, rams Nibbo at the tunnel: both tumble in — crash and clatter inside.
LAP 3: out rides the kitchen CAT, happily munching the golden sushi... followed by Grumpo & Nibbo rolled together
       into ONE giant maki roll. The cat tosses them the empty golden plate and winks. The roll gets stuck in the
       tunnel, squeezes, POP — the empty plate spins down on the tunnel roof.
"""
import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow
from hook import overlay, hook_title, counter

W, H, FPS = 1080, 1920, 60
GS = 0.92
GR = 130 * GS
NR = 112
INK = "#1a0a2e"
GFILL = "#9466e0"
NB, NS = "#ffd23c", "#3d2a12"

BELT = 1392                    # plate base line on the belt
L_EXIT, R_ENT = 200, 880       # tunnel mouths
V = 220.0                      # belt speed px/s
GX0, GY = 380.0, 1300.0
NX0, NY = 700.0, 1305.0
GXW = 470.0                    # Grumpo's waiting seat
RIDE_Y = BELT - NR * 0.95
CHOP = 175

# ---- times
T_CHOP_G, T_CHOP_N = 0.3, 0.45
T_CLASH0, T_CLASH1 = 0.7, 1.6
T_LOCK1 = 1.9
T_GONE1 = (R_ENT - 260) / V      # 2.82
T_GLARE = T_GONE1 + 0.05
T_IDEA_N = T_GONE1 + 0.35
T_HOP0, T_HOP1 = T_GONE1 + 0.5, T_GONE1 + 0.8
T_DASH1 = T_GONE1 + 1.15
T_SLIDE0, T_SLIDE1 = T_GONE1 + 0.75, T_GONE1 + 1.2
T_LAP2 = T_GONE1 + 1.8
T_DOUBLE = T_LAP2 + 0.35
T_PLUCK0, T_PLUCK1 = T_LAP2 + 0.55, T_LAP2 + 0.8
T_LIFT1 = T_LAP2 + 1.08
T_LEAP0, T_LEAP1 = T_LAP2 + 1.08, T_LAP2 + 1.38
T_SNATCH = T_LAP2 + 1.2
T_CHOMP = T_LAP2 + 1.45
LAND_X = 600.0
T_JUMPG0, T_JUMPG1 = T_LAP2 + 1.75, T_LAP2 + 1.95
T_RAM = T_LEAP1 + 1.1
T_IN = T_RAM + 0.12
T_LAP3 = T_IN + 1.13
T_ROLL0, T_ROLL1 = T_LAP3 + 2.25, T_LAP3 + 2.55
T_GULP = T_LAP3 + 2.6
T_TOSS0, T_TOSS1 = T_GULP + 0.1, T_GULP + 0.35
T_WINK = T_GULP + 0.55
MK_OFF = 380
MK_OUT = 392.0
MK_STUCK_X = 730
T_STUCK = T_ROLL1 + (MK_STUCK_X - MK_OUT) / V
T_POP0, T_POP1 = T_STUCK + 0.62, T_STUCK + 0.77
T_PLATE_LAND = T_POP0 + 0.55
T_PEEK = T_PLATE_LAND + 0.2
T_LOOP = T_PEEK + 0.9
DUR = T_LOOP + 1.35
CLACKS = [0.8, 1.02, 1.24, 1.44]

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


# ---------------------------------------------------------------- scripted positions
def gold_x(t):
    return 260 + V * t


def nib_ride_x(t):
    if t < T_LEAP0:
        return 140 + V * (t - T_LAP2)
    if t < T_LEAP1:
        return lerp(140 + V * (T_LEAP0 - T_LAP2), LAND_X, eio(seg(t, T_LEAP0, T_LEAP1)))
    return LAND_X + V * (t - T_LEAP1)


def cat_x(t):
    return 140 + V * (t - T_LAP3)


def maki_x(t):
    if t < T_ROLL0:
        return -400.0
    x = lerp(0, MK_OUT, eout(seg(t, T_ROLL0, T_ROLL1))) + V * max(0.0, t - T_ROLL1)
    if t >= T_STUCK:
        x = MK_STUCK_X - 8 * seg(t, T_STUCK, T_POP0) + 6 * math.sin((t - T_STUCK) * 18) * (t < T_POP0)
    if t >= T_POP0:
        x = lerp(MK_STUCK_X - 8, 1080, ein(seg(t, T_POP0, T_POP1)))
    return x


def lap(t):
    if t >= T_LOOP + 0.15:
        return 4
    return 3 if t >= T_LAP3 else (2 if t >= T_LAP2 else 1)


def maki2_x(t):
    return lerp(20, 390, eout(seg(t, T_LOOP, T_LOOP + 0.55)))


# ---------------------------------------------------------------- drawing helpers
def defs():
    return ('<linearGradient id="wood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c98a52"/><stop offset="1" stop-color="#a86a3a"/></linearGradient>'
            '<linearGradient id="wallW" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3e2c4"/><stop offset="1" stop-color="#e6cfa6"/></linearGradient>'
            '<linearGradient id="goldP" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff3a0"/><stop offset="0.5" stop-color="#ffcf3a"/><stop offset="1" stop-color="#e0a018"/></linearGradient>'
            '<radialGradient id="kitchen" cx="0.5" cy="0.7" r="0.7"><stop offset="0" stop-color="#7a4a2a"/><stop offset="1" stop-color="#3a2216"/></radialGradient>'
            '<radialGradient id="aura" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#fff6b0" stop-opacity="0.9"/><stop offset="1" stop-color="#fff6b0" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="vig" cx="0.5" cy="0.55" r="0.8"><stop offset="0.62" stop-color="#1a2030" stop-opacity="0"/><stop offset="1" stop-color="#1a2030" stop-opacity="0.3"/></radialGradient>')


def plate(x, y, col="#3a8fd8", s=1.0, gold=False, rx=None):
    rx = rx or 78
    fill = "url(#goldP)" if gold else col
    rim = "#b07a10" if gold else mix_hex(col, "#000000", 0.25)
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            f'<ellipse cx="0" cy="-8" rx="{rx}" ry="18" fill="{fill}" stroke="{OL}" stroke-width="5"/>'
            f'<ellipse cx="0" cy="-10" rx="{rx*0.66:.0f}" ry="10" fill="none" stroke="{rim}" stroke-width="4"/>'
            f'<path d="M{-rx*0.7:.0f} -16 q{rx*0.3:.0f} -6 {rx*0.6:.0f} -4" stroke="#ffffff" stroke-width="5" fill="none" opacity="0.6" stroke-linecap="round"/></g>')


def nigiri(x, y, s=1.0, rot=0.0, gold=True):
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
         f'<rect x="-40" y="-26" width="80" height="34" rx="16" fill="#ffffff" stroke="{OL}" stroke-width="5"/>'
         '<circle cx="-22" cy="-6" r="3" fill="#e8eef4"/><circle cx="6" cy="-2" r="3" fill="#e8eef4"/><circle cx="24" cy="-8" r="3" fill="#e8eef4"/>'
         f'<path d="M-50 -24 Q -46 -52 0 -50 Q 46 -50 52 -26 Q 30 -14 0 -18 Q -30 -16 -50 -24Z" fill="#ff8a4a" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
         '<path d="M-34 -42 q8 10 4 20 M-10 -48 q8 12 4 26 M14 -48 q8 12 4 26 M36 -40 q6 8 2 16" stroke="#ffd2b0" stroke-width="5" fill="none" stroke-linecap="round"/>']
    if gold:
        o.append('<circle cx="-20" cy="-44" r="4" fill="#ffe14a" stroke="#c88a10" stroke-width="1.5"/><circle cx="12" cy="-40" r="3.5" fill="#ffe14a" stroke="#c88a10" stroke-width="1.5"/>'
                 '<circle cx="30" cy="-34" r="3" fill="#ffe14a" stroke="#c88a10" stroke-width="1.5"/>')
    o.append('</g>')
    return "".join(o)


def maki_piece(x, y, col):
    return (f'<circle cx="{x}" cy="{y}" r="20" fill="#2a4a2a" stroke="{OL}" stroke-width="4"/>'
            f'<circle cx="{x}" cy="{y}" r="13" fill="#ffffff"/><circle cx="{x}" cy="{y}" r="6" fill="{col}"/>')


def filler(x, k):
    cols = ["#3a8fd8", "#e8402e", "#5fbf5a", "#9a6ae0"]
    c = cols[k % 4]
    o = [plate(x, BELT, c, 0.85)]
    if k % 2 == 0:
        o.append(maki_piece(x - 22, BELT - 30, "#ff8a4a") + maki_piece(x + 22, BELT - 30, "#5fbf5a"))
    else:
        o.append(nigiri(x, BELT - 12, 0.6, 0, False))
    return "".join(o)


def chopsticks(hx, hy, ang, gap=6.0, L=CHOP):
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    o = []
    for sgn in (-1, 1):
        x0, y0 = hx + nx * sgn * 6 - ux * 20, hy + ny * sgn * 6 - uy * 20
        x1, y1 = hx + ux * L + nx * sgn * gap * 0.5, hy + uy * L + ny * sgn * gap * 0.5
        o.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{OL}" stroke-width="11" stroke-linecap="round"/>'
                 f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#d9a35a" stroke-width="5" stroke-linecap="round"/>')
    return "".join(o)


def chop_hand(tip, ang, L=CHOP):
    a = math.radians(ang)
    return tip[0] - L * math.cos(a), tip[1] - L * math.sin(a)


def tunnel(x0, x1, shake=0.0, t=0.0):
    dx = shake * math.sin(t * 70)
    dy = shake * 0.6 * math.cos(t * 55)
    o = [f'<g transform="translate({dx:.1f} {dy:.1f})">']
    o.append(f'<rect x="{x0}" y="1238" width="{x1-x0}" height="208" rx="10" fill="url(#wood)" stroke="{OL}" stroke-width="6"/>'
             f'<rect x="{x0-10}" y="1228" width="{x1-x0+20}" height="26" rx="8" fill="#7a4a2a" stroke="{OL}" stroke-width="5"/>'
             f'<path d="M{x0+14} 1290 h{x1-x0-28} M{x0+14} 1350 h{x1-x0-28}" stroke="#8a5a30" stroke-width="4"/>')
    # little noren flap on the belt side
    side = x1 if x0 < 540 else x0
    sgn = -1 if x0 < 540 else 1
    for k in range(2):
        xx = side + sgn * (8 + k * 34)
        o.append(f'<rect x="{min(xx, xx - sgn*30):.0f}" y="1256" width="30" height="64" rx="4" fill="#2a3a7a" stroke="{OL}" stroke-width="4"/>')
    o.append(f'<circle cx="{(x0+x1)/2:.0f}" cy="1395" r="16" fill="#e8402e" stroke="{OL}" stroke-width="4"/><circle cx="{(x0+x1)/2:.0f}" cy="1395" r="6" fill="#ffffff"/>')
    o.append('</g>')
    return "".join(o)


def lantern(x, y, t):
    sw = 3 * math.sin(t * 1.5 + x)
    return (f'<g transform="rotate({sw:.1f} {x} {y-70})"><line x1="{x}" y1="{y-140}" x2="{x}" y2="{y-58}" stroke="{OL}" stroke-width="4"/>'
            f'<rect x="{x-22}" y="{y-62}" width="44" height="12" rx="3" fill="#2a2a2a"/>'
            f'<ellipse cx="{x}" cy="{y}" rx="44" ry="56" fill="#e8402e" stroke="{OL}" stroke-width="5"/>'
            f'<path d="M{x-40} {y-20} Q{x} {y-28} {x+40} {y-20} M{x-44} {y+4} Q{x} {y-2} {x+44} {y+4} M{x-38} {y+28} Q{x} {y+22} {x+38} {y+28}" stroke="#b02a1a" stroke-width="3" fill="none"/>'
            f'<ellipse cx="{x-14}" cy="{y-18}" rx="10" ry="18" fill="#ffffff" opacity="0.3"/>'
            f'<rect x="{x-22}" y="{y+52}" width="44" height="12" rx="3" fill="#2a2a2a"/></g>')


def bar(t, cat_peek=0.0, cat_tail=0.0):
    o = [f'<rect x="-900" y="-400" width="2900" height="1900" fill="url(#wallW)"/>']
    for x in range(-900, 2000, 160):
        o.append(f'<path d="M{x} -400 V1380" stroke="#d6bc8e" stroke-width="5"/>')
    o.append(f'<rect x="-900" y="1150" width="2900" height="30" fill="#a86a3a" stroke="{OL}" stroke-width="4"/>')
    # kitchen doorway with noren
    o.append(f'<rect x="440" y="880" width="200" height="300" fill="url(#kitchen)" stroke="{OL}" stroke-width="6"/>'
             f'<rect x="428" y="866" width="224" height="22" rx="6" fill="#7a4a2a" stroke="{OL}" stroke-width="5"/>')
    if cat_peek > 0:
        cy = 1180 - 70 * cat_peek
        o.append(f'<g transform="translate(540 {cy:.1f})"><path d="M-46 -24 L-34 -70 L-12 -40Z M46 -24 L34 -70 L12 -40Z" fill="#ff9f43" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>'
                 f'<ellipse cx="0" cy="0" rx="56" ry="46" fill="#ff9f43" stroke="{OL}" stroke-width="5"/>'
                 f'<ellipse cx="-18" cy="-6" rx="9" ry="11" fill="#fff36a" stroke="{OL}" stroke-width="3"/><ellipse cx="18" cy="-6" rx="9" ry="11" fill="#fff36a" stroke="{OL}" stroke-width="3"/>'
                 f'<ellipse cx="{-18 + 3*math.sin(t*3):.1f}" cy="-6" rx="3" ry="9" fill="{OL}"/><ellipse cx="{18 + 3*math.sin(t*3):.1f}" cy="-6" rx="3" ry="9" fill="{OL}"/></g>')
    if cat_tail > 0:
        sw = 20 * math.sin(t * 6)
        o.append(f'<path d="M600 1180 q{30+sw:.0f} -60 {10+sw:.0f} -{110*cat_tail:.0f}" fill="none" stroke="{OL}" stroke-width="22" stroke-linecap="round"/>'
                 f'<path d="M600 1180 q{30+sw:.0f} -60 {10+sw:.0f} -{110*cat_tail:.0f}" fill="none" stroke="#ff9f43" stroke-width="13" stroke-linecap="round"/>')
    for k in range(5):
        x = 448 + k * 40
        o.append(f'<rect x="{x}" y="884" width="36" height="140" rx="4" fill="#2a3a7a" stroke="{OL}" stroke-width="4"/>')
    o.append(f'<circle cx="540" cy="950" r="26" fill="#ffffff" stroke="{OL}" stroke-width="4"/><circle cx="540" cy="950" r="14" fill="#e8402e"/>')
    # wall menu boards (icons only)
    for bx in (170, 910):
        o.append(f'<rect x="{bx-90}" y="1010" width="180" height="110" rx="8" fill="#5a3a22" stroke="{OL}" stroke-width="5"/>')
        o.append(nigiri(bx - 40, 1080, 0.55, 0, False) + maki_piece(bx + 40, 1064, "#ff8a4a") + maki_piece(bx + 40, 1100, "#5fbf5a"))
    o.append(lantern(330, 1000, t) + lantern(750, 1000, t))
    # stools (only visible when seats are empty)
    return "".join(o)


def belt_layer(t):
    o = []
    # back rail + belt top surface
    o.append(f'<rect x="-900" y="1376" width="2900" height="18" fill="#b9c0cc" stroke="{OL}" stroke-width="4"/>')
    o.append(f'<rect x="-900" y="1392" width="2900" height="28" fill="#6a7280"/>')
    off = (V * t) % 60
    for x in range(-900, 2000, 60):
        xx = x + off
        o.append(f'<path d="M{xx:.0f} 1392 v28" stroke="#4a5160" stroke-width="5"/>')
    o.append(f'<rect x="-900" y="1418" width="2900" height="22" fill="#d9dee6" stroke="{OL}" stroke-width="5"/>')
    return "".join(o)


def counter_front():
    o = [f'<rect x="-900" y="1440" width="2900" height="700" fill="url(#wood)"/>',
         f'<path d="M-900 1440 H2000" stroke="{OL}" stroke-width="6"/>']
    for x in range(-900, 2000, 140):
        o.append(f'<path d="M{x} 1450 V2140" stroke="#9a5e32" stroke-width="5"/>')
    o.append(f'<rect x="-900" y="1500" width="2900" height="14" fill="#8a5028"/>')
    return "".join(o)


def cat(x, y, s=1.0, mood="happy", t=0.0, chew=0.0, holding=False, tilt=0.0):
    sw = 18 * math.sin(t * 5)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({tilt:.1f}) scale({s:.3f})">']
    o.append(f'<path d="M50 30 Q 120 10 {100+sw:.0f} -60 Q {96+sw:.0f} -80 {110+sw:.0f} -90" fill="none" stroke="{OL}" stroke-width="24" stroke-linecap="round"/>'
             f'<path d="M50 30 Q 120 10 {100+sw:.0f} -60 Q {96+sw:.0f} -80 {110+sw:.0f} -90" fill="none" stroke="#ff9f43" stroke-width="14" stroke-linecap="round"/>')
    o.append(f'<path d="M-62 -40 L-48 -104 L-14 -66Z M62 -40 L48 -104 L14 -66Z" fill="#ff9f43" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
             '<path d="M-52 -56 L-46 -86 L-30 -66Z M52 -56 L46 -86 L30 -66Z" fill="#ffb0c0"/>')
    o.append(f'<ellipse cx="0" cy="0" rx="86" ry="76" fill="#e07f22" stroke="{OL}" stroke-width="6"/>'
             f'<ellipse cx="-6" cy="-6" rx="80" ry="68" fill="#ff9f43"/>'
             f'<ellipse cx="0" cy="40" rx="50" ry="30" fill="#ffe2bc"/>'
             f'<path d="M-14 -70 v18 M0 -74 v22 M14 -70 v18" stroke="#c8641a" stroke-width="7" stroke-linecap="round"/>'
             f'<ellipse cx="0" cy="0" rx="86" ry="76" fill="none" stroke="{OL}" stroke-width="6"/>')
    # cheeks puff when chewing
    cb = 6 * chew
    o.append(f'<ellipse cx="{-34-cb:.1f}" cy="16" rx="{24+cb:.1f}" ry="{18+cb*0.6:.1f}" fill="#fff0dc"/><ellipse cx="{34+cb:.1f}" cy="16" rx="{24+cb:.1f}" ry="{18+cb*0.6:.1f}" fill="#fff0dc"/>')
    if mood == "wink":
        o.append(f'<path d="M-40 -14 q12 -12 24 0" fill="none" stroke="{OL}" stroke-width="6" stroke-linecap="round"/>'
                 f'<ellipse cx="28" cy="-12" rx="10" ry="13" fill="#7ad06a" stroke="{OL}" stroke-width="3"/><ellipse cx="28" cy="-12" rx="4" ry="10" fill="{OL}"/><circle cx="31" cy="-17" r="2.5" fill="#fff"/>')
    else:
        o.append(f'<path d="M-40 -10 q12 -14 24 0 M16 -10 q12 -14 24 0" fill="none" stroke="{OL}" stroke-width="6" stroke-linecap="round"/>')
    o.append(f'<path d="M-7 4 h14 l-7 8z" fill="#ff7fa0" stroke="{OL}" stroke-width="3" stroke-linejoin="round"/>'
             f'<path d="M-14 18 q7 8 14 0 q7 8 14 0" fill="none" stroke="{OL}" stroke-width="4" stroke-linecap="round"/>'
             f'<path d="M-36 8 l-46 -6 M-36 16 l-44 8 M36 8 l46 -6 M36 16 l44 8" stroke="{OL}" stroke-width="3" stroke-linecap="round"/>'
             '<ellipse cx="-52" cy="14" rx="10" ry="5" fill="#ff7fa0" opacity="0.5"/><ellipse cx="52" cy="14" rx="10" ry="5" fill="#ff7fa0" opacity="0.5"/>')
    if holding:
        o.append(nigiri(0, 48, 0.62, 0, True))
        o.append(f'<circle cx="-30" cy="46" r="15" fill="#ff9f43" stroke="{OL}" stroke-width="4"/><circle cx="30" cy="46" r="15" fill="#ff9f43" stroke="{OL}" stroke-width="4"/>')
    else:
        o.append(f'<circle cx="-34" cy="66" r="15" fill="#ff9f43" stroke="{OL}" stroke-width="4"/><circle cx="34" cy="66" r="15" fill="#ff9f43" stroke="{OL}" stroke-width="4"/>')
    o.append('</g>')
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
    elif kind == "tongue":
        o.append(f'<path d="M-60 2 h46 v34 h-46z" fill="{base}"/>'
                 f'<path d="M-58 20 q20 -14 40 0" fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M-72 -26 Q -44 -22 -16 -14 M72 -36 Q 44 -30 16 -18" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<path d="M-30 64 q34 18 64 -4" fill="none" stroke="{ink}" stroke-width="10" stroke-linecap="round"/>'
                 f'<path d="M{18+6*math.sin(t*14):.1f} 70 q2 22 16 22 q14 0 12 -26" fill="#ff6a8a" stroke="{ink}" stroke-width="6" stroke-linejoin="round"/>')
    elif kind == "strain":
        o.append(f'<path d="M-76 -40 L -18 -8 M76 -40 L 18 -8" fill="none" stroke="{ink}" stroke-width="18" stroke-linecap="round"/>'
                 f'<rect x="-40" y="58" width="80" height="34" rx="12" fill="#fff" stroke="{ink}" stroke-width="7"/>'
                 f'<path d="M-36 75 h72 M-14 60 v30 M12 60 v30" stroke="{ink}" stroke-width="4"/>')
    elif kind == "flat":
        o.append(f'<path d="M-60 6 h44 v30 h-44z M16 6 h44 v30 h-44z" fill="{base}"/>'
                 f'<path d="M-58 22 h40 M18 22 h40" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M-70 -10 Q -44 -14 -16 -8 M70 -10 Q 44 -14 16 -8" fill="none" stroke="{ink}" stroke-width="14" stroke-linecap="round"/>'
                 f'<path d="M-26 76 h52" stroke="{ink}" stroke-width="9" stroke-linecap="round"/>')
    elif kind == "chomp":
        o.append(f'<path d="M-78 -40 L -20 -6 M78 -40 L 20 -6" fill="none" stroke="{ink}" stroke-width="20" stroke-linecap="round"/>'
                 f'<path d="M-50 52 h100 v30 h-100z" fill="#fff" stroke="{ink}" stroke-width="7"/>'
                 f'<path d="M-50 67 h100 M-25 52 v30 M0 52 v30 M25 52 v30" stroke="{ink}" stroke-width="4"/>')
    o.append('</g>')
    return "".join(o)


def nib_face(x, y, r, rot, sx, sy, kind, t=0.0):
    if not kind:
        return ""
    f = r / 48 * 1.05
    d = "#2a1a10"
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx*f:.3f} {sy*f:.3f})">']
    if kind in ("lookup", "lookleft", "lookright", "lookdown", "madleft"):
        dx, dy = {"lookup": (0, -4), "lookleft": (-4, 1), "lookright": (4, 1), "lookdown": (0, 4), "madleft": (-4, 1)}[kind]
        o.append(f'<ellipse cx="-14" cy="-4" rx="7" ry="9" fill="#fff" stroke="{d}" stroke-width="2"/><ellipse cx="14" cy="-4" rx="7" ry="9" fill="#fff" stroke="{d}" stroke-width="2"/>'
                 f'<circle cx="{-14+dx}" cy="{-4+dy}" r="4.5" fill="{d}"/><circle cx="{14+dx}" cy="{-4+dy}" r="4.5" fill="{d}"/>')
        if kind == "madleft":
            o.append(f'<path d="M-24 -20 l12 5 M24 -20 l-12 5" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                     f'<path d="M-8 18 q8 -6 16 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
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
                 f'<path d="M-12 16 q4 -5 8 0 t8 0 t8 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    elif kind == "sparkle":
        o.append(f'<path d="M-21 -2 q7 -10 14 0 M7 -2 q7 -10 14 0" fill="none" stroke="{d}" stroke-width="5" stroke-linecap="round"/>'
                 f'<path d="M-12 8 q12 18 24 0z" fill="#7a2a1a" stroke="{d}" stroke-width="4" stroke-linejoin="round"/>')
    elif kind == "tease":
        o.append(f'<path d="M-21 -2 q7 -10 14 0" fill="none" stroke="{d}" stroke-width="5" stroke-linecap="round"/>'
                 f'<ellipse cx="14" cy="-4" rx="6" ry="8" fill="{d}"/><circle cx="16" cy="-7" r="2.2" fill="#fff"/>'
                 f'<path d="M-10 10 q10 8 20 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>'
                 f'<path d="M-4 13 q0 14 8 14 q8 0 7 -15" fill="#ff6a8a" stroke="{d}" stroke-width="3"/>')
    o.append('</g>')
    return "".join(o)


def nibbo_costume(x, y, r, rot, sx, sy, t):
    """nori belt + salmon-slice hat (Nibbo dressed as a nigiri)."""
    k = r / NR
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx*k:.3f} {sy*k:.3f})">'
            f'<path d="M-104 48 Q 0 70 104 48 L100 82 Q 0 104 -100 82Z" fill="#24402a" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M-90 62 Q 0 80 90 62" stroke="#3a6040" stroke-width="5" fill="none"/>'
            f'<path d="M-118 -66 Q -100 -128 0 -128 Q 100 -128 118 -66 Q 70 -82 0 -84 Q -70 -82 -118 -66Z" fill="#ff8a4a" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            '<path d="M-78 -112 q14 14 6 30 M-30 -124 q14 16 6 36 M24 -124 q14 16 6 36 M74 -110 q10 12 4 26" stroke="#ffd2b0" stroke-width="7" fill="none" stroke-linecap="round"/></g>')


# ---------------------------------------------------------------- states
def grumpo_state(t):
    g = dict(x=GX0, y=GY, rot=0.0, sx=1.0, sy=1.0, ex="grumpy", kind=None, look=(-1, 0.4), red=0.0,
             hR=None, chop=None, ride=False, show=True, sushi=False)
    rest = lambda: ((g["x"] + 120, 1385), -10)
    if t < T_CHOP_G:
        g["look"] = (cl((gold_x(t) - g["x"]) / 250, -1, 1), 0.6)
        g["ex"] = "suspicious"
        tip, ang = rest()
        g["chop"] = (tip, ang, 6)
        return g
    if t < T_GONE1 + 0.05:
        px = gold_x(t)
        g["look"] = (cl((px - g["x"]) / 250, -1, 1), 0.6)
        g["ex"] = "angry"
        ang = 22
        if t < T_CLASH0:
            q = eio(seg(t, T_CHOP_G, T_CLASH0))
            tip = lerp2(rest()[0], (px - 8, BELT - 40), q)
            ang = lerp(-10, 22, q)
        elif t < T_CLASH1:
            k = (t - T_CLASH0)
            tip = (px - 8 + 26 * math.sin(k * 14), BELT - 50 - 30 * abs(math.sin(k * 14)))
            g["red"] = 0.3
            g["rot"] = 3 * math.sin(k * 14)
        elif t < T_LOCK1:
            tip = (gold_x(T_CLASH1) + 4 + 3 * math.sin(t * 60), BELT - 70)
            g["ex"], g["kind"] = "x", "strain"
            g["red"] = 0.45
        else:
            q = eio(seg(t, T_LOCK1, T_LOCK1 + 0.2))
            tip = lerp2((gold_x(T_CLASH1) + 4, BELT - 70), (g["x"] + 230, BELT - 120), q)
            ang = lerp(22, -20, q)
            g["ex"] = "shock"
            g["look"] = (1, 0.2)
        g["chop"] = (tip, ang, 2 if T_CLASH1 <= t < T_LOCK1 else 6)
        return g
    if t < T_HOP0:
        g["ex"], g["look"] = "angry", (1, 0)
        g["red"] = 0.5 * seg(t, T_GLARE, T_GLARE + 0.15)
        g["rot"] = 2 * math.sin(t * 40) * (t >= T_GLARE)
        g["chop"] = ((g["x"] + 160, BELT - 110), -30, 6)
        return g
    if t < T_LAP2:
        g["red"] = 0.5 * (1 - seg(t, T_HOP0, T_SLIDE0))
        g["look"] = (1, -0.2) if t < T_SLIDE0 else (-1, 0.4)
        g["ex"] = "suspicious" if t < T_SLIDE0 else "smug"
        p = eio(seg(t, T_SLIDE0, T_SLIDE1))
        g["x"] = lerp(GX0, GXW, p)
        g["rot"] = -8 * math.sin(math.pi * p)
        if t >= T_SLIDE1:
            g["ex"], g["kind"] = "x", "tongue"
            g["sx"], g["sy"] = squash(t, T_SLIDE1, 0.25, 0.1)
        click = 3 + 3 * math.sin(t * 25) if t >= T_SLIDE1 else 6
        g["chop"] = ((g["x"] - 120, BELT - 150), 200, click * 2)
        return g
    g["x"] = GXW
    g["y"] = GY - 90 * eio(seg(t, T_LAP2 - 0.4, T_LAP2 - 0.1))
    nx = nib_ride_x(t)
    if t < T_PLUCK0:
        g["look"] = (-1, 0.4)
        g["ex"], g["kind"] = "x", "tongue"
        g["chop"] = ((g["x"] - 120, BELT - 150), 200, 8)
        if t >= T_DOUBLE:
            g["ex"], g["kind"] = "shock", None
            g["look"] = (cl((nx - g["x"]) / 200, -1, 1), 0.3)
            g["sx"], g["sy"] = squash(t, T_DOUBLE, 0.25, 0.18)
        return g
    if t < T_CHOMP:
        sp = sushi_on_nib(T_PLUCK1)
        g["look"] = (0.3, 0.3)
        if t < T_PLUCK1:
            q = eio(seg(t, T_PLUCK0, T_PLUCK1))
            tip = lerp2((g["x"] - 120, BELT - 150), sushi_on_nib(t), q)
            g["chop"] = (tip, lerp(200, 150, q), 8 if q < 0.8 else 2)
            g["ex"] = "smug"
        else:
            q = eio(seg(t, T_PLUCK1, T_LIFT1))
            tip = lerp2(sushi_on_nib(T_PLUCK1), (g["x"] + 18, g["y"] + 62), q)
            g["chop"] = (tip, lerp(150, 160, q), 2)
            g["ex"] = "smug" if q < 0.5 else "shock"
            g["look"] = (0.2, 0.5)
            g["sushi"] = t < T_SNATCH
            if t >= T_SNATCH:
                g["chop"] = ((g["x"] + 18, g["y"] + 62), 160, 2)
        return g
    if t < T_JUMPG0:
        g["sx"], g["sy"] = squash(t, T_CHOMP, 0.25, 0.14)
        g["ex"], g["kind"] = "x", "chomp"
        g["chop"] = ((g["x"] + 18, g["y"] + 62), 160, 0)
        if t >= T_CHOMP + 0.2:
            g["ex"], g["kind"] = "angry", None
            g["red"] = 0.8 * seg(t, T_CHOMP + 0.2, T_CHOMP + 0.4)
            g["rot"] = 3 * math.sin(t * 45)
            g["look"] = (1, 0.3)
            g["chop"] = ((g["x"] + 140, g["y"] - 40), -60, 0)
        return g
    g["red"] = 0.8
    g["ex"] = "angry"
    g["look"] = (1, 0.2)
    if t < T_JUMPG1:
        p = seg(t, T_JUMPG0, T_JUMPG1)
        g["x"] = lerp(GXW, 560, p)
        g["y"] = lerp(GY - 90, BELT - GR, p) - 160 * math.sin(math.pi * p)
        g["ride"] = True
        return g
    if t < T_RAM:
        p = seg(t, T_JUMPG1, T_RAM)
        g["x"] = lerp(560, R_ENT - 90, ein(p) * 0.4 + p * 0.6)
        g["y"] = BELT - GR - 10 * abs(math.sin(t * 22))
        g["rot"] = 400 * p
        g["ride"] = True
        return g
    if t < T_IN:
        p = seg(t, T_RAM, T_IN)
        g["x"] = lerp(R_ENT - 90, R_ENT + 60, p)
        g["y"] = BELT - GR
        g["ride"] = True
        g["ex"] = "shock"
        g["sx"], g["sy"] = 0.85, 1.1
        return g
    g["show"] = False
    return g


def sushi_on_nib(t):
    nx = nib_ride_x(t)
    return (nx + 4, RIDE_Y - NR - 58)


def nibbo_state(t):
    n = dict(x=NX0, y=NY, rot=0.0, sx=1.0, sy=1.0, ex="happy", kind=None, hL=None, hR=None, chop=None,
             ride=False, show=True, costume=False, gold_on_head=False, sushi_head=False, sushi_hand=False)
    rest = ((n["x"] - 120, 1385), 190)
    if t < T_CHOP_N:
        n["ex"], n["kind"] = "blank", "lookleft"
        n["chop"] = (rest[0], rest[1], 6)
        return n
    if t < T_GONE1 + 0.05:
        px = gold_x(t)
        n["ex"], n["kind"] = "blank", ("lookleft" if px < n["x"] else "lookright")
        ang = 158
        if t < T_CLASH0:
            q = eio(seg(t, T_CHOP_N, T_CLASH0))
            tip = lerp2(rest[0], (px + 8, BELT - 40), q)
            ang = lerp(190, 158, q)
        elif t < T_CLASH1:
            k = (t - T_CLASH0)
            tip = (px + 8 - 26 * math.sin(k * 14 + 0.6), BELT - 50 - 30 * abs(math.sin(k * 14 + 0.6)))
            n["ex"], n["kind"] = "blank", "effort"
            n["rot"] = -3 * math.sin(k * 14)
        elif t < T_LOCK1:
            tip = (gold_x(T_CLASH1) - 4 + 3 * math.sin(t * 57), BELT - 74)
            n["ex"], n["kind"] = "blank", "effort"
        else:
            q = eio(seg(t, T_LOCK1, T_LOCK1 + 0.2))
            tip = lerp2((gold_x(T_CLASH1) - 4, BELT - 74), (n["x"] - 200, BELT - 120), q)
            ang = lerp(158, 200, q)
            n["ex"], n["kind"] = "wow", None
        n["chop"] = (tip, ang, 2 if T_CLASH1 <= t < T_LOCK1 else 6)
        return n
    if t < T_IDEA_N:
        n["ex"], n["kind"] = "blank", "madleft"
        n["chop"] = ((n["x"] - 150, BELT - 110), 210, 6)
        return n
    if t < T_HOP0:
        n["ex"], n["kind"] = "blank", "sparkle"
        n["sx"], n["sy"] = squash(t, T_IDEA_N, 0.2, 0.15)
        return n
    if t < T_HOP1:
        p = seg(t, T_HOP0, T_HOP1)
        n["x"] = lerp(NX0, 750, p)
        n["y"] = lerp(NY, RIDE_Y, p) - 150 * math.sin(math.pi * p)
        n["rot"] = 360 * eio(p)
        n["ex"] = "joy"
        n["ride"] = True
        return n
    if t < T_LAP2:
        p = seg(t, T_HOP1, T_DASH1)
        n["x"] = lerp(750, 1010, ein(p))
        n["y"] = RIDE_Y - 10 * abs(math.sin(t * 20))
        n["ex"] = "joy"
        n["ride"] = True
        if p >= 1:
            n["show"] = False
        return n
    # LAP 2: Nibbo rides out dressed as a nigiri
    n["ride"] = True
    n["costume"] = True
    n["gold_on_head"] = True
    nx = nib_ride_x(t)
    n["x"] = nx
    n["y"] = RIDE_Y - 4 * abs(math.sin(t * 6))
    if t < T_PLUCK0:
        n["sushi_head"] = True
        n["ex"] = "happy"
        n["hL"] = (nx - 100, n["y"] - 40 + 15 * math.sin(t * 14))
        return n
    if t < T_LEAP0:
        n["sushi_head"] = t < T_PLUCK1
        n["ex"], n["kind"] = ("blank", "lookleft") if t >= T_PLUCK1 else ("wow", None)
        return n
    if t < T_LEAP1:
        p = seg(t, T_LEAP0, T_LEAP1)
        sx0 = nib_ride_x(T_LEAP0)
        sx1 = nib_ride_x(T_LEAP1)
        peak = (GXW - 80, GY - 130)
        if p < 0.5:
            q = eout(p / 0.5)
            n["x"] = lerp(sx0, peak[0], q)
            n["y"] = lerp(RIDE_Y, peak[1], q)
        else:
            q = ein((p - 0.5) / 0.5)
            n["x"] = lerp(peak[0], sx1, q)
            n["y"] = lerp(peak[1], RIDE_Y, q)
        n["rot"] = -20 * math.sin(math.pi * p)
        n["ex"] = "joy"
        n["hL"] = lerp2((n["x"] + 60, n["y"] - 40), (GXW + 18, GY - 90 + 62), eio(seg(t, T_LEAP0, T_SNATCH))) if t < T_SNATCH else (n["x"] - 40, n["y"] - 140)
        n["sushi_hand"] = t >= T_SNATCH
        return n
    if t < T_RAM:
        n["sx"], n["sy"] = squash(t, T_LEAP1, 0.25, 0.15)
        n["ex"], n["kind"] = "blank", "tease"
        n["hL"] = (n["x"] - 30, n["y"] - 150 + 10 * math.sin(t * 12))
        n["sushi_hand"] = True
        if t >= T_RAM - 0.35:
            n["ex"], n["kind"] = "wow", None
        return n
    if t < T_IN:
        p = seg(t, T_RAM, T_IN)
        n["x"] = lerp(n["x"], R_ENT + 120, p)
        n["sx"], n["sy"] = 0.8, 1.15
        n["ex"] = "dizzy"
        n["sushi_hand"] = True
        n["hL"] = (n["x"] - 30, n["y"] - 150)
        return n
    n["show"] = False
    return n


# ---------------------------------------------------------------- camera
def _k(cx, z, dy=0.0):
    return (cx, 1392 - 490 / z + dy, z)


CK = [(0.0, _k(540, 1.45)), (0.7, _k(560, 1.55)), (1.8, _k(600, 1.52)), (T_GONE1, _k(580, 1.45)),
      (T_LAP2 - 0.6, _k(500, 1.45)), (T_LAP2 + 0.2, _k(440, 1.52)), (T_LAP2 + 1.1, _k(480, 1.52)), (T_LAP2 + 1.6, _k(580, 1.45)),
      (T_IN, _k(690, 1.45)), (T_LAP3 - 0.3, _k(680, 1.45)), (T_LAP3 + 0.3, _k(440, 1.5)), (T_LAP3 + 1.6, _k(520, 1.52)), (T_LAP3 + 2.3, _k(520, 1.5)),
      (T_LAP3 + 3.3, _k(640, 1.48)), (T_STUCK, _k(730, 1.5)), (T_PLATE_LAND, _k(780, 1.52)), (T_LOOP - 0.2, _k(810, 1.56)),
      (T_LOOP + 0.15, _k(430, 1.5)), (DUR, _k(430, 1.55))]
SHAKES = [(T_LOOP + 0.5, 8, 0.2), (T_CLASH1, 5, 0.2), (T_CHOMP, 8, 0.2), (T_RAM, 16, 0.3), (T_IN + 0.1, 12, 0.7), (T_STUCK, 8, 0.2),
          (T_POP0, 14, 0.3), (T_PLATE_LAND, 4, 0.15)]


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
def scripted_xs(t):
    xs = []
    if t < T_GONE1 + 0.1:
        xs.append(gold_x(t))
    if T_LAP2 <= t < T_IN:
        xs.append(nib_ride_x(t))
    if t >= T_LAP3:
        xs += [x for x in range(-400, int(cat_x(t)) + 1, 60)]
    if t >= T_LOOP - 0.5:
        xs += [maki2_x(t) - 130, maki2_x(t), maki2_x(t) + 130, maki2_x(t) + 260, 200, 330]
    return xs


def stool(x):
    return (f'<rect x="{x-14}" y="1300" width="28" height="90" fill="#7a4a2a" stroke="{OL}" stroke-width="4"/>'
            f'<ellipse cx="{x}" cy="1300" rx="70" ry="16" fill="#e8402e" stroke="{OL}" stroke-width="5"/>')


def frame(t):
    ctx = Ctx()
    g = grumpo_state(t)
    n = nibbo_state(t)
    peek = 0.0
    if T_GONE1 - 0.7 <= t < T_GONE1 + 0.9:
        peek = math.sin(math.pi * seg(t, T_GONE1 - 0.7, T_GONE1 + 0.9)) ** 0.5
    tail = 0.0
    if T_IN + 0.2 <= t < T_IN + 0.9:
        tail = math.sin(math.pi * seg(t, T_IN + 0.2, T_IN + 0.9))
    L = [bar(t, peek, tail)]
    # empty stools once they're gone
    if not g["show"] or g["ride"]:
        L.append(stool(GXW))
    if not n["show"] or n["ride"]:
        L.append(stool(NX0))
    if g["show"] and not g["ride"] and g["y"] < GY - 20:
        L.append(f'<rect x="{g["x"]-14:.0f}" y="{g["y"]+GR-8:.0f}" width="28" height="{BELT-g["y"]-GR+8:.0f}" fill="#7a4a2a" stroke="{OL}" stroke-width="4"/>'
                 f'<ellipse cx="{g["x"]:.0f}" cy="{g["y"]+GR-8:.0f}" rx="70" ry="16" fill="#e8402e" stroke="{OL}" stroke-width="5"/>')
    # seated characters (behind the belt)
    if g["show"] and not g["ride"]:
        L.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "up", g["look"], g["rot"], g["sx"], g["sy"], drink=False, t=t))
        L.append(grumpo_extra(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], g["kind"], t, g["red"]))
    if n["show"] and not n["ride"]:
        L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"] if n["kind"] is None else "blank", rot=n["rot"], sx=n["sx"], sy=n["sy"]))
        L.append(nib_face(n["x"], n["y"], NR, n["rot"], n["sx"], n["sy"], n["kind"], t))
    L.append(belt_layer(t))
    # filler plates riding the belt
    xs = scripted_xs(t)
    for k in range(5):
        x = L_EXIT - 120 + ((V * t + k * 300 + 40) % 1500)
        if x < L_EXIT - 90 or x > R_ENT + 90:
            continue
        if any(abs(x - s) < 175 for s in xs):
            continue
        L.append(filler(x, k))

    # ---- LAP 1 golden plate
    if t < T_GONE1 + 0.1:
        px = gold_x(t)
        L.append(f'<circle cx="{px:.0f}" cy="{BELT-40}" r="{120+8*math.sin(t*8):.0f}" fill="url(#aura)" opacity="0.8"/>')
        L.append(plate(px, BELT, s=1.0, gold=True) + nigiri(px, BELT - 12, 1.0))
        L.append(star_twinkle(px + 60, BELT - 90, (t * 1.3) % 1))

    # ---- riders on the belt
    if g["show"] and g["ride"]:
        L.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "up", g["look"], g["rot"], g["sx"], g["sy"], drink=False, t=t))
        if t >= T_JUMPG1 and t < T_RAM:
            L.append(speed_lines(g["x"] - 150, g["y"], 0, 0.85))
    if n["show"] and n["ride"]:
        if n["costume"] and t < T_RAM:
            L.append(plate(nib_ride_x(t), BELT, "#3a8fd8", 1.55))
        L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"] if n["kind"] is None else "blank", rot=n["rot"], sx=n["sx"], sy=n["sy"]))
        L.append(nib_face(n["x"], n["y"], NR, n["rot"], n["sx"], n["sy"], n["kind"], t))
        if n["costume"]:
            L.append(nibbo_costume(n["x"], n["y"], NR, n["rot"], n["sx"], n["sy"], t))
        if n["gold_on_head"]:
            hx, hy = bodypt(n["x"], n["y"], 1, n["rot"], n["sx"], n["sy"], 0, -NR - 26)
            L.append(plate(hx, hy + 8, s=0.8, gold=True))
            if n["sushi_head"]:
                L.append(nigiri(hx, hy - 2, 0.8))
                L.append(f'<circle cx="{hx:.0f}" cy="{hy-30:.0f}" r="{70+6*math.sin(t*8):.0f}" fill="url(#aura)" opacity="0.6"/>')

    # ---- LAP 3: the cat + the maki roll
    if t >= T_LAP3:
        cx = cat_x(t)
        if cx < R_ENT + 140:
            chew = abs(math.sin(t * 12)) if t < T_GULP else 0.0
            mood = "wink" if T_WINK <= t < T_WINK + 0.6 else "happy"
            L.append(plate(cx, BELT, "#e8402e", 1.3))
            L.append(cat(cx, BELT - 82, 1.0, mood, t, chew, holding=t < T_GULP, tilt=4 * math.sin(t * 3)))
            if t < T_GULP:
                L.append(f'<g opacity="0.8">' + "".join(f'<circle cx="{cx - 70 + 140*((t*1.3 + k*0.33) % 1):.0f}" cy="{BELT - 200 - 40*((t*1.3 + k*0.33) % 1):.0f}" r="5" fill="#ffffff" stroke="{OL}" stroke-width="2"/>' for k in range(3)) + '</g>')
        mx = maki_x(t)
        if mx < R_ENT + 200:
            msx, msy = 1.0, 1.0
            if T_STUCK <= t < T_POP0:
                q = seg(t, T_STUCK, T_POP0)
                msx = 1 - 0.18 * q - 0.04 * math.sin((t - T_STUCK) * 30)
                msy = 1 + 0.12 * q
            if t >= T_POP0:
                msx, msy = 0.7, 1.2
            if t < T_POP0:
                L.append(plate(mx, BELT, "#5fbf5a", 1.7))
            rr = 12 * math.sin(math.pi * seg(t, T_ROLL0, T_ROLL1 + 0.15))
            L.append(f'<g transform="rotate({rr:.1f} {mx:.1f} {BELT-4})">' + draw_maki(ctx, mx, BELT - 4, t, msx, msy) + '</g>')
            if t >= T_TOSS1 and t < T_POP0 + 0.05:
                L.append(plate(mx + 10, BELT - 4 - 250 * msy, s=0.85, gold=True))
    # ...and the roll comes around AGAIN
    if t >= T_LOOP:
        m2 = maki2_x(t)
        L.append(plate(m2, BELT, "#5fbf5a", 1.7))
        L.append(draw_maki(ctx, m2, BELT - 4, t, 1.0, 1.0))
    # cat tosses the empty golden plate back onto the roll
    if T_TOSS0 <= t < T_TOSS1:
        p = seg(t, T_TOSS0, T_TOSS1)
        x0, y0 = cat_x(T_TOSS0), BELT - 130
        x1, y1 = maki_x(T_TOSS1) + 10, BELT - 254
        L.append(plate(lerp(x0, x1, p), lerp(y0, y1, p) - 160 * math.sin(math.pi * p), s=0.85, gold=True))
    # tunnels (hide what's inside)
    shake_r = 0.0
    if T_IN <= t < T_IN + 0.8:
        shake_r = 10 * (1 - seg(t, T_IN, T_IN + 0.8))
    if T_STUCK <= t < T_POP0 + 0.3:
        shake_r = max(shake_r, 5)
    if t >= T_PEEK:
        q = eout(seg(t, T_PEEK, T_PEEK + 0.35))
        L.append(cat(1000, 1300 - 120 * q, 0.75, "wink" if t >= T_PEEK + 0.45 else "happy", t, 0.0, tilt=-10))
    L.append(tunnel(90, L_EXIT, 0.0, t))
    L.append(tunnel(R_ENT, 990, shake_r, t))
    L.append(counter_front())
    # the plate pops off and spins on the tunnel roof
    if t >= T_POP0 + 0.05:
        p = seg(t, T_POP0 + 0.05, T_PLATE_LAND)
        x0, y0 = MK_STUCK_X + 10, BELT - 4 - 250 * 1.2
        x1, y1 = 915, 1222
        if p < 1:
            L.append(f'<g transform="rotate({p*720:.0f} {lerp(x0, x1, p):.0f} {lerp(y0, y1, p) - 200*math.sin(math.pi*p):.0f})">'
                     + plate(lerp(x0, x1, p), lerp(y0, y1, p) - 200 * math.sin(math.pi * p), s=0.85, gold=True) + '</g>')
        else:
            q = t - T_PLATE_LAND
            wob = math.exp(-q * 2.2)
            ang = q * (10 + 30 * (1 - wob))
            L.append(f'<g transform="translate(915 1222) scale({1:.2f} 1)">'
                     f'<g transform="rotate({8*wob*math.sin(ang*3):.1f}) scale({0.75 + 0.25*abs(math.cos(ang*3))*wob + 0.25*(1-wob):.2f} 1)">'
                     + plate(0, 0, s=0.85, gold=True) + '</g></g>')


    # ---- arms + chopsticks (seated characters reach over the belt)
    if g["show"] and not g["ride"] and g["chop"]:
        tip, ang, gap = g["chop"]
        hx, hy = chop_hand(tip, ang)
        sd = 1 if hx > g["x"] else -1
        sx_, sy_ = bodypt(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], sd * 112, 40)
        L.append(arm(sx_, sy_, hx, hy, INK, 14, 20))
        L.append(chopsticks(hx, hy, ang, gap))
        L.append(hand(hx, hy, mix_hex(GFILL, "#ff6a52", g["red"]), OL, 19))
        if g["sushi"]:
            L.append(nigiri(tip[0], tip[1] + 14, 0.8, ang - 160))
    if n["show"] and not n["ride"] and n["chop"]:
        tip, ang, gap = n["chop"]
        hx, hy = chop_hand(tip, ang)
        sd = 1 if hx > n["x"] else -1
        sx_, sy_ = bodypt(n["x"], n["y"], 1, n["rot"], n["sx"], n["sy"], sd * 96, 30)
        L.append(arm(sx_, sy_, hx, hy, NS, 11, 16))
        L.append(chopsticks(hx, hy, ang, gap))
        L.append(hand(hx, hy, NB, NS, 15))
    if n["show"] and n["hL"]:
        sd = 1 if n["hL"][0] > n["x"] + 10 else -1
        sx_, sy_ = bodypt(n["x"], n["y"], 1, n["rot"], n["sx"], n["sy"], sd * 96, 26)
        L.append(arm(sx_, sy_, n["hL"][0], n["hL"][1], NS, 11, 16))
        L.append(hand(*n["hL"], NB, NS, 15))
        if n["sushi_hand"]:
            L.append(nigiri(n["hL"][0], n["hL"][1] - 18, 0.8, 10 * math.sin(t * 12)))
            L.append(star_twinkle(n["hL"][0] + 50, n["hL"][1] - 50, (t * 1.8) % 1))

    # ---- effects
    for c in CLACKS:
        if c <= t < c + 0.2:
            L.append(impact(gold_x(c), BELT - 70, seg(t, c, c + 0.2)))
    L.append(symbol(n["x"] + 10, n["y"] - 175, "!", seg(t, T_IDEA_N, T_IDEA_N + 0.5), "#ff9a20"))
    L.append(symbol(g["x"] + 10, g["y"] - 190, "!", seg(t, T_DOUBLE, T_DOUBLE + 0.5)))
    L.append(impact(g["x"] + 20, g["y"] + 70, seg(t, T_CHOMP, T_CHOMP + 0.22)))
    L.append(impact(R_ENT - 10, BELT - 110, seg(t, T_RAM, T_RAM + 0.3)))
    if T_IN + 0.1 <= t < T_IN + 0.8:
        q = seg(t, T_IN + 0.1, T_IN + 0.8)
        for k in range(4):
            a = -math.pi / 2 + (k - 1.5) * 0.5
            L.append(f'<circle cx="{935 + 160*q*math.cos(a):.0f}" cy="{1228 + 160*q*math.sin(a):.0f}" r="{26 + 18*q:.0f}" fill="#f4f4f4" stroke="#bbb" stroke-width="4" opacity="{1-q:.2f}"/>')
        # a plate flies out of the roof
        L.append(f'<g transform="rotate({q*600:.0f} {935 + 60*q:.0f} {1200 - 380*math.sin(math.pi*q):.0f})">' + plate(935 + 60 * q, 1200 - 380 * math.sin(math.pi * q), "#3a8fd8", 0.7) + '</g>')
    if T_GULP <= t < T_GULP + 0.5:
        L.append(symbol(cat_x(t) - 20, BELT - 260, "!", seg(t, T_GULP, T_GULP + 0.5), "#ff9a20"))
    L.append(impact(MK_STUCK_X + 170, BELT - 120, seg(t, T_STUCK, T_STUCK + 0.25)))
    L.append(impact(R_ENT, BELT - 120, seg(t, T_POP0, T_POP0 + 0.25)))
    if T_WINK <= t < T_WINK + 0.6:
        L.append(star_twinkle(cat_x(t) + 60, BELT - 230, seg(t, T_WINK, T_WINK + 0.6)))

    cx_, cy_, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx_:.1f} {-cy_:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{defs()}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g>'
           f'<rect width="{W}" height="{H}" fill="url(#vig)"/></svg>')
    lp = lap(t)
    bump = [0.0, T_LAP2, T_LAP3, T_LOOP + 0.15][lp - 1]
    return overlay(svg, hook_title(t + 0.12, "1 golden sushi,", "WHO GRABS IT?"),
                   counter(t, f"{lp}/3", "LAP", min(lp, 3), 3, bump_t=bump))


def draw_maki(ctx, x, y, t, sx=1.0, sy=1.0):
    """giant maki roll: Grumpo + Nibbo wrapped in one nori band. (x, y) bottom centre."""
    o = [f'<g transform="translate({x:.1f} {y:.1f}) scale({sx:.3f} {sy:.3f})">']
    o.append(f'<ellipse cx="0" cy="-125" rx="192" ry="128" fill="#ffffff" stroke="{OL}" stroke-width="6"/>')
    for k in range(16):
        a = k * 0.39 + 0.1
        ex_, ey_ = 172 * math.cos(a), -125 + 110 * math.sin(a)
        if ey_ > -40:
            continue
        o.append(f'<ellipse cx="{ex_:.0f}" cy="{ey_:.0f}" rx="9" ry="5" fill="#eef2f6" stroke="#c9d2de" stroke-width="2" transform="rotate({k*40} {ex_:.0f} {ey_:.0f})"/>')
    stuck = T_STUCK <= t < T_POP0 + 0.2
    gk = "strain" if stuck else ("dizzy" if t < T_LAP3 + 1.0 else "flat")
    biting = T_ROLL0 <= t < T_GULP + 0.1
    if t >= T_LOOP:
        gk = "dizzy"
    if biting:
        o.append(grumpo(ctx, -60, -140, 0.68, "shock", 0.0, "up", (1, 0.3), 10, 1, 1, drink=False, t=t))
    else:
        o.append(grumpo(ctx, -78, -130, 0.66, "x", 0.0, "up", (0.6, 0), -6, 1, 1, drink=False, t=t))
        o.append(grumpo_extra(-78, -130, 0.66, -6, 1, 1, gk, t))
    nk = "effort" if stuck else ("worried" if t >= T_LAP3 + 1.0 else None)
    if biting:
        nk = "lookright"
    if t >= T_LOOP:
        nk = None
    o.append(nibbo(ctx, 84, -128, 80, "dizzy" if nk is None else "blank", rot=6))
    o.append(nib_face(84, -128, 80, 6, 1, 1, nk, t))
    # nori band
    o.append(f'<path d="M-196 -86 Q 0 -60 196 -86 L190 -12 Q 0 14 -190 -12Z" fill="#24402a" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
             f'<path d="M-180 -66 Q 0 -42 180 -66" stroke="#3a6040" stroke-width="6" fill="none"/>'
             f'<path d="M-150 -40 Q 0 -18 150 -40" stroke="#3a6040" stroke-width="4" fill="none"/>')
    # rice grains stuck on them
    for (rx_, ry_) in [(-110, -200), (-40, -230), (60, -200), (130, -170), (-150, -140)]:
        o.append(f'<ellipse cx="{rx_}" cy="{ry_}" rx="8" ry="4.5" fill="#ffffff" stroke="#c9d2de" stroke-width="2" transform="rotate({rx_} {rx_} {ry_})"/>')
    o.append('</g>')
    return "".join(o)


def build_sfx():
    k = 0.0
    while k < DUR:
        sfx(k, "belt", 0.35, 1.0)
        k += 1.8
    sfx(0.0, "shine", 0.7, 1.0)
    sfx(0.05, "gasp", 0.4, 1.3)
    sfx(T_CHOP_G, "whoosh", 0.4, 1.6)
    sfx(T_CHOP_N, "whoosh", 0.4, 1.8)
    for c in CLACKS:
        sfx(c, "clack", 0.9, 1.0 + 0.08 * (CLACKS.index(c) % 2))
    sfx(T_CLASH1, "clack", 0.7, 0.8)
    sfx(T_CLASH1 + 0.05, "strain", 0.5, 1.2)
    sfx(T_LOCK1, "gasp", 0.5, 1.0)
    sfx(T_GONE1, "blip_down", 0.5, 0.9)
    sfx(T_GLARE, "grumble", 0.6, 1.0)
    sfx(T_GONE1 - 0.5, "purr", 0.25, 1.0)
    sfx(T_IDEA_N, "ding", 0.6, 1.3)
    sfx(T_HOP0, "boing", 0.6, 1.3)
    sfx(T_HOP1, "plop", 0.5, 1.3)
    sfx(T_HOP1 + 0.05, "zoom", 0.5, 1.4)
    sfx(T_SLIDE0, "squeak_slide", 0.4, 1.0)
    for c in (T_SLIDE1 + 0.1, T_SLIDE1 + 0.32, T_SLIDE1 + 0.54):
        sfx(c, "clack", 0.4, 1.3)
    sfx(T_LAP2, "pop", 0.5, 1.2)
    sfx(T_DOUBLE, "alert", 0.5, 1.0)
    sfx(T_DOUBLE + 0.02, "gasp", 0.5, 0.9)
    sfx(T_PLUCK1 - 0.05, "clack", 0.7, 1.1)
    sfx(T_PLUCK1 + 0.05, "rise", 0.4, 1.0)
    sfx(T_LEAP0, "boing", 0.7, 1.4)
    sfx(T_SNATCH, "zip", 0.7, 1.3)
    sfx(T_CHOMP, "clack", 1.0, 0.75)
    sfx(T_CHOMP + 0.02, "bonk", 0.5, 1.4)
    sfx(T_LEAP1, "plop", 0.5, 1.2)
    sfx(T_LEAP1 + 0.2, "laugh", 0.4, 1.3)
    sfx(T_CHOMP + 0.25, "grumble", 0.8, 0.85)
    sfx(T_JUMPG0, "boing", 0.7, 0.8)
    sfx(T_JUMPG1, "thud", 0.5, 1.0)
    sfx(T_JUMPG1 + 0.05, "zoom", 0.6, 0.9)
    sfx(T_RAM - 0.3, "gasp", 0.5, 1.4)
    sfx(T_RAM, "bonk", 0.9, 0.9)
    sfx(T_RAM + 0.02, "squish", 0.6, 1.0)
    sfx(T_IN + 0.05, "metal_crash", 0.8, 1.2)
    sfx(T_IN + 0.2, "clatter", 0.7, 1.0)
    sfx(T_IN + 0.45, "bonk", 0.5, 1.1)
    sfx(T_IN + 0.6, "clatter", 0.5, 1.3)
    sfx(T_LAP3, "pop", 0.5, 1.0)
    sfx(T_LAP3 + 0.1, "purr", 0.6, 1.0)
    for k in range(5):
        sfx(T_LAP3 + 0.2 + k * 0.26, "munch", 0.45, 1.3)
    sfx(T_LAP3 + 1.0, "blip_down", 0.4, 0.8)
    sfx(T_ROLL0 - 0.05, "whoosh", 0.6, 0.9)
    sfx(T_ROLL0, "rumble", 0.5, 1.3)
    sfx(T_ROLL1, "thud", 0.6, 1.0)
    sfx(T_ROLL0 + 0.05, "wobble", 0.5, 1.0)
    sfx(T_ROLL1 - 0.1, "gasp", 0.5, 0.9)
    sfx(T_GULP, "gulp", 0.8, 1.2)
    sfx(T_TOSS0, "whoosh", 0.5, 1.5)
    sfx(T_TOSS1, "ding", 0.5, 1.5)
    sfx(T_WINK, "cool", 0.5, 1.2)
    sfx(T_STUCK, "thunk", 0.7, 1.0)
    sfx(T_STUCK + 0.1, "strain", 0.6, 1.0)
    sfx(T_STUCK + 0.35, "stretch", 0.6, 0.9)
    sfx(T_POP0, "cork_pop", 0.9, 1.0)
    sfx(T_POP0 + 0.05, "whoosh", 0.5, 1.2)
    sfx(T_POP0 + 0.25, "clatter", 0.4, 1.2)
    sfx(T_PLATE_LAND, "plate_spin", 0.8, 1.0)
    sfx(T_PEEK, "pop", 0.4, 1.4)
    sfx(T_PEEK + 0.1, "purr", 0.5, 1.0)
    sfx(T_PEEK + 0.45, "cool", 0.5, 1.3)
    sfx(T_LOOP - 0.15, "whoosh", 0.6, 1.0)
    sfx(T_LOOP, "pop", 0.6, 0.9)
    sfx(T_LOOP + 0.15, "ding", 0.5, 1.0)
    sfx(T_LOOP + 0.5, "thud", 0.4, 1.0)
    sfx(T_LOOP + 0.6, "blip_down", 0.5, 0.7)
