"""Grumpo & Nibbo — Episode 14: The Armrest (economy cabin of a plane, 60 fps).

Grumpo (window) and Nibbo (aisle seat) are buckled in, seatbelt sign ON, and they slam their elbows onto the
ONE shared armrest at the very same moment. Rounds (structure A: tries + final, no counter):
  1. Elbow push-war: shaking, Grumpo turns red and shoves; Nibbo's arm flies off and he bonks the aisle side.
  2. Nibbo presses the little release button: the armrest flips UP, Grumpo (leaning on it) tips over and
     squashes Nibbo against the aisle; Nibbo springs back like rubber and flings Grumpo upright, then folds
     the armrest down and claims it.
  3. Grumpo slaps his hand on top of Nibbo's. Nibbo dangles a bag of peanuts; greedy Grumpo grabs it with
     both hands and pours it in — Nibbo sprawls over the whole armrest. Grumpo notices, sputters peanuts,
     and lunges to hug the armrest with both arms, squeezing Nibbo to the aisle edge.
Final: bing-bong, the seatbelt sign goes OFF. Nibbo unbuckles, pops out, hops across the aisle to a totally
EMPTY row, lifts its armrest and lies across both seats with an arm on each outer armrest. Grumpo jumps to
follow — but he is still buckled: the belt yanks him back, he slams into the seat and the armrest he fought
for snaps off in his hands (spring boings out). Nibbo, comfy, waves. Ending: Nibbo wins.
"""
import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow, cloud
from hook import overlay, hook_title

W, H, FPS, DUR = 1080, 1920, 60, 21.6
GS = 0.92
GR = 130 * GS
NR = 112
INK = "#1a0a2e"
GFILL = "#9466e0"
NB, NS = "#ffd23c", "#3d2a12"

FLOOR = 1760
CUSH = 1430            # cushion top (front lip starts here)
G0 = (520.0, 1325.0)   # grumpo seated centre
N0 = (860.0, 1335.0)   # nibbo seated centre
ARM_X = 690            # shared armrest
PAD_Y = 1412           # armrest pad top
AISLE = (1030, 1200)
ARM_C = 1535           # across-aisle middle armrest
SEATS = [(355, 685), (695, 1025), (1205, 1530), (1540, 1865)]
VP = (1115, 1270)      # aisle vanishing point

# ---- times
T_SLAM = 0.28
T_ZAP0, T_ZAP1 = 0.45, 1.2
T_PUSH0, T_PUSH1 = 1.2, 3.3
T_SHOVE = 3.35
T_BONK = 3.55
T_REC0, T_REC1 = 3.9, 4.3
T_IDEA = 4.45
T_PRESS = 5.0
T_FLIP0, T_FLIP1 = 5.05, 5.2
T_TIP0, T_TIP1 = 5.12, 5.42
T_SPRING = 5.95
T_BACK1 = 6.3
T_DOWN0, T_DOWN1 = 6.55, 6.72
T_CLAIM = 6.85
T_MAD = 7.0
T_SLAM2 = 7.35
T_BAG0, T_BAG1 = 8.25, 8.65
T_SHAKE0, T_SHAKE1 = 8.7, 9.35
T_GRAB = 9.45
T_EAT0, T_EAT1 = 9.7, 10.65
T_SPRAWL0, T_SPRAWL1 = 9.75, 10.2
T_NOTICE = 10.75
T_HUG0, T_HUG1 = 11.15, 11.45
T_CHIME = 12.7
T_LOOKUP = 13.05
T_UNBUCK = 13.45
T_POP = 13.7
T_HOP1 = 14.05          # lands in aisle
T_HOP2 = 14.45          # lands on across seats (sitting)
T_LIFT = 14.6           # lifts across armrest
T_LIE0, T_LIE1 = 14.75, 15.05
T_SEE = 16.15
T_JUMP0, T_JUMP1 = 16.7, 17.05
T_YANK1 = 17.3
T_SNAP = 17.45
T_SPRINGOUT = 18.3
T_WAVE0, T_WAVE1 = 19.7, 21.0

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
        s = math.sin(math.pi * k / d)
        return 1 + a * 0.6 * s, 1 - a * s
    return 1.0, 1.0


def wob(t, t0, d=0.6, a=10.0, f=18.0):
    k = t - t0
    if 0 <= k < d:
        return a * math.exp(-k * 5) * math.sin(k * f)
    return 0.0


def bodypt(x, y, s, rot, sx, sy, px, py):
    """point in a character's local frame -> world."""
    a = math.radians(rot)
    lx, ly = px * s * sx, py * s * sy
    return x + lx * math.cos(a) - ly * math.sin(a), y + lx * math.sin(a) + ly * math.cos(a)


def arm(x0, y0, x1, y1, col, w=13, sag=20):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    return f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


def hand(x, y, fill, stroke, r=16):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="5"/>'


# ---------------------------------------------------------------- props
def peanut(x, y, rot=0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<path d="M-12 -4 Q -14 -12 -6 -12 Q 0 -10 2 -6 Q 6 -12 12 -10 Q 18 -4 12 4 Q 6 10 0 6 Q -6 12 -12 6 Q -16 2 -12 -4Z" fill="#d9a45a" stroke="#6a4416" stroke-width="2.5"/>'
            f'<path d="M-6 -4 v6 M6 -4 v6" stroke="#a8742e" stroke-width="2"/></g>')


def peanut_bag(x, y, rot=0.0, s=1.0, open_=False):
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">']
    o.append(f'<path d="M-36 -46 L36 -46 L40 46 Q 0 54 -40 46Z" fill="#3a8fd8" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>')
    o.append('<path d="M-30 -30 L-22 44" stroke="#7ec0f2" stroke-width="7" stroke-linecap="round" opacity="0.8"/>')
    o.append(f'<ellipse cx="0" cy="8" rx="24" ry="22" fill="#ffffff" stroke="{OL}" stroke-width="3"/>')
    o.append(peanut(0, 8, -20, 1.3))
    if open_:
        o.append(f'<path d="M-36 -46 Q 0 -60 36 -46" fill="#1d4f82" stroke="{OL}" stroke-width="4"/>')
    else:
        o.append(f'<path d="M-38 -46 l8 -10 l8 10 l8 -10 l8 10 l8 -10 l8 10 l8 -10 l8 10 l8 -10 l4 6" fill="#e9f2fb" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>')
    o.append('</g>')
    return "".join(o)


def zap(x0, y0, x1, y1, t, op=1.0):
    if op <= 0:
        return ""
    pts = []
    n = 7
    for k in range(n + 1):
        p = k / n
        x = lerp(x0, x1, p)
        y = lerp(y0, y1, p) + (0 if k in (0, n) else (22 if (k + int(t * 30)) % 2 else -22))
        pts.append(f"{x:.0f},{y:.0f}")
    pl = " ".join(pts)
    return (f'<g opacity="{op:.2f}"><polyline points="{pl}" fill="none" stroke="{OL}" stroke-width="20" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<polyline points="{pl}" fill="none" stroke="#ffe23a" stroke-width="11" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<polyline points="{pl}" fill="none" stroke="#fffbe0" stroke-width="4" stroke-linejoin="round"/></g>')


def sweat(x, y, p, s=1.0):
    if p <= 0 or p >= 1:
        return ""
    yy = y + 40 * p
    return f'<path d="M{x:.0f} {yy:.0f} q{9*s:.0f} {14*s:.0f} 0 {22*s:.0f} q{-9*s:.0f} {-8*s:.0f} 0 {-22*s:.0f}z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3" opacity="{1-p:.2f}"/>'


def zzz(x, y, t, op=1.0):
    o = []
    for k in range(3):
        p = (t * 0.6 + k / 3) % 1
        xx = x + 50 * p + 10 * math.sin(p * 9)
        yy = y - 100 * p
        sz = 22 + 26 * p
        o.append(f'<text x="{xx:.0f}" y="{yy:.0f}" font-family="Fredoka" font-weight="700" font-size="{sz:.0f}" text-anchor="middle" '
                 f'fill="#ffffff" stroke="{OL}" stroke-width="6" paint-order="stroke" opacity="{op*min(1, (1-p)*2.2, p*6):.2f}">Z</text>')
    return "".join(o)


def spring_coil(x, y, h, rot=0):
    pts = []
    for k in range(9):
        pts.append(f"{(14 if k % 2 else -14)},{-k * h / 8:.1f}")
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})"><polyline points="0,0 {" ".join(pts)}" fill="none" stroke="{OL}" stroke-width="9" stroke-linejoin="round"/>'
            f'<polyline points="0,0 {" ".join(pts)}" fill="none" stroke="#d7dce6" stroke-width="4" stroke-linejoin="round"/></g>')


# ---------------------------------------------------------------- cabin
def defs():
    return ('<linearGradient id="wallG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9dee9"/><stop offset="1" stop-color="#b9c1d3"/></linearGradient>'
            '<linearGradient id="skyW" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3f8fe6"/><stop offset="1" stop-color="#b8e2ff"/></linearGradient>'
            '<linearGradient id="seatG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3a6fd0"/><stop offset="0.7" stop-color="#2f5fb8"/><stop offset="1" stop-color="#244c98"/></linearGradient>'
            '<linearGradient id="binG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f4f6fa"/><stop offset="1" stop-color="#dde2ec"/></linearGradient>'
            '<linearGradient id="carpet" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4e5a80"/><stop offset="1" stop-color="#3a4466"/></linearGradient>'
            '<radialGradient id="amber"><stop offset="0" stop-color="#ffd76a" stop-opacity="0.9"/><stop offset="1" stop-color="#ffb02a" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="readL"><stop offset="0" stop-color="#fff8d8" stop-opacity="0.5"/><stop offset="1" stop-color="#fff8d8" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="vig" cx="0.5" cy="0.55" r="0.78"><stop offset="0.6" stop-color="#0c1030" stop-opacity="0"/><stop offset="1" stop-color="#0c1030" stop-opacity="0.4"/></radialGradient>'
            '<clipPath id="winL"><ellipse cx="210" cy="1170" rx="62" ry="92"/></clipPath>'
            '<clipPath id="winR"><ellipse cx="2030" cy="1170" rx="62" ry="92"/></clipPath>')


def window(cx, cy, t, clip):
    o = [f'<ellipse cx="{cx}" cy="{cy}" rx="88" ry="120" fill="#eef1f6" stroke="{OL}" stroke-width="6"/>',
         f'<ellipse cx="{cx}" cy="{cy}" rx="70" ry="100" fill="#c7cdd9" stroke="{OL}" stroke-width="4"/>']
    cl_ = []
    for k, (dx, dy, s) in enumerate([(0, -30, 0.32), (140, 40, 0.42), (260, -10, 0.3)]):
        x = cx - 90 + ((dx - t * 160) % 300)
        cl_.append(cloud(x, cy + dy, s))
    o.append(f'<g clip-path="url(#{clip})"><rect x="{cx-70}" y="{cy-100}" width="140" height="200" fill="url(#skyW)"/>'
             + "".join(cl_) +
             f'<rect x="{cx-70}" y="{cy-100}" width="140" height="52" fill="#e4e7ee"/><path d="M{cx-70} {cy-48} H{cx+70}" stroke="{OL}" stroke-width="4"/>'
             f'<rect x="{cx-12}" y="{cy-56}" width="24" height="8" rx="4" fill="#9aa2b4"/>'
             f'<path d="M{cx-40} {cy+60} l50 -70" stroke="#ffffff" stroke-width="10" opacity="0.35" stroke-linecap="round"/></g>')
    o.append(f'<ellipse cx="{cx}" cy="{cy}" rx="62" ry="92" fill="none" stroke="{OL}" stroke-width="5"/>')
    return "".join(o)


def cabin(t, sign_on):
    o = []
    # back (rows behind) wall
    o.append(f'<rect x="-600" y="300" width="3400" height="{FLOOR-300}" fill="url(#wallG)"/>')
    # aisle perspective (far galley wall + receding seat stacks)
    vx, vy = VP
    o.append(f'<path d="M{AISLE[0]} {FLOOR} L{vx-40} {vy+60} L{vx+40} {vy+60} L{AISLE[1]} {FLOOR}Z" fill="#46507a"/>')
    o.append(f'<rect x="{vx-58}" y="{vy-200}" width="116" height="262" fill="#cfd5e2" stroke="{OL}" stroke-width="4"/>'
             f'<rect x="{vx-30}" y="{vy-150}" width="60" height="212" rx="6" fill="#aeb7cb" stroke="{OL}" stroke-width="4"/>'
             f'<circle cx="{vx+18}" cy="{vy-50}" r="5" fill="{OL}"/><rect x="{vx-12}" y="{vy-136}" width="24" height="12" rx="3" fill="#6fd07a"/>')
    for k in range(4):
        f = 0.82 - k * 0.17
        ylo = lerp(vy + 60, CUSH + 40, f)
        ytop = lerp(vy - 70, 1060, f)
        xl = lerp(vx - 58, AISLE[0], f)
        xr = lerp(vx + 58, AISLE[1], f)
        w = 70 * f + 20
        o.append(f'<rect x="{xl-w:.0f}" y="{ytop:.0f}" width="{w:.0f}" height="{ylo-ytop:.0f}" rx="{10*f+6:.0f}" fill="{mix_hex("#6f8fd0", "#a9b6d4", 1-f)}" stroke="{OL}" stroke-width="{2+3*f:.1f}"/>'
                 f'<rect x="{xr:.0f}" y="{ytop:.0f}" width="{w:.0f}" height="{ylo-ytop:.0f}" rx="{10*f+6:.0f}" fill="{mix_hex("#6f8fd0", "#a9b6d4", 1-f)}" stroke="{OL}" stroke-width="{2+3*f:.1f}"/>'
                 f'<rect x="{xl-w+4:.0f}" y="{ytop+4:.0f}" width="{w-8:.0f}" height="{(ylo-ytop)*0.18:.0f}" rx="5" fill="#eef1f7" opacity="0.9"/>'
                 f'<rect x="{xr+4:.0f}" y="{ytop+4:.0f}" width="{w-8:.0f}" height="{(ylo-ytop)*0.18:.0f}" rx="5" fill="#eef1f7" opacity="0.9"/>')
    # aisle floor lights
    for k in range(6):
        f = k / 6
        y = lerp(FLOOR, vy + 60, f ** 0.7)
        for side in (0, 1):
            x = lerp(AISLE[side], vx - 40 if side == 0 else vx + 40, f ** 0.7)
            o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{6*(1-f)+2:.1f}" fill="#bfe8ff" opacity="0.85"/>')
    # side walls with windows
    o.append(f'<path d="M-600 300 H300 Q 360 700 350 1150 Q 345 1500 330 {FLOOR} H-600Z" fill="#e3e7ef" stroke="{OL}" stroke-width="6"/>')
    o.append(f'<path d="M300 300 Q 360 700 350 1150 Q 345 1500 330 {FLOOR}" fill="none" stroke="#c4cad8" stroke-width="22" opacity="0.6"/>')
    o.append(window(210, 1170, t, "winL"))
    o.append(f'<path d="M2800 300 H1940 Q 1880 700 1890 1150 Q 1895 1500 1910 {FLOOR} H2800Z" fill="#e3e7ef" stroke="{OL}" stroke-width="6"/>')
    o.append(window(2030, 1170, t + 0.7, "winR"))
    # overhead bins
    for x0, x1 in [(320, 1035), (1195, 1920)]:
        o.append(f'<path d="M{x0-40} 300 H{x1+40} V820 Q {(x0+x1)/2} 880 {x0-40} 820Z" fill="url(#binG)" stroke="{OL}" stroke-width="6"/>')
        mid = (x0 + x1) / 2
        o.append(f'<path d="M{mid} 330 V850" stroke="#b9c0cf" stroke-width="5"/>')
        for hx in (mid - 180, mid + 180):
            o.append(f'<rect x="{hx-50}" y="780" width="100" height="22" rx="11" fill="#7e879a" stroke="{OL}" stroke-width="4"/>')
        o.append(f'<path d="M{x0-20} 815 Q {mid} 870 {x1+20} 815" fill="none" stroke="#ffffff" stroke-width="6" opacity="0.8"/>')
    # PSU strip
    for x0, x1, signs in [(320, 1035, (ARM_X, 520, 860)), (1195, 1920, (ARM_C, 1370, 1700))]:
        o.append(f'<path d="M{x0} 880 H{x1} V990 Q {(x0+x1)/2} 1010 {x0} 990Z" fill="#d3d8e3" stroke="{OL}" stroke-width="5"/>')
        sx_, l1, l2 = signs
        for lx in (l1, l2):
            o.append(f'<circle cx="{lx}" cy="940" r="20" fill="#f2f0e6" stroke="{OL}" stroke-width="4"/><circle cx="{lx+52}" cy="944" r="13" fill="#9aa2b4" stroke="{OL}" stroke-width="4"/>'
                     f'<circle cx="{lx+52}" cy="944" r="5" fill="{OL}"/>')
        on = sign_on if x0 < 1000 else sign_on
        bg = "#ffb83a" if on else "#8c93a4"
        icon = "#3a2206" if on else "#5c6374"
        if on:
            o.append(f'<circle cx="{sx_}" cy="942" r="75" fill="url(#amber)" opacity="{0.8+0.2*math.sin(t*6):.2f}"/>')
        o.append(f'<rect x="{sx_-44}" y="916" width="88" height="54" rx="12" fill="{bg}" stroke="{OL}" stroke-width="5"/>')
        # seatbelt icon: two straps + buckle
        o.append(f'<path d="M{sx_-30} 932 Q {sx_-20} 956 {sx_-8} 946 M{sx_+30} 932 Q {sx_+20} 956 {sx_+8} 946" fill="none" stroke="{icon}" stroke-width="6" stroke-linecap="round"/>'
                 f'<rect x="{sx_-10}" y="938" width="20" height="16" rx="3" fill="{icon}"/>')
    # floor (carpet)
    o.append(f'<rect x="-600" y="{FLOOR}" width="3400" height="600" fill="url(#carpet)" stroke="{OL}" stroke-width="6"/>')
    for k in range(-6, 30):
        x = k * 90
        o.append(f'<path d="M{x} {FLOOR+30} l20 18 l20 -18 M{x+45} {FLOOR+90} l20 18 l20 -18" fill="none" stroke="#5f6b94" stroke-width="5"/>')
    o.append(f'<rect x="{AISLE[0]}" y="{FLOOR}" width="{AISLE[1]-AISLE[0]}" height="600" fill="#56618a"/>')
    return "".join(o)


def backrest(x0, x1):
    cx = (x0 + x1) / 2
    w = x1 - x0 - 20
    return (f'<rect x="{x0+10}" y="1040" width="{w}" height="420" rx="46" fill="url(#seatG)" stroke="{OL}" stroke-width="6"/>'
            f'<path d="M{x0+40} 1150 V1400" stroke="#4a82e0" stroke-width="12" stroke-linecap="round" opacity="0.6"/>'
            f'<rect x="{x0+30}" y="1052" width="{w-40}" height="74" rx="18" fill="#eef1f7" stroke="{OL}" stroke-width="4"/>'
            f'<path d="M{x0+44} 1112 H{x1-44}" stroke="#c9d0de" stroke-width="5"/>'
            f'<path d="M{cx-30} 1080 h60" stroke="#c9d0de" stroke-width="5" stroke-linecap="round"/>')


def cushion_front(x0, x1):
    return (f'<path d="M{x0+4} {CUSH+10} Q {(x0+x1)/2} {CUSH-6} {x1-4} {CUSH+10} L{x1-10} {CUSH+82} Q {(x0+x1)/2} {CUSH+96} {x0+10} {CUSH+82}Z" fill="#2a55a6" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<path d="M{x0+24} {CUSH+18} Q {(x0+x1)/2} {CUSH+6} {x1-24} {CUSH+18}" fill="none" stroke="#4a82e0" stroke-width="7" stroke-linecap="round"/>'
            f'<rect x="{x0+30}" y="{CUSH+92}" width="{x1-x0-60}" height="{FLOOR-CUSH-92}" fill="#20283f" opacity="0.55"/>'
            f'<rect x="{x0+40}" y="{CUSH+90}" width="22" height="{FLOOR-CUSH-90}" fill="#8a93a8" stroke="{OL}" stroke-width="4"/>'
            f'<rect x="{x1-62}" y="{CUSH+90}" width="22" height="{FLOOR-CUSH-90}" fill="#8a93a8" stroke="{OL}" stroke-width="4"/>'
            f'<rect x="{x0+30}" y="{FLOOR-14}" width="{x1-x0-60}" height="16" rx="6" fill="#6c7488" stroke="{OL}" stroke-width="4"/>')


def armrest(x, up=0.0, shake=0.0, broken=False, button_glint=0.0):
    """up: 0 = down (pad visible), 1 = folded up behind. Drawn in two parts: back bar (behind chars) & pad (front)."""
    return armrest_back(x, up), armrest_front(x, up, shake, broken, button_glint)


def armrest_back(x, up):
    if up <= 0.05:
        return ""
    h = 270 * eout(up)
    return (f'<rect x="{x-21}" y="{PAD_Y-h:.0f}" width="42" height="{h+20:.0f}" rx="16" fill="#4a5064" stroke="{OL}" stroke-width="5"/>'
            f'<rect x="{x-12}" y="{PAD_Y-h+10:.0f}" width="12" height="{max(0, h-20):.0f}" rx="6" fill="#6c7388"/>')


def armrest_front(x, up=0.0, shake=0.0, broken=False, glint=0.0):
    o = []
    # support post (always)
    o.append(f'<rect x="{x-18}" y="{PAD_Y+20}" width="36" height="{CUSH+84-PAD_Y-20}" rx="8" fill="#3c4152" stroke="{OL}" stroke-width="5"/>')
    if broken:
        o.append(f'<path d="M{x-18} {PAD_Y+22} l8 -10 l8 8 l8 -12 l8 10 l4 -4" fill="#3c4152" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>')
        return "".join(o)
    if up < 0.35:
        k = 1 - up / 0.35
        dy = shake
        o.append(f'<g transform="translate(0 {dy:.1f})"><rect x="{x-27}" y="{PAD_Y + (1-k)*-20:.0f}" width="54" height="{34*k:.0f}" rx="12" fill="#5a6176" stroke="{OL}" stroke-width="5"/>'
                 f'<rect x="{x-20}" y="{PAD_Y+4 + (1-k)*-20:.0f}" width="40" height="{8*k:.0f}" rx="4" fill="#7c8499"/></g>')
    # release button on the front face
    o.append(f'<circle cx="{x}" cy="{PAD_Y+46}" r="9" fill="#d8dde8" stroke="{OL}" stroke-width="4"/>')
    if glint > 0:
        o.append(star_twinkle(x + 14, PAD_Y + 36, glint))
    return "".join(o)


def underseat_bags():
    o = []
    # Grumpo's purple backpack
    o.append(f'<path d="M430 {FLOOR-4} V1610 Q 430 1560 480 1560 H560 Q 610 1560 610 1610 V{FLOOR-4}Z" fill="#7a4fc4" stroke="{OL}" stroke-width="6"/>'
             f'<rect x="455" y="1640" width="130" height="70" rx="14" fill="#9466e0" stroke="{OL}" stroke-width="5"/>'
             f'<path d="M470 1672 H570" stroke="{OL}" stroke-width="4"/><rect x="510" y="1662" width="20" height="14" rx="4" fill="#d8dde8" stroke="{OL}" stroke-width="3"/>'
             f'<path d="M490 1562 Q 520 1530 550 1562" fill="none" stroke="{OL}" stroke-width="8"/>')
    # Nibbo's little yellow duffel + travel pillow
    o.append(f'<rect x="770" y="1640" width="170" height="{FLOOR-1644}" rx="40" fill="#ffc22e" stroke="{OL}" stroke-width="6"/>'
             f'<path d="M790 1680 H920" stroke="#e0951a" stroke-width="8"/><path d="M820 1642 Q 855 1600 890 1642" fill="none" stroke="{OL}" stroke-width="8"/>'
             f'<circle cx="855" cy="1700" r="16" fill="#ff7fa0" stroke="{OL}" stroke-width="4"/>')
    return "".join(o)


def broken_piece(x, y, rot):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale(1.35)"><rect x="-27" y="-17" width="54" height="34" rx="12" fill="#5a6176" stroke="{OL}" stroke-width="5"/>'
            f'<rect x="-20" y="-13" width="40" height="8" rx="4" fill="#7c8499"/>'
            f'<rect x="-14" y="15" width="28" height="44" rx="6" fill="#3c4152" stroke="{OL}" stroke-width="5"/>'
            f'<path d="M-14 58 l6 10 l6 -8 l6 10 l6 -8 l4 6" fill="#3c4152" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<circle cx="0" cy="34" r="7" fill="#d8dde8" stroke="{OL}" stroke-width="3"/></g>')


def belt_strap(ax, ay, bx, by, sag=10):
    mx, my = (ax + bx) / 2, (ay + by) / 2 + sag
    d = f"M{ax:.1f} {ay:.1f} Q {mx:.1f} {my:.1f} {bx:.1f} {by:.1f}"
    return (f'<path d="{d}" fill="none" stroke="{OL}" stroke-width="22" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="#8b93a6" stroke-width="13" stroke-linecap="round"/>')


def buckle(x, y, rot=0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})"><rect x="-22" y="-14" width="44" height="28" rx="7" fill="#e2e6ee" stroke="{OL}" stroke-width="5"/>'
            f'<rect x="-12" y="-6" width="24" height="12" rx="3" fill="#aab2c2"/></g>')


# ---------------------------------------------------------------- character extras
def grumpo_extra(x, y, s, rot, sx, sy, kind, t, red=0.0):
    if not kind:
        return ""
    ink = mix_hex(INK, "#3a0505", red)
    base = mix_hex("#9466e0", "#ff6a52", red)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s*sx:.3f} {s*sy:.3f})">']
    worried = f'<path d="M-72 -28 Q -46 -36 -16 -54 M16 -54 Q 46 -36 72 -28" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
    if kind == "strain":
        o.append(f'<path d="M-76 -40 L -18 -8 M76 -40 L 18 -8" fill="none" stroke="{ink}" stroke-width="18" stroke-linecap="round"/>'
                 f'<rect x="-40" y="58" width="80" height="34" rx="12" fill="#fff" stroke="{ink}" stroke-width="7"/>'
                 f'<path d="M-36 75 h72 M-14 60 v30 M12 60 v30" stroke="{ink}" stroke-width="4"/>')
        o.append(f'<path d="M98 -20 q12 18 0 28 q-12 -10 0 -28z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3"/>')
    elif kind == "hungry":
        o.append(f'<path d="M-72 -42 Q -46 -62 -16 -48 M16 -48 Q 46 -62 72 -42" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<path d="M-34 60 Q 0 104 34 60Z" fill="#4a0a14" stroke="{ink}" stroke-width="8" stroke-linejoin="round"/>'
                 f'<ellipse cx="0" cy="80" rx="14" ry="7" fill="#ff7a90"/>')
        dp = (t * 1.4) % 1
        o.append(f'<path d="M24 {78+dp*40:.0f} q8 14 0 22 q-8 -8 0 -22z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3" opacity="{1-dp:.2f}"/>')
    elif kind == "gulp":   # mouth wide open upward (pouring)
        o.append(f'<path d="M-72 -44 Q -46 -66 -16 -50 M16 -50 Q 46 -66 72 -44" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<ellipse cx="0" cy="72" rx="34" ry="30" fill="#4a0a14" stroke="{ink}" stroke-width="8"/>'
                 f'<ellipse cx="0" cy="86" rx="18" ry="9" fill="#ff7a90"/>')
    elif kind == "munch":
        ch = abs(math.sin(t * 16))
        o.append(f'<path d="M-72 -36 Q -46 -48 -16 -40 M16 -40 Q 46 -48 72 -36" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<circle cx="-64" cy="{62+5*ch:.1f}" r="{28+4*ch:.1f}" fill="{base}" stroke="{ink}" stroke-width="4"/>'
                 f'<circle cx="64" cy="{62+5*ch:.1f}" r="{28+4*ch:.1f}" fill="{base}" stroke="{ink}" stroke-width="4"/>'
                 f'<path d="M-20 {72+4*ch:.1f} q20 {8+6*ch:.1f} 40 0" fill="none" stroke="{ink}" stroke-width="8" stroke-linecap="round"/>')
    elif kind == "sputter":
        o.append(f'<path d="M-72 -40 Q -40 -64 -8 -44 M8 -44 Q 40 -64 72 -40" fill="none" stroke="{ink}" stroke-width="16" stroke-linecap="round"/>'
                 f'<ellipse cx="0" cy="78" rx="24" ry="22" fill="#4a0a14" stroke="{ink}" stroke-width="8"/>'
                 f'<circle cx="-64" cy="62" r="26" fill="{base}" stroke="{ink}" stroke-width="4"/><circle cx="64" cy="62" r="26" fill="{base}" stroke="{ink}" stroke-width="4"/>')
    elif kind == "hugsmug":   # eyes closed, smug grin
        o.append(f'<path d="M-60 6 h44 v30 h-44z M16 6 h44 v30 h-44z" fill="{base}"/>'
                 f'<path d="M-58 18 q20 12 40 0 M18 18 q20 12 40 0" fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M-72 -26 Q -44 -20 -16 -12 M72 -26 Q 44 -20 16 -12" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<path d="M-30 64 q34 24 64 -8" fill="none" stroke="{ink}" stroke-width="10" stroke-linecap="round"/>')
    elif kind == "dizzy":
        for ex in (-38, 38):
            o.append(f'<circle cx="{ex}" cy="16" r="21" fill="#fff" stroke="{ink}" stroke-width="3"/>'
                     f'<path d="M{ex} 16 m-12 0 a12 12 0 1 1 12 12 a8 8 0 1 1 -8 -8 a4 4 0 1 1 4 4" fill="none" stroke="{ink}" stroke-width="4" '
                     f'transform="rotate({t*720:.0f} {ex} 16)"/>')
        o.append(f'<path d="M-30 74 q10 -10 20 0 t20 0 t20 0" fill="none" stroke="{ink}" stroke-width="8" stroke-linecap="round"/>')
    elif kind == "sad":
        o.append(worried + f'<path d="M-30 82 q30 -24 60 0" fill="none" stroke="{ink}" stroke-width="9" stroke-linecap="round"/>'
                 f'<path d="M-34 36 v8 M34 36 v8" stroke="#bfefff" stroke-width="6" stroke-linecap="round"/>')
    elif kind == "squished":
        o.append(f'<path d="M-72 -40 Q -40 -64 -8 -44 M8 -44 Q 40 -64 72 -40" fill="none" stroke="{ink}" stroke-width="16" stroke-linecap="round"/>'
                 f'<path d="M-24 78 q8 -10 16 0 t16 0 t16 0" fill="none" stroke="{ink}" stroke-width="8" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


def nib_extra(x, y, r, rot, sx, sy, kind):
    if not kind:
        return ""
    f = r / 48 * 1.05
    d = "#2a1a10"
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx*f:.3f} {sy*f:.3f})">']
    if kind == "frown":
        o.append(f'<path d="M-24 -20 l13 6 M24 -20 l-13 6" stroke="{d}" stroke-width="4" stroke-linecap="round"/>'
                 f'<path d="M-8 17 q8 -7 16 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    elif kind == "sly":      # (on 'happy' eyes) raised brow + side smirk
        o.append(f'<path d="M-24 -18 q8 -6 16 -2 M8 -22 q8 -6 16 0" fill="none" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>')
    elif kind == "pressed":  # squeezed face
        o.append(f'<path d="M-22 -10 l12 6 l-12 6 M22 -10 l-12 6 l12 6" fill="none" stroke="{d}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>'
                 f'<path d="M-8 16 q4 -4 8 0 t8 0" fill="none" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>')
    elif kind == "wink":     # one eye closed (left), other open — used with blank face
        o.append(f'<path d="M-21 -4 q7 -8 14 0" fill="none" stroke="{d}" stroke-width="5" stroke-linecap="round"/>'
                 f'<ellipse cx="14" cy="-4" rx="6" ry="8" fill="{d}"/><circle cx="16" cy="-7" r="2.2" fill="#fff"/>'
                 f'<path d="M-10 10 q10 12 22 0" fill="none" stroke="{d}" stroke-width="5" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


# ---------------------------------------------------------------- states
def grumpo_state(t):
    g = dict(x=G0[0], y=G0[1], rot=0.0, sx=1.0, sy=1.0, ex="grumpy", kind=None, look=(0.6, 0), red=0.0,
             hR=None, hL=None, bag=None, piece=None)
    pad_c = (ARM_X - 8, PAD_Y - 2)
    # --- slam + push
    if t < T_SHOVE:
        p = seg(t, 0, T_SLAM)
        g["hR"] = (lerp(640, ARM_X - 14, ein(p)), lerp(1250, PAD_Y - 4, ein(p)))
        a, b = squash(t, T_SLAM, 0.25, 0.08)
        g["sx"], g["sy"] = a, b
        g["ex"] = "angry"
        g["look"] = (1, -0.2)
        if t >= T_PUSH0:
            q = seg(t, T_PUSH0, T_PUSH1)
            j = 6 * math.sin(t * 38)
            g["hR"] = (ARM_X - 14 + 10 * q + j, PAD_Y - 4)
            g["red"] = 0.6 * q
            g["ex"], g["kind"] = "x", "strain"
            g["rot"] = 4 * q + 1.5 * math.sin(t * 31)
            g["x"] = G0[0] + 12 * q
        return g
    if t < T_PRESS:
        p = seg(t, T_SHOVE, T_SHOVE + 0.15)
        g["hR"] = (lerp(ARM_X - 4, ARM_X + 6, p), PAD_Y - 4)
        g["red"] = 0.6 * (1 - seg(t, T_SHOVE + 0.2, T_SHOVE + 0.9))
        g["ex"] = "smug"
        g["look"] = (0.7, 0)
        g["rot"] = lerp(4, 7, p)
        g["x"] = G0[0] + 12
        return g
    # --- armrest flips: tip over onto Nibbo
    if t < T_SPRING:
        p = eout(seg(t, T_TIP0, T_TIP1))
        g["rot"] = lerp(7, 62, p)
        g["x"] = lerp(G0[0] + 12, 690, p)
        g["y"] = lerp(G0[1], 1360, p)
        g["ex"] = "shock"
        g["look"] = (0.6, 0.8)
        if t < T_TIP0 + 0.05:
            g["hR"] = (ARM_X + 6, PAD_Y - 4)
        if t >= T_TIP1:
            g["ex"], g["kind"] = "x", "squished"
            a, b = squash(t, T_TIP1, 0.3, 0.12)
            g["sx"], g["sy"] = b, a
        return g
    if t < T_BACK1 + 0.35:
        p = seg(t, T_SPRING, T_BACK1)
        g["rot"] = lerp(62, -14, eout(p)) + wob(t, T_BACK1, 0.5, 10, 20)
        g["x"] = lerp(690, G0[0], eout(p))
        g["y"] = lerp(1360, G0[1], eout(p)) - 70 * math.sin(math.pi * p)
        g["ex"], g["kind"] = "x", "dizzy"
        a, b = squash(t, T_BACK1, 0.3, 0.15)
        g["sx"], g["sy"] = a, b
        return g
    # --- Nibbo claims it
    if t < T_SLAM2:
        g["ex"], g["kind"] = ("x", "dizzy") if t < T_DOWN1 else ("shock", None)
        if t >= T_MAD:
            g["ex"] = "angry"
        g["look"] = (0.9, 0.3)
        g["rot"] = wob(t, T_BACK1, 0.6, 10, 20) - 14 * (1 - seg(t, T_BACK1, T_BACK1 + 0.4))
        if t > T_SLAM2 - 0.2:
            p = seg(t, T_SLAM2 - 0.2, T_SLAM2)
            g["hR"] = (lerp(640, ARM_X - 2, ein(p)), lerp(1240, PAD_Y - 14, ein(p)))
        return g
    # --- hand on top, then peanut bait
    if t < T_GRAB:
        g["hR"] = (ARM_X - 2, PAD_Y - 14)
        g["ex"] = "smug"
        g["look"] = (0.8, 0)
        a, b = squash(t, T_SLAM2, 0.25, 0.08)
        g["sx"], g["sy"] = a, b
        if t >= T_SHAKE0 - 0.15:
            g["ex"], g["kind"] = "x", "hungry"
            g["look"] = (0.9 + 0.3 * math.sin(t * 22), -0.6)
            g["rot"] = 6 * seg(t, T_SHAKE0 - 0.15, T_SHAKE0 + 0.2)
        return g
    if t < T_NOTICE:
        p = seg(t, T_GRAB, T_GRAB + 0.18)
        bx, by = lerp(800, 600, eout(p)), lerp(1215, 1185, eout(p))
        br = 0
        if t >= T_EAT0 - 0.15:
            q = seg(t, T_EAT0 - 0.15, T_EAT0 + 0.1)
            bx, by = lerp(600, 548, q), lerp(1185, 1150, q)
            br = lerp(0, 150, eio(q))
        g["bag"] = (bx, by, br)
        g["hR"] = (bx + 40, by + 20)
        g["hL"] = (bx - 40, by + 26)
        g["ex"], g["kind"] = "x", ("hungry" if t < T_EAT0 - 0.1 else "gulp")
        g["look"] = (0.4, -0.8)
        g["rot"] = lerp(6, -10, seg(t, T_GRAB, T_EAT0))
        if t >= T_EAT1 - 0.15:
            g["kind"] = "munch"
            g["look"] = (0.2, 0)
            g["rot"] = -10 + 10 * seg(t, T_EAT1 - 0.15, T_EAT1 + 0.1)
        return g
    if t < T_HUG0:
        g["ex"], g["kind"] = "shock", None
        if t < T_NOTICE + 0.35:
            g["ex"], g["kind"] = "x", "sputter"
        g["look"] = (1, 0.6)
        g["sx"], g["sy"] = squash(t, T_NOTICE, 0.3, 0.15)
        return g
    # --- hug the armrest
    if t < T_SEE:
        p = eback(seg(t, T_HUG0, T_HUG1), 1.2)
        g["rot"] = lerp(0, 24, p)
        g["x"] = lerp(G0[0], 590, p)
        g["y"] = lerp(G0[1], 1335, p)
        g["hR"] = (lerp(640, ARM_X + 26, p), lerp(1300, PAD_Y + 18, p))
        g["hL"] = (lerp(560, ARM_X - 26, p), lerp(1380, PAD_Y + 30, p))
        g["ex"], g["kind"] = ("angry", None) if t < T_HUG1 else ("x", "hugsmug")
        g["red"] = 0.25 * (1 - seg(t, T_HUG1, T_HUG1 + 0.8))
        if T_CHIME <= t < T_CHIME + 1.0 and t >= T_HUG1:
            g["ex"], g["kind"] = "x", "hugsmug"
        return g
    if t < T_JUMP0:
        g["rot"], g["x"], g["y"] = 24, 590, 1335
        g["hR"] = (ARM_X + 26, PAD_Y + 18)
        g["hL"] = (ARM_X - 26, PAD_Y + 30)
        g["ex"] = "shock"
        g["look"] = (1, -0.2)
        g["sx"], g["sy"] = squash(t, T_SEE, 0.3, 0.12)
        if t >= T_SEE + 0.3:
            g["ex"] = "angry"
        return g
    # --- jump to follow -> belt yank -> armrest snaps off
    if t < T_YANK1:
        if t < T_JUMP1:
            p = eout(seg(t, T_JUMP0, T_JUMP1))
            g["x"], g["y"], g["rot"] = lerp(590, 720, p), lerp(1335, 1110, p), lerp(24, 30, p)
            g["ex"] = "angry"
            g["sx"], g["sy"] = lerp(1, 0.9, p), lerp(1, 1.12, p)
            g["hR"] = (g["x"] + 150, g["y"] - 40)
        else:
            p = ein(seg(t, T_JUMP1, T_YANK1))
            g["x"], g["y"], g["rot"] = lerp(720, G0[0] + 20, p), lerp(1110, G0[1], p), lerp(30, -6, p)
            g["ex"] = "shock"
            g["hR"] = (lerp(g["x"] + 150, ARM_X - 6, p), lerp(g["y"] - 40, PAD_Y - 6, p))
        g["look"] = (1, 0)
        return g
    # landed: holds broken piece
    g["x"], g["y"] = G0[0] + 20, G0[1]
    g["sx"], g["sy"] = squash(t, T_YANK1, 0.35, 0.25)
    g["rot"] = wob(t, T_YANK1, 0.6, 8, 22)
    if t < T_SNAP:
        g["hR"] = (ARM_X - 6, PAD_Y - 6)
        g["ex"] = "shock"
    else:
        p = eout(seg(t, T_SNAP, T_SNAP + 0.3))
        px, py = lerp(ARM_X - 6, 640, p), lerp(PAD_Y - 6, 1190, p) - 60 * math.sin(math.pi * p)
        prot = lerp(0, -25, p)
        if t > T_SNAP + 1.0:
            q = seg(t, T_SNAP + 1.0, T_SNAP + 1.6)
            px, py, prot = lerp(640, 610, q), lerp(1190, 1260, q), lerp(-25, -60, q)
        g["piece"] = (px, py, prot)
        g["hR"] = (px + 30, py + 30)
        g["hL"] = (px - 30, py + 34)
        g["ex"] = "shock"
        g["look"] = (0.6, -0.5)
        if t > T_SNAP + 1.0:
            g["ex"], g["kind"] = "x", "sad"
            g["look"] = (0.3, 0.5)
    return g


def nibbo_state(t):
    n = dict(x=N0[0], y=N0[1], rot=0.0, sx=1.0, sy=1.0, ex="happy", kind=None, hL=None, hR=None,
             belted=True, bag=None, lying=False)
    if t < T_SHOVE:
        p = seg(t, 0, T_SLAM)
        n["hL"] = (lerp(760, ARM_X + 14, ein(p)), lerp(1250, PAD_Y - 2, ein(p)))
        n["sx"], n["sy"] = squash(t, T_SLAM, 0.25, 0.1)
        n["ex"], n["kind"] = "happy", "frown"
        if t >= T_PUSH0:
            q = seg(t, T_PUSH0, T_PUSH1)
            j = 6 * math.sin(t * 38)
            n["hL"] = (ARM_X + 14 + 10 * q + j, PAD_Y - 2)
            n["ex"], n["kind"] = "nervous", None
            n["rot"] = -3 * q + 1.5 * math.sin(t * 29)
        return n
    if t < T_PRESS - 0.2:
        p = seg(t, T_SHOVE, T_BONK)
        n["rot"] = lerp(0, 26, eout(p))
        n["x"] = lerp(N0[0], N0[0] + 50, eout(p))
        if t < T_SHOVE + 0.35:
            q = seg(t, T_SHOVE, T_SHOVE + 0.35)
            n["hL"] = (lerp(ARM_X + 20, 820, q), lerp(PAD_Y, 1180, q) - 80 * math.sin(math.pi * q))
        n["ex"] = "wow"
        if t >= T_BONK:
            n["ex"] = "dizzy"
            r = seg(t, T_REC0, T_REC1)
            n["rot"] = 26 * (1 - eio(r)) + wob(t, T_BONK, 0.4, 6, 30)
            n["x"] = lerp(N0[0] + 50, N0[0], eio(r))
            n["sx"], n["sy"] = squash(t, T_BONK, 0.25, 0.18)
            if t >= T_REC1:
                n["ex"], n["kind"] = "happy", "frown"
            if t >= T_IDEA:
                n["ex"], n["kind"] = "wow", None
        return n
    if t < T_TIP0:
        p = seg(t, T_PRESS - 0.2, T_PRESS)
        n["hL"] = (lerp(790, ARM_X + 10, eio(p)), lerp(1460, PAD_Y + 46, eio(p)))
        n["ex"], n["kind"] = "happy", "sly"
        return n
    if t < T_SPRING:
        p = eout(seg(t, T_TIP0 + 0.1, T_TIP1))
        n["x"] = lerp(N0[0], 905, p)
        n["sx"], n["sy"] = lerp(1, 0.6, p), lerp(1, 1.16, p)
        n["ex"], n["kind"] = ("wow", None) if p < 0.5 else ("x", "pressed")
        return n
    if t < T_CLAIM:
        p = seg(t, T_SPRING, T_SPRING + 0.35)
        k = math.sin(p * math.pi * 2.5) * math.exp(-p * 3) if p < 1 else 0
        n["x"] = lerp(905, N0[0], eout(p))
        n["sx"], n["sy"] = lerp(0.6, 1, eout(p)) + 0.25 * k, lerp(1.16, 1, eout(p)) - 0.2 * k
        n["ex"], n["kind"] = "joy", None
        if t >= T_DOWN0 - 0.15:
            q = seg(t, T_DOWN0 - 0.15, T_DOWN1)
            n["hL"] = (lerp(780, ARM_X + 4, q), lerp(1300, PAD_Y - 6, q) - 60 * math.sin(math.pi * q))
            n["ex"], n["kind"] = "happy", "sly"
        return n
    if t < T_BAG0:
        n["hL"] = (ARM_X + 8, PAD_Y - 2)
        n["ex"] = "joy" if t < T_SLAM2 else "uhoh"
        if t >= T_SLAM2:
            n["sx"], n["sy"] = squash(t, T_SLAM2, 0.25, 0.15)
        if t >= T_SLAM2 + 0.4:
            n["ex"], n["kind"] = "happy", "frown"
        return n
    if t < T_SPRAWL0:
        n["hL"] = (ARM_X + 8, PAD_Y - 2)
        n["ex"], n["kind"] = "happy", "sly"
        p = seg(t, T_BAG0, T_BAG1)
        bx, by = lerp(990, 800, eout(p)), lerp(1560, 1215, eout(p))
        br = 0
        if T_SHAKE0 <= t < T_SHAKE1:
            br = 14 * math.sin((t - T_SHAKE0) * 30)
            bx += 8 * math.sin((t - T_SHAKE0) * 30)
        if t < T_GRAB:
            n["bag"] = (bx, by, br)
            n["hR"] = (bx + 30, by + 40)
        else:
            q = seg(t, T_GRAB, T_GRAB + 0.25)
            n["hR"] = (lerp(830, 960, q), lerp(1255, 1380, q))
        return n
    if t < T_HUG0:
        p = eio(seg(t, T_SPRAWL0, T_SPRAWL1))
        n["x"] = lerp(N0[0], 815, p)
        n["rot"] = lerp(0, -16, p)
        n["hL"] = (lerp(ARM_X + 8, ARM_X - 10, p), PAD_Y - 2)
        n["hR"] = (lerp(960, ARM_X + 30, p), lerp(1380, PAD_Y - 4, p))
        n["ex"], n["kind"] = ("joy", None) if p > 0.3 else ("happy", "sly")
        if t >= T_NOTICE + 0.1:
            n["ex"], n["kind"] = "wow", None
        return n
    if t < T_POP:
        p = eback(seg(t, T_HUG0, T_HUG1), 1.2)
        n["x"] = lerp(815, 912, p)
        n["rot"] = lerp(-16, 8, p)
        n["sx"], n["sy"] = lerp(1, 0.72, p), lerp(1, 1.12, p)
        n["ex"], n["kind"] = ("wow", None) if t < T_HUG1 else ("x", "pressed")
        if t >= T_HUG1 + 0.4:
            n["ex"], n["kind"] = "happy", "frown"
        if t >= T_LOOKUP:
            n["ex"], n["kind"] = "wow", None
        if t >= T_LOOKUP + 0.25:
            n["ex"], n["kind"] = "joy", None
        if T_UNBUCK - 0.2 <= t < T_UNBUCK + 0.2:
            q = math.sin(math.pi * seg(t, T_UNBUCK - 0.2, T_UNBUCK + 0.2))
            n["hR"] = (lerp(990, 905, q), lerp(1400, 1430, q))
        n["belted"] = t < T_UNBUCK
        return n
    n["belted"] = False
    if t < T_HOP1:
        p = seg(t, T_POP, T_HOP1)
        n["x"] = lerp(912, 1115, eio(p))
        n["y"] = lerp(N0[1], FLOOR - NR, p) - 230 * math.sin(math.pi * p)
        n["sx"], n["sy"] = lerp(0.72, 1, eout(p * 3) if p < 0.33 else 1), lerp(1.12, 1, min(1, p * 3))
        n["rot"] = 360 * eio(p) * 0
        n["ex"] = "joy"
        return n
    if t < T_HOP2:
        p = seg(t, T_HOP1, T_HOP2)
        n["x"] = lerp(1115, 1370, eio(p))
        n["y"] = lerp(FLOOR - NR, 1340, p) - 200 * math.sin(math.pi * p)
        n["ex"] = "joy"
        if p < 0.15:
            n["sx"], n["sy"] = 1.15, 0.85
        return n
    if t < T_LIE0:
        n["x"], n["y"] = 1370, 1340
        n["sx"], n["sy"] = squash(t, T_HOP2, 0.25, 0.15)
        n["ex"] = "happy"
        q = seg(t, T_LIFT - 0.1, T_LIFT + 0.1)
        n["hR"] = (lerp(1460, ARM_C, q), lerp(1380, PAD_Y + 30, q))
        return n
    n["lying"] = True
    p = eout(seg(t, T_LIE0, T_LIE1))
    n["x"], n["y"] = lerp(1370, 1480, p), lerp(1340, 1360, p)
    n["rot"] = lerp(0, -10, p)
    n["sx"], n["sy"] = lerp(1, 1.4, p), lerp(1, 0.8, p)
    n["ex"], n["kind"] = "joy", None
    n["hL"] = None
    n["hR"] = None
    if t >= T_WAVE0:
        q = (t - T_WAVE0)
        k = min(1, q / 0.25)
        n["hR"] = (1705 + 24 * k * math.sin(q * 14), lerp(1330, 1225, k))
        n["ex"], n["kind"] = "x", "wink"
    return n


# ---------------------------------------------------------------- camera
CK = [(0.0, (690, 1325, 1.62)), (1.2, (690, 1335, 1.65)), (T_PUSH1, (695, 1355, 1.85)), (T_BONK + 0.1, (730, 1345, 1.69)),
      (4.4, (720, 1355, 1.72)), (T_PRESS, (705, 1370, 1.85)), (T_TIP1 + 0.1, (720, 1335, 1.67)), (T_CLAIM, (700, 1330, 1.65)),
      (T_SLAM2, (690, 1345, 1.77)), (T_BAG1, (690, 1335, 1.72)), (T_SHAKE1, (660, 1305, 1.79)), (T_EAT1, (650, 1295, 1.79)),
      (T_NOTICE + 0.3, (680, 1325, 1.69)), (T_HUG1 + 0.2, (720, 1345, 1.72)), (T_CHIME - 0.1, (720, 1335, 1.72)),
      (T_CHIME + 0.35, (705, 1185, 1.62)), (T_LOOKUP + 0.3, (720, 1185, 1.62)), (T_UNBUCK, (800, 1315, 1.62)),
      (T_POP + 0.1, (840, 1325, 1.57)), (T_HOP1 + 0.2, (1250, 1355, 1.53)), (T_LIE1, (1500, 1355, 1.59)), (15.75, (1515, 1360, 1.65)),
      (16.3, (650, 1325, 1.65)), (T_JUMP1, (660, 1275, 1.57)), (T_SNAP + 0.2, (600, 1315, 1.69)), (19.0, (590, 1315, 1.87)),
      (19.6, (1500, 1345, 1.65)), (DUR, (1505, 1345, 1.73))]
SHAKES = [(T_SLAM, 8, 0.25), (T_BONK, 6, 0.25), (T_FLIP1, 5, 0.2), (T_TIP1, 9, 0.3), (T_SLAM2, 6, 0.2), (T_HUG1, 6, 0.25),
          (T_YANK1, 16, 0.45), (T_SNAP, 8, 0.25)]


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
    # constant gentle cabin vibration
    return cx + amp * math.sin(t * 93), cy + amp * math.cos(t * 79) + 1.2 * math.sin(t * 13), z


# ---------------------------------------------------------------- frame
def frame(t):
    ctx = Ctx()
    g = grumpo_state(t)
    n = nibbo_state(t)
    sign_on = t < T_CHIME + 0.08
    L = [cabin(t, sign_on)]

    # main armrest state
    up = 0.0
    if T_FLIP0 <= t < T_DOWN1:
        up = eout(seg(t, T_FLIP0, T_FLIP1)) * (1 - eio(seg(t, T_DOWN0, T_DOWN1)))
    broken = t >= T_SNAP
    shake = 0.0
    if T_PUSH0 <= t < T_SHOVE:
        shake = 3 * math.sin(t * 41)
    shake += wob(t, T_SLAM, 0.4, 4, 40) + wob(t, T_DOWN1, 0.35, 5, 40) + wob(t, T_SLAM2, 0.3, 4, 40)
    glint = seg(t, T_IDEA - 0.05, T_IDEA + 0.5)
    up_c = eout(seg(t, T_LIFT - 0.05, T_LIFT + 0.1))

    # backrests + folded armrests (behind chars)
    for x0, x1 in SEATS:
        L.append(backrest(x0, x1))
    L.append(armrest_back(ARM_X, up))
    L.append(armrest_back(ARM_C, up_c))

    # characters
    L.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "up", g["look"], g["rot"], g["sx"], g["sy"], drink=False, t=t))
    L.append(grumpo_extra(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], g["kind"], t, g["red"]))
    if n["lying"]:
        pp = eout(seg(t, T_LIE0, T_LIE1))
        L.append(f'<g transform="translate(1318 {1385-10*pp:.0f}) rotate(-8) scale({0.6+0.4*pp:.2f})"><path d="M-70 -34 Q 0 -52 70 -34 Q 84 0 70 34 Q 0 52 -70 34 Q -84 0 -70 -34Z" fill="#f4f6fb" stroke="{OL}" stroke-width="6"/>'
                 f'<path d="M-40 -10 q40 14 80 0" fill="none" stroke="#c9d0de" stroke-width="5" stroke-linecap="round"/></g>')
    L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"], rot=n["rot"], sx=n["sx"], sy=n["sy"]))
    L.append(nib_extra(n["x"], n["y"], NR, n["rot"], n["sx"], n["sy"], n["kind"]))
    if n["lying"]:
        bp = eout(seg(t, T_LIE1 - 0.1, T_LIE1 + 0.3))
        if bp > 0:
            L.append(f'<g opacity="{bp:.2f}"><path d="M{1625-40*(1-bp):.0f} 1300 Q 1720 1280 1810 1310 L1820 1450 Q 1720 1470 1620 1450Z" fill="#e8475e" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
                     f'<path d="M1645 1340 Q 1720 1322 1805 1346 M1645 1400 Q 1720 1384 1810 1404" fill="none" stroke="#ffffff" stroke-width="8" opacity="0.7"/></g>')

    # seat belts
    ga, gb = (G0[0] - 110, CUSH - 12), (G0[0] + 110, CUSH - 12)
    bk = bodypt(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], 0, 96)
    L.append(belt_strap(*ga, *bk, 8) + belt_strap(*bk, *gb, 8) + buckle(*bk, g["rot"] * 0.5))
    na, nb_ = (N0[0] - 102, CUSH - 10), (N0[0] + 102, CUSH - 10)
    if n["belted"]:
        nbk = bodypt(n["x"], n["y"], 1, n["rot"], n["sx"], n["sy"], 0, NR * 0.74)
        L.append(belt_strap(*na, *nbk, 6) + belt_strap(*nbk, *nb_, 6) + buckle(*nbk, n["rot"] * 0.5))
    else:
        L.append(belt_strap(na[0], na[1], na[0] + 34, na[1] + 70, 0) + belt_strap(nb_[0], nb_[1], nb_[0] - 30, nb_[1] + 70, 0) +
                 buckle(nb_[0] - 30, nb_[1] + 74, 80))
    for x0, x1 in SEATS[2:]:
        cx_ = (x0 + x1) / 2
        L.append(belt_strap(cx_ - 120, CUSH + 6, cx_ - 70, CUSH + 70, 0) + belt_strap(cx_ + 120, CUSH + 6, cx_ + 70, CUSH + 70, 0))

    # cushion fronts + armrest pads (in front of bodies)
    for x0, x1 in SEATS:
        L.append(cushion_front(x0, x1))
    L.append(underseat_bags())
    L.append(armrest_front(SEATS[0][0] + 6))
    L.append(armrest_front(AISLE[0] - 4))
    L.append(armrest_front(ARM_X, up, shake, broken, glint))
    L.append(armrest_front(AISLE[1] + 4))
    L.append(armrest_front(ARM_C, up_c))
    L.append(armrest_front(SEATS[3][1] - 4))
    if broken and t < T_SPRINGOUT + 1.5:
        pass
    if t >= T_SPRINGOUT:
        p = eback(seg(t, T_SPRINGOUT, T_SPRINGOUT + 0.25), 2.5)
        L.append(spring_coil(ARM_X, PAD_Y + 22, 110 * p, wob(t, T_SPRINGOUT, 1.2, 14, 16)))

    # ---- arms + hands (Grumpo)
    for side, key in ((1, "hR"), (-1, "hL")):
        if g[key]:
            sx_, sy_ = bodypt(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], side * 112, 30)
            hx, hy = g[key]
            L.append(arm(sx_, sy_, hx, hy, INK, 14, 24))
    if g["bag"]:
        bx, by, br = g["bag"]
        L.append(peanut_bag(bx, by, br, 1.0, open_=t >= T_EAT0 - 0.2))
    if g["piece"]:
        L.append(broken_piece(*g["piece"]))
    for key in ("hR", "hL"):
        if g[key]:
            L.append(hand(*g[key], mix_hex(GFILL, "#ff6a52", g["red"]), OL, 18))

    # ---- arms + hands (Nibbo)
    for side, key in ((-1, "hL"), (1, "hR")):
        if n[key]:
            sx_, sy_ = bodypt(n["x"], n["y"], 1, n["rot"], n["sx"], n["sy"], side * 96, 26)
            hx, hy = n[key]
            L.append(arm(sx_, sy_, hx, hy, NS, 11, 18))
    if n["bag"]:
        bx, by, br = n["bag"]
        L.append(peanut_bag(bx, by, br))
    for key in ("hL", "hR"):
        if n[key]:
            L.append(hand(*n[key], NB, NS, 15))

    # ---- effects
    # elbow slam impact
    L.append(impact(ARM_X, PAD_Y - 10, seg(t, T_SLAM, T_SLAM + 0.25)))
    # glare lightning
    if T_ZAP0 <= t < T_ZAP1:
        op = min(1, seg(t, T_ZAP0, T_ZAP0 + 0.1) * 1) * (1 - seg(t, T_ZAP1 - 0.15, T_ZAP1))
        L.append(zap(g["x"] + 60, g["y"] + 5, n["x"] - 30, n["y"] - 10, t, op))
    if T_PUSH0 <= t < T_SHOVE:
        for k in range(3):
            p = ((t - T_PUSH0) * 2.2 + k / 3) % 1
            L.append(sweat(n["x"] + 60 + 20 * k, n["y"] - 90, p))
    L.append(impact(n["x"] + 110, n["y"] - 20, seg(t, T_BONK, T_BONK + 0.25), "#ffffff"))
    L.append(symbol(n["x"] + 20, n["y"] - 150, "!", seg(t, T_IDEA, T_IDEA + 0.55), "#ffb02a"))
    L.append(impact(ARM_X + 10, PAD_Y + 46, seg(t, T_PRESS, T_PRESS + 0.2), "#ffffff"))
    L.append(impact(820, 1330, seg(t, T_TIP1, T_TIP1 + 0.25), "#ffffff"))
    L.append(impact(ARM_X, PAD_Y - 20, seg(t, T_SLAM2, T_SLAM2 + 0.2)))
    L.append(symbol(g["x"] + 30, g["y"] - 170, "!", seg(t, T_DOWN1 + 0.1, T_DOWN1 + 0.6)))
    # peanuts pouring into Grumpo's mouth
    if T_EAT0 <= t < T_EAT1:
        bx, by, br = g["bag"] if g["bag"] else (548, 1150, 150)
        mx, my = bodypt(g["x"], g["y"], GS, g["rot"], 1, 1, 0, 70)
        for k in range(7):
            p = ((t - T_EAT0) * 3.2 + k / 7) % 1
            ox, oy = bx - 10, by + 40
            L.append(peanut(lerp(ox, mx, p) + 8 * math.sin(k * 2.1), lerp(oy, my, p), k * 50 + t * 400, 0.9))
    if T_NOTICE <= t < T_NOTICE + 0.6:
        q = seg(t, T_NOTICE, T_NOTICE + 0.6)
        mx, my = bodypt(g["x"], g["y"], GS, g["rot"], 1, 1, 0, 70)
        for k in range(6):
            a = math.radians(-150 + k * 24)
            L.append(peanut(mx + 220 * q * math.cos(a), my + 220 * q * math.sin(a) + 260 * q * q, k * 70 + q * 500, 0.9))
        L.append(symbol(g["x"] + 40, g["y"] - 190, "!", seg(t, T_NOTICE, T_NOTICE + 0.6)))
    if T_NOTICE - 0.05 <= t < T_NOTICE + 0.8:   # dropped bag falling
        q = seg(t, T_NOTICE - 0.05, T_NOTICE + 0.5)
        L.append(peanut_bag(lerp(548, 470, q), lerp(1150, 1480, ein(q)), lerp(150, 230, q), 1.0, True))
    if T_SPRAWL1 <= t < T_NOTICE:
        L.append(star_twinkle(n["x"] + 70, n["y"] - 110, seg(t, T_SPRAWL1, T_SPRAWL1 + 0.5)))
    L.append(impact(820, 1340, seg(t, T_HUG1, T_HUG1 + 0.25), "#ffffff"))
    # chime glow on the sign
    if T_CHIME <= t < T_CHIME + 0.6:
        q = seg(t, T_CHIME, T_CHIME + 0.6)
        L.append(f'<circle cx="{ARM_X}" cy="942" r="{60+80*q:.0f}" fill="none" stroke="#ffffff" stroke-width="{10*(1-q):.1f}" opacity="{1-q:.2f}"/>')
    L.append(symbol(n["x"] + 20, n["y"] - 160, "!", seg(t, T_LOOKUP, T_LOOKUP + 0.5), "#ffb02a"))
    L.append(impact(n["x"], n["y"] + 80, seg(t, T_UNBUCK, T_UNBUCK + 0.2), "#ffffff"))
    L.append(impact(905, 1340, seg(t, T_POP, T_POP + 0.25)))
    if T_POP <= t < T_HOP2:
        L.append(speed_lines(n["x"] - 40, n["y"], 0, 0.7))
    L.append(impact(ARM_C, PAD_Y + 10, seg(t, T_LIFT, T_LIFT + 0.2), "#ffffff"))
    if n["lying"] and t >= T_LIE1 + 0.3:
        L.append(zzz(1540, 1190, t, seg(t, T_LIE1 + 0.3, T_LIE1 + 0.8) * (1 if t < T_WAVE0 else 1 - seg(t, T_WAVE0, T_WAVE0 + 0.3))))
    L.append(symbol(g["x"] + 40, g["y"] - 180, "!", seg(t, T_SEE, T_SEE + 0.6)))
    if T_JUMP0 <= t < T_JUMP1:
        L.append(speed_lines(g["x"] - 60, g["y"] + 60, -40, 0.8))
    L.append(impact(g["x"], g["y"] + 40, seg(t, T_YANK1, T_YANK1 + 0.3), "#ffffff"))
    L.append(impact(ARM_X, PAD_Y, seg(t, T_SNAP, T_SNAP + 0.25)))
    if T_SNAP <= t < T_SNAP + 0.5:
        q = seg(t, T_SNAP, T_SNAP + 0.5)
        for k in range(5):
            a = math.radians(-160 + k * 35)
            L.append(f'<rect x="{ARM_X+120*q*math.cos(a):.0f}" y="{PAD_Y+120*q*math.sin(a)+200*q*q:.0f}" width="12" height="8" fill="#3c4152" stroke="{OL}" stroke-width="2" opacity="{1-q:.2f}"/>')

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{defs()}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g>'
           f'<rect width="{W}" height="{H}" fill="url(#vig)"/></svg>')
    return overlay(svg, hook_title(t + 0.12, "Grumpo vs Nibbo:", "THE ARMREST"))


def build_sfx():
    # cabin ambience throughout
    k = 0.0
    while k < DUR:
        sfx(k, "cabin_hum", 0.55, 1.0)
        k += 2.0
    sfx(0.0, "whoosh", 0.6, 1.3)
    sfx(T_SLAM - 0.02, "thud", 1.0, 0.9)
    sfx(T_SLAM, "bonk", 0.6, 0.8)
    sfx(T_ZAP0, "zip", 0.7, 1.4)
    sfx(T_ZAP0 + 0.3, "zip", 0.6, 1.6)
    sfx(T_PUSH0, "strain", 0.9, 1.0)
    sfx(T_PUSH0 + 0.85, "strain", 0.9, 1.15)
    for k in range(8):
        sfx(T_PUSH0 + k * 0.26, "squeak", 0.25, 1.4 + 0.05 * (k % 3))
    sfx(T_PUSH0 + 1.3, "creak", 0.5, 1.4)
    sfx(T_SHOVE, "whoosh", 0.8, 1.2)
    sfx(T_BONK, "bonk", 1.0, 1.1)
    sfx(T_BONK + 0.05, "boing", 0.4, 1.6)
    sfx(T_SHOVE + 0.3, "cool", 0.35, 1.0)
    sfx(T_IDEA, "ding", 0.6, 1.3)
    sfx(T_IDEA + 0.05, "shine", 0.4, 1.2)
    sfx(T_PRESS - 0.18, "sneak", 0.35, 1.4)
    sfx(T_PRESS, "click", 0.9, 1.0)
    sfx(T_FLIP0, "seat_clack", 0.9, 1.1)
    sfx(T_TIP0, "gasp", 0.6, 0.9)
    sfx(T_TIP0 + 0.05, "slide_down", 0.6, 1.0)
    sfx(T_TIP1, "squish", 0.9, 0.8)
    sfx(T_TIP1, "thud", 0.6, 1.1)
    sfx(T_TIP1 + 0.2, "squeak", 0.4, 1.8)
    sfx(T_SPRING, "boing", 1.0, 0.9)
    sfx(T_SPRING + 0.05, "whoosh", 0.6, 1.0)
    sfx(T_BACK1, "thud", 0.6, 1.0)
    sfx(T_BACK1 + 0.05, "wobble", 0.4, 1.4)
    sfx(T_DOWN1, "thunk", 0.9, 1.0)
    sfx(T_CLAIM, "pop", 0.5, 1.3)
    sfx(T_DOWN1 + 0.1, "gasp", 0.5, 1.0)
    sfx(T_SLAM2 - 0.15, "whoosh", 0.5, 1.4)
    sfx(T_SLAM2, "thud", 0.9, 1.0)
    sfx(T_SLAM2 + 0.05, "squeak", 0.6, 1.2)
    sfx(T_BAG0 + 0.1, "rustle", 0.7, 1.1)
    sfx(T_SHAKE0, "shaker", 0.9, 1.0)
    sfx(T_SHAKE0 + 0.1, "grumble", 0.45, 1.0)
    sfx(T_GRAB, "whoosh", 0.7, 1.5)
    sfx(T_GRAB + 0.05, "rustle", 0.6, 1.3)
    sfx(T_EAT0 - 0.1, "rustle", 0.5, 1.0)
    sfx(T_EAT0, "popcorn", 0.6, 0.7)
    sfx(T_EAT0 + 0.3, "munch", 0.8, 1.0)
    sfx(T_EAT0 + 0.65, "munch", 0.7, 1.1)
    sfx(T_SPRAWL0 + 0.1, "slide_up", 0.4, 1.2)
    sfx(T_SPRAWL1, "shine", 0.5, 1.4)
    sfx(T_NOTICE, "spit", 0.9, 1.0)
    sfx(T_NOTICE + 0.02, "gasp", 0.6, 1.0)
    sfx(T_NOTICE + 0.1, "popcorn", 0.4, 1.3)
    sfx(T_NOTICE + 0.45, "plop", 0.4, 1.4)
    sfx(T_HUG0, "whoosh", 0.8, 1.0)
    sfx(T_HUG1, "squish", 1.0, 0.9)
    sfx(T_HUG1 + 0.03, "thud", 0.5, 1.2)
    sfx(T_HUG1 + 0.25, "squeak", 0.4, 1.6)
    sfx(T_CHIME, "plane_chime", 1.0, 1.0)
    sfx(T_LOOKUP, "blip", 0.5, 1.3)
    sfx(T_UNBUCK, "buckle", 1.0, 1.0)
    sfx(T_POP, "cork_pop", 0.9, 1.0)
    sfx(T_POP + 0.05, "hop", 0.6, 1.0)
    sfx(T_HOP1, "tiptoe", 0.7, 1.0)
    sfx(T_HOP1 + 0.03, "hop", 0.6, 1.2)
    sfx(T_HOP2, "plop", 0.6, 1.0)
    sfx(T_LIFT, "seat_clack", 0.8, 1.2)
    sfx(T_LIE0 + 0.05, "stretch", 0.5, 1.2)
    sfx(T_LIE1, "plop", 0.5, 0.9)
    sfx(T_LIE1 + 0.1, "cool", 0.5, 1.1)
    sfx(15.4, "snore", 0.4, 1.3)
    sfx(T_SEE, "gasp", 0.7, 0.9)
    sfx(T_SEE + 0.3, "grumble", 0.6, 0.8)
    sfx(T_JUMP0, "boing", 0.6, 1.2)
    sfx(T_JUMP0 + 0.05, "whoosh", 0.7, 1.0)
    sfx(T_JUMP0 + 0.15, "stretch", 0.9, 0.9)
    sfx(T_JUMP1, "twang", 1.0, 0.9)
    sfx(T_YANK1, "thud", 1.0, 0.8)
    sfx(T_YANK1 + 0.02, "boing", 0.7, 0.7)
    sfx(T_SNAP, "snap", 1.0, 1.0)
    sfx(T_SNAP + 0.05, "clank", 0.7, 1.1)
    sfx(T_SNAP + 0.5, "blip_down", 0.6, 0.9)
    sfx(T_SNAP + 1.0, "deflate", 0.5, 1.0)
    sfx(T_SPRINGOUT, "boing", 0.9, 1.5)
    sfx(T_SPRINGOUT + 0.4, "boing", 0.4, 1.9)
    sfx(19.1, "whoosh", 0.5, 0.9)
    sfx(T_WAVE0 + 0.1, "pop", 0.5, 1.5)
    sfx(T_WAVE0 + 0.2, "ding", 0.4, 1.8)
    sfx(20.4, "snore", 0.35, 1.3)
