"""Grumpo & Nibbo — Episode 15: Shhh! (library sneeze, 60 fps).

Silent library, one long reading table. Nibbo opens a dusty old book: dust in the face -> a sneeze starts building.
Grumpo (reading) won't allow a single sound. Structure E: ONE escalating gag — every sneeze Grumpo blocks is stored
and the next one is bigger (on-screen counter: SNEEZE 25% -> 60% -> 150% -> 400% -> 999%).
  1. hand slapped over Nibbo's mouth -> muffled 'mff', cheeks puff. Grumpo does a smug 'shh'.
  2. Nibbo turns a page, more dust -> Grumpo claps his big book shut on Nibbo's face -> pages burst out.
  3. a dust bunny drops from the shelf -> Grumpo vaults the table and SITS on Nibbo -> big muffled jolt,
     Grumpo bounces, his sunglasses drop onto his eyes (cool). He reads on top of Nibbo.
Final: Nibbo inhales from below, swelling, lifting Grumpo up; counter races to 999% -> ACHOO: Grumpo is blasted
into the bookshelf, flattened, slides down onto the table and the whole shelf avalanches books onto him (only his
eyes stick out), some books onto Nibbo too. Quiet. Nibbo smugly gives Grumpo the 'shh'... a loose page floats onto
Nibbo's face: 'ah...' (SNEEZE 25% again) -> Grumpo's horror face, he dives at Nibbo — cut. Ending: both lose.
"""
import math, sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow
from hook import overlay, hook_title, counter

W, H, FPS, DUR = 1080, 1920, 60, 21.4
GS = 0.92
NR = 112
INK = "#1a0a2e"
GFILL = "#9466e0"
NB, NS = "#ffd23c", "#3d2a12"

TOP = 1405          # table top (back edge)
TFRONT = 1445       # table front edge
FLOOR = 1780
G0 = (450.0, 1322.0)
N0 = (770.0, 1335.0)
SHELF_L = (70, 470)
SHELF_R = (730, 1130)
SH_TOP = 560
ROWS = [700, 850, 1000, 1150, 1300]   # shelf board y (books stand on them)
SPL = (300.0, 1090.0)                 # where Grumpo splats on the left shelf
LAND = (430.0, 1308.0)                # Grumpo lands on the table here

# ---- times
T_DUST1 = 0.12
T_AH1_0, T_AH1_1 = 0.3, 1.2
T_CNT = 0.45
T_GLANCE, T_GSHOCK = 0.7, 0.95
T_SLAP = 1.28
T_MUFF1 = 1.48
T_UNSLAP = 2.0
T_SHH0, T_SHH1 = 2.15, 3.0
T_READ = 3.05
T_PAGE = 3.45
T_DUST2 = 3.6
T_AH2_0, T_AH2_1 = 3.8, 4.85
T_PANIC = 4.15
T_CLAMP = 4.95
T_MUFF2 = 5.15
T_UNCLAMP = 5.8
T_BUNNY0, T_BUNNY1 = 6.75, 7.2
T_AH3_0, T_AH3_1 = 7.3, 8.35
T_HOP0, T_HOP1 = 7.85, 8.4
T_MUFF3 = 8.65
T_BOUNCE1 = 9.05
T_COOL0 = 9.25
T_INF0, T_INF1 = 10.5, 12.95
T_WORRY = 11.3
T_SCARED = 12.2
T_BLAST = 13.05
T_SPLAT = 13.38
T_SLIDE0, T_SLIDE1 = 14.15, 14.6
T_DROP1 = 14.85
T_WOB = 14.9
T_AV0, T_AV1 = 15.25, 16.75
T_QUIET = 16.9
T_SHHN0, T_SHHN1 = 17.6, 18.9
T_PF0, T_PF1 = 18.45, 19.15
T_AH4_0 = 19.2
T_HORROR = 19.5
T_DIVE0, T_DIVE1 = 20.25, 20.6
T_END = DUR

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


def wob(t, t0, d=0.6, a=10.0, f=18.0):
    k = t - t0
    if 0 <= k < d:
        return a * math.exp(-k * 5) * math.sin(k * f)
    return 0.0


def bodypt(x, y, s, rot, sx, sy, px, py):
    a = math.radians(rot)
    lx, ly = px * s * sx, py * s * sy
    return x + lx * math.cos(a) - ly * math.sin(a), y + lx * math.sin(a) + ly * math.cos(a)


def arm(x0, y0, x1, y1, col, w=13, sag=20):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    return f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


def hand(x, y, fill, stroke, r=16):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="5"/>'


def finger_hand(x, y, fill, stroke, r=16, rot=0):
    """hand with index finger raised ('shh')."""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">'
            f'<rect x="{-r*0.32:.1f}" y="{-r*2.6:.1f}" width="{r*0.64:.1f}" height="{r*2.4:.1f}" rx="{r*0.32:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="5"/>'
            f'<circle r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="5"/></g>')


# ---------------------------------------------------------------- books
PAL = ["#c8423a", "#2f7fd8", "#2f9e5a", "#7d4cc4", "#e07b2a", "#1f8f87", "#b5552e", "#34495e", "#e8b830", "#8a8f9a", "#b03a6f", "#5a7a2a"]


def book_rect(x, y, w, h, col, rot=0.0, cx=None, cy=None):
    """book standing on (x, y) bottom-left, w wide, h tall; or rotated around its centre."""
    bx, by = x + w / 2, y - h / 2
    if cx is not None:
        bx, by = cx, cy
    band = mix_hex(col, "#ffffff", 0.45)
    dark = mix_hex(col, "#000000", 0.25)
    return (f'<g transform="translate({bx:.1f} {by:.1f}) rotate({rot:.1f})">'
            f'<rect x="{-w/2:.1f}" y="{-h/2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3" fill="{col}" stroke="{OL}" stroke-width="3.5"/>'
            f'<rect x="{w/2-w*0.28:.1f}" y="{-h/2+3:.1f}" width="{w*0.22:.1f}" height="{h-6:.1f}" fill="{dark}" opacity="0.6"/>'
            f'<path d="M{-w/2+3:.1f} {-h*0.28:.1f} h{w-6:.1f} M{-w/2+3:.1f} {h*0.26:.1f} h{w-6:.1f}" stroke="{band}" stroke-width="{max(3, w*0.12):.1f}"/></g>')


def make_shelf_books(x0, x1, seed):
    rnd = random.Random(seed)
    books = []
    for ri, by in enumerate(ROWS):
        x = x0 + 26
        while x < x1 - 60:
            w = rnd.uniform(24, 44)
            h = rnd.uniform(86, 122)
            col = rnd.choice(PAL)
            lean = 0
            if rnd.random() < 0.08 and x < x1 - 120:
                lean = -14
            books.append(dict(x=x, y=by, w=w, h=h, col=col, row=ri, lean=lean))
            x += w + rnd.uniform(1, 4)
            if rnd.random() < 0.06:
                x += rnd.uniform(16, 40)
    return books


BOOKS_L = make_shelf_books(*SHELF_L, 11)
BOOKS_R = make_shelf_books(*SHELF_R, 23)


def plan_avalanche(books, cx, hmax, halfw, t0, t1, seed, count, rows_min=1):
    """choose books that fall, with landing spots forming a pile around cx."""
    rnd = random.Random(seed)
    cand = [i for i, b in enumerate(books) if b["row"] >= rows_min]
    rnd.shuffle(cand)
    cand = cand[:count]
    # fall order: top rows first-ish, left to right wave
    cand.sort(key=lambda i: (books[i]["x"] * 0.002 - books[i]["row"] * 0.25 + rnd.uniform(0, 0.4)))
    plan = {}
    n = len(cand)
    for k, i in enumerate(cand):
        b = books[i]
        ts = t0 + (t1 - t0) * k / max(1, n - 1) * 0.85 + rnd.uniform(0, 0.08)
        dx = rnd.uniform(-halfw, halfw)
        frac = (k + 1) / n
        hgt = hmax * (1 - (dx / (halfw * 1.15)) ** 2) * (0.25 + 0.75 * frac)
        lx, ly = cx + dx, TOP + 22 - hgt
        rot = rnd.choice([1, -1]) * rnd.uniform(70, 105) + rnd.uniform(-12, 12)
        plan[i] = dict(ts=ts, dur=rnd.uniform(0.32, 0.45), lx=lx, ly=ly, rot=rot, spin=rnd.uniform(-200, 200))
    return plan


AV_L = plan_avalanche(BOOKS_L, LAND[0], 92, 220, T_AV0, T_AV1, 5, 46)
AV_R = plan_avalanche(BOOKS_R, N0[0] + 10, 26, 160, T_AV0 + 0.35, T_AV1, 9, 11, rows_min=2)
# books blown off by the blast (fly forward/out of frame)
rb = random.Random(77)
BLOWN = [i for i in range(len(BOOKS_L)) if BOOKS_L[i]["row"] == 0 and i not in AV_L][:6]


def book_state(b, i, plan, t, blown=False):
    """returns (svg, layer) ; layer 'shelf' | 'front'"""
    lean = b["lean"]
    sx, sy = b["x"] + b["w"] / 2, b["y"] - b["h"] / 2
    wobx = 0.0
    if T_WOB <= t < T_AV1:
        wobx = 3 * math.sin(t * 40 + i) * (1 - seg(t, T_WOB, T_AV1))
    if blown and t >= T_BLAST:
        p = seg(t, T_BLAST + 0.02 * (i % 5), T_BLAST + 0.6)
        if p >= 1:
            return "", "shelf"
        x = sx - 400 * p + 30 * i
        y = sy - 260 * p + 900 * p * p
        return book_rect(0, 0, b["w"] * (1 + p * 0.8), b["h"] * (1 + p * 0.8), b["col"], 300 * p, x, y), "front"
    if i in plan:
        pl = plan[i]
        if t >= pl["ts"]:
            p = seg(t, pl["ts"], pl["ts"] + pl["dur"])
            x = lerp(sx, pl["lx"], p)
            y = lerp(sy, pl["ly"], p) - 70 * math.sin(math.pi * p) * (1 - p)
            y = sy + (pl["ly"] - sy) * (p * p) if pl["ly"] > sy else lerp(sy, pl["ly"], eout(p))
            rot = lerp(lean, pl["rot"], eout(p)) + (pl["spin"] * math.sin(math.pi * p) if p < 1 else 0)
            sc = 1 + 0.3 * p
            if p >= 1:
                rot += wob(t, pl["ts"] + pl["dur"], 0.3, 6, 30)
            return book_rect(0, 0, b["w"] * sc, b["h"] * sc, b["col"], rot, x, y), "front"
    if lean:
        return book_rect(0, 0, b["w"], b["h"], b["col"], lean, sx + wobx - 6, sy + 4), "shelf"
    return book_rect(b["x"] + wobx, b["y"], b["w"], b["h"], b["col"]), "shelf"


# ---------------------------------------------------------------- room
def defs():
    return ('<linearGradient id="wallL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9d2a8"/><stop offset="1" stop-color="#d7b98a"/></linearGradient>'
            '<linearGradient id="woodS" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8a5a34"/><stop offset="1" stop-color="#6e4426"/></linearGradient>'
            '<linearGradient id="tableTop" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c98a52"/><stop offset="1" stop-color="#b2733e"/></linearGradient>'
            '<linearGradient id="tableFr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9a5e30"/><stop offset="1" stop-color="#7a4520"/></linearGradient>'
            '<linearGradient id="winSky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5aa6ee"/><stop offset="1" stop-color="#cbeaff"/></linearGradient>'
            '<radialGradient id="lampGlow"><stop offset="0" stop-color="#fff2b8" stop-opacity="0.75"/><stop offset="1" stop-color="#fff2b8" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="vig" cx="0.5" cy="0.58" r="0.8"><stop offset="0.6" stop-color="#2a1608" stop-opacity="0"/><stop offset="1" stop-color="#2a1608" stop-opacity="0.38"/></radialGradient>'
            '<radialGradient id="dustG"><stop offset="0" stop-color="#d8cdb8" stop-opacity="0.95"/><stop offset="1" stop-color="#cbbfa8" stop-opacity="0"/></radialGradient>')


def shelf_frame(x0, x1, rot=0.0, sx=1.0, sy=1.0, pivot=None):
    o = []
    o.append(f'<rect x="{x0}" y="{SH_TOP}" width="{x1-x0}" height="{TOP+60-SH_TOP}" rx="8" fill="url(#woodS)" stroke="{OL}" stroke-width="7"/>')
    o.append(f'<rect x="{x0+18}" y="{SH_TOP+20}" width="{x1-x0-36}" height="{TOP+60-SH_TOP-20}" fill="#4a2c16"/>')
    for by in ROWS:
        o.append(f'<rect x="{x0+10}" y="{by}" width="{x1-x0-20}" height="22" fill="#9a6a40" stroke="{OL}" stroke-width="5"/>'
                 f'<rect x="{x0+14}" y="{by+3}" width="{x1-x0-28}" height="6" fill="#b9875a"/>')
    o.append(f'<rect x="{x0-16}" y="{SH_TOP-26}" width="{x1-x0+32}" height="40" rx="8" fill="#9a6a40" stroke="{OL}" stroke-width="6"/>')
    return "".join(o)


def room(t):
    o = [f'<rect x="-700" y="-200" width="2600" height="2400" fill="url(#wallL)"/>']
    # wallpaper stripes
    for k in range(-14, 40):
        o.append(f'<rect x="{k*70}" y="-200" width="26" height="{TOP+30}" fill="#e1c597" opacity="0.55"/>')
    # wainscot
    o.append(f'<rect x="-700" y="1180" width="2600" height="{TOP+80-1180}" fill="#a8703f" stroke="{OL}" stroke-width="6"/>')
    for k in range(-8, 24):
        o.append(f'<rect x="{k*120+14}" y="1205" width="92" height="160" rx="6" fill="#b47c48" stroke="#8a5530" stroke-width="4"/>')
    # arched window (center, high)
    o.append(f'<path d="M520 1060 V760 Q 600 640 680 760 V1060Z" fill="#f3e4c6" stroke="{OL}" stroke-width="7"/>'
             f'<path d="M538 1046 V768 Q 600 670 662 768 V1046Z" fill="url(#winSky)"/>'
             f'<path d="M600 680 V1046 M538 880 H662" stroke="#f3e4c6" stroke-width="10"/>'
             f'<path d="M548 1000 l40 -60" stroke="#fff" stroke-width="8" opacity="0.4" stroke-linecap="round"/>'
             f'<rect x="506" y="1056" width="188" height="20" rx="6" fill="#f3e4c6" stroke="{OL}" stroke-width="5"/>')
    # far shelves (outside the two hero shelves)
    for x0 in (-560, -250, 1190, 1500):
        o.append(f'<rect x="{x0}" y="{SH_TOP+40}" width="260" height="{TOP-SH_TOP}" rx="8" fill="#7a4c2a" stroke="{OL}" stroke-width="6"/>')
        rnd = random.Random(x0)
        for by in ROWS:
            x = x0 + 20
            while x < x0 + 230:
                w = rnd.uniform(22, 38)
                h = rnd.uniform(80, 112)
                o.append(f'<rect x="{x:.0f}" y="{by-h:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{mix_hex(rnd.choice(PAL), "#7a4c2a", 0.35)}" stroke="{OL}" stroke-width="3"/>')
                x += w + 2
            o.append(f'<rect x="{x0+8}" y="{by}" width="244" height="18" fill="#8f5f36" stroke="{OL}" stroke-width="4"/>')
    return "".join(o)


def poster(x, y, glint=0.0, rot=0.0):
    """'shh' icon poster: face with finger on lips (no words)."""
    return (f'<g transform="translate({x} {y}) rotate({rot:.1f})">'
            f'<rect x="-56" y="-66" width="112" height="132" rx="10" fill="#fdf6e4" stroke="{OL}" stroke-width="6"/>'
            f'<circle cy="-6" r="38" fill="#ffd9b0" stroke="{OL}" stroke-width="4"/>'
            f'<path d="M-18 -16 h10 M8 -16 h10" stroke="{OL}" stroke-width="5" stroke-linecap="round"/>'
            f'<circle cy="12" r="6" fill="{OL}"/>'
            f'<rect x="-5" y="-6" width="10" height="44" rx="5" fill="#ffc48a" stroke="{OL}" stroke-width="3.5"/>'
            f'<rect x="-40" y="44" width="80" height="12" rx="6" fill="#e8475e"/>'
            + (star_twinkle(40, -50, glint) if glint > 0 else "") + '</g>')


def chair(x, y_top):
    return (f'<path d="M{x-110} {TOP} V{y_top+40} Q {x-110} {y_top} {x-70} {y_top} H{x+70} Q {x+110} {y_top} {x+110} {y_top+40} V{TOP}" fill="#7a4626" stroke="{OL}" stroke-width="6"/>'
            f'<path d="M{x-80} {y_top+30} H{x+80}" stroke="#9a6236" stroke-width="10" stroke-linecap="round"/>')


def table():
    return (f'<path d="M-700 {TOP} H1900 V{TFRONT} H-700Z" fill="url(#tableTop)" stroke="{OL}" stroke-width="6"/>'
            f'<path d="M-700 {TOP+10} H1900" stroke="#dba06a" stroke-width="5" opacity="0.8"/>'
            f'<rect x="-700" y="{TFRONT}" width="2600" height="{FLOOR-TFRONT}" fill="url(#tableFr)" stroke="{OL}" stroke-width="6"/>'
            + "".join(f'<rect x="{k*260+40}" y="{TFRONT+40}" width="200" height="{FLOOR-TFRONT-80}" rx="10" fill="none" stroke="#6a3a18" stroke-width="6"/>' for k in range(-3, 8))
            + f'<rect x="-700" y="{FLOOR}" width="2600" height="400" fill="#5a3420"/>')


def lamp(x, t, spin=0.0, glow=1.0):
    o = []
    if glow > 0:
        o.append(f'<ellipse cx="{x}" cy="{TOP-20}" rx="170" ry="70" fill="url(#lampGlow)" opacity="{glow:.2f}"/>')
    o.append(f'<rect x="{x-44}" y="{TOP-14}" width="88" height="20" rx="8" fill="#c9a23a" stroke="{OL}" stroke-width="5"/>'
             f'<rect x="{x-6}" y="{TOP-78}" width="12" height="66" fill="#c9a23a" stroke="{OL}" stroke-width="4"/>')
    o.append(f'<g transform="translate({x} {TOP-86}) rotate({spin:.1f}) scale(0.78)">'
             f'<path d="M-72 18 Q -66 -20 0 -24 Q 66 -20 72 18Z" fill="#2f8f5a" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
             f'<path d="M-52 4 Q 0 -14 52 4" fill="none" stroke="#5cc489" stroke-width="6" stroke-linecap="round"/>'
             f'<rect x="-72" y="14" width="144" height="10" rx="5" fill="#fff2b8" stroke="{OL}" stroke-width="3"/></g>')
    return "".join(o)


def old_book(x, y, openp=1.0, flutter=0.0, t=0.0):
    """Nibbo's dusty book lying open on the table."""
    o = [f'<g transform="translate({x:.1f} {y:.1f})">']
    o.append(f'<path d="M-96 0 L-90 -18 L90 -18 L96 0 Z" fill="#6a3d1e" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>')
    ang = 1 - openp
    o.append(f'<path d="M0 -14 Q -44 {-26-30*ang:.1f} -86 -14 L-84 -6 Q -44 -16 0 -4Z" fill="#efe2c2" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>')
    o.append(f'<path d="M0 -14 Q 44 {-26-30*ang:.1f} 86 -14 L84 -6 Q 44 -16 0 -4Z" fill="#f6ead0" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>')
    o.append(f'<path d="M-70 -14 q30 -8 60 -2 M10 -14 q30 -8 60 -2" fill="none" stroke="#c9b48c" stroke-width="3"/>')
    if flutter > 0:
        for k in range(3):
            a = 80 * math.sin(t * 30 + k * 1.7) * flutter
            o.append(f'<path d="M0 -12 Q {20+k*10:.0f} {-40-k*6:.0f} {60*math.cos(math.radians(a)):.0f} {-14-60*abs(math.sin(math.radians(a))):.0f}" fill="#fffaf0" stroke="{OL}" stroke-width="3" opacity="0.95"/>')
    o.append('</g>')
    return "".join(o)


def big_book(x, y, rot=0.0, mode="open", s=1.0):
    """Grumpo's big red hardcover. mode: open (reading, pages to viewer), closed (cover to viewer)."""
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">']
    if mode == "open":
        o.append(f'<path d="M-104 -66 L0 -54 L104 -66 L104 50 L0 62 L-104 50Z" fill="#b8322a" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
                 f'<path d="M-94 -60 L-2 -48 L-2 54 L-94 42Z" fill="#fbf3dc" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>'
                 f'<path d="M94 -60 L2 -48 L2 54 L94 42Z" fill="#f4e8cc" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>'
                 f'<path d="M-80 -36 l64 8 M-80 -16 l64 8 M-80 4 l50 6 M16 -26 l64 -8 M16 -6 l64 -8 M16 14 l50 -6" stroke="#c9b48c" stroke-width="5" stroke-linecap="round"/>')
    else:
        o.append(f'<rect x="-82" y="-66" width="164" height="124" rx="8" fill="#b8322a" stroke="{OL}" stroke-width="6"/>'
                 f'<rect x="-82" y="-66" width="22" height="124" rx="6" fill="#8e2219" stroke="{OL}" stroke-width="4"/>'
                 f'<rect x="-40" y="-40" width="96" height="60" rx="6" fill="none" stroke="#e8b830" stroke-width="6"/>'
                 f'<circle cx="8" cy="-10" r="12" fill="#e8b830"/>'
                 f'<path d="M82 -60 v112" stroke="#fbf3dc" stroke-width="7"/>')
    o.append('</g>')
    return "".join(o)


def dust_puff(x, y, p, s=1.0):
    if p <= 0 or p >= 1:
        return ""
    o = []
    for k in range(7):
        a = math.radians(-160 + k * 23)
        r = (20 + 70 * eout(p)) * s
        cx = x + r * math.cos(a) * 1.3
        cy = y + r * math.sin(a) - 20 * p * s
        rr = (16 + 22 * p) * s * (0.8 + 0.3 * (k % 2))
        o.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{rr:.0f}" fill="#d8cdb8" stroke="#a89a80" stroke-width="3" opacity="{(1-p)*0.95:.2f}"/>')
    return "".join(o)


def dust_stream(x0, y0, x1, y1, t, t0, t1):
    """particles drifting from (x0,y0) to (x1,y1)."""
    if not (t0 <= t < t1 + 0.2):
        return ""
    o = []
    for k in range(9):
        p = seg(t, t0 + k * 0.06, t1 - 0.3 + k * 0.05)
        if p <= 0 or p >= 1:
            continue
        x = lerp(x0, x1, eio(p)) + 22 * math.sin(p * 7 + k)
        y = lerp(y0, y1, eio(p)) + 16 * math.cos(p * 5 + k * 2)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{5+3*(k%3)}" fill="#e6dcc6" stroke="#a89a80" stroke-width="2" opacity="{min(1, (1-p)*3):.2f}"/>')
    return "".join(o)


def dust_bunny(x, y, rot=0.0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<path d="M-30 6 Q -36 -18 -14 -22 Q -6 -36 10 -26 Q 32 -28 30 -6 Q 40 10 22 18 Q 0 28 -18 20 Q -38 20 -30 6Z" fill="#cfc4ae" stroke="#7d7260" stroke-width="4"/>'
            f'<path d="M-30 -6 l-12 -6 M30 -2 l12 -4 M-10 -24 l-4 -12 M14 22 l6 10" stroke="#7d7260" stroke-width="3" stroke-linecap="round"/></g>')


def page(x, y, rot, s=1.0, op=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})" opacity="{op:.2f}">'
            f'<path d="M-32 -42 H24 L34 -30 V42 H-32Z" fill="#fffaf0" stroke="{OL}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M-22 -24 h40 M-22 -10 h46 M-22 4 h46 M-22 18 h30" stroke="#c9b48c" stroke-width="4" stroke-linecap="round"/></g>')


def wind_lines(x, y, p, ang=-130):
    if p <= 0 or p >= 1:
        return ""
    o = []
    a = math.radians(ang)
    for k in range(9):
        off = (k - 4) * 46
        nx, ny = -math.sin(a) * off, math.cos(a) * off
        d0 = 60 + 500 * p + (k % 3) * 40
        L = 140 + (k % 2) * 80
        x0, y0 = x + nx + d0 * math.cos(a), y + ny + d0 * math.sin(a)
        o.append(f'<line x1="{x0:.0f}" y1="{y0:.0f}" x2="{x0+L*math.cos(a):.0f}" y2="{y0+L*math.sin(a):.0f}" stroke="#ffffff" stroke-width="12" stroke-linecap="round" opacity="{(1-p)*0.9:.2f}"/>')
    return "".join(o)


# ---------------------------------------------------------------- faces
def grumpo_extra(x, y, s, rot, sx, sy, kind, t, red=0.0, a=0.0):
    if not kind:
        return ""
    ink = mix_hex(INK, "#3a0505", red)
    base = mix_hex("#9466e0", "#ff6a52", red)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s*sx:.3f} {s*sy:.3f})">']
    worried = f'<path d="M-72 -28 Q -46 -36 -16 -54 M16 -54 Q 46 -36 72 -28" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>'
    if kind == "shh":     # stern, pursed lips
        o.append(f'<path d="M-60 16 h44 v-22 h-44z M16 16 h44 v-22 h-44z" fill="{base}"/>'
                 f'<path d="M-58 14 h40 M18 14 h40" stroke="{ink}" stroke-width="6" stroke-linecap="round"/>'
                 f'<path d="M-72 -30 Q -44 -20 -16 -8 M72 -30 Q 44 -20 16 -8" fill="none" stroke="{ink}" stroke-width="17" stroke-linecap="round"/>'
                 f'<ellipse cx="0" cy="74" rx="12" ry="10" fill="#4a0a14" stroke="{ink}" stroke-width="6"/>')
    elif kind == "worried":
        o.append(worried + f'<path d="M-30 78 q10 -10 20 0 t20 0 t20 0" fill="none" stroke="{ink}" stroke-width="8" stroke-linecap="round"/>')
        dp = (t * 1.5) % 1
        o.append(f'<path d="M100 {-40+dp*50:.0f} q12 18 0 28 q-12 -10 0 -28z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3" opacity="{1-dp:.2f}"/>')
    elif kind == "smugread":   # glasses down, smug grin
        o.append(f'<path d="M-30 66 q34 22 64 -10" fill="none" stroke="{ink}" stroke-width="10" stroke-linecap="round"/>'
                 f'<path d="M-72 -34 Q -44 -26 -16 -16 M72 -34 Q 44 -26 16 -16" fill="none" stroke="{ink}" stroke-width="15" stroke-linecap="round"/>')
    elif kind == "squished":
        o.append(f'<path d="M-72 -40 Q -40 -64 -8 -44 M8 -44 Q 40 -64 72 -40" fill="none" stroke="{ink}" stroke-width="16" stroke-linecap="round"/>'
                 f'<path d="M-24 78 q8 -10 16 0 t16 0 t16 0" fill="none" stroke="{ink}" stroke-width="8" stroke-linecap="round"/>')
    elif kind == "dizzy":
        for ex in (-38, 38):
            o.append(f'<circle cx="{ex}" cy="16" r="21" fill="#fff" stroke="{ink}" stroke-width="3"/>'
                     f'<path d="M{ex} 16 m-12 0 a12 12 0 1 1 12 12 a8 8 0 1 1 -8 -8 a4 4 0 1 1 4 4" fill="none" stroke="{ink}" stroke-width="4" '
                     f'transform="rotate({t*720:.0f} {ex} 16)"/>')
        o.append(f'<path d="M-30 74 q10 -10 20 0 t20 0 t20 0" fill="none" stroke="{ink}" stroke-width="8" stroke-linecap="round"/>')
    elif kind == "glare":    # buried: angry brows only (mouth hidden by books)
        o.append(f'<path d="M-78 -40 L -20 -6 M78 -40 L 20 -6" fill="none" stroke="{ink}" stroke-width="20" stroke-linecap="round"/>')
    elif kind == "horror":
        o.append(f'<path d="M-72 -46 Q -40 -74 -8 -52 M8 -52 Q 40 -74 72 -46" fill="none" stroke="{ink}" stroke-width="16" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


def nib_face(x, y, r, rot, sx, sy, kind, a=0.0):
    """Nibbo faces drawn on a blank bloop (expr 'blank')."""
    if not kind:
        return ""
    f = r / 48 * 1.05
    d = "#2a1a10"
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx*f:.3f} {sy*f:.3f})">']
    if kind == "ah":
        k = min(1.0, a)
        oy = -7 * k
        o.append(f'<g transform="translate(0 {oy:.1f})">')
        o.append(f'<path d="M-25 {-20-6*k:.1f} q8 {-6-4*k:.1f} 16 -2 M9 {-22-6*k:.1f} q8 {-4-4*k:.1f} 16 2" fill="none" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>')
        if k < 0.55:
            ry = 8 * (1 - 0.7 * k / 0.55)
            o.append(f'<ellipse cx="-14" cy="-4" rx="6" ry="{ry:.1f}" fill="{d}"/><ellipse cx="14" cy="-4" rx="6" ry="{ry:.1f}" fill="{d}"/>')
        else:
            o.append(f'<path d="M-21 -6 l8 3 l-8 4 M21 -6 l-8 3 l8 4" fill="none" stroke="{d}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>')
        o.append(f'<ellipse cx="0" cy="{15+2*k:.1f}" rx="{5+4*a:.1f}" ry="{3+9*a:.1f}" fill="#7a2a1a" stroke="{d}" stroke-width="3.5"/>')
        o.append('</g>')
    elif kind == "muff":
        o.append(f'<path d="M-24 -22 q8 -8 16 -4 M8 -26 q8 -4 16 4" fill="none" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<ellipse cx="-14" cy="-6" rx="8" ry="11" fill="{d}"/><ellipse cx="14" cy="-6" rx="8" ry="11" fill="{d}"/>'
                 '<circle cx="-11" cy="-10" r="3" fill="#fff"/><circle cx="17" cy="-10" r="3" fill="#fff"/>')
        for sgn in (-1, 1):
            o.append(f'<circle cx="{sgn*38}" cy="12" r="{14+4*a:.1f}" fill="#ffc22e" stroke="#3d2a12" stroke-width="3"/>'
                     f'<ellipse cx="{sgn*38}" cy="14" rx="7" ry="4" fill="#ff7fa0" opacity="0.6"/>')
    elif kind == "sneeze":
        o.append(f'<path d="M-22 -8 l9 4 l-9 5 M22 -8 l-9 4 l9 5" fill="none" stroke="{d}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
                 f'<ellipse cx="0" cy="18" rx="16" ry="17" fill="#7a2a1a" stroke="{d}" stroke-width="4"/>'
                 f'<ellipse cx="0" cy="26" rx="8" ry="5" fill="#ff7a90"/>')
    elif kind == "teary":
        o.append(f'<path d="M-21 -2 q7 -8 14 0 M7 -2 q7 -8 14 0" fill="none" stroke="{d}" stroke-width="5" stroke-linecap="round"/>'
                 f'<path d="M-10 16 q10 -6 20 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>'
                 f'<path d="M-16 4 v10 M16 4 v10" stroke="#8fd8ff" stroke-width="5" stroke-linecap="round"/>')
    elif kind == "smug":
        o.append(f'<ellipse cx="-14" cy="-3" rx="6" ry="7" fill="{d}"/><ellipse cx="14" cy="-3" rx="6" ry="7" fill="{d}"/>'
                 f'<path d="M-24 -9 h20 M4 -9 h20" stroke="#ffd23c" stroke-width="8"/>'
                 f'<path d="M-24 -6 h20 M4 -6 h20" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<path d="M-6 13 q8 6 16 -2" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    elif kind == "sheep":
        o.append(f'<ellipse cx="-14" cy="-4" rx="6" ry="8" fill="{d}"/><ellipse cx="14" cy="-4" rx="6" ry="8" fill="{d}"/>'
                 '<circle cx="-12" cy="-7" r="2.2" fill="#fff"/><circle cx="16" cy="-7" r="2.2" fill="#fff"/>'
                 f'<path d="M-8 14 q8 6 16 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>'
                 '<path d="M26 -26 q8 13 0 18 q-8 -5 0 -18z" fill="#bfefff" stroke="#3a6a8a" stroke-width="2.5"/>')
    o.append('</g>')
    return "".join(o)


# ---------------------------------------------------------------- states
def nib_mouth(n):
    return bodypt(n["x"], n["y"], 1, n["rot"], n["sx"], n["sy"], 0, NR * 0.32 - 7 * min(1, n["a"]) * NR / 48)


def nibbo_state(t):
    n = dict(x=N0[0], y=N0[1], rot=0.0, sx=1.0, sy=1.0, ex="blank", kind="sheep", a=0.0, hL=None, hR=None, tint=0.0,
             hLfinger=False)
    # resting hands on the old book
    n["hL"], n["hR"] = (720, TOP + 6), (860, TOP + 6)
    if t < T_SLAP:
        p = seg(t, T_AH1_0, T_AH1_1)
        if t < T_AH1_0:
            n["ex"], n["kind"] = "wow", None
            n["sx"], n["sy"] = squash(t, T_DUST1, 0.25, 0.08)
        else:
            n["kind"], n["a"] = "ah", 0.75 * eio(p)
            n["rot"] = -14 * eio(p) + 2 * math.sin(t * 9) * p
            n["y"] = N0[1] - 18 * eio(p)
            n["hL"], n["hR"] = (lerp(720, 690, p), TOP + 6), (lerp(860, 880, p), TOP + 6)
        return n
    if t < T_UNSLAP:
        n["kind"] = "muff"
        n["rot"] = -14 * (1 - seg(t, T_SLAP, T_SLAP + 0.15))
        n["y"] = N0[1] - 18 * (1 - seg(t, T_SLAP, T_SLAP + 0.15))
        if t >= T_MUFF1:
            k = t - T_MUFF1
            n["a"] = 0.6 * math.exp(-k * 4)
            n["sx"], n["sy"] = 1 + 0.16 * math.exp(-k * 6) * abs(math.cos(k * 30)), 1 - 0.1 * math.exp(-k * 6)
            n["y"] += -10 * math.exp(-k * 8)
        n["hL"], n["hR"] = (690, TOP + 6), (880, TOP + 6)
        return n
    if t < T_PAGE:
        n["kind"] = "sheep" if t < T_SHH0 + 0.2 else "sheep"
        if T_SHH0 + 0.2 <= t < T_SHH1:
            n["ex"], n["kind"] = "nervous", None
            n["rot"] = 4 * math.sin((t - T_SHH0) * 6)
        return n
    if t < T_CLAMP:
        q = seg(t, T_PAGE - 0.15, T_PAGE + 0.15)
        n["hR"] = (lerp(860, 790, eio(q)), TOP + 6 - 50 * math.sin(math.pi * q))
        n["kind"] = "sheep"
        if t >= T_DUST2:
            n["ex"], n["kind"] = "wow", None
        if t >= T_AH2_0:
            p = seg(t, T_AH2_0, T_AH2_1)
            n["ex"], n["kind"], n["a"] = "blank", "ah", 1.0 * eio(p)
            n["rot"] = -20 * eio(p) + 3 * math.sin(t * 10) * p
            n["y"] = N0[1] - 34 * eio(p)
            n["sx"], n["sy"] = 1 - 0.05 * p, 1 + 0.07 * p
            n["hL"], n["hR"] = (lerp(720, 680, p), TOP + 6), (lerp(790, 890, p), TOP + 6)
        return n
    if t < T_UNCLAMP:
        n["kind"] = "muff"
        n["rot"] = -20 * (1 - seg(t, T_CLAMP, T_CLAMP + 0.12))
        n["y"] = N0[1] - 34 * (1 - seg(t, T_CLAMP, T_CLAMP + 0.12))
        if t >= T_MUFF2:
            k = t - T_MUFF2
            n["a"] = 1.0 * math.exp(-k * 3)
            n["sx"], n["sy"] = 1 + 0.22 * math.exp(-k * 5) * abs(math.cos(k * 28)), 1 - 0.14 * math.exp(-k * 5)
        n["hL"], n["hR"] = (680, TOP + 6), (890, TOP + 6)
        return n
    if t < T_BUNNY1:
        n["ex"], n["kind"] = "blank", "teary"
        n["rot"] = 5 * math.sin((t - T_UNCLAMP) * 8) * (1 - seg(t, T_UNCLAMP, T_UNCLAMP + 0.8))
        return n
    if t < T_HOP1:
        n["sx"], n["sy"] = squash(t, T_BUNNY1, 0.2, 0.1)
        n["ex"], n["kind"] = "wow", None
        if t >= T_AH3_0:
            p = seg(t, T_AH3_0, T_AH3_1)
            n["ex"], n["kind"], n["a"] = "blank", "ah", 1.25 * eio(p)
            n["rot"] = -26 * eio(p) + 4 * math.sin(t * 12) * p
            n["y"] = N0[1] - 50 * eio(p)
            n["sx"], n["sy"] = 1 + 0.06 * p, 1 + 0.1 * p
            n["hL"], n["hR"] = (lerp(720, 660, p), TOP + 6 - 30 * p), (lerp(860, 900, p), TOP + 6 - 30 * p)
        return n
    if t < T_INF0:
        # sat on: squashed
        p = eout(seg(t, T_HOP1, T_HOP1 + 0.15))
        n["kind"] = "muff"
        n["rot"] = lerp(-26, 0, p)
        n["sx"], n["sy"] = lerp(1.06, 1.2, p), lerp(1.1, 0.8, p)
        n["y"] = lerp(N0[1] - 50, N0[1] + 22, p)
        n["a"] = 0.2
        if t >= T_MUFF3:
            k = t - T_MUFF3
            n["a"] = 0.2 + 1.0 * math.exp(-k * 3)
            n["sx"] = 1.2 + 0.2 * math.exp(-k * 5) * abs(math.cos(k * 26))
            n["sy"] = 0.8 + 0.12 * math.exp(-k * 5)
        if t >= T_COOL0 + 0.4:
            n["kind"] = "muff"
            n["a"] = 0.1
        n["hL"], n["hR"] = (650, TOP + 6), (910, TOP + 6)
        return n
    if t < T_BLAST:
        p = seg(t, T_INF0, T_INF1)
        e = eio(p)
        n["kind"] = "muff" if t < T_INF0 + 0.3 else "inflate"
        n["sx"], n["sy"] = lerp(1.2, 1.42, e), lerp(0.8, 1.5, e)
        n["y"] = N0[1] + 22 - 70 * e
        jit = 3 * p * math.sin(t * 50)
        n["x"] = N0[0] + jit
        n["a"] = 0.1 + 1.0 * e
        n["tint"] = 0.6 * e
        n["hL"], n["hR"] = (lerp(650, 610, e), TOP + 6), (lerp(910, 950, e), TOP + 6)
        if t >= T_BLAST - 0.2:
            n["kind"] = "ah"
            n["a"] = 1.3
        return n
    if t < T_AV0:
        k = t - T_BLAST
        p = seg(t, T_BLAST, T_BLAST + 0.45)
        n["kind"] = "sneeze" if k < 0.4 else "blankdaze"
        n["sx"], n["sy"] = lerp(1.42, 1.0, eout(p)) + 0.1 * math.sin(k * 40) * math.exp(-k * 4), lerp(1.5, 1.0, eout(p))
        n["y"] = lerp(N0[1] - 48, N0[1], eout(p)) + 30 * math.sin(math.pi * p)
        n["rot"] = 8 * math.sin(k * 25) * math.exp(-k * 3)
        n["tint"] = 0.6 * (1 - p)
        if k >= 0.4:
            n["ex"], n["kind"] = "dizzy", None
        if t >= T_DROP1 + 0.1:
            n["ex"], n["kind"] = "joy", None
        n["hL"], n["hR"] = (650, TOP + 6), (910, TOP + 6)
        return n
    # avalanche & after
    n["hL"], n["hR"] = None, None
    n["ex"], n["kind"] = "wow", None
    hit = T_AV0 + 0.45
    if t >= hit:
        n["sx"], n["sy"] = squash(t, hit, 0.25, 0.15)
        n["ex"], n["kind"] = "dizzy", None
    if t >= T_QUIET + 0.3:
        n["ex"], n["kind"] = "blank", "sheep"
    if t >= T_SHHN0:
        n["ex"], n["kind"] = "blank", "smug"
        q = seg(t, T_SHHN0, T_SHHN0 + 0.25)
        n["hR"] = (lerp(880, N0[0] + 8, eout(q)), lerp(TOP + 20, N0[1] + 52, eout(q)))
        n["hRfinger"] = True
        n["rot"] = 6 * math.sin((t - T_SHHN0) * 5)
    if t >= T_PF1:
        n["hR"] = None
        n["hRfinger"] = False
        n["ex"], n["kind"] = "wow", None
        n["rot"] = 0
    if t >= T_AH4_0:
        p = seg(t, T_AH4_0, T_DIVE1)
        n["ex"], n["kind"], n["a"] = "blank", "ah", 0.95 * eio(p)
        n["rot"] = -16 * eio(p)
        n["y"] = N0[1] - 22 * eio(p)
    return n


def grumpo_state(t):
    g = dict(x=G0[0], y=G0[1], rot=0.0, sx=1.0, sy=1.0, ex="grumpy", kind=None, look=(0.2, 0.9), red=0.0, glasses="up",
             hR=None, hL=None, book=None, hRfinger=False, on_table=False, buried=0.0, front=False)
    reading = ((G0[0] + 20, 1395, 0, "open"))
    if t < T_SLAP - 0.12:
        g["book"] = reading
        g["hR"], g["hL"] = (G0[0] + 110, 1400), (G0[0] - 70, 1408)
        if t >= T_GLANCE:
            g["look"] = (1, -0.2)
        if t >= T_GSHOCK:
            g["ex"] = "shock"
            g["sx"], g["sy"] = squash(t, T_GSHOCK, 0.25, 0.12)
        return g
    n = nibbo_state(t)
    if t < T_UNSLAP:
        g["book"] = (G0[0] - 10, 1400, -8, "open")
        g["hL"] = (G0[0] - 80, 1408)
        mx, my = nib_mouth(n)
        p = seg(t, T_SLAP - 0.12, T_SLAP)
        g["hR"] = (lerp(G0[0] + 110, mx, ein(p)), lerp(1400, my + 4, ein(p)))
        g["ex"] = "angry"
        g["look"] = (1, 0)
        g["rot"] = 10 * ein(p)
        g["x"] = G0[0] + 26 * ein(p)
        if t >= T_MUFF1:
            g["sx"], g["sy"] = squash(t, T_MUFF1, 0.25, 0.08)
            g["ex"] = "shock" if t < T_MUFF1 + 0.25 else "angry"
        return g
    if t < T_READ:
        g["book"] = (G0[0] - 10, 1400 + 50 * eio(seg(t, T_UNSLAP, T_SHH0)) * (1 - seg(t, T_SHH1 - 0.1, T_READ)), -8, "open")
        g["hL"] = (G0[0] - 80, 1408)
        g["ex"], g["kind"] = "x", "shh"
        g["look"] = (0.8, 0)
        q = seg(t, T_UNSLAP, T_SHH0)
        g["rot"] = lerp(10, -4, eio(q))
        g["x"] = lerp(G0[0] + 26, G0[0], eio(q))
        if t >= T_SHH0 - 0.1:
            p = eout(seg(t, T_SHH0 - 0.1, T_SHH0 + 0.15))
            mx, my = bodypt(g["x"], g["y"], GS, g["rot"], 1, 1, 6, 80)
            g["hR"] = (lerp(G0[0] + 130, mx, p), lerp(1300, my + 14, p))
            g["hRfinger"] = True
            g["rot"] = -4 + 3 * math.sin((t - T_SHH0) * 7)
        else:
            g["hR"] = (lerp(N0[0] - 60, G0[0] + 130, eio(q)), lerp(N0[1] + 30, 1300, eio(q)))
        return g
    if t < T_PANIC:
        p = seg(t, T_READ, T_READ + 0.25)
        g["book"] = reading
        g["hR"], g["hL"] = (lerp(G0[0] + 60, G0[0] + 110, p), 1400), (G0[0] - 70, 1408)
        g["ex"], g["look"] = "grumpy", (0.2, 0.9)
        if t >= T_DUST2 + 0.1:
            g["look"] = (1, -0.1)
            g["ex"] = "suspicious"
        return g
    if t < T_UNCLAMP:
        mx, my = nib_mouth(n)
        g["ex"] = "shock"
        g["look"] = (1, -0.3)
        g["sx"], g["sy"] = squash(t, T_PANIC, 0.25, 0.12)
        if t < T_CLAMP - 0.35:
            g["book"] = (G0[0] + 20, 1395 - 20 * seg(t, T_PANIC, T_PANIC + 0.3), 0, "open")
            g["hR"], g["hL"] = (G0[0] + 110, 1390), (G0[0] - 70, 1398)
            g["kind"] = None
        else:
            p = seg(t, T_CLAMP - 0.35, T_CLAMP)
            bx, by = lerp(G0[0] + 20, mx - 6, ein(p)), lerp(1375, my - 6, ein(p))
            g["book"] = (bx, by, lerp(0, -8, p), "open" if p < 0.6 else "closed")
            g["hR"], g["hL"] = (bx + 90, by + 6), (bx - 90, by + 10)
            g["ex"] = "angry"
            g["rot"] = 14 * ein(p)
            g["x"] = G0[0] + 60 * ein(p)
            if t >= T_MUFF2:
                k = t - T_MUFF2
                jx = 8 * math.exp(-k * 5) * math.sin(k * 40)
                g["book"] = (mx - 6 + jx, my - 6 - 10 * math.exp(-k * 6), -8, "closed")
                g["hR"], g["hL"] = (mx + 84 + jx, my), (mx - 96 + jx, my + 4)
                g["ex"] = "shock" if k < 0.3 else "smug"
        return g
    if t < T_HOP0:
        p = eio(seg(t, T_UNCLAMP, T_UNCLAMP + 0.35))
        g["book"] = (lerp(N0[0] - 60, G0[0] + 20, p), lerp(1330, 1395, p), lerp(-8, 0, p), "closed" if p < 0.5 else "open")
        g["hR"], g["hL"] = (lerp(N0[0] + 30, G0[0] + 110, p), lerp(1330, 1400, p)), (lerp(N0[0] - 150, G0[0] - 70, p), lerp(1336, 1408, p))
        g["x"] = lerp(G0[0] + 60, G0[0], p)
        g["rot"] = lerp(14, 0, p)
        g["ex"], g["kind"] = "x", "smugread"
        g["look"] = (0.2, 0.9)
        if t >= T_BUNNY1:
            g["ex"], g["kind"], g["look"] = "shock", None, (1, -0.4)
            g["sx"], g["sy"] = squash(t, T_BUNNY1, 0.25, 0.12)
        if t >= T_AH3_0 + 0.3:
            g["ex"] = "angry"
            g["red"] = 0.3 * seg(t, T_AH3_0 + 0.3, T_HOP0)
            g["sx"], g["sy"] = lerp(1, 1.12, seg(t, T_HOP0 - 0.25, T_HOP0)), lerp(1, 0.86, seg(t, T_HOP0 - 0.25, T_HOP0))
        return g
    # --- vault and sit on Nibbo
    sit = lambda nn: (nn["x"], nn["y"] - NR * nn["sy"] - 130 * GS * 0.86 + 12)
    if t < T_HOP1:
        p = seg(t, T_HOP0, T_HOP1)
        sx_, sy_ = sit(n)
        g["x"] = lerp(G0[0], sx_, eio(p))
        g["y"] = lerp(G0[1], sy_, p) - 200 * math.sin(math.pi * p)
        g["rot"] = 360 * eio(p) * 0 + 20 * math.sin(math.pi * p)
        g["ex"] = "angry"
        g["red"] = 0.3
        g["sx"], g["sy"] = 0.92, 1.1
        return g
    if t < T_INF0:
        sx_, sy_ = sit(n)
        g["x"], g["y"] = sx_, sy_
        g["sx"], g["sy"] = squash(t, T_HOP1, 0.3, 0.14)
        g["ex"] = "smug"
        g["red"] = 0.3 * (1 - seg(t, T_HOP1, T_HOP1 + 0.6))
        g["look"] = (0, 0.3)
        if t >= T_MUFF3:
            k = t - T_MUFF3
            bounce = 120 * math.sin(math.pi * seg(t, T_MUFF3, T_BOUNCE1))
            g["y"] = sy_ - bounce
            g["ex"] = "shock"
            g["sx"], g["sy"] = (0.9, 1.12) if t < T_BOUNCE1 else squash(t, T_BOUNCE1, 0.3, 0.16)
            g["glasses"] = "up" if t < T_BOUNCE1 else "down"
            if t >= T_BOUNCE1:
                g["ex"] = "grumpy"
        if t >= T_COOL0:
            g["ex"], g["kind"] = "x", "smugread"
            g["glasses"] = "down"
            p = eout(seg(t, T_COOL0 + 0.2, T_COOL0 + 0.6))
            g["book"] = (g["x"] + 10, g["y"] + 130 - 30 * p, 0, "open")
            g["hR"], g["hL"] = (g["x"] + 100, g["y"] + 136 - 30 * p), (g["x"] - 80, g["y"] + 142 - 30 * p)
            if p <= 0:
                g["book"] = None
                g["hR"], g["hL"] = None, None
        return g
    if t < T_BLAST:
        sx_, sy_ = sit(n)
        g["x"], g["y"] = sx_, sy_
        g["glasses"] = "down"
        g["ex"], g["kind"] = "x", "smugread"
        g["book"] = (g["x"] + 10, g["y"] + 100, 0, "open")
        g["hR"], g["hL"] = (g["x"] + 100, g["y"] + 106), (g["x"] - 80, g["y"] + 112)
        g["rot"] = 2 * math.sin(t * 40) * seg(t, T_INF0, T_INF1)
        if t >= T_WORRY:
            g["glasses"] = "up"
            g["ex"], g["kind"] = "x", "worried"
            g["look"] = (0, 1)
        if t >= T_SCARED:
            g["ex"], g["kind"] = "shock", None
            g["red"] = 0.0
            g["sx"], g["sy"] = squash(t, T_SCARED, 0.25, 0.12)
            q = seg(t, T_SCARED, T_SCARED + 0.2)
            g["book"] = (g["x"] + 10 + 60 * q, g["y"] + 40 - 40 * q, 30 * q, "open")
            g["hR"], g["hL"] = (g["x"] + 130, g["y"] - 40), (g["x"] - 130, g["y"] - 40)
        return g
    # --- blasted to the shelf
    g["front"] = True
    if t < T_SPLAT:
        p = seg(t, T_BLAST, T_SPLAT)
        x0, y0 = N0[0], 1030
        g["x"] = lerp(x0, SPL[0], eout(p))
        g["y"] = lerp(y0, SPL[1], eout(p)) - 60 * math.sin(math.pi * p)
        g["rot"] = -540 * eout(p)
        g["ex"] = "shock"
        g["look"] = (0, -1)
        g["sx"], g["sy"] = 1.1, 0.9
        return g
    if t < T_SLIDE0:
        g["x"], g["y"] = SPL
        k = t - T_SPLAT
        g["sx"], g["sy"] = 1.35 - 0.05 * math.exp(-k * 6) * math.sin(k * 30), 0.72
        g["ex"], g["kind"] = "x", "squished"
        return g
    if t < T_DROP1:
        p = seg(t, T_SLIDE0, T_SLIDE1)
        q = seg(t, T_SLIDE1, T_DROP1)
        g["x"] = lerp(SPL[0], SPL[0] + 40, p) + lerp(0, LAND[0] - SPL[0] - 40, eio(q))
        g["y"] = lerp(SPL[1], 1170, ein(p)) + lerp(0, LAND[1] - 1170, ein(q))
        g["sx"], g["sy"] = lerp(1.35, 0.95, p), lerp(0.72, 1.08, p)
        g["ex"], g["kind"] = "x", "squished"
        g["rot"] = lerp(0, -10, p)
        return g
    g["x"], g["y"] = LAND
    g["on_table"] = True
    g["sx"], g["sy"] = squash(t, T_DROP1, 0.3, 0.22)
    g["ex"], g["kind"] = "x", "dizzy"
    g["rot"] = wob(t, T_DROP1, 0.7, 8, 16)
    if t >= T_AV0:
        g["ex"], g["kind"] = "shock", None
        g["look"] = (-0.3, -1)
    hit = T_AV0 + 0.3
    if t >= hit:
        g["ex"], g["kind"] = "x", "dizzy"
        g["sx"], g["sy"] = squash(t, hit, 0.25, 0.12)
    if t >= T_QUIET:
        g["y"] = LAND[1] - 42 * eback(seg(t, T_QUIET, T_QUIET + 0.35))
    if t >= T_QUIET + 0.2:
        g["ex"], g["kind"] = "x", "glare"
        g["look"] = (0.9, 0)
        g["red"] = 0.35 * seg(t, T_SHHN0, T_SHHN0 + 0.6)
    if t >= T_HORROR:
        g["ex"], g["kind"] = "shock", "horror"
        g["red"] = 0.0
        g["look"] = (1, 0)
        g["sx"], g["sy"] = squash(t, T_HORROR, 0.3, 0.15)
    if t >= T_DIVE0:
        p = seg(t, T_DIVE0, T_DIVE1)
        g["x"] = lerp(LAND[0], N0[0] - 175, eio(p))
        g["y"] = LAND[1] - 42 - 110 * math.sin(math.pi * min(1, p * 1.1)) + 10 * p
        g["rot"] = 18 * p
        g["ex"], g["kind"] = "angry", None
        mx, my = nib_mouth(n)
        g["hR"] = (lerp(g["x"] + 120, mx - 4, eio(p)), lerp(g["y"] + 20, my + 2, eio(p)))

    return g


# ---------------------------------------------------------------- camera
CK = [(0.0, (610, 1215, 1.74)), (T_GSHOCK, (610, 1215, 1.74)), (T_SLAP + 0.1, (630, 1225, 1.84)), (T_UNSLAP, (620, 1220, 1.8)),
      (T_SHH0 + 0.2, (540, 1215, 1.9)), (T_READ, (610, 1215, 1.76)), (T_DUST2, (680, 1225, 1.84)), (T_AH2_1, (670, 1205, 1.86)),
      (T_MUFF2 + 0.3, (620, 1215, 1.76)), (T_BUNNY0, (660, 1200, 1.72)), (T_AH3_1 - 0.3, (650, 1180, 1.7)),
      (T_HOP1, (680, 1130, 1.6)), (T_COOL0 + 0.6, (720, 1120, 1.7)), (T_INF0, (720, 1120, 1.68)),
      (T_INF1, (700, 1060, 1.42)), (T_BLAST + 0.05, (620, 1080, 1.3)), (T_SPLAT + 0.1, (430, 1110, 1.42)), (T_SLIDE0, (420, 1130, 1.5)),
      (T_DROP1 + 0.2, (500, 1170, 1.5)), (T_WOB + 0.3, (510, 1150, 1.4)), (T_AV1, (580, 1170, 1.45)),
      (T_QUIET + 0.4, (600, 1200, 1.62)), (T_SHHN1, (610, 1210, 1.7)), (T_HORROR, (620, 1215, 1.74)), (T_DIVE1, (640, 1220, 1.82)),
      (DUR, (640, 1220, 1.86))]
SHAKES = [(T_MUFF1, 5, 0.2), (T_MUFF2, 8, 0.25), (T_MUFF3, 12, 0.3), (T_BLAST, 26, 0.6), (T_SPLAT, 14, 0.3),
          (T_DROP1, 10, 0.25), (T_AV0 + 0.3, 6, 1.2), (T_DIVE1, 10, 0.3)]


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
    if T_INF0 <= t < T_BLAST:
        amp = max(amp, 7 * seg(t, T_INF0, T_INF1))
    return cx + amp * math.sin(t * 93), cy + amp * math.cos(t * 79), z


# ---------------------------------------------------------------- frame
def sneeze_value(t):
    if t < T_MUFF1 + 0.05:
        return "25%", 0, T_CNT
    if t < T_MUFF2 + 0.05:
        return "60%", 1, T_MUFF1 + 0.05
    if t < T_MUFF3 + 0.05:
        return "150%", 2, T_MUFF2 + 0.05
    if t < T_INF0 + 0.4:
        return "400%", 3, T_MUFF3 + 0.05
    p = seg(t, T_INF0 + 0.4, T_INF1)
    v = int(lerp(400, 999, eio(p)))
    return f"{v}%", 3, (T_INF1 if t >= T_INF1 else None)


def frame(t):
    ctx = Ctx()
    n = nibbo_state(t)
    g = grumpo_state(t)
    L = [room(t)]
    # hero shelves + books on them
    front_books = []
    L.append(shelf_frame(*SHELF_L))
    for i, b in enumerate(BOOKS_L):
        svg, lay = book_state(b, i, AV_L, t, blown=i in BLOWN)
        (L if lay == "shelf" else front_books).append(svg)
    L.append(shelf_frame(*SHELF_R))
    for i, b in enumerate(BOOKS_R):
        svg, lay = book_state(b, i, AV_R, t)
        (L if lay == "shelf" else front_books).append(svg)
    # dust bunny resting on top of right shelf until it falls
    if t < T_BUNNY0:
        L.append(dust_bunny(820, SH_TOP - 40, 0, 1.0))
    L.append(poster(600, 1175, seg(t, T_SHH0 + 0.3, T_SHH0 + 0.9), wob(t, T_BLAST, 1.0, 14, 14) + (0 if t < T_BLAST else 6)))
    L.append(chair(G0[0], 1150))
    L.append(chair(N0[0], 1150))

    # characters behind the table
    def draw_g():
        out = [grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], g["glasses"], g["look"], g["rot"], g["sx"], g["sy"], drink=False, t=t),
               grumpo_extra(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], g["kind"], t, g["red"])]
        return "".join(out)

    def draw_n():
        out = [nibbo(ctx, n["x"], n["y"], NR, n["ex"] if n["kind"] is None else "blank", rot=n["rot"], sx=n["sx"], sy=n["sy"])]
        if n["tint"] > 0:
            out.append(f'<g transform="translate({n["x"]:.1f} {n["y"]:.1f}) rotate({n["rot"]:.1f}) scale({n["sx"]:.3f} {n["sy"]:.3f})">'
                       f'<circle r="{NR-4}" fill="#ff4a2a" opacity="{n["tint"]*0.55:.2f}"/></g>')
        kind = n["kind"]
        if kind == "inflate":
            kind = "muff"
        out.append(nib_face(n["x"], n["y"], NR, n["rot"], n["sx"], n["sy"], kind, n["a"]))
        return "".join(out)

    if not g["front"]:
        L.append(draw_n())
        L.append(draw_g())
    else:
        L.append(draw_n())
        if not g["on_table"]:
            L.append(draw_g())

    # table, lamp, props
    L.append(table())
    spin = 0.0
    if t >= T_BLAST:
        spin = 720 * eout(seg(t, T_BLAST, T_BLAST + 1.2))
    L.append(lamp(600, t, spin))
    fl = 0.0
    if T_MUFF2 <= t < T_MUFF2 + 0.8:
        fl = 1 - seg(t, T_MUFF2, T_MUFF2 + 0.8)
    if t >= T_BLAST:
        fl = 1 - seg(t, T_BLAST, T_BLAST + 1.4)
    L.append(old_book(790, TOP + 26, 1.0, fl, t))
    if g["on_table"]:
        L.append(draw_g())

    # pages blown by the blast
    if T_BLAST <= t < T_BLAST + 1.6:
        q = seg(t, T_BLAST, T_BLAST + 1.6)
        for k in range(9):
            a = math.radians(-170 + k * 22)
            d = 120 + 900 * eout(q) * (0.6 + 0.1 * (k % 4))
            L.append(page(800 + d * math.cos(a), 1250 + d * math.sin(a) * 0.7 + 400 * q * q, k * 40 + q * 600 * (1 if k % 2 else -1), 1.0 + q, 1 - q))

    # landed / falling books (front)
    # pile base mound behind the books, growing
    pf = seg(t, T_AV0 + 0.3, T_AV1 + 0.3)
    if pf > 0:
        h = 78 * eio(pf)
        L.append(f'<path d="M{LAND[0]-250} {TOP+24} Q {LAND[0]} {TOP+24-2.2*h:.0f} {LAND[0]+250} {TOP+24}Z" fill="#6a3a22" stroke="{OL}" stroke-width="5"/>')
        h2 = 26 * eio(seg(t, T_AV0 + 0.6, T_AV1 + 0.4))
        if h2 > 0:
            L.append(f'<path d="M{N0[0]-170} {TOP+24} Q {N0[0]+10} {TOP+24-2.2*h2:.0f} {N0[0]+190} {TOP+24}Z" fill="#6a3a22" stroke="{OL}" stroke-width="5"/>')
    L.extend(front_books)

    # ---- hands/arms Grumpo
    if g["book"]:
        bx, by, br, mode = g["book"]
        L.append(big_book(bx, by, br, mode, 0.95))
    for side, key in ((1, "hR"), (-1, "hL")):
        if g[key]:
            sx_, sy_ = bodypt(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], side * 112, 30)
            L.append(arm(sx_, sy_, g[key][0], g[key][1], INK, 14, 24))
    for key in ("hR", "hL"):
        if g[key]:
            col = mix_hex(GFILL, "#ff6a52", g["red"])
            if key == "hR" and g["hRfinger"]:
                L.append(finger_hand(g[key][0], g[key][1], col, OL, 18))
            else:
                L.append(hand(*g[key], col, OL, 19))
    # ---- hands Nibbo
    for side, key in ((-1, "hL"), (1, "hR")):
        if n[key]:
            sx_, sy_ = bodypt(n["x"], n["y"], 1, n["rot"], n["sx"], n["sy"], side * 96, 26)
            L.append(arm(sx_, sy_, n[key][0], n[key][1], NS, 11, 18))
    for key in ("hL", "hR"):
        if n[key]:
            if key == "hR" and n.get("hRfinger"):
                L.append(finger_hand(n[key][0], n[key][1], NB, NS, 19))
            else:
                L.append(hand(*n[key], NB, NS, 15))

    # ---- effects
    L.append(dust_puff(790, TOP - 10, seg(t, T_DUST1, T_DUST1 + 0.7)))
    L.append(dust_stream(790, TOP - 30, N0[0] + 5, N0[1] + 10, t, T_DUST1 + 0.1, T_AH1_0 + 0.5))
    L.append(symbol(G0[0] + 40, G0[1] - 160, "!", seg(t, T_GSHOCK, T_GSHOCK + 0.5)))
    if t >= T_SLAP - 0.02:
        L.append(impact(*nib_mouth(n), seg(t, T_SLAP, T_SLAP + 0.2), "#ffffff"))
    if T_MUFF1 <= t < T_MUFF1 + 0.5:
        q = seg(t, T_MUFF1, T_MUFF1 + 0.5)
        mx, my = nib_mouth(n)
        for k in range(4):
            a = math.radians(-120 + k * 80)
            L.append(f'<circle cx="{mx+90*q*math.cos(a):.0f}" cy="{my+70*q*math.sin(a):.0f}" r="{10+16*q:.0f}" fill="#ffffff" stroke="#c9c2b0" stroke-width="3" opacity="{1-q:.2f}"/>')
    L.append(dust_puff(790, TOP - 10, seg(t, T_DUST2, T_DUST2 + 0.6), 1.2))
    L.append(dust_stream(790, TOP - 30, N0[0], N0[1] - 10, t, T_DUST2 + 0.05, T_AH2_0 + 0.5))
    L.append(symbol(G0[0] + 40, G0[1] - 160, "!", seg(t, T_PANIC, T_PANIC + 0.5)))
    if T_MUFF2 <= t < T_MUFF2 + 0.9:
        q = seg(t, T_MUFF2, T_MUFF2 + 0.9)
        mx, my = nib_mouth(n)
        for k in range(5):
            a = math.radians(-150 + k * 30)
            d = 60 + 260 * eout(q)
            L.append(page(mx + d * math.cos(a), my - 40 + d * math.sin(a) + 300 * q * q, k * 50 + q * 400, 0.7, 1 - q))
        L.append(impact(mx, my, seg(t, T_MUFF2, T_MUFF2 + 0.25)))
    # dust bunny drop
    if T_BUNNY0 <= t < T_BUNNY1 + 0.6:
        p = seg(t, T_BUNNY0, T_BUNNY1)
        if t < T_BUNNY1:
            L.append(dust_bunny(lerp(820, N0[0] + 10, p), lerp(SH_TOP - 40, N0[1] - NR - 10, ein(p)), 200 * p, 1.0))
        else:
            q = seg(t, T_BUNNY1, T_BUNNY1 + 0.6)
            L.append(dust_puff(N0[0], N0[1] - NR, q, 1.1))
    if T_AH3_0 <= t < T_HOP1:
        L.append(dust_bunny(n["x"] + 10, n["y"] - NR * n["sy"] - 8, n["rot"], 0.9))
    L.append(symbol(G0[0] + 40, G0[1] - 170, "!", seg(t, T_BUNNY1, T_BUNNY1 + 0.5)))
    if T_HOP0 <= t < T_HOP1:
        L.append(speed_lines(g["x"] - 80, g["y"] + 40, 30, 0.8))
    L.append(impact(n["x"], n["y"] - NR * n["sy"], seg(t, T_HOP1, T_HOP1 + 0.25), "#ffffff"))
    if T_MUFF3 <= t < T_MUFF3 + 0.6:
        q = seg(t, T_MUFF3, T_MUFF3 + 0.6)
        for k in range(6):
            a = math.radians(180 + k * 36 - 20)
            L.append(f'<circle cx="{n["x"]+150*q*math.cos(a)*1.4:.0f}" cy="{n["y"]+40+60*q*math.sin(a):.0f}" r="{14+20*q:.0f}" fill="#ffffff" stroke="#c9c2b0" stroke-width="3" opacity="{1-q:.2f}"/>')
        L.append(impact(n["x"], n["y"] - 60, seg(t, T_MUFF3, T_MUFF3 + 0.25)))
    if T_BOUNCE1 <= t < T_BOUNCE1 + 0.8:
        L.append(star_twinkle(g["x"] + 60, g["y"] - 10, seg(t, T_BOUNCE1, T_BOUNCE1 + 0.6)))
    if T_INF0 + 0.3 <= t < T_BLAST:
        p = seg(t, T_INF0, T_INF1)
        for k in range(3):
            q = ((t - T_INF0) * 2 + k / 3) % 1
            L.append(f'<path d="M{n["x"]-NR*n["sx"]-20-20*q:.0f} {n["y"]-30+k*30:.0f} h{-40*p:.0f}" stroke="#ffffff" stroke-width="8" stroke-linecap="round" opacity="{(1-q)*p:.2f}"/>'
                     f'<path d="M{n["x"]+NR*n["sx"]+20+20*q:.0f} {n["y"]-30+k*30:.0f} h{40*p:.0f}" stroke="#ffffff" stroke-width="8" stroke-linecap="round" opacity="{(1-q)*p:.2f}"/>')
    L.append(symbol(g["x"] + 40, g["y"] - 170, "!", seg(t, T_SCARED, T_SCARED + 0.6)))
    # the blast
    if T_BLAST <= t < T_BLAST + 0.9:
        q = seg(t, T_BLAST, T_BLAST + 0.9)
        L.append(wind_lines(n["x"], n["y"] - 60, q, -125))
        L.append(wind_lines(n["x"], n["y"] - 60, q, -70))
        L.append(impact(n["x"], n["y"] - 80, seg(t, T_BLAST, T_BLAST + 0.35)))
    if T_BLAST <= t < T_SPLAT:
        L.append(speed_lines(g["x"] + 80, g["y"] + 40, 200, 0.9))
    L.append(impact(SPL[0], SPL[1], seg(t, T_SPLAT, T_SPLAT + 0.3)))
    L.append(impact(LAND[0], LAND[1] + 90, seg(t, T_DROP1, T_DROP1 + 0.25), "#ffffff"))
    # avalanche dust
    if T_AV0 + 0.4 <= t < T_SHHN0 + 0.6:
        q = seg(t, T_AV0 + 0.4, T_SHHN0 + 0.6)
        for k in range(7):
            x = LAND[0] - 260 + k * 110 + 20 * math.sin(t * 2 + k)
            y = TOP - 40 - 260 * q - 30 * (k % 3)
            L.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{40+50*q:.0f}" fill="#e6dcc6" opacity="{0.75*(1-q):.2f}"/>')
    # loose page floating onto Nibbo
    if T_PF0 <= t < T_AH4_0 + 0.2:
        p = seg(t, T_PF0, T_PF1)
        x = lerp(N0[0] - 120, N0[0] + 6, p) + 40 * math.sin(p * 9)
        y = lerp(980, N0[1] - 30, eio(p))
        L.append(page(x, y, 30 * math.sin(p * 9), 0.8, 1 - seg(t, T_AH4_0, T_AH4_0 + 0.2)))
    if t >= T_AH4_0:
        L.append(dust_stream(N0[0] + 10, N0[1] - 30, N0[0], N0[1] + 4, t, T_AH4_0 - 0.05, T_AH4_0 + 0.5))
    L.append(symbol(g["x"] + 30, g["y"] - 170, "!", seg(t, T_HORROR, T_HORROR + 0.6)))
    if T_DIVE0 <= t < T_DIVE1:
        L.append(speed_lines(g["x"] - 100, g["y"], 0, 0.9))
    if t >= T_DIVE1:
        L.append(impact(*nib_mouth(n), seg(t, T_DIVE1, T_DIVE1 + 0.3)))

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    flash = ""
    if T_BLAST <= t < T_BLAST + 0.3:
        flash = f'<rect width="{W}" height="{H}" fill="#ffffff" opacity="{0.75*(1-seg(t, T_BLAST, T_BLAST+0.3)):.2f}"/>'
    if t >= T_DIVE1:
        flash = f'<rect width="{W}" height="{H}" fill="#ffffff" opacity="{0.5*(1-seg(t, T_DIVE1, T_DIVE1+0.25)):.2f}"/>'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{defs()}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g>'
           f'<rect width="{W}" height="{H}" fill="url(#vig)"/>{flash}</svg>')
    layers = [hook_title(t + 0.12, "Shhh! Don't sneeze", "IN THE LIBRARY")]
    if T_CNT <= t < T_BLAST + 0.45:
        v, st, bt = sneeze_value(t)
        if t >= T_BLAST:
            v, st, bt = "999%", 3, T_BLAST
        layers.append(counter(t, v, "SNEEZE", st, 3, bump_t=bt))
    if t >= T_AH4_0 + 0.1:
        layers.append(counter(t, "25%", "SNEEZE", 0, 3, bump_t=T_AH4_0 + 0.1))
    return overlay(svg, *layers)


def build_sfx():
    sfx(0.0, "poof", 0.7, 1.0)
    sfx(0.02, "book_thud", 0.5, 1.2)
    sfx(T_DUST1, "poof", 0.8, 0.8)
    sfx(T_CNT, "blip", 0.5, 1.2)
    sfx(T_AH1_0, "sneeze_build", 0.9, 1.0)
    sfx(T_GSHOCK, "gasp", 0.6, 0.9)
    sfx(T_SLAP - 0.1, "whoosh", 0.7, 1.4)
    sfx(T_SLAP, "squish", 0.9, 1.1)
    sfx(T_SLAP, "tap", 0.6, 0.7)
    sfx(T_MUFF1, "mff", 1.0, 1.1)
    sfx(T_MUFF1 + 0.05, "blip", 0.5, 1.35)
    sfx(T_MUFF1 + 0.1, "balloon", 0.3, 1.4)
    sfx(T_SHH0, "steam", 0.5, 1.6)
    sfx(T_SHH0 + 0.35, "shine", 0.4, 1.4)
    sfx(T_SHH0 + 0.2, "tick", 0.5, 1.0)
    sfx(T_READ, "rustle", 0.3, 1.3)
    sfx(T_PAGE, "flap", 0.6, 1.3)
    sfx(T_DUST2, "poof", 0.9, 0.75)
    sfx(T_AH2_0, "sneeze_build", 1.0, 0.95)
    sfx(T_PANIC, "gasp", 0.7, 0.95)
    sfx(T_CLAMP - 0.3, "whoosh", 0.7, 1.1)
    sfx(T_CLAMP, "book_thud", 1.0, 0.8)
    sfx(T_CLAMP, "thunk", 0.6, 1.0)
    sfx(T_MUFF2, "mff", 1.0, 0.9)
    sfx(T_MUFF2 + 0.05, "flutter", 0.9, 1.0)
    sfx(T_MUFF2 + 0.05, "blip", 0.5, 1.5)
    sfx(T_UNCLAMP, "deflate", 0.4, 1.4)
    sfx(T_UNCLAMP + 0.3, "tick", 0.5, 1.0)
    sfx(T_BUNNY0, "slide_down", 0.4, 1.6)
    sfx(T_BUNNY1, "poof", 0.9, 0.9)
    sfx(T_BUNNY1 + 0.05, "gasp", 0.6, 0.85)
    sfx(T_AH3_0, "sneeze_build", 1.0, 0.88)
    sfx(T_HOP0 - 0.1, "grumble", 0.6, 1.0)
    sfx(T_HOP0, "boing", 0.7, 1.0)
    sfx(T_HOP0 + 0.05, "whoosh", 0.7, 0.9)
    sfx(T_HOP1, "squish", 1.0, 0.75)
    sfx(T_HOP1, "thud", 0.7, 0.9)
    sfx(T_MUFF3, "mff", 1.0, 0.7)
    sfx(T_MUFF3 + 0.02, "boing", 0.8, 0.8)
    sfx(T_MUFF3 + 0.05, "blip", 0.5, 1.7)
    sfx(T_BOUNCE1, "thud", 0.6, 1.1)
    sfx(T_BOUNCE1 + 0.05, "cool", 0.6, 1.0)
    sfx(T_COOL0 + 0.3, "rustle", 0.4, 1.2)
    sfx(T_COOL0 + 0.7, "tick", 0.5, 1.0)
    sfx(T_INF0, "inhale", 0.8, 0.7)
    sfx(T_INF0 + 0.3, "balloon", 0.6, 0.8)
    sfx(T_INF0 + 0.8, "inhale", 0.8, 0.6)
    sfx(T_INF0 + 1.0, "strain", 0.6, 1.0)
    sfx(T_WORRY, "gulp", 0.6, 1.0)
    sfx(T_INF0 + 1.4, "balloon", 0.6, 0.65)
    sfx(T_INF0 + 1.6, "rise", 0.7, 0.8)
    sfx(T_SCARED, "gasp", 0.8, 0.9)
    sfx(T_INF1 - 0.4, "inhale", 0.9, 0.5)
    sfx(T_BLAST - 0.12, "big_achoo", 1.0, 1.0)
    sfx(T_BLAST, "rumble", 0.8, 1.0)
    sfx(T_BLAST + 0.05, "flutter", 1.0, 0.9)
    sfx(T_BLAST + 0.05, "whoosh", 0.9, 0.7)
    sfx(T_BLAST + 0.1, "zoom", 0.6, 1.0)
    sfx(T_SPLAT, "splat", 1.0, 0.8)
    sfx(T_SPLAT, "thud", 0.9, 0.8)
    sfx(T_SPLAT + 0.4, "creak", 0.5, 1.0)
    sfx(T_SLIDE0, "squeak_slide", 0.8, 0.9)
    sfx(T_DROP1, "thud", 1.0, 0.9)
    sfx(T_WOB, "creak", 0.8, 0.8)
    sfx(T_WOB + 0.2, "wobble", 0.5, 0.9)
    for i, pl in list(AV_L.items())[::3] + list(AV_R.items())[::3]:
        sfx(pl["ts"] + pl["dur"], "book_thud", 0.55, 0.85 + (i % 5) * 0.08)
    sfx(T_AV0 + 0.3, "clatter", 0.9, 0.8)
    sfx(T_AV0 + 0.8, "clatter", 0.8, 0.7)
    sfx(T_AV0 + 0.3, "bonk", 0.6, 1.0)
    sfx(T_AV0 + 0.45, "bonk", 0.5, 1.4)
    sfx(T_QUIET + 0.1, "tick", 0.6, 1.0)
    sfx(T_QUIET + 1.1, "tick", 0.6, 1.0)
    sfx(T_SHHN0, "steam", 0.6, 1.9)
    sfx(T_SHHN0 + 0.3, "grumble", 0.5, 0.9)
    sfx(T_PF0, "flap", 0.4, 1.5)
    sfx(T_PF1 - 0.1, "flap", 0.4, 1.7)
    sfx(T_AH4_0 + 0.1, "blip", 0.5, 1.2)
    sfx(T_AH4_0 + 0.05, "sneeze_build", 0.9, 1.05)
    sfx(T_HORROR, "gasp", 0.9, 0.8)
    sfx(T_DIVE0, "whoosh", 0.9, 1.0)
    sfx(T_DIVE1, "squish", 1.0, 1.0)
    sfx(T_DIVE1, "thud", 0.8, 1.0)
