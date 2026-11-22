"""Grumpo & Nibbo — Episode 6: Black Friday (store opening race, 60 fps).

6:00 AM, Black Friday. Grumpo squashes Nibbo against the store's shutter; a poster
promises a big TV at -90%. The clock flips, the shutter rattles up — Nibbo squirts out
under the gap and Grumpo face-plants the rising shutter. RACE: Grumpo hops into a
shopping cart and zooms past (Nibbo is spun by the draft), but the cart hits the
wet-floor sign and spins out. Nibbo cannonballs into the ball bin, boings off
Grumpo's head and lands on the TV box. Grumpo rams the pedestal: box, Nibbo and Grumpo
all fly. They both grab the box ... it's weirdly light. Grumpo shakes it: out drops a
TV the size of a matchbox. The tag explains it: -90% ... of the SIZE. The antenna falls
off. Meanwhile Nibbo has found the real prize: the giant empty box.
Ending: the prize was worthless.
"""
import math, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow
from hook import overlay, hook_title

W, H, FPS, DUR = 1080, 1920, 60, 20.9
FLOOR = 1700
GS = 0.92
NR = 112
GY = FLOOR - 120
NG = FLOOR - NR

GATE_X0, GATE_X1 = 600, 656
ROLL_Y0, ROLL_Y1 = 1110, 1196
CART_Y = 1385                     # Grumpo centre while sitting in cart
BIN_X, BIN_W, BIN_TOP = 1230, 250, 1528
SIGN_X = 1470
PUD0, PUD1 = 1380, 1780
PED_X, PED_W, PED_TOP = 2150, 250, 1530
BW, BH = 264, 214                 # big TV box
BOX_ON_PED = (PED_X, PED_TOP - BH / 2)
BOX_FLOOR = (2470, FLOOR - BH / 2)

T_TICK = 1.55
T_OPEN = 1.72
T_SQUIRT = 2.12
T_FACE = 2.36
T_DROP = 2.86
T_RUN = 3.2
T_HOP = 3.72
T_CARTIN = 4.0
T_PASS = 4.5
T_SIGN = 5.35
T_STOP = 6.6
T_BIN = 5.98
T_LAUNCH = 6.5
T_HEAD = 7.25
T_BOXLAND = 8.05
T_SEE = 8.15
T_PUSH = 8.6
T_CRASH = 9.15
T_LAND = 10.0
T_LIFT0, T_LIFT1 = 10.75, 11.35
T_GRAB = 12.05
T_FLIP = 12.55
T_DROPTV = 13.0
T_PALM = 13.3
T_TOSSLAND = 13.45
T_TVON = 13.8
T_TAG0, T_TAG1 = 14.55, 15.75
T_EYE = 16.0
T_ANT = 16.9
T_NJUMP, T_NIN = 17.0, 17.5
T_BHOP1, T_BHOP2 = 18.3, 18.85
T_DIE = 19.5
T_SLUMP = 19.7

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


def arc(t, t0, t1, p0, p1, h):
    p = seg(t, t0, t1)
    return lerp(p0[0], p1[0], p), lerp(p0[1], p1[1], p) - h * 4 * p * (1 - p)


def arm(x0, y0, x1, y1, col, w=10, sag=30):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    return f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


def hand(x, y, fill, stroke, r=13):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="5"/>'


def sweat(x, y, p=1.0):
    return f'<path d="M{x:.1f} {y:.1f} q12 20 0 28 q-12 -8 0 -28z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3" opacity="{p:.2f}"/>'


def txt(x, y, s, size, fill, stroke="#ffffff", sw=0, rot=0):
    st = f'stroke="{stroke}" stroke-width="{sw}" paint-order="stroke" stroke-linejoin="round"' if sw else ""
    return (f'<text x="{x}" y="{y}" transform="rotate({rot} {x} {y})" font-family="Fredoka" font-weight="700" font-size="{size}" '
            f'text-anchor="middle" fill="{fill}" {st}>{s}</text>')


def burst(x, y, r, rot=0, fill="#e8303a"):
    pts = []
    for k in range(24):
        a = math.radians(k * 15)
        rr = r if k % 2 == 0 else r * 0.8
        pts.append(f"{x + rr*math.cos(a):.1f},{y + rr*math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{fill}" stroke="{OL}" stroke-width="5" stroke-linejoin="round" transform="rotate({rot} {x} {y})"/>'


# ---------------------------------------------------------------- props
def tv_picture(x0, y0, w, h, ctx):
    """a TV set with a hilly landscape on screen (used on poster + box print)."""
    cid = ctx.uid("tvp")
    ctx.defs.append(f'<clipPath id="{cid}"><rect x="{x0+10}" y="{y0+10}" width="{w-20}" height="{h-20}" rx="6"/></clipPath>')
    return (f'<rect x="{x0+w/2-30:.0f}" y="{y0+h-4}" width="60" height="18" rx="4" fill="#3a3a48" stroke="{OL}" stroke-width="4"/>'
            f'<rect x="{x0+w/2-60:.0f}" y="{y0+h+10}" width="120" height="10" rx="5" fill="#3a3a48" stroke="{OL}" stroke-width="4"/>'
            f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="10" fill="#22222c" stroke="{OL}" stroke-width="5"/>'
            f'<g clip-path="url(#{cid})"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#6ec3ff"/>'
            f'<circle cx="{x0+w*0.75:.0f}" cy="{y0+h*0.3:.0f}" r="{h*0.12:.0f}" fill="#fff3a0"/>'
            f'<path d="M{x0} {y0+h*0.75:.0f} Q {x0+w*0.3:.0f} {y0+h*0.35:.0f} {x0+w*0.6:.0f} {y0+h*0.7:.0f} T {x0+w} {y0+h*0.6:.0f} V{y0+h} H{x0}Z" fill="#5cc46a"/>'
            f'<path d="M{x0} {y0+h*0.9:.0f} Q {x0+w*0.5:.0f} {y0+h*0.65:.0f} {x0+w} {y0+h*0.85:.0f} V{y0+h} H{x0}Z" fill="#3fa456"/>'
            f'<path d="M{x0+w*0.1:.0f} {y0+h} L{x0+w*0.4:.0f} {y0} L{x0+w*0.52:.0f} {y0} L{x0+w*0.22:.0f} {y0+h}Z" fill="#ffffff" opacity="0.18"/></g>')


def size_tag(x, y, s=1.0, rot=0):
    """price tag: burst '-90%' + icon strip BIG TV -> tiny TV (the fine print)."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            f'<path d="M-70 -6 h140 v74 h-140z" fill="#ffffff" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            # big tv icon
            f'<rect x="-60" y="10" width="50" height="36" rx="4" fill="#6ec3ff" stroke="{OL}" stroke-width="4"/>'
            f'<path d="M-44 46 h18 M-35 46 v8 M-46 54 h22" stroke="{OL}" stroke-width="4" stroke-linecap="round"/>'
            # arrow
            f'<path d="M-2 28 h26 m-9 -9 l9 9 l-9 9" fill="none" stroke="#e8303a" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>'
            # tiny tv icon
            f'<rect x="38" y="30" width="14" height="11" rx="2" fill="#6ec3ff" stroke="{OL}" stroke-width="3"/>'
            f'<path d="M45 41 v5 M40 46 h10" stroke="{OL}" stroke-width="3" stroke-linecap="round"/>'
            f'{burst(0, -40, 58, 8)}'
            f'{txt(0, -26, "-90%", 40, "#ffffff", OL, 7, -8)}'
            '</g>')


def big_box(ctx, x, y, rot=0.0, flaps=0.0, sx=1.0, sy=1.0, front_only=False):
    """cardboard TV box; local origin = centre. flaps 0 closed (taped) .. 1 open."""
    hw, hh = BW / 2, BH / 2
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx:.3f} {sy:.3f})">']
    if flaps > 0:
        a = 120 * flaps
        o.append(f'<g transform="translate({-hw} {-hh}) rotate({-a:.1f})"><rect x="0" y="-8" width="{hw:.0f}" height="16" rx="3" fill="#c48f52" stroke="{OL}" stroke-width="5"/></g>'
                 f'<g transform="translate({hw} {-hh}) rotate({a:.1f})"><rect x="{-hw:.0f}" y="-8" width="{hw:.0f}" height="16" rx="3" fill="#c48f52" stroke="{OL}" stroke-width="5"/></g>')
    if not front_only and flaps > 0:
        o.append(f'<rect x="{-hw+8}" y="{-hh-2}" width="{BW-16}" height="26" fill="#7a5224"/>')
    o.append(f'<rect x="{-hw}" y="{-hh}" width="{BW}" height="{BH}" rx="8" fill="#dcaa6a" stroke="{OL}" stroke-width="7"/>')
    o.append(f'<rect x="{-hw+8}" y="{hh-26}" width="{BW-16}" height="18" rx="4" fill="#c48f52"/>')
    o.append(f'<path d="M{-hw+14} {-hh+14} V{hh-30}" stroke="#f0c890" stroke-width="7" stroke-linecap="round"/>')
    o.append(tv_picture(-hw + 22, -hh + 32, 150, 104, ctx))
    if flaps <= 0:
        o.append(f'<rect x="-22" y="{-hh-3}" width="44" height="26" fill="#d8c9a0" opacity="0.85" stroke="#a89466" stroke-width="2"/>')
    o.append(size_tag(hw - 58, -hh + 56, 0.78, 6))
    o.append('</g>')
    return "".join(o)


def tiny_tv(x, y, s=1.0, rot=0.0, on=0.0, antenna=True, t=0.0, dead=False):
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">']
    if antenna:
        o.append(f'<path d="M0 -18 L-12 -36 M0 -18 L12 -38" stroke="{OL}" stroke-width="3.5" stroke-linecap="round"/>'
                 '<circle cx="-12" cy="-36" r="3.5" fill="#e8303a"/><circle cx="12" cy="-38" r="3.5" fill="#e8303a"/>')
    o.append(f'<rect x="-24" y="-18" width="48" height="36" rx="6" fill="#8a8fa0" stroke="{OL}" stroke-width="4"/>'
             f'<rect x="-19" y="-13" width="30" height="26" rx="3" fill="#1a1a24"/>'
             f'<circle cx="17" cy="-6" r="3" fill="{OL}"/><circle cx="17" cy="5" r="3" fill="{OL}"/>'
             f'<rect x="-18" y="18" width="7" height="6" fill="{OL}"/><rect x="11" y="18" width="7" height="6" fill="{OL}"/>')
    if on > 0 and not dead:
        fl = 0.75 + 0.25 * math.sin(t * 47)
        o.append(f'<g opacity="{on*fl:.2f}"><rect x="-19" y="-13" width="30" height="26" rx="3" fill="#6ec3ff"/>'
                 '<path d="M-19 8 Q -8 -2 2 6 T 11 4 V13 H-19Z" fill="#5cc46a"/>'
                 f'<circle cx="5" cy="-6" r="3.5" fill="#fff3a0"/></g>')
        o.append(f'<rect x="-26" y="-20" width="52" height="40" rx="8" fill="#9fdcff" opacity="{0.25*on:.2f}"/>')
    if dead:
        o.append('<path d="M-17 0 h26" stroke="#ffffff" stroke-width="2" opacity="0.6"/>')
    o.append('</g>')
    return "".join(o)


def antenna_piece(x, y, rot):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})"><path d="M0 0 L12 -20" stroke="{OL}" stroke-width="3.5" stroke-linecap="round"/>'
            '<circle cx="12" cy="-20" r="3.5" fill="#e8303a"/></g>')


def cart_back(x, spin=1.0, tilt=0.0):
    return (f'<g transform="translate({x:.1f} {FLOOR}) rotate({tilt:.1f} 0 -20) scale({spin:.3f} 1)">'
            f'<path d="M-150 -236 L-196 -300" stroke="{OL}" stroke-width="16" stroke-linecap="round"/>'
            f'<path d="M-150 -236 L-196 -300" stroke="#c9d1dc" stroke-width="8" stroke-linecap="round"/>'
            f'<path d="M-208 -306 l-14 -18" stroke="{OL}" stroke-width="26" stroke-linecap="round"/>'
            f'<path d="M-208 -306 l-14 -18" stroke="#e8303a" stroke-width="16" stroke-linecap="round"/>'
            f'<path d="M-150 -236 L150 -236 L122 -84 L-118 -84Z" fill="#8a96a8" fill-opacity="0.35" stroke="#7a8496" stroke-width="5"/>'
            '</g>')


def cart_front(x, spin=1.0, tilt=0.0, t=0.0, rolling=False):
    o = [f'<g transform="translate({x:.1f} {FLOOR}) rotate({tilt:.1f} 0 -20) scale({spin:.3f} 1)">']
    o.append(f'<path d="M-118 -84 L-100 -40 M122 -84 L100 -40 M-110 -46 H110" stroke="{OL}" stroke-width="12" stroke-linecap="round"/>'
             f'<path d="M-118 -84 L-100 -40 M122 -84 L100 -40 M-110 -46 H110" stroke="#c9d1dc" stroke-width="6" stroke-linecap="round"/>')
    for wx in (-100, 100):
        a = (t * 900) % 360 if rolling else 0
        o.append(f'<g transform="translate({wx} -20) rotate({a:.0f})"><circle r="20" fill="#3a3a48" stroke="{OL}" stroke-width="5"/>'
                 '<path d="M-10 0 H10" stroke="#8a8fa0" stroke-width="4"/><circle r="5" fill="#c9d1dc"/></g>')
    # basket front: wire mesh
    o.append(f'<path d="M-150 -236 L150 -236 L122 -84 L-118 -84Z" fill="#dfe6ee" fill-opacity="0.38"/>')
    for k in range(1, 9):
        xt = -150 + k * 300 / 9
        xb = -118 + k * 240 / 9
        o.append(f'<path d="M{xt:.0f} -236 L{xb:.0f} -84" stroke="#8a96a8" stroke-width="4"/>')
    for k in range(1, 4):
        yy = -236 + k * 38
        f = (yy + 236) / 152
        o.append(f'<path d="M{-150 + 32*f:.0f} {yy} H{150 - 28*f:.0f}" stroke="#8a96a8" stroke-width="4"/>')
    o.append(f'<path d="M-150 -236 L150 -236 L122 -84 L-118 -84Z" fill="none" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>')
    o.append(f'<path d="M-156 -236 H156" stroke="{OL}" stroke-width="14" stroke-linecap="round"/><path d="M-156 -236 H156" stroke="#e8303a" stroke-width="7" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


def wet_sign(x, y, rot):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">'
            f'<path d="M-58 0 L-18 -190 L18 -190 L58 0" fill="none" stroke="{OL}" stroke-width="14" stroke-linejoin="round"/>'
            f'<path d="M-52 -4 L-16 -184 L16 -184 L52 -4Z" fill="#ffd23a" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<path d="M-30 -112 L0 -160 L30 -112Z" fill="#ffffff" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>'
            f'<circle cx="6" cy="-140" r="5" fill="{OL}"/><path d="M4 -134 l-6 12 l8 4 M-2 -122 l-8 4" stroke="{OL}" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
            f'<path d="M-18 -116 q10 -4 20 0" stroke="#3a8be0" stroke-width="3" fill="none"/>'
            f'<path d="M-34 -70 q8 -10 16 0 t16 0 t16 0 t16 0" stroke="#3a8be0" stroke-width="5" fill="none" stroke-linecap="round"/>'
            '</g>')


BALLS = [(BIN_X - 105 + (k * 37) % 215, BIN_TOP + 4 - (k * 13) % 26, ["#e8303a", "#3a8be0", "#ffd23a", "#46b86a", "#ff6fa8", "#8a5ad8"][k % 6])
         for k in range(22)]


def ball_bin_back():
    return (f'<rect x="{BIN_X-BIN_W/2}" y="{BIN_TOP-14}" width="{BIN_W}" height="30" fill="#7a1a20"/>')


def ball_bin_front(t):
    o = []
    jig = 0.0
    if T_BIN <= t < T_LAUNCH + 0.2:
        jig = 1.0
    for k, (bx, by, c) in enumerate(BALLS):
        dy = 0.0
        if jig:
            dy = -abs(math.sin(t * 18 + k)) * 10
        o.append(f'<circle cx="{bx:.0f}" cy="{by+dy:.0f}" r="20" fill="{c}" stroke="{OL}" stroke-width="4"/>'
                 f'<circle cx="{bx-6:.0f}" cy="{by+dy-7:.0f}" r="5" fill="#ffffff" opacity="0.6"/>')
    o.append(f'<rect x="{BIN_X-BIN_W/2}" y="{BIN_TOP}" width="{BIN_W}" height="{FLOOR-BIN_TOP}" rx="10" fill="#e8303a" stroke="{OL}" stroke-width="7"/>'
             f'<rect x="{BIN_X-BIN_W/2+12}" y="{BIN_TOP+12}" width="{BIN_W-24}" height="14" rx="5" fill="#ff7a80"/>')
    o.append(burst(BIN_X, BIN_TOP + 92, 46, 10, "#ffd23a"))
    o.append(txt(BIN_X, BIN_TOP + 106, "%", 44, "#e8303a"))
    return "".join(o)


def flying_balls(t):
    if not (T_BIN - 0.02 <= t < T_BIN + 0.9) and not (T_LAUNCH <= t < T_LAUNCH + 0.9):
        return ""
    o = []
    for t0, seed in ((T_BIN, 1), (T_LAUNCH, 2)):
        if not (t0 <= t < t0 + 0.9):
            continue
        rnd = random.Random(seed)
        k = t - t0
        for i in range(7):
            vx = rnd.uniform(-420, 420)
            vy = rnd.uniform(-900, -600)
            x = BIN_X + rnd.uniform(-60, 60) + vx * k
            y = BIN_TOP + vy * k + 0.5 * 2600 * k * k
            if y > FLOOR - 20:
                continue
            c = ["#e8303a", "#3a8be0", "#ffd23a", "#46b86a", "#ff6fa8", "#8a5ad8"][i % 6]
            o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="18" fill="{c}" stroke="{OL}" stroke-width="4"/>')
    return "".join(o)


def pedestal(t):
    o = [f'<path d="M{PED_X-60} 900 L{PED_X-190} {FLOOR} H{PED_X+190} L{PED_X+60} 900Z" fill="#fff6c0" opacity="0.28"/>',
         f'<rect x="{PED_X-PED_W/2}" y="{PED_TOP}" width="{PED_W}" height="{FLOOR-PED_TOP}" rx="10" fill="#f4f1fa" stroke="{OL}" stroke-width="7"/>',
         f'<rect x="{PED_X-PED_W/2-12}" y="{PED_TOP-6}" width="{PED_W+24}" height="30" rx="8" fill="#e8303a" stroke="{OL}" stroke-width="6"/>',
         f'<path d="M{PED_X-PED_W/2+16} {PED_TOP+40} V{FLOOR-16}" stroke="#ffffff" stroke-width="10" stroke-linecap="round"/>',
         burst(PED_X, PED_TOP + 98, 40, -8, "#ffd23a"),
         txt(PED_X, PED_TOP + 110, "%", 38, "#e8303a")]
    return "".join(o)


def gate_bottom(t):
    if t < T_OPEN:
        return FLOOR
    if t < T_SQUIRT:
        p = seg(t, T_OPEN, T_SQUIRT)
        return FLOOR - 95 * p + 6 * math.sin(t * 60) * (1 - p)
    return lerp(FLOOR - 95, ROLL_Y1 + 10, eio(seg(t, T_SQUIRT, 3.25)))


def gate(t):
    gb = gate_bottom(t)
    o = [f'<rect x="{GATE_X0-40}" y="-900" width="{GATE_X1-GATE_X0+80}" height="{ROLL_Y0+900}" fill="#3a3550"/>',
         f'<rect x="{GATE_X0-40}" y="{ROLL_Y0-40}" width="{GATE_X1-GATE_X0+80}" height="40" fill="#e8303a" stroke="{OL}" stroke-width="5"/>']
    h = gb - ROLL_Y1
    if h > 2:
        o.append(f'<rect x="{GATE_X0}" y="{ROLL_Y1}" width="{GATE_X1-GATE_X0}" height="{h:.1f}" fill="#b9c0cc" stroke="{OL}" stroke-width="6"/>')
        y = gb - 4
        while y > ROLL_Y1 + 6:
            o.append(f'<path d="M{GATE_X0+4} {y:.1f} H{GATE_X1-4}" stroke="#8a93a2" stroke-width="5"/>')
            y -= 22
        o.append(f'<rect x="{GATE_X0-6}" y="{gb-16:.1f}" width="{GATE_X1-GATE_X0+12}" height="18" rx="5" fill="#6a7282" stroke="{OL}" stroke-width="5"/>')
    o.append(f'<rect x="{GATE_X0-34}" y="{ROLL_Y0}" width="{GATE_X1-GATE_X0+68}" height="{ROLL_Y1-ROLL_Y0}" rx="14" fill="#8a93a2" stroke="{OL}" stroke-width="7"/>'
             f'<path d="M{GATE_X0-22} {ROLL_Y0+18} H{GATE_X1+22}" stroke="#c9d1dc" stroke-width="7" stroke-linecap="round"/>')
    # floor guide rails
    o.append(f'<rect x="{GATE_X0-8}" y="{FLOOR-6}" width="{GATE_X1-GATE_X0+16}" height="10" fill="#6a7282"/>')
    return "".join(o)


def clock(t):
    s = "5:59" if t < T_TICK else "6:00"
    col = "#ff4a4a" if t < T_TICK else "#5aff8a"
    blink = 1.0 if (t < T_TICK and math.sin(t * 9) > 0) or t >= T_TICK else 0.0
    if t < T_TICK:
        s = s.replace(":", ":" if blink else " ")
    sc = 1.0 + (0.2 * math.sin(math.pi * seg(t, T_TICK, T_TICK + 0.3)) if t >= T_TICK else 0)
    o = [f'<g transform="translate(470 1206) scale({sc:.3f})">',
         f'<rect x="-74" y="-40" width="148" height="80" rx="14" fill="#1a1a24" stroke="{OL}" stroke-width="6"/>',
         f'<rect x="-64" y="-30" width="128" height="60" rx="8" fill="#0d0d14"/>',
         txt(0, 20, s, 52, col),
         '</g>']
    if t >= T_TICK:
        o.insert(0, f'<circle cx="470" cy="1206" r="{90 + 40*seg(t, T_TICK, T_TICK+0.4):.0f}" fill="#5aff8a" opacity="{0.35*(1-seg(t, T_TICK, T_TICK+0.4)):.2f}"/>')
    return "".join(o)


def poster(ctx):
    x0, y0 = 104, 1122
    return (f'<rect x="{x0}" y="{y0}" width="300" height="250" rx="12" fill="#ffffff" stroke="{OL}" stroke-width="7"/>'
            f'<rect x="{x0+12}" y="{y0+12}" width="276" height="226" rx="6" fill="#1f2a6a"/>'
            + "".join(f'<circle cx="{x0+30+k*42}" cy="{y0+30+(k%2)*14}" r="4" fill="#ffd23a" opacity="0.8"/>' for k in range(7))
            + tv_picture(x0 + 26, y0 + 50, 170, 118, ctx)
            + burst(x0 + 232, y0 + 86, 62, 12)
            + txt(x0 + 232, y0 + 101, "-90%", 40, "#ffffff", OL, 7, -10))


def store_bg(t, ctx):
    o = []
    # mall corridor (left)
    o.append(f'<rect x="-900" y="-900" width="{GATE_X0+900}" height="{FLOOR+900}" fill="#d9d2ee"/>')
    for x in range(-880, GATE_X0, 90):
        o.append(f'<rect x="{x}" y="-900" width="40" height="{FLOOR+900}" fill="#d0c8e8"/>')
    o.append(f'<rect x="-900" y="1600" width="{GATE_X0+900}" height="{FLOOR-1600}" fill="#b9b0dc"/>'
             f'<rect x="-900" y="1590" width="{GATE_X0+900}" height="14" fill="#f4f1fa" stroke="{OL}" stroke-width="4"/>')
    o.append(poster(ctx))
    # doorway interior (visible once the shutter is up)
    o.append(f'<rect x="{GATE_X0-1}" y="{ROLL_Y0}" width="{GATE_X1-GATE_X0+2}" height="{FLOOR-ROLL_Y0}" fill="#e9dcc0"/>')
    # store interior wall
    o.append(f'<rect x="{GATE_X1}" y="-900" width="3400" height="{FLOOR+900}" fill="#f6ecd6"/>')
    for x in range(GATE_X1 + 30, 4000, 160):
        o.append(f'<rect x="{x}" y="-900" width="70" height="{FLOOR+900}" fill="#f1e4c8"/>')
    # pennant string (sale flags with %)
    for seg_x in range(GATE_X1 + 40, 3600, 520):
        pts = []
        for k in range(9):
            px = seg_x + k * 60
            py = 1110 + 26 * math.sin(math.pi * k / 8)
            pts.append((px, py))
        o.append('<path d="M' + " L".join(f"{px:.0f} {py:.0f}" for px, py in pts) + f'" stroke="{OL}" stroke-width="4" fill="none"/>')
        for k, (px, py) in enumerate(pts[:-1]):
            c = "#e8303a" if k % 2 == 0 else "#ffd23a"
            o.append(f'<path d="M{px:.0f} {py:.0f} L{px+60:.0f} {pts[k+1][1]:.0f} L{px+30:.0f} {py+62:.0f}Z" fill="{c}" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>')
    # shelving units along wall
    for sx0 in (760, 1560, 2700, 3100):
        if 1900 < sx0 < 2600:
            continue
        o.append(f'<rect x="{sx0}" y="1230" width="330" height="{FLOOR-1230}" fill="#c9d1dc" stroke="{OL}" stroke-width="6"/>')
        for r, sy in enumerate((1330, 1450, 1570)):
            rnd = random.Random(sx0 + r)
            bx = sx0 + 14
            while bx < sx0 + 300:
                bw = rnd.choice([44, 58, 70])
                bh = rnd.choice([56, 70, 84])
                c = rnd.choice(["#ff8a3a", "#3a8be0", "#46b86a", "#8a5ad8", "#ffd23a", "#ff6fa8", "#2ec4b6"])
                if bx + bw > sx0 + 318:
                    break
                if r == 0 and rnd.random() < 0.5:
                    o.append(f'<rect x="{bx}" y="{sy-bh+20}" width="{bw+10}" height="{bh-24}" rx="5" fill="#22222c" stroke="{OL}" stroke-width="4"/>'
                             f'<rect x="{bx+6}" y="{sy-bh+26}" width="{bw-2}" height="{bh-36}" rx="3" fill="#6ec3ff"/>')
                else:
                    o.append(f'<rect x="{bx}" y="{sy-bh}" width="{bw}" height="{bh}" rx="4" fill="{c}" stroke="{OL}" stroke-width="4"/>'
                             f'<rect x="{bx+6}" y="{sy-bh+8}" width="{bw-12}" height="10" rx="3" fill="#ffffff" opacity="0.45"/>')
                bx += bw + 8
            o.append(f'<rect x="{sx0}" y="{sy}" width="330" height="14" fill="#8a93a2" stroke="{OL}" stroke-width="4"/>')
        o.append(burst(sx0 + 300, 1250, 34, 0, "#e8303a") + txt(sx0 + 300, 1262, "%", 32, "#ffffff"))
    # floors
    o.append(f'<rect x="-900" y="{FLOOR}" width="{GATE_X0+900}" height="900" fill="#cdb894"/>')
    for x in range(-900, GATE_X0, 110):
        o.append(f'<path d="M{x} {FLOOR} V{FLOOR+900}" stroke="#b9a37c" stroke-width="4"/>')
    o.append(f'<rect x="{GATE_X0}" y="{FLOOR}" width="3800" height="900" fill="#c4ccda"/>')
    for x in range(GATE_X0, 4400, 140):
        o.append(f'<path d="M{x} {FLOOR} l-60 900" stroke="#b0b9c9" stroke-width="4"/>')
    o.append(f'<path d="M{GATE_X0} {FLOOR+60} H4400 M{GATE_X0} {FLOOR+150} H4400" stroke="#b0b9c9" stroke-width="4"/>')
    o.append(f'<line x1="-900" y1="{FLOOR}" x2="4400" y2="{FLOOR}" stroke="{OL}" stroke-width="6"/>')
    # puddle
    o.append(f'<ellipse cx="{(PUD0+PUD1)/2}" cy="{FLOOR+28}" rx="{(PUD1-PUD0)/2}" ry="24" fill="#9fdcff" opacity="0.75"/>'
             f'<path d="M{PUD0+80} {FLOOR+22} h90 M{PUD0+230} {FLOOR+34} h60" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="0.8"/>')
    return "".join(o)


# ---------------------------------------------------------------- motion
CARTK = [(0, 900), (T_CARTIN, 900), (T_SIGN, 1440)]


def cart_state(t):
    """x, spin scaleX, tilt, rolling"""
    if t < T_CARTIN:
        return 900, 1.0, 0.0, False
    if t < T_SIGN:
        p = seg(t, T_CARTIN, T_SIGN)
        return lerp(900, 1440, p ** 1.6), 1.0, -3 * math.sin(t * 20), True
    if t < T_STOP:
        p = eout(seg(t, T_SIGN, T_STOP))
        ang = 3 * 360 * p
        s = math.cos(math.radians(ang))
        s = math.copysign(max(0.12, abs(s)), s)
        return lerp(1440, 1640, p), s, 4 * math.sin(t * 30) * (1 - p), p < 0.95
    if t < T_PUSH:
        return 1640, 1.0, 0.0, False
    if t < T_CRASH:
        p = seg(t, T_PUSH, T_CRASH)
        return lerp(1640, 1870, p ** 2), 1.0, -4, True
    k = t - T_CRASH
    tilt = 22 * math.exp(-k * 5) * math.cos(k * 18) if k < 1.2 else 0
    return 1870, 1.0, tilt, False


def box_state(t):
    """x, y, rot, flaps, sx, sy"""
    if t < T_CRASH:
        x, y = BOX_ON_PED
        sx, sy = squash(t, T_BOXLAND, 0.3, 0.12)
        return x, y + BH / 2 * (1 - sy), 0, 0, sx, sy
    if t < T_LAND:
        x, y = arc(t, T_CRASH, T_LAND, BOX_ON_PED, BOX_FLOOR, 330)
        return x, y, 360 * eio(seg(t, T_CRASH, T_LAND)), 0, 1, 1
    if t < T_GRAB:
        x, y = BOX_FLOOR
        if T_LIFT0 <= t < T_LIFT1 + 0.25:
            p = seg(t, T_LIFT0, T_LIFT1)
            y -= 190 * math.sin(math.pi * p) if p < 1 else 0
        sx, sy = squash(t, T_LAND, 0.3, 0.12)
        if t >= T_LIFT1:
            sx, sy = squash(t, T_LIFT1, 0.25, 0.08)
        return x, y, 0, 0, sx, sy
    if t < T_FLIP:
        p = eio(seg(t, T_GRAB, T_FLIP))
        return lerp(BOX_FLOOR[0], 2290, p), lerp(BOX_FLOOR[1], 1230, p), 180 * p, 0, 1, 1
    if t < T_DROPTV + 0.05:
        k = t - T_FLIP
        fl = eout(seg(t, T_FLIP, T_FLIP + 0.2))
        return 2290 + 14 * math.sin(k * 55), 1230 + 10 * math.sin(k * 40), 180 + 4 * math.sin(k * 30), fl, 1, 1
    if t < T_TOSSLAND:
        x, y = arc(t, T_DROPTV + 0.05, T_TOSSLAND, (2290, 1230), BOX_FLOOR, 120)
        return x, y, lerp(180, 360, eio(seg(t, T_DROPTV + 0.05, T_TOSSLAND))), 1, 1, 1
    x, y = BOX_FLOOR
    sx, sy = squash(t, T_TOSSLAND, 0.3, 0.14)
    if t >= T_NIN:
        sx, sy = squash(t, T_NIN, 0.3, 0.16)
    hop_dx = 0.0
    hop_y = 0.0
    for th, dx in ((T_BHOP1, 70), (T_BHOP2, 70)):
        if t >= th:
            p = seg(t, th, th + 0.42)
            hop_dx += dx * eio(p)
            hop_y -= 90 * 4 * p * (1 - p)
            if p >= 1:
                a, b = squash(t, th + 0.42, 0.25, 0.14)
                sx, sy = sx * a, sy * b
    return x + hop_dx, y + hop_y + BH / 2 * (1 - sy), 0, 1, sx, sy


GXK = [(0, 298)]


def grumpo_state(t):
    g = dict(x=298, y=GY, ex="smug", look=(1, 0), rot=0.0, sx=1.0, sy=1.0, red=0.0, vis=True, in_cart=False)
    if t < T_SQUIRT:
        push = abs(math.sin(t * 5.2))
        g["x"] = 298 + 10 * push
        g["sx"], g["sy"] = 1 + 0.04 * push, 1 - 0.03 * push
        g["ex"] = "smug" if t < T_TICK else ("shock" if t < T_OPEN + 0.1 else "smug")
        g["look"] = (1, 0) if t < 0.9 else ((0.4, -1) if t < T_OPEN + 0.1 else (1, 0.3))
    elif t < T_FACE:
        p = seg(t, T_SQUIRT, T_FACE)
        g["x"] = lerp(308, 482, ein(p))
        g["rot"] = 24 * p
        g["ex"] = "shock"
        g["look"] = (1, 0.4)
    elif t < T_DROP:
        k = seg(t, T_FACE, T_DROP - 0.1)
        g["x"] = 482
        g["y"] = GY - 46 * eio(k)
        g["sx"], g["sy"] = 0.9 - 0.04 * k, 1.12 + 0.06 * k
        g["rot"] = 14
        g["ex"] = "shock"
        g["look"] = (1, -1)
    elif t < T_RUN:
        g["x"] = 482
        g["sx"], g["sy"] = squash(t, T_DROP, 0.3, 0.25)
        g["ex"] = "angry"
        g["red"] = 0.45 * seg(t, T_DROP + 0.05, T_DROP + 0.2)
        g["x"] += 5 * math.sin(t * 70)
        g["look"] = (1, 0)
    elif t < T_HOP:
        p = seg(t, T_RUN, T_HOP)
        g["x"] = lerp(482, 800, p)
        g["y"] = GY - abs(math.sin(p * math.pi * 3)) * 26
        g["rot"] = 10
        g["ex"] = "angry"
        g["red"] = 0.3 * (1 - p)
        g["look"] = (1, 0)
    elif t < T_CARTIN:
        x, y = arc(t, T_HOP, T_CARTIN, (800, GY), (900, CART_Y), 170)
        g["x"], g["y"] = x, y
        g["rot"] = 20 * seg(t, T_HOP, T_CARTIN)
        g["ex"] = "smug"
        g["look"] = (1, 0.5)
    elif t < T_CRASH:
        cx, spin, tilt, rolling = cart_state(t)
        g["in_cart"] = True
        g["x"], g["y"] = cx, CART_Y
        g["spin"] = spin
        if t < T_SIGN:
            g["ex"] = "smug"
            g["sx"], g["sy"] = squash(t, T_CARTIN, 0.3, 0.2)
            g["y"] -= abs(math.sin(t * 22)) * 4
            g["look"] = (1, 0) if t < T_PASS - 0.15 or t > T_PASS + 0.45 else (-1, 0.3)
        elif t < T_STOP:
            g["ex"] = "shock"
            g["look"] = (math.sin(t * 20), 0)
        elif t < T_HEAD:
            g["ex"] = "suspicious"
            g["look"] = (math.cos(t * 9), math.sin(t * 9))
        elif t < T_SEE:
            g["ex"] = "shock"
            g["sx"], g["sy"] = squash(t, T_HEAD, 0.35, 0.3)
            g["look"] = (math.cos(t * 9), math.sin(t * 9))
        elif t < T_PUSH:
            g["ex"] = "angry" if t > T_SEE + 0.2 else "shock"
            g["look"] = (1, -0.5)
            g["red"] = 0.5 * seg(t, T_SEE + 0.15, T_SEE + 0.4)
            g["x"] += 4 * math.sin(t * 70) * seg(t, T_SEE + 0.2, T_SEE + 0.3)
            k = seg(t, T_SEE + 0.2, T_PUSH)
            g["sx"], g["sy"] = 1 + 0.06 * k, 1 - 0.08 * k
        else:
            g["ex"] = "angry"
            g["red"] = 0.5
            g["look"] = (1, -0.3)
            g["rot"] = 8
    elif t < T_LAND:
        x, y = arc(t, T_CRASH, T_LAND, (1870, CART_Y), (2225, GY), 380)
        g["x"], g["y"] = x, y
        g["rot"] = 360 * eio(seg(t, T_CRASH, T_LAND))
        g["ex"] = "shock"
        g["red"] = 0.5 * (1 - seg(t, T_CRASH, T_CRASH + 0.4))
        g["look"] = (1, 0)
    else:
        g["x"] = 2225
        g["sx"], g["sy"] = squash(t, T_LAND, 0.3, 0.22)
        g["ex"] = pick(t, [(T_LAND, "angry"), (T_LIFT0, "angry"), (T_LIFT1, "shock"), (11.6, "suspicious"), (T_GRAB, "smug"),
                           (T_FLIP + 0.2, "suspicious"), (T_PALM, "shock"), (T_TVON, "suspicious"), (T_TAG0 + 0.6, "shock"),
                           (T_EYE, "suspicious"), (T_ANT + 0.15, "shock"), (T_ANT + 0.55, "grumpy"), (T_BHOP1 + 0.25, "angry"),
                           (T_DIE, "shock"), (T_SLUMP, "grumpy")], "angry")
        g["look"] = pick(t, [(T_LAND, (1, 0)), (T_LIFT1, (0.6, -1)), (11.6, (1, 0)), (T_GRAB, (0.6, -1)), (T_DROPTV, (0.5, 1)),
                             (T_PALM, (0.8, 0.6)), (T_TAG0, (1, 0.6)), (T_EYE, (1, 0)), (T_ANT + 0.15, (0.8, 1)),
                             (T_BHOP1 + 0.25, (1, 0)), (T_DIE - 0.2, (0.8, 0.6))], (1, 0))
        if T_LIFT0 <= t < T_LIFT0 + 0.2:
            k = seg(t, T_LIFT0, T_LIFT0 + 0.2)
            g["sx"], g["sy"] = 1 + 0.06 * k, 1 - 0.08 * k
            g["red"] = 0.25
        if T_LIFT0 + 0.2 <= t < T_LIFT1:
            g["y"] = GY - 30 * math.sin(math.pi * seg(t, T_LIFT0 + 0.2, T_LIFT1))
        if T_FLIP <= t < T_DROPTV:
            g["y"] = GY - abs(math.sin(t * 28)) * 8
        if T_ANT + 0.55 <= t < T_DIE:
            g["red"] = 0.35 * seg(t, T_ANT + 0.55, T_ANT + 0.9)
            if t >= T_BHOP1 + 0.25:
                g["red"] = 0.45
        if t >= T_SLUMP:
            k = eio(seg(t, T_SLUMP, T_SLUMP + 0.6))
            g["sx"], g["sy"] = 1 + 0.12 * k, 1 - 0.18 * k
            g["y"] = GY + 120 * 0.18 * k * GS
            g["red"] = 0.0
    return g


def nibbo_state(t):
    n = dict(x=508, y=NG, ex="nervous", rot=0.0, sx=1.0, sy=1.0, vis=True, in_box=False, in_bin=False)
    if t < T_SQUIRT:
        push = abs(math.sin(t * 5.2))
        n["sx"], n["sy"] = 0.82 - 0.05 * push, 1.14 + 0.05 * push
        n["y"] = NG - NR * (n["sy"] - 1)
        n["x"] = 600 - NR * n["sx"] - 2
        n["ex"] = "nervous" if t < T_TICK else "wow"
        if t > T_OPEN + 0.15:
            n["ex"] = "cool"
    elif t < 2.46:
        p = seg(t, T_SQUIRT, 2.46)
        n["x"] = lerp(510, 830, eout(p))
        n["sx"], n["sy"] = 1.7, 0.36
        n["y"] = FLOOR - NR * 0.36
        n["ex"] = "joy"
    elif t < T_PASS:
        n["sx"], n["sy"] = squash(t, 2.46, 0.3, -0.3)
        p = seg(t, 2.46, T_PASS)
        n["x"] = lerp(830, 1040, p)
        n["y"] = NG - abs(math.sin(p * math.pi * 5)) * 46
        n["ex"] = "joy"
        if t > T_RUN:
            n["ex"] = "happy"
        if T_HOP <= t < T_PASS:
            n["ex"] = "wow"
    elif t < 5.05:
        n["x"] = 1040
        n["rot"] = 360 * eout(seg(t, T_PASS, 5.0))
        n["ex"] = "dizzy" if t > 4.75 else "uhoh"
        n["x"] -= 30 * math.sin(math.pi * seg(t, T_PASS, 5.0))
    elif t < 5.55:
        p = seg(t, 5.05, 5.55)
        n["x"] = lerp(1040, 1100, p)
        n["y"] = NG - abs(math.sin(p * math.pi * 2)) * 30
        n["ex"] = "happy"
    elif t < T_BIN:
        x, y = arc(t, 5.55, T_BIN, (1100, NG), (BIN_X, BIN_TOP + 60), 200)
        n["x"], n["y"] = x, y
        n["ex"] = "joy"
        n["rot"] = 20 * seg(t, 5.55, T_BIN)
    elif t < T_LAUNCH:
        n["in_bin"] = True
        n["x"] = BIN_X
        k = seg(t, T_BIN, T_LAUNCH)
        n["y"] = BIN_TOP + 60 + 20 * math.sin(math.pi * k) + 8 * math.sin(t * 30)
        n["ex"] = "joy"
    elif t < T_HEAD:
        n["in_bin"] = t < T_LAUNCH + 0.12
        x, y = arc(t, T_LAUNCH, T_HEAD, (BIN_X, BIN_TOP + 40), (1640, CART_Y - 130 - NR + 6), 330)
        n["x"], n["y"] = x, y
        n["rot"] = 360 * seg(t, T_LAUNCH, T_HEAD)
        n["ex"] = "joy"
    elif t < T_BOXLAND:
        x, y = arc(t, T_HEAD, T_BOXLAND, (1640, CART_Y - 130 - NR + 6), (PED_X, PED_TOP - BH - NR), 300)
        n["x"], n["y"] = x, y
        n["rot"] = 360 * seg(t, T_HEAD, T_BOXLAND)
        n["sx"], n["sy"] = squash(t, T_HEAD, 0.2, 0.3)
        n["ex"] = "joy"
    elif t < T_CRASH:
        n["x"], n["y"] = PED_X, PED_TOP - BH - NR
        n["sx"], n["sy"] = squash(t, T_BOXLAND, 0.3, 0.25)
        n["y"] += NR * (1 - n["sy"])
        n["ex"] = "cool" if t < T_PUSH + 0.1 else "wow"
        if t < T_PUSH:
            n["rot"] = 8 * math.sin((t - T_BOXLAND) * 14)
    elif t < T_LAND:
        x, y = arc(t, T_CRASH, T_LAND, (PED_X, PED_TOP - BH - NR), (2705, NG), 420)
        n["x"], n["y"] = x, y
        n["rot"] = -360 * eio(seg(t, T_CRASH, T_LAND))
        n["ex"] = "uhoh"
    elif t < T_NJUMP:
        n["x"] = 2705
        n["sx"], n["sy"] = squash(t, T_LAND, 0.3, 0.22)
        n["ex"] = pick(t, [(T_LAND, "nervous"), (T_LIFT1, "wow"), (11.6, "uhoh"), (T_GRAB, "nervous"), (T_DROPTV, "wow"),
                           (T_TAG0, "uhoh"), (T_TAG1, "happy")], "nervous")
        if T_LIFT0 + 0.2 <= t < T_LIFT1:
            n["y"] = NG - 30 * math.sin(math.pi * seg(t, T_LIFT0 + 0.2, T_LIFT1))
        if t >= T_TAG1:
            n["rot"] = -10
    else:
        bx, by, br, bf, bsx, bsy = box_state(t)
        if t < T_NIN:
            x, y = arc(t, T_NJUMP, T_NIN, (2705, NG), (bx, by - 10), 260)
            n["x"], n["y"] = x, y
            n["rot"] = -30 * seg(t, T_NJUMP, T_NIN)
            n["ex"] = "joy"
            n["in_box"] = t > T_NIN - 0.12
        else:
            n["in_box"] = True
            pop = eout(seg(t, T_NIN + 0.15, T_NIN + 0.4))
            n["x"] = bx
            n["y"] = by - BH / 2 * bsy + 30 - 85 * pop
            n["ex"] = "joy" if t < T_DIE else "happy"
            n["rot"] = 8 * math.sin(t * 6)
    return n


# ---------------------------------------------------------------- camera
CK = [(0.0, (450, 1330, 1.5)), (1.5, (450, 1330, 1.5)), (2.0, (520, 1330, 1.45)), (2.5, (600, 1320, 1.4)),
      (3.2, (640, 1320, 1.4)), (3.9, (880, 1320, 1.38)), (5.0, (1240, 1320, 1.35)), (5.6, (1430, 1320, 1.35)),
      (6.6, (1450, 1300, 1.33)), (7.3, (1620, 1280, 1.33)), (8.1, (1880, 1290, 1.3)), (9.15, (2040, 1300, 1.33)),
      (10.0, (2450, 1340, 1.45)), (12.0, (2450, 1340, 1.45)), (12.4, (2390, 1300, 1.45)), (13.25, (2390, 1300, 1.45)),
      (13.6, (2290, 1500, 2.25)), (T_TAG0, (2290, 1500, 2.25)), (T_TAG0 + 0.45, (2550, 1545, 3.0)), (T_TAG1, (2550, 1545, 3.0)),
      (T_TAG1 + 0.35, (2300, 1500, 2.1)), (17.0, (2300, 1500, 2.1)), (17.45, (2410, 1400, 1.45)), (DUR, (2420, 1420, 1.52))]
SHAKES = [(T_FACE, 10, 0.25), (T_DROP, 8, 0.25), (T_SIGN, 8, 0.3), (T_HEAD, 6, 0.2), (T_CRASH, 24, 0.45), (T_LAND, 14, 0.3),
          (T_TOSSLAND, 6, 0.2)]


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
def draw_grumpo(ctx, g, t):
    return grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"],
                  False, 0, None, 0, t)


def tv_state(t, g):
    """tiny tv: (x, y, rot, s) or None"""
    if t < T_DROPTV:
        return None
    palm = (g["x"] + 148, g["y"] + 34)
    if t < T_PALM:
        x, y = arc(t, T_DROPTV, T_PALM, (2290, 1340), (palm[0], palm[1] - 30), -20)
        return x, y, 540 * seg(t, T_DROPTV, T_PALM), 1.0
    if T_EYE <= t < T_ANT + 0.5:
        p = eio(seg(t, T_EYE, T_EYE + 0.35)) * (1 - eio(seg(t, T_ANT + 0.25, T_ANT + 0.5)))
        ex = (g["x"] + 60, g["y"] + 2)
        return lerp(palm[0], ex[0] + 10, p), lerp(palm[1] - 30, ex[1], p), 0, 1 + 0.15 * p
    yy = palm[1] - 30
    if t >= T_SLUMP:
        yy += 18 * eio(seg(t, T_SLUMP, T_SLUMP + 0.6))
    return palm[0], yy, 0, 1.0


def frame(t):
    ctx = Ctx()
    L = [store_bg(t, ctx)]
    g = grumpo_state(t)
    n = nibbo_state(t)
    ink = mix_hex("#1a0a2e", "#3a0505", g["red"])
    gfill = mix_hex("#9466e0", "#ff6a52", g["red"])
    NB, NS = "#ffd23c", "#3d2a12"

    L.append(gate(t))
    L.append(clock(t))
    # props behind characters
    L.append(ball_bin_back())
    sign_rot, sign_x, sign_y = 0.0, SIGN_X, FLOOR
    if t >= T_SIGN:
        p = seg(t, T_SIGN, T_SIGN + 0.55)
        sign_x = lerp(SIGN_X, SIGN_X + 330, eout(p))
        sign_y = FLOOR - 220 * 4 * p * (1 - p)
        sign_rot = lerp(0, 450, p)
        if p >= 1:
            sign_rot = 450 + 8 * math.exp(-(t - T_SIGN - 0.55) * 8) * math.sin((t - T_SIGN) * 40)
    pedestal_svg = pedestal(t)
    L.append(pedestal_svg)

    # nibbo in bin (behind bin front)
    def draw_nibbo():
        return nibbo(ctx, n["x"], n["y"], NR, n["ex"], rot=n["rot"], sx=n["sx"], sy=n["sy"])

    if n["in_bin"]:
        L.append(draw_nibbo())
    L.append(ball_bin_front(t))
    L.append(flying_balls(t))

    # big box
    bx, by, br, bf, bsx, bsy = box_state(t)
    box_front_later = n["in_box"]
    if t < T_CRASH:
        L.append(shadow(bx, PED_TOP + 4, 130))
    elif t >= T_LAND:
        L.append(shadow(bx, FLOOR + 6, 140, 1 - cl((BOX_FLOOR[1] - by) / 400)))

    # nibbo (normal layer) before box when in box
    if n["in_box"]:
        L.append(shadow(bx, FLOOR + 6, 0))
        L.append(draw_nibbo())
        L.append(big_box(ctx, bx, by, br, bf, bsx, bsy))
    elif not (T_GRAB <= t < T_TOSSLAND):
        L.append(big_box(ctx, bx, by, br, bf, bsx, bsy))

    # wet sign
    L.append(wet_sign(sign_x, sign_y, sign_rot))

    # cart (behind grumpo) + grumpo + cart front
    cx_, spin, tilt, rolling = cart_state(t)
    L.append(shadow(cx_, FLOOR + 6, 170))
    if g["in_cart"]:
        L.append(f'<g transform="translate({cx_:.1f} 0) scale({spin:.3f} 1) translate({-cx_:.1f} 0)">')
    L.append(cart_back(cx_, 1.0 if g["in_cart"] else spin, tilt))
    if g["in_cart"]:
        gg = dict(g)
        L.append(f'<g transform="rotate({tilt:.1f} {cx_:.1f} {FLOOR-20})">{draw_grumpo(ctx, gg, t)}</g>')
        L.append(cart_front(cx_, 1.0, tilt, t, rolling))
        L.append('</g>')
    else:
        L.append(cart_front(cx_, spin, tilt, t, rolling))

    if not g["in_cart"]:
        air = max(0.0, (GY - g["y"]) / 400)
        L.append(shadow(g["x"], FLOOR + 6, 120, max(0.25, 1 - air)))
        L.append(draw_grumpo(ctx, g, t))

    # Grumpo arms
    sh_r = (g["x"] + 88, g["y"] - 20)
    sh_l = (g["x"] - 88, g["y"] - 20)
    if T_LAND <= t < T_GRAB:
        p1 = (bx - BW / 2 * bsx + 6, by - 30)
        p2 = (bx - BW / 2 * bsx + 6, by + 40)
        L.append(arm(sh_r[0], sh_r[1], p1[0], p1[1], ink, 12, 8) + hand(p1[0], p1[1], gfill, OL, 15))
        L.append(arm(g["x"] + 70, g["y"] + 50, p2[0], p2[1], ink, 12, 0) + hand(p2[0], p2[1], gfill, OL, 15))
    if T_GRAB <= t < T_DROPTV + 0.05:
        L.append(big_box(ctx, bx, by, br, bf, bsx, bsy))
        hy = by + 6
        lx = bx - BW / 2 + 4
        rx = bx + BW / 2 - 4
        L.append(arm(sh_l[0], sh_l[1] - 30, lx, hy, ink, 12, -20) + hand(lx, hy, gfill, OL, 15))
        L.append(arm(sh_r[0], sh_r[1] - 30, rx, hy, ink, 12, -20) + hand(rx, hy, gfill, OL, 15))
    if T_DROPTV + 0.05 <= t < T_TOSSLAND:
        L.append(big_box(ctx, bx, by, br, bf, bsx, bsy))
    tvs = tv_state(t, g)
    if t >= T_DROPTV + 0.05:
        palm = (g["x"] + 148, g["y"] + 34)
        if tvs and T_EYE <= t < T_ANT + 0.5:
            hp = (tvs[0], tvs[1] + 26)
        else:
            hp = palm
        L.append(arm(sh_r[0] - 10, sh_r[1] + 20, hp[0], hp[1], ink, 12, 20) + hand(hp[0], hp[1], gfill, OL, 15))
    if tvs:
        on = seg(t, T_TVON, T_TVON + 0.15)
        L.append(tiny_tv(tvs[0], tvs[1], tvs[3] * 1.3, tvs[2], on, t < T_ANT, t, dead=t >= T_DIE))
        if t >= T_ANT:
            k = t - T_ANT
            ay = tvs[1] - 26 + min(0.5 * 2600 * k * k, (FLOOR - 4) - (tvs[1] - 26))
            ax = tvs[0] + 8 + 60 * min(k, 0.4)
            L.append(antenna_piece(ax, ay, 200 * min(k, 0.5)))
    if g["in_cart"] and T_PUSH - 0.25 <= t < T_CRASH:
        L.append(speed_lines(g["x"] - 200, g["y"] + 40, 0, 0.9))
    if g["in_cart"] and T_CARTIN + 0.4 <= t < T_SIGN:
        L.append(speed_lines(g["x"] - 210, g["y"] + 60, 0, 0.8))

    # Nibbo
    if not n["in_bin"] and not n["in_box"]:
        air = max(0.0, (NG - n["y"]) / 400)
        L.append(shadow(n["x"], FLOOR + 6, 105, max(0.2, 1 - air)))
        L.append(draw_nibbo())
        if T_LAND <= t < T_GRAB:
            p1 = (bx + BW / 2 * bsx - 6, by - 20)
            p2 = (bx + BW / 2 * bsx - 6, by + 40)
            L.append(arm(n["x"] - 80, n["y"] - 40, p1[0], p1[1], NS, 10, 8) + hand(p1[0], p1[1], NB, NS, 12))
            L.append(arm(n["x"] - 90, n["y"] + 10, p2[0], p2[1], NS, 10, 0) + hand(p2[0], p2[1], NB, NS, 12))
    if n["ex"] == "nervous" and not n["in_box"]:
        L.append(sweat(n["x"] + 92 * n["sx"], n["y"] - 80 + 30 * ((t * 1.5) % 1)))
    if n["ex"] == "dizzy" or (n["ex"] == "uhoh" and T_PASS <= t < 5.05):
        for k in range(3):
            ang = -t * 5 + k * 2.1
            L.append(star_twinkle(n["x"] + 90 * math.cos(ang), n["y"] - 130 + 20 * math.sin(ang), 0.35 + 0.3 * ((t * 2 + k * 0.33) % 1)))
    if T_STOP - 0.3 <= t < T_SEE:
        for k in range(3):
            ang = t * 5 + k * 2.1
            L.append(star_twinkle(g["x"] + 95 * math.cos(ang), g["y"] - 150 + 22 * math.sin(ang), 0.35 + 0.3 * ((t * 2 + k * 0.33) % 1)))
    # draft swirl when cart passes Nibbo
    if T_PASS - 0.1 <= t < T_PASS + 0.5:
        p = seg(t, T_PASS - 0.1, T_PASS + 0.5)
        for k in range(3):
            L.append(f'<path d="M{1040 - 120 + k*20:.0f} {NG - 60 + k*50} q60 -40 120 0 q-60 40 -100 -10" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="{0.8*(1-p):.2f}" transform="rotate({p*200:.0f} 1040 {NG})"/>')

    # ---- effects
    L.append(symbol(n["x"] - 10, n["y"] - 170, "!", seg(t, T_TICK + 0.05, T_TICK + 0.6), "#3a7ad6") if t < 2.2 else "")
    L.append(symbol(g["x"] + 30, GY - 180, "!", seg(t, T_SQUIRT + 0.05, T_SQUIRT + 0.55)))
    L.append(impact(600, g["y"] - 10, seg(t, T_FACE, T_FACE + 0.22)))
    L.append(impact(g["x"], FLOOR - 10, seg(t, T_DROP, T_DROP + 0.25), "#ffffff"))
    L.append(impact(SIGN_X - 30, FLOOR - 120, seg(t, T_SIGN, T_SIGN + 0.25)))
    L.append(impact(1640, CART_Y - 140, seg(t, T_HEAD, T_HEAD + 0.22), "#ffffff"))
    L.append(impact(PED_X - PED_W / 2, FLOOR - 100, seg(t, T_CRASH, T_CRASH + 0.3)))
    L.append(symbol(g["x"] + 20, g["y"] - 190, "!", seg(t, T_SEE, T_SEE + 0.6)))
    L.append(symbol(g["x"] - 10, GY - 190, "?", seg(t, T_LIFT1 + 0.1, T_LIFT1 + 0.75), "#3a7ad6"))
    L.append(symbol(n["x"] + 10, NG - 180, "?", seg(t, T_LIFT1 + 0.2, T_LIFT1 + 0.85), "#3a7ad6"))
    L.append(symbol(g["x"] - 20, GY - 190, "!", seg(t, T_PALM + 0.05, T_PALM + 0.6)))
    L.append(symbol(n["x"] + 100, n["y"] - 140, "♥", seg(t, T_NIN + 0.4, T_NIN + 1.1), "#ff4d7a"))
    L.append(symbol(n["x"] + 110, n["y"] - 150, "♥", seg(t, T_BHOP2 + 0.3, T_BHOP2 + 1.0), "#ff4d7a"))
    if T_LAND + 0.15 <= t < T_LIFT0:
        # glare lightning between them
        p = (t * 12) % 1
        yy = 1520
        pts = " ".join(f"{lerp(2320, 2600, k/6):.0f},{yy + (18 if (k + int(t*12)) % 2 else -18)}" for k in range(7))
        L.append(f'<polyline points="{pts}" fill="none" stroke="#ffd23a" stroke-width="9" stroke-linejoin="round" opacity="{0.6+0.4*p:.2f}"/>')
    if T_FLIP <= t < T_DROPTV:
        for k in range(3):
            L.append(f'<path d="M{2140 + k*14} {1170 + k*40} q-20 10 0 20" stroke="#ffffff" stroke-width="6" fill="none" stroke-linecap="round"/>'
                     f'<path d="M{2440 - k*14} {1170 + k*40} q20 10 0 20" stroke="#ffffff" stroke-width="6" fill="none" stroke-linecap="round"/>')
    if T_ANT + 0.55 <= t < T_DIE and g["ex"] in ("grumpy", "angry"):
        L.append(f'<path d="M{g["x"]+70:.0f} {GY-110} l18 -8 l-6 18 M{g["x"]+88:.0f} {GY-92} l18 -8 l-6 18" stroke="#e8303a" stroke-width="6" fill="none" stroke-linecap="round"/>')
    if T_DROP + 0.05 <= t < T_RUN:
        L.append(f'<path d="M{g["x"]+70:.0f} {GY-110} l18 -8 l-6 18 M{g["x"]+88:.0f} {GY-92} l18 -8 l-6 18" stroke="#e8303a" stroke-width="6" fill="none" stroke-linecap="round"/>')
    if T_DIE <= t < T_DIE + 0.6 and tvs:
        L.append(f'<path d="M{tvs[0]-4:.0f} {tvs[1]-30:.0f} q-8 -16 4 -30 q10 -14 0 -30" stroke="#9a9aa8" stroke-width="5" fill="none" opacity="{1-seg(t, T_DIE, T_DIE+0.6):.2f}"/>')

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g></svg>')
    return overlay(svg, hook_title(t + 0.12, "Black Friday deal:", "90% OFF TV!"))


def build_sfx():
    # shoving at the shutter
    for k in range(3):
        sfx(0.05 + k * 0.6, "squish", 0.5, 1.1 + 0.05 * k)
    sfx(0.3, "strain", 0.4, 1.3)
    sfx(0.9, "grumble", 0.4, 1.1)
    for k in range(3):
        sfx(0.2 + k * 0.45, "click", 0.25, 1.6)
    sfx(T_TICK, "ding", 0.8, 1.2)
    sfx(T_TICK + 0.12, "ding", 0.6, 1.6)
    sfx(T_OPEN, "pipe_rattle", 0.7, 1.0)
    sfx(T_OPEN + 0.05, "creak", 0.6, 1.2)
    sfx(T_SQUIRT, "squeak_slide", 0.8, 1.2)
    sfx(T_SQUIRT + 0.02, "zip", 0.6, 1.4)
    sfx(2.46, "pop", 0.8, 1.1)
    sfx(T_SQUIRT + 0.1, "gasp", 0.5, 1.0)
    sfx(T_FACE, "bonk", 1.0, 0.9)
    sfx(T_FACE + 0.05, "clank", 0.5, 1.2)
    sfx(T_FACE + 0.1, "pipe_rattle", 0.6, 0.9)
    sfx(T_FACE + 0.15, "stretch", 0.5, 1.3)
    sfx(T_DROP, "thud", 0.9, 1.0)
    sfx(T_DROP + 0.1, "grumble", 0.7, 0.95)
    for k in range(5):
        sfx(2.6 + k * 0.33, "hop", 0.45, 1.35)
    for k in range(3):
        sfx(T_RUN + k * 0.17, "tiptoe", 0.5, 0.8)
    sfx(T_HOP, "boing", 0.6, 1.0)
    sfx(T_CARTIN, "clank", 0.8, 0.9)
    sfx(T_CARTIN + 0.02, "squeak", 0.4, 0.8)
    sfx(T_CARTIN + 0.1, "zoom", 0.7, 0.9)
    sfx(T_CARTIN + 0.2, "whirr", 0.5, 0.8)
    sfx(T_PASS - 0.05, "whoosh", 0.9, 1.0)
    sfx(T_PASS + 0.2, "slide_up", 0.4, 1.4)
    sfx(T_SIGN, "clank", 0.8, 1.2)
    sfx(T_SIGN, "splash_small", 0.7, 1.0)
    sfx(T_SIGN + 0.05, "squeak_slide", 0.8, 0.9)
    sfx(T_SIGN + 0.4, "squeak_slide", 0.6, 1.1)
    sfx(T_SIGN + 0.55, "clatter", 0.5, 1.4)
    sfx(T_SIGN + 0.1, "wobble", 0.5, 1.2)
    sfx(5.6, "hop", 0.4, 1.4)
    sfx(5.8, "whoosh", 0.4, 1.6)
    sfx(T_BIN, "splash", 0.5, 1.8)
    sfx(T_BIN, "clatter", 0.6, 1.6)
    sfx(T_LAUNCH, "boing", 0.9, 0.9)
    sfx(T_LAUNCH + 0.02, "clatter", 0.5, 1.7)
    sfx(T_STOP - 0.1, "blip_down", 0.3, 0.8)
    sfx(T_HEAD, "boing", 1.0, 1.3)
    sfx(T_HEAD, "bonk", 0.6, 1.3)
    sfx(T_BOXLAND, "thunk", 0.6, 1.4)
    sfx(T_BOXLAND + 0.15, "laugh", 0.5, 1.4)
    sfx(T_SEE, "alert", 0.5, 1.0)
    sfx(T_SEE + 0.2, "grumble", 0.7, 0.9)
    sfx(T_SEE + 0.25, "inhale", 0.4, 1.0)
    sfx(T_PUSH, "zoom", 0.8, 1.1)
    sfx(T_PUSH + 0.05, "whirr", 0.6, 1.1)
    sfx(T_CRASH, "crash_bush", 0.6, 0.8)
    sfx(T_CRASH, "bonk", 1.0, 0.75)
    sfx(T_CRASH + 0.02, "clank", 0.8, 0.8)
    sfx(T_CRASH + 0.08, "whoosh", 0.7, 0.9)
    sfx(T_CRASH + 0.1, "gasp", 0.5, 1.3)
    sfx(T_LAND, "thud", 1.0, 0.9)
    sfx(T_LAND + 0.03, "thud", 0.6, 1.2)
    sfx(T_LAND + 0.3, "grumble", 0.5, 1.0)
    sfx(T_LAND + 0.35, "suspense", 0.4, 1.0)
    sfx(T_LIFT0, "strain", 0.7, 1.0)
    sfx(T_LIFT0 + 0.2, "slide_up", 0.6, 1.2)
    sfx(T_LIFT1, "tap", 0.6, 1.4)
    sfx(T_LIFT1 + 0.08, "shaker", 0.25, 1.8)
    sfx(T_LIFT1 + 0.15, "blip", 0.4, 1.0)
    sfx(T_GRAB, "whoosh", 0.5, 1.3)
    sfx(T_FLIP, "pop", 0.5, 1.2)
    sfx(T_FLIP + 0.05, "shaker", 0.6, 1.4)
    sfx(T_DROPTV + 0.1, "slide_down", 0.4, 1.8)
    sfx(T_PALM, "tap", 0.7, 1.9)
    sfx(T_PALM + 0.02, "ding", 0.35, 2.2)
    sfx(T_TOSSLAND, "thunk", 0.5, 1.1)
    sfx(T_PALM + 0.1, "gasp", 0.5, 0.9)
    sfx(T_TVON, "blip", 0.5, 1.8)
    sfx(T_TVON + 0.05, "whirr", 0.2, 2.4)
    sfx(T_TAG0 + 0.4, "zip", 0.4, 1.2)
    sfx(T_TAG0 + 0.55, "alert", 0.5, 1.2)
    sfx(T_TAG1 - 0.2, "blip_down", 0.5, 0.8)
    sfx(T_EYE, "squeak", 0.4, 1.4)
    sfx(T_NJUMP, "hop", 0.6, 1.2)
    sfx(T_NIN, "plop", 0.7, 1.0)
    sfx(T_NIN + 0.3, "pop", 0.5, 1.3)
    sfx(T_NIN + 0.4, "laugh", 0.6, 1.3)
    sfx(T_ANT, "tap", 0.6, 2.2)
    sfx(T_ANT + 0.4, "tap", 0.4, 2.5)
    sfx(T_ANT + 0.55, "grumble", 0.7, 0.9)
    sfx(T_BHOP1, "boing", 0.6, 1.4)
    sfx(T_BHOP1 + 0.42, "thunk", 0.4, 1.5)
    sfx(T_BHOP2, "boing", 0.6, 1.5)
    sfx(T_BHOP2 + 0.42, "thunk", 0.4, 1.6)
    sfx(T_BHOP2 + 0.35, "ding", 0.4, 1.8)
    sfx(T_DIE, "blip_down", 0.7, 0.7)
    sfx(T_DIE + 0.05, "error_beep", 0.3, 0.9)
    sfx(T_SLUMP + 0.05, "slide_down", 0.5, 0.7)
    sfx(T_SLUMP + 0.3, "grumble", 0.6, 0.75)
