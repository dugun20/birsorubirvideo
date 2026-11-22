"""Grumpo & Nibbo — Episode 8: The Copycat (empty cinema, imitation structure, 60 fps).

A completely EMPTY cinema — and Grumpo drops into the one seat right in front of Nibbo.
Nibbo leans left: Grumpo leans left. Right: right. Left-right-left at full speed: copied.
Nibbo stretches tall: Grumpo stretches taller. Nibbo hops up onto his backrest: Grumpo hops
onto his — and his empty seat cushion quietly snaps UP behind him (Nibbo notices).
Nibbo crouches for a big jump, Grumpo crouches too... Nibbo only fakes it; Grumpo launches
for real, drops his popcorn, falls into the folded seat, squeezes straight through it and ends
up flattened under the seat. The popcorn bucket lands in Nibbo's hands, popcorn rains back in,
Nibbo sits down with a perfect view and munches. Nibbo wins.
"""
import math, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow
from hook import overlay, hook_title

W, H, FPS, DUR = 1080, 1920, 60, 15.0
GS = 0.92
GR = 130 * GS            # grumpo radius (~120)
NR = 112
CX = 540                 # the column both of them sit in
SEAT_DX = 260
FLOOR = 1530             # row-1 floor
R1_TOP, R1_SIT = 1262, 1418   # row 1 (Grumpo)
R2_TOP, R2_SIT = 1160, 1340   # row 2 (Nibbo)
R3_TOP, R3_SIT = 1064, 1244   # row 3 (empty)
G_SIT_B = R1_SIT + 2          # Grumpo bottom when seated
G_PERCH_B = R1_TOP + 2        # on top of his backrest
N_SIT_B = R2_SIT + 2
N_PERCH_B = R2_TOP + 2
G_UNDER_B = FLOOR

# --- key times
T_LAND = 0.32
T_FOLD = 7.22            # Grumpo's empty cushion snaps up
T_IDEA = 7.78
T_FAKE = 9.15
T_LAUNCH = 9.22
T_APEX = 9.68
T_DROP = 10.02
T_WEDGE = 10.30
T_SLIP0, T_SLIP1 = 10.62, 10.86
T_RELEASE = 9.78
T_CATCH = 10.48
T_SITDN0, T_SITDN1 = 99.0, 99.5
T_SLAM = 10.98            # cushion slams back down on flattened Grumpo
T_FLASH = 13.35
T_TOSS0, T_TOSS1 = 13.85, 14.35

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
    """piecewise smooth keyframes [(t, v), ...]."""
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


# ---------------------------------------------------------------- props
def puff(x, y, s=1.0, rot=0.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.0f}) scale({s:.2f})">'
            f'<circle cx="-7" cy="2" r="9" fill="#fff6dc" stroke="{OL}" stroke-width="3"/>'
            f'<circle cx="7" cy="1" r="9" fill="#fff6dc" stroke="{OL}" stroke-width="3"/>'
            f'<circle cx="0" cy="-7" r="9" fill="#fffaf0" stroke="{OL}" stroke-width="3"/>'
            '<circle cx="-2" cy="2" r="7" fill="#fffaf0"/><circle cx="3" cy="6" r="3" fill="#ffd25a"/></g>')


PUFFS_TOP = [(-44, -8, 1.0, 10), (-18, -22, 1.1, -20), (10, -18, 1.05, 40), (38, -6, 1.0, -5), (-30, 8, 0.9, 70),
             (0, 2, 1.0, 0), (26, 10, 0.95, 30), (-8, -36, 1.0, 15), (20, -36, 0.9, -30)]


def bucket(ctx, x, y, s=1.0, rot=0.0, full=1.0):
    """popcorn bucket; (x,y) = centre of the bucket body; rim at y-70."""
    cid = ctx.uid("bk")
    body = "M-62 -68 L62 -68 L46 70 Q 0 80 -46 70Z"
    ctx.defs.append(f'<clipPath id="{cid}"><path d="{body}"/></clipPath>')
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">']
    n = int(round(len(PUFFS_TOP) * cl(full)))
    for (px, py, ps, pr) in PUFFS_TOP[:n]:
        o.append(puff(px, py - 72, ps * 1.3, pr))
    o.append(f'<g clip-path="url(#{cid})"><rect x="-70" y="-80" width="140" height="170" fill="#ffffff"/>')
    for k in range(-3, 4):
        o.append(f'<path d="M{k*36-9} -80 L{k*30-8} 90 L{k*30+12} 90 L{k*36+11} -80Z" fill="#e8303a"/>')
    o.append('<rect x="-70" y="40" width="140" height="50" fill="#000" opacity="0.12"/></g>')
    o.append(f'<path d="{body}" fill="none" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>')
    o.append(f'<rect x="-68" y="-80" width="136" height="20" rx="8" fill="#ffd23a" stroke="{OL}" stroke-width="5"/>')
    o.append('<circle cx="0" cy="6" r="24" fill="#ffd23a" stroke="#221c2e" stroke-width="4"/>'
             '<path d="M-10 6 l7 -14 l3 10 l7 -9 l3 13" fill="none" stroke="#e8303a" stroke-width="4" stroke-linejoin="round"/>')
    o.append('</g>')
    return "".join(o)


def soda(x, y):
    return (f'<g transform="translate({x} {y})"><path d="M-17 -40 h34 l-5 46 h-24z" fill="#3a8be0" stroke="{OL}" stroke-width="4"/>'
            f'<rect x="-20" y="-46" width="40" height="9" rx="4" fill="#f4f1fa" stroke="{OL}" stroke-width="3"/>'
            f'<path d="M4 -46 l8 -26" stroke="#ff5a6e" stroke-width="5" stroke-linecap="round"/>'
            '<path d="M-10 -30 v26" stroke="#ffffff" stroke-width="4" opacity="0.5"/></g>')


# ---------------------------------------------------------------- cinema
SEAT_RED, SEAT_DK, SEAT_LT = "#d0303f", "#9c1f30", "#ef5a62"


def seat_back(x, top, sit, dark=0.0):
    red = mix_hex(SEAT_RED, "#2a1428", dark)
    dk = mix_hex(SEAT_DK, "#1e0e1e", dark)
    lt = mix_hex(SEAT_LT, "#3a1c34", dark)
    h = sit - top + 14
    return (f'<rect x="{x-112}" y="{top}" width="224" height="{h}" rx="46" fill="{red}" stroke="{OL}" stroke-width="6"/>'
            f'<rect x="{x-84}" y="{top+26}" width="168" height="{h-52}" rx="30" fill="{dk}"/>'
            f'<path d="M{x-80} {top+44} v{h-96}" stroke="{red}" stroke-width="8" stroke-linecap="round" opacity="0.6"/>'
            f'<path d="M{x-90} {top+12} q 30 -6 70 -4" stroke="{lt}" stroke-width="8" fill="none" stroke-linecap="round"/>')


def seat_cushion(x, sit, fold=0.0, dark=0.0, wob=0.0):
    """front view: fold=0 -> horizontal slab, fold=1 -> flipped up (underside shown)."""
    red = mix_hex(mix_hex(SEAT_LT, "#3a1c34", dark), "#7a1626", fold)
    edge = mix_hex(SEAT_RED, "#5a0f1e", fold)
    hgt = lerp(46, 142, fold)
    top = lerp(sit - 10, sit - 126, fold) + wob
    o = [f'<rect x="{x-108}" y="{top:.1f}" width="216" height="{hgt:.1f}" rx="20" fill="{red}" stroke="{OL}" stroke-width="6"/>']
    if fold < 0.3:
        o.append(f'<path d="M{x-92} {top+12:.1f} H{x+92}" stroke="#ff8a8e" stroke-width="7" stroke-linecap="round" opacity="{0.8*(1-fold/0.3):.2f}"/>')
    else:
        a = (fold - 0.3) / 0.7
        o.append(f'<g opacity="{a:.2f}"><rect x="{x-80}" y="{top+hgt-34:.1f}" width="160" height="16" rx="6" fill="#8a93a2" stroke="{OL}" stroke-width="4"/>'
                 f'<circle cx="{x-64}" cy="{top+hgt-26:.1f}" r="4" fill="{OL}"/><circle cx="{x+64}" cy="{top+hgt-26:.1f}" r="4" fill="{OL}"/>'
                 f'<path d="M{x-80} {top+22:.1f} H{x+80}" stroke="{edge}" stroke-width="6" stroke-linecap="round"/></g>')
    return "".join(o)


def armrest(x, sit, floor, dark=0.0, cup=False):
    post = mix_hex("#4a3450", "#1c1020", dark)
    pad = mix_hex("#5e4466", "#24142a", dark)
    o = [f'<rect x="{x-17}" y="{sit-40}" width="34" height="{floor-sit+40}" rx="8" fill="{post}" stroke="{OL}" stroke-width="5"/>',
         f'<rect x="{x-24}" y="{sit-62}" width="48" height="30" rx="12" fill="{pad}" stroke="{OL}" stroke-width="5"/>']
    if cup:
        o.append(f'<ellipse cx="{x}" cy="{sit-60}" rx="20" ry="7" fill="#1a1020" stroke="{OL}" stroke-width="3"/>')
    return "".join(o)


def row(xs, top, sit, floor, dark, folds=None, skip_cushion=(), cups=()):
    o = []
    for x in xs:
        o.append(seat_back(x, top, sit, dark))
    # under-seat darkness
    for x in xs:
        o.append(f'<rect x="{x-104}" y="{sit+20}" width="208" height="{floor-sit-20}" fill="#120a16"/>')
    for x in xs:
        if x in skip_cushion:
            continue
        f, w = (folds or {}).get(x, (0.0, 0.0))
        o.append(seat_cushion(x, sit, f, dark, w))
    for k, x in enumerate(xs + [xs[-1] + SEAT_DX]):
        ax = x - SEAT_DX / 2
        o.append(armrest(ax, sit, floor, dark, ax in cups))
    return "".join(o)


XS = [CX + SEAT_DX * k for k in range(-3, 4)]


def back_wall(t):
    o = [f'<rect x="-900" y="-400" width="2900" height="2600" fill="#24122c"/>']
    for x in range(-900, 2000, 120):
        o.append(f'<path d="M{x} -400 V1300" stroke="#2e1838" stroke-width="58"/><path d="M{x+30} -400 V1300" stroke="#1c0e24" stroke-width="6"/>')
    # wall sconces (dim)
    for x in (120, 960):
        o.append(f'<path d="M{x-40} 980 L{x+40} 980 L{x+24} 1020 L{x-24} 1020Z" fill="#ffb84a" stroke="{OL}" stroke-width="4"/>'
                 f'<ellipse cx="{x}" cy="940" rx="90" ry="70" fill="#ffb84a" opacity="0.10"/>')
    # projection booth window + lens
    o.append(f'<rect x="{CX-120}" y="812" width="240" height="120" rx="16" fill="#140a1a" stroke="{OL}" stroke-width="7"/>'
             f'<rect x="{CX-104}" y="828" width="208" height="88" rx="10" fill="#2e2040"/>'
             f'<circle cx="{CX+30}" cy="872" r="30" fill="#fffbe0" opacity="0.95"/><circle cx="{CX+30}" cy="872" r="62" fill="#fff6c8" opacity="0.25"/>'
             f'<rect x="{CX-90}" y="846" width="70" height="50" rx="8" fill="#4a3a5a" stroke="{OL}" stroke-width="4"/>')
    return "".join(o)


def beam(t):
    """projector cone toward the screen (toward the camera) + floating dust."""
    ox, oy = CX + 30, 872
    o = [f'<path d="M{ox} {oy} L-700 1900 L1800 1900Z" fill="url(#beamG)"/>']
    for k in range(9):
        a = math.radians(-12 + 6 * k + 2 * math.sin(t * 0.7 + k))
        L = 1300
        x2, y2 = ox + L * math.sin(a), oy + L * math.cos(a)
        o.append(f'<path d="M{ox} {oy} L{x2:.0f} {y2:.0f}" stroke="#fff6d0" stroke-width="{18 + 10*(k%3)}" opacity="{0.035 + 0.02*math.sin(t*3+k):.3f}"/>')
    rnd = random.Random(8)
    for k in range(26):
        x = rnd.uniform(200, 880)
        y = rnd.uniform(900, 1250)
        x += 20 * math.sin(t * 0.6 + k)
        y += ((t * 14 + k * 37) % 120) - 60
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(2, 4):.1f}" fill="#fff6d0" opacity="{0.25 + 0.2*math.sin(t*2+k):.2f}"/>')
    return "".join(o)


def floor_layer():
    o = [f'<rect x="-900" y="{FLOOR}" width="2900" height="700" fill="#3a1f44"/>']
    for k in range(-10, 22):
        x = k * 90
        o.append(f'<path d="M{x} {FLOOR+30} l20 18 l-20 18 l-20 -18z" fill="#4a2a56"/>')
    o.append(f'<path d="M-900 {FLOOR} H2000" stroke="{OL}" stroke-width="6"/>')
    # step lights along the floor edge
    for k in range(-10, 22):
        o.append(f'<circle cx="{k*60+20}" cy="{FLOOR+12}" r="5" fill="#ffd25a" opacity="0.85"/>')
    return "".join(o)


def riser(top, floor):
    return (f'<rect x="-900" y="{top}" width="2900" height="{floor-top}" fill="#2a1532"/>'
            f'<path d="M-900 {top} H2000" stroke="{OL}" stroke-width="5"/>'
            + "".join(f'<circle cx="{k*60+50}" cy="{top+14}" r="4" fill="#ffd25a" opacity="0.7"/>' for k in range(-10, 22)))


# ---------------------------------------------------------------- states
# Nibbo lateral lean & Grumpo copy (Grumpo copies ~0.1-0.3 s later)
NX_KEYS = [(0, 0), (1.10, 0), (1.35, -175), (2.20, -175), (2.42, 175), (3.05, 175), (3.15, -175), (3.35, -175), (3.45, 175),
           (3.65, 175), (3.75, -175), (3.95, -175), (4.05, 175), (4.30, 175), (4.50, 0),
           (7.50, 0), (7.68, -165), (8.10, -165), (8.28, 0)]
GX_KEYS = [(0, 0), (1.62, 0), (1.84, -160), (2.55, -160), (2.76, 160), (3.12, 160), (3.22, -160), (3.42, -160), (3.52, 160),
           (3.72, 160), (3.81, -160), (4.0, -160), (4.09, 160), (4.36, 160), (4.58, 0),
           (7.98, 0), (8.14, -150), (8.30, -150), (8.45, 0)]


def nibbo_state(t):
    n = dict(x=CX + kf(t, NX_KEYS), b=N_SIT_B, ex="joy", rot=0.0, sx=1.0, sy=1.0, hold=False, look=0)
    dx = n["x"] - CX
    n["rot"] = dx * 0.075
    lift = abs(dx) / 175 * 14
    n["b"] -= lift
    # stretch
    st = kf(t, [(4.68, 1.0), (4.95, 1.62), (5.72, 1.62), (5.86, 0.86), (5.98, 1.06), (6.08, 1.0)])
    n["sy"] *= st
    n["sx"] *= 1 - (st - 1) * 0.25
    # perch hop
    if 6.25 <= t < 6.6:
        p = seg(t, 6.25, 6.6)
        n["b"] = lerp(N_SIT_B, N_PERCH_B, eio(p)) - 120 * 4 * p * (1 - p)
    elif 6.6 <= t < T_SITDN0:
        n["b"] = N_PERCH_B - lift
    if 6.6 <= t < 6.9:
        a, b = squash(t, 6.6, 0.3, 0.2)
        n["sx"] *= a
        n["sy"] *= b
    # crouch + fake hop
    cr = kf(t, [(8.5, 1.0), (8.82, 0.72), (T_FAKE, 0.72), (T_FAKE + 0.1, 1.1), (T_FAKE + 0.26, 0.96), (T_FAKE + 0.4, 1.0)])
    n["sy"] *= cr
    n["sx"] *= 1 + (1 - cr) * 0.35
    if T_FAKE <= t < T_FAKE + 0.3:
        n["b"] -= 30 * math.sin(math.pi * seg(t, T_FAKE, T_FAKE + 0.3))
    # catch
    if t >= T_CATCH:
        n["hold"] = True
        a, b = squash(t, T_CATCH, 0.3, 0.18)
        n["sx"] *= a
        n["sy"] *= b
    if T_SITDN0 <= t < T_SITDN1:
        p = seg(t, T_SITDN0, T_SITDN1)
        n["b"] = lerp(N_PERCH_B, N_SIT_B, ein(p)) - 70 * math.sin(math.pi * p)
    elif t >= T_SITDN1:
        n["b"] = N_SIT_B
        a, b = squash(t, T_SITDN1, 0.3, 0.2)
        n["sx"] *= a
        n["sy"] *= b
    # munching chew
    for tm in (11.9, 12.45, 13.0):
        if tm <= t < tm + 0.45:
            k = t - tm
            n["sx"] *= 1 + 0.05 * math.sin(k * 40)
            n["sy"] *= 1 - 0.04 * math.sin(k * 40)
    n["ex"] = pick(t, [(0, "joy"), (0.3, "wow"), (0.6, "uhoh"), (1.2, "happy"), (1.75, "uhoh"), (2.3, "happy"), (2.7, "uhoh"),
                       (3.1, "nervous"), (4.6, "uhoh"), (4.9, "happy"), (5.4, "uhoh"), (5.9, "uhoh"), (6.55, "joy"), (7.1, "uhoh"),
                       (7.62, "wow"), (T_IDEA, "happy"), (8.4, "happy"), (T_LAUNCH, "happy"), (T_RELEASE + 0.1, "wow"),
                       (T_CATCH, "joy"), (11.6, "happy"), (11.9, "joy"), (T_FLASH, "wow"), (T_FLASH + 0.4, "joy")], "joy")
    n["y"] = n["b"] - NR * n["sy"]
    return n


def grumpo_state(t):
    g = dict(x=CX + kf(t, GX_KEYS), b=G_SIT_B, ex="smug", red=0.0, look=(0, -0.6), sx=1.0, sy=1.0, rot=0.0,
             hold=True, behind=False, under=False)
    dx = g["x"] - CX
    g["rot"] = dx * 0.06
    g["b"] -= abs(dx) / 160 * 10
    g["look"] = ((-1 if dx < -5 else (1 if dx > 5 else 0)) * 0.9, -0.7)
    # entrance: drops in from above
    if t < T_LAND:
        p = seg(t, -0.15, T_LAND)
        g["b"] = lerp(G_SIT_B - 330, G_SIT_B, ein(p))
        g["sy"] = 1.08
        g["sx"] = 0.95
    a, b = squash(t, T_LAND, 0.32, 0.26)
    g["sx"] *= a
    g["sy"] *= b
    # stretch (copy)
    st = kf(t, [(5.18, 1.0), (5.42, 1.78), (5.72, 1.78), (5.86, 0.84), (5.98, 1.06), (6.1, 1.0)])
    g["sy"] *= st
    g["sx"] *= 1 - (st - 1) * 0.22
    # perch hop (copy)
    if 6.98 <= t < 7.34:
        p = seg(t, 6.98, 7.34)
        g["b"] = lerp(G_SIT_B, G_PERCH_B, eio(p)) - 120 * 4 * p * (1 - p)
    elif 7.34 <= t < T_LAUNCH:
        g["b"] = G_PERCH_B - abs(dx) / 160 * 10
    if 7.34 <= t < 7.64:
        a, b = squash(t, 7.34, 0.3, 0.22)
        g["sx"] *= a
        g["sy"] *= b
    # crouch copy
    cr = kf(t, [(8.62, 1.0), (8.95, 0.68), (T_LAUNCH, 0.68)])
    if t < T_LAUNCH:
        g["sy"] *= cr
        g["sx"] *= 1 + (1 - cr) * 0.4
    # launch / hang / drop
    if T_LAUNCH <= t < T_APEX:
        p = seg(t, T_LAUNCH, T_APEX)
        g["b"] = lerp(G_PERCH_B, G_PERCH_B - 330, eout(p))
        g["sy"] *= 1 + 0.25 * (1 - p)
        g["sx"] *= 1 - 0.15 * (1 - p)
    elif T_APEX <= t < T_DROP:
        g["b"] = G_PERCH_B - 330 - 8 * math.sin(math.pi * seg(t, T_APEX, T_DROP))
    elif T_DROP <= t < T_WEDGE:
        p = seg(t, T_DROP, T_WEDGE)
        g["b"] = lerp(G_PERCH_B - 330, R1_SIT + 70, ein(p))
        g["sy"] *= 1 + 0.15 * p
        g["sx"] *= 1 - 0.1 * p
    elif T_WEDGE <= t < T_SLIP0:
        # stuck in the folded seat: squeezed, wiggling
        k = t - T_WEDGE
        g["b"] = R1_SIT + 70
        g["sx"] *= 0.78 + 0.05 * math.sin(k * 38)
        g["sy"] *= 1.16 - 0.05 * math.sin(k * 38)
        g["behind"] = True
    elif T_SLIP0 <= t < T_SLIP1:
        p = seg(t, T_SLIP0, T_SLIP1)
        g["behind"] = True
        g["b"] = lerp(R1_SIT + 70, G_UNDER_B, ein(p))
        g["sx"] *= lerp(0.78, 1.5, p)
        g["sy"] *= lerp(1.16, 0.44, p)
    elif t >= T_SLIP1:
        g["under"] = True
        k = t - T_SLIP1
        g["b"] = G_UNDER_B
        g["sx"] = 1.5 + 0.12 * math.exp(-k * 6) * math.sin(k * 40)
        g["sy"] = 0.44 - 0.06 * math.exp(-k * 6) * math.sin(k * 40)
        g["rot"] = 0
        g["look"] = (pick(t, [(0, 0), (11.7, -0.8), (12.9, 0.6), (13.6, -0.8)], 0), -0.4)
        g["red"] = 0.3 * seg(t, 11.6, 12.4)
    if t >= T_DROP:
        g["rot"] = 0
    if t >= T_RELEASE:
        g["hold"] = False
    g["ex"] = pick(t, [(0, "grumpy"), (T_LAND + 0.25, "smug"), (5.86, "grumpy"), (6.1, "smug"), (T_APEX - 0.05, "shock"),
                       (T_WEDGE, "shock"), (T_SLIP1 + 0.2, "grumpy"), (12.0, "angry"), (12.6, "grumpy")], "smug")
    if T_APEX <= t < T_WEDGE:
        g["look"] = (0, 1)
    g["y"] = g["b"] - GR * g["sy"]
    return g


def g_fold(t):
    """Grumpo's seat cushion fold amount + wobble."""
    if t < T_FOLD:
        return 0.0, 0.0
    p = seg(t, T_FOLD, T_FOLD + 0.12)
    f = eout(p)
    k = t - T_FOLD
    w = -10 * math.exp(-k * 7) * math.sin(k * 45) if k > 0.12 else 0.0
    if t >= T_SLAM:
        q = t - T_SLAM
        f = 1 - eout(seg(t, T_SLAM, T_SLAM + 0.1))
        w = 5 * math.exp(-q * 8) * math.sin(q * 50) if q > 0.1 else 0.0
        return f, w
    if T_WEDGE <= t < T_SLIP1 + 0.4:
        q = t - T_WEDGE
        w += 6 * math.sin(q * 50) * math.exp(-q * 3)
    return f, w


def bucket_pos(t, g, n):
    """returns (x, y, rot, full) of the bucket."""
    if t < T_RELEASE:
        return g["x"] + 168 + g["rot"] * 2, g["y"] + 26 + (GR * (g["sy"] - 1) * 0.3), g["rot"] * 0.6 + 6, 1.0
    if t < T_CATCH:
        p = seg(t, T_RELEASE, T_CATCH)
        x0, y0 = CX + 168, G_PERCH_B - 330 - GR + 26
        x1, y1 = CX + 150, N_PERCH_B - 50
        x = lerp(x0, x1, p)
        y = lerp(y0, y1, p) - 260 * 4 * p * (1 - p)
        return x, y, 354 * eio(p) + 6, lerp(1.0, 0.35, seg(t, T_RELEASE, T_RELEASE + 0.2))
    full = lerp(0.35, 1.0, seg(t, T_CATCH, T_CATCH + 0.55))
    bob = 0
    for tm in (11.9, 12.45, 13.0):
        if tm - 0.25 <= t < tm + 0.2:
            bob = -10 * math.sin(math.pi * seg(t, tm - 0.25, tm + 0.2))
    return n["x"] + 150, n["b"] - 50 + bob, 0.0, full


# spilled popcorn (flies out of the bucket when Grumpo lets go)
_rs = random.Random(42)
SPILL = [(_rs.uniform(-420, 420), _rs.uniform(-900, -300), _rs.uniform(-600, 600), _rs.uniform(0.8, 1.2)) for _ in range(16)]
RAIN = [(_rs.uniform(-60, 60), _rs.uniform(0.0, 0.35), _rs.uniform(0.25, 0.4)) for _ in range(9)]


def spill(t):
    o = []
    if t < T_RELEASE:
        return ""
    x0, y0 = CX + 168, G_PERCH_B - 330 - GR - 40
    for vx, vy, vr, s in SPILL:
        k = t - T_RELEASE
        x = x0 + vx * k
        y = y0 + vy * k + 0.5 * 2600 * k * k
        if y > FLOOR + 30:
            # resting on the floor
            kk = (-vy + math.sqrt(max(0, vy * vy + 2 * 2600 * (FLOOR + 30 - y0)))) / 2600
            x = x0 + vx * kk
            y = FLOOR + 30
            o.append(puff(x, y, s * 1.2, vr * kk))
        else:
            o.append(puff(x, y, s * 1.3, vr * k))
    return "".join(o)


def rain(t, n):
    """popcorn falling back into the caught bucket."""
    o = []
    for dx, d0, dd in RAIN:
        ts = T_CATCH - 0.15 + d0
        if ts <= t < ts + dd:
            p = seg(t, ts, ts + dd)
            x = n["x"] + 150 + dx * (1 - p)
            y = lerp(N_PERCH_B - 520, N_PERCH_B - 120, p * p)
            o.append(puff(x, y, 1.3, 300 * p))
    return "".join(o)


# ---------------------------------------------------------------- camera
CK = [(0.0, (540, 1130, 1.5)), (0.5, (540, 1180, 1.8)), (2.9, (540, 1180, 1.8)), (3.05, (540, 1180, 1.86)),
      (4.4, (540, 1180, 1.86)), (4.65, (540, 1150, 1.7)), (6.1, (540, 1150, 1.7)), (6.45, (540, 1110, 1.7)),
      (7.45, (540, 1110, 1.7)), (7.6, (490, 1130, 1.85)), (8.4, (490, 1130, 1.85)), (8.6, (540, 1110, 1.72)),
      (T_LAUNCH, (540, 1100, 1.68)), (T_APEX, (540, 1020, 1.45)), (T_DROP, (540, 1030, 1.45)),
      (T_WEDGE + 0.05, (540, 1200, 1.55)), (10.9, (540, 1200, 1.55)), (11.5, (540, 1140, 1.6)), (13.2, (540, 1145, 1.64)),
      (DUR, (540, 1150, 1.7))]
SHAKES = [(T_SLAM, 8, 0.25), (T_LAND, 9, 0.25), (T_FOLD, 4, 0.2), (T_WEDGE, 10, 0.25), (T_SLIP1, 12, 0.3), (T_FLASH, 5, 0.4)]


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


def movie_light(t):
    """flickering light from the screen; returns (colour, opacity)."""
    f = 0.5 + 0.25 * math.sin(t * 5.1) + 0.15 * math.sin(t * 13.7 + 1) + 0.1 * math.sin(t * 2.3)
    col = mix_hex("#5a8aff", "#ffb070", 0.5 + 0.5 * math.sin(t * 1.3))
    op = 0.06 + 0.05 * f
    if T_FLASH <= t < T_FLASH + 0.6:
        q = seg(t, T_FLASH, T_FLASH + 0.6)
        col = mix_hex("#ff8a2a", col, q)
        op = lerp(0.32, op, q)
    return col, op


EXTRA_DEFS = ('<radialGradient id="beamG" cx="0.5" cy="0" r="1" fx="0.5" fy="0">'
              '<stop offset="0" stop-color="#fff6d0" stop-opacity="0.22"/><stop offset="0.6" stop-color="#fff6d0" stop-opacity="0.05"/>'
              '<stop offset="1" stop-color="#fff6d0" stop-opacity="0"/></radialGradient>'
              '<radialGradient id="vign" cx="0.5" cy="0.55" r="0.75"><stop offset="0.55" stop-color="#0a0410" stop-opacity="0"/>'
              '<stop offset="1" stop-color="#0a0410" stop-opacity="0.55"/></radialGradient>')


# ---------------------------------------------------------------- frame
def frame(t):
    ctx = Ctx()
    g = grumpo_state(t)
    n = nibbo_state(t)
    NB, NS = "#ffd23c", "#3d2a12"
    gfill = mix_hex("#9466e0", "#ff6a52", g["red"])
    gink = mix_hex("#1a0a2e", "#3a0505", g["red"])
    L = [back_wall(t)]
    # row 3 (empty, far)
    L.append(row(XS, R3_TOP, R3_SIT, R3_SIT + 120, 0.45, cups=(CX - 390, CX + 130)))
    L.append(riser(R3_SIT + 40, R2_SIT + 140))
    L.append(beam(t))

    # row 2 (Nibbo's row): backs, then nibbo, then cushions/armrests in front of him
    r2 = []
    for x in XS:
        r2.append(seat_back(x, R2_TOP, R2_SIT, 0.18))
    L.append("".join(r2))
    L.append(soda(CX + 390, R2_SIT - 66))

    def draw_nibbo():
        o = [nibbo(ctx, n["x"], n["y"], NR, n["ex"], rot=n["rot"], sx=n["sx"], sy=n["sy"])]
        if n["hold"]:
            bx, by, br, bf = bucket_pos(t, g, n)
            o.append(bucket(ctx, bx, by, 0.95, br, bf))
            o.append(arm(n["x"] + 96, n["y"] + 30, bx - 50, by + 4, NS, 10, 12) + hand(bx - 50, by + 4, NB, NS, 13))
            # munch: one hand brings a puff to the mouth
            for tm in (11.75, 12.3, 12.85):
                if tm <= t < tm + 0.35:
                    p = math.sin(math.pi * seg(t, tm, tm + 0.35))
                    hx, hy = lerp(bx - 10, n["x"] + 30, p), lerp(by - 80, n["y"] + 34, p)
                    o.append(arm(n["x"] + 80, n["y"] + 50, hx + 14, hy, NS, 10, 10) + puff(hx, hy - 16, 1.2) + hand(hx + 14, hy, NB, NS, 13))
            if T_TOSS0 <= t < T_TOSS1:
                p = seg(t, T_TOSS0, T_TOSS1)
                o.append(puff(n["x"] + 90 - 80 * p, n["y"] - 60 - 300 * 4 * p * (1 - p) + 70 * p, 1.3, 400 * p))
        return "".join(o)

    nib_perched = n["b"] < R2_TOP + 40
    if not nib_perched:
        L.append(shadow(n["x"], R2_SIT - 4, 100, 0.6))
        L.append(draw_nibbo())
    # row-2 cushions + armrests (in front of seated Nibbo; partly hidden by row 1 anyway)
    r2f = []
    for x in XS:
        r2f.append(seat_cushion(x, R2_SIT, 0.0, 0.18))
    for x in XS + [XS[-1] + SEAT_DX]:
        r2f.append(armrest(x - SEAT_DX / 2, R2_SIT, R2_SIT + 120, 0.18, (x - SEAT_DX / 2) == CX + 390 + SEAT_DX / 2))
    L.append("".join(r2f))
    if nib_perched:
        L.append(shadow(n["x"], R2_TOP + 6, 90, 0.5))
        L.append(draw_nibbo())
    L.append(riser(R2_SIT + 60, FLOOR))

    # row 1 (Grumpo's row)
    L.append("".join(seat_back(x, R1_TOP, R1_SIT, 0.0) for x in XS))
    L.append(floor_layer())
    for x in XS:
        L.append(f'<rect x="{x-104}" y="{R1_SIT+20}" width="208" height="{FLOOR-R1_SIT-20}" fill="#120a16"/>')

    fold, wob = g_fold(t)

    def draw_grumpo():
        o = []
        o.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"],
                        False, 0, None, 0, t))
        if g["hold"]:
            bx, by, br, bf = bucket_pos(t, g, n)
            o.append(bucket(ctx, bx, by, 1.0, br, bf))
            o.append(arm(g["x"] + 104, g["y"] + 40, bx - 50, by + 6, gink, 13, 10) + hand(bx - 50, by + 6, gfill, OL, 16))
        return "".join(o)

    perched = g["b"] < R1_SIT - 60 and not g["behind"]
    if g["under"]:
        L.append(draw_grumpo())
    for x in XS:
        if x == CX:
            if not perched and not g["behind"] and not g["under"]:
                L.append(shadow(g["x"], R1_SIT - 6, 120, 0.6))
                L.append(draw_grumpo())
            if g["behind"]:
                L.append(draw_grumpo())
            L.append(seat_cushion(x, R1_SIT, fold, 0.0, wob))
        else:
            L.append(seat_cushion(x, R1_SIT, 0.0, 0.0))
    for x in XS + [XS[-1] + SEAT_DX]:
        L.append(armrest(x - SEAT_DX / 2, R1_SIT, FLOOR, 0.0, False))
    if perched:
        L.append(shadow(g["x"], R1_TOP + 6, 110, 0.5))
        L.append(draw_grumpo())
    L.append(spill(t))
    if t >= T_RELEASE and not g["hold"] and t < T_CATCH:
        bx, by, br, bf = bucket_pos(t, g, n)
        L.append(bucket(ctx, bx, by, 1.0, br, bf))
    L.append(rain(t, n))

    # ---- effects
    # landing dust/puffs
    if T_LAND <= t < T_LAND + 0.5:
        q = seg(t, T_LAND, T_LAND + 0.5)
        for k in range(4):
            px = CX + 170 + (k - 1.5) * 30
            L.append(puff(px + 40 * (k - 1.5) * q, G_SIT_B - GR - 130 - 140 * math.sin(math.pi * q) * (0.6 + 0.2 * k), 1.0, 200 * q))
    L.append(impact(CX, G_SIT_B, seg(t, T_LAND, T_LAND + 0.2), "#ffffff"))
    L.append(symbol(CX, N_SIT_B - 2 * NR - 50, "?", seg(t, 0.55, 1.15), "#3a7ad6"))
    L.append(symbol(n["x"] - 40, n["y"] - 150, "!", seg(t, T_IDEA, T_IDEA + 0.55), "#ffb020"))
    L.append(symbol(g["x"] + 30, g["y"] - 170, "!", seg(t, T_APEX, T_APEX + 0.45)))
    # speed lines for the fast copy section
    if 3.05 <= t < 4.12:
        d = 1 if (kf(t + 0.02, GX_KEYS) - kf(t, GX_KEYS)) > 0 else -1
        L.append(speed_lines(g["x"] - d * 140, g["y"], 0 if d > 0 else 180, 0.8))
        L.append(speed_lines(n["x"] - d * 120, n["y"] - 20, 0 if d > 0 else 180, 0.6))
    # Nibbo's eye-line to the folded seat
    if T_FOLD + 0.1 <= t < T_FOLD + 0.45:
        L.append(impact(CX, R1_SIT - 110, seg(t, T_FOLD, T_FOLD + 0.3), "#ffffff"))
    if T_LAUNCH <= t < T_LAUNCH + 0.4:
        L.append(speed_lines(g["x"], g["b"] + 10, -90, 1 - seg(t, T_LAUNCH, T_LAUNCH + 0.4)))
    if T_DROP + 0.1 <= t < T_WEDGE:
        L.append(speed_lines(g["x"], g["y"] - GR * g["sy"] - 10, 90, 0.9))
    L.append(impact(CX, R1_SIT - 60, seg(t, T_WEDGE, T_WEDGE + 0.22), "#ffffff"))
    L.append(impact(CX, FLOOR - 10, seg(t, T_SLIP1, T_SLIP1 + 0.22), "#fff6a8"))
    if T_CATCH <= t < T_CATCH + 0.6:
        L.append(star_twinkle(n["x"] + 110, n["y"] - 80, seg(t, T_CATCH, T_CATCH + 0.6)))
    if T_TOSS1 - 0.05 <= t < T_TOSS1 + 0.5:
        L.append(star_twinkle(n["x"] - 90, n["y"] - 110, seg(t, T_TOSS1 - 0.05, T_TOSS1 + 0.5)))
    # grumble marks over flattened grumpo
    if 12.0 <= t < 12.9:
        L.append(f'<path d="M{CX+150} {FLOOR-90} l18 -8 l-6 18 M{CX+170} {FLOOR-70} l18 -8 l-6 18" stroke="#e8303a" stroke-width="6" fill="none" stroke-linecap="round"/>')

    col, op = movie_light(t)
    L.append(f'<rect x="-900" y="-400" width="2900" height="2700" fill="{col}" opacity="{op:.3f}"/>')

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{EXTRA_DEFS}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g>'
           f'<rect width="{W}" height="{H}" fill="url(#vign)"/></svg>')
    return overlay(svg, hook_title(t + 0.12, "Nibbo can't see", "THE MOVIE!"))


def build_sfx():
    sfx(0.0, "whoosh", 0.6, 0.8)
    sfx(T_LAND, "thud", 1.0, 0.9)
    sfx(T_LAND + 0.02, "squeak", 0.6, 0.7)
    sfx(T_LAND + 0.05, "popcorn", 0.5, 1.0)
    sfx(0.6, "gasp", 0.4, 1.4)
    # lean / copy pairs
    for tn, tg in [(1.10, 1.62), (2.20, 2.55)]:
        sfx(tn, "whoosh", 0.45, 1.6)
        sfx(tn + 0.18, "blip", 0.35, 1.3)
        sfx(tg, "whoosh", 0.7, 1.0)
        sfx(tg + 0.2, "squeak", 0.4, 0.9)
    for k, (tn, tg) in enumerate([(3.05, 3.12), (3.35, 3.42), (3.65, 3.72), (3.95, 4.0)]):
        sfx(tn, "whoosh", 0.4, 1.9 + 0.05 * k)
        sfx(tg, "whoosh", 0.55, 1.2 + 0.05 * k)
    sfx(4.4, "grumble", 0.35, 1.6)
    # stretch
    sfx(4.68, "stretch", 0.6, 1.3)
    sfx(5.18, "stretch", 0.8, 0.85)
    sfx(5.86, "boing", 0.6, 1.3)
    sfx(5.9, "boing", 0.6, 0.9)
    # perch hops
    sfx(6.25, "hop", 0.6, 1.3)
    sfx(6.6, "thunk", 0.5, 1.4)
    sfx(6.98, "hop", 0.7, 0.95)
    sfx(7.34, "thunk", 0.7, 1.0)
    sfx(T_FOLD, "seat_clack", 0.9, 1.0)
    sfx(7.66, "whoosh", 0.35, 1.7)
    sfx(T_IDEA, "ding", 0.5, 1.3)
    sfx(8.0, "whoosh", 0.45, 1.1)
    # crouch & fake jump
    sfx(8.5, "squish", 0.4, 1.3)
    sfx(8.62, "squish", 0.5, 0.9)
    sfx(8.7, "suspense", 0.45, 1.0)
    sfx(T_FAKE, "hop", 0.35, 1.6)
    sfx(T_LAUNCH, "boing", 0.9, 0.75)
    sfx(T_LAUNCH + 0.03, "whoosh", 0.7, 0.9)
    sfx(T_APEX, "gasp", 0.6, 0.9)
    sfx(T_RELEASE, "pop", 0.5, 0.9)
    sfx(T_RELEASE + 0.05, "popcorn", 0.8, 1.0)
    sfx(T_DROP, "slide_down", 0.7, 0.9)
    sfx(T_WEDGE, "thud", 0.9, 0.85)
    sfx(T_WEDGE + 0.02, "seat_clack", 0.7, 0.85)
    sfx(T_WEDGE + 0.1, "squeak", 0.6, 0.6)
    sfx(T_SLIP0 - 0.05, "squish", 0.8, 0.8)
    sfx(T_SLIP1, "thud", 0.7, 1.1)
    sfx(T_SLIP1 + 0.02, "squish", 0.5, 1.3)
    sfx(T_SLAM, "seat_clack", 1.0, 0.9)
    sfx(T_SLAM + 0.04, "squish", 0.6, 0.7)
    sfx(T_CATCH, "click", 0.6, 1.0)
    sfx(T_CATCH + 0.02, "ding", 0.4, 1.6)
    sfx(T_CATCH - 0.1, "popcorn", 0.7, 1.15)
    sfx(T_CATCH + 0.4, "popcorn", 0.5, 1.3)
    for tm in (11.9, 12.45, 13.0):
        sfx(tm, "munch", 0.7, 1.1)
    sfx(12.0, "grumble", 0.5, 0.95)
    sfx(T_FLASH, "rumble", 0.55, 0.8)
    sfx(T_FLASH + 0.05, "whoosh", 0.35, 0.6)
    sfx(T_TOSS0, "pop", 0.4, 1.4)
    sfx(T_TOSS1, "gulp", 0.6, 1.2)
    sfx(T_TOSS1 + 0.15, "laugh", 0.5, 1.3)
