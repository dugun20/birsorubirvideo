"""Grumpo & Nibbo — Episode 17: Campfire vs 1 Mosquito (night campfire, 60 fps).

Structure D (common enemy): Grumpo and Nibbo roast marshmallows at a campfire; ONE mosquito torments them.
  - It lands on Grumpo's head -> Nibbo's rubber-arm SLAP hits Grumpo (mosquito already gone). Dizzy stars.
  - It lands on Nibbo's cheek -> Grumpo's revenge windmill slap: Nibbo spins like a top (mosquito gone again).
  - Meanwhile both marshmallows caught fire -> frantic blowing -> two charcoal lumps.
  - The mosquito mocks them over the fire. They look at each other and NOD: team-up.
    Double slap from both sides -> it zips up, they clap each other's hands (accidental high five).
  - Grumpo's idea: fresh marshmallows (he tosses one onto Nibbo's stick), roast them gooey as bait.
    Mosquito comes sniffing between the two tips -> wink -> both sticks swing in: SQUISH, mosquito trapped in goo.
    Grumpo flicks the gooey blob onto a tree trunk (it sticks there, wings flapping).
Ending (they make peace / share): a real high five; Grumpo's bag has only ONE marshmallow left — he pulls it in half
and hands Nibbo the other half. Both roast side by side, Grumpo with a tiny blush-smile.
"""
import math, sys, os, random
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

GROUND = 1700
FX = 540                     # fire centre
GX, GY = 335.0, GROUND - GR
NX, NY = 745.0, GROUND - NR
G_TIP0 = (488.0, 1468.0)      # Grumpo's marshmallow tip (resting over fire)
N_TIP0 = (592.0, 1468.0)
G_HAND0 = (GX + 118, GY + 34)
N_HAND0 = (NX - 100, NY + 34)
TREE_X = 40                  # tree trunk on the left (splat target)
SPLAT = (78.0, 1360.0)
BAG = (175.0, GROUND - 46)

# ---- times
T_LAND1 = 1.05
T_NSEE = 1.35
T_WIND1_0, T_WIND1_1 = 1.5, 1.95
T_ML1 = 1.98
T_SLAP1 = 2.08
T_RET1 = 2.45
T_GLARE = 2.95
T_LAND2 = 3.6
T_GSMUG = 3.75
T_WIND2_0, T_WIND2_1 = 3.85, 4.35
T_ML2 = 4.36
T_SLAP2 = 4.45
T_SPIN1 = 5.05
T_IGN = 4.7                  # marshmallows catch fire
T_NOTICE = 5.6
T_BLOW0, T_BLOW1 = 5.8, 6.55
T_OUT = 6.55
T_SAD0 = 6.7
T_M3 = 7.2
T_ANGRY3 = 7.55
T_LOOK = 8.0
T_NOD0, T_NOD1 = 8.2, 8.6
T_WIND3_0, T_WIND3_1 = 8.65, 9.0
T_ML3 = 9.02
T_CLAP = 9.1
T_CLAPUP = 9.45
T_UNCLAP = 9.85
T_IDEA = 10.0
T_FRESH = 10.35
T_TOSS0, T_TOSS1 = 10.55, 11.05
T_ROAST0, T_ROAST1 = 11.15, 12.4
T_M4 = 11.4
T_HOVER = 12.4
T_WINK = 12.55
T_SWING0, T_SQUISH = 12.85, 13.05
T_PULL0, T_PULL1 = 13.75, 14.15
T_FLICK0, T_FLICK1 = 14.3, 14.85
T_HI5_0, T_HI5 = 15.15, 15.45
T_LAUGH1 = 16.0
T_LAST0 = 16.15
T_LAST1 = 16.6
T_SPLIT0, T_SPLIT1 = 16.95, 17.5
T_GIVE0, T_GIVE1 = 17.6, 18.05
T_ONSTICK = 18.3
T_COZY = 18.55
DUR = 20.2

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


# ---------------------------------------------------------------- scene
def defs():
    return ('<linearGradient id="skyN" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d1430"/><stop offset="0.6" stop-color="#1f2a58"/><stop offset="1" stop-color="#3a3f72"/></linearGradient>'
            '<radialGradient id="fireGlow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ffb347" stop-opacity="0.55"/><stop offset="0.5" stop-color="#ff8a2a" stop-opacity="0.18"/><stop offset="1" stop-color="#ff8a2a" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="warm" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ff9a3a" stop-opacity="0.22"/><stop offset="1" stop-color="#ff9a3a" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="moonG" cx="0.5" cy="0.5" r="0.5"><stop offset="0.35" stop-color="#fff8dc" stop-opacity="0.5"/><stop offset="1" stop-color="#fff8dc" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="vig" cx="0.5" cy="0.58" r="0.8"><stop offset="0.55" stop-color="#05060f" stop-opacity="0"/><stop offset="1" stop-color="#05060f" stop-opacity="0.55"/></radialGradient>')


def pine_dark(x, y, s=1.0, col="#16233a"):
    o = []
    for (w, h, dy) in [(110, 120, 0), (90, 110, -80), (62, 100, -156)]:
        yy = y + dy * s
        o.append(f'<path d="M{x-w*s:.0f} {yy:.0f} L{x:.0f} {yy-h*s*1.3:.0f} L{x+w*s:.0f} {yy:.0f}Z" fill="{col}"/>')
    o.append(f'<rect x="{x-9*s:.0f}" y="{y:.0f}" width="{18*s:.0f}" height="{40*s:.0f}" fill="{col}"/>')
    return "".join(o)


def world(t):
    o = [f'<rect x="-1400" y="-400" width="4000" height="3200" fill="url(#skyN)"/>']
    rnd = random.Random(7)
    for k in range(90):
        x, y = rnd.uniform(-600, 1700), rnd.uniform(500, 1350)
        tw = 0.5 + 0.5 * math.sin(t * rnd.uniform(1.5, 4) + k)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(1.5,4):.1f}" fill="#fffbe8" opacity="{0.35+0.6*tw:.2f}"/>')
    # moon
    o.append('<circle cx="880" cy="1110" r="150" fill="url(#moonG)"/>'
             f'<circle cx="880" cy="1110" r="58" fill="#fff4cc" stroke="{OL}" stroke-width="5"/>'
             '<circle cx="860" cy="1096" r="11" fill="#eedfa8"/><circle cx="900" cy="1128" r="8" fill="#eedfa8"/><circle cx="896" cy="1086" r="5" fill="#eedfa8"/>')
    # far hills + pine silhouettes
    o.append(f'<path d="M-1400 {GROUND-260} Q -800 {GROUND-420} -200 {GROUND-300} Q 400 {GROUND-180} 900 {GROUND-330} Q 1400 {GROUND-430} 2400 {GROUND-260} V{GROUND} H-1400Z" fill="#1c2747"/>')
    for k in range(-8, 14):
        x = k * 120 + 30 * math.sin(k * 1.9)
        o.append(pine_dark(x, GROUND - 230 + 20 * math.cos(k * 1.3), 0.75, "#142039"))
    for k in range(-6, 12):
        x = k * 170 + 50 * math.sin(k * 2.7) + 60
        if 150 < x < 950:
            continue
        o.append(pine_dark(x, GROUND - 120, 1.05, "#0f1a2e"))
    # tent (right, back)
    tx, ty = 1060, GROUND - 40
    o.append(f'<path d="M{tx-170} {ty} L{tx} {ty-230} L{tx+170} {ty}Z" fill="#e0703a" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
             f'<path d="M{tx} {ty-230} L{tx+170} {ty} L{tx+60} {ty}Z" fill="#b8542a"/>'
             f'<path d="M{tx-40} {ty} L{tx} {ty-150} L{tx+30} {ty}Z" fill="#3a2230" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
             f'<path d="M{tx-170} {ty} L{tx} {ty-230} L{tx+170} {ty}" fill="none" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>')
    # tree trunk on the left (big, near)
    o.append(f'<path d="M{TREE_X-70} {GROUND+10} Q {TREE_X-50} {GROUND-300} {TREE_X-60} {GROUND-900} L{TREE_X+60} {GROUND-900} Q {TREE_X+46} {GROUND-300} {TREE_X+80} {GROUND+10}Z" fill="#5a3b2a" stroke="{OL}" stroke-width="6"/>'
             f'<path d="M{TREE_X+20} {GROUND-40} Q {TREE_X+30} {GROUND-400} {TREE_X+26} {GROUND-880}" fill="none" stroke="#7a5238" stroke-width="12" opacity="0.7"/>'
             f'<path d="M{TREE_X-30} {GROUND-500} q14 30 2 60 M{TREE_X-10} {GROUND-200} q12 26 0 50" fill="none" stroke="#3a2418" stroke-width="5" stroke-linecap="round"/>'
             f'<circle cx="{TREE_X-40}" cy="{GROUND-960}" r="170" fill="#183020" stroke="{OL}" stroke-width="6"/>')
    # ground
    o.append(f'<rect x="-1400" y="{GROUND}" width="4000" height="900" fill="#2b2220"/>')
    o.append(f'<rect x="-1400" y="{GROUND-26}" width="4000" height="30" fill="#2f5a3a" stroke="{OL}" stroke-width="5"/>')
    o.append(f'<rect x="-1400" y="{GROUND-23}" width="4000" height="7" fill="#3f7a4c"/>')
    rnd = random.Random(3)
    for k in range(40):
        x = rnd.uniform(-500, 1600)
        y = GROUND + rnd.uniform(60, 500)
        o.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rnd.uniform(8,18):.0f}" ry="{rnd.uniform(4,9):.0f}" fill="#211a18"/>')
    for x in (230, 380, 700, 860, 980, -100):
        o.append(f'<path d="M{x-14} {GROUND-24} l6 -22 l4 18 l6 -28 l5 26 l7 -18 l2 24z" fill="#2f6a3c" stroke="{OL}" stroke-width="3.5" stroke-linejoin="round"/>')
    # fire glow on ground
    fl = 1 + 0.06 * math.sin(t * 13) + 0.04 * math.sin(t * 7.3)
    o.append(f'<ellipse cx="{FX}" cy="{GROUND-40}" rx="{620*fl:.0f}" ry="{420*fl:.0f}" fill="url(#fireGlow)"/>')
    # marshmallow bag (left, on ground)
    o.append(bag(BAG[0], BAG[1], t))
    return "".join(o)


def bag(x, y, t, empty=False):
    return (f'<g transform="translate({x:.1f} {y:.1f})">'
            f'<path d="M-46 40 L-40 -44 Q -46 -58 -30 -60 L30 -60 Q 46 -58 40 -44 L46 40 Q 0 52 -46 40Z" fill="#eef3ff" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M-36 -46 Q 0 -36 36 -46" fill="none" stroke="#2a7de8" stroke-width="7"/>'
            f'<rect x="-18" y="-14" width="36" height="28" rx="10" fill="#ffffff" stroke="{OL}" stroke-width="4"/>'
            f'<rect x="-10" y="-8" width="20" height="16" rx="6" fill="#ffe9c8"/></g>')


def fire(t, x=FX, y=GROUND - 14):
    o = []
    # stones
    for k in range(7):
        a = math.radians(180 + k * 30)
        sx = x + 125 * math.cos(a) * 1.0
        sy = y + 18 + 20 * math.sin(a) * 0.3
        o.append(f'<ellipse cx="{sx:.0f}" cy="{sy+8:.0f}" rx="30" ry="20" fill="#7d7f8e" stroke="{OL}" stroke-width="5"/>'
                 f'<ellipse cx="{sx-8:.0f}" cy="{sy:.0f}" rx="10" ry="5" fill="#a9abb8"/>')
    # logs
    o.append(f'<g transform="translate({x} {y})"><rect x="-100" y="-22" width="200" height="40" rx="20" fill="#7a4a2a" stroke="{OL}" stroke-width="6" transform="rotate(-12)"/>'
             f'<rect x="-100" y="-22" width="200" height="40" rx="20" fill="#8a5a34" stroke="{OL}" stroke-width="6" transform="rotate(12)"/>'
             f'<circle cx="94" cy="18" r="16" fill="#d9a46a" stroke="{OL}" stroke-width="5"/><circle cx="-94" cy="18" r="16" fill="#d9a46a" stroke="{OL}" stroke-width="5"/>'
             f'<ellipse cx="0" cy="0" rx="70" ry="16" fill="#ff7a1a" opacity="0.8"/></g>')
    # flames
    for k, (w, h, col, ph) in enumerate([(80, 250, "#e8401c", 0.0), (60, 200, "#ff8a1a", 1.3), (40, 140, "#ffd23a", 2.4), (22, 70, "#fff6c8", 3.1)]):
        hh = h * (1 + 0.1 * math.sin(t * 11 + ph) + 0.06 * math.sin(t * 23 + ph * 2))
        sw = 14 * math.sin(t * 7 + ph)
        o.append(f'<path d="M{x-w} {y} Q {x-w-10} {y-hh*0.45:.0f} {x-w*0.3+sw*0.5:.0f} {y-hh*0.7:.0f} Q {x-w*0.1+sw:.0f} {y-hh*0.85:.0f} {x+sw:.0f} {y-hh:.0f} '
                 f'Q {x+w*0.35+sw*0.4:.0f} {y-hh*0.75:.0f} {x+w*0.55:.0f} {y-hh*0.55:.0f} Q {x+w*0.75:.0f} {y-hh*0.68:.0f} {x+w*0.8:.0f} {y-hh*0.8:.0f} '
                 f'Q {x+w+16:.0f} {y-hh*0.4:.0f} {x+w} {y}Z" fill="{col}" stroke="{OL if k == 0 else "none"}" stroke-width="5" stroke-linejoin="round"/>')
    # sparks
    for k in range(9):
        p = (t * 0.7 + k / 9) % 1
        sx = x + 60 * math.sin(k * 2.1 + t * 2) * p + (k - 4) * 8
        sy = y - 120 - p * 520
        o.append(f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="{5*(1-p)+1.5:.1f}" fill="#ffd23a" opacity="{(1-p):.2f}"/>')
    return "".join(o)


def stick(h, tip, back=0.25):
    bx = h[0] - (tip[0] - h[0]) * back
    by = h[1] - (tip[1] - h[1]) * back
    return (f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{tip[0]:.1f}" y2="{tip[1]:.1f}" stroke="{OL}" stroke-width="15" stroke-linecap="round"/>'
            f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{tip[0]:.1f}" y2="{tip[1]:.1f}" stroke="#a8743f" stroke-width="7" stroke-linecap="round"/>')


def marsh(x, y, ang, toast=0.0, burnt=0.0, s=1.0, sx=1.0, flame=0.0, t=0.0):
    """marshmallow at the stick tip. toast 0..1 (golden), burnt 0..1 (charcoal)."""
    body = mix_hex("#ffffff", "#f2b65a", toast)
    body = mix_hex(body, "#2a2226", burnt)
    top = mix_hex("#fff7ec", "#ffd590", toast)
    top = mix_hex(top, "#45383c", burnt)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({ang:.1f}) scale({s*sx:.3f} {s:.3f})">',
         f'<rect x="-30" y="-24" width="60" height="48" rx="18" fill="{body}" stroke="{OL}" stroke-width="5"/>',
         f'<rect x="-22" y="-18" width="22" height="12" rx="6" fill="{top}" opacity="0.9"/>']
    if burnt > 0.5:
        o.append('<path d="M-14 6 l6 -4 M8 10 l6 -6 M-4 -4 l4 4" stroke="#6a5a5e" stroke-width="3" stroke-linecap="round"/>')
    o.append('</g>')
    if flame > 0:
        fh = 70 * flame * (1 + 0.15 * math.sin(t * 25 + x))
        sw = 8 * math.sin(t * 17 + x)
        o.append(f'<path d="M{x-26*flame:.1f} {y-14:.1f} Q {x-30*flame:.1f} {y-fh*0.6:.1f} {x+sw:.1f} {y-fh-14:.1f} Q {x+30*flame:.1f} {y-fh*0.6:.1f} {x+26*flame:.1f} {y-14:.1f}Z" fill="#ff7a1a" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>'
                 f'<path d="M{x-12*flame:.1f} {y-14:.1f} Q {x-14*flame:.1f} {y-fh*0.4:.1f} {x+sw*0.6:.1f} {y-fh*0.7-14:.1f} Q {x+14*flame:.1f} {y-fh*0.4:.1f} {x+12*flame:.1f} {y-14:.1f}Z" fill="#ffd23a"/>')
    return "".join(o)


def smoke(x, y, t, t0, n=3):
    o = []
    for k in range(n):
        p = ((t - t0) * 0.9 + k / n) % 1
        o.append(f'<circle cx="{x + 14*math.sin(p*7+k):.0f}" cy="{y - 20 - p*170:.0f}" r="{10+p*26:.0f}" fill="#8a8a96" opacity="{0.6*(1-p):.2f}"/>')
    return "".join(o)


def mosquito(x, y, t, d=1, s=1.0, rot=0.0, flap=1.0, stuck=False):
    """cartoon mosquito, facing d (1 = right)."""
    fl = 0.25 + 0.75 * abs(math.sin(t * 95)) if flap > 0 else 1.0
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({d*s:.3f} {s:.3f})">']
    # legs
    if not stuck:
        for k, lx in enumerate((-8, 4, 14)):
            sw = 4 * math.sin(t * 9 + k)
            o.append(f'<path d="M{lx} 8 l{-10+k*4} 22 l{-6+k*3+sw:.1f} 20" fill="none" stroke="{OL}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    # wings (behind body)
    for k, (wx, wa) in enumerate(((-6, -30), (4, -12))):
        o.append(f'<g transform="translate({wx} -10) rotate({wa}) scale(1 {fl:.2f})"><ellipse cx="0" cy="-26" rx="13" ry="28" fill="#dff4ff" fill-opacity="0.75" stroke="{OL}" stroke-width="3"/>'
                 f'<path d="M0 -6 L0 -46" stroke="#9cc7e0" stroke-width="2"/></g>')
    # abdomen
    o.append(f'<ellipse cx="-34" cy="4" rx="30" ry="13" fill="#5c6274" stroke="{OL}" stroke-width="4" transform="rotate(14 -34 4)"/>'
             f'<path d="M-46 -6 l-4 18 M-34 -8 l-3 20 M-22 -6 l-2 18" stroke="#3a3e4c" stroke-width="4" stroke-linecap="round"/>')
    # thorax + head
    o.append(f'<circle cx="0" cy="0" r="15" fill="#6c7286" stroke="{OL}" stroke-width="4"/>'
             f'<circle cx="20" cy="-8" r="13" fill="#7a8096" stroke="{OL}" stroke-width="4"/>'
             f'<circle cx="25" cy="-12" r="8" fill="#ffffff" stroke="{OL}" stroke-width="2.5"/><circle cx="27" cy="-12" r="4" fill="#c01a2a"/>'
             f'<path d="M17 -22 l12 -2" stroke="{OL}" stroke-width="3.5" stroke-linecap="round"/>'
             f'<path d="M30 -2 L60 8" stroke="{OL}" stroke-width="4" stroke-linecap="round"/>'
             f'<path d="M22 -20 q4 -16 14 -18 M16 -20 q-2 -14 6 -20" fill="none" stroke="{OL}" stroke-width="2.5" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


def buzz_lines(x, y, t, op=0.8):
    o = []
    for k in range(3):
        p = (t * 3 + k / 3) % 1
        o.append(f'<path d="M{x-40-30*p:.0f} {y-20+18*k:.0f} q8 -8 16 0 t16 0" fill="none" stroke="#dfe8ff" stroke-width="3" stroke-linecap="round" opacity="{op*(1-p):.2f}"/>')
    return "".join(o)


def handprint(x, y, rot, s, col, op):
    if op <= 0:
        return ""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})" opacity="{op:.2f}">'
            f'<ellipse cx="0" cy="8" rx="22" ry="20" fill="{col}"/>'
            + "".join(f'<ellipse cx="{dx}" cy="{dy}" rx="7" ry="14" fill="{col}" transform="rotate({ra} {dx} {dy})"/>' for dx, dy, ra in ((-20, -16, -20), (-7, -24, -6), (7, -24, 6), (20, -16, 20)))
            + f'<ellipse cx="26" cy="14" rx="7" ry="12" fill="{col}" transform="rotate(50 26 14)"/></g>')


def dizzy_stars(x, y, t, rx=90, op=1.0):
    o = []
    for k in range(3):
        a = t * 7 + k * 2.09
        sx, sy = x + rx * math.cos(a), y + rx * 0.3 * math.sin(a)
        pts = " ".join(f"{sx + (16 if j % 2 == 0 else 7) * math.cos(math.radians(j*36-90)):.1f},{sy + (16 if j % 2 == 0 else 7) * math.sin(math.radians(j*36-90)):.1f}" for j in range(10))
        o.append(f'<polygon points="{pts}" fill="#fff36a" stroke="{OL}" stroke-width="3" opacity="{op:.2f}"/>')
    return "".join(o)


def heart(x, y, p):
    if p <= 0 or p >= 1:
        return ""
    s = eback(min(1, p * 3)) * 1.0
    return (f'<g transform="translate({x:.1f} {y - 60*p:.1f}) scale({s:.2f})" opacity="{1 if p < 0.7 else (1-p)/0.3:.2f}">'
            f'<path d="M0 18 C -30 -2 -26 -26 -10 -26 C -2 -26 0 -18 0 -14 C 0 -18 2 -26 10 -26 C 26 -26 30 -2 0 18Z" fill="#ff5a7a" stroke="{OL}" stroke-width="4"/></g>')


def smell(x, y, t, op):
    if op <= 0:
        return ""
    o = []
    for k in range(3):
        p = (t * 0.8 + k / 3) % 1
        xx = x + (k - 1) * 22
        o.append(f'<path d="M{xx:.0f} {y-10-p*120:.0f} q12 -14 0 -28 q-12 -14 0 -28" fill="none" stroke="#ffe7b0" stroke-width="5" stroke-linecap="round" opacity="{op*(1-p):.2f}"/>')
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
    elif kind == "puff":
        o.append(f'<path d="M-70 -34 Q -44 -26 -16 -12 M70 -34 Q 44 -26 16 -12" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<circle cx="-78" cy="60" r="34" fill="{base}" stroke="#221c2e" stroke-width="6"/><circle cx="78" cy="60" r="34" fill="{base}" stroke="#221c2e" stroke-width="6"/>'
                 f'<ellipse cx="0" cy="72" rx="12" ry="10" fill="#4a0a14" stroke="{ink}" stroke-width="6"/>')
    elif kind == "grin":
        o.append(f'<path d="M-60 6 h44 v30 h-44z M16 6 h44 v30 h-44z" fill="{base}"/>'
                 f'<path d="M-58 22 q20 -16 40 0 M18 22 q20 -16 40 0" fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M-72 -30 Q -44 -24 -16 -14 M72 -30 Q 44 -24 16 -14" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<path d="M-40 58 Q 0 100 40 58Z" fill="#4a0a14" stroke="{ink}" stroke-width="8" stroke-linejoin="round"/>'
                 f'<path d="M-30 62 h60" stroke="#fff" stroke-width="8"/>')
    elif kind == "wink":
        o.append(f'<path d="M-60 2 h46 v34 h-46z" fill="{base}"/>'
                 f'<path d="M-58 20 q20 -14 40 0" fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M-72 -26 Q -44 -22 -16 -14 M72 -36 Q 44 -30 16 -18" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<path d="M-30 64 q34 24 64 -8" fill="none" stroke="{ink}" stroke-width="10" stroke-linecap="round"/>')
    elif kind == "sad":
        o.append(f'<path d="M-70 -20 Q -44 -34 -18 -44 M70 -20 Q 44 -34 18 -44" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
                 f'<path d="M-30 84 q30 -22 60 0" fill="none" stroke="{ink}" stroke-width="10" stroke-linecap="round"/>')
    elif kind == "content":
        o.append(f'<path d="M-60 2 h44 v34 h-44z M16 2 h44 v34 h-44z" fill="{base}"/>'
                 f'<path d="M-58 22 q20 -14 40 0 M18 22 q20 -14 40 0" fill="none" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M-70 -26 Q -44 -26 -16 -16 M70 -26 Q 44 -26 16 -16" fill="none" stroke="{ink}" stroke-width="14" stroke-linecap="round"/>'
                 f'<path d="M-22 66 q22 16 44 0" fill="none" stroke="{ink}" stroke-width="9" stroke-linecap="round"/>'
                 '<ellipse cx="-72" cy="52" rx="20" ry="11" fill="#ff7fa0" opacity="0.75"/><ellipse cx="72" cy="52" rx="20" ry="11" fill="#ff7fa0" opacity="0.75"/>')
    o.append('</g>')
    return "".join(o)


def nib_face(x, y, r, rot, sx, sy, kind):
    if not kind:
        return ""
    f = r / 48 * 1.05
    d = "#2a1a10"
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx*f:.3f} {sy*f:.3f})">']
    if kind == "side":      # eyes rolled to the left (bug on cheek)
        o.append(f'<ellipse cx="-14" cy="-4" rx="7" ry="9" fill="#fff" stroke="{d}" stroke-width="2"/><ellipse cx="14" cy="-4" rx="7" ry="9" fill="#fff" stroke="{d}" stroke-width="2"/>'
                 f'<circle cx="-18" cy="-2" r="4.5" fill="{d}"/><circle cx="10" cy="-2" r="4.5" fill="{d}"/>'
                 f'<path d="M-6 15 h12" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    elif kind == "sad":
        o.append(f'<path d="M-24 -16 l12 -4 M24 -16 l-12 -4" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<ellipse cx="-14" cy="-3" rx="6" ry="7" fill="{d}"/><ellipse cx="14" cy="-3" rx="6" ry="7" fill="{d}"/>'
                 '<circle cx="-12" cy="-6" r="2" fill="#fff"/><circle cx="16" cy="-6" r="2" fill="#fff"/>'
                 f'<path d="M-9 17 q9 -8 18 0" fill="none" stroke="{d}" stroke-width="4.5" stroke-linecap="round"/>')
    elif kind == "angry":
        o.append(f'<path d="M-24 -18 l14 6 M24 -18 l-14 6" stroke="{d}" stroke-width="4.5" stroke-linecap="round"/>'
                 f'<ellipse cx="-13" cy="-3" rx="6" ry="7" fill="{d}"/><ellipse cx="13" cy="-3" rx="6" ry="7" fill="{d}"/>'
                 f'<path d="M-9 16 q9 -6 18 0" fill="none" stroke="{d}" stroke-width="4.5" stroke-linecap="round"/>')
    elif kind == "puff":
        o.append(f'<path d="M-22 -18 l12 4 M22 -18 l-12 4" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<path d="M-20 -4 l10 0 M10 -4 l10 0" stroke="{d}" stroke-width="5" stroke-linecap="round"/>')
        for sgn in (-1, 1):
            o.append(f'<circle cx="{sgn*30}" cy="14" r="15" fill="#ffc22e" stroke="{NS}" stroke-width="3"/>')
        o.append(f'<ellipse cx="0" cy="16" rx="5" ry="5" fill="#7a2a1a" stroke="{d}" stroke-width="3"/>')
    elif kind == "wink":
        o.append(f'<path d="M-21 -2 q7 -8 14 0" fill="none" stroke="{d}" stroke-width="5" stroke-linecap="round"/>'
                 f'<ellipse cx="14" cy="-4" rx="6" ry="8" fill="{d}"/><circle cx="16" cy="-7" r="2.2" fill="#fff"/>'
                 f'<path d="M-9 12 q9 9 18 0" fill="none" stroke="{d}" stroke-width="5" stroke-linecap="round"/>')
    elif kind == "lookup":
        o.append(f'<ellipse cx="-14" cy="-8" rx="6" ry="8" fill="{d}"/><ellipse cx="14" cy="-8" rx="6" ry="8" fill="{d}"/>'
                 '<circle cx="-12" cy="-12" r="2.2" fill="#fff"/><circle cx="16" cy="-12" r="2.2" fill="#fff"/>'
                 f'<path d="M-6 12 q6 4 12 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


# ---------------------------------------------------------------- mosquito path
def _buzz(t, a=26):
    return a * math.sin(t * 9.1) + 8 * math.sin(t * 23), a * 0.8 * math.cos(t * 7.3) + 6 * math.sin(t * 19)


G_HEAD = (GX + 6, GY - GR - 4)
N_CHEEK = (NX - 112, NY + 6)
MIDAIR = (FX, 1400.0)


def mos_state(t):
    """(x, y, dir, rot, mode) mode: fly/land/stuck/gone"""
    if t < T_LAND1:
        p = eio(seg(t, 0, T_LAND1))
        x = lerp(240, G_HEAD[0], p) + 150 * math.sin(p * math.pi * 1.5) * (1 - p)
        y = lerp(1330, G_HEAD[1], p) - 120 * math.sin(p * math.pi) + (1 - p) * _buzz(t)[1]
        return x, y, 1, 0, "fly"
    if t < T_ML1:
        return G_HEAD[0], G_HEAD[1], 1, 22, "land"
    if t < T_LAND2:
        p = seg(t, T_ML1, T_LAND2)
        if p < 0.3:
            q = eout(p / 0.3)
            x, y = lerp(G_HEAD[0], 460, q), lerp(G_HEAD[1], 1260, q)
        else:
            q = eio((p - 0.3) / 0.7)
            x = lerp(460, N_CHEEK[0], q) + 90 * math.sin(q * math.pi * 2) * (1 - q)
            y = lerp(1260, N_CHEEK[1], q) - 60 * math.sin(q * math.pi)
        bx, by = _buzz(t, 18)
        k = 1 - seg(t, T_LAND2 - 0.2, T_LAND2)
        return x + bx * k, y + by * k, 1 if p < 0.3 else -1, 0, "fly"
    if t < T_ML2:
        return N_CHEEK[0], N_CHEEK[1], -1, -60, "land"
    if t < T_M3:
        p = eout(seg(t, T_ML2, T_ML2 + 0.5))
        return lerp(N_CHEEK[0], 560, p), lerp(N_CHEEK[1], 900, p), -1, 0, "fly" if p < 1 else "gone"
    if t < T_ML3:
        p = seg(t, T_M3, T_M3 + 0.5)
        cx, cy = MIDAIR
        k = t - T_M3
        x = cx + 110 * math.sin(k * 3.2)
        y = lerp(900, cy, eout(p)) + 40 * math.sin(k * 6.4)
        d = 1 if math.cos(k * 3.2) > 0 else -1
        return x, y, d, 0, "fly"
    if t < T_M4:
        p = eout(seg(t, T_ML3, T_ML3 + 0.25))
        x0 = FX + 110 * math.sin((T_ML3 - T_M3) * 3.2)
        y0 = MIDAIR[1] + 40 * math.sin((T_ML3 - T_M3) * 6.4)
        k = t - T_ML3
        if t < T_CLAPUP + 0.5:
            return lerp(x0, FX, p), lerp(y0, 1190, p) + _buzz(t, 10)[1], 1, 0, "fly"
        # loop-the-loop mocking, then off
        q = seg(t, T_CLAPUP + 0.5, T_M4)
        return FX + 70 * math.sin(q * 6.28) + 400 * q * q, 1190 - 70 * (1 - math.cos(q * 6.28)) - 400 * q * q, 1, -360 * q, "fly"
    if t < T_SQUISH:
        p = eio(seg(t, T_M4, T_HOVER))
        x = lerp(950, FX, p) + 60 * math.sin(p * 6) * (1 - p)
        y = lerp(1150, 1428, p)
        bx, by = _buzz(t, 10)
        return x + bx * 0.5, y + by * 0.4, -1, 0, "fly"
    return None


# ---------------------------------------------------------------- characters
def grumpo_state(t):
    g = dict(x=GX, y=GY, rot=0.0, sx=1.0, sy=1.0, ex="grumpy", kind=None, look=(0.6, 0), red=0.0,
             hR=G_HAND0, hL=None, tip=G_TIP0, print=0.0, stars=0.0)
    # handprint fades
    if T_SLAP1 <= t:
        g["print"] = 1 - seg(t, T_SLAP1 + 2.6, T_SLAP1 + 3.3)
    if t < T_LAND1:
        m = mos_state(t)
        dx, dy = (m[0] - GX) / 300, (m[1] - GY) / 300
        g["look"] = (cl(dx, -1, 1), cl(dy, -1, 1))
        g["ex"] = "suspicious"
        return g
    if t < T_SLAP1:
        g["look"] = (0.1, -1)
        g["ex"] = "suspicious" if t < T_NSEE + 0.2 else "shock"
        if t >= T_WIND1_1:
            g["look"] = (1, -0.6)
        return g
    if t < T_GLARE:
        g["sx"], g["sy"] = squash(t, T_SLAP1, 0.35, 0.3)
        g["y"] = GY + GR * (1 - g["sy"])
        g["ex"], g["kind"] = "x", "dizzy"
        g["stars"] = 1 - seg(t, T_GLARE - 0.2, T_GLARE)
        return g
    if t < T_LAND2:
        g["ex"] = "angry"
        g["red"] = 0.55 * seg(t, T_GLARE, T_GLARE + 0.2)
        g["look"] = (1, 0)
        g["rot"] = 3 * math.sin(t * 30)
        g["sx"], g["sy"] = squash(t, T_GLARE, 0.25, 0.12)
        if t >= T_LAND2 - 0.25:
            g["look"] = (1, -0.2)
        return g
    if t < T_SLAP2:
        g["red"] = 0.55 * (1 - seg(t, T_LAND2, T_GSMUG))
        g["ex"] = "smug"
        g["look"] = (1, 0)
        if t >= T_WIND2_0:
            p = seg(t, T_WIND2_0, T_WIND2_1)
            a = math.radians(200 + 540 * eio(p))
            g["hL"] = (GX - 30 + 150 * math.cos(a), GY - 60 + 150 * math.sin(a))
            g["ex"], g["kind"] = "x", "grin"
            g["rot"] = -8 * p
        if t >= T_WIND2_1:
            q = eout(seg(t, T_WIND2_1, T_SLAP2))
            g["hL"] = lerp2((GX - 180, GY - 110), (N_CHEEK[0] + 10, N_CHEEK[1] - 4), q)
            g["rot"] = lerp(-8, 10, q)
        return g
    if t < T_NOTICE:
        k = seg(t, T_SLAP2, T_SLAP2 + 0.35)
        if k < 1:
            g["hL"] = lerp2((N_CHEEK[0] + 10, N_CHEEK[1] - 4), (GX - 110, GY + 40), eio(k))
        g["ex"], g["kind"] = "x", "grin"
        g["rot"] = 10 * (1 - k)
        if t >= T_SPIN1:
            g["ex"], g["kind"] = "smug", None
            g["look"] = (1, 0)
        return g
    if t < T_SAD0:
        g["ex"] = "shock"
        g["look"] = (1, -0.4)
        g["sx"], g["sy"] = squash(t, T_NOTICE, 0.25, 0.12)
        if t >= T_BLOW0:
            p = eout(seg(t, T_BLOW0, T_BLOW0 + 0.2))
            g["tip"] = lerp2(G_TIP0, (GX + 210, GY - 20), p)
            g["hR"] = lerp2(G_HAND0, (GX + 120, GY + 30), p)
            g["ex"], g["kind"] = "x", "puff"
            g["sx"] = 1.06 + 0.03 * math.sin(t * 40)
            g["sy"] = 2 - g["sx"]
            g["look"] = (1, -0.3)
        if t >= T_OUT:
            g["ex"], g["kind"] = "shock", None
        return g
    burnt_tip = (GX + 210, GY - 20)
    if t < T_M3 + 0.3:
        g["tip"] = burnt_tip
        g["hR"] = (GX + 120, GY + 30)
        g["ex"], g["kind"] = "x", "sad"
        g["look"] = (1, -0.4)
        return g
    if t < T_IDEA:
        p = eio(seg(t, T_M3 + 0.3, T_M3 + 0.6))
        g["tip"] = lerp2(burnt_tip, (G_TIP0[0] - 40, G_TIP0[1] + 10), p)
        g["hR"] = G_HAND0
        m = mos_state(t)
        if m:
            g["look"] = (cl((m[0] - GX) / 300, -1, 1), cl((m[1] - GY) / 300, -1, 1))
        g["ex"] = "angry"
        g["red"] = 0.3
        if T_LOOK <= t < T_WIND3_0:
            g["look"] = (1, 0)
            g["ex"] = "suspicious"
            g["red"] = 0.0
            if t >= T_NOD0:
                q = seg(t, T_NOD0, T_NOD1)
                g["y"] = GY + 16 * abs(math.sin(q * math.pi * 2))
                g["ex"] = "smug"
        if T_WIND3_0 <= t < T_CLAP:
            p = eio(seg(t, T_WIND3_0, T_WIND3_1))
            g["hL"] = lerp2((GX - 110, GY + 40), (GX - 190, GY - 150), p)
            g["ex"] = "angry"
            g["red"] = 0.35
            g["look"] = (1, -0.3)
            if t >= T_WIND3_1:
                q = eout(seg(t, T_WIND3_1, T_CLAP))
                g["hL"] = lerp2((GX - 190, GY - 150), (FX - 18, 1386), q)
        if T_CLAP <= t < T_IDEA:
            g["hL"] = (FX - 18, 1386) if t < T_UNCLAP else lerp2((FX - 18, 1386), (GX - 110, GY + 40), eio(seg(t, T_UNCLAP, T_UNCLAP + 0.15)))
            if t >= T_UNCLAP + 0.15:
                g["hL"] = None
            g["ex"] = "shock" if t < T_CLAPUP else "angry"
            g["red"] = 0.0 if t < T_CLAPUP else 0.4
            g["look"] = (0.6, -0.2) if t < T_CLAPUP else (0.8, -1)
            g["sx"], g["sy"] = squash(t, T_CLAP, 0.25, 0.1)
        return g
    if t < T_ROAST0:
        g["ex"] = "smug"
        g["look"] = (-0.5, -0.5)
        g["sx"], g["sy"] = squash(t, T_IDEA, 0.25, 0.12)
        g["tip"] = (G_TIP0[0] - 40, G_TIP0[1] + 10)
        if t >= T_FRESH - 0.25:
            p = seg(t, T_FRESH - 0.25, T_FRESH)
            g["hL"] = lerp2((BAG[0] + 20, BAG[1] - 20), (GX - 60, GY - 60), eout(p))
            g["look"] = (-1, 0.5)
        if t >= T_TOSS0:
            p = seg(t, T_TOSS0, T_TOSS1)
            g["hL"] = lerp2((GX - 60, GY - 60), (GX + 20, GY - 170), eout(min(1, p * 3)))
            g["look"] = (1, -0.4)
            g["ex"] = "smug"
        return g
    if t < T_SWING0:
        p = eio(seg(t, T_ROAST0, T_ROAST0 + 0.3))
        g["tip"] = lerp2((G_TIP0[0] - 40, G_TIP0[1] + 10), (FX - 72, 1440), p)
        g["hR"] = lerp2(G_HAND0, (GX + 124, GY + 10), p)
        m = mos_state(t)
        g["ex"] = "smug"
        if m:
            g["look"] = (cl((m[0] - GX) / 300, -1, 1), cl((m[1] - GY) / 300, -1, 1))
        if t >= T_WINK:
            g["ex"], g["kind"] = "x", "wink"
        return g
    if t < T_PULL0:
        p = eio(seg(t, T_SWING0, T_SQUISH))
        g["hR"] = lerp2((GX + 124, GY + 10), (GX + 150, GY + 8), p)
        g["tip"] = lerp2((FX - 72, 1440), (FX - 36, 1436), p)
        g["ex"], g["kind"] = ("x", "grin") if t >= T_SQUISH + 0.15 else ("angry", None)
        g["sx"], g["sy"] = squash(t, T_SQUISH, 0.3, 0.12)
        return g
    if t < T_FLICK1:
        p = eio(seg(t, T_PULL0, T_PULL1))
        g["hR"] = lerp2((GX + 150, GY + 8), (GX + 110, GY - 10), p)
        g["tip"] = lerp2((FX - 36, 1436), (GX + 230, GY - 110), p)
        g["ex"] = "smug"
        g["look"] = (0.6, -0.6)
        if t >= T_FLICK0:
            q = seg(t, T_FLICK0, T_FLICK1)
            a = lerp(-30, -150, eout(min(1, q * 2.5)))
            L = 230
            g["hR"] = (GX + 110, GY - 10)
            g["tip"] = (GX + 110 + L * math.cos(math.radians(a)), GY - 10 + L * math.sin(math.radians(a)))
            g["look"] = (-1, -0.4)
            g["rot"] = -10 * math.sin(q * math.pi)
        return g
    # after the flick
    stick_up = (GX + 110 + 230 * math.cos(math.radians(-150)), GY - 10 + 230 * math.sin(math.radians(-150)))
    p = eio(seg(t, T_FLICK1, T_FLICK1 + 0.3))
    g["hR"] = lerp2((GX + 110, GY - 10), G_HAND0, p)
    g["tip"] = lerp2(stick_up, (G_TIP0[0] - 30, G_TIP0[1] + 8), p)
    g["ex"], g["kind"] = "x", "grin"
    if t < T_HI5:
        q = eio(seg(t, T_HI5_0, T_HI5))
        g["hL"] = lerp2((GX - 110, GY + 40), (FX - 18, 1330), q) if t >= T_HI5_0 else None
    elif t < T_LAST0:
        q = eio(seg(t, T_HI5 + 0.4, T_HI5 + 0.6))
        g["hL"] = lerp2((FX - 18, 1330), (GX - 110, GY + 40), q)
        g["sx"], g["sy"] = squash(t, T_HI5, 0.3, 0.12)
        if t >= T_LAUGH1:
            g["ex"], g["kind"] = "smug", None
    elif t < T_SPLIT0:
        q = eio(seg(t, T_LAST0, T_LAST1))
        g["hL"] = lerp2((BAG[0] + 20, BAG[1] - 20), (GX - 40, GY - 140), q)
        g["ex"], g["kind"] = "suspicious", None
        g["look"] = (-0.4, -1) if t < T_LAST1 + 0.15 else (1, 0)
    elif t < T_GIVE0:
        q = eio(seg(t, T_SPLIT0, T_SPLIT1))
        g["hL"] = (GX - 40 - 50 * q, GY - 140)
        g["hR"] = (GX + 30 + 70 * q, GY - 140)
        g["ex"], g["kind"] = "x", "puff" if t < T_SPLIT1 else "content"
        g["look"] = (0, -1)
        if t >= T_SPLIT1:
            g["ex"], g["kind"] = "x", "content"
    elif t < T_ONSTICK:
        q = eio(seg(t, T_GIVE0, T_GIVE1))
        r = eio(seg(t, T_GIVE1 + 0.05, T_ONSTICK))
        g["hL"] = (GX - 90, GY - 140) if t < T_ONSTICK - 0.1 else None
        g["hR"] = lerp2((GX + 100, GY - 140), (NX - 150, NY - 60), q) if t < T_GIVE1 + 0.05 else lerp2((NX - 150, NY - 60), G_HAND0, r)
        g["ex"], g["kind"] = "x", "content"
        g["look"] = (1, 0)
    else:
        g["ex"], g["kind"] = "x", "content"
        g["tip"] = (G_TIP0[0] - 30, G_TIP0[1] + 8)
    return g


def nibbo_state(t):
    n = dict(x=NX, y=NY, rot=0.0, sx=1.0, sy=1.0, ex="happy", kind=None, hL=N_HAND0, hR=None, tip=N_TIP0, print=0.0, stars=0.0)
    if T_SLAP2 <= t:
        n["print"] = 1 - seg(t, T_SLAP2 + 2.4, T_SLAP2 + 3.1)
    if t < T_NSEE:
        n["ex"] = "happy"
        n["y"] = NY - 6 * abs(math.sin(t * 4))
        return n
    if t < T_SLAP1:
        n["ex"] = "wow"
        n["sx"], n["sy"] = squash(t, T_NSEE, 0.25, 0.12)
        if t >= T_WIND1_0:
            p = eio(seg(t, T_WIND1_0, T_WIND1_1))
            n["hR"] = lerp2((NX + 96, NY + 30), (NX + 10, NY - 250), p)
            n["ex"], n["kind"] = "blank", "angry"
            n["rot"] = 8 * p
        if t >= T_WIND1_1:
            q = eout(seg(t, T_WIND1_1, T_SLAP1))
            n["hR"] = lerp2((NX + 10, NY - 250), (G_HEAD[0] + 10, G_HEAD[1] + 4), q)
            n["rot"] = lerp(8, -12, q)
        return n
    if t < T_LAND2:
        k = seg(t, T_RET1, T_RET1 + 0.3)
        if t < T_RET1:
            n["hR"] = (G_HEAD[0] + 10, G_HEAD[1] + 4)
            n["ex"], n["kind"] = "blank", "angry"
            n["rot"] = -12
        elif k < 1:
            n["hR"] = lerp2((G_HEAD[0] + 10, G_HEAD[1] + 4), (NX + 96, NY + 30), eio(k))
            n["rot"] = -12 * (1 - k)
            n["ex"] = "uhoh"
        else:
            n["ex"] = "nervous"
            if t >= T_GLARE:
                # sheepish: points up at the mosquito
                n["hR"] = (NX + 40, NY - 190 + 10 * math.sin(t * 12))
        return n
    if t < T_SLAP2:
        n["ex"], n["kind"] = "blank", "side"
        n["rot"] = -4 if t < T_WIND2_0 else -4 + 2 * math.sin(t * 40)
        return n
    if t < T_NOTICE:
        p = seg(t, T_SLAP2, T_SPIN1)
        n["rot"] = -720 * eout(p)
        n["ex"] = "dizzy"
        n["x"] = NX + 12 * math.sin(p * math.pi)
        n["sx"], n["sy"] = squash(t, T_SLAP2, 0.3, 0.2)
        if t >= T_SPIN1:
            n["rot"] = 6 * math.sin((t - T_SPIN1) * 9) * math.exp(-(t - T_SPIN1) * 2)
            n["stars"] = 1 - seg(t, T_NOTICE - 0.15, T_NOTICE)
        return n
    if t < T_SAD0:
        n["ex"] = "wow"
        n["sx"], n["sy"] = squash(t, T_NOTICE, 0.25, 0.12)
        if t >= T_BLOW0:
            p = eout(seg(t, T_BLOW0, T_BLOW0 + 0.2))
            n["tip"] = lerp2(N_TIP0, (NX - 190, NY - 20), p)
            n["hL"] = lerp2(N_HAND0, (NX - 100, NY + 24), p)
            n["ex"], n["kind"] = "blank", "puff"
            n["sx"] = 1.08 + 0.03 * math.sin(t * 44)
            n["sy"] = 2 - n["sx"]
        if t >= T_OUT:
            n["ex"], n["kind"] = "wow", None
        return n
    burnt_tip = (NX - 190, NY - 20)
    if t < T_M3 + 0.3:
        n["tip"] = burnt_tip
        n["hL"] = (NX - 100, NY + 24)
        n["ex"], n["kind"] = "blank", "sad"
        return n
    if t < T_IDEA:
        p = eio(seg(t, T_M3 + 0.3, T_M3 + 0.6))
        n["tip"] = lerp2(burnt_tip, (N_TIP0[0] + 40, N_TIP0[1] + 10), p)
        n["hL"] = N_HAND0
        n["ex"], n["kind"] = "blank", "angry"
        if T_LOOK <= t < T_WIND3_0:
            n["ex"], n["kind"] = "happy", None
            if t >= T_NOD0:
                q = seg(t, T_NOD0, T_NOD1)
                n["y"] = NY + 14 * abs(math.sin(q * math.pi * 2))
                n["ex"], n["kind"] = "blank", "wink" if q > 0.5 else "angry"
        if T_WIND3_0 <= t < T_CLAP:
            p = eio(seg(t, T_WIND3_0, T_WIND3_1))
            n["hR"] = lerp2((NX + 96, NY + 30), (NX + 170, NY - 150), p)
            n["ex"], n["kind"] = "blank", "angry"
            if t >= T_WIND3_1:
                q = eout(seg(t, T_WIND3_1, T_CLAP))
                n["hR"] = lerp2((NX + 170, NY - 150), (FX + 18, 1386), q)
        if T_CLAP <= t < T_IDEA:
            n["hR"] = (FX + 18, 1386) if t < T_UNCLAP else lerp2((FX + 18, 1386), (NX + 96, NY + 30), eio(seg(t, T_UNCLAP, T_UNCLAP + 0.15)))
            if t >= T_UNCLAP + 0.15:
                n["hR"] = None
            n["ex"], n["kind"] = ("wow", None) if t < T_CLAPUP else ("blank", "lookup")
            n["sx"], n["sy"] = squash(t, T_CLAP, 0.25, 0.1)
        return n
    if t < T_ROAST0:
        n["tip"] = (N_TIP0[0] + 40, N_TIP0[1] + 10)
        n["ex"] = "happy"
        if t >= T_TOSS0:
            p = seg(t, T_TOSS0, T_TOSS1)
            n["ex"] = "wow" if p < 0.95 else "joy"
            if t >= T_TOSS1:
                n["sx"], n["sy"] = squash(t, T_TOSS1, 0.25, 0.12)
        return n
    if t < T_SWING0:
        p = eio(seg(t, T_ROAST0, T_ROAST0 + 0.3))
        n["tip"] = lerp2((N_TIP0[0] + 40, N_TIP0[1] + 10), (FX + 72, 1440), p)
        n["hL"] = lerp2(N_HAND0, (NX - 104, NY + 10), p)
        n["ex"] = "happy"
        if t >= T_M4 + 0.3:
            n["ex"], n["kind"] = "blank", "angry"
        if t >= T_WINK + 0.12:
            n["ex"], n["kind"] = "blank", "wink"
        return n
    if t < T_PULL0:
        p = eio(seg(t, T_SWING0, T_SQUISH))
        n["hL"] = lerp2((NX - 104, NY + 10), (NX - 130, NY + 8), p)
        n["tip"] = lerp2((FX + 72, 1440), (FX + 36, 1436), p)
        n["ex"], n["kind"] = ("joy", None) if t >= T_SQUISH + 0.15 else ("blank", "angry")
        n["sx"], n["sy"] = squash(t, T_SQUISH, 0.3, 0.12)
        if t >= T_SQUISH + 0.3:
            n["y"] = NY - 30 * abs(math.sin((t - T_SQUISH) * 8))
        return n
    if t < T_FLICK1:
        p = eio(seg(t, T_PULL0, T_PULL1))
        n["tip"] = lerp2((FX + 36, 1436), (N_TIP0[0] + 30, N_TIP0[1] + 4), p)
        n["hL"] = lerp2((NX - 130, NY + 8), N_HAND0, p)
        n["ex"] = "joy" if t < T_FLICK0 else "wow"
        return n
    n["tip"] = (N_TIP0[0] + 30, N_TIP0[1] + 4)
    n["ex"] = "joy"
    if t < T_HI5:
        q = eio(seg(t, T_HI5_0, T_HI5))
        n["hR"] = lerp2((NX + 96, NY + 30), (FX + 18, 1330), q) if t >= T_HI5_0 else None
        if t < T_HI5_0:
            n["ex"] = "happy"
    elif t < T_LAST0:
        q = eio(seg(t, T_HI5 + 0.4, T_HI5 + 0.6))
        n["hR"] = lerp2((FX + 18, 1330), (NX + 96, NY + 30), q) if q < 1 else None
        n["sx"], n["sy"] = squash(t, T_HI5, 0.3, 0.12)
        n["y"] = NY - 24 * abs(math.sin((t - T_HI5) * 9)) * (1 - seg(t, T_LAUGH1, T_LAST0))
    elif t < T_GIVE0:
        n["ex"], n["kind"] = "blank", "lookup"
        if t >= T_SPLIT0:
            n["ex"], n["kind"] = "nervous", None
    elif t < T_ONSTICK:
        n["ex"] = "wow" if t < T_GIVE1 else "joy"
        q = eio(seg(t, T_GIVE1 - 0.1, T_GIVE1 + 0.1))
        if t >= T_GIVE1 - 0.1:
            n["hR"] = lerp2((NX + 96, NY + 30), (NX - 150, NY - 60), q) if t < T_GIVE1 + 0.15 else lerp2((NX - 150, NY - 60), (N_TIP0[0] + 40, N_TIP0[1] - 10), eio(seg(t, T_GIVE1 + 0.15, T_ONSTICK)))
    else:
        n["ex"] = "joy"
        n["y"] = NY - 10 * abs(math.sin((t - T_ONSTICK) * 6)) * (1 - seg(t, T_ONSTICK + 0.6, T_ONSTICK + 1.0))
    return n


# ---------------------------------------------------------------- marshmallow states
def g_marsh(t):
    """(kind, args) for Grumpo's marshmallow: toast, burnt, flame"""
    if t < T_OUT:
        toast = seg(t, 0, T_IGN)
        flame = seg(t, T_IGN, T_IGN + 0.6) * (1 - seg(t, T_BLOW0 + 0.2, T_OUT)) * (1 + 0.6 * seg(t, T_NOTICE, T_BLOW0))
        return dict(toast=toast, burnt=seg(t, T_IGN + 0.2, T_OUT), flame=min(1.3, flame), s=1.0, show=True)
    if t < T_FRESH:
        return dict(toast=0, burnt=1, flame=0, s=1.0, show=True)
    if t < T_SQUISH:
        return dict(toast=seg(t, T_ROAST0, T_ROAST1) * 0.85, burnt=0, flame=0, s=1.0 + 0.35 * seg(t, T_ROAST0, T_ROAST1), show=True)
    return dict(show=False)


def n_marsh(t):
    if t < T_OUT:
        toast = seg(t, 0, T_IGN + 0.15)
        flame = seg(t, T_IGN + 0.15, T_IGN + 0.7) * (1 - seg(t, T_BLOW0 + 0.2, T_OUT)) * (1 + 0.6 * seg(t, T_NOTICE, T_BLOW0))
        return dict(toast=toast, burnt=seg(t, T_IGN + 0.3, T_OUT), flame=min(1.3, flame), s=0.9, show=True)
    if t < T_TOSS1:
        return dict(toast=0, burnt=1, flame=0, s=0.9, show=True, burnt_only=True)
    if t < T_SQUISH:
        return dict(toast=seg(t, T_ROAST0, T_ROAST1) * 0.85, burnt=0, flame=0, s=0.9 + 0.35 * seg(t, T_ROAST0, T_ROAST1), show=True)
    if t < T_GIVE1 + 0.15:
        return dict(show=False)
    return dict(toast=0, burnt=0, flame=0, s=0.62, show=True)


def stick_ang(h, tip):
    return math.degrees(math.atan2(tip[1] - h[1], tip[0] - h[0]))


# ---------------------------------------------------------------- camera
def _cut(t0, a, b):
    return [(t0 - 0.001, a), (t0, b)]


BASE = (540, 1430, 1.28)
CK = ([(0.0, (470, 1440, 1.36)), (T_LAND1, (420, 1460, 1.45)), (T_WIND1_1, (470, 1440, 1.38)), (T_SLAP1 + 0.1, (420, 1470, 1.5)),
       (T_GLARE, (520, 1450, 1.36)), (T_LAND2, (560, 1460, 1.36)), (T_WIND2_1, (540, 1450, 1.3)), (T_SLAP2 + 0.05, (620, 1470, 1.48)), (T_SPIN1, (600, 1460, 1.42)),
       (T_NOTICE, (540, 1460, 1.4)), (T_OUT, (540, 1470, 1.42)), (T_M3, (540, 1430, 1.3)), (T_NOD1, (540, 1440, 1.32)),
       (T_CLAP, (540, 1420, 1.42)), (T_UNCLAP, (540, 1400, 1.3)), (T_IDEA, (440, 1440, 1.3)), (T_TOSS1, (540, 1440, 1.28)),
       (T_HOVER, (540, 1450, 1.4)), (T_SQUISH, (540, 1440, 1.62)), (T_PULL1, (500, 1420, 1.35)), (T_FLICK1 + 0.2, (300, 1430, 1.3)),
       (T_HI5_0, (540, 1440, 1.28)), (T_HI5 + 0.3, (540, 1420, 1.34)), (T_LAST1, (420, 1440, 1.36)), (T_GIVE1, (540, 1440, 1.3)),
       (DUR, (540, 1470, 1.4))])
CK = [(tt, (x, y - 160, z + 0.17)) for tt, (x, y, z) in CK]
SHAKES = [(T_SLAP1, 14, 0.3), (T_SLAP2, 14, 0.3), (T_CLAP, 10, 0.25), (T_SQUISH, 12, 0.3), (T_FLICK1, 8, 0.25), (T_HI5, 6, 0.2)]


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


def arm_anchor(c, key, side, py0=30):
    hx = c[key][0]
    sd = 1 if hx > c["x"] + 10 else (-1 if hx < c["x"] - 10 else side)
    return sd, py0


# ---------------------------------------------------------------- frame
def blob(x, y, t, s=1.0, flap=True, rot=0.0):
    """two squished gooey marshmallows with the mosquito trapped inside."""
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">']
    # wings sticking out on top (flapping)
    fl = 0.3 + 0.7 * abs(math.sin(t * 95)) if flap else 1
    for wx, wa in ((-8, -20), (8, 20)):
        o.append(f'<g transform="translate({wx} -38) rotate({wa}) scale(1 {fl:.2f})"><ellipse cx="0" cy="-22" rx="11" ry="24" fill="#dff4ff" fill-opacity="0.8" stroke="{OL}" stroke-width="3"/></g>')
    o.append(f'<path d="M-62 -30 Q -70 0 -60 30 Q 0 46 60 30 Q 70 0 62 -30 Q 0 -48 -62 -30Z" fill="#f4c57a" stroke="{OL}" stroke-width="5"/>'
             f'<path d="M-40 -26 Q 0 -38 40 -26" fill="none" stroke="#fff0d0" stroke-width="8" stroke-linecap="round"/>'
             f'<path d="M-4 -34 Q 6 0 -4 34" fill="none" stroke="#d99a4a" stroke-width="4"/>'
             f'<path d="M-30 36 q4 16 -2 26 M24 38 q-2 12 4 20" fill="none" stroke="#f4c57a" stroke-width="7" stroke-linecap="round"/>')
    # mosquito eye + nose peeking out
    o.append(f'<circle cx="12" cy="-6" r="9" fill="#fff" stroke="{OL}" stroke-width="2.5"/><circle cx="14" cy="-6" r="4.5" fill="#c01a2a"/>'
             f'<path d="M22 4 L50 12" stroke="{OL}" stroke-width="4" stroke-linecap="round"/>')
    for k, lx in enumerate((-16, -4, 8)):
        sw = 6 * math.sin(t * 30 + k * 2) if flap else 0
        o.append(f'<path d="M{lx} 34 l{-4+sw:.1f} 20" stroke="{OL}" stroke-width="3" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


def frame(t):
    ctx = Ctx()
    g = grumpo_state(t)
    n = nibbo_state(t)
    L = [world(t)]
    L.append(shadow(GX, GROUND + 6, 120))
    L.append(shadow(NX, GROUND + 6, 110))

    # ---- sticks + marshmallows (behind the fire's front flames? sticks over the fire)
    def g_stick():
        out = [stick(g["hR"], g["tip"])]
        gm = g_marsh(t)
        if gm["show"]:
            ang = stick_ang(g["hR"], g["tip"])
            out.append(marsh(g["tip"][0] - 8 * math.cos(math.radians(ang)), g["tip"][1] - 8 * math.sin(math.radians(ang)), ang,
                             gm["toast"], gm["burnt"], gm["s"], 1.0, gm["flame"], t))
            if T_OUT <= t < T_FRESH:
                L.append(smoke(g["tip"][0], g["tip"][1] - 20, t, T_OUT, 2))
        return "".join(out)

    def n_stick():
        out = [stick(n["hL"], n["tip"])]
        nm = n_marsh(t)
        if nm["show"]:
            ang = stick_ang(n["hL"], n["tip"])
            out.append(marsh(n["tip"][0] - 8 * math.cos(math.radians(ang)), n["tip"][1] - 8 * math.sin(math.radians(ang)), ang,
                             nm["toast"], nm["burnt"], nm["s"], 1.0, nm["flame"], t))
            if T_OUT <= t < T_TOSS0:
                L.append(smoke(n["tip"][0], n["tip"][1] - 20, t, T_OUT + 0.3, 2))
        return "".join(out)

    # Grumpo
    L.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "up", g["look"], g["rot"], g["sx"], g["sy"], drink=False, t=t))
    L.append(grumpo_extra(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], g["kind"], t, g["red"]))
    if g["print"] > 0:
        px, py = bodypt(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], 6, -98)
        L.append(handprint(px, py, g["rot"] + 180, 1.15, "#ffcf3a", g["print"] * 0.85))
    # Nibbo
    L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"] if n["kind"] is None else "blank", rot=n["rot"], sx=n["sx"], sy=n["sy"]))
    L.append(nib_face(n["x"], n["y"], NR, n["rot"], n["sx"], n["sy"], n["kind"]))
    if n["print"] > 0:
        px, py = bodypt(n["x"], n["y"], 1, n["rot"], n["sx"], n["sy"], -78, 10)
        L.append(handprint(px, py, n["rot"] - 90, 0.95, "#c43aa0", n["print"] * 0.7))

    # fire in front of their lower bodies? (fire is between them, draw now)
    L.append(fire(t))
    L.append(g_stick())
    L.append(n_stick())

    # gooey blob on Grumpo's stick after the squish
    if T_SQUISH <= t < T_FLICK0 + 0.12:
        if t < T_PULL0:
            bx, by = FX, 1436
            s = 1 + 0.15 * math.exp(-(t - T_SQUISH) * 8) * math.sin((t - T_SQUISH) * 40)
        else:
            ang = stick_ang(g["hR"], g["tip"])
            bx, by = g["tip"][0] - 10 * math.cos(math.radians(ang)), g["tip"][1] - 10 * math.sin(math.radians(ang))
            s = 1.0
            # goo strand from Nibbo's stick while pulling
            if t < T_PULL1 + 0.1:
                q = seg(t, T_PULL0, T_PULL1 + 0.1)
                L.append(f'<path d="M{bx+40:.0f} {by:.0f} Q {(bx+n["tip"][0])/2:.0f} {by+40+30*q:.0f} {n["tip"][0]-10:.0f} {n["tip"][1]:.0f}" fill="none" stroke="#f4c57a" stroke-width="{10*(1-q)+2:.1f}" stroke-linecap="round"/>')
        L.append(blob(bx, by, t, s))
    if T_FLICK0 + 0.12 <= t < T_FLICK1 + 0.05:
        p = seg(t, T_FLICK0 + 0.12, T_FLICK1 + 0.05)
        x0 = GX + 110 + 230 * math.cos(math.radians(-110))
        y0 = GY - 10 + 230 * math.sin(math.radians(-110))
        bx = lerp(x0, SPLAT[0] + 40, p)
        by = lerp(y0, SPLAT[1], p) - 180 * math.sin(math.pi * p)
        L.append(blob(bx, by, t, 1.0, True, -540 * p))
        L.append(speed_lines(bx + 50, by, 200, 0.8))
    if t >= T_FLICK1 + 0.05:
        k = t - T_FLICK1 - 0.05
        sxv = 1 + 0.2 * math.exp(-k * 7) * math.sin(k * 40)
        L.append(f'<g transform="translate({SPLAT[0]+40:.0f} {SPLAT[1]:.0f}) scale({sxv:.3f} {2-sxv:.3f}) rotate(-90)">' + blob(0, 0, t, 1.0, True) + '</g>')
        L.append(f'<path d="M{SPLAT[0]+10:.0f} {SPLAT[1]+50:.0f} q-4 30 4 50 M{SPLAT[0]+60:.0f} {SPLAT[1]+40:.0f} q4 20 -2 36" fill="none" stroke="#f4c57a" stroke-width="8" stroke-linecap="round"/>')

    # mosquito
    m = mos_state(t)
    if m and m[4] != "gone":
        mx, my, md, mr, mode = m
        L.append(mosquito(mx, my, t, md, 1.0, mr))
        if mode == "fly":
            L.append(buzz_lines(mx - md * 10, my, t, 0.7))

    # the tossed fresh marshmallow
    if T_TOSS0 <= t < T_TOSS1:
        p = seg(t, T_TOSS0, T_TOSS1)
        x = lerp(GX + 20, N_TIP0[0] + 40, p)
        y = lerp(GY - 170, N_TIP0[1] + 10, p) - 260 * math.sin(math.pi * p)
        L.append(marsh(x, y, 720 * p, 0, 0, 0.9))
    # burnt lumps fall off when replaced
    if T_FRESH - 0.15 <= t < T_FRESH + 0.6:
        p = seg(t, T_FRESH - 0.15, T_FRESH + 0.6)
        L.append(marsh(lerp(G_TIP0[0] - 40, G_TIP0[0] - 20, p), lerp(G_TIP0[1] + 10, GROUND - 20, ein(p)), 200 * p, 0, 1, 1.0))
    if T_TOSS1 - 0.05 <= t < T_TOSS1 + 0.6:
        p = seg(t, T_TOSS1 - 0.05, T_TOSS1 + 0.6)
        L.append(marsh(lerp(N_TIP0[0] + 40, N_TIP0[0] + 70, p), lerp(N_TIP0[1] + 10, GROUND - 20, ein(p)), -200 * p, 0, 1, 0.9))
    # last marshmallow (in Grumpo's hand / split / given)
    if T_LAST0 + 0.2 <= t < T_SPLIT0:
        hx, hy = g["hL"]
        L.append(marsh(hx + 6, hy - 34, 0, 0, 0, 0.9))
    if T_SPLIT0 <= t < T_GIVE1 + 0.15:
        q = eio(seg(t, T_SPLIT0, T_SPLIT1))
        lx, ly = g["hL"]
        if t < T_SPLIT1:
            rx_, ry_ = g["hR"]
            L.append(f'<path d="M{lx+20:.0f} {ly-30:.0f} Q {(lx+rx_)/2:.0f} {ly-10:.0f} {rx_-20:.0f} {ry_-30:.0f}" fill="none" stroke="#ffffff" stroke-width="{26*(1-q)+6:.1f}" stroke-linecap="round"/>')
            L.append(marsh(lx + 10, ly - 32, -10, 0, 0, 0.62))
            L.append(marsh(rx_ - 10, ry_ - 32, 10, 0, 0, 0.62))
        else:
            L.append(marsh(lx + 10, ly - 32, -10, 0, 0, 0.62))
            hx, hy = g["hR"] if t < T_GIVE1 else n["hR"] if n["hR"] else g["hR"]
            L.append(marsh(hx, hy - 32, 0, 0, 0, 0.62))
    if T_GIVE1 + 0.15 <= t < T_ONSTICK and n["hR"]:
        hx, hy = n["hR"]
        L.append(marsh(hx, hy - 30, 0, 0, 0, 0.62))
    if t >= T_ONSTICK - 0.1:
        # Grumpo's half on his own stick
        ang = stick_ang(g["hR"], g["tip"])
        L.append(marsh(g["tip"][0] - 8, g["tip"][1] - 4, ang, 0.4 * seg(t, T_ONSTICK, DUR), 0, 0.62))
        if t >= T_ONSTICK:
            nm_ang = stick_ang(n["hL"], n["tip"])

    # ---- arms + hands
    for side, key in ((1, "hR"), (-1, "hL")):
        if g[key]:
            sd, py = arm_anchor(g, key, side)
            sx_, sy_ = bodypt(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], sd * 112, py)
            L.append(arm(sx_, sy_, g[key][0], g[key][1], INK, 14, 20))
    for key in ("hR", "hL"):
        if g[key]:
            L.append(hand(*g[key], mix_hex(GFILL, "#ff6a52", g["red"]), OL, 19))
    for side, key in ((-1, "hL"), (1, "hR")):
        if n[key]:
            sd, py = arm_anchor(n, key, side, 26)
            sx_, sy_ = bodypt(n["x"], n["y"], 1, n["rot"], n["sx"], n["sy"], sd * 96, py)
            L.append(arm(sx_, sy_, n[key][0], n[key][1], NS, 11, 16))
    for key in ("hL", "hR"):
        if n[key]:
            L.append(hand(*n[key], NB, NS, 15))

    # ---- effects
    L.append(symbol(n["x"] + 10, n["y"] - 170, "!", seg(t, T_NSEE, T_NSEE + 0.5)))
    L.append(impact(G_HEAD[0] + 10, G_HEAD[1], seg(t, T_SLAP1, T_SLAP1 + 0.25)))
    if g["stars"] > 0:
        L.append(dizzy_stars(g["x"], g["y"] - GR - 10, t, 95, g["stars"]))
    L.append(symbol(g["x"] + 20, g["y"] - 190, "!", seg(t, T_GSMUG, T_GSMUG + 0.5), "#ffb02a"))
    if T_WIND2_0 <= t < T_SLAP2:
        L.append(speed_lines(g["hL"][0], g["hL"][1], 0, 0.6) if t >= T_WIND2_1 else "")
    L.append(impact(N_CHEEK[0], N_CHEEK[1], seg(t, T_SLAP2, T_SLAP2 + 0.25)))
    if T_SLAP2 < t < T_SPIN1:
        L.append(speed_lines(n["x"] + 120, n["y"], 90, 0.6))
    if n["stars"] > 0:
        L.append(dizzy_stars(n["x"], n["y"] - NR - 10, t, 80, n["stars"]))
    L.append(symbol(g["x"] + 20, g["y"] - 190, "!", seg(t, T_NOTICE, T_NOTICE + 0.5)))
    L.append(symbol(n["x"] + 10, n["y"] - 170, "!", seg(t, T_NOTICE + 0.05, T_NOTICE + 0.55)))
    if T_BLOW0 + 0.1 <= t < T_OUT:
        for c, sgn in ((g, 1), (n, -1)):
            tip = c["tip"]
            for k in range(3):
                q = ((t - T_BLOW0) * 4 + k / 3) % 1
                x0 = c["x"] + sgn * 70
                L.append(f'<path d="M{lerp(x0, tip[0], q):.0f} {lerp(c["y"] - 10, tip[1], q) + (k-1)*14:.0f} l{sgn*30} -4" stroke="#ffffff" stroke-width="5" stroke-linecap="round" opacity="{1-q:.2f}"/>')
    L.append(impact(g["tip"][0], g["tip"][1] - 10, seg(t, T_OUT, T_OUT + 0.3), "#cfcfd8"))
    L.append(impact(n["tip"][0], n["tip"][1] - 10, seg(t, T_OUT, T_OUT + 0.3), "#cfcfd8"))
    L.append(impact(FX, 1386, seg(t, T_CLAP, T_CLAP + 0.3)))
    L.append(symbol(g["x"] + 20, g["y"] - 190, "!", seg(t, T_IDEA, T_IDEA + 0.6), "#ffb02a"))
    if T_IDEA <= t < T_IDEA + 0.6:
        L.append(star_twinkle(g["x"] - 70, g["y"] - 150, seg(t, T_IDEA, T_IDEA + 0.6)))
    L.append(star_twinkle(GX - 60, GY - 70, seg(t, T_FRESH - 0.05, T_FRESH + 0.4)))
    L.append(impact(N_TIP0[0] + 40, N_TIP0[1] + 10, seg(t, T_TOSS1, T_TOSS1 + 0.25), "#ffffff"))
    if T_ROAST0 + 0.4 <= t < T_SWING0:
        op = seg(t, T_ROAST0 + 0.4, T_ROAST0 + 0.8)
        L.append(smell(FX - 72, 1410, t, op))
        L.append(smell(FX + 72, 1410, t + 0.4, op))
    L.append(impact(FX, 1436, seg(t, T_SQUISH, T_SQUISH + 0.3), "#fff0c8"))
    L.append(impact(SPLAT[0] + 40, SPLAT[1], seg(t, T_FLICK1 + 0.05, T_FLICK1 + 0.35), "#fff0c8"))
    if t >= T_FLICK1 + 0.3:
        L.append(buzz_lines(SPLAT[0] + 110, SPLAT[1] - 40, t, 0.5))
    L.append(impact(FX, 1330, seg(t, T_HI5, T_HI5 + 0.3)))
    L.append(star_twinkle(FX - 50, 1270, seg(t, T_HI5, T_HI5 + 0.6)))
    L.append(star_twinkle(FX + 60, 1300, seg(t, T_HI5 + 0.1, T_HI5 + 0.7)))
    L.append(symbol(n["x"] + 10, n["y"] - 170, "?", seg(t, T_LAST1 + 0.1, T_LAST1 + 0.7), "#3a8fd8"))
    L.append(heart(n["x"] + 10, n["y"] - 150, seg(t, T_GIVE1, T_GIVE1 + 1.0)))
    L.append(heart(g["x"] + 30, g["y"] - 170, seg(t, T_COZY + 0.4, T_COZY + 1.4)))

    # warm firelight over everything
    fl = 1 + 0.05 * math.sin(t * 13)
    L.append(f'<ellipse cx="{FX}" cy="{GROUND-200}" rx="{700*fl:.0f}" ry="{520*fl:.0f}" fill="url(#warm)"/>')

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{defs()}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g>'
           f'<rect width="{W}" height="{H}" fill="url(#vig)"/></svg>')
    return overlay(svg, hook_title(t + 0.12, "Campfire night vs", "1 MOSQUITO"))


def build_sfx():
    k = 0.0
    while k < DUR:
        sfx(k, "crackle", 0.35, 1.0)
        k += 1.9
    # mosquito buzz while flying
    for a, b, p in [(0.0, T_LAND1, 1.0), (T_ML1, T_LAND2, 1.05), (T_ML2, T_ML2 + 0.6, 1.1), (T_M3, T_ML3 + 1.0, 1.0),
                    (T_CLAPUP, T_M4 - 0.3, 1.15), (T_M4, T_SQUISH, 0.95)]:
        k = a
        while k < b - 0.2:
            sfx(k, "buzz", 0.55, p)
            k += 1.0
    sfx(0.0, "zoom", 0.4, 1.6)
    sfx(T_LAND1, "tap", 0.5, 1.6)
    sfx(T_LAND1 + 0.3, "suck", 0.35, 1.8)
    sfx(T_NSEE, "gasp", 0.5, 1.4)
    sfx(T_WIND1_0, "whoosh", 0.5, 1.2)
    sfx(T_ML1, "zip", 0.6, 1.5)
    sfx(T_SLAP1, "slap", 1.0, 1.0)
    sfx(T_SLAP1 + 0.02, "bonk", 0.5, 1.0)
    sfx(T_SLAP1 + 0.15, "wobble", 0.5, 1.0)
    sfx(T_GLARE, "grumble", 0.7, 0.9)
    sfx(T_GLARE + 0.3, "squeak", 0.4, 1.4)
    sfx(T_LAND2, "tap", 0.5, 1.7)
    sfx(T_GSMUG, "laugh", 0.4, 0.8)
    sfx(T_WIND2_0, "whirr", 0.5, 1.2)
    sfx(T_ML2, "zip", 0.6, 1.6)
    sfx(T_SLAP2, "slap", 1.0, 1.1)
    sfx(T_SLAP2 + 0.05, "zoom", 0.5, 1.4)
    sfx(T_SLAP2 + 0.1, "whirr", 0.4, 1.6)
    sfx(T_IGN, "sizzle", 0.5, 1.0)
    sfx(T_IGN + 0.5, "sizzle", 0.5, 0.9)
    sfx(T_NOTICE, "gasp", 0.7, 1.0)
    sfx(T_NOTICE + 0.05, "alert", 0.4, 1.2)
    sfx(T_BLOW0, "blow", 0.9, 1.0)
    sfx(T_BLOW0 + 0.35, "blow", 0.9, 1.1)
    sfx(T_OUT, "poof", 0.8, 1.0)
    sfx(T_SAD0, "blip_down", 0.6, 0.9)
    sfx(T_ANGRY3, "grumble", 0.6, 0.95)
    sfx(T_NOD0, "blip", 0.4, 1.0)
    sfx(T_NOD0 + 0.2, "blip", 0.4, 1.2)
    sfx(T_WIND3_0, "whoosh", 0.6, 1.0)
    sfx(T_ML3, "zip", 0.6, 1.7)
    sfx(T_CLAP, "slap", 1.0, 1.25)
    sfx(T_CLAP + 0.03, "slap", 0.6, 0.9)
    sfx(T_CLAPUP + 0.5, "slide_up", 0.4, 1.8)
    sfx(T_IDEA, "ding", 0.7, 1.0)
    sfx(T_FRESH, "pop", 0.7, 1.1)
    sfx(T_TOSS0, "whoosh", 0.5, 1.3)
    sfx(T_TOSS1, "squish", 0.6, 1.4)
    sfx(T_ROAST0 + 0.2, "sizzle", 0.4, 1.2)
    sfx(T_M4 + 0.6, "inhale", 0.4, 1.8)
    sfx(T_WINK, "cool", 0.5, 1.0)
    sfx(T_SWING0, "whoosh", 0.7, 1.0)
    sfx(T_SQUISH, "squish", 1.0, 0.9)
    sfx(T_SQUISH + 0.02, "splat", 0.7, 1.0)
    sfx(T_SQUISH + 0.2, "buzz", 0.4, 1.6)
    sfx(T_SQUISH + 0.25, "cheer", 0.5, 1.3)
    sfx(T_PULL0, "stretch", 0.6, 1.2)
    sfx(T_FLICK0, "whoosh", 0.7, 0.9)
    sfx(T_FLICK1, "splat", 1.0, 0.9)
    sfx(T_FLICK1 + 0.3, "buzz", 0.3, 1.8)
    sfx(T_HI5, "slap", 0.9, 1.3)
    sfx(T_HI5 + 0.05, "ding", 0.5, 1.4)
    sfx(T_HI5 + 0.2, "laugh", 0.6, 1.2)
    sfx(T_LAST0, "rustle", 0.5, 1.0)
    sfx(T_LAST1, "blip", 0.5, 1.0)
    sfx(T_SPLIT0, "stretch", 0.7, 1.3)
    sfx(T_SPLIT1, "pop", 0.7, 1.2)
    sfx(T_GIVE1, "shine", 0.6, 1.2)
    sfx(T_ONSTICK, "squish", 0.4, 1.6)
    sfx(T_COZY + 0.4, "ding", 0.4, 1.6)
