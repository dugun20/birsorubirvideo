"""Grumpo & Nibbo — Episode 5: The Wishbone (Thanksgiving dinner table, escalating single joke, 60 fps).

One slice of pumpkin pie is left. Forks clash. Grumpo plucks the turkey's wishbone:
winner gets the pie. But this wishbone will NOT break — it bends like rubber, then
stretches right across the table. They pluck it at each other like a guitar string
(each one jiggles like jelly), then one huge yank ... SNAP! They fly off their chairs,
the pie is flung up, splits in two mid-air and lands in BOTH open mouths.
Their wishbone halves are exactly equal — so they clink them. They share.
"""
import math, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow
from hook import overlay, hook_title

W, H, FPS, DUR = 1080, 1920, 60, 16.0
GS = 0.92
NR = 112
TB, TF = 1560, 1760          # table surface back / front edge
CLOTH_BOT = 1900
FLOOR = 1915
GY0, NY0 = 1430, 1446        # seated centers (behind table)
PIE = (548, 1640)            # pie slice centre on its plate
TURKEY = (402, 1640)
WB_REST = (400, 1580)        # wishbone in the carcass

T_CLASH = 0.32
T_PLUCK = 1.9
T_GRAB = 2.75
T_BOING = 3.25
P2A, P2B = 4.6, 6.2          # big stretch
T_TW1 = 6.95                 # Grumpo plucks
T_TW2 = 8.05                 # Nibbo plucks back
T_YANK = 9.75
T_SNAP = 10.8
T_HIDE = 11.35
T_POP = 11.8
T_SPLIT = 11.5
T_EAT = 12.25
T_CLINK = 14.55

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


def kf(t, keys, ease=eio):
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return lerp(v0, v1, ease(seg(t, t0, t1)))
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


def jelly(t, t0, d, a):
    """jiggle like jelly after being hit by the twang wave."""
    k = t - t0
    if 0 <= k < d:
        e = math.exp(-k * 3.0) * a
        s = math.sin(k * 62)
        return 1 + e * s, 1 - e * s, 10 * e * math.sin(k * 47)
    return 1.0, 1.0, 0.0


def arm(x0, y0, x1, y1, col, w=10, sag=30):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    return f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


def hand(x, y, fill, stroke, r=13):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="5"/>'


def sweat(x, y, p=1.0):
    return f'<path d="M{x:.1f} {y:.1f} q12 20 0 28 q-12 -8 0 -28z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3" opacity="{p:.2f}"/>'


# ---------------------------------------------------------------- props
def pie_slice(x, y, rot=0.0, s=1.0, cream=True):
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">']
    # side (front) face: crust base + filling
    o.append(f'<path d="M-64 -4 L54 10 L54 40 L-64 20Z" fill="#d98a3a" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>')
    o.append('<path d="M-60 12 L52 28 L52 38 L-60 20Z" fill="#c9843e"/>')
    o.append('<path d="M-60 -2 L52 12 L52 20 L-60 6Z" fill="#f0a24a" opacity="0.7"/>')
    # top face
    o.append(f'<path d="M-64 -4 L44 -32 Q 64 -12 54 10Z" fill="#f29a3c" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>')
    o.append('<path d="M-40 -6 L30 -24" stroke="#ffc074" stroke-width="5" stroke-linecap="round" opacity="0.8"/>')
    # back crust
    o.append(f'<path d="M44 -32 Q 66 -12 54 10 L54 40 Q 76 16 70 -10 Q 64 -34 44 -32Z" fill="#d9a05a" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>')
    o.append('<path d="M58 -22 q6 4 3 10 M63 -6 q6 4 3 10 M62 10 q6 4 2 10" stroke="#a8682a" stroke-width="3.5" fill="none" stroke-linecap="round"/>')
    if cream:
        o.append(f'<path d="M-22 -14 Q -30 -30 -14 -32 Q -12 -48 4 -44 Q 20 -50 22 -34 Q 34 -28 24 -14 Q 0 -6 -22 -14Z" fill="#fffaf2" stroke="{OL}" stroke-width="4.5" stroke-linejoin="round"/>'
                 '<path d="M-12 -24 q8 -8 18 -2" stroke="#e6dccb" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
                 '<ellipse cx="-8" cy="-36" rx="5" ry="3" fill="#ffffff"/>')
    o.append('</g>')
    return "".join(o)


def half_slice(x, y, rot, s, side):
    """one half of the split slice (side -1 = left/tip half, 1 = crust half)."""
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">']
    if side < 0:
        o.append(f'<path d="M-40 -2 L22 -18 L22 26 L-40 14Z" fill="#d98a3a" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
                 f'<path d="M-40 -2 L22 -18 L22 8Z" fill="#f29a3c" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
                 '<path d="M-20 0 L12 -10" stroke="#ffc074" stroke-width="4" stroke-linecap="round"/>'
                 '<path d="M22 -18 l-5 8 l6 6 l-5 8 l5 8" stroke="#ffdfb0" stroke-width="3" fill="none"/>')
    else:
        o.append(f'<path d="M-28 -12 L20 -26 Q 38 -8 30 10 L30 34 L-28 24Z" fill="#d98a3a" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
                 f'<path d="M-28 -12 L20 -26 Q 38 -8 30 10 L-28 2Z" fill="#f29a3c" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
                 f'<path d="M20 -26 Q 40 -8 30 10 L30 34 Q 48 14 42 -6 Q 38 -26 20 -26Z" fill="#d9a05a" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
                 f'<path d="M-10 -14 Q -16 -26 -4 -28 Q 4 -38 14 -28 Q 22 -20 14 -12 Q 0 -8 -10 -14Z" fill="#fffaf2" stroke="{OL}" stroke-width="4"/>')
    o.append('</g>')
    return "".join(o)


def plate(x, y, rattle=0.0):
    return (f'<g transform="translate({x:.1f} {y - abs(rattle):.1f}) rotate({rattle*0.6:.1f})">'
            f'<ellipse cx="0" cy="10" rx="84" ry="20" fill="#1a1028" opacity="0.18"/>'
            f'<ellipse cx="0" cy="0" rx="82" ry="20" fill="#fbf7ef" stroke="{OL}" stroke-width="5"/>'
            '<ellipse cx="0" cy="0" rx="62" ry="13" fill="none" stroke="#8fb6e0" stroke-width="4"/>'
            '<ellipse cx="0" cy="-1" rx="50" ry="9" fill="#f2ece0"/></g>')


def wishbone_small(x, y, rot=0.0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            f'<path d="M-26 -30 Q -22 6 0 18 Q 22 6 26 -30" fill="none" stroke="{OL}" stroke-width="15" stroke-linecap="round"/>'
            '<path d="M-26 -30 Q -22 6 0 18 Q 22 6 26 -30" fill="none" stroke="#f4e9cc" stroke-width="8" stroke-linecap="round"/>'
            f'<circle cx="0" cy="18" r="9" fill="#f4e9cc" stroke="{OL}" stroke-width="4"/></g>')


def turkey(t):
    x, y = TURKEY
    o = [f'<ellipse cx="{x}" cy="{y+12}" rx="104" ry="22" fill="#1a1028" opacity="0.18"/>',
         f'<ellipse cx="{x}" cy="{y}" rx="100" ry="24" fill="#e9eef3" stroke="{OL}" stroke-width="5"/>',
         f'<ellipse cx="{x}" cy="{y-2}" rx="80" ry="15" fill="#d6dee8"/>']
    # parsley
    for dx in (-78, 70):
        o.append(f'<g stroke="{OL}" stroke-width="3"><circle cx="{x+dx}" cy="{y-6}" r="11" fill="#5aa947"/><circle cx="{x+dx+12}" cy="{y-2}" r="9" fill="#6dbb5f"/></g>')
    # picked carcass: roasted dome with bare ribs
    o.append(f'<path d="M{x-66} {y-4} Q {x-70} {y-62} {x-10} {y-70} Q {x+56} {y-72} {x+66} {y-6}Z" fill="#c8722e" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>')
    o.append(f'<path d="M{x-52} {y-14} Q {x-50} {y-52} {x-12} {y-58}" stroke="#e39a52" stroke-width="9" fill="none" stroke-linecap="round"/>')
    for k, dx in enumerate((-30, -2, 26)):
        o.append(f'<path d="M{x+dx-14} {y-10} Q {x+dx} {y-66} {x+dx+14} {y-10}" fill="none" stroke="{OL}" stroke-width="12" stroke-linecap="round"/>'
                 f'<path d="M{x+dx-14} {y-10} Q {x+dx} {y-66} {x+dx+14} {y-10}" fill="none" stroke="#f4e9cc" stroke-width="6" stroke-linecap="round"/>')
    # drumstick bone
    o.append(f'<g transform="rotate(30 {x+56} {y-30})"><rect x="{x+50}" y="{y-92}" width="13" height="64" rx="6" fill="#f4e9cc" stroke="{OL}" stroke-width="5"/>'
             f'<circle cx="{x+50}" cy="{y-94}" r="10" fill="#f4e9cc" stroke="{OL}" stroke-width="5"/><circle cx="{x+63}" cy="{y-94}" r="10" fill="#f4e9cc" stroke="{OL}" stroke-width="5"/>'
             f'<rect x="{x+51}" y="{y-96}" width="11" height="14" fill="#f4e9cc"/></g>')
    if t < T_PLUCK:
        wig = 3 * math.sin(t * 50) if 1.75 <= t < T_PLUCK else 0
        o.append(wishbone_small(WB_REST[0], WB_REST[1], wig, 0.95))
    return "".join(o)


def pumpkin(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})">'
            f'<ellipse cx="0" cy="8" rx="56" ry="12" fill="#1a1028" opacity="0.18"/>'
            f'<g stroke="{OL}" stroke-width="5"><ellipse cx="-24" cy="-26" rx="26" ry="32" fill="#e8772a"/><ellipse cx="24" cy="-26" rx="26" ry="32" fill="#e8772a"/>'
            '<ellipse cx="0" cy="-28" rx="26" ry="35" fill="#f58a34"/></g>'
            '<path d="M-6 -50 q6 -6 10 0" stroke="#ffb066" stroke-width="5" fill="none" stroke-linecap="round"/>'
            f'<path d="M0 -60 q2 -22 14 -26" stroke="{OL}" stroke-width="12" fill="none" stroke-linecap="round"/>'
            '<path d="M0 -60 q2 -22 14 -26" stroke="#6a8a2a" stroke-width="6" fill="none" stroke-linecap="round"/>'
            f'<path d="M8 -70 q22 -8 30 8 q-18 6 -30 -8z" fill="#5aa947" stroke="{OL}" stroke-width="3.5"/></g>')


def candle(x, y, t, ph=0.0):
    fl = 1 + 0.12 * math.sin(t * 23 + ph) + 0.06 * math.sin(t * 41 + ph)
    return (f'<circle cx="{x}" cy="{y-118}" r="46" fill="#fff3b0" opacity="0.28"/>'
            f'<rect x="{x-26}" y="{y-14}" width="52" height="16" rx="6" fill="#c9a24a" stroke="{OL}" stroke-width="4"/>'
            f'<rect x="{x-13}" y="{y-104}" width="26" height="92" rx="5" fill="#fff4dc" stroke="{OL}" stroke-width="4.5"/>'
            f'<rect x="{x-8}" y="{y-98}" width="6" height="80" rx="3" fill="#ffffff"/>'
            f'<g transform="translate({x} {y-108}) scale(1 {fl:.2f})"><path d="M0 -34 Q 15 -10 0 0 Q -15 -10 0 -34Z" fill="#ffb02a" stroke="#d45a0a" stroke-width="3"/>'
            '<path d="M0 -18 Q 6 -7 0 -3 Q -6 -7 0 -18Z" fill="#fff3a8"/></g>')


def gravy(x, y):
    return (f'<g transform="translate({x} {y})"><ellipse cx="0" cy="8" rx="60" ry="12" fill="#1a1028" opacity="0.18"/>'
            f'<path d="M-44 -30 Q -46 4 0 6 Q 40 4 40 -30Z" fill="#fbf7ef" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M40 -30 Q 66 -40 72 -46 Q 62 -24 38 -14" fill="#fbf7ef" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M-44 -30 Q -50 -52 -64 -40" fill="none" stroke="{OL}" stroke-width="5"/>'
            f'<ellipse cx="-2" cy="-30" rx="42" ry="9" fill="#8a4a1e" stroke="{OL}" stroke-width="4"/></g>')


def corn(x, y, rot):
    o = [f'<g transform="translate({x} {y}) rotate({rot})">',
         f'<path d="M-50 -4 Q -60 -30 -86 -36 Q -66 -6 -50 6Z" fill="#c9b27a" stroke="{OL}" stroke-width="4"/>',
         f'<rect x="-52" y="-16" width="104" height="32" rx="16" fill="#ffcf3a" stroke="{OL}" stroke-width="5"/>']
    for i in range(6):
        o.append(f'<path d="M{-36+i*14} -12 v24" stroke="#e8a81a" stroke-width="3"/>')
    o.append('</g>')
    return "".join(o)


# ---------------------------------------------------------------- room + table
def room(t):
    o = [f'<rect x="-600" y="-900" width="2400" height="{FLOOR+900}" fill="#f2d6ac"/>']
    # damask-ish wallpaper stripes + diamonds
    for x in range(-600, 1800, 110):
        o.append(f'<rect x="{x}" y="-900" width="44" height="{FLOOR+900}" fill="#ecca9a"/>')
        for y in range(700, 1500, 130):
            o.append(f'<path d="M{x+77} {y} l12 16 l-12 16 l-12 -16z" fill="#e2b984"/>')
    # dado rail
    o.append(f'<rect x="-600" y="1370" width="2400" height="20" fill="#8a4a24" stroke="{OL}" stroke-width="4"/>')
    o.append(f'<rect x="-600" y="1390" width="2400" height="{FLOOR-1390}" fill="#a65a2e"/>')
    # window (dusk sky + falling leaves)
    wx0, wx1, wy0, wy1 = 380, 716, 900, 1300
    o.append(f'<rect x="{wx0-18}" y="{wy0-18}" width="{wx1-wx0+36}" height="{wy1-wy0+36}" rx="12" fill="#f8efe2" stroke="{OL}" stroke-width="7"/>')
    o.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1-wx0}" height="{wy1-wy0}" fill="url(#dusk)"/>')
    cid = "winclip"
    o.append(f'<clipPath id="{cid}"><rect x="{wx0}" y="{wy0}" width="{wx1-wx0}" height="{wy1-wy0}"/></clipPath><g clip-path="url(#{cid})">')
    o.append(f'<circle cx="{wx0+250}" cy="{wy1-70}" r="46" fill="#ffd9a0" opacity="0.9"/>')
    o.append(f'<path d="M{wx0-20} {wy1-40} Q {wx0+90} {wy1-120} {wx0+200} {wy1-60} Q {wx0+290} {wy1-110} {wx1+20} {wy1-60} V{wy1+10} H{wx0-20}Z" fill="#6a3a5a"/>')
    o.append(f'<path d="M{wx0+60} {wy1-60} V{wy1-170} M{wx0+60} {wy1-130} l-36 -36 M{wx0+60} {wy1-150} l30 -30" stroke="#4a2440" stroke-width="10" stroke-linecap="round"/>')
    for (cx, cy, r) in [(wx0+30, wy1-180, 34), (wx0+80, wy1-200, 40), (wx0+50, wy1-150, 30)]:
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#d9542a" opacity="0.9"/>')
    rnd = random.Random(7)
    for k in range(7):
        ph = rnd.random()
        x0 = wx0 + rnd.uniform(0, wx1 - wx0)
        p = (t * 0.22 + ph) % 1
        lx = x0 + 40 * math.sin(p * 9 + k)
        ly = wy0 - 30 + p * (wy1 - wy0 + 60)
        col = ["#ff9a2a", "#e8452a", "#ffcf3a"][k % 3]
        o.append(f'<ellipse cx="{lx:.1f}" cy="{ly:.1f}" rx="11" ry="6" fill="{col}" transform="rotate({p*720+k*40:.0f} {lx:.1f} {ly:.1f})"/>')
    o.append('</g>')
    o.append(f'<path d="M{(wx0+wx1)/2} {wy0} V{wy1} M{wx0} {(wy0+wy1)/2} H{wx1}" stroke="#f8efe2" stroke-width="14"/>')
    o.append(f'<rect x="{wx0}" y="{wy0}" width="{wx1-wx0}" height="{wy1-wy0}" fill="none" stroke="{OL}" stroke-width="5"/>')
    # curtains
    for side in (-1, 1):
        cx = wx0 - 30 if side < 0 else wx1 + 30
        x_in = cx + 70 * (1 if side < 0 else -1)
        x_out = cx - 60 * (1 if side < 0 else -1)
        o.append(f'<path d="M{x_out} {wy0-50} L{x_in} {wy0-50} Q {x_in-40*(1 if side<0 else -1)} {wy0+200} {x_in+10*(1 if side<0 else -1)} {wy1+40} L{x_out} {wy1+60}Z" '
                 f'fill="#b8342e" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>')
        for k in range(2):
            fx = x_out + (k + 1) * 40 * (1 if side < 0 else -1)
            o.append(f'<path d="M{fx} {wy0-40} Q {fx+6} {wy0+180} {fx-4} {wy1+40}" stroke="#8e2420" stroke-width="7" fill="none" stroke-linecap="round"/>')
        o.append(f'<rect x="{min(x_out, x_in)-6}" y="{wy0+150}" width="{abs(x_in-x_out)+12}" height="20" rx="8" fill="#ffcf3a" stroke="{OL}" stroke-width="4"/>')
    o.append(f'<rect x="{wx0-120}" y="{wy0-66}" width="{wx1-wx0+240}" height="20" rx="10" fill="#8a4a24" stroke="{OL}" stroke-width="5"/>')
    # leaf garland across the wall
    gpts = []
    for k in range(-3, 15):
        x = -200 + k * 100
        gpts.append((x, 1040 + 34 * math.sin(k * 0.9)))
    path = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in gpts)
    o.append(f'<path d="{path}" fill="none" stroke="#6a3a1a" stroke-width="5"/>')
    for k, (x, y) in enumerate(gpts):
        col = ["#e8452a", "#ff9a2a", "#ffcf3a", "#c8501e"][k % 4]
        sw = 6 * math.sin(t * 2 + k)
        o.append(f'<g transform="translate({x:.0f} {y+18:.0f}) rotate({sw:.1f})"><path d="M0 -14 L10 -4 L18 -8 L14 6 L22 14 L8 14 L0 26 L-8 14 L-22 14 L-14 6 L-18 -8 L-10 -4Z" '
                 f'fill="{col}" stroke="{OL}" stroke-width="3.5" stroke-linejoin="round"/></g>')
    # framed pictures
    for (px, py, w, h) in [(110, 1130, 150, 180), (990, 1130, 150, 180)]:
        o.append(f'<rect x="{px-w/2}" y="{py-h/2}" width="{w}" height="{h}" rx="6" fill="#c98a3a" stroke="{OL}" stroke-width="6"/>'
                 f'<rect x="{px-w/2+16}" y="{py-h/2+16}" width="{w-32}" height="{h-32}" fill="#bfe0f0"/>'
                 f'<path d="M{px-w/2+16} {py+h/2-16} L{px-20} {py-10} L{px+10} {py+20} L{px+30} {py} L{px+w/2-16} {py+h/2-16}Z" fill="#7cb86a"/>'
                 f'<circle cx="{px+25}" cy="{py-40}" r="14" fill="#ffe08a"/>')
    return "".join(o)


def chair(x, rot):
    piv = (x, 1760)
    return (f'<g transform="rotate({rot:.1f} {piv[0]} {piv[1]})">'
            f'<rect x="{x-118}" y="1262" width="26" height="520" rx="10" fill="#8a4a24" stroke="{OL}" stroke-width="6"/>'
            f'<rect x="{x+92}" y="1262" width="26" height="520" rx="10" fill="#8a4a24" stroke="{OL}" stroke-width="6"/>'
            f'<rect x="{x-128}" y="1246" width="256" height="40" rx="18" fill="#a85e30" stroke="{OL}" stroke-width="6"/>'
            f'<rect x="{x-112}" y="1252" width="200" height="10" rx="5" fill="#c97a46"/>'
            f'<rect x="{x-110}" y="1350" width="220" height="22" rx="8" fill="#a85e30" stroke="{OL}" stroke-width="5"/></g>')


def cranberry(x, y):
    return (f'<g transform="translate({x} {y})"><ellipse cx="0" cy="10" rx="62" ry="13" fill="#1a1028" opacity="0.18"/>'
            f'<path d="M-54 -22 Q -50 16 0 18 Q 50 16 54 -22Z" fill="#fbf7ef" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            '<path d="M-44 -6 Q 0 8 44 -6" stroke="#8fb6e0" stroke-width="4" fill="none"/>'
            f'<ellipse cx="0" cy="-22" rx="54" ry="13" fill="#b81e3a" stroke="{OL}" stroke-width="5"/>'
            '<circle cx="-18" cy="-24" r="6" fill="#e8455a"/><circle cx="6" cy="-20" r="5" fill="#e8455a"/><circle cx="22" cy="-26" r="5" fill="#e8455a"/>'
            '<ellipse cx="-24" cy="-28" rx="8" ry="3" fill="#ffffff" opacity="0.5"/></g>')


def table_front():
    o = []
    # deep table surface (seen from above), checked tablecloth
    o.append(f'<path d="M-400 {TB} H1500 L1580 {TF} H-480Z" fill="#fbf3e2" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>')
    for k in range(1, 5):
        y = TB + k * (TF - TB) / 5
        o.append(f'<path d="M-440 {y:.0f} H1540" stroke="#f0dcc0" stroke-width="16"/>')
    for x in range(-400, 1500, 120):
        o.append(f'<path d="M{x} {TB} L{x + (x-548)*0.12:.0f} {TF}" stroke="#f0dcc0" stroke-width="14"/>')
    # runner down the long axis
    o.append(f'<path d="M-420 {TB+64} H1520 L1530 {TB+132} H-430Z" fill="#d96a2a"/>')
    o.append(f'<path d="M-420 {TB+72} H1520 M-428 {TB+124} H1528" stroke="#ffcf3a" stroke-width="5"/>')
    for x in range(-400, 1500, 100):
        o.append(f'<path d="M{x+50} {TB+86} l10 12 l-10 12 l-10 -12z" fill="#ffb066"/>')
    o.append(f'<path d="M-400 {TB} H1500" stroke="{OL}" stroke-width="6"/>')
    # skirt
    o.append(f'<rect x="-480" y="{TF}" width="2060" height="{CLOTH_BOT-TF}" fill="#c8502a" stroke="{OL}" stroke-width="6"/>')
    for x in range(-480, 1580, 90):
        o.append(f'<path d="M{x+45} {TF+10} V{CLOTH_BOT-6}" stroke="#a83e1e" stroke-width="16" stroke-linecap="round" opacity="0.8"/>')
    o.append("".join(f'<path d="M{x} {CLOTH_BOT-6} q22 26 45 0 q22 26 45 0" fill="#c8502a" stroke="{OL}" stroke-width="5"/>' for x in range(-480, 1580, 90)))
    o.append(f'<rect x="-480" y="{TF}" width="2060" height="16" fill="#fbf3e2" stroke="{OL}" stroke-width="5"/>')
    for x in range(-470, 1580, 30):
        o.append(f'<circle cx="{x}" cy="{TF+18}" r="7" fill="#fbf3e2" stroke="{OL}" stroke-width="3"/>')
    # floor
    o.append(f'<rect x="-600" y="{CLOTH_BOT+14}" width="2400" height="600" fill="#7a4626"/>')
    for k, y in enumerate(range(CLOTH_BOT + 14, CLOTH_BOT + 600, 46)):
        off = (k % 2) * 120
        o.append(f'<path d="M-600 {y} H1800" stroke="#5e3218" stroke-width="4"/>')
        for x in range(-600 + off, 1800, 240):
            o.append(f'<path d="M{x} {y} v46" stroke="#5e3218" stroke-width="4"/>')
    return "".join(o)


# ---------------------------------------------------------------- character motion
GXK = [(0, 330), (P2A, 330), (P2B, 282), (T_YANK, 282), (T_YANK + 0.3, 272), (T_SNAP, 272),
       (T_HIDE, 150), (T_POP - 0.01, 150), (T_POP, 250), (13.9, 250), (T_CLINK - 0.05, 318), (DUR, 318)]
NXK = [(0, 760), (P2A, 760), (P2B, 812), (T_YANK, 812), (T_YANK + 0.3, 822), (T_SNAP, 822),
       (T_HIDE, 945), (T_POP - 0.01, 945), (T_POP, 845), (13.9, 845), (T_CLINK - 0.05, 778), (DUR, 778)]
AXK = [(T_GRAB, 492), (3.0, 492), (3.22, 466), (3.5, 494), (P2A, 494), (P2B, 400), (T_YANK, 400), (T_YANK + 0.3, 388), (T_SNAP, 345)]
BXK = [(T_GRAB, 604), (3.0, 604), (3.22, 630), (3.5, 602), (P2A, 602), (P2B, 700), (T_YANK, 700), (T_YANK + 0.3, 712), (T_SNAP, 755)]
BAND_Y = 1478


def fling(t, side):
    """after the snap: thrown back off the chair, disappears behind the table."""
    k = seg(t, T_SNAP, T_HIDE)
    y0 = GY0 if side < 0 else NY0
    y = y0 - 150 * math.sin(math.pi * min(1, k * 1.6)) * (1 - k) + 420 * ein(k)
    rot = side * 130 * eout(k)
    return y, rot


def popup(t, y0):
    k = seg(t, T_POP, T_POP + 0.3)
    if k < 1:
        return lerp(y0 + 360, y0 - 30, eout(k / 0.75)) if k < 0.75 else lerp(y0 - 30, y0, eio((k - 0.75) / 0.25))
    return y0


def grumpo_state(t):
    g = dict(x=kf(t, GXK), y=GY0, look=(1, 0), sx=1.0, sy=1.0, red=0.0, rot=0.0)
    g["ex"] = pick(t, [(0, "angry"), (1.2, "grumpy"), (1.45, "suspicious"), (1.9, "smug"), (3.0, "angry"), (T_BOING, "shock"),
                       (3.7, "suspicious"), (4.3, "angry"), (6.55, "smug"), (T_TW2 - 0.15, "shock"), (8.45, "shock"), (9.15, "angry"),
                       (T_SNAP, "shock"), (T_EAT + 0.08, "smug"), (13.25, "suspicious"), (13.75, "shock"), (14.05, "smug")], "angry")
    g["look"] = pick(t, [(0, (1, 0.6)), (1.2, (1, 0)), (1.45, (1, 0.7)), (1.9, (1, -0.6)), (2.4, (1, 0)), (3.0, (1, -0.2)),
                         (3.7, (1, -0.5)), (4.3, (1, 0)), (6.55, (1, 0.2)), (7.2, (1, 0)), (T_TW2 - 0.15, (1, 0)),
                         (T_SNAP, (0, -1)), (T_POP, (0.6, -1)), (T_EAT, (0, 0.3)), (13.25, (0.6, -1)), (13.75, (1, 0)), (14.05, (1, -0.3))], (1, 0))
    if T_SPLIT <= t < T_EAT:
        g["look"] = (lerp(0.6, -0.2, seg(t, T_SPLIT, T_EAT)), lerp(-1, 0.4, seg(t, T_SPLIT, T_EAT)))
    # red face
    if P2A <= t < 6.6:
        g["red"] = 0.35 * seg(t, P2A, P2B) * (1 - seg(t, 6.4, 6.6))
    if 8.4 <= t < T_SNAP:
        g["red"] = 0.55 * seg(t, 8.6, 9.3)
    if T_SNAP <= t < T_HIDE:
        g["red"] = 0.55 * (1 - seg(t, T_SNAP, T_HIDE))
    # body motion
    if t < 0.95:
        g["x"] += 6 * math.sin(t * 40) * seg(t, T_CLASH, T_CLASH + 0.05)
        g["rot"] = 8 * eout(seg(t, 0, T_CLASH))
    if T_PLUCK <= t < T_PLUCK + 0.3:
        g["sx"], g["sy"] = squash(t, T_PLUCK, 0.3, 0.12)
    if 2.4 <= t < 2.7:
        g["y"] = GY0 - 26 * math.sin(math.pi * seg(t, 2.4, 2.7))
    if 3.0 <= t < 3.6:
        g["rot"] = -12 * math.sin(math.pi * seg(t, 3.0, 3.25)) if t < 3.25 else 10 * math.exp(-(t - 3.25) * 8) * math.sin((t - 3.25) * 30)
    if 4.3 <= t < P2A:
        g["sx"], g["sy"] = squash(t, 4.3, 0.3, 0.12)
    if P2A <= t < T_SNAP:
        lean = -16 * seg(t, P2A, P2A + 0.4)
        if t >= T_YANK:
            lean = -16 - 14 * eout(seg(t, T_YANK, T_YANK + 0.25))
        g["rot"] = lean + 1.5 * math.sin(t * 60) * (1 if (P2B - 0.4 <= t < 6.6 or t >= T_YANK) else 0)
    if 9.3 <= t < T_YANK:
        k = eio(seg(t, 9.3, 9.65))
        g["sx"], g["sy"] = 1 + 0.12 * k, 1 + 0.06 * k
    jx, jy, jr = jelly(t, T_TW2 + 0.32, 0.9, 0.2)
    g["sx"] *= jx
    g["sy"] *= jy
    g["x"] += jr
    if T_SNAP <= t < T_POP:
        g["y"], g["rot"] = fling(t, -1)
    if T_POP <= t:
        g["y"] = popup(t, GY0)
        g["sx"], g["sy"] = squash(t, T_POP + 0.22, 0.25, 0.1)
    if T_EAT <= t < 13.2:
        c = math.sin((t - T_EAT) * 22)
        g["sx"], g["sy"] = 1 + 0.04 * c, 1 - 0.04 * c
        if t < T_EAT + 0.25:
            g["sx"], g["sy"] = squash(t, T_EAT, 0.25, 0.14)
    if 13.9 <= t < T_CLINK:
        g["y"] = GY0 - 30 * math.sin(math.pi * seg(t, 13.9, T_CLINK))
        g["rot"] = 10 * math.sin(math.pi * seg(t, 13.9, T_CLINK))
    if t >= T_CLINK + 0.3:
        g["y"] = GY0 - 6 * abs(math.sin((t - T_CLINK) * 5))
    return g


def nibbo_state(t):
    n = dict(x=kf(t, NXK), y=NY0, rot=0.0, sx=1.0, sy=1.0)
    n["ex"] = pick(t, [(0, "uhoh"), (T_CLASH, "wow"), (0.9, "nervous"), (1.45, "uhoh"), (2.15, "wow"), (2.4, "joy"), (2.8, "happy"),
                       (T_BOING, "wow"), (3.7, "uhoh"), (4.3, "happy"), (P2A + 0.2, "nervous"), (T_TW1 + 0.3, "dizzy"),
                       (7.75, "happy"), (T_TW2 - 0.05, "joy"), (9.25, "nervous"), (T_SNAP, "wow"), (T_EAT + 0.08, "joy"),
                       (13.25, "happy"), (13.75, "wow"), (14.05, "happy"), (T_CLINK, "joy")], "uhoh")
    if t < 0.95:
        n["x"] += 6 * math.sin(t * 40 + 1) * seg(t, T_CLASH, T_CLASH + 0.05)
        n["rot"] = -8 * eout(seg(t, 0, T_CLASH))
    if 2.4 <= t < 2.8:
        n["y"] = NY0 - 40 * abs(math.sin(math.pi * 2 * seg(t, 2.4, 2.8)))
    if 3.0 <= t < 3.6:
        n["rot"] = 12 * math.sin(math.pi * seg(t, 3.0, 3.25)) if t < 3.25 else -10 * math.exp(-(t - 3.25) * 8) * math.sin((t - 3.25) * 30)
    if 4.3 <= t < P2A:
        n["sx"], n["sy"] = squash(t, 4.3, 0.3, 0.12)
    if P2A <= t < T_SNAP:
        lean = 16 * seg(t, P2A, P2A + 0.4)
        if t >= T_YANK:
            lean = 16 + 14 * eout(seg(t, T_YANK, T_YANK + 0.25))
        n["rot"] = lean + 1.5 * math.sin(t * 60 + 2) * (1 if (P2B - 0.4 <= t < 6.6 or t >= T_YANK) else 0)
    if 9.3 <= t < T_YANK:
        k = eio(seg(t, 9.3, 9.65))
        n["sx"], n["sy"] = 1 + 0.12 * k, 1 + 0.06 * k
    jx, jy, jr = jelly(t, T_TW1 + 0.3, 0.8, 0.16)
    n["sx"] *= jx
    n["sy"] *= jy
    n["x"] += jr
    if 8.4 <= t < 9.2:   # giggles at Grumpo
        n["y"] = NY0 - 8 * abs(math.sin(t * 24))
    if T_SNAP <= t < T_POP:
        n["y"], n["rot"] = fling(t, 1)
    if T_POP <= t:
        n["y"] = popup(t - 0.06, NY0)
        n["sx"], n["sy"] = squash(t, T_POP + 0.28, 0.25, 0.12)
    if T_EAT <= t < 13.2:
        c = math.sin((t - T_EAT) * 22 + 1)
        n["sx"], n["sy"] = 1 + 0.05 * c, 1 - 0.05 * c
        if t < T_EAT + 0.25:
            n["sx"], n["sy"] = squash(t, T_EAT, 0.25, 0.16)
    if 13.9 <= t < T_CLINK:
        n["y"] = NY0 - 30 * math.sin(math.pi * seg(t, 13.9, T_CLINK))
        n["rot"] = -10 * math.sin(math.pi * seg(t, 13.9, T_CLINK))
    if t >= T_CLINK + 0.3:
        n["y"] = NY0 - 8 * abs(math.sin((t - T_CLINK) * 5 + 0.7))
    return n


# ---------------------------------------------------------------- the wishbone
def pulses(t):
    """travelling bumps along the stretched bone: (centre x, amplitude, width)."""
    out = []
    # Grumpo pluck: held down then released
    if 6.7 <= t < T_TW1:
        out.append((440, 34 * eio(seg(t, 6.7, 6.9)), 46))
    if T_TW1 <= t < T_TW1 + 0.32:
        p = seg(t, T_TW1, T_TW1 + 0.3)
        out.append((lerp(440, 692, p), -38 * (1 - 0.3 * p), 50))
    if 7.85 <= t < T_TW2:
        out.append((660, 46 * eio(seg(t, 7.85, 8.0)), 50))
    if T_TW2 <= t < T_TW2 + 0.34:
        p = seg(t, T_TW2, T_TW2 + 0.32)
        out.append((lerp(660, 405, p), -60 * (1 - 0.3 * p), 56))
    return out


def band_points(A, B, J, t, N=48):
    vib = 0.0
    for t0, a in [(T_TW1, 10), (T_TW2, 16)]:
        if t >= t0:
            vib += a * math.exp(-(t - t0) * 4.5) * math.sin((t - t0) * 70)
    if T_YANK + 0.25 <= t < T_SNAP:
        vib += 2.5 * math.sin(t * 90)
    pl = pulses(t)
    pts = []
    for i in range(N + 1):
        u = i / N
        if u <= 0.5:
            v = u / 0.5
            c = ((A[0] + J[0]) / 2, (A[1] + J[1]) / 2 + 8)
            x = (1 - v) ** 2 * A[0] + 2 * (1 - v) * v * c[0] + v * v * J[0]
            y = (1 - v) ** 2 * A[1] + 2 * (1 - v) * v * c[1] + v * v * J[1]
        else:
            v = (u - 0.5) / 0.5
            c = ((J[0] + B[0]) / 2, (J[1] + B[1]) / 2 + 8)
            x = (1 - v) ** 2 * J[0] + 2 * (1 - v) * v * c[0] + v * v * B[0]
            y = (1 - v) ** 2 * J[1] + 2 * (1 - v) * v * c[1] + v * v * B[1]
        y += vib * math.sin(math.pi * u)
        for (px, amp, wd) in pl:
            y += amp * math.exp(-((x - px) / wd) ** 2)
        pts.append((x, y))
    return pts


def bone_path(pts, th, col="#f4e9cc"):
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return (f'<path d="{d}" fill="none" stroke="{OL}" stroke-width="{th+9:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{th:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')


def wb_ends(t, g, n):
    A = (kf(t, AXK), BAND_Y + (g["y"] - GY0) * 0.3)
    B = (kf(t, BXK), BAND_Y + (n["y"] - NY0) * 0.3)
    return A, B


def wishbone_full(t, A, B):
    d = max(1.0, B[0] - A[0])
    d0 = 112.0
    sag = 46 * min(1.0, (d0 / d)) ** 1.1
    jx = (A[0] + B[0]) / 2
    jy = (A[1] + B[1]) / 2 + sag
    if 3.0 <= t < 3.9:   # rubbery bend instead of breaking
        if t < T_BOING:
            jy += 50 * eio(seg(t, 3.0, T_BOING))
        else:
            jy += 50 * math.exp(-(t - T_BOING) * 7) * math.cos((t - T_BOING) * 34)
    th = max(8.0, 15 * (d0 / d) ** 0.45)
    if t >= T_YANK:
        th = lerp(th, 5.5, seg(t, T_YANK, T_YANK + 0.3))
    pts = band_points(A, B, (jx, jy), t)
    jp = pts[len(pts) // 2]
    o = [bone_path(pts, th)]
    o.append(f'<circle cx="{jp[0]:.1f}" cy="{jp[1]:.1f}" r="{max(6, th*0.9):.1f}" fill="#f4e9cc" stroke="{OL}" stroke-width="4.5"/>')
    if th > 8:
        hl = " L".join(f"{x:.1f} {y - th*0.18:.1f}" for x, y in pts[6:len(pts)//2 - 4])
        o.append(f'<path d="M{hl}" fill="none" stroke="#ffffff" stroke-width="{th*0.22:.1f}" stroke-linecap="round" opacity="0.7"/>')
    # cracks right before the snap
    if T_YANK + 0.35 <= t < T_SNAP:
        k = seg(t, T_YANK + 0.35, T_SNAP - 0.1)
        x, y = jp
        o.append(f'<g opacity="{min(1, k*3):.2f}"><path d="M{x-4:.1f} {y-14:.1f} l6 8 l-5 6 l6 8" stroke="{OL}" stroke-width="3" fill="none"/>'
                 f'<path d="M{x+7:.1f} {y+12:.1f} l-5 -7 l4 -6" stroke="{OL}" stroke-width="3" fill="none"/></g>')
        if k > 0.5:
            o.append(f'<path d="M{x-30:.1f} {y-40:.1f} l10 12 M{x+30:.1f} {y-40:.1f} l-10 12 M{x:.1f} {y-48:.1f} v14" stroke="#ffffff" stroke-width="5" stroke-linecap="round" opacity="{(k-0.5)*2:.2f}"/>')
    return "".join(o), jp


def half_bone(Hx, Hy, ang, L=78, th=12):
    a = math.radians(ang)
    ex, ey = Hx + L * math.cos(a), Hy + L * math.sin(a)
    mx, my = (Hx + ex) / 2 - 10 * math.sin(a), (Hy + ey) / 2 + 10 * math.cos(a)
    d = f"M{Hx:.1f} {Hy:.1f} Q {mx:.1f} {my:.1f} {ex:.1f} {ey:.1f}"
    return (f'<path d="{d}" fill="none" stroke="{OL}" stroke-width="{th+9}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="#f4e9cc" stroke-width="{th}" stroke-linecap="round"/>'
            f'<path d="M{ex:.1f} {ey:.1f} l{6*math.cos(a+1.2):.1f} {6*math.sin(a+1.2):.1f} l{6*math.cos(a-0.6):.1f} {6*math.sin(a-0.6):.1f}" stroke="{OL}" stroke-width="3" fill="none"/>'), (ex, ey)


def bubble(x, y, p):
    if p <= 0 or p >= 1:
        return ""
    sc = min(1, p * 5) * (1 + 0.15 * math.sin(min(1, p * 5) * math.pi))
    op = 1 if p < 0.85 else (1 - p) / 0.15
    puffs = [(-70, 0, 46), (-30, -26, 52), (24, -28, 54), (70, -4, 46), (40, 26, 42), (-20, 28, 44)]
    o = [f'<g transform="translate({x} {y}) scale({sc:.2f})" opacity="{op:.2f}">']
    o.append(f'<circle cx="-92" cy="78" r="12" fill="#fff" stroke="{OL}" stroke-width="4"/><circle cx="-110" cy="108" r="7" fill="#fff" stroke="{OL}" stroke-width="3.5"/>')
    o.append(f'<g stroke="{OL}" stroke-width="10">' + "".join(f'<circle cx="{a}" cy="{b}" r="{r}" fill="#fff"/>' for a, b, r in puffs) + '</g>')
    o.append("".join(f'<circle cx="{a}" cy="{b}" r="{r}" fill="#fff"/>' for a, b, r in puffs))
    o.append(wishbone_small(-58, 8, 0, 0.85))
    o.append(f'<path d="M-24 0 h34 m-12 -12 l12 12 l-12 12" stroke="{OL}" stroke-width="7" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    o.append(pie_slice(62, 6, 0, 0.62))
    o.append('</g>')
    return "".join(o)


def equal_badge(x, y, p):
    if p <= 0 or p >= 1:
        return ""
    sc = min(1, p * 6) * (1 + 0.25 * math.sin(min(1, p * 6) * math.pi))
    op = 1 if p < 0.8 else (1 - p) / 0.2
    return (f'<g transform="translate({x} {y}) scale({sc:.2f})" opacity="{op:.2f}">'
            f'<circle r="62" fill="#ffffff" stroke="{OL}" stroke-width="8"/>'
            f'<rect x="-34" y="-26" width="68" height="18" rx="9" fill="#2fb84a" stroke="{OL}" stroke-width="5"/>'
            f'<rect x="-34" y="8" width="68" height="18" rx="9" fill="#2fb84a" stroke="{OL}" stroke-width="5"/></g>')


def fork(x, y, ang, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s:.3f})">'
            f'<rect x="-6" y="-9" width="86" height="18" rx="9" fill="#cfd6de" stroke="{OL}" stroke-width="5"/>'
            f'<path d="M80 -14 Q 96 -16 100 -14 L134 -14 M80 14 Q 96 16 100 14 L134 14 M96 -5 L134 -5 M96 5 L134 5" stroke="{OL}" stroke-width="10" stroke-linecap="round" fill="none"/>'
            f'<path d="M80 -14 Q 96 -16 100 -14 L134 -14 M80 14 Q 96 16 100 14 L134 14 M96 -5 L134 -5 M96 5 L134 5" stroke="#e8edf2" stroke-width="4.5" stroke-linecap="round" fill="none"/>'
            f'<path d="M78 -16 Q 98 -20 100 0 Q 98 20 78 16Z" fill="#e8edf2" stroke="{OL}" stroke-width="4.5"/>'
            '<rect x="4" y="-4" width="60" height="5" rx="2.5" fill="#ffffff" opacity="0.7"/></g>')


def crumbs(x, y, t, t0, n=6, seed=1):
    if not (t0 <= t < t0 + 0.7):
        return ""
    k = t - t0
    rnd = random.Random(seed)
    o = []
    for i in range(n):
        vx = rnd.uniform(-160, 160)
        vy = rnd.uniform(-260, -80)
        cx = x + vx * k
        cy = y + vy * k + 900 * k * k
        o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rnd.uniform(4,8):.1f}" fill="{rnd.choice(["#d98a3a", "#f29a3c", "#d9a05a"])}" stroke="{OL}" stroke-width="2" opacity="{1-k/0.7:.2f}"/>')
    return "".join(o)


# ---------------------------------------------------------------- camera
CK = [(0.0, (548, 1440, 2.05)), (0.9, (548, 1440, 2.05)), (1.35, (548, 1250, 1.6)), (P2A, (548, 1250, 1.6)),
      (P2B - 0.4, (548, 1236, 1.42)), (T_YANK, (548, 1236, 1.42)), (T_YANK + 0.4, (548, 1500, 2.3)), (T_SNAP, (548, 1500, 2.3)),
      (T_SNAP + 0.22, (548, 1268, 1.36)), (13.2, (548, 1268, 1.36)), (14.3, (548, 1300, 1.55)), (DUR, (548, 1310, 1.62))]
SHAKES = [(T_CLASH, 7, 0.22), (T_BOING, 5, 0.2), (T_YANK, 7, 0.3), (T_SNAP, 30, 0.45), (T_HIDE, 16, 0.35), (T_CLINK, 4, 0.2)]


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
DEFS_EP = ('<linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4a3c8a"/>'
           '<stop offset="0.55" stop-color="#b8608a"/><stop offset="1" stop-color="#ffab5e"/></linearGradient>'
           '<radialGradient id="warm" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffd27a" stop-opacity="0.35"/>'
           '<stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>')


def frame(t):
    ctx = Ctx()
    g = grumpo_state(t)
    n = nibbo_state(t)
    L = [room(t)]
    L.append(f'<ellipse cx="548" cy="1480" rx="620" ry="400" fill="url(#warm)"/>')
    GI = mix_hex("#1a0a2e", "#3a0505", g["red"])
    GF = mix_hex("#9466e0", "#ff6a52", g["red"])
    NB, NS = "#ffd23c", "#3d2a12"

    # chairs (scoot with them, tip over after the snap)
    gc_rot = -95 * ein(seg(t, T_SNAP + 0.05, T_HIDE + 0.1))
    nc_rot = 95 * ein(seg(t, T_SNAP + 0.05, T_HIDE + 0.1))
    gcx = kf(min(t, T_SNAP), GXK)
    ncx = kf(min(t, T_SNAP), NXK)
    L.append(chair(gcx, gc_rot))
    L.append(chair(ncx, nc_rot))

    # characters (behind the table)
    L.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"], False, 0, None, 0, t))
    L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"], rot=n["rot"], sx=n["sx"], sy=n["sy"]))
    if n["ex"] == "nervous":
        L.append(sweat(n["x"] + 96, n["y"] - 86 + 30 * ((t * 1.6) % 1)))
    if g["red"] > 0.3 and t < T_SNAP:
        L.append(f'<path d="M{g["x"]-60:.0f} {g["y"]-118:.0f} l18 -8 l-6 18 M{g["x"]-42:.0f} {g["y"]-100:.0f} l18 -8 l-6 18" stroke="#e8303a" stroke-width="6" fill="none" stroke-linecap="round"/>')

    # table + things on it
    L.append(table_front())
    L.append(gravy(170, 1712))
    L.append(candle(60, 1606, t, 0.0) + candle(1036, 1606, t, 1.7))
    L.append(corn(930, 1716, -8) + cranberry(800, 1730))
    L.append(turkey(t))
    L.append(pumpkin(706, 1628, 0.85))
    # pie plate + pie
    rattle = 0.0
    if P2B - 0.4 <= t < 6.6 or T_YANK <= t < T_SNAP:
        rattle = 3 * math.sin(t * 70)
    for t0, a in [(T_TW1 + 0.15, 6), (T_TW2 + 0.15, 8)]:
        if t0 <= t < t0 + 0.4:
            rattle += a * (1 - (t - t0) / 0.4) * math.sin(t * 80)
    if T_CLASH <= t < T_CLASH + 0.3:
        rattle += 5 * (1 - (t - T_CLASH) / 0.3) * math.sin(t * 90)
    L.append(plate(PIE[0], PIE[1] + 16, rattle))
    if t < T_SNAP:
        L.append(pie_slice(PIE[0], PIE[1] - 6 - abs(rattle) * 1.4, rattle * 0.8, 1.0))
    else:
        L.append(f'<g opacity="0.85"><circle cx="{PIE[0]-14}" cy="{PIE[1]+12}" r="5" fill="#d98a3a"/><circle cx="{PIE[0]+20}" cy="{PIE[1]+14}" r="4" fill="#f29a3c"/><circle cx="{PIE[0]+4}" cy="{PIE[1]+10}" r="3" fill="#d9a05a"/></g>')

    # ---- forks (opening clash)
    if t < 1.32:
        e_in = eout(seg(t, 0.0, T_CLASH))
        e_out = eio(seg(t, 0.95, 1.3))
        jit = 5 * math.sin(t * 60) if T_CLASH <= t < 0.95 else 0
        ghx = lerp(lerp(g["x"] + 130, 420, e_in), g["x"] + 120, e_out) + jit
        ghy = lerp(lerp(1500, 1562, e_in), 1470, e_out)
        nhx = lerp(lerp(n["x"] - 120, 678, e_in), n["x"] - 112, e_out) - jit
        nhy = lerp(lerp(1500, 1562, e_in), 1470, e_out)
        op = 1 - seg(t, 1.15, 1.32)
        L.append(f'<g opacity="{op:.2f}">')
        L.append(fork(ghx, ghy, lerp(4, -30, e_out), 0.95))
        L.append(fork(nhx, nhy, lerp(176, 210, e_out), 0.95))
        L.append(arm(g["x"] + 100, g["y"] + 10, ghx, ghy, GI, 12, 16) + hand(ghx, ghy, GF, OL, 15))
        L.append(arm(n["x"] - 92, n["y"] + 8, nhx, nhy, NS, 10, 16) + hand(nhx, nhy, NB, NS, 12))
        L.append('</g>')
        if T_CLASH <= t < 0.95:
            for k in range(3):
                p = ((t - T_CLASH) * 3 + k / 3) % 1
                a = k * 2.1 + t * 4
                L.append(f'<circle cx="{548 + 60*p*math.cos(a):.1f}" cy="{1580 - 60*p*abs(math.sin(a)) - 20*p:.1f}" r="{6*(1-p)+2:.1f}" fill="#fff6a8" stroke="#ffb020" stroke-width="2"/>')

    # ---- wishbone
    jp = None
    if 1.55 <= t < T_GRAB:
        # Grumpo reaches into the carcass, plucks, raises it
        if t < T_PLUCK:
            e = eio(seg(t, 1.55, 1.85))
            hx, hy = lerp(g["x"] + 88, WB_REST[0] - 18, e), lerp(g["y"] - 30, WB_REST[1] - 22, e)
            L.append(arm(g["x"] + 88, g["y"] - 30, hx, hy, GI, 12, 20) + hand(hx, hy, GF, OL, 15))
        else:
            e = eout(seg(t, T_PLUCK, 2.25))
            e2 = eio(seg(t, 2.45, T_GRAB))
            hx = lerp(lerp(WB_REST[0] - 18, 452, e), 492, e2)
            hy = lerp(lerp(WB_REST[1] - 22, 1380, e), BAND_Y, e2)
            wig = 10 * math.sin(t * 9) * (1 - e2)
            L.append(arm(g["x"] + 88, g["y"] - 30, hx, hy, GI, 12, 22))
            L.append(wishbone_small(hx + 22, hy + 24, wig - 5, 1.6))
            L.append(hand(hx, hy, GF, OL, 15))
            # Nibbo reaches for the free prong
            if t >= 2.45:
                e3 = eio(seg(t, 2.45, T_GRAB))
                nx_, ny_ = lerp(n["x"] - 70, 604, e3), lerp(n["y"] - 50, BAND_Y, e3)
                L.append(arm(n["x"] - 70, n["y"] - 50, nx_, ny_, NS, 10, 20) + hand(nx_, ny_, NB, NS, 12))
    elif T_GRAB <= t < T_SNAP:
        A, B = wb_ends(t, g, n)
        bsvg, jp = wishbone_full(t, A, B)
        L.append(arm(g["x"] + 88, g["y"] - 30, A[0], A[1], GI, 12, 14))
        L.append(arm(n["x"] - 70, n["y"] - 50, B[0], B[1], NS, 10, 14))
        L.append(bsvg)
        L.append(hand(A[0], A[1], GF, OL, 16) + hand(B[0], B[1], NB, NS, 13))
        # pluck arms
        if 6.55 <= t < T_TW1 + 0.25:
            e = eio(seg(t, 6.55, 6.72)) * (1 - eio(seg(t, T_TW1, T_TW1 + 0.25)))
            px, py = 440, BAND_Y + 6 + 34 * eio(seg(t, 6.7, 6.9)) * (t < T_TW1)
            sx0, sy0 = g["x"] + 96, g["y"] + 14
            hx, hy = lerp(sx0, px, e), lerp(sy0, py if t < T_TW1 else py - 30, e)
            L.append(arm(sx0, sy0, hx, hy, GI, 12, 10) + hand(hx, hy, GF, OL, 14))
        if 7.7 <= t < T_TW2 + 0.25:
            e = eio(seg(t, 7.7, 7.87)) * (1 - eio(seg(t, T_TW2, T_TW2 + 0.25)))
            px, py = 660, BAND_Y + 6 + 46 * eio(seg(t, 7.85, 8.0)) * (t < T_TW2)
            sx0, sy0 = n["x"] - 92, n["y"] + 4
            hx, hy = lerp(sx0, px, e), lerp(sy0, py if t < T_TW2 else py - 30, e)
            L.append(arm(sx0, sy0, hx, hy, NS, 10, 10) + hand(hx, hy, NB, NS, 12))
    elif T_SNAP <= t < T_HIDE:
        k = seg(t, T_SNAP, T_HIDE)
        rec = eout(seg(t, T_SNAP, T_SNAP + 0.12))
        hx, hy = g["x"] + 70, g["y"] - 40
        L.append(half_bone(hx, hy, -20 - 150 * k, lerp(190, 78, rec), 8)[0] + hand(hx, hy, GF, OL, 15))
        hx, hy = n["x"] - 70, n["y"] - 40
        L.append(half_bone(hx, hy, 200 + 150 * k, lerp(190, 78, rec), 8)[0] + hand(hx, hy, NB, NS, 12))
    elif t >= 13.2:
        e = eout(seg(t, 13.2, 13.5))
        e2 = eio(seg(t, 13.9, T_CLINK))
        bump = 6 * math.sin(math.pi * seg(t, T_CLINK, T_CLINK + 0.15)) if t >= T_CLINK else 0
        ghx = lerp(lerp(g["x"] + 70, g["x"] + 112, e), 496, e2) - bump
        ghy = lerp(lerp(g["y"] + 10, g["y"] - 84, e), 1352, e2)
        nhx = lerp(lerp(n["x"] - 70, n["x"] - 112, e), 600, e2) + bump
        nhy = lerp(lerp(n["y"] + 10, n["y"] - 88, e), 1352, e2)
        L.append(arm(g["x"] + 88, g["y"] - 20, ghx, ghy, GI, 12, 10))
        L.append(arm(n["x"] - 70, n["y"] - 40, nhx, nhy, NS, 10, 10))
        L.append(half_bone(ghx, ghy, -55, 76, 11)[0] + hand(ghx, ghy, GF, OL, 15))
        L.append(half_bone(nhx, nhy, -125, 76, 11)[0] + hand(nhx, nhy, NB, NS, 12))

    # ---- flying pie
    if T_SNAP <= t < T_SPLIT:
        p = seg(t, T_SNAP, T_SPLIT - 0.05)
        y = lerp(PIE[1] - 6, 1140, eout(p))
        L.append(pie_slice(PIE[0], y, 720 * eout(p), 1.0 + 0.15 * p))
    if T_SPLIT <= t < T_EAT + 0.12:
        p = seg(t, T_SPLIT, T_EAT)
        targets = [((g["x"], GY0 + 82), -1), ((n["x"], NY0 + 34), 1)]
        for (tx, ty), side in targets:
            x0, y0 = PIE[0] + 26 * side, 1140
            x = lerp(x0, tx, p)
            y = y0 + (ty - y0) * p * p - 120 * p * (1 - p) * 2
            s = 1.15 if t < T_EAT else 1.15 * (1 - seg(t, T_EAT, T_EAT + 0.12))
            L.append(half_slice(x, y, side * 200 * p, s, side))
        L.append(crumbs(PIE[0], 1140, t, T_SPLIT, 8, 3))

    # ---- effects
    L.append(crumbs(g["x"], GY0 + 70, t, T_EAT + 0.1, 5, 5))
    L.append(crumbs(n["x"], NY0 + 30, t, T_EAT + 0.1, 5, 6))
    L.append(crumbs(g["x"], GY0 + 70, t, T_EAT + 0.55, 3, 8))
    L.append(crumbs(n["x"], NY0 + 30, t, T_EAT + 0.6, 3, 9))
    L.append(impact(548, 1580, seg(t, T_CLASH, T_CLASH + 0.22), "#ffffff"))
    L.append(symbol(g["x"] + 30, GY0 - 176, "!", seg(t, 1.35, 1.95)))
    L.append(bubble(420, 1200, seg(t, 2.05, 3.05)))
    L.append(star_twinkle(n["x"] + 60, NY0 - 170, seg(t, 2.35, 2.85)))
    L.append(symbol(g["x"] + 10, GY0 - 176, "?", seg(t, 3.65, 4.3), "#3a7ad6"))
    L.append(symbol(n["x"] - 10, NY0 - 166, "?", seg(t, 3.75, 4.35), "#3a7ad6"))
    L.append(symbol(n["x"] + 10, NY0 - 166, "!", seg(t, T_YANK + 0.05, T_YANK + 0.6)))
    L.append(symbol(g["x"] + 10, GY0 - 176, "!", seg(t, T_TW2 - 0.15, T_TW2 + 0.4)))
    if T_TW1 + 0.3 <= t < 7.7:
        L.append(f'<path d="M{n["x"]+130:.0f} {n["y"]-40:.0f} q10 10 0 20 q-10 10 0 20 M{n["x"]+150:.0f} {n["y"]-50:.0f} q10 12 0 24 q-10 12 0 24" stroke="#ffffff" stroke-width="6" fill="none" stroke-linecap="round" opacity="{1-seg(t, 7.3, 7.7):.2f}"/>')
    if T_TW2 + 0.32 <= t < 9.1:
        L.append(f'<path d="M{g["x"]-150:.0f} {g["y"]-40:.0f} q-10 10 0 20 q10 10 0 20 M{g["x"]-170:.0f} {g["y"]-50:.0f} q-10 12 0 24 q10 12 0 24" stroke="#ffffff" stroke-width="6" fill="none" stroke-linecap="round" opacity="{1-seg(t, 8.7, 9.1):.2f}"/>')
    if jp is not None and T_TW1 - 0.02 <= t < T_TW1 + 0.15:
        L.append(impact(440, BAND_Y, seg(t, T_TW1 - 0.02, T_TW1 + 0.15), "#fff6a8"))
    if jp is not None and T_TW2 - 0.02 <= t < T_TW2 + 0.15:
        L.append(impact(660, BAND_Y, seg(t, T_TW2 - 0.02, T_TW2 + 0.15), "#fff6a8"))
    if T_SNAP <= t < T_SNAP + 0.35:
        k = seg(t, T_SNAP, T_SNAP + 0.35)
        L.append(impact(548, 1520, k, "#ffffff"))
        L.append(f'<circle cx="548" cy="1520" r="{60 + 500*k:.0f}" fill="none" stroke="#ffffff" stroke-width="{14*(1-k):.1f}" opacity="{1-k:.2f}"/>')
        L.append(speed_lines(380, 1470, 200, 1 - k) + speed_lines(716, 1470, -20, 1 - k))
    if T_HIDE <= t < T_HIDE + 0.6:
        p = seg(t, T_HIDE, T_HIDE + 0.6)
        for cx0 in (150, 945):
            for k in range(4):
                cx = cx0 + (k - 1.5) * (50 + 60 * p)
                L.append(f'<circle cx="{cx:.0f}" cy="{TB - 20 - 70*p:.0f}" r="{30 + 30*p:.0f}" fill="#f6efe4" stroke="#c9b8a0" stroke-width="4" opacity="{0.9*(1-p):.2f}"/>')
    L.append(equal_badge(548, 1215, seg(t, 13.5, 14.3)))
    L.append(star_twinkle(548, 1286, seg(t, T_CLINK, T_CLINK + 0.45)))
    L.append(symbol(548, 1150, "♥", seg(t, T_CLINK + 0.2, DUR + 0.1), "#ff4d7a"))
    if T_CLINK + 0.2 <= t:
        L.append(star_twinkle(g["x"] - 40, GY0 - 160, ((t - T_CLINK) * 1.3) % 1))
        L.append(star_twinkle(n["x"] + 50, NY0 - 150, ((t - T_CLINK) * 1.3 + 0.5) % 1))

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    flash = ""
    if T_SNAP <= t < T_SNAP + 0.12:
        flash = f'<rect width="{W}" height="{H}" fill="#ffffff" opacity="{0.7*(1-seg(t, T_SNAP, T_SNAP+0.12)):.2f}"/>'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{DEFS_EP}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g>{flash}</svg>')
    return overlay(svg, hook_title(t + 0.12, "Winner gets", "THE LAST SLICE"))


def build_sfx():
    # fork clash
    sfx(0.0, "whoosh", 0.5, 1.5)
    sfx(T_CLASH, "clank", 1.0, 1.4)
    sfx(T_CLASH + 0.02, "clank", 0.6, 1.9)
    for k in range(4):
        sfx(0.45 + k * 0.12, "tap", 0.35, 1.6 + 0.1 * (k % 2))
    sfx(0.5, "grumble", 0.55, 1.0)
    sfx(1.0, "whoosh", 0.35, 1.2)
    # wishbone idea + pluck
    sfx(1.38, "ding", 0.45, 1.3)
    sfx(1.6, "squish", 0.4, 1.3)
    sfx(T_PLUCK, "cork_pop", 0.8, 1.2)
    sfx(2.05, "pop", 0.5, 1.4)
    sfx(2.4, "hop", 0.5, 1.4)
    sfx(2.6, "hop", 0.4, 1.5)
    sfx(T_GRAB, "click", 0.5, 1.0)
    # pull 1: rubbery bend
    sfx(3.0, "strain", 0.5, 1.2)
    sfx(3.05, "stretch", 0.6, 1.5)
    sfx(T_BOING, "boing", 0.9, 1.0)
    sfx(T_BOING + 0.05, "wobble", 0.5, 1.4)
    sfx(3.7, "squeak", 0.4, 1.0)
    sfx(3.8, "squeak", 0.35, 1.3)
    # pull 2: big stretch
    sfx(4.3, "inhale", 0.4, 1.2)
    sfx(P2A, "stretch", 0.8, 1.0)
    sfx(P2A + 0.7, "stretch", 0.7, 0.85)
    sfx(P2A + 0.2, "drag", 0.6, 1.0)
    sfx(P2A + 0.9, "drag", 0.5, 0.9)
    sfx(P2A + 0.3, "strain", 0.7, 1.0)
    sfx(P2B - 0.1, "creak", 0.5, 1.4)
    sfx(6.0, "rumble", 0.25, 1.6)
    # twang war
    sfx(6.6, "sneak", 0.4, 1.3)
    sfx(6.75, "stretch", 0.4, 1.8)
    sfx(T_TW1, "twang", 1.0, 1.0)
    sfx(T_TW1 + 0.3, "wobble", 0.8, 1.6)
    sfx(T_TW1 + 0.35, "boing", 0.5, 1.7)
    sfx(7.3, "laugh", 0.45, 0.9)
    sfx(7.8, "stretch", 0.45, 1.6)
    sfx(T_TW2, "twang", 1.0, 0.75)
    sfx(T_TW2 + 0.32, "wobble", 0.9, 1.0)
    sfx(T_TW2 + 0.36, "boing", 0.6, 1.1)
    sfx(8.55, "laugh", 0.55, 1.4)
    sfx(9.0, "grumble", 0.7, 0.85)
    # final yank
    sfx(9.3, "inhale", 0.7, 1.0)
    sfx(9.35, "inhale", 0.5, 1.4)
    sfx(T_YANK, "zip", 0.6, 0.8)
    sfx(T_YANK, "stretch", 0.9, 0.8)
    sfx(T_YANK + 0.05, "strain", 0.8, 1.1)
    sfx(T_YANK + 0.3, "suspense", 0.7, 1.0)
    sfx(10.15, "creak", 0.8, 1.6)
    sfx(10.45, "creak", 0.9, 1.9)
    sfx(10.62, "stretch", 0.6, 2.0)
    # SNAP
    sfx(T_SNAP, "snap", 1.0, 1.0)
    sfx(T_SNAP, "thud", 0.6, 1.3)
    sfx(T_SNAP + 0.02, "twang", 0.6, 1.4)
    sfx(T_SNAP + 0.05, "whoosh", 0.8, 0.8)
    sfx(T_SNAP + 0.08, "whoosh", 0.7, 1.1)
    sfx(T_SNAP + 0.1, "gasp", 0.4, 1.1)
    sfx(T_SNAP + 0.12, "rise", 0.5, 1.2)
    sfx(T_HIDE, "thud", 1.0, 0.8)
    sfx(T_HIDE + 0.04, "clatter", 0.8, 0.8)
    sfx(T_HIDE + 0.1, "thud", 0.7, 1.1)
    sfx(T_SPLIT, "pop", 0.7, 1.1)
    sfx(T_SPLIT + 0.05, "slide_down", 0.4, 1.6)
    sfx(T_POP, "boing", 0.6, 1.4)
    sfx(T_POP + 0.06, "boing", 0.5, 1.8)
    sfx(T_EAT, "gulp", 0.9, 0.9)
    sfx(T_EAT + 0.03, "gulp", 0.8, 1.35)
    for k in range(4):
        sfx(T_EAT + 0.2 + k * 0.24, "munch", 0.6, 0.95 + 0.1 * (k % 2))
    sfx(13.25, "click", 0.4, 1.4)
    sfx(13.55, "ding", 0.5, 1.0)
    sfx(13.95, "hop", 0.5, 1.3)
    sfx(13.97, "hop", 0.45, 1.6)
    sfx(T_CLINK, "ding", 0.9, 1.5)
    sfx(T_CLINK + 0.08, "ding", 0.6, 2.0)
    sfx(T_CLINK + 0.25, "cheer", 0.45, 1.1)
    sfx(T_CLINK + 0.3, "laugh", 0.4, 1.2)
