"""Grumpo & Nibbo — Episode 21: Only 1 Outlet (café, stealth / sneaking, 60 fps).

A cosy café. Both phones are at 1% (blinking red battery bubbles) and there is ONE working outlet: a pop-up
floor box between the tables (the two wall sockets are taped over with red X's).
  0. Both lunge with their plugs — the plugs clack together over the box; Grumpo belly-bumps Nibbo away,
     plugs in (bolt!), hops up and SITS on the outlet box, arms crossed. Guarded.
  1. Nibbo points at the ceiling; Grumpo looks up; Nibbo belly-slides at the box — without even looking,
     Grumpo spreads wide and Nibbo bonks off him, flipping onto his head.
  2. Nibbo swings his cable like a lasso and throws the plug at Grumpo's phone — Grumpo swats it back with
     the phone and the cable wraps Nibbo up like a spool; he topples over.
  3. Ding: Grumpo is at 100%. He pulls the phone off the cable but stays sitting on the outlet out of spite,
     giggling at videos. Nibbo wriggles free, gets an idea, tiptoes in under the raised phone and plugs his
     cable into GRUMPO'S PHONE. Energy flows: Grumpo's battery drains, Nibbo's fills. Grumpo notices, shakes
     and taps the phone... it dies (black screen). His eyes follow the cable down to a beaming Nibbo at 100%.
Grumpo jumps off the box to re-charge — while his back is turned Nibbo zips in, pulls Grumpo's plug, plugs
in his own and sits on the box, arms crossed, then takes a selfie with fuming Grumpo behind him (flash).
Ending: Nibbo wins. Structure: K stealth/sneaking. No counter.
"""
import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow
from hook import overlay, hook_title

W, H, FPS, DUR = 1080, 1920, 60, 23.6
GS = 0.92
GR = 130 * GS
NR = 112
FLOOR = 1700
GY = FLOOR - GR             # grumpo standing centre y
NY = FLOOR - NR
INK = "#1a0a2e"
GFILL = "#9466e0"
NB, NS = "#ffd23c", "#3d2a12"

BX = 1000                   # outlet floor box centre x
BOX_T = 1656                # box top y
SOCK = (BX, 1630)           # plug centre when plugged in (prongs down into the box)
GSEAT = 1640 - GR * 0.94    # grumpo sitting on the box
NSEAT = 1640 - NR * 0.94
GC_COL, NC_COL = "#b48cff", "#ffd84a"
LOOSE_G = (872, 1688)       # where grumpo's cable end lands after unplugging his phone
LOOSE_P = (1150, 1686)      # where grumpo's plug lands after nibbo yanks it

# ---- times
T_CLASH = 0.48
T_BUMP = 0.95
T_NLAND = 1.4
T_GPLUG = 1.22
T_HOP0, T_HOP1 = 1.32, 1.75
T_POINT0, T_POINT1 = 3.0, 3.35
T_LOOKUP = 3.45
T_SLIDE0, T_SLIDE1 = 3.6, 4.02
T_SPREAD0, T_SPREAD1 = 3.9, 4.05
T_BONK = 4.04
T_NBACK1 = 4.6
T_FLIP0, T_FLIP1 = 4.95, 5.2
T_SPIN0, T_SPIN1 = 5.75, 7.25
T_THROW1 = 7.58
T_SWAT = 7.58
T_RET1 = 7.9
T_WRAP1 = 8.6
T_TIP1 = 8.95
T_FULL = 9.5
T_UNPL0, T_UNPL1 = 9.75, 9.95
T_TOSS1 = 10.3
T_LAUGH0 = 10.5
T_FREE0, T_FREE1 = 10.1, 10.7
T_IDEA = 11.0
T_TIP0, T_TIPEND = 11.45, 12.85
T_REACH1 = 13.2
T_DRAIN0, T_DRAIN1 = 13.3, 17.0
T_NOTICE = 14.7
T_SHAKE0, T_SHAKE1 = 15.25, 15.95
T_TAP0, T_TAP1 = 16.0, 16.55
T_DEAD = 17.0
T_FOLLOW0, T_FOLLOW1 = 17.55, 18.05
T_SHOW = 18.1
T_NUNPL = 18.45
T_NHOP1 = 18.85
T_WAVE0, T_WAVE1 = 18.85, 19.3
T_JUMP0, T_JUMP1 = 19.3, 19.7
T_ZIP0, T_ZIP1 = 19.72, 19.95
T_YANK = 19.98
T_NPLUG = 20.12
T_NSIT0, T_NSIT1 = 20.15, 20.45
T_SCOOP0, T_SCOOP1 = 19.75, 20.1
T_RAISE1 = 20.45
T_CHECK = 20.6
T_LOOKCAB = 20.95
T_REALIZE = 21.4
T_SELFIE0, T_SELFIE1 = 21.9, 22.25
T_FLASH = 22.45

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


def squash(t, t0, d=0.3, a=0.22):
    k = t - t0
    if 0 <= k < d:
        s = math.sin(math.pi * k / d)
        return 1 + a * 0.6 * s, 1 - a * s
    return 1.0, 1.0


def arc(p, a, b, h):
    return lerp(a[0], b[0], p), lerp(a[1], b[1], p) - h * 4 * p * (1 - p)


def arm(x0, y0, x1, y1, col, w=12, sag=20):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    return f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


def hand(x, y, fill, stroke, r=15):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="5"/>'


def rotp(dx, dy, rot):
    a = math.radians(rot)
    return dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)


# ---------------------------------------------------------------- spline cable
def catmull(pts, n=10):
    if len(pts) < 2:
        return pts
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            u = k / n
            u2, u3 = u * u, u * u * u
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * u + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * u2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * u3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * u + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * u2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * u3)
            out.append((x, y))
    out.append(pts[-1])
    return out


def cable_svg(samples, col, w=9):
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in samples)
    return (f'<path d="{d}" fill="none" stroke="{OL}" stroke-width="{w+7}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


def along(samples, f):
    """point at fraction f of the polyline length."""
    L = [0.0]
    for a, b in zip(samples, samples[1:]):
        L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    tgt = f * L[-1]
    for i in range(1, len(L)):
        if L[i] >= tgt:
            q = (tgt - L[i - 1]) / max(1e-6, L[i] - L[i - 1])
            a, b = samples[i - 1], samples[i]
            return lerp(a[0], b[0], q), lerp(a[1], b[1], q)
    return samples[-1]


# ---------------------------------------------------------------- props
def plug(x, y, rot, col, s=1.0):
    """prongs point to local -y; cable exits at local +y (returned)."""
    svg = (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
           f'<rect x="-12" y="-44" width="7" height="22" rx="2" fill="#d8dde6" stroke="{OL}" stroke-width="3"/>'
           f'<rect x="5" y="-44" width="7" height="22" rx="2" fill="#d8dde6" stroke="{OL}" stroke-width="3"/>'
           f'<rect x="-21" y="-26" width="42" height="46" rx="9" fill="#f4f2f8" stroke="{OL}" stroke-width="5"/>'
           f'<rect x="-21" y="6" width="42" height="9" fill="{col}" stroke="{OL}" stroke-width="3"/>'
           f'<path d="M-13 -18 v14" stroke="#ffffff" stroke-width="5" stroke-linecap="round" opacity="0.9"/>'
           f'<path d="M-6 20 h12 l-3 10 h-6z" fill="#e0dde8" stroke="{OL}" stroke-width="3"/></g>')
    ex, ey = rotp(0, 30 * s, rot)
    return svg, (x + ex, y + ey)


def connector(x, y, rot, col):
    """small phone-end connector lying loose (tip points local -y). returns svg, cable point."""
    svg = (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">'
           f'<rect x="-6" y="-24" width="12" height="12" rx="3" fill="#cfd5de" stroke="{OL}" stroke-width="3"/>'
           f'<rect x="-11" y="-14" width="22" height="26" rx="6" fill="#f4f2f8" stroke="{OL}" stroke-width="4"/>'
           f'<rect x="-11" y="2" width="22" height="6" fill="{col}"/></g>')
    ex, ey = rotp(0, 12, rot)
    return svg, (x + ex, y + ey)


def phone(x, y, rot=0.0, state="on", t=0.0, s=1.0, back=False):
    """phone centred at (x,y). returns svg, port (bottom centre) world pos."""
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">',
         f'<rect x="-34" y="-60" width="68" height="120" rx="13" fill="#2b2a3c" stroke="{OL}" stroke-width="6"/>']
    if back:
        o.append(f'<rect x="-30" y="-56" width="60" height="112" rx="10" fill="#ff8fc0"/>'
                 f'<rect x="-24" y="-50" width="26" height="30" rx="8" fill="#2b2a3c"/><circle cx="-16" cy="-40" r="6" fill="#6a7aa8" stroke="#111" stroke-width="2"/>'
                 f'<circle cx="-4" cy="-28" r="4" fill="#fff6c0"/>')
    elif state == "dead":
        o.append(f'<rect x="-28" y="-52" width="56" height="102" rx="7" fill="#0b0b12"/>'
                 f'<path d="M-20 -40 L4 -48 L-20 20Z" fill="#ffffff" opacity="0.08"/>')
    else:
        o.append(f'<rect x="-28" y="-52" width="56" height="102" rx="7" fill="#7fd0ff"/>'
                 f'<rect x="-28" y="-52" width="56" height="16" fill="#ffffff" opacity="0.5"/>'
                 f'<rect x="-22" y="-30" width="44" height="34" rx="5" fill="#ff7aa8" stroke="{OL}" stroke-width="2.5"/>'
                 f'<path d="M-6 -22 l12 9 l-12 9z" fill="#ffffff"/>'
                 f'<rect x="-22" y="12" width="44" height="7" rx="3" fill="#ffffff" opacity="0.8"/>'
                 f'<rect x="-22" y="24" width="30" height="7" rx="3" fill="#ffffff" opacity="0.6"/>'
                 f'<path d="M-24 -50 L-10 -50 L-24 -20Z" fill="#ffffff" opacity="0.35"/>')
    o.append(f'<rect x="-9" y="52" width="18" height="4" rx="2" fill="#111"/></g>')
    px, py = rotp(0, 60 * s, rot)
    return "".join(o), (x + px, y + py)


def battery(x, y, lvl, charging, t, vis=1.0, sparkle=0.0, s=1.0):
    """battery status bubble. lvl 0..1."""
    if vis <= 0.01:
        return ""
    sc = s * vis
    if lvl < 0.15:
        col = "#ff3b3b"
    elif lvl < 0.45:
        col = "#ffc21a"
    else:
        col = "#4fd65a"
    blink = 1.0
    if lvl < 0.15 and not charging:
        blink = 0.35 + 0.65 * (0.5 + 0.5 * math.copysign(1, math.sin(t * 9)))
    fw = max(6, 104 * lvl)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) scale({sc:.3f})">',
         f'<ellipse cx="0" cy="0" rx="104" ry="66" fill="#ffffff" stroke="{OL}" stroke-width="7"/>',
         f'<path d="M-26 58 L-38 92 L4 62" fill="#ffffff" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>',
         f'<ellipse cx="0" cy="0" rx="100" ry="62" fill="#ffffff"/>',
         f'<rect x="-66" y="-32" width="120" height="64" rx="12" fill="#efeef4" stroke="{OL}" stroke-width="7"/>',
         f'<rect x="56" y="-14" width="14" height="28" rx="4" fill="{OL}"/>',
         f'<rect x="-58" y="-24" width="{fw:.1f}" height="48" rx="7" fill="{col}" opacity="{blink:.2f}"/>']
    if charging:
        pul = 1 + 0.12 * math.sin(t * 10)
        o.append(f'<g transform="scale({pul:.3f})"><path d="M6 -40 L-20 6 L-2 6 L-10 40 L22 -8 L2 -8 L12 -40Z" fill="#fff36a" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/></g>')
    if sparkle > 0:
        for k in range(8):
            a = math.radians(k * 45 + 10)
            r0, r1 = 110 + 20 * sparkle, 140 + 40 * sparkle
            o.append(f'<path d="M{r0*math.cos(a):.0f} {r0*math.sin(a)*0.7:.0f} L{r1*math.cos(a):.0f} {r1*math.sin(a)*0.7:.0f}" stroke="#ffe24a" stroke-width="9" stroke-linecap="round" opacity="{1-sparkle:.2f}"/>')
    o.append('</g>')
    return "".join(o)


def outlet_box(t, plugged=True):
    o = [shadow(BX, FLOOR + 4, 110),
         f'<path d="M{BX-74} {FLOOR} L{BX-62} {BOX_T} H{BX+62} L{BX+74} {FLOOR}Z" fill="#b9bfca" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>',
         f'<rect x="{BX-64}" y="{BOX_T-10}" width="128" height="14" rx="5" fill="#dde2ea" stroke="{OL}" stroke-width="5"/>',
         f'<path d="M{BX-52} {BOX_T+16} H{BX+52}" stroke="#ffffff" stroke-width="5" opacity="0.6" stroke-linecap="round"/>',
         f'<rect x="{BX-22}" y="{BOX_T-8}" width="44" height="8" rx="3" fill="#3a3448"/>']
    # little lightning icon on the front
    o.append(f'<path d="M{BX+4} {BOX_T+20} L{BX-8} {BOX_T+36} L{BX} {BOX_T+36} L{BX-4} {BOX_T+44} L{BX+10} {BOX_T+30} L{BX+2} {BOX_T+30}Z" fill="#ffd23a" stroke="{OL}" stroke-width="2.5"/>')
    return "".join(o)


def dead_outlet(x, y):
    """wall socket taped over with a red X."""
    return (f'<g transform="translate({x} {y})"><rect x="-34" y="-44" width="68" height="88" rx="10" fill="#f1ede4" stroke="{OL}" stroke-width="5"/>'
            f'<rect x="-8" y="-24" width="5" height="16" fill="#3a3448"/><rect x="5" y="-24" width="5" height="16" fill="#3a3448"/>'
            f'<rect x="-8" y="10" width="5" height="16" fill="#3a3448"/><rect x="5" y="10" width="5" height="16" fill="#3a3448"/>'
            f'<g transform="rotate(38)"><rect x="-50" y="-11" width="100" height="22" fill="#ff4a3a" stroke="{OL}" stroke-width="3" opacity="0.95"/></g>'
            f'<g transform="rotate(-38)"><rect x="-50" y="-11" width="100" height="22" fill="#ff4a3a" stroke="{OL}" stroke-width="3" opacity="0.95"/></g></g>')


def table(x, top, items):
    o = [shadow(x, FLOOR + 4, 120),
         f'<rect x="{x-12}" y="{top+10}" width="24" height="{FLOOR-top-24}" fill="#3a3448" stroke="{OL}" stroke-width="5"/>',
         f'<ellipse cx="{x}" cy="{FLOOR-8}" rx="70" ry="14" fill="#3a3448" stroke="{OL}" stroke-width="5"/>',
         items,
         f'<rect x="{x-125}" y="{top-6}" width="250" height="24" rx="10" fill="#c98a55" stroke="{OL}" stroke-width="6"/>',
         f'<path d="M{x-110} {top+2} H{x+60}" stroke="#e8b07a" stroke-width="6" stroke-linecap="round"/>']
    return "".join(o)


def mug(x, y, t):
    o = [f'<path d="M{x-30} {y-56} h60 l-6 56 h-48z" fill="#ffffff" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>',
         f'<path d="M{x+28} {y-46} q24 4 18 22 q-4 12 -22 8" fill="none" stroke="{OL}" stroke-width="5"/>',
         f'<rect x="{x-24}" y="{y-40}" width="48" height="12" fill="#6e4a8a" opacity="0.8"/>']
    for k in range(2):
        p = (t * 0.6 + k * 0.5) % 1
        o.append(f'<path d="M{x-8+k*16} {y-64-60*p:.0f} q-10 -14 0 -28" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="{0.6*(1-p):.2f}"/>')
    return "".join(o)


def croissant(x, y):
    return (f'<ellipse cx="{x}" cy="{y-6}" rx="56" ry="10" fill="#ffffff" stroke="{OL}" stroke-width="4"/>'
            f'<path d="M{x-44} {y-14} Q {x-40} {y-50} {x} {y-52} Q {x+40} {y-50} {x+44} {y-14} Q {x} {y-26} {x-44} {y-14}Z" fill="#f0a640" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M{x-20} {y-48} q6 12 0 26 M{x} {y-52} v28 M{x+20} {y-48} q-6 12 0 26" fill="none" stroke="#b86a1a" stroke-width="4" stroke-linecap="round"/>')


def iced(x, y):
    return (f'<path d="M{x-26} {y-90} h52 l-6 90 h-40z" fill="#cfeaff" fill-opacity="0.7" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M{x-23} {y-60} h46 l-4 58 h-38z" fill="#c8956a"/>'
            f'<rect x="{x-16}" y="{y-54}" width="14" height="14" rx="3" fill="#ffffff" opacity="0.7"/><rect x="{x+2}" y="{y-44}" width="13" height="13" rx="3" fill="#ffffff" opacity="0.7"/>'
            f'<path d="M{x+6} {y-90} L{x+22} {y-140} h12" fill="none" stroke="#ff5a7a" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{x+44}" cy="{y-10}" r="22" fill="#d89a5a" stroke="{OL}" stroke-width="4"/><circle cx="{x+38}" cy="{y-14}" r="4" fill="#5a3418"/><circle cx="{x+50}" cy="{y-4}" r="3.5" fill="#5a3418"/>')


def lamp(x, y, t):
    sw = 2 * math.sin(t * 1.3 + x)
    return (f'<g transform="rotate({sw:.2f} {x} -400)"><path d="M{x} -400 V{y-60}" stroke="{OL}" stroke-width="5"/>'
            f'<circle cx="{x}" cy="{y+10}" r="120" fill="#ffd98a" opacity="0.18"/>'
            f'<path d="M{x-70} {y} Q {x-60} {y-64} {x} {y-66} Q {x+60} {y-64} {x+70} {y}Z" fill="#e8a23a" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<path d="M{x-46} {y-30} q20 -24 46 -28" fill="none" stroke="#ffd27a" stroke-width="6" stroke-linecap="round"/>'
            f'<ellipse cx="{x}" cy="{y+4}" rx="30" ry="14" fill="#fff6c8" stroke="{OL}" stroke-width="4"/></g>')


def plant(x, s=1.0):
    o = [f'<path d="M{x-46*s} {FLOOR-110*s} h{92*s} l-{12*s} {110*s} h-{68*s}z" fill="#d8693a" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>',
         f'<rect x="{x-52*s}" y="{FLOOR-124*s}" width="{104*s}" height="{22*s}" rx="6" fill="#e8814e" stroke="{OL}" stroke-width="5"/>']
    for k, (a, L) in enumerate([(-60, 260), (-25, 330), (5, 360), (35, 300), (70, 240)]):
        r = math.radians(a - 90)
        ex, ey = x + L * s * math.cos(r), FLOOR - 120 * s + L * s * math.sin(r)
        o.append(f'<path d="M{x} {FLOOR-120*s} Q {(x+ex)/2+20*s} {(FLOOR-120*s+ey)/2} {ex:.0f} {ey:.0f}" fill="none" stroke="#2f7a3a" stroke-width="7"/>')
        o.append(f'<g transform="translate({ex:.0f} {ey:.0f}) rotate({a:.0f})"><path d="M0 0 C -60 -20 -60 -100 0 -130 C 60 -100 60 -20 0 0Z" fill="{"#4fae56" if k % 2 else "#3f9a4a"}" stroke="{OL}" stroke-width="5"/>'
                 f'<path d="M0 -10 V-110" stroke="#2f7a3a" stroke-width="4"/></g>')
    return "".join(o)


def room(t):
    o = [f'<defs><linearGradient id="osky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5db2f0"/><stop offset="1" stop-color="#c8ecff"/></linearGradient>'
         f'<radialGradient id="vig" cx="0.5" cy="0.55" r="0.78"><stop offset="0.6" stop-color="#1a0f20" stop-opacity="0"/><stop offset="1" stop-color="#1a0f20" stop-opacity="0.35"/></radialGradient>'
         f'<radialGradient id="glow"><stop offset="0" stop-color="#bff0ff" stop-opacity="0.7"/><stop offset="1" stop-color="#bff0ff" stop-opacity="0"/></radialGradient>'
         f'<clipPath id="wclip"><rect x="330" y="820" width="420" height="440"/></clipPath></defs>']
    o.append(f'<rect x="-900" y="-900" width="4200" height="{FLOOR+900}" fill="#2f6b70"/>')
    for x in range(-900, 3300, 110):
        o.append(f'<rect x="{x}" y="-900" width="50" height="{FLOOR+900}" fill="#33737a"/>')
    # window with street outside
    sky = [f'<rect x="330" y="820" width="420" height="440" fill="url(#osky)"/>',
           cloud_s(440, 880, t), cloud_s(660, 930, t + 3),
           '<rect x="330" y="1000" width="200" height="260" fill="#e0a878" stroke="#221c2e" stroke-width="4"/>',
           '<rect x="530" y="960" width="230" height="300" fill="#c9d3e8" stroke="#221c2e" stroke-width="4"/>']
    for wx in (360, 450):
        for wy in (1030, 1120):
            sky.append(f'<rect x="{wx}" y="{wy}" width="50" height="60" fill="#7fc4ef" stroke="#221c2e" stroke-width="3"/>')
    for wx in (560, 650):
        for wy in (990, 1080):
            sky.append(f'<rect x="{wx}" y="{wy}" width="56" height="64" fill="#ffe08a" stroke="#221c2e" stroke-width="3"/>')
    for k in range(5):
        sky.append(f'<path d="M{530+k*46} 1170 h46 v30 q-23 14 -46 0z" fill="{"#e84a4a" if k % 2 == 0 else "#ffffff"}" stroke="#221c2e" stroke-width="3"/>')
    sky.append('<circle cx="420" cy="1190" r="56" fill="#5aa957" stroke="#221c2e" stroke-width="4"/><rect x="414" y="1220" width="12" height="40" fill="#8a5a3a"/>')
    o.append(f'<g clip-path="url(#wclip)">{"".join(sky)}</g>')
    o.append(f'<rect x="322" y="812" width="436" height="456" rx="8" fill="none" stroke="#efe6d6" stroke-width="20"/>'
             f'<rect x="312" y="802" width="456" height="476" rx="10" fill="none" stroke="{OL}" stroke-width="6"/>'
             f'<path d="M540 812 V1268 M322 1040 H758" stroke="#efe6d6" stroke-width="14"/>'
             f'<rect x="300" y="1268" width="480" height="26" rx="6" fill="#efe6d6" stroke="{OL}" stroke-width="5"/>'
             f'<path d="M350 1250 L420 830" stroke="#ffffff" stroke-width="18" opacity="0.18"/>')
    # chalkboard menu (icons only)
    o.append(f'<rect x="1180" y="850" width="320" height="300" rx="10" fill="#b5642a" stroke="{OL}" stroke-width="6"/>'
             f'<rect x="1198" y="868" width="284" height="264" rx="6" fill="#24382e"/>'
             f'<g fill="none" stroke="#f4f0e0" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity="0.9">'
             f'<path d="M1222 900 h44 l-5 40 h-34z M1266 908 q16 2 12 16 q-3 8 -14 6"/><path d="M1236 892 q-6 -10 0 -18 M1252 892 q-6 -10 0 -18"/>'
             f'<path d="M1300 920 q40 -14 60 0 q40 -14 60 0 q10 4 30 0"/>'
             f'<path d="M1222 1000 Q 1228 970 1250 970 Q 1272 970 1278 1000 Q 1250 990 1222 1000Z"/>'
             f'<path d="M1300 990 q40 -14 60 0 q30 -10 50 0"/>'
             f'<path d="M1230 1062 h40 l-6 46 h-28z M1250 1062 l12 -24"/>'
             f'<path d="M1300 1080 q40 -14 60 0 q36 -12 70 0"/></g>'
             f'<circle cx="1452" cy="904" r="16" fill="none" stroke="#ffd23a" stroke-width="4"/><path d="M1446 904 h12 M1452 898 v12" stroke="#ffd23a" stroke-width="4"/>')
    # wainscot
    o.append(f'<rect x="-900" y="1390" width="4200" height="{FLOOR-1390}" fill="#7a4b33"/>')
    for x in range(-880, 3300, 190):
        o.append(f'<rect x="{x}" y="1420" width="160" height="{FLOOR-1450}" rx="8" fill="#85543a" stroke="#5e3826" stroke-width="4"/>')
    o.append(f'<rect x="-900" y="1372" width="4200" height="26" fill="#5e3826" stroke="{OL}" stroke-width="5"/>')
    o.append(dead_outlet(735, 1300) + dead_outlet(1290, 1300))
    # floor tiles
    o.append(f'<rect x="-900" y="{FLOOR}" width="4200" height="1100" fill="#d9ccb3"/>')
    for r, y in enumerate(range(FLOOR, FLOOR + 1100, 90)):
        for c, x in enumerate(range(-900, 3300, 90)):
            if (r + c) % 2 == 0:
                o.append(f'<rect x="{x}" y="{y}" width="90" height="90" fill="#bfa98a"/>')
    o.append(f'<path d="M-900 {FLOOR} H3300" stroke="{OL}" stroke-width="7"/>')
    o.append(lamp(640, 1030, t) + lamp(1360, 1000, t + 2))
    o.append(plant(210, 1.0) + plant(1760, 0.95))
    return "".join(o)


def cloud_s(x, y, t):
    x = x + 12 * math.sin(t * 0.3)
    return (f'<g fill="#ffffff"><circle cx="{x-30:.0f}" cy="{y}" r="26"/><circle cx="{x:.0f}" cy="{y-14}" r="32"/><circle cx="{x+34:.0f}" cy="{y}" r="24"/>'
            f'<rect x="{x-56:.0f}" y="{y}" width="114" height="22" rx="11"/></g>')


# ---------------------------------------------------------------- faces
def grumpo_extra(x, y, s, rot, sx, sy, kind, t, red=0.0):
    ink = mix_hex(INK, "#3a0505", red)
    base = mix_hex("#9466e0", "#ff6a52", red)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s*sx:.3f} {s*sy:.3f})">']
    worried = f'<path d="M-72 -28 Q -46 -36 -16 -54 M16 -54 Q 46 -36 72 -28" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
    if kind == "laugh":
        o.append(f'<ellipse cx="-38" cy="16" rx="24" ry="26" fill="{base}"/><ellipse cx="38" cy="16" rx="24" ry="26" fill="{base}"/>'
                 f'<path d="M-56 22 q18 -22 36 0 M20 22 q18 -22 36 0" fill="none" stroke="{ink}" stroke-width="9" stroke-linecap="round"/>'
                 f'<path d="M-72 -34 Q -44 -24 -16 -14 M72 -34 Q 44 -24 16 -14" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<path d="M-40 52 Q 0 {112+8*abs(math.sin(t*22)):.0f} 40 52Z" fill="#4a0a14" stroke="{ink}" stroke-width="8" stroke-linejoin="round"/>'
                 f'<path d="M-32 56 h64" stroke="#ffffff" stroke-width="9"/>')
    elif kind == "worried":
        o.append(worried + f'<path d="M-26 76 q8 -8 16 0 t16 0 t16 0" fill="none" stroke="{ink}" stroke-width="8" stroke-linecap="round"/>'
                 '<path d="M96 -40 q12 18 0 28 q-12 -10 0 -28z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3"/>')
    elif kind == "flat":
        o.append(f'<path d="M-72 -28 Q -44 -22 -16 -16 M72 -28 Q 44 -22 16 -16" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<path d="M-26 74 h52" stroke="{ink}" stroke-width="9" stroke-linecap="round"/>')
    elif kind == "twitch":
        tw = 6 * math.sin(t * 60)
        o.append(f'<path d="M-80 -40 L -20 {-6+tw:.1f} M80 -40 L 20 -6" fill="none" stroke="{ink}" stroke-width="20" stroke-linecap="round"/>'
                 f'<path d="M-40 70 q10 -10 20 0 q10 10 20 0 q10 -10 20 0 q10 10 20 0" fill="none" stroke="{ink}" stroke-width="9" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


def nib_face(x, y, r, rot, sx, sy, kind, look=(0, 0)):
    """custom Nibbo faces drawn over bloop(expr='none')."""
    f = r / 48 * 1.05
    d = "#2a1a10"
    lx, ly = look
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx*f:.3f} {sy*f:.3f})">']
    eyes = (f'<ellipse cx="{-14+lx*4:.1f}" cy="{-4+ly*3:.1f}" rx="6" ry="8" fill="{d}"/><ellipse cx="{14+lx*4:.1f}" cy="{-4+ly*3:.1f}" rx="6" ry="8" fill="{d}"/>'
            f'<circle cx="{-12+lx*4:.1f}" cy="{-7+ly*3:.1f}" r="2.2" fill="#fff"/><circle cx="{16+lx*4:.1f}" cy="{-7+ly*3:.1f}" r="2.2" fill="#fff"/>')
    if kind == "frown":      # determined
        o.append(eyes + f'<path d="M-24 -20 l14 6 M24 -20 l-14 6" stroke="{d}" stroke-width="4" stroke-linecap="round"/>'
                 f'<path d="M-8 16 q8 -5 16 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    elif kind == "sad":
        o.append(eyes + f'<path d="M-24 -16 l12 -5 M24 -16 l-12 -5" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<path d="M-8 18 q8 -7 16 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    elif kind == "sneak":
        o.append(eyes + f'<path d="M-10 13 q10 6 20 -2" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>'
                 f'<path d="M-22 -16 h14 M8 -16 h14" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>')
    elif kind == "wink":
        o.append(f'<ellipse cx="-14" cy="-4" rx="6" ry="8" fill="{d}"/><circle cx="-12" cy="-7" r="2.2" fill="#fff"/>'
                 f'<path d="M7 -3 q7 -8 14 0" fill="none" stroke="{d}" stroke-width="4.5" stroke-linecap="round"/>'
                 f'<path d="M-10 10 q10 12 20 0" fill="#7a2a1a" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>')
    elif kind == "smug":
        o.append(f'<path d="M-21 -4 h14 M7 -4 h14" stroke="{d}" stroke-width="5" stroke-linecap="round"/>'
                 f'<path d="M-21 -10 q7 -4 14 0 M7 -10 q7 -4 14 0" fill="none" stroke="{d}" stroke-width="3" stroke-linecap="round"/>'
                 f'<path d="M-8 12 q10 6 18 -4" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


def bulb(x, y, p):
    if p <= 0 or p >= 1:
        return ""
    sc = eback(min(1, p * 4)) if p < 0.8 else (1 - p) / 0.2
    o = [f'<g transform="translate({x:.1f} {y:.1f}) scale({max(0.01, sc):.3f})">']
    for k in range(7):
        a = math.radians(-90 + (k - 3) * 30)
        o.append(f'<path d="M{70*math.cos(a):.0f} {-10+70*math.sin(a):.0f} L{95*math.cos(a):.0f} {-10+95*math.sin(a):.0f}" stroke="#ffe24a" stroke-width="8" stroke-linecap="round"/>')
    o.append(f'<circle cx="0" cy="-10" r="44" fill="#fff36a" stroke="{OL}" stroke-width="6"/>'
             f'<rect x="-20" y="28" width="40" height="26" rx="5" fill="#b9bfca" stroke="{OL}" stroke-width="5"/>'
             f'<path d="M-12 -6 q6 -14 12 0 q6 -14 12 0" fill="none" stroke="#e8a23a" stroke-width="5"/>'
             f'<ellipse cx="-16" cy="-28" rx="9" ry="6" fill="#ffffff" opacity="0.8"/></g>')
    return "".join(o)


# ---------------------------------------------------------------- battery levels
def g_level(t):
    if t < T_GPLUG:
        return 0.02
    if t < T_DRAIN0:
        return lerp(0.02, 1.0, cl((t - T_GPLUG) / (T_FULL - T_GPLUG)))
    return lerp(1.0, 0.0, eio(seg(t, T_DRAIN0, T_DRAIN1)))


def n_level(t):
    if t < T_DRAIN0:
        return 0.02
    return lerp(0.02, 1.0, eio(seg(t, T_DRAIN0, T_DRAIN1)))


# ---------------------------------------------------------------- grumpo
def grumpo_state(t):
    g = dict(x=700.0, y=GY, ex="angry", kind=None, sx=1.0, sy=1.0, rot=0.0, look=(1, 0.4), red=0.0,
             phone=None, phone_rot=0.0, plug=None, other=None, seated=False)
    if t < T_CLASH:
        p = eout(seg(t, 0, T_CLASH - 0.05))
        g["x"] = lerp(770, 862, p)
        g["y"] = GY - 30 * abs(math.sin(p * math.pi * 2))
        g["rot"] = 12 * p
        g["plug"] = (lerp(g["x"] + 120, 978, p), lerp(GY - 40, 1580, p))
        g["phone"] = (g["x"] - 130, g["y"] - 10)
        return g
    if t < T_BUMP:
        j = 5 * math.sin(t * 70)
        g["x"] = 862 + j
        g["rot"] = 10 + 3 * math.sin(t * 50)
        g["plug"] = (980 + j * 0.6, 1580 + 3 * math.sin(t * 60))
        g["phone"] = (g["x"] - 130, g["y"] - 10)
        g["red"] = 0.3 * seg(t, T_CLASH, T_BUMP)
        return g
    if t < T_HOP0:
        p = eback(seg(t, T_BUMP, T_BUMP + 0.13))
        g["x"] = lerp(862, 900, p)
        a, b = squash(t, T_BUMP, 0.25, 0.2)
        g["sx"], g["sy"] = b, a
        g["rot"] = lerp(10, 0, seg(t, T_BUMP, T_BUMP + 0.2))
        g["ex"] = "angry" if t < T_GPLUG else "smug"
        g["red"] = 0.3 * (1 - seg(t, T_BUMP, T_GPLUG))
        q = eio(seg(t, T_BUMP + 0.05, T_GPLUG))
        g["plug"] = (lerp(980, SOCK[0], q), lerp(1580, SOCK[1], q)) if t < T_GPLUG else None
        g["phone"] = (g["x"] - 130, g["y"] - 10)
        g["other"] = (SOCK[0] - 20, SOCK[1] - 30) if t >= T_GPLUG - 0.05 else None
        g["look"] = (1, 1) if t < T_GPLUG + 0.05 else (1, 0)
        return g
    if t < T_HOP1:
        p = seg(t, T_HOP0, T_HOP1)
        g["x"], g["y"] = arc(eio(p), (900, GY), (BX, GSEAT), 110)
        g["rot"] = 20 * math.sin(math.pi * p)
        g["ex"] = "smug"
        g["look"] = (1, 0)
        g["phone"] = (lerp(g["x"] - 130, g["x"] + 132, eio(p)), g["y"] - 30)
        return g
    if t < T_JUMP0:
        g["x"], g["y"] = BX, GSEAT
        g["seated"] = True
        a, b = squash(t, T_HOP1, 0.3, 0.2)
        g["sx"], g["sy"] = 1.03 * a, 0.94 * b
        g["ex"] = "smug"
        g["look"] = (1, 0.2)
        ph = (g["x"] + 132, g["y"] - 30)
        prot = 0.0
        other = (g["x"] - 118, g["y"] + 50)     # left hand resting
        if T_LOOKUP <= t < 4.4:
            g["ex"] = "blank"
            g["look"] = (-0.4, -1)
        if T_SPREAD0 <= t < 4.5:
            k = eio(seg(t, T_SPREAD0, T_SPREAD1)) * (1 - eio(seg(t, 4.3, 4.5)))
            g["sx"] *= 1 + 0.3 * k
            g["sy"] *= 1 - 0.14 * k
            g["y"] += GR * 0.14 * k * 0.9
        if 4.4 <= t < T_SPIN0:
            g["ex"] = "smug"
            g["look"] = (1, 0.6)
        if T_SPIN0 <= t < T_SWAT:
            g["ex"] = "suspicious"
            g["look"] = (1, -0.6)
        if T_SWAT - 0.12 <= t < T_SWAT + 0.3:
            p = seg(t, T_SWAT - 0.12, T_SWAT + 0.3)
            w = math.sin(math.pi * p)
            ph = (g["x"] + 132 + 50 * w, g["y"] - 30 - 90 * w)
            prot = 60 * w
            g["ex"] = "angry"
            g["look"] = (1, -0.4)
        if T_SWAT + 0.3 <= t < T_FULL:
            g["ex"] = "smug"
            g["look"] = (1, 0.4)
            if 8.1 <= t < 8.7:   # blows on the phone like a smoking gun
                ph = (g["x"] + 110, g["y"] - 70)
                prot = -30
                g["look"] = (1, -0.4)
        if T_FULL <= t < T_UNPL0:
            g["ex"] = "smug"
            g["look"] = (0.6, -0.6)
        if T_UNPL0 <= t < T_LAUGH0:
            p = eback(seg(t, T_UNPL0, T_UNPL1))
            ph = (g["x"] + 132, g["y"] - 30 - 50 * p)
            g["ex"] = "smug"
            g["look"] = (1, -0.2)
        if T_LAUGH0 <= t:
            ph = (g["x"] + 135, g["y"] - 70)
        if T_LAUGH0 <= t < T_NOTICE:
            g["ex"] = "blank"
            g["kind"] = "laugh"
            g["y"] -= 6 * abs(math.sin(t * 16))
            g["rot"] = 3 * math.sin(t * 16)
            other = (g["x"] - 120, g["y"] + 30 + 8 * math.sin(t * 16))
        if T_NOTICE <= t < T_DEAD:
            g["ex"] = "blank"
            g["kind"] = "flat" if t < T_SHAKE0 else "worried"
            g["look"] = (1, -0.5)
            if T_SHAKE0 <= t < T_SHAKE1:
                prot = 20 * math.sin(t * 40)
                ph = (ph[0] + 8 * math.sin(t * 40), ph[1])
            if T_TAP0 <= t < T_TAP1:
                k = abs(math.sin((t - T_TAP0) * math.pi / 0.18))
                other = (ph[0] - 50 + 30 * k, ph[1] - 10)
        if T_DEAD <= t:
            g["ex"] = "shock"
            g["kind"] = None
            g["look"] = (1, -0.6)
            a, b = squash(t, T_DEAD, 0.3, 0.12)
            g["sx"], g["sy"] = g["sx"] * b, g["sy"] * a
            if t >= T_FOLLOW0:
                q = eio(seg(t, T_FOLLOW0, T_FOLLOW1))
                g["look"] = (1, lerp(-0.6, 1, q))
                g["ex"] = "blank"
            if t >= T_SHOW + 0.15:
                g["ex"] = "angry"
                g["look"] = (1, 0.8)
                g["red"] = 0.55 * seg(t, T_SHOW + 0.15, T_JUMP0)
        g["phone"] = ph
        g["phone_rot"] = prot
        g["other"] = other
        return g
    # jumped off to the left
    if t < T_JUMP1:
        p = seg(t, T_JUMP0, T_JUMP1)
        g["x"], g["y"] = arc(eio(p), (BX, GSEAT), (745, GY), 120)
        g["rot"] = -25 * math.sin(math.pi * p)
        g["ex"] = "angry"
        g["red"] = 0.55
        g["look"] = (-1, 0.6)
        g["phone"] = (g["x"] + 132, g["y"] - 30)
        return g
    g["x"], g["y"] = 745, GY
    a, b = squash(t, T_JUMP1, 0.3, 0.18)
    g["sx"], g["sy"] = b, a
    g["red"] = 0.55
    g["ex"] = "angry"
    ph = (g["x"] + 132, g["y"] - 30)
    if t < T_RAISE1:
        if t < T_SCOOP1:
            q = eio(seg(t, T_SCOOP0, T_SCOOP1))
            ph = (lerp(g["x"] + 132, LOOSE_G[0] + 2, q), lerp(g["y"] - 30, LOOSE_G[1] - 70, q))
            g["rot"] = 18 * q
        else:
            q = eio(seg(t, T_SCOOP1 + 0.05, T_RAISE1))
            ph = (lerp(LOOSE_G[0] + 2, g["x"] + 132, q), lerp(LOOSE_G[1] - 70, g["y"] - 30, q))
            g["rot"] = 18 * (1 - q)
        g["look"] = (1, 1)
    else:
        g["red"] = lerp(0.55, 0.2, seg(t, T_RAISE1, T_CHECK))
        g["ex"] = "suspicious"
        g["look"] = (1, -0.3)
        if t >= T_CHECK + 0.2:
            g["ex"] = "blank"
            g["kind"] = "flat"
        if t >= T_LOOKCAB:
            q = eio(seg(t, T_LOOKCAB, T_LOOKCAB + 0.35))
            g["look"] = (1, lerp(-0.3, 1, q))
        if t >= T_REALIZE:
            g["ex"] = "shock"
            g["kind"] = None
            g["look"] = (1, 0)
            a, b = squash(t, T_REALIZE, 0.3, 0.14)
            g["sx"], g["sy"] = b, a
        if t >= T_REALIZE + 0.5:
            g["ex"] = "blank"
            g["kind"] = "twitch"
            g["red"] = lerp(0.2, 0.75, seg(t, T_REALIZE + 0.5, T_FLASH))
            g["rot"] = 2.5 * math.sin(t * 45)
            g["look"] = (1, 0.1)
    g["phone"] = ph
    g["phone_rot"] = 0.0
    g["other"] = (g["x"] - 118, g["y"] + 40)
    return g


# ---------------------------------------------------------------- nibbo
def nibbo_state(t):
    n = dict(x=1360.0, y=NY, rot=0.0, sx=1.0, sy=1.0, face="frown", ex="none", look=(0, 0),
             phone=None, phone_rot=0.0, plug=None, plug_rot=180.0, wrap=0.0, sit=False, back=False)
    if t < T_CLASH:
        p = eout(seg(t, 0, T_CLASH - 0.05))
        n["x"] = lerp(1250, 1140, p)
        n["y"] = NY - 34 * abs(math.sin(p * math.pi * 2))
        n["rot"] = -12 * p
        n["plug"] = (lerp(n["x"] - 110, 1022, p), lerp(NY - 40, 1580, p))
        n["phone"] = (n["x"] + 122, n["y"] - 10)
        n["look"] = (-1, 0.6)
        return n
    if t < T_BUMP:
        j = 5 * math.sin(t * 70 + 1)
        n["x"] = 1140 + j
        n["rot"] = -10 - 3 * math.sin(t * 50)
        n["plug"] = (1020 + j * 0.6, 1580 + 3 * math.sin(t * 60 + 1))
        n["phone"] = (n["x"] + 122, n["y"] - 10)
        n["look"] = (-1, 0.6)
        return n
    if t < T_NLAND:
        p = seg(t, T_BUMP, T_NLAND)
        n["x"], n["y"] = arc(eout(p), (1140, NY), (1340, NY), 150)
        n["rot"] = 360 * eout(p)
        n["face"], n["ex"] = None, "wow"
        n["phone"] = (n["x"] + 122, n["y"] - 10)
        n["plug"] = (n["x"] - 120, n["y"] + 20)
        n["plug_rot"] = 200
        return n
    n["x"] = 1340
    a, b = squash(t, T_NLAND, 0.3, 0.2)
    n["sx"], n["sy"] = a, b
    n["phone"] = (n["x"] + 122, n["y"] - 10)
    n["plug"] = (n["x"] - 118, n["y"] + 30)
    n["plug_rot"] = 200
    if t < 1.95:
        n["face"], n["ex"] = None, "dizzy"
        n["rot"] = 8 * math.sin(t * 14)
    elif t < T_POINT0:
        n["face"] = "sad"
        n["look"] = (0.6, -0.4)
        n["phone"] = (n["x"] + 110, n["y"] - 70)
    if T_POINT0 <= t < T_SLIDE0:
        n["face"], n["ex"] = None, "wow"
        n["look"] = (-1, -1)
        n["point"] = eback(seg(t, T_POINT0, T_POINT1))
        if t >= T_LOOKUP + 0.05:
            n["face"], n["ex"] = "sneak", "none"
            n["look"] = (-1, 0.3)
    if T_SLIDE0 <= t < T_BONK:
        p = eio(seg(t, T_SLIDE0, T_SLIDE1))
        n["x"] = lerp(1340, 1124, p)
        k = min(1, seg(t, T_SLIDE0, T_SLIDE0 + 0.12))
        n["sx"], n["sy"] = 1 + 0.35 * k, 1 - 0.36 * k
        n["face"] = "frown"
        n["look"] = (-1, 0.3)
        n["plug"] = (n["x"] - 150, FLOOR - 38)
        n["plug_rot"] = -90
        n["phone"] = (n["x"] + 125, FLOOR - 40)
        n["phone_rot"] = 90
        n["slide"] = True
    if T_BONK <= t < T_NBACK1:
        p = seg(t, T_BONK, T_NBACK1)
        n["x"], n["y"] = arc(eout(p), (1124, NY), (1340, NY), 140)
        n["rot"] = 180 * eout(p)
        c = 1 - seg(t, T_BONK, T_BONK + 0.12)
        n["sx"], n["sy"] = 1 - 0.3 * c, 1 + 0.2 * c
        n["face"], n["ex"] = None, "dizzy"
        n["phone"] = (n["x"] + 122, n["y"] - 10)
    if T_NBACK1 <= t < T_FLIP1:
        n["rot"] = 180 if t < T_FLIP0 else lerp(180, 360, eio(seg(t, T_FLIP0, T_FLIP1)))
        n["y"] = NY
        n["face"], n["ex"] = None, "dizzy"
        a, b = squash(t, T_NBACK1, 0.3, 0.2)
        n["sx"], n["sy"] = a, b
        n["rot"] += 6 * math.sin(t * 20) * (t < T_FLIP0)
    if T_FLIP1 <= t < T_SPIN0:
        n["face"] = "frown"
        n["look"] = (-1, 0)
        n["x"] = lerp(1340, 1380, eio(seg(t, T_FLIP1, T_SPIN0)))
        n["y"] = NY - 20 * abs(math.sin(math.pi * seg(t, T_FLIP1, T_SPIN0)))
    if T_SPIN0 <= t < T_RET1:
        n["x"] = 1380
        n["face"] = "frown"
        n["look"] = (-1, -0.6)
        n["lasso"] = True
    if T_RET1 <= t < T_FREE1:
        n["x"] = 1380
        n["face"], n["ex"] = None, "dizzy"
        n["phone"] = None
        n["plug"] = None
        if t < T_WRAP1:
            p = seg(t, T_RET1, T_WRAP1)
            n["rot"] = 720 * eout(p)
            n["wrap"] = min(1, p * 1.3)
        elif t < T_TIP1:
            p = eio(seg(t, T_WRAP1, T_TIP1))
            n["rot"] = 720 + 95 * p
            n["y"] = NY + 4 * p
            n["wrap"] = 1
            n["sx"], n["sy"] = 1.0, 1.0
        elif t < T_FREE0:
            n["rot"] = 815 + 4 * math.sin(t * 24)
            n["wrap"] = 1
            n["sx"], n["sy"] = squash(t, T_TIP1, 0.25, 0.15)
        else:
            p = seg(t, T_FREE0, T_FREE1)
            n["rot"] = lerp(815, 1080 + 360, eout(p))
            n["y"] = NY - 60 * math.sin(math.pi * p)
            n["wrap"] = 1 - eout(p)
    if T_FREE1 <= t < T_TIP0:
        n["x"] = 1380
        a, b = squash(t, T_FREE1, 0.3, 0.2)
        n["sx"], n["sy"] = a, b
        n["face"], n["ex"] = None, "dizzy"
        if t >= T_FREE1 + 0.25:
            n["face"], n["ex"] = "sad", "none"
            n["look"] = (-1, -0.3)
        if t >= T_IDEA:
            n["face"], n["ex"] = None, "joy"
    if T_TIP0 <= t < T_SHOW:
        p = seg(t, T_TIP0, T_TIPEND)
        steps = 5
        k = p * steps
        f = k - int(min(k, steps - 0.001))
        n["x"] = lerp(1380, 1222, eio(p))
        crouch = min(1, seg(t, T_TIP0, T_TIP0 + 0.3))
        n["sy"] = 1 - 0.16 * crouch
        n["sx"] = 1 + 0.06 * crouch
        n["y"] = FLOOR - NR * n["sy"] - (14 * math.sin(math.pi * f) if p < 1 else 0)
        n["face"] = "sneak"
        n["look"] = (-1, -0.6)
        n["phone"] = (n["x"] + 120, n["y"] + 10)
        n["phone_rot"] = 10
        n["plug"] = (n["x"] - 125, n["y"] + 20)
        n["plug_rot"] = 0
        if t >= T_TIPEND:
            n["reach"] = eio(seg(t, T_TIPEND, T_REACH1))
        if T_NOTICE <= t < T_DEAD:
            n["face"], n["ex"] = None, "nervous"
        if t >= T_DEAD:
            n["face"] = "sneak"
            n["look"] = (-1, -1)
    if T_SHOW <= t < T_ZIP0:
        n["face"], n["ex"] = None, "joy"
        n["sy"], n["sx"] = 0.84, 1.06
        n["x"] = 1222
        n["y"] = FLOOR - NR * n["sy"]
        up = eback(seg(t, T_SHOW, T_SHOW + 0.25))
        n["phone"] = (n["x"] + 120 + 10 * up, n["y"] + 10 - 140 * up)
        n["phone_rot"] = 10 - 10 * up
        n["plug"] = (n["x"] - 125, n["y"] + 20)
        n["plug_rot"] = 0
        if t >= T_NUNPL:
            p = seg(t, T_NUNPL, T_NHOP1)
            n["x"], n["y"] = arc(eio(p), (1222, FLOOR - NR * 0.84), (1350, NY), 70)
            n["sy"], n["sx"] = lerp(0.84, 1, p), lerp(1.06, 1, p)
            n["phone"] = (n["x"] + 120, n["y"] - 110)
            n["plug"] = (n["x"] - 120, n["y"] + 30)
            n["plug_rot"] = 200
        if t >= T_NHOP1:
            n["face"] = "wink"
            n["ex"] = "none"
            a, b = squash(t, T_NHOP1, 0.25, 0.15)
            n["sx"], n["sy"] = a, b
            n["wave"] = seg(t, T_WAVE0, T_WAVE1 + 0.2)
            n["phone"] = (n["x"] + 122, n["y"] - 10)
    if T_ZIP0 <= t < T_NSIT0:
        p = eio(seg(t, T_ZIP0, T_ZIP1))
        n["x"] = lerp(1350, 1095, p)
        n["y"] = NY
        n["sx"], n["sy"] = (1.2, 0.86) if t < T_ZIP1 else (1, 1)
        n["face"] = "frown"
        n["look"] = (-1, 0.8)
        n["phone"] = (n["x"] + 122, n["y"] - 10)
        if t < T_NPLUG:
            q = eio(seg(t, T_YANK, T_NPLUG))
            n["plug"] = (lerp(n["x"] - 120, SOCK[0], q), lerp(n["y"] + 20, SOCK[1], q))
            n["plug_rot"] = lerp(200, 180, q)
        else:
            n["plug"] = SOCK
            n["plug_rot"] = 180
        n["zip"] = t < T_ZIP1 + 0.05
    if t >= T_NSIT0:
        p = seg(t, T_NSIT0, T_NSIT1)
        if t < T_NSIT1:
            n["x"], n["y"] = arc(eio(p), (1095, NY), (BX + 4, NSEAT), 90)
            n["rot"] = 15 * math.sin(math.pi * p)
        else:
            n["x"], n["y"] = BX + 4, NSEAT
            a, b = squash(t, T_NSIT1, 0.3, 0.2)
            n["sx"], n["sy"] = 1.03 * a, 0.94 * b
        n["sit"] = True
        n["face"] = "smug"
        n["plug"] = SOCK
        n["plug_rot"] = 180
        n["phone"] = (n["x"] + 122, n["y"] - 20)
        if t >= T_REALIZE:
            n["face"] = "wink"
        if t >= T_SELFIE0:
            q = eback(seg(t, T_SELFIE0, T_SELFIE1))
            n["phone"] = (lerp(n["x"] + 122, n["x"] + 40, q), lerp(n["y"] - 20, n["y"] - 210, q))
            n["back"] = q > 0.5
            n["face"], n["ex"] = None, "joy"
            n["look"] = (0.3, -1)
    return n


# ---------------------------------------------------------------- camera
CK = [(0.0, (1010, 1540, 1.4)), (0.5, (1000, 1550, 1.55)), (0.95, (1000, 1550, 1.58)), (1.5, (1090, 1530, 1.45)),
      (2.0, (1160, 1530, 1.5)), (3.0, (1170, 1530, 1.5)), (3.6, (1150, 1540, 1.5)), (4.05, (1120, 1550, 1.6)),
      (4.7, (1170, 1540, 1.5)), (5.6, (1190, 1510, 1.42)), (7.25, (1190, 1510, 1.42)), (7.6, (1150, 1520, 1.45)),
      (8.2, (1200, 1540, 1.55)), (9.2, (1200, 1540, 1.52)), (9.55, (1020, 1520, 1.75)), (10.4, (1060, 1520, 1.65)),
      (11.0, (1220, 1530, 1.55)), (12.3, (1160, 1540, 1.6)), (13.3, (1120, 1530, 1.72)), (14.6, (1110, 1520, 1.72)),
      (15.4, (1090, 1510, 1.82)), (T_DEAD, (1080, 1510, 1.9)), (T_FOLLOW1, (1140, 1540, 1.75)), (T_SHOW + 0.3, (1160, 1540, 1.65)),
      (19.2, (1150, 1540, 1.5)), (19.75, (980, 1540, 1.45)), (20.5, (930, 1530, 1.48)), (21.3, (905, 1530, 1.52)),
      (DUR, (900, 1525, 1.6))]
SHAKES = [(T_CLASH, 6, 0.25), (T_BUMP, 8, 0.25), (T_HOP1, 7, 0.25), (T_BONK, 9, 0.3), (T_SWAT, 6, 0.2),
          (T_TIP1, 6, 0.25), (T_DEAD, 6, 0.3), (T_JUMP1, 8, 0.25), (T_NSIT1, 6, 0.2), (T_REALIZE, 7, 0.3)]


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
    cy -= 150          # keep the characters in the lower-middle of the frame (less empty floor)
    z *= 1.08
    return cx + amp * math.sin(t * 93), cy + amp * math.cos(t * 79), z


# ---------------------------------------------------------------- frame
def frame(t):
    ctx = Ctx()
    g = grumpo_state(t)
    n = nibbo_state(t)
    L = [room(t)]
    L.append(table(640, 1450, mug(600, 1444, t) + croissant(690, 1444)))
    L.append(table(1470, 1450, iced(1440, 1444)))
    L.append(outlet_box(t))

    # ---------------- grumpo's charger (cable + plug)
    gph_svg, gport = phone(g["phone"][0], g["phone"][1], g["phone_rot"], "dead" if t >= T_DEAD else "on", t, 0.92)
    back_layer, front_layer = [], []
    if t < T_GPLUG:
        psvg, pex = plug(g["plug"][0], g["plug"][1], 180, GC_COL)
        samp = catmull([pex, (pex[0] - 40, pex[1] - 40), ((pex[0] + gport[0]) / 2, max(pex[1], gport[1]) + 60), gport])
        front_layer.append(cable_svg(samp, GC_COL) + psvg)
    else:
        if t < T_YANK:
            gp, grot = SOCK, 180
        else:
            q = seg(t, T_YANK, T_YANK + 0.3)
            gp = arc(eout(q), SOCK, LOOSE_P, 90)
            grot = lerp(180, 290, q)
        psvg, pex = plug(gp[0], gp[1], grot, GC_COL)
        # where is the phone-end of the cable?
        if t < T_UNPL0 + 0.05:
            end = gport
            con = ""
        elif t < T_SCOOP1:
            q = seg(t, T_UNPL0 + 0.05, T_TOSS1)
            e0 = gport if t < T_TOSS1 else LOOSE_G
            end = arc(eout(q), (BX + 132, GSEAT + 30), LOOSE_G, 150) if t < T_TOSS1 else LOOSE_G
            con, _ = connector(end[0], end[1], lerp(0, -80, q) if t < T_TOSS1 else -80, GC_COL)
            del e0
        else:
            end = gport
            con = ""
        if t < T_UNPL0 + 0.05 or t >= T_SCOOP1:
            if t < T_JUMP0:
                pts = [pex, (pex[0] + 20, pex[1] - 10), (pex[0] + 70, 1640), (end[0] - 10, end[1] + 50), end]
            elif t < T_YANK:
                pts = [pex, (pex[0] - 30, pex[1] - 10), (pex[0] - 70, 1680), (end[0] + 20, end[1] + 60), end]
            else:
                pts = [pex, (pex[0] - 20, 1690), ((pex[0] + end[0]) / 2, 1694), (end[0] + 10, end[1] + 70), end]
        else:
            pts = [pex, (pex[0] - 20, pex[1] - 6), (pex[0] - 70, 1680), end]
        samp = catmull(pts)
        back_layer.append(cable_svg(samp, GC_COL) + psvg + con)

    # ---------------- nibbo's cable
    nph_state = "on"
    nport = None
    nph_svg = ""
    if n["phone"] is not None:
        nph_svg, nport = phone(n["phone"][0], n["phone"][1], n["phone_rot"], nph_state, t, 0.9, back=n.get("back", False))
    n_cable_front = ""
    n_cable_back = ""
    energy = ""
    if n["phone"] is not None and not n.get("lasso"):
        if T_TIP0 <= t < T_SHOW + 0.05 or (T_SHOW <= t < T_NUNPL):
            # plug in nibbo's left hand or in grumpo's phone port
            r = n.get("reach", 0.0)
            hand0 = (n["x"] - 125, n["y"] + 20)
            tgt = (gport[0], gport[1] + 46)
            if t >= T_REACH1:
                pp = tgt
            else:
                pp = (lerp(hand0[0], tgt[0], r), lerp(hand0[1], tgt[1], r))
            psvg, pex = plug(pp[0], pp[1], 0, NC_COL, 0.9)
            samp = catmull([pex, (pex[0] + 6, pex[1] + 60), (pex[0] + 50, FLOOR - 6), (nport[0] + 10, FLOOR - 8), nport])
            n_cable_front = cable_svg(samp, NC_COL, 8) + psvg
            if T_DRAIN0 <= t < T_DRAIN1:
                for k in range(5):
                    f = ((t - T_DRAIN0) * 0.9 + k / 5) % 1
                    ex, ey = along(samp, f)
                    energy += (f'<g transform="translate({ex:.1f} {ey:.1f}) rotate({30*k})"><path d="M6 -24 L-15 3 L-2 3 L-8 24 L15 -3 L2 -3Z" '
                               f'fill="#fff36a" stroke="{OL}" stroke-width="3" stroke-linejoin="round"/></g>')
        elif n["plug"] is not None:
            px, py = n["plug"]
            psvg, pex = plug(px, py, n["plug_rot"], NC_COL, 0.9)
            if n.get("sit") or (t >= T_NPLUG):
                pts = [pex, (pex[0] + 10, pex[1] - 20), (pex[0] + 70, 1660), (nport[0] - 10, nport[1] + 50), nport]
                n_cable_back = cable_svg(catmull(pts), NC_COL, 8) + psvg
            else:
                mid = ((pex[0] + nport[0]) / 2, max(pex[1], nport[1]) + 70)
                if n.get("slide"):
                    mid = ((pex[0] + nport[0]) / 2, FLOOR - 8)
                n_cable_front = cable_svg(catmull([pex, mid, nport]), NC_COL, 8) + psvg

    lasso_svg = ""
    if n.get("lasso"):
        nx, ny = n["x"], n["y"]
        hnd = (nx - 40, ny - 150)
        if t < T_SPIN1:
            a = (t - T_SPIN0) * 2 * math.pi * 1.9
            rr = 85
            cx_, cy_ = nx - 20, ny - 215
            pp = (cx_ + rr * math.cos(a), cy_ + rr * 0.45 * math.sin(a))
            prot = math.degrees(a) + 90
        elif t < T_THROW1:
            q = seg(t, T_SPIN1, T_THROW1)
            pp = arc(eio(q), (nx - 100, ny - 215), (BX + 150, GSEAT - 80), 110)
            prot = -90
        else:
            q = seg(t, T_THROW1, T_RET1)
            pp = arc(eout(q), (BX + 150, GSEAT - 80), (nx + 20, ny - 40), 70)
            prot = lerp(-90, 120, q)
        nph_svg, nport = phone(nx + 122, ny - 10, 0, "on", t, 0.9)
        psvg, pex = plug(pp[0], pp[1], prot, NC_COL, 0.9)
        samp = catmull([nport, (nport[0] + 20, nport[1] + 70), (nx + 60, ny + 60), hnd, ((hnd[0] + pex[0]) / 2, (hnd[1] + pex[1]) / 2 + 30), pex])
        lasso_svg = (cable_svg(samp, NC_COL, 8) + psvg
                     + arm(nx - 70, ny - 40, hnd[0], hnd[1], NS, 10, -10) + hand(hnd[0], hnd[1], NB, NS, 13))
        if t < T_SPIN1:
            for k in range(3):
                aa = (t - T_SPIN0) * 2 * math.pi * 1.9 - k * 0.35
                lasso_svg += (f'<path d="M{nx-20+95*math.cos(aa):.0f} {ny-215+43*math.sin(aa):.0f} l{-14*math.sin(aa):.0f} {7*math.cos(aa):.0f}" '
                              f'stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="{0.6-0.18*k:.2f}"/>')

    # ---------------- draw order
    L.extend(back_layer)
    L.append(n_cable_back)

    # Nibbo (behind grumpo when sneaking close)
    def draw_nibbo():
        o = []
        nx, ny = n["x"], n["y"]
        if not n["sit"]:
            o.append(shadow(nx, FLOOR + 6, 100, 0.9))
        ex = n["ex"] if n["face"] is None else "none"
        o.append(nibbo(ctx, nx, ny, NR, ex, rot=n["rot"], sx=n["sx"], sy=n["sy"]))
        if n["face"]:
            o.append(nib_face(nx, ny, NR, n["rot"], n["sx"], n["sy"], n["face"], n["look"]))
        if n["wrap"] > 0:
            cnt = n["wrap"] * 4
            cid = ctx.uid("wr")
            ctx.defs.append(f'<clipPath id="{cid}"><circle r="{NR+8}"/></clipPath>')
            o.append(f'<g transform="translate({nx:.1f} {ny:.1f}) rotate({n["rot"]:.1f})"><g clip-path="url(#{cid})">')
            for k in range(4):
                if k < cnt:
                    yy = -70 + k * 46
                    o.append(f'<path d="M-130 {yy+18} Q 0 {yy-14} 130 {yy+18}" fill="none" stroke="{OL}" stroke-width="20"/>'
                             f'<path d="M-130 {yy+18} Q 0 {yy-14} 130 {yy+18}" fill="none" stroke="{NC_COL}" stroke-width="12"/>')
            o.append('</g>')
            if n["wrap"] > 0.9:
                ps, _ = plug(-118, 60, 140, NC_COL, 0.8)
                ph_, _ = phone(96, 30, 25, "on", t, 0.75)
                o.append(ph_ + ps)
            o.append('</g>')
        return "".join(o)

    sneaking = T_TIP0 <= t < T_NUNPL
    if sneaking:
        L.append(draw_nibbo())

    # Grumpo
    gx, gy = g["x"], g["y"]
    if not g["seated"]:
        L.append(shadow(gx, FLOOR + 6, 120))
    L.append(grumpo(ctx, gx, gy, GS, g["ex"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"], False, 0, None, 0, t))
    if g["kind"]:
        L.append(grumpo_extra(gx, gy, GS, g["rot"], g["sx"], g["sy"], g["kind"], t, g["red"]))
    # screen glow on grumpo's face while watching
    if T_LAUGH0 <= t < T_DEAD:
        L.append(f'<ellipse cx="{gx+70:.0f}" cy="{gy-10:.0f}" rx="90" ry="110" fill="url(#glow)" opacity="0.55"/>')

    if not sneaking:
        L.append(draw_nibbo())

    # cables in front, phones, arms
    L.extend(front_layer)
    L.append(n_cable_front)
    ink = mix_hex(INK, "#3a0505", g["red"])
    gfill = mix_hex(GFILL, "#ff6a52", g["red"])
    sx0 = gx + 100 * GS * g["sx"]
    sxl = gx - 100 * GS * g["sx"]
    sy0 = gy + 30 * GS
    php = g["phone"]
    # right arm to phone, left arm to plug/other
    L.append(arm(sxl, sy0, php[0], php[1] + 10, ink, 13, 18) if php[0] < gx else arm(sx0, sy0, php[0], php[1] + 10, ink, 13, 18))
    L.append(gph_svg)
    L.append(hand(php[0] + (-20 if php[0] < gx else 20), php[1] + 18, gfill, OL, 16))
    if g["plug"] is not None:
        L.append(arm(sx0, sy0, g["plug"][0] + 8, g["plug"][1] + 10, ink, 13, 10) + hand(g["plug"][0] + 8, g["plug"][1] + 14, gfill, OL, 16))
    elif g["other"] is not None:
        ox, oy = g["other"]
        L.append(arm(sxl, sy0, ox, oy, ink, 13, 14) + hand(ox, oy, gfill, OL, 16))
    # grumpo's phone blowing puff
    if 8.15 <= t < 8.7:
        q = seg(t, 8.15, 8.7)
        L.append(f'<circle cx="{php[0]+10:.0f}" cy="{php[1]-80-60*q:.0f}" r="{10+18*q:.0f}" fill="#ffffff" opacity="{0.7*(1-q):.2f}"/>')

    # Nibbo arms + phone
    nx, ny = n["x"], n["y"]
    if n["phone"] is not None and not n.get("lasso"):
        L.append(arm(nx + 80 * n["sx"], ny + 10, n["phone"][0] - 10, n["phone"][1] + 10, NS, 10, 10))
        L.append(nph_svg)
        L.append(hand(n["phone"][0] - 18, n["phone"][1] + 18, NB, NS, 13))
        if n["plug"] is not None and not n.get("sit") and not (t >= T_REACH1 and t < T_NUNPL):
            if T_TIP0 <= t < T_NUNPL:
                r = n.get("reach", 0.0)
                hx, hy = lerp(nx - 125, gport[0], r), lerp(ny + 20, gport[1] + 46, r) + 14
            else:
                hx, hy = n["plug"][0], n["plug"][1] + 8
            L.append(arm(nx - 80 * n["sx"], ny + 10, hx, hy, NS, 10, 10) + hand(hx, hy, NB, NS, 13))
        if n.get("point") is not None and n["point"] > 0:
            k = n["point"]
            hx, hy = nx - 60 - 70 * k, ny - 40 - 150 * k
            L.append(arm(nx - 70, ny - 10, hx, hy, NS, 10, -10) + hand(hx, hy, NB, NS, 13)
                     + f'<path d="M{hx-6:.0f} {hy-14:.0f} l-14 -26" stroke="{NS}" stroke-width="10" stroke-linecap="round"/>'
                     f'<path d="M{hx-6:.0f} {hy-14:.0f} l-14 -26" stroke="{NB}" stroke-width="5" stroke-linecap="round"/>')
        if n.get("wave") is not None and n["wave"] > 0 and t < T_ZIP0:
            w = math.sin((t - T_WAVE0) * 22) * 18
            hx, hy = nx - 110 + w, ny - 120
            L.append(arm(nx - 70, ny - 10, hx, hy, NS, 10, -10) + hand(hx, hy, NB, NS, 13))
        if n.get("sit"):
            L.append(arm(nx - 80, ny + 10, nx - 90, ny + 60, NS, 10, 10) + hand(nx - 90, ny + 60, NB, NS, 13))
    L.append(lasso_svg)
    L.append(energy)

    # ---------------- battery bubbles
    gl, nl = g_level(t), n_level(t)
    gvis = 1.0
    nvis = 1.0
    def win(t, a, b, fade=0.15):
        if t < a or t > b:
            return 0.0
        return min(1.0, eback(seg(t, a, a + 0.25)), seg(t, b, b - fade) if False else 1 - seg(t, b - fade, b))
    gvis = max(win(t, -0.3, 2.9), win(t, T_GPLUG - 0.05, 2.9), win(t, 9.2, 10.4), win(t, 13.6, T_DEAD + 0.9))
    nvis = max(win(t, -0.3, 2.95), win(t, 13.6, 19.3), win(t, T_NSIT1, DUR + 1))
    gcharge = T_GPLUG <= t < T_FULL
    ncharge = (T_DRAIN0 <= t < T_DRAIN1) or t >= T_NPLUG
    gb = (gx - 30, gy - 225)
    nb = (nx + 20, ny - 215)
    if t >= T_NSIT1:
        nb = (nx + 30, ny - 215)
    if T_SELFIE0 <= t:
        nb = (nx + 150, ny - 170)
    gsp = seg(t, T_FULL, T_FULL + 0.5) if T_FULL <= t < T_FULL + 0.5 else 0
    nsp = seg(t, T_SHOW, T_SHOW + 0.5) if T_SHOW <= t < T_SHOW + 0.5 else 0
    L.append(battery(gb[0], gb[1], gl, gcharge, t, gvis, gsp, 0.82))
    L.append(battery(nb[0], nb[1], nl, ncharge, t, nvis, nsp, 0.82))

    # ---------------- effects
    L.append(impact(BX, 1560, seg(t, T_CLASH, T_CLASH + 0.22)))
    L.append(impact(1060, gy + 10 if t < 2 else 1560, seg(t, T_BUMP, T_BUMP + 0.22), "#ffffff"))
    if T_GPLUG <= t < T_GPLUG + 0.3:
        q = seg(t, T_GPLUG, T_GPLUG + 0.3)
        for k in range(6):
            a = math.radians(-160 + k * 28)
            L.append(f'<path d="M{BX+40*math.cos(a):.0f} {BOX_T-10+40*math.sin(a):.0f} l{40*q*math.cos(a):.0f} {40*q*math.sin(a):.0f}" stroke="#fff36a" stroke-width="7" stroke-linecap="round" opacity="{1-q:.2f}"/>')
    L.append(impact(1110, 1600, seg(t, T_BONK, T_BONK + 0.22), "#ffffff"))
    L.append(impact(BX + 160, GSEAT - 100, seg(t, T_SWAT, T_SWAT + 0.2), "#ffffff"))
    L.append(impact(n["x"] - 90, FLOOR - 40, seg(t, T_TIP1, T_TIP1 + 0.2), "#ffffff") if T_TIP1 <= t < T_TIP1 + 0.2 else "")
    if T_SLIDE0 <= t < T_BONK:
        L.append(speed_lines(n["x"] + 140, FLOOR - 60, 180, 1.0))
    if n.get("zip"):
        L.append(speed_lines(n["x"] + 150, n["y"], 180, 1.0))
    L.append(symbol(n["x"] - 10, n["y"] - 175, "!", seg(t, T_POINT0, T_POINT0 + 0.5), "#ffb02a"))
    L.append(symbol(gx + 40, gy - 190, "?", seg(t, T_LOOKUP + 0.05, 4.3), "#3a7ad6"))
    L.append(bulb(n["x"] + 10, n["y"] - 210, seg(t, T_IDEA, T_IDEA + 0.75)))
    L.append(symbol(gx + 125, gy - 175, "?", seg(t, T_NOTICE + 0.15, T_SHAKE0 + 0.2), "#3a7ad6"))
    L.append(symbol(gx + 125, gy - 185, "!", seg(t, T_DEAD, T_DEAD + 0.55)))
    L.append(symbol(gx - 20, gy - 190, "!", seg(t, T_REALIZE, T_REALIZE + 0.5)))
    if T_FULL <= t < T_FULL + 0.6:
        L.append(star_twinkle(gb[0] + 70, gb[1] - 50, seg(t, T_FULL, T_FULL + 0.6)))
    if T_SHOW <= t < T_SHOW + 0.6:
        L.append(star_twinkle(nb[0] - 70, nb[1] - 50, seg(t, T_SHOW, T_SHOW + 0.6)))
    if T_DEAD <= t < T_DEAD + 0.4:
        q = seg(t, T_DEAD, T_DEAD + 0.4)
        L.append(f'<circle cx="{php[0]:.0f}" cy="{php[1]:.0f}" r="{30+80*q:.0f}" fill="none" stroke="#7fd0ff" stroke-width="6" opacity="{1-q:.2f}"/>')
    if T_REALIZE + 0.5 <= t:
        # grumble lines around grumpo
        for k, (dx, dy) in enumerate([(-150, -40), (150, -60), (-160, 40)]):
            w = 8 * math.sin(t * 50 + k)
            d = -1 if dx < 0 else 1
            L.append(f'<path d="M{gx+dx:.0f} {gy+dy-24:.0f} q{d*18+w:.0f} 12 0 24 q{d*18-w:.0f} 12 0 24" fill="none" stroke="#ff6a52" stroke-width="7" stroke-linecap="round"/>')

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    flash = ""
    if T_FLASH <= t < T_FLASH + 0.35:
        flash = f'<rect width="{W}" height="{H}" fill="#ffffff" opacity="{0.9*(1-seg(t, T_FLASH, T_FLASH+0.35)):.2f}"/>'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g>'
           f'<rect width="{W}" height="{H}" fill="url(#vig)"/>{flash}</svg>')
    return overlay(svg, hook_title(t + 0.12, "Both phones at 1%,", "ONLY 1 OUTLET!"))


def build_sfx():
    sfx(0.0, "error_beep", 0.5, 1.0)
    sfx(0.05, "whoosh", 0.7, 1.0)
    sfx(0.1, "whoosh", 0.6, 1.2)
    for k in range(3):
        sfx(0.08 + k * 0.13, "hop", 0.4, 1.0 + 0.1 * k)
    sfx(T_CLASH, "clank", 0.9, 1.4)
    sfx(T_CLASH + 0.02, "clack", 0.7, 1.0)
    sfx(T_CLASH + 0.1, "strain", 0.6, 1.0)
    sfx(T_BUMP, "boing", 0.9, 0.8)
    sfx(T_BUMP + 0.02, "bonk", 0.6, 1.0)
    sfx(T_BUMP + 0.05, "whoosh", 0.6, 1.3)
    sfx(T_GPLUG, "click", 0.9, 1.0)
    sfx(T_GPLUG + 0.02, "zap", 0.6, 1.0)
    sfx(T_GPLUG + 0.12, "charge_ok", 0.8, 1.0)
    sfx(T_NLAND, "thud", 0.6, 1.3)
    sfx(T_NLAND + 0.05, "boing", 0.4, 1.6)
    sfx(T_HOP0, "hop", 0.5, 0.9)
    sfx(T_HOP1, "squish", 0.6, 0.8)
    sfx(T_HOP1 + 0.02, "thud", 0.6, 1.0)
    sfx(2.2, "error_beep", 0.55, 1.05)
    sfx(2.55, "deflate", 0.3, 1.4)
    sfx(T_POINT0, "gasp", 0.6, 1.3)
    sfx(T_POINT0 + 0.05, "pop", 0.5, 1.2)
    sfx(T_LOOKUP, "blip", 0.4, 1.0)
    sfx(T_SLIDE0, "squeak_slide", 0.8, 1.1)
    sfx(T_SLIDE0 + 0.05, "whoosh", 0.5, 1.4)
    sfx(T_SPREAD0, "squish", 0.7, 0.7)
    sfx(T_BONK, "bonk", 1.0, 0.9)
    sfx(T_BONK + 0.03, "boing", 0.8, 1.1)
    sfx(T_NBACK1, "thud", 0.6, 1.4)
    sfx(T_FLIP0, "slide_up", 0.4, 1.4)
    sfx(T_FLIP1, "plop", 0.5, 1.2)
    sfx(5.25, "hop", 0.4, 1.3)
    for k in range(4):
        sfx(T_SPIN0 + k * 0.4, "whoosh", 0.55 + 0.08 * k, 1.5 - 0.08 * k)
    sfx(T_SPIN1, "zoom", 0.6, 1.2)
    sfx(T_SWAT, "slap", 1.0, 1.0)
    sfx(T_SWAT + 0.02, "boing", 0.5, 1.3)
    sfx(T_SWAT + 0.05, "whoosh", 0.5, 1.6)
    for k in range(4):
        sfx(T_RET1 + k * 0.16, "zip", 0.55, 1.0 + 0.1 * k)
    sfx(T_TIP1, "thud", 0.8, 1.0)
    sfx(T_TIP1 + 0.05, "boing", 0.3, 1.8)
    sfx(8.15, "blow", 0.6, 1.2)
    sfx(T_FULL, "ding", 0.9, 1.0)
    sfx(T_FULL + 0.05, "shine", 0.5, 1.2)
    sfx(T_UNPL0 + 0.05, "pop", 0.8, 1.0)
    sfx(T_UNPL0 + 0.15, "whoosh", 0.4, 1.6)
    sfx(T_TOSS1, "clack", 0.4, 1.6)
    sfx(T_FREE0, "zip", 0.5, 0.9)
    sfx(T_FREE0 + 0.2, "zip", 0.5, 1.1)
    sfx(T_FREE1, "boing", 0.5, 1.2)
    sfx(T_LAUGH0, "laugh", 0.55, 1.0)
    sfx(T_LAUGH0 + 1.4, "laugh", 0.5, 1.05)
    sfx(T_LAUGH0 + 2.8, "laugh", 0.45, 0.95)
    sfx(T_IDEA, "ding", 0.6, 1.5)
    sfx(T_IDEA + 0.05, "pop", 0.5, 1.3)
    for k in range(5):
        sfx(T_TIP0 + 0.15 + k * (T_TIPEND - T_TIP0) / 5, "tiptoe", 0.65, 1.0 + 0.05 * k)
    sfx(T_TIP0, "sneak", 0.5, 1.0)
    sfx(T_REACH1 - 0.05, "click", 0.6, 1.4)
    sfx(T_DRAIN0, "zap", 0.5, 1.3)
    sfx(T_DRAIN0 + 0.15, "charge_ok", 0.5, 1.2)
    for k in range(7):
        sfx(T_DRAIN0 + 0.4 + k * 0.5, "blip", 0.22, 1.6 + 0.04 * k)
    sfx(T_NOTICE, "blip_down", 0.4, 1.0)
    sfx(T_NOTICE + 0.15, "squeak", 0.35, 1.1)
    sfx(T_SHAKE0, "shaker", 0.6, 1.2)
    sfx(T_TAP0, "tap", 0.8, 1.0)
    sfx(T_TAP0 + 0.18, "tap", 0.8, 1.05)
    sfx(T_TAP0 + 0.36, "tap", 0.8, 1.1)
    sfx(16.6, "error_beep", 0.6, 0.95)
    sfx(T_DEAD, "power_off", 1.0, 1.0)
    sfx(T_DEAD + 0.05, "gasp", 0.6, 0.9)
    sfx(T_FOLLOW0, "slide_down", 0.4, 1.3)
    sfx(T_SHOW, "ding", 0.9, 1.15)
    sfx(T_SHOW + 0.05, "shine", 0.6, 1.3)
    sfx(T_SHOW + 0.1, "cheer", 0.25, 1.4)
    sfx(T_NUNPL, "pop", 0.7, 1.2)
    sfx(T_NHOP1, "hop", 0.5, 1.2)
    sfx(T_WAVE0 + 0.05, "squeak", 0.3, 1.6)
    sfx(T_SHOW + 0.25, "grumble", 0.6, 0.9)
    sfx(T_JUMP0, "boing", 0.7, 0.9)
    sfx(T_JUMP1, "thud", 0.8, 0.9)
    sfx(T_ZIP0, "zoom", 0.7, 1.4)
    sfx(T_YANK, "pop", 0.8, 0.9)
    sfx(T_NPLUG, "click", 0.8, 1.1)
    sfx(T_NPLUG + 0.02, "zap", 0.4, 1.2)
    sfx(T_NSIT1, "squish", 0.5, 1.1)
    sfx(T_NSIT1 + 0.05, "charge_ok", 0.7, 1.1)
    sfx(T_SCOOP1, "click", 0.6, 0.8)
    sfx(T_CHECK, "error_beep", 0.5, 0.9)
    sfx(T_LOOKCAB, "slide_down", 0.35, 1.2)
    sfx(T_REALIZE, "gasp", 0.8, 0.85)
    sfx(T_REALIZE + 0.05, "blip_down", 0.5, 0.8)
    sfx(T_REALIZE + 0.5, "grumble", 0.9, 0.7)
    sfx(T_REALIZE + 0.55, "rumble", 0.6, 1.1)
    sfx(T_SELFIE0, "slide_up", 0.4, 1.3)
    sfx(T_FLASH, "shutter", 1.0, 1.0)
    sfx(T_FLASH + 0.25, "laugh", 0.3, 1.5)
    sfx(T_FLASH + 0.4, "grumble", 0.7, 0.65)
