"""Grumpo & Nibbo — Episode 7: Snooze (bedroom at sunrise, reverse role + SNOOZE counter, 60 fps).

Grumpo wants to sleep in. Morning-person Nibbo wants him UP and escalates the wake-up gear:
a little bell clock (slapped flat), a giant bell clock (slapped — the bells pop off),
a rubber chicken (stuffed under the pillow, muffled squawks), an air horn (Grumpo, still
asleep, turns it around — Nibbo honks himself), and finally a GONG. As Nibbo winds up the
mallet, Grumpo's sleepy hand pats around for the snooze button ... and presses Nibbo's head.
Nibbo snoozes instantly, tips over and bonks the gong with a soft 'dong'. Grumpo smiles,
peeks with one eye, and sleeps on. Grumpo wins. Counter: SNOOZE 1..5.
"""
import math, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow
from hook import overlay, hook_title, counter

W, H, FPS, DUR = 1080, 1920, 60, 18.0
FLOOR = 1700
GS = 0.92
NR = 112
NG = FLOOR - NR
NBED = 1384             # Nibbo standing on the mattress
MAT = 1452                 # mattress top
BLANKET_TOP = 1492
G0 = (372, 1392)           # Grumpo head on pillow
HP = (486, 1322)           # where Nibbo holds the gadgets
NX0 = 650

# times
T_SLAP1 = 1.55
T_POP2, T_RING2, T_SLAP2 = 2.45, 2.85, 4.25
T_POP3, T_SQ1, T_SQ2, T_GRAB3, T_UNDER = 5.2, 5.6, 6.0, 6.5, 6.9
T_POP4, T_TURN0, T_TURN1, T_HONK = 8.0, 8.65, 9.15, 9.45
T_EXIT, T_BACK0, T_BACK1 = 10.55, 11.0, 11.9
T_MALLET, T_WIND1 = 12.05, 12.9
T_PRESS = 13.1
T_TIP0, T_TIP1 = 14.0, 14.7
T_PEEK0, T_PEEK1 = 16.3, 17.2

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


def arc(t, t0, t1, p0, p1, h):
    p = seg(t, t0, t1)
    return lerp(p0[0], p1[0], p), lerp(p0[1], p1[1], p) - h * 4 * p * (1 - p)


def arm(x0, y0, x1, y1, col, w=10, sag=30):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    return f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


def hand(x, y, fill, stroke, r=13):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="5"/>'


def ringing(t):
    return (0.0 <= t < T_SLAP1) or (T_RING2 <= t < T_SLAP2)


def sound_arcs(x, y, t, d=1, big=1.0, op=1.0):
    o = []
    for k in range(3):
        p = (t * 3 + k / 3) % 1
        r = (30 + 70 * p) * big
        o.append(f'<path d="M{x + d*r*0.5:.0f} {y - r:.0f} A {r:.0f} {r:.0f} 0 0 {1 if d > 0 else 0} {x + d*r*0.5:.0f} {y + r:.0f}" '
                 f'fill="none" stroke="#ffffff" stroke-width="7" stroke-linecap="round" opacity="{op*(1-p):.2f}"/>')
    return "".join(o)


def zzz(x, y, t, ph=0.0, s=1.0):
    o = []
    for k in range(3):
        p = (t * 0.55 + ph + k / 3) % 1
        xx = x - 70 * p * s + 14 * math.sin(p * 9)
        yy = y - 120 * p * s
        sz = (26 + 30 * p) * s
        o.append(f'<text x="{xx:.0f}" y="{yy:.0f}" font-family="Fredoka" font-weight="700" font-size="{sz:.0f}" text-anchor="middle" '
                 f'fill="#ffffff" stroke="{OL}" stroke-width="6" paint-order="stroke" opacity="{min(1, (1-p)*2.2, p*6):.2f}">Z</text>')
    return "".join(o)


# ---------------------------------------------------------------- props
def bell_clock(x, y, s=1.0, rot=0.0, sy=1.0, t=0.0, ring=False, bells=True, face_col="#e8303a"):
    jit = 4 * math.sin(t * 140) if ring else 0
    o = [f'<g transform="translate({x+jit:.1f} {y:.1f}) rotate({rot + (3*math.sin(t*120) if ring else 0):.1f}) scale({s:.3f} {s*sy:.3f})">']
    o.append(f'<path d="M-30 34 l-14 22 M30 34 l14 22" stroke="{OL}" stroke-width="9" stroke-linecap="round"/>')
    if bells:
        hb = 6 * math.sin(t * 140) if ring else 0
        o.append(f'<path d="M-46 -40 a26 26 0 0 1 36 -24z" fill="#ffd23a" stroke="{OL}" stroke-width="5" stroke-linejoin="round" transform="rotate(-20 -28 -52)"/>'
                 f'<path d="M10 -64 a26 26 0 0 1 36 24z" fill="#ffd23a" stroke="{OL}" stroke-width="5" stroke-linejoin="round" transform="rotate(20 28 -52)"/>'
                 f'<path d="M0 -50 V-64 M{-8+hb:.1f} -66 L{8+hb:.1f} -66" stroke="{OL}" stroke-width="5" stroke-linecap="round"/>')
    o.append(f'<circle r="48" fill="{face_col}" stroke="{OL}" stroke-width="6"/><circle r="36" fill="#ffffff" stroke="{OL}" stroke-width="4"/>'
             f'<path d="M0 0 V-24 M0 0 L16 8" stroke="{OL}" stroke-width="5" stroke-linecap="round"/><circle r="4" fill="{OL}"/>'
             f'<ellipse cx="-18" cy="-22" rx="8" ry="4" fill="#ffffff" opacity="0.7" transform="rotate(-35 -18 -22)"/>'
             f'<rect x="-8" y="-60" width="16" height="10" rx="3" fill="#8a93a2" stroke="{OL}" stroke-width="4"/>')
    o.append('</g>')
    return "".join(o)


def loose_bell(x, y, rot):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale(2.1)"><path d="M-18 8 a20 20 0 0 1 36 0z" fill="#ffd23a" stroke="{OL}" stroke-width="3"/></g>')


def spring(x, y, h, rot=0):
    pts = " ".join(f"{(10 if k % 2 else -10):.0f},{-k*h/8:.1f}" for k in range(9))
    return f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})"><polyline points="{pts}" fill="none" stroke="#8a93a2" stroke-width="5" stroke-linejoin="round"/></g>'


def chicken(x, y, rot=0.0, sx=1.0, sy=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx:.3f} {sy:.3f})">'
            f'<path d="M-62 6 Q -40 -26 10 -14 Q 40 -10 48 -40 Q 54 -60 70 -58 Q 84 -54 80 -38 Q 76 -14 60 4 Q 30 34 -30 28 Q -70 26 -62 6Z" fill="#ffe14a" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M66 -60 q4 -14 12 -6 q6 -12 12 0 q8 -4 4 8" fill="#e8303a" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M80 -44 l22 4 l-20 8z" fill="#ff9a2a" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>'
            f'<circle cx="70" cy="-46" r="4" fill="{OL}"/>'
            f'<path d="M-20 28 l-6 24 M0 28 l4 24" stroke="#ff9a2a" stroke-width="6" stroke-linecap="round"/>'
            f'<path d="M-40 4 q14 -10 30 0" stroke="#e8b81a" stroke-width="5" fill="none"/></g>')


def air_horn(x, y, rot=0.0, s=1.0, press=0.0):
    """bell points to -x (left) at rot=0."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            f'<rect x="10" y="-26" width="64" height="52" rx="12" fill="#f4f7fa" stroke="{OL}" stroke-width="5"/>'
            f'<rect x="10" y="-10" width="64" height="18" fill="#e8303a"/>'
            f'<rect x="34" y="{-40+8*press:.1f}" width="20" height="16" rx="4" fill="#3a3a48" stroke="{OL}" stroke-width="4"/>'
            f'<path d="M10 -10 L-20 -10 L-62 -36 L-62 36 L-20 10 L10 10Z" fill="#e8303a" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<ellipse cx="-62" cy="0" rx="8" ry="36" fill="#a8141e" stroke="{OL}" stroke-width="4"/>'
            '<path d="M-14 -4 L-48 -22" stroke="#ff8a90" stroke-width="5" stroke-linecap="round"/></g>')


GONG_Y = 1470


def gong(x, t, wob=0.0):
    o = [f'<g transform="translate({x:.1f} 0)">',
         f'<path d="M-118 {FLOOR-30} V1290 M118 {FLOOR-30} V1290" stroke="{OL}" stroke-width="24" stroke-linecap="round"/>',
         f'<path d="M-118 {FLOOR-30} V1290 M118 {FLOOR-30} V1290" stroke="#b5642a" stroke-width="13" stroke-linecap="round"/>',
         f'<path d="M-140 1290 H140" stroke="{OL}" stroke-width="26" stroke-linecap="round"/><path d="M-140 1290 H140" stroke="#c9763a" stroke-width="15" stroke-linecap="round"/>',
         f'<path d="M-150 {FLOOR-30} H150" stroke="{OL}" stroke-width="22" stroke-linecap="round"/><path d="M-150 {FLOOR-30} H150" stroke="#b5642a" stroke-width="12" stroke-linecap="round"/>',
         f'<circle cx="-120" cy="{FLOOR-14}" r="14" fill="#3a3a48" stroke="{OL}" stroke-width="4"/><circle cx="120" cy="{FLOOR-14}" r="14" fill="#3a3a48" stroke="{OL}" stroke-width="4"/>',
         f'<path d="M-40 1290 L-30 {GONG_Y-92} M40 1290 L30 {GONG_Y-92}" stroke="{OL}" stroke-width="4"/>',
         f'<g transform="translate(0 {GONG_Y}) rotate({wob:.2f})">'
         f'<circle r="98" fill="#e8a81a" stroke="{OL}" stroke-width="7"/><circle r="74" fill="none" stroke="#c8861a" stroke-width="6"/>'
         f'<circle r="30" fill="#f6c84a" stroke="#c8861a" stroke-width="5"/>'
         f'<ellipse cx="-40" cy="-50" rx="22" ry="9" fill="#fff6c8" opacity="0.7" transform="rotate(-40 -40 -50)"/></g>',
         '</g>']
    return "".join(o)


def mallet(x, y, rot):
    """handle end at (x,y), head along -y at rot=0."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">'
            f'<path d="M0 10 V-130" stroke="{OL}" stroke-width="16" stroke-linecap="round"/><path d="M0 10 V-130" stroke="#c9763a" stroke-width="8" stroke-linecap="round"/>'
            f'<ellipse cx="0" cy="-150" rx="34" ry="28" fill="#ff6fa8" stroke="{OL}" stroke-width="5"/>'
            '<ellipse cx="-10" cy="-160" rx="10" ry="6" fill="#ffffff" opacity="0.5"/></g>')


# ---------------------------------------------------------------- room
def room(t, shake):
    o = []
    dawn = seg(t, 0, DUR)
    wall = mix_hex("#8a8fd0", "#b9b6e6", dawn)
    o.append(f'<rect x="-900" y="-900" width="3200" height="{FLOOR+900}" fill="{wall}"/>')
    for x in range(-900, 2300, 130):
        o.append(f'<rect x="{x}" y="-900" width="60" height="{FLOOR+900}" fill="{mix_hex("#8086c8", "#b0acdf", dawn)}"/>')
    # window with sunrise
    wx0, wy0, ww, wh = 560, 1040, 300, 290
    cid = "win"
    sky_top = mix_hex("#3a3f8a", "#7ab8ff", dawn)
    sky_bot = mix_hex("#ff9a6a", "#ffe0a0", dawn)
    o.append(f'<defs><linearGradient id="skyw" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{sky_top}"/><stop offset="1" stop-color="{sky_bot}"/></linearGradient>'
             f'<clipPath id="{cid}"><rect x="{wx0}" y="{wy0}" width="{ww}" height="{wh}"/></clipPath></defs>')
    o.append(f'<rect x="{wx0-14}" y="{wy0-14}" width="{ww+28}" height="{wh+28}" rx="10" fill="#f4f1fa" stroke="{OL}" stroke-width="7"/>')
    sun_y = lerp(wy0 + wh + 40, wy0 + 120, eio(dawn))
    o.append(f'<g clip-path="url(#{cid})"><rect x="{wx0}" y="{wy0}" width="{ww}" height="{wh}" fill="url(#skyw)"/>'
             f'<circle cx="{wx0+190}" cy="{sun_y:.1f}" r="90" fill="#fff3b0" opacity="0.5"/><circle cx="{wx0+190}" cy="{sun_y:.1f}" r="52" fill="#fff6c8"/>'
             f'<path d="M{wx0} {wy0+wh-50} Q {wx0+80} {wy0+wh-110} {wx0+160} {wy0+wh-60} T {wx0+ww} {wy0+wh-70} V{wy0+wh} H{wx0}Z" fill="{mix_hex("#3a4a7a", "#5a9a6a", dawn)}"/>'
             f'<path d="M{wx0+20} {wy0+wh} L{wx0+110} {wy0} L{wx0+150} {wy0} L{wx0+60} {wy0+wh}Z" fill="#ffffff" opacity="0.15"/></g>')
    o.append(f'<path d="M{wx0+ww/2} {wy0} V{wy0+wh} M{wx0} {wy0+wh/2} H{wx0+ww}" stroke="#f4f1fa" stroke-width="12"/>'
             f'<rect x="{wx0-14}" y="{wy0-14}" width="{ww+28}" height="{wh+28}" rx="10" fill="none" stroke="{OL}" stroke-width="7"/>')
    # curtains
    o.append(f'<path d="M{wx0-60} {wy0-40} Q {wx0-20} {wy0+150} {wx0-50} {wy0+wh+40} H{wx0+10} Q {wx0+30} {wy0+150} {wx0+20} {wy0-40}Z" fill="#ff8aa8" stroke="{OL}" stroke-width="5"/>'
             f'<path d="M{wx0+ww+60} {wy0-40} Q {wx0+ww+20} {wy0+150} {wx0+ww+50} {wy0+wh+40} H{wx0+ww-10} Q {wx0+ww-30} {wy0+150} {wx0+ww-20} {wy0-40}Z" fill="#ff8aa8" stroke="{OL}" stroke-width="5"/>'
             f'<rect x="{wx0-80}" y="{wy0-52}" width="{ww+160}" height="16" rx="8" fill="#b5642a" stroke="{OL}" stroke-width="4"/>')
    # picture frame above bed (rattles)
    pr = 4 * math.sin(t * 50) * shake
    o.append(f'<g transform="rotate({pr:.1f} 300 1120)"><path d="M300 1120 L250 1160 M300 1120 L350 1160" stroke="{OL}" stroke-width="3"/>'
             f'<rect x="230" y="1160" width="140" height="110" rx="6" fill="#ffd23a" stroke="{OL}" stroke-width="6"/>'
             f'<rect x="244" y="1174" width="112" height="82" fill="#8fd0ff"/><circle cx="330" cy="1200" r="12" fill="#fff3a0"/>'
             f'<path d="M244 1256 L284 1210 L314 1240 L334 1222 L356 1256Z" fill="#5cc46a"/></g>')
    # floor (wood planks) + rug
    o.append(f'<rect x="-900" y="{FLOOR}" width="3200" height="900" fill="#b5784a"/>')
    for k, y in enumerate(range(FLOOR + 40, FLOOR + 900, 70)):
        o.append(f'<path d="M-900 {y} H2300" stroke="#9a6238" stroke-width="5"/>')
    o.append(f'<line x1="-900" y1="{FLOOR}" x2="2300" y2="{FLOOR}" stroke="{OL}" stroke-width="6"/>'
             f'<rect x="-900" y="{FLOOR-20}" width="3200" height="20" fill="#e8e2f6" stroke="{OL}" stroke-width="4"/>')
    o.append(f'<ellipse cx="700" cy="{FLOOR+70}" rx="420" ry="44" fill="#6fc0c8" stroke="{OL}" stroke-width="5"/>'
             f'<ellipse cx="700" cy="{FLOOR+70}" rx="340" ry="30" fill="none" stroke="#ffffff" stroke-width="5" stroke-dasharray="18 14"/>')
    return "".join(o)


def bed_back(dy):
    return (f'<g transform="translate(0 {dy:.1f})">'
            f'<rect x="130" y="1150" width="70" height="{FLOOR-1150}" rx="18" fill="#c9763a" stroke="{OL}" stroke-width="7"/>'
            f'<circle cx="165" cy="1150" r="26" fill="#d98a4a" stroke="{OL}" stroke-width="6"/>'
            f'<path d="M150 1190 V1640" stroke="#e8a46a" stroke-width="9" stroke-linecap="round"/>'
            f'<rect x="190" y="{MAT}" width="1100" height="110" rx="14" fill="#f4f1fa" stroke="{OL}" stroke-width="6"/>'
            f'<rect x="190" y="{MAT+110}" width="1100" height="46" fill="#c9763a" stroke="{OL}" stroke-width="6"/>'
            f'<rect x="210" y="{MAT+156}" width="28" height="{FLOOR-MAT-156}" fill="#b5642a" stroke="{OL}" stroke-width="5"/>'
            f'<path d="M206 1360 Q 200 1330 240 1328 H420 Q 456 1330 452 1370 L448 {MAT+6} H210Z" fill="#ffffff" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<path d="M230 1350 h150" stroke="#e3e0ee" stroke-width="8" stroke-linecap="round"/>'
            '</g>')


def blanket(dy, t, flap=0.0):
    w = "".join(f" Q {x+40} {BLANKET_TOP + 10*math.sin(x/60 + t*flap*30) * flap - 8} {x+80} {BLANKET_TOP + 4*math.sin(x/50)}" for x in range(300, 1300, 80))
    return (f'<g transform="translate(0 {dy:.1f})">'
            f'<path d="M288 {BLANKET_TOP+10} Q 290 {BLANKET_TOP} 300 {BLANKET_TOP} {w} V{MAT+140} H300 Q 280 {MAT+120} 288 {BLANKET_TOP+10}Z" fill="#5a8ae8" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<path d="M300 {BLANKET_TOP+4} H1300" stroke="#ffffff" stroke-width="14" opacity="0.9"/>'
            + "".join(f'<circle cx="{x}" cy="{MAT+80 + (x//100 % 2)*30}" r="9" fill="#ffd23a" opacity="0.8"/>' for x in range(380, 1300, 100))
            + '</g>')


def sleep_lids(x, y, s, rot, sx, sy, red, open_right=0.0, content=False):
    base = mix_hex("#9466e0", "#ff6a52", red)
    ink = mix_hex("#1a0a2e", "#3a0505", red)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s*sx:.3f} {s*sy:.3f})">']
    for cx, side in ((-38, 0), (38, 1)):
        if side == 1 and open_right > 0:
            # half-open lid (top part covered)
            hh = 46 * (1 - open_right)
            o.append(f'<rect x="{cx-24}" y="-10" width="48" height="{hh:.1f}" fill="{base}"/>'
                     f'<path d="M{cx-20} {-10+hh:.1f} h40" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>')
            continue
        o.append(f'<ellipse cx="{cx}" cy="16" rx="24" ry="26" fill="{base}"/>')
        if content:
            o.append(f'<path d="M{cx-18} 20 q18 -14 36 0" fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>')
        else:
            o.append(f'<path d="M{cx-18} 16 q18 14 36 0" fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


# ---------------------------------------------------------------- states
def bed_shake(t):
    if T_RING2 <= t < T_SLAP2:
        return 1.0
    if 0 <= t < T_SLAP1:
        return 0.3
    return 0.0


def grumpo_state(t):
    sh = bed_shake(t)
    g = dict(x=G0[0], y=G0[1] + sh * 6 * math.sin(t * 60), ex="grumpy", red=0.0, look=(0, 0), sx=1.0, sy=1.0, rot=-6,
             content=False, peek=0.0)
    g["ex"] = pick(t, [(0, "grumpy"), (2.0, "smug"), (T_RING2, "grumpy"), (T_SLAP2 + 0.5, "smug"), (T_SQ1, "grumpy"),
                       (T_UNDER + 0.3, "smug"), (T_POP4 + 0.6, "grumpy"), (T_HONK + 0.2, "smug"), (T_WIND1 - 0.4, "grumpy"),
                       (T_PRESS + 0.3, "smug")], "grumpy")
    g["content"] = g["ex"] == "smug"
    if T_RING2 <= t < T_SLAP2:
        g["red"] = 0.25 * seg(t, T_RING2 + 0.4, T_SLAP2 - 0.3)
    for ts in (T_SLAP1, T_SLAP2):
        a, b = squash(t, ts, 0.25, 0.08)
        g["sx"], g["sy"] = g["sx"] * a, g["sy"] * b
    # breathing
    br = 0.025 * math.sin(t * 2.6)
    g["sx"] *= 1 + br
    g["sy"] *= 1 - br * 0.6
    if T_PEEK0 <= t < T_PEEK1:
        g["peek"] = math.sin(math.pi * seg(t, T_PEEK0, T_PEEK1)) ** 0.5
        g["look"] = (1, 0.6)
    return g


def grumpo_hand(t):
    """returns hand target or None (arm comes out from under the blanket)."""
    base = (470, 1500)
    def reach(t0, t1, t2, t3, tgt):
        if t0 <= t < t3:
            e = eio(seg(t, t0, t1)) * (1 - eio(seg(t, t2, t3)))
            return (lerp(base[0], tgt[0], e), lerp(base[1], tgt[1], e))
        return None
    for args in [(1.15, T_SLAP1, T_SLAP1 + 0.25, 1.9, (HP[0], HP[1] - 56)),
                 (3.85, T_SLAP2, T_SLAP2 + 0.25, 4.65, (HP[0] + 6, HP[1] - 112))]:
        r = reach(*args)
        if r:
            return r
    if T_GRAB3 - 0.3 <= t < T_UNDER + 0.3:
        if t < T_GRAB3:
            return reach(T_GRAB3 - 0.3, T_GRAB3, 99, 99, (HP[0] + 30, HP[1] - 40))
        p = eio(seg(t, T_GRAB3, T_UNDER))
        pos = (lerp(HP[0] + 30, 300, p), lerp(HP[1] - 40, 1400, p) - 60 * math.sin(math.pi * p))
        if t >= T_UNDER:
            e = eio(seg(t, T_UNDER, T_UNDER + 0.3))
            return (lerp(300, base[0], e), lerp(1400, base[1], e))
        return pos
    if T_TURN0 - 0.3 <= t < T_TURN1 + 0.3:
        if t < T_TURN0:
            return reach(T_TURN0 - 0.3, T_TURN0, 99, 99, (HP[0] + 40, HP[1] + 10))
        if t < T_TURN1:
            return (HP[0] + 40 - 20 * math.sin(math.pi * seg(t, T_TURN0, T_TURN1)), HP[1] + 10)
        e = eio(seg(t, T_TURN1, T_TURN1 + 0.3))
        return (lerp(HP[0] + 40, base[0], e), lerp(HP[1] + 10, base[1], e))
    if 12.2 <= t < T_PRESS + 0.6:
        # blind patting: blanket, blanket, air, then Nibbo's head
        pats = [(12.2, (520, 1470)), (12.45, (590, 1470)), (12.7, (560, 1420)), (12.9, (NX0 - 10, 1440)), (T_PRESS, (NX0, NG - NR + 4))]
        if t < T_PRESS + 0.25:
            prev = base
            for (tk, pk) in pats:
                if t < tk:
                    p = seg(t, tk - 0.22, tk)
                    return (lerp(prev[0], pk[0], eio(p)), lerp(prev[1], pk[1], eio(p)) - 30 * math.sin(math.pi * p))
                prev = pk
            return pats[-1][1]
        e = eio(seg(t, T_PRESS + 0.25, T_PRESS + 0.6))
        return (lerp(NX0, base[0], e), lerp(NG - NR + 4, base[1], e))
    return None


def nibbo_state(t):
    n = dict(x=NX0, y=NBED if t < T_EXIT else NG, ex="joy", rot=0.0, sx=1.0, sy=1.0, sleep=False, glasses=False)
    n["ex"] = pick(t, [(0, "joy"), (T_SLAP1, "uhoh"), (T_POP2 - 0.15, "happy"), (T_RING2, "joy"), (T_SLAP2, "wow"),
                       (T_POP3 - 0.1, "happy"), (T_SQ1, "joy"), (T_GRAB3, "uhoh"), (T_POP4 - 0.1, "happy"),
                       (T_TURN0, "joy"), (T_HONK, "dizzy"), (T_BACK0, "cool")], "joy")
    for tp in (T_POP2, T_POP3, T_POP4, T_MALLET):
        a, b = squash(t, tp, 0.3, 0.16)
        n["sx"], n["sy"] = n["sx"] * a, n["sy"] * b
    if T_SLAP1 <= t < T_SLAP1 + 0.5:
        n["rot"] = 10 * math.sin((t - T_SLAP1) * 30) * (1 - seg(t, T_SLAP1, T_SLAP1 + 0.5))
    if T_SLAP2 <= t < 5.0:
        k = seg(t, T_SLAP2, T_SLAP2 + 0.2)
        n["x"] = NX0 + 30 * eout(k) * (1 - seg(t, 4.6, 5.0))
        n["rot"] = 14 * (1 - seg(t, 4.6, 5.0))
    if T_HONK <= t < T_EXIT:
        k = t - T_HONK
        push = eout(seg(t, T_HONK, T_HONK + 0.3)) * (1 - eio(seg(t, 10.0, T_EXIT)))
        n["x"] = NX0 + 90 * push
        n["sx"] = 1 + 0.12 * math.sin(k * 60) * math.exp(-k * 2.5)
        n["sy"] = 1 - 0.1 * math.sin(k * 60 + 1) * math.exp(-k * 2.5)
        n["rot"] = 10 * push
    if T_EXIT <= t < T_BACK0:
        n["x"], n["y"] = arc(t, T_EXIT, T_BACK0, (NX0, NBED), (1150, NG), 160)
        n["ex"] = "happy"
    if T_BACK0 <= t < T_BACK1:
        p = seg(t, T_BACK0, T_BACK1)
        n["x"] = lerp(1150, NX0, eout(p))
        n["y"] = NG - abs(math.sin(p * math.pi * 3)) * 16
        n["rot"] = -10
        n["glasses"] = True
    if t >= T_BACK0:
        n["glasses"] = t < T_PRESS + 0.35
        n["ex"] = "cool" if n["glasses"] else n["ex"]
    if T_MALLET <= t < T_PRESS:
        k = eio(seg(t, T_MALLET + 0.1, T_WIND1))
        n["rot"] = -14 * k + 2 * math.sin(t * 30) * seg(t, T_WIND1, T_PRESS)
        n["sx"], n["sy"] = n["sx"] * (1 - 0.05 * k), n["sy"] * (1 + 0.06 * k)
    if t >= T_PRESS:
        a, b = squash(t, T_PRESS, 0.35, 0.35)
        n["sx"], n["sy"] = a, b
        n["rot"] = -14 * (1 - seg(t, T_PRESS, T_PRESS + 0.3))
        if t >= T_PRESS + 0.35:
            n["ex"] = "zz"
            n["sleep"] = True
        if t >= T_TIP0:
            p = eio(seg(t, T_TIP0, T_TIP1))
            n["rot"] = 22 * p
            n["x"] = NX0 + 14 * p
            if t >= T_TIP1:
                n["rot"] = 22 + 3 * math.exp(-(t - T_TIP1) * 6) * math.sin((t - T_TIP1) * 40)
    n["y"] += NR * (1 - n["sy"])
    return n


def held(t, n):
    """position of the hold point following Nibbo."""
    return HP[0] + (n["x"] - NX0), HP[1] + (n["y"] - (NBED if t < T_EXIT else NG))


# ---------------------------------------------------------------- camera
CK = [(0.0, (470, 1300, 1.5)), (T_RING2, (470, 1300, 1.5)), (T_RING2 + 0.4, (450, 1290, 1.62)), (T_SLAP2, (450, 1290, 1.62)),
      (T_SLAP2 + 0.5, (470, 1300, 1.5)), (T_SQ1, (470, 1300, 1.5)), (T_SQ1 + 0.3, (430, 1280, 1.7)), (T_UNDER + 0.6, (430, 1280, 1.7)),
      (T_POP4 + 0.3, (480, 1300, 1.52)), (T_HONK + 0.6, (500, 1300, 1.52)), (T_EXIT, (540, 1300, 1.48)), (T_BACK1, (580, 1300, 1.44)),
      (T_WIND1, (570, 1290, 1.48)), (T_PRESS, (570, 1300, 1.5)), (T_TIP1 + 0.4, (590, 1310, 1.42)), (T_PEEK0 - 0.4, (570, 1310, 1.45)),
      (T_PEEK0 + 0.3, (430, 1300, 1.85)), (T_PEEK1, (430, 1300, 1.85)), (DUR, (560, 1310, 1.45))]
SHAKES = [(T_SLAP1, 6, 0.2), (T_SLAP2, 12, 0.3), (T_HONK, 16, 0.5), (T_PRESS, 6, 0.2), (T_TIP1, 4, 0.3)]


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
    if T_RING2 <= t < T_SLAP2:
        amp = max(amp, 3)
    return cx + amp * math.sin(t * 93), cy + amp * math.cos(t * 79), z


def snooze_count(t):
    marks = [T_SLAP1, T_SLAP2, T_UNDER, T_HONK, T_PRESS]
    c = sum(1 for m in marks if t >= m)
    bt = max([m for m in marks if t >= m], default=None)
    return c, bt


# ---------------------------------------------------------------- frame
def frame(t):
    ctx = Ctx()
    sh = bed_shake(t)
    dy = sh * 5 * math.sin(t * 70)
    L = [room(t, sh)]
    g = grumpo_state(t)
    n = nibbo_state(t)
    ink = mix_hex("#1a0a2e", "#3a0505", g["red"])
    gfill = mix_hex("#9466e0", "#ff6a52", g["red"])
    NB, NS = "#ffd23c", "#3d2a12"

    # gong (behind nibbo)
    gx = None
    if t >= T_BACK0:
        p = seg(t, T_BACK0, T_BACK1)
        gx = lerp(1390, 868, eout(p))
        wob = 0.0
        if t >= T_TIP1:
            k = t - T_TIP1
            wob = 4 * math.exp(-k * 1.5) * math.sin(k * 14)
        L.append(shadow(gx, FLOOR + 4, 170))
        L.append(gong(gx, t, wob))
        if T_BACK0 <= t < T_MALLET:
            L.append(mallet(gx + 60, 1560, 25))
        if T_TIP1 <= t < T_TIP1 + 1.6:
            q = seg(t, T_TIP1, T_TIP1 + 1.6)
            for k in range(2):
                r = 110 + 160 * ((q + k * 0.5) % 1)
                L.append(f'<circle cx="{gx:.0f}" cy="{GONG_Y}" r="{r:.0f}" fill="none" stroke="#ffe08a" stroke-width="6" opacity="{0.6*(1-q):.2f}"/>')

    L.append(bed_back(dy))
    # chicken under pillow (behind grumpo)
    if t >= T_UNDER:
        bump = 0.0
        for tm in (7.2, 7.65):
            if tm <= t < tm + 0.3:
                bump = math.sin(math.pi * (t - tm) / 0.3)
        L.append(f'<g opacity="0.95">{chicken(262, 1420 - 8*bump, -10, 0.7, 0.7*(1-0.25*bump))}</g>')
        L.append(f'<path d="M206 1360 Q 200 {1330-14*bump:.0f} 240 {1328-14*bump:.0f} H330" fill="none" stroke="{OL}" stroke-width="6"/>')

    # grumpo
    L.append(grumpo(ctx, g["x"], g["y"] + dy, GS, g["ex"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"],
                    False, 0, None, 0, t))
    L.append(sleep_lids(g["x"], g["y"] + dy, GS, g["rot"], g["sx"], g["sy"], g["red"], g["peek"], g["content"]))
    L.append(blanket(dy, t, 1.0 if T_HONK <= t < T_HONK + 0.7 else 0.0))

    # grumpo arm
    hp = grumpo_hand(t)
    if hp:
        L.append(arm(450, 1500 + dy, hp[0], hp[1], ink, 13, -10 if hp[1] < 1450 else 10) + hand(hp[0], hp[1], gfill, OL, 16))

    # ---- nibbo + gadget
    hx, hy = held(t, n)
    item = ""
    two_hands = True
    if t < T_SLAP1 + 0.7:
        sy = 1.0 if t < T_SLAP1 else 0.38
        item = bell_clock(hx, hy + (30 if t >= T_SLAP1 else 0), 1.0, 0, sy, t, ringing(t))
    elif t < T_POP2:
        p = seg(t, T_SLAP1 + 0.7, T_POP2)
        x, y = arc(t, T_SLAP1 + 0.7, T_POP2, (hx, hy + 30), (1250, 1500), 200)
        item = bell_clock(x, y, 1.0, 400 * p, 0.38)
        two_hands = False
    elif t < T_SLAP2 + 0.8:
        k = eout(seg(t, T_POP2, T_POP2 + 0.3))
        big = 1.9
        cy = lerp(n["y"], hy - 60, k)
        flat = t >= T_SLAP2
        item = bell_clock(hx + 10, cy + (40 if flat else 0), big * k + 0.01, 0, 0.5 if flat else 1.0, t, ringing(t), bells=not flat, face_col="#3a8be0")
        if flat:
            q = t - T_SLAP2
            for k2, (vx, vy, vr) in enumerate([(-500, -900, -400), (520, -950, 380)]):
                bx = hx + 10 + (-52 if k2 == 0 else 52) + vx * q
                by = cy - 100 + vy * q + 0.5 * 3000 * q * q
                if by < FLOOR:
                    item += loose_bell(bx, by, vr * q)
            sp = min(1, q / 0.2)
            item += spring(hx - 10, cy - 40, 70 * sp, -20) + spring(hx + 30, cy - 40, 80 * sp, 15)
    elif t < T_POP3:
        x, y = arc(t, T_SLAP2 + 0.8, T_POP3, (hx + 10, hy - 20), (1300, 1550), 220)
        item = bell_clock(x, y, 1.9, 300 * seg(t, T_SLAP2 + 0.8, T_POP3), 0.5, bells=False, face_col="#3a8be0")
        two_hands = False
    elif t < T_GRAB3:
        k = eout(seg(t, T_POP3, T_POP3 + 0.3))
        sq = 0.0
        for ts in (T_SQ1, T_SQ2):
            if ts <= t < ts + 0.3:
                sq = math.sin(math.pi * (t - ts) / 0.3)
        item = chicken(hx - 10, lerp(n["y"], hy, k), -8, (1 + 0.3 * sq) * k + 0.01, (1 - 0.35 * sq) * k + 0.01)
        if sq > 0:
            item += sound_arcs(hx - 110, hy - 40, t, -1, 0.9, sq)
    elif t < T_UNDER:
        hp2 = grumpo_hand(t)
        item = chicken(hp2[0] - 20, hp2[1] + 10, -40 * seg(t, T_GRAB3, T_UNDER), 1 - 0.3 * seg(t, T_GRAB3, T_UNDER), 1 - 0.3 * seg(t, T_GRAB3, T_UNDER))
        two_hands = False
    elif t < T_POP4:
        two_hands = False
    elif t < T_HONK + 0.55:
        k = eout(seg(t, T_POP4, T_POP4 + 0.3))
        rot = 180 * eio(seg(t, T_TURN0, T_TURN1))
        press = 1.0 if T_HONK - 0.05 <= t < T_HONK + 0.5 else 0.0
        item = air_horn(hx, lerp(n["y"], hy + 10, k), rot, 1.2 * k + 0.01, press)
        if t >= T_HONK:
            q = seg(t, T_HONK, T_HONK + 0.55)
            for kk in range(5):
                yy = hy + 10 + (kk - 2) * 24
                x0 = hx + 70 + 120 * ((q * 2 + kk * 0.2) % 1)
                item += f'<path d="M{x0:.0f} {yy:.0f} h70" stroke="#ffffff" stroke-width="9" stroke-linecap="round" opacity="{0.9*(1-q):.2f}"/>'
    elif t < T_EXIT:
        x, y = arc(t, T_HONK + 0.55, T_EXIT, (hx - 40, hy + 10), (hx - 60, FLOOR - 30), 60)
        item = air_horn(x, y, 180 + 90 * seg(t, T_HONK + 0.55, T_EXIT), 1.2)
        two_hands = False
    else:
        two_hands = False
        if t < T_EXIT + 0.5:
            item = air_horn(NX0 - 100, FLOOR - 30, 270, 1.2)
    if T_EXIT + 0.5 <= t:
        pass
    # mallet in Nibbo's hands
    mal = ""
    if T_MALLET <= t < T_PRESS + 0.55:
        k = eio(seg(t, T_MALLET, T_WIND1))
        rot = lerp(30, -60, k) + (3 * math.sin(t * 40) if t > T_WIND1 else 0)
        mx, my = n["x"] - 10 - 40 * k, n["y"] - 130 - 30 * k
        mal = mallet(mx, my, rot)
    elif T_PRESS + 0.55 <= t:
        q = seg(t, T_PRESS + 0.55, T_PRESS + 0.9)
        mx = n["x"] - 50 - 60 * q
        my = lerp(n["y"] - 160, FLOOR - 16, ein(q))
        rot = lerp(-60, -100, q)
        mal = mallet(mx, my, rot) if q < 1 else mallet(n["x"] - 110, FLOOR - 16, -95)

    L.append(shadow(n["x"], (BLANKET_TOP + 6 if t < T_EXIT + 0.2 else FLOOR + 6), 105, 0.8))
    face = "happy" if n["ex"] == "zz" else n["ex"]
    L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"] if n["ex"] != "zz" else "none", rot=n["rot"], sx=n["sx"], sy=n["sy"]))
    if n["sleep"]:
        L.append(f'<g transform="translate({n["x"]:.1f} {n["y"]:.1f}) rotate({n["rot"]:.1f}) scale({n["sx"]*NR/48*1.05:.3f} {n["sy"]*NR/48*1.05:.3f})">'
                 f'<path d="M-22 -4 q8 8 16 0 M6 -4 q8 8 16 0" fill="none" stroke="#2a1a10" stroke-width="5" stroke-linecap="round"/>'
                 f'<ellipse cx="0" cy="14" rx="5" ry="6" fill="#7a2a1a" stroke="#2a1a10" stroke-width="3"/></g>')
    if n["glasses"] and n["ex"] != "cool":
        pass
    # nibbo arms
    if item and two_hands:
        L.append(item)
        L.append(arm(n["x"] - 84, n["y"] - 46, hx + 10, hy + 34, NS, 10, -6) + hand(hx + 10, hy + 34, NB, NS, 12))
        L.append(arm(n["x"] - 100, n["y"] + 10, hx + 30, hy + 44, NS, 10, 14) + hand(hx + 30, hy + 44, NB, NS, 12))
    elif item:
        L.append(item)
    if mal:
        L.append(mal)
        if t < T_PRESS + 0.55:
            k = eio(seg(t, T_MALLET, T_WIND1))
            mx, my = n["x"] - 10 - 40 * k, n["y"] - 130 - 30 * k
            L.append(arm(n["x"] - 60, n["y"] - 60, mx, my + 4, NS, 10, 10) + hand(mx, my + 4, NB, NS, 12))
            L.append(arm(n["x"] + 50, n["y"] - 60, mx + 6, my - 20, NS, 10, 10) + hand(mx + 6, my - 20, NB, NS, 12))
    if T_BACK0 <= t < T_MALLET and gx is not None:
        # pulling the gong by a rope
        L.append(f'<path d="M{n["x"]+60:.0f} {n["y"]-30:.0f} Q {(n["x"]+gx-140)/2:.0f} {n["y"]+30:.0f} {gx-140:.0f} {FLOOR-40}" stroke="#c9763a" stroke-width="7" fill="none"/>')
        L.append(hand(n["x"] + 60, n["y"] - 30, NB, NS, 12))
    # grumpo hand drawn again on top when pressing nibbo
    if hp and T_PRESS - 0.3 <= t < T_PRESS + 0.6:
        L.append(arm(450, 1500 + dy, hp[0], hp[1], ink, 13, -30) + hand(hp[0], hp[1], gfill, OL, 16))

    # ---- effects
    if ringing(t):
        big = 1.0 if t < T_SLAP1 else 1.8
        L.append(sound_arcs(hx - 70 * big, hy - 30, t, -1, big) + sound_arcs(hx + 70 * big, hy - 30, t, 1, big))
    L.append(impact(HP[0], HP[1] - 50, seg(t, T_SLAP1, T_SLAP1 + 0.2)))
    L.append(impact(HP[0], HP[1] - 120, seg(t, T_SLAP2, T_SLAP2 + 0.25)))
    L.append(impact(NX0, NG - NR, seg(t, T_PRESS, T_PRESS + 0.2), "#ffffff"))
    L.append(impact(gx - 98 if gx else 0, GONG_Y, seg(t, T_TIP1, T_TIP1 + 0.25), "#ffe08a") if gx else "")
    L.append(symbol(n["x"] + 20, n["y"] - 170, "!", seg(t, T_HONK + 0.05, T_HONK + 0.6)))
    L.append(symbol(n["x"] + 20, n["y"] - 175, "!", seg(t, T_PRESS + 0.02, T_PRESS + 0.45), "#3a7ad6"))
    L.append(symbol(n["x"] - 10, n["y"] - 170, "?", seg(t, T_UNDER + 0.1, T_UNDER + 0.8), "#3a7ad6"))
    # zzz (grumpo, when content) + nibbo snoring
    if g["content"] and not (T_PEEK0 <= t < T_PEEK1):
        L.append(zzz(g["x"] - 40, g["y"] - 120, t, 0.0, 1.0))
    if n["sleep"] and t > T_PRESS + 0.5:
        L.append(zzz(n["x"] + 40, n["y"] - 110, t, 0.4, 0.75))
    if T_PEEK0 + 0.1 <= t < T_PEEK1 - 0.1:
        L.append(star_twinkle(g["x"] + 70, g["y"] - 40, seg(t, T_PEEK0 + 0.3, T_PEEK0 + 0.9)))
    if T_SQ1 <= t < T_GRAB3:
        L.append(f'<path d="M{g["x"]+70:.0f} {g["y"]-110:.0f} l18 -8 l-6 18 M{g["x"]+88:.0f} {g["y"]-92:.0f} l18 -8 l-6 18" stroke="#e8303a" stroke-width="6" fill="none" stroke-linecap="round"/>')

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g></svg>')
    c, bt = snooze_count(t)
    return overlay(svg, hook_title(t + 0.12, "Don't wake", "GRUMPO!"),
                   counter(t, c, "SNOOZE", c, 5, bump_t=bt))


def build_sfx():
    sfx(0.0, "alarm_ring", 0.6, 1.0)
    sfx(0.75, "alarm_ring", 0.6, 1.0)
    sfx(0.2, "snore", 0.4, 1.0)
    sfx(1.1, "grumble", 0.4, 1.1)
    sfx(T_SLAP1, "bonk", 0.9, 1.2)
    sfx(T_SLAP1 + 0.02, "squish", 0.6, 1.0)
    sfx(T_SLAP1 + 0.05, "ding", 0.45, 1.0)
    sfx(T_SLAP1 + 0.1, "blip", 0.45, 1.0)
    sfx(T_SLAP1 + 0.7, "whoosh", 0.5, 1.4)
    sfx(2.1, "snore", 0.55, 1.0)
    sfx(T_POP2, "pop", 0.7, 0.9)
    for k in range(3):
        sfx(T_RING2 + k * 0.45, "alarm_ring", 0.95, 0.72)
    sfx(T_RING2 + 0.1, "rumble", 0.5, 1.2)
    sfx(T_RING2 + 0.3, "shaker", 0.4, 1.0)
    sfx(3.6, "grumble", 0.6, 0.9)
    sfx(T_SLAP2, "bonk", 1.0, 0.85)
    sfx(T_SLAP2 + 0.02, "boing", 0.8, 1.1)
    sfx(T_SLAP2 + 0.08, "boing", 0.6, 1.5)
    sfx(T_SLAP2 + 0.1, "blip", 0.45, 1.06)
    sfx(T_SLAP2 + 0.5, "clank", 0.5, 1.3)
    sfx(T_SLAP2 + 0.8, "whoosh", 0.4, 1.2)
    sfx(4.75, "snore", 0.55, 0.95)
    sfx(T_POP3, "pop", 0.7, 1.1)
    sfx(T_SQ1, "chicken", 1.0, 1.0)
    sfx(T_SQ2, "chicken", 1.0, 1.1)
    sfx(T_SQ1 + 0.2, "grumble", 0.4, 1.2)
    sfx(T_GRAB3, "squeak", 0.6, 0.8)
    sfx(T_GRAB3 + 0.1, "whoosh", 0.5, 1.2)
    sfx(T_UNDER, "thud", 0.5, 1.4)
    sfx(T_UNDER + 0.02, "blip", 0.45, 1.12)
    sfx(7.2, "chicken", 0.3, 0.8)
    sfx(7.65, "chicken", 0.25, 0.75)
    sfx(7.5, "snore", 0.5, 1.0)
    sfx(T_POP4, "pop", 0.7, 1.2)
    sfx(T_TURN0, "creak", 0.4, 1.6)
    sfx(T_TURN1, "click", 0.5, 1.2)
    sfx(T_HONK - 0.05, "click", 0.6, 1.0)
    sfx(T_HONK, "honk", 1.0, 1.0)
    sfx(T_HONK + 0.02, "blip", 0.45, 1.18)
    sfx(T_HONK + 0.6, "wobble", 0.5, 1.0)
    sfx(T_HONK + 1.0, "clank", 0.4, 1.4)
    sfx(10.0, "snore", 0.5, 1.0)
    for k in range(3):
        sfx(T_EXIT + k * 0.15, "hop", 0.4, 1.3)
    sfx(T_BACK0, "drag", 0.6, 1.0)
    sfx(T_BACK0 + 0.4, "drag", 0.5, 1.1)
    sfx(T_BACK0 + 0.1, "creak", 0.4, 0.9)
    sfx(T_MALLET, "pop", 0.5, 1.0)
    sfx(T_MALLET + 0.1, "suspense", 0.6, 1.0)
    sfx(T_MALLET + 0.15, "inhale", 0.5, 1.0)
    for k, tk in enumerate((12.2, 12.45, 12.7, 12.9)):
        sfx(tk, "tap", 0.5, 0.9 + 0.05 * k)
    sfx(T_PRESS, "click", 0.9, 0.9)
    sfx(T_PRESS + 0.02, "squish", 0.6, 1.2)
    sfx(T_PRESS + 0.05, "blip", 0.5, 1.26)
    sfx(T_PRESS + 0.3, "slide_down", 0.5, 1.0)
    sfx(T_PRESS + 0.9, "clank", 0.5, 1.6)
    sfx(T_PRESS + 0.6, "snore", 0.45, 1.5)
    sfx(T_TIP1, "gong", 0.6, 1.0)
    sfx(15.2, "snore", 0.55, 1.0)
    sfx(15.5, "snore", 0.35, 1.5)
    sfx(T_PEEK0 + 0.2, "squeak", 0.3, 1.3)
    sfx(T_PEEK0 + 0.4, "ding", 0.3, 2.0)
    sfx(17.0, "snore", 0.55, 0.95)
