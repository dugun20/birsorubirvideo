"""Grumpo & Nibbo — Episode 18: The Red Sock (laundromat, 60 fps).

Structure I (misunderstanding — the viewer knows, Grumpo doesn't) + escalating SPIN counter (400 -> 1,200 -> 5,000 -> 99,999).
Only ONE washing machine works. Grumpo (huge pile of WHITE laundry on his head) hip-bumps Nibbo away from it;
Nibbo's basket flips and his RED SOCK lands on top of Grumpo's white pile (spotlight — Grumpo never notices).
Grumpo stuffs everything in. Nibbo sees the sock through the porthole and tries to warn him 3 times:
  1. jumping + pointing -> Grumpo wags his finger, turns the dial: SPIN 400
  2. a card with icons (sock + shirt = pink shirt) -> snatched, crumpled, tossed: SPIN 1,200
  3. tugging his arm toward the porthole -> flicked away, Nibbo spins off: SPIN 5,000
Grumpo leans on the machine, smug. The dial spins by itself: SPIN 99,999 -> the machine bucks like a rodeo bull,
Grumpo rides it, flung to the floor at the 'ding'. He opens the door: EVERYTHING IS PINK.
Twist ending: the last thing out is Nibbo's sock — now perfectly WHITE (all its red went into Grumpo's laundry).
Nibbo happily takes it and leaves; pink briefs land on Grumpo's head.
"""
import math, sys, os, random
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
PINK = "#ff8fbf"

FLOOR = 1700
WX = 540                       # working washer centre
W_TOP = FLOOR - 380
PORT = (WX, 1532)
PR = 100
DIAL = (WX + 78, W_TOP + 38)
GX, GY = 300.0, FLOOR - GR
NX, NY = 790.0, FLOOR - NR
POSTER = (690, 1120)

# ---- times
T_ARR = 0.55
T_BUMP = 0.6
T_SOCK1 = 1.45                 # sock lands on the white pile
T_SPOT0, T_SPOT1 = 1.45, 2.1
T_DOOR_O = 2.05
T_ARM = [2.25, 2.6, 2.95]      # three armfuls in
T_DOOR_C = 3.3
T_SEEK = 2.9
T_SEE = 3.5
T_W1_0, T_W1_1 = 3.75, 4.45
T_WAG0 = 3.95
T_D1 = 4.6
T_W2_0 = 4.95
T_SNATCH = 5.45
T_CRUMPLE = 5.6
T_TOSS0, T_TOSS1 = 5.8, 6.2
T_D2 = 6.15
T_W3_0, T_W3_1 = 6.4, 7.05
T_FLICK = 7.1
T_SLIDE1 = 7.55
T_D3 = 7.75
T_LEAN = 8.0
T_COVER = 8.2
T_D4 = 8.75
T_LAUNCH1 = 9.1
T_STOP = 10.9
T_THROWN1 = 11.25
T_UP = 11.65
T_OPEN = 11.85
T_REACH0, T_REACH1 = 12.0, 12.35
T_PINK = 12.4
T_POUR0, T_POUR1 = 12.55, 13.1
T_ANGRY = 13.25
T_POINT = 13.55
T_SOCK2_0, T_SOCK2_1 = 14.15, 14.75
T_GASP = 14.85
T_BRIEFS0, T_BRIEFS1 = 15.15, 15.6
T_LEAVE0, T_LEAVE1 = 15.6, 16.7
DUR = 17.4

D_TIMES = [T_D1, T_D2, T_D3, T_D4]
D_VALS = [400, 1200, 5000, 99999]

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


def level(t):
    return sum(1 for d in D_TIMES if t >= d)


def pinkness(t):
    return seg(t, T_D1 + 0.3, T_D4 + 0.8) ** 0.8


# drum angle: piecewise constant speeds (rad/s)
SPEEDS = [0, 2.5, 5, 10, 34]


def drum_ang(t):
    if t >= T_STOP:
        t = T_STOP
    a = 0.0
    edges = [0.0] + [d + 0.1 for d in D_TIMES] + [1e9]
    for i in range(len(SPEEDS)):
        lo, hi = edges[i], edges[i + 1]
        if t > lo:
            a += SPEEDS[i] * (min(t, hi) - lo)
    return a


def machine_motion(t):
    """(dx, dy, rot) of the working washer."""
    lv = level(t) if t < T_STOP else 0
    amp = [0, 1.5, 4, 9, 0][lv]
    dx = amp * math.sin(t * 61)
    dy = -abs(amp * 0.6 * math.sin(t * 47))
    rot = amp * 0.12 * math.sin(t * 53)
    if T_D3 + 0.3 <= t < T_D4:
        dy -= 8 * abs(math.sin(t * 9))
    if T_D4 <= t < T_STOP:
        k = t - T_D4
        hop = abs(math.sin(k * 7.5))
        dy = -55 * hop * min(1, k * 4)
        rot = 6 * math.sin(k * 7.5 + 0.7)
        dx = 14 * math.sin(k * 3.1)
    if T_STOP <= t < T_STOP + 0.4:
        k = t - T_STOP
        dy = 6 * math.exp(-k * 10) * math.sin(k * 50)
    return dx, dy, rot


# ---------------------------------------------------------------- props
def defs():
    return ('<linearGradient id="wallL" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a9dcd6"/><stop offset="1" stop-color="#cdeee8"/></linearGradient>'
            '<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#cfefff" stop-opacity="0.55"/><stop offset="1" stop-color="#7ab8e0" stop-opacity="0.35"/></linearGradient>'
            '<radialGradient id="spot" cx="0.5" cy="0.5" r="0.5"><stop offset="0.45" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#0a0614" stop-opacity="0.65"/></radialGradient>'
            '<radialGradient id="vig" cx="0.5" cy="0.55" r="0.8"><stop offset="0.62" stop-color="#1a2030" stop-opacity="0"/><stop offset="1" stop-color="#1a2030" stop-opacity="0.32"/></radialGradient>')


def shirt(x, y, col, rot=0.0, s=1.0):
    sh = mix_hex(col, "#000000", 0.12)
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            f'<path d="M-22 -30 L-46 -16 L-36 2 L-26 -4 L-26 32 L26 32 L26 -4 L36 2 L46 -16 L22 -30 Q 0 -18 -22 -30Z" fill="{col}" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M-26 20 L26 20 L26 32 L-26 32Z" fill="{sh}"/>'
            f'<path d="M-12 -27 Q 0 -16 12 -27" fill="none" stroke="{OL}" stroke-width="4"/></g>')


def towel(x, y, col, rot=0.0, s=1.0):
    sh = mix_hex(col, "#000000", 0.12)
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            f'<rect x="-44" y="-18" width="88" height="36" rx="10" fill="{col}" stroke="{OL}" stroke-width="5"/>'
            f'<path d="M-40 8 h80" stroke="{sh}" stroke-width="7"/><path d="M-30 -18 v36 M30 -18 v36" stroke="{sh}" stroke-width="4"/></g>')


def sock(x, y, col, rot=0.0, s=1.0, sparkle=0.0):
    sh = mix_hex(col, "#000000", 0.15)
    o = (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
         f'<path d="M-12 -36 L12 -36 L12 8 Q 12 24 30 24 Q 44 26 42 36 Q 40 44 26 42 L-4 40 Q -14 38 -12 24Z" fill="{col}" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
         f'<path d="M-12 -28 h24 M-12 -20 h24" stroke="{sh}" stroke-width="4"/>'
         f'<path d="M26 26 q10 2 12 10" fill="none" stroke="{sh}" stroke-width="4" stroke-linecap="round"/></g>')
    return o


def briefs(x, y, col, rot=0.0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            f'<path d="M-40 -16 L40 -16 L36 4 Q 14 6 8 24 L-8 24 Q -14 6 -36 4Z" fill="{col}" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M-40 -16 L40 -16 L40 -8 L-40 -8Z" fill="{mix_hex(col, "#ffffff", 0.4)}" stroke="{OL}" stroke-width="4"/></g>')


def basket(x, y, col, s=1.0, rot=0.0):
    sh = mix_hex(col, "#000000", 0.2)
    holes = "".join(f'<rect x="{-48+k*20}" y="-8" width="10" height="20" rx="4" fill="{sh}"/>' for k in range(5))
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            f'<path d="M-62 -26 L62 -26 L52 34 L-52 34Z" fill="{col}" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            f'<rect x="-68" y="-34" width="136" height="16" rx="7" fill="{mix_hex(col, "#ffffff", 0.25)}" stroke="{OL}" stroke-width="5"/>'
            f'{holes}</g>')


def x_sign(x, y, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.2f}) rotate(-6)">'
            f'<rect x="-46" y="-46" width="92" height="92" rx="8" fill="#fffbe8" stroke="{OL}" stroke-width="5"/>'
            f'<rect x="-30" y="-54" width="60" height="16" fill="#f0e2a0" opacity="0.85"/>'
            f'<circle r="30" fill="#e8402e" stroke="{OL}" stroke-width="4"/>'
            f'<path d="M-14 -14 L14 14 M14 -14 L-14 14" stroke="#fff" stroke-width="9" stroke-linecap="round"/></g>')


def icon_card(x, y, s=1.0, rot=0.0, glow=0.0, frame_col="#ffffff"):
    """sock + white shirt = pink shirt (icons only)."""
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">']
    if glow > 0:
        o.append(f'<rect x="-190" y="-80" width="380" height="160" rx="26" fill="#fff6a8" opacity="{0.6*glow:.2f}"/>')
    o.append(f'<rect x="-170" y="-64" width="340" height="128" rx="16" fill="{frame_col}" stroke="{OL}" stroke-width="6"/>')
    o.append(sock(-120, -6, "#e8302a", 0, 0.9))
    o.append(f'<path d="M-82 0 h20 M-72 -10 v20" stroke="{OL}" stroke-width="7" stroke-linecap="round"/>')
    o.append(shirt(-20, 0, "#ffffff", 0, 0.95))
    o.append(f'<path d="M30 -6 h22 M30 6 h22" stroke="{OL}" stroke-width="7" stroke-linecap="round"/>')
    o.append(shirt(110, 0, PINK, 0, 0.95))
    o.append('</g>')
    return "".join(o)


def washer(cx, t, working=True, dx=0.0, dy=0.0, rot=0.0, door=0.0, contents=None, dial_ang=0.0, glow=0.0):
    """front-loader; cx = centre x, bottom at FLOOR (+dy). door 0 closed .. 1 swung open."""
    body = "#f3f6fa" if working else "#d9dee6"
    shade = "#c9d2de" if working else "#b4bcc8"
    o = [f'<g transform="translate({cx+dx:.1f} {FLOOR+dy:.1f}) rotate({rot:.2f} 0 -190)">']
    o.append(f'<rect x="-150" y="-380" width="300" height="380" rx="26" fill="{shade}" stroke="{OL}" stroke-width="7"/>'
             f'<rect x="-150" y="-380" width="282" height="370" rx="24" fill="{body}"/>'
             f'<rect x="-150" y="-380" width="300" height="380" rx="26" fill="none" stroke="{OL}" stroke-width="7"/>'
             f'<path d="M-150 -300 H150" stroke="{OL}" stroke-width="5"/>'
             f'<rect x="-136" y="-362" width="120" height="44" rx="10" fill="#2a3446" stroke="{OL}" stroke-width="4"/>')
    if working:
        o.append(f'<rect x="-128" y="-354" width="104" height="28" rx="6" fill="#3ad07a" opacity="0.85"/>'
                 f'<circle cx="-60" cy="-340" r="0" fill="none"/>')
        o.append(f'<circle cx="-2" cy="-340" r="15" fill="#5fd36a" stroke="{OL}" stroke-width="4"/>')
        ax, ay = DIAL[0] - WX, -380 + 38 + 4
        o.append(f'<circle cx="{ax}" cy="{ay}" r="28" fill="#dfe6ee" stroke="{OL}" stroke-width="5"/>'
                 f'<line x1="{ax}" y1="{ay}" x2="{ax + 20*math.cos(dial_ang):.1f}" y2="{ay + 20*math.sin(dial_ang):.1f}" stroke="#e8402e" stroke-width="6" stroke-linecap="round"/>')
        if glow > 0:
            o.append(f'<circle cx="{ax}" cy="{ay}" r="{36+20*glow:.0f}" fill="none" stroke="#ffd23a" stroke-width="{8*(1-glow)+2:.1f}" opacity="{1-glow:.2f}"/>')
    else:
        o.append(f'<circle cx="-2" cy="-340" r="15" fill="#8a929e" stroke="{OL}" stroke-width="4"/>'
                 f'<circle cx="80" cy="-338" r="28" fill="#c4cbd4" stroke="{OL}" stroke-width="5"/>')
    # porthole ring + inside
    py = PORT[1] - FLOOR
    o.append(f'<circle cx="0" cy="{py}" r="{PR+22}" fill="#aab4c0" stroke="{OL}" stroke-width="6"/>')
    o.append(f'<circle cx="0" cy="{py}" r="{PR}" fill="#2c3448" stroke="{OL}" stroke-width="5"/>')
    if contents:
        o.append(contents)
    if door < 0.02:
        o.append(f'<circle cx="0" cy="{py}" r="{PR}" fill="url(#glass)"/>'
                 f'<path d="M-60 {py-50} q30 -34 70 -40" fill="none" stroke="#ffffff" stroke-width="10" stroke-linecap="round" opacity="0.7"/>'
                 f'<circle cx="0" cy="{py}" r="{PR+10}" fill="none" stroke="#e4e9ef" stroke-width="12"/>'
                 f'<circle cx="0" cy="{py}" r="{PR+16}" fill="none" stroke="{OL}" stroke-width="3"/>')
    else:
        # door swung open to the left (seen as an ellipse)
        k = eio(door)
        ox = -lerp(0, 190, k)
        rx = PR + 22 - 70 * k
        o.append(f'<ellipse cx="{ox:.1f}" cy="{py}" rx="{rx:.1f}" ry="{PR+22}" fill="#aab4c0" stroke="{OL}" stroke-width="6"/>'
                 f'<ellipse cx="{ox:.1f}" cy="{py}" rx="{max(4, rx-22):.1f}" ry="{PR}" fill="url(#glass)" stroke="{OL}" stroke-width="4"/>')
    if not working:
        o.append(f'<circle cx="0" cy="{py}" r="{PR}" fill="#1a2030" opacity="0.45"/>')
        o.append(x_sign(0, -230, 0.95))
    # feet
    o.append(f'<rect x="-130" y="-4" width="40" height="12" rx="4" fill="#5a6270" stroke="{OL}" stroke-width="4"/>'
             f'<rect x="90" y="-4" width="40" height="12" rx="4" fill="#5a6270" stroke="{OL}" stroke-width="4"/>')
    o.append('</g>')
    return "".join(o)


def drum_contents(t, n_in, pink, ang, water):
    """clothes tumbling inside the porthole (local coords of washer group)."""
    py = PORT[1] - FLOOR
    cid = "drumclip"
    o = [f'<g clip-path="url(#{cid})">']
    if water > 0:
        wl = py + PR - 2 * PR * 0.45 * water
        wcol = mix_hex("#7ac8f0", "#ff9ac8", pink)
        wave = " ".join(f"L{x} {wl + 6*math.sin(x/16 + t*9):.1f}" for x in range(-PR, PR + 1, 10))
        o.append(f'<path d="M{-PR} {py+PR} L{-PR} {wl:.1f} {wave} L{PR} {py+PR}Z" fill="{wcol}" opacity="0.85"/>')
    items = [("towel", "#ffffff"), ("shirt", "#ffffff"), ("sock", "red"), ("shirt", "#ffffff"), ("towel", "#ffffff"), ("shirt", "#ffffff")]
    spinning = ang > 0.01
    for k in range(min(n_in, len(items))):
        kind, col = items[k]
        if col == "red":
            c = mix_hex("#e8302a", "#ffffff", pink)
        else:
            c = mix_hex("#ffffff", PINK, pink)
        if spinning:
            a = ang + k * 1.05
            rr = 48 + 10 * (k % 2)
            x, y = rr * math.cos(a), py + rr * math.sin(a)
            r = math.degrees(a) * 1.3
        else:
            x = -50 + (k % 3) * 50
            y = py + 50 - (k // 3) * 38
            r = 20 * ((k % 2) * 2 - 1)
        f = {"towel": towel, "shirt": shirt, "sock": sock}[kind]
        o.append(f(x, y, c, r, 0.75))
    if water > 0 and spinning:
        for k in range(5):
            a = -ang * 1.3 + k * 1.3
            o.append(f'<circle cx="{60*math.cos(a):.0f}" cy="{py + 60*math.sin(a):.0f}" r="{6+3*(k%2)}" fill="#ffffff" opacity="0.7"/>')
    o.append('</g>')
    return "".join(o)


def wall(t):
    o = [f'<rect x="-800" y="-400" width="2700" height="{FLOOR+400}" fill="url(#wallL)"/>']
    # tiles
    for y in range(980, FLOOR, 70):
        o.append(f'<line x1="-800" y1="{y}" x2="1900" y2="{y}" stroke="#97cbc4" stroke-width="3"/>')
    for k, y in enumerate(range(980, FLOOR, 70)):
        for x in range(-800 + (k % 2) * 45, 1900, 90):
            o.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+70}" stroke="#97cbc4" stroke-width="3"/>')
    o.append(f'<rect x="-800" y="940" width="2700" height="40" fill="#5fb3a8" stroke="{OL}" stroke-width="5"/>')
    # ceiling lamps
    for x in ():
        o.append(f'<line x1="{x}" y1="-400" x2="{x}" y2="760" stroke="{OL}" stroke-width="5"/>'
                 f'<path d="M{x-70} 830 L{x-40} 760 L{x+40} 760 L{x+70} 830Z" fill="#ffcf4a" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
                 f'<ellipse cx="{x}" cy="832" rx="70" ry="12" fill="#fff6c8" stroke="{OL}" stroke-width="4"/>')
    # floor
    o.append(f'<rect x="-800" y="{FLOOR}" width="2700" height="900" fill="#e9e1d2"/>')
    for i in range(-10, 24):
        for j in range(0, 8):
            if (i + j) % 2 == 0:
                o.append(f'<rect x="{i*90}" y="{FLOOR + j*80}" width="90" height="80" fill="#cfc4b0"/>')
    o.append(f'<rect x="-800" y="{FLOOR-14}" width="2700" height="20" fill="#5fb3a8" stroke="{OL}" stroke-width="5"/>')
    # poster (icons only)
    o.append(icon_card(POSTER[0], POSTER[1], 0.78, 2, 0, "#fffbe8"))
    o.append(f'<circle cx="{POSTER[0]-128}" cy="{POSTER[1]-48}" r="7" fill="#e8402e" stroke="{OL}" stroke-width="3"/><circle cx="{POSTER[0]+136}" cy="{POSTER[1]-44}" r="7" fill="#e8402e" stroke="{OL}" stroke-width="3"/>')
    # detergent shelf (left)
    o.append(f'<rect x="80" y="1090" width="240" height="16" rx="4" fill="#b07a45" stroke="{OL}" stroke-width="5"/>')
    for k, (c, h) in enumerate([("#ff7a3a", 90), ("#3a8fd8", 70), ("#7ad06a", 80)]):
        x = 110 + k * 70
        o.append(f'<rect x="{x}" y="{1090-h}" width="50" height="{h}" rx="10" fill="{c}" stroke="{OL}" stroke-width="5"/>'
                 f'<rect x="{x+14}" y="{1090-h-16}" width="22" height="18" rx="4" fill="#ffffff" stroke="{OL}" stroke-width="4"/>'
                 f'<circle cx="{x+25}" cy="{1090-h/2:.0f}" r="10" fill="#ffffff" opacity="0.8"/>')
    # bubbles floating near the ceiling
    for k in range(6):
        p = (t * 0.15 + k / 6) % 1
        o.append(f'<circle cx="{120 + k*170 + 30*math.sin(t+k):.0f}" cy="{1200 - p*400:.0f}" r="{10+k%3*5}" fill="#ffffff" fill-opacity="0.25" stroke="#ffffff" stroke-width="3" opacity="{0.8*(1-p):.2f}"/>')
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
                 f'<path d="M4 72 q2 30 16 30 q14 0 12 -32" fill="#ff6a8a" stroke="{ink}" stroke-width="6" stroke-linejoin="round"/>')
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
    elif kind == "yeehaw":
        o.append(f'<path d="M-72 -44 Q -40 -64 -8 -46 M8 -46 Q 40 -64 72 -44" fill="none" stroke="{ink}" stroke-width="16" stroke-linecap="round"/>'
                 f'<path d="M-44 56 Q 0 116 44 56Z" fill="#4a0a14" stroke="{ink}" stroke-width="8" stroke-linejoin="round"/>'
                 f'<ellipse cx="0" cy="88" rx="16" ry="8" fill="#ff6a8a"/>')
    elif kind == "flat":
        o.append(f'<path d="M-60 6 h44 v30 h-44z M16 6 h44 v30 h-44z" fill="{base}"/>'
                 f'<path d="M-58 22 h40 M18 22 h40" stroke="{ink}" stroke-width="7" stroke-linecap="round"/>'
                 f'<path d="M-70 -10 Q -44 -14 -16 -8 M70 -10 Q 44 -14 16 -8" fill="none" stroke="{ink}" stroke-width="14" stroke-linecap="round"/>'
                 f'<path d="M-26 76 h52" stroke="{ink}" stroke-width="9" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


def nib_face(x, y, r, rot, sx, sy, kind):
    if not kind:
        return ""
    f = r / 48 * 1.05
    d = "#2a1a10"
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx*f:.3f} {sy*f:.3f})">']
    if kind == "worried":
        o.append(f'<path d="M-24 -18 l12 -5 M24 -18 l-12 -5" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<ellipse cx="-14" cy="-3" rx="7" ry="9" fill="{d}"/><ellipse cx="14" cy="-3" rx="7" ry="9" fill="{d}"/>'
                 '<circle cx="-12" cy="-7" r="2.4" fill="#fff"/><circle cx="16" cy="-7" r="2.4" fill="#fff"/>'
                 f'<ellipse cx="0" cy="17" rx="9" ry="6" fill="#7a2a1a" stroke="{d}" stroke-width="3.5"/>')
    elif kind == "lookleft":
        o.append(f'<ellipse cx="-14" cy="-4" rx="7" ry="9" fill="#fff" stroke="{d}" stroke-width="2"/><ellipse cx="14" cy="-4" rx="7" ry="9" fill="#fff" stroke="{d}" stroke-width="2"/>'
                 f'<circle cx="-18" cy="-2" r="4.5" fill="{d}"/><circle cx="10" cy="-2" r="4.5" fill="{d}"/>'
                 f'<path d="M-24 -18 q8 -6 16 -2 M8 -20 q8 -4 16 2" fill="none" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<path d="M-6 15 q6 -3 12 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    elif kind == "covered":
        o.append(f'<path d="M-8 16 q8 6 16 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    elif kind == "peek":
        o.append(f'<ellipse cx="14" cy="-4" rx="6" ry="8" fill="{d}"/><circle cx="16" cy="-7" r="2.2" fill="#fff"/>'
                 f'<ellipse cx="0" cy="17" rx="7" ry="9" fill="#7a2a1a" stroke="{d}" stroke-width="3.5"/>')
    elif kind == "shrug":
        o.append(f'<path d="M-24 -20 l12 4 M24 -14 l-12 -4" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<ellipse cx="-14" cy="-3" rx="6" ry="7" fill="{d}"/><ellipse cx="14" cy="-3" rx="6" ry="7" fill="{d}"/>'
                 f'<path d="M-24 -6 h20" stroke="#ffd23c" stroke-width="7"/><path d="M-24 -4 h20" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<path d="M-9 16 q9 -4 18 2" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    elif kind == "sparkle":
        o.append(f'<path d="M-21 -2 q7 -10 14 0 M7 -2 q7 -10 14 0" fill="none" stroke="{d}" stroke-width="5" stroke-linecap="round"/>'
                 f'<path d="M-12 8 q12 18 24 0z" fill="#7a2a1a" stroke="{d}" stroke-width="4" stroke-linejoin="round"/>')
    o.append('</g>')
    return "".join(o)


# ---------------------------------------------------------------- states
PILE = [("towel", 0), ("shirt", 0), ("towel", 0), ("shirt", 0), ("shirt", 0), ("towel", 0)]


def pile_count(t):
    """items still on Grumpo's head."""
    n = 6
    for k, ta in enumerate(T_ARM):
        if t >= ta + 0.12:
            n -= 2
    return max(0, n)


def n_in_drum(t):
    if t < T_ARM[0] + 0.3:
        return 0
    k = sum(1 for ta in T_ARM if t >= ta + 0.3)
    return min(6, 2 * k)


def grumpo_state(t):
    g = dict(x=GX, y=GY, rot=0.0, sx=1.0, sy=1.0, ex="grumpy", kind=None, look=(1, 0), red=0.0, hR=None, hL=None,
             pile=pile_count(t), carry=None, hat=False, front=False)
    if t < T_ARR:
        p = eout(seg(t, -0.3, T_ARR))
        g["x"] = lerp(-120, GX + 60, p)
        g["y"] = GY - 14 * abs(math.sin(t * 16))
        g["rot"] = 8
        g["ex"] = "smug"
        g["hL"] = (g["x"] - 70, g["y"] - 150)
        g["hR"] = (g["x"] + 70, g["y"] - 150)
        return g
    if t < T_DOOR_O:
        k = seg(t, T_BUMP, T_BUMP + 0.35)
        g["x"] = lerp(GX + 60, GX, eio(k))
        g["rot"] = lerp(-16, 0, eio(k)) if t >= T_BUMP else 8
        g["ex"] = "smug"
        g["look"] = (1, 0)
        g["hL"] = (g["x"] - 70, g["y"] - 150)
        g["hR"] = (g["x"] + 70, g["y"] - 150)
        if t >= T_SOCK1 - 0.2:
            g["look"] = (1, 0.2)
        return g
    if t < T_DOOR_C + 0.25:
        g["ex"] = "smug"
        g["look"] = (1, 0.3)
        g["hL"] = (g["x"] - 70, g["y"] - 150) if g["pile"] > 0 else None
        if t < T_ARM[0]:
            q = seg(t, T_DOOR_O, T_ARM[0])
            g["hR"] = lerp2((PORT[0] + 80, PORT[1]), (PORT[0] - 190, PORT[1]), eio(q))
        else:
            for k, ta in enumerate(T_ARM):
                if ta <= t < ta + 0.35:
                    q = seg(t, ta, ta + 0.35)
                    top = (g["x"] + 10, g["y"] - GR - 40 - 30 * (2 - k))
                    if q < 0.35:
                        g["hR"] = lerp2((PORT[0] - 60, PORT[1]), top, eio(q / 0.35))
                    else:
                        g["hR"] = lerp2(top, (PORT[0] - 20, PORT[1]), eio((q - 0.35) / 0.65))
                        g["carry"] = (k, g["hR"])
            if t >= T_ARM[-1] + 0.35:
                q = seg(t, T_ARM[-1] + 0.35, T_DOOR_C)
                g["hR"] = lerp2((PORT[0] - 20, PORT[1]), (PORT[0] - 190, PORT[1] - 10), eio(q))
                g["ex"] = "x"
                g["kind"] = "strain" if q > 0.5 else None
                if q <= 0.5:
                    g["ex"] = "smug"
            if t >= T_DOOR_C:
                g["hR"] = None
                g["sx"], g["sy"] = squash(t, T_DOOR_C, 0.25, 0.12)
                g["ex"], g["kind"] = "smug", None
        return g
    if t < T_W1_0:
        g["ex"] = "smug"
        g["look"] = (1, -0.2)
        return g
    if t < T_D1 + 0.25:
        g["look"] = (1, 0)
        g["ex"] = "smug"
        if t >= T_WAG0 and t < T_D1 - 0.25:
            g["hR"] = (g["x"] + 70 + 22 * math.sin((t - T_WAG0) * 22), g["y"] - 140)
            g["ex"], g["kind"] = "x", "tongue"
        elif t >= T_D1 - 0.25:
            q = eio(seg(t, T_D1 - 0.25, T_D1))
            g["hR"] = lerp2((g["x"] + 70, g["y"] - 140), DIAL, q)
            g["look"] = (1, -1)
        return g
    if t < T_W2_0:
        g["hR"] = lerp2(DIAL, (g["x"] + 110, g["y"] + 30), eio(seg(t, T_D1 + 0.25, T_D1 + 0.45)))
        g["ex"] = "smug"
        g["look"] = (1, 0)
        return g
    if t < T_D2 + 0.25:
        g["ex"] = "suspicious"
        g["look"] = (1, -0.3)
        if t >= T_SNATCH - 0.15:
            q = eio(seg(t, T_SNATCH - 0.15, T_SNATCH))
            card = (NX, NY - 230)
            g["hR"] = lerp2((g["x"] + 110, g["y"] + 30), card, q)
        if t >= T_SNATCH:
            q = eio(seg(t, T_SNATCH, T_CRUMPLE))
            g["hR"] = lerp2((NX, NY - 230), (g["x"] + 80, g["y"] - 120), q)
            g["ex"] = "angry"
        if t >= T_CRUMPLE:
            g["hR"] = (g["x"] + 80, g["y"] - 120)
            g["hL"] = (g["x"] + 40, g["y"] - 130)
            g["ex"], g["kind"] = "x", "strain"
        if t >= T_TOSS0:
            q = seg(t, T_TOSS0, T_TOSS0 + 0.2)
            g["hL"] = None
            g["hR"] = lerp2((g["x"] + 80, g["y"] - 120), (g["x"] - 60, g["y"] - 180), eout(q))
            g["ex"], g["kind"] = "smug", None
        if t >= T_D2 - 0.2:
            q = eio(seg(t, T_D2 - 0.2, T_D2))
            g["hR"] = lerp2((g["x"] - 60, g["y"] - 180), DIAL, q)
            g["look"] = (1, -1)
        return g
    if t < T_FLICK + 0.1:
        g["hR"] = lerp2(DIAL, (g["x"] + 110, g["y"] + 30), eio(seg(t, T_D2 + 0.25, T_D2 + 0.45)))
        g["ex"] = "smug"
        if t >= T_W3_0 + 0.25:
            # Nibbo tugs his hand toward the porthole; he resists
            nh = nibbo_state(t)["hL"]
            g["hR"] = (nh[0] - 10, nh[1]) if nh else g["hR"]
            g["ex"], g["kind"] = "x", "strain"
            g["rot"] = -6 + 3 * math.sin(t * 30)
            g["red"] = 0.25
        if t >= T_FLICK - 0.12:
            g["ex"], g["kind"] = "angry", None
            g["hR"] = (g["x"] + 150, g["y"] - 10)
        return g
    if t < T_LEAN:
        g["red"] = 0.25 * (1 - seg(t, T_FLICK, T_D3))
        g["ex"] = "smug"
        g["hR"] = (g["x"] + 150, g["y"] - 10) if t < T_FLICK + 0.25 else None
        if t >= T_D3 - 0.25:
            q = eio(seg(t, T_D3 - 0.25, T_D3))
            g["hR"] = lerp2((g["x"] + 110, g["y"]), DIAL, q)
            g["hL"] = lerp2((g["x"] - 100, g["y"]), (DIAL[0] - 30, DIAL[1] + 10), q)
            g["ex"], g["kind"] = "x", "grin"
        return g
    if t < T_D4:
        q = eio(seg(t, T_LEAN, T_LEAN + 0.3))
        g["x"] = lerp(GX, GX + 70, q)
        g["rot"] = 14 * q
        g["ex"] = "smug"
        g["look"] = (1, 0)
        g["hR"] = (g["x"] + 20, g["y"] + 50)
        g["hL"] = (g["x"] - 10, g["y"] + 56)
        return g
    if t < T_LAUNCH1:
        p = seg(t, T_D4, T_LAUNCH1)
        dx, dy, rot = machine_motion(t)
        top = (WX + dx, W_TOP + dy - GR + 8)
        g["x"] = lerp(GX + 70, top[0], eio(p))
        g["y"] = lerp(GY, top[1], p) - 140 * math.sin(math.pi * p)
        g["rot"] = 14 - 360 * eio(p)
        g["ex"] = "shock"
        g["look"] = (0, -1)
        g["front"] = True
        return g
    if t < T_STOP:
        dx, dy, rot = machine_motion(t)
        k = t - T_LAUNCH1
        g["x"] = WX + dx - 8 * math.sin(k * 7.5)
        g["y"] = W_TOP + dy - GR + 8 - 24 * abs(math.sin(k * 7.5 + 1.2))
        g["rot"] = rot * 1.6 + 8 * math.sin(k * 7.5)
        g["sx"], g["sy"] = 1 + 0.06 * math.sin(k * 15), 1 - 0.06 * math.sin(k * 15)
        g["ex"], g["kind"] = "x", "yeehaw"
        g["hR"] = (g["x"] + 120, g["y"] - 120 + 20 * math.sin(k * 12))
        g["hL"] = (g["x"] - 100, g["y"] + 70)
        g["front"] = True
        return g
    if t < T_UP:
        p = seg(t, T_STOP, T_THROWN1)
        g["front"] = True
        if p < 1:
            g["x"] = lerp(WX, GX + 60, eio(p))
            g["y"] = lerp(W_TOP - GR + 8, GY, p) - 160 * math.sin(math.pi * p)
            g["rot"] = -300 * eio(p)
            g["ex"] = "shock"
        else:
            g["x"] = GX + 60
            g["sy"] = 0.62 + 0.38 * eout(seg(t, T_THROWN1 + 0.1, T_UP))
            g["sx"] = 2 - g["sy"]
            g["y"] = FLOOR - GR * g["sy"]
            g["ex"], g["kind"] = "x", "dizzy"
        return g
    g["x"] = GX + 60
    g["front"] = True
    if t < T_PINK:
        g["ex"] = "smug"
        g["sx"], g["sy"] = squash(t, T_UP, 0.25, 0.1)
        if t >= T_OPEN - 0.15:
            q = eio(seg(t, T_OPEN - 0.15, T_OPEN))
            g["hR"] = lerp2((g["x"] + 110, g["y"] + 20), (PORT[0] + 60, PORT[1]), q)
            if t >= T_OPEN:
                q2 = eio(seg(t, T_OPEN, T_REACH0))
                g["hR"] = lerp2((PORT[0] + 60, PORT[1]), (PORT[0] - 120, PORT[1]), q2)
        if t >= T_REACH0:
            q = seg(t, T_REACH0, T_REACH1)
            g["hR"] = lerp2((PORT[0] - 120, PORT[1]), PORT, eio(min(1, q * 2))) if q < 0.5 else lerp2(PORT, (g["x"] + 40, g["y"] - 170), eio((q - 0.5) * 2))
            g["look"] = (1, 0.3)
        return g
    g["hR"] = (g["x"] + 40, g["y"] - 170)
    g["carry"] = ("pink",)
    if t < T_ANGRY:
        g["ex"] = "shock"
        g["look"] = (-0.2, -1)
        g["sx"], g["sy"] = squash(t, T_PINK, 0.3, 0.16)
        return g
    if t < T_SOCK2_0:
        g["ex"] = "angry"
        g["red"] = 0.7 * seg(t, T_ANGRY, T_ANGRY + 0.2)
        g["look"] = (1, 0)
        g["rot"] = 3 * math.sin(t * 34)
        g["hR"] = (g["x"] + 100, g["y"] - 80)
        if t >= T_POINT + 0.2:
            g["look"] = (1, -1)
        return g
    g["hR"] = None
    g["carry"] = ("pink_floor",)
    if t < T_BRIEFS1:
        g["red"] = 0.7 * (1 - seg(t, T_SOCK2_0, T_SOCK2_0 + 0.4))
        g["ex"] = "shock"
        m = sock2_pos(t)
        if m:
            g["look"] = (cl((m[0] - g["x"]) / 300, -1, 1), cl((m[1] - g["y"]) / 300, -1, 1))
        else:
            g["look"] = (1, 0)
        if t >= T_BRIEFS0:
            g["look"] = (0, -1)
        return g
    g["hat"] = True
    g["ex"], g["kind"] = "x", "flat"
    g["sx"], g["sy"] = squash(t, T_BRIEFS1, 0.3, 0.14)
    return g


def sock2_pos(t):
    if T_SOCK2_0 <= t < T_SOCK2_1:
        p = seg(t, T_SOCK2_0, T_SOCK2_1)
        x = lerp(PORT[0], NX - 20, p)
        y = lerp(PORT[1], NY - 190, p) - 300 * math.sin(math.pi * p)
        return x, y, 900 * p
    return None


def nibbo_state(t):
    n = dict(x=NX, y=NY, rot=0.0, sx=1.0, sy=1.0, ex="happy", kind=None, hL=None, hR=None, basket=None, card=None)
    if t < T_BUMP:
        p = eout(seg(t, -0.3, T_ARR))
        n["x"] = lerp(1200, WX + 210, p)
        n["y"] = NY - 12 * abs(math.sin(t * 18))
        n["rot"] = -8
        n["basket"] = (n["x"] - 40, n["y"] + 10, 0.75, 0)
        n["hL"] = (n["x"] - 90, n["y"] + 10)
        n["hR"] = (n["x"] + 10, n["y"] + 30)
        return n
    if t < T_SEEK:
        p = seg(t, T_BUMP, T_BUMP + 0.5)
        n["x"] = lerp(WX + 210, NX, eout(p))
        n["y"] = NY - 120 * math.sin(math.pi * p) if p < 1 else NY
        n["rot"] = 300 * eout(p)
        n["ex"] = "wow" if p < 1 else "dizzy"
        if p >= 1:
            n["sx"], n["sy"] = squash(t, T_BUMP + 0.5, 0.3, 0.2)
            n["rot"] = 0
        if t >= T_BUMP + 1.2:
            n["ex"] = "happy"
            # gathering clothes back into the basket
            n["hL"] = (n["x"] - 80, NY + 70 - 30 * abs(math.sin(t * 9)))
        return n
    if t < T_SEE:
        n["ex"], n["kind"] = "blank", "lookleft"
        n["rot"] = 10 * math.sin((t - T_SEEK) * 5)
        return n
    if t < T_W1_0:
        n["ex"] = "wow"
        n["sx"], n["sy"] = squash(t, T_SEE, 0.3, 0.16)
        return n
    if t < T_W2_0:
        k = t - T_W1_0
        n["x"] = NX - 60
        n["y"] = NY - 90 * abs(math.sin(k * 9))
        n["ex"], n["kind"] = "blank", "worried"
        n["hL"] = (n["x"] - 140, n["y"] - 10)
        n["hR"] = (n["x"] + 70, n["y"] - 130 + 30 * math.sin(k * 18))
        if t >= T_D1:
            n["ex"], n["kind"] = "uhoh", None
            n["y"] = NY
            n["hL"], n["hR"] = None, None
        return n
    if t < T_D2 + 0.2:
        n["ex"], n["kind"] = "blank", "worried"
        if t < T_SNATCH:
            p = eout(seg(t, T_W2_0, T_W2_0 + 0.3))
            n["card"] = (NX, lerp(NY + 40, NY - 230, p), lerp(0.3, 0.62, p))
            n["hL"] = (NX - 80, n["card"][1] + 10)
            n["hR"] = (NX + 80, n["card"][1] + 10)
            n["y"] = NY - 30 * abs(math.sin(t * 8))
        else:
            n["ex"], n["kind"] = "wow", None
            if t >= T_CRUMPLE:
                n["ex"], n["kind"] = "blank", "worried"
        return n
    if t < T_FLICK:
        p = eio(seg(t, T_W3_0, T_W3_0 + 0.25))
        n["x"] = lerp(NX, GX + 250, p)
        n["y"] = NY - 60 * math.sin(math.pi * p)
        n["ex"], n["kind"] = "blank", "worried"
        if t >= T_W3_0 + 0.25:
            k = t - T_W3_0 - 0.25
            n["x"] = GX + 250 + 30 * seg(t, T_W3_0 + 0.25, T_W3_1) + 6 * math.sin(k * 30)
            n["rot"] = 14
            n["hL"] = (GX + 160 + 20 * seg(t, T_W3_0 + 0.25, T_W3_1), GY + 20)
            n["hR"] = (n["x"] + 40, n["y"] + 70)
            n["sx"], n["sy"] = 1.06, 0.94
        return n
    if t < T_LEAN:
        p = seg(t, T_FLICK, T_SLIDE1)
        n["x"] = lerp(GX + 280, NX + 20, eout(p))
        n["rot"] = 720 * eout(p)
        n["ex"] = "dizzy"
        if p >= 1:
            n["rot"] = 0
            n["x"] = NX + 20
            n["sx"], n["sy"] = squash(t, T_SLIDE1, 0.25, 0.15)
        return n
    n["x"] = NX + 20
    if t < T_STOP + 0.2:
        n["ex"] = "uhoh"
        if t >= T_COVER:
            q = eio(seg(t, T_COVER, T_COVER + 0.2))
            n["hL"] = lerp2((n["x"] - 90, n["y"] + 40), (n["x"] - 18, n["y"] - 10), q)
            n["hR"] = lerp2((n["x"] + 90, n["y"] + 40), (n["x"] + 18, n["y"] - 10), q)
            n["ex"], n["kind"] = "blank", "covered"
        if t >= T_D4 + 0.6:
            n["hR"] = (n["x"] + 40, n["y"] - 8)
            n["ex"], n["kind"] = "blank", "peek"
            n["rot"] = -6
        return n
    if t < T_POINT:
        n["ex"] = "uhoh" if t < T_PINK else "nervous"
        return n
    if t < T_SOCK2_0:
        n["ex"], n["kind"] = "blank", "shrug"
        q = eio(seg(t, T_POINT, T_POINT + 0.2))
        n["hR"] = lerp2((n["x"] + 90, n["y"] + 40), (n["x"] + 30, n["y"] - 170), q)
        n["hL"] = lerp2((n["x"] - 90, n["y"] + 40), (n["x"] - 120, n["y"] - 20), q)
        return n
    if t < T_SOCK2_1 + 0.1:
        n["ex"] = "wow"
        q = eio(seg(t, T_SOCK2_0 + 0.2, T_SOCK2_1))
        n["hR"] = lerp2((n["x"] + 70, n["y"] + 40), (NX - 20, NY - 170), q)
        return n
    if t < T_LEAVE0:
        n["ex"], n["kind"] = "blank", "sparkle"
        n["hR"] = (NX + 10, NY - 190)
        n["y"] = NY - 40 * abs(math.sin((t - T_SOCK2_1) * 9))
        n["sx"], n["sy"] = squash(t, T_SOCK2_1 + 0.1, 0.25, 0.12)
        return n
    p = seg(t, T_LEAVE0, T_LEAVE1)
    n["x"] = lerp(NX + 20, 1260, p)
    n["y"] = NY - 50 * abs(math.sin(p * math.pi * 4))
    n["ex"] = "joy"
    n["hR"] = (n["x"] + 30, n["y"] - 170)
    n["basket"] = (n["x"] - 40, n["y"] + 20, 0.75, 0)
    n["hL"] = (n["x"] - 100, n["y"] + 20)
    return n


# ---------------------------------------------------------------- camera
CK = [(0.0, (560, 1270, 1.45)), (T_BUMP, (560, 1280, 1.48)), (T_SOCK1, (420, 1240, 1.55)), (T_SPOT1, (430, 1260, 1.5)),
      (T_DOOR_C, (480, 1270, 1.45)), (T_SEE, (560, 1280, 1.5)), (T_D1, (560, 1260, 1.42)), (T_SNATCH, (580, 1250, 1.4)),
      (T_D2, (540, 1260, 1.45)), (T_FLICK, (520, 1270, 1.5)), (T_D3, (560, 1270, 1.45)), (T_D4, (560, 1200, 1.3)),
      (T_STOP - 0.3, (540, 1160, 1.25)), (T_THROWN1, (520, 1270, 1.45)), (T_PINK, (480, 1290, 1.6)), (T_ANGRY, (520, 1280, 1.48)),
      (T_POINT + 0.3, (620, 1220, 1.4)), (T_SOCK2_1, (640, 1260, 1.45)), (T_BRIEFS1, (460, 1290, 1.55)), (DUR, (480, 1290, 1.5))]
SHAKES = [(T_BUMP, 10, 0.25), (T_DOOR_C, 6, 0.2), (T_D3, 8, 0.3), (T_D4, 16, 0.4), (T_STOP, 18, 0.35), (T_THROWN1, 14, 0.3), (T_PINK, 6, 0.2)]


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
    if T_D4 <= t < T_STOP:
        amp = max(amp, 6)
    return cx + amp * math.sin(t * 93), cy + amp * math.cos(t * 79), z


def arm_anchor(c, key, side, py0=30):
    hx = c[key][0]
    sd = 1 if hx > c["x"] + 10 else (-1 if hx < c["x"] - 10 else side)
    return sd, py0


# ---------------------------------------------------------------- frame
def pile_svg(x, y, count, t, sock_on, rot=0.0):
    """white laundry stacked on Grumpo's head; (x, y) = top of head."""
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">']
    for k in range(count):
        kind = PILE[k][0]
        yy = -22 - k * 30
        xx = 12 * math.sin(k * 1.7 + t * 0.8)
        r = 8 * math.sin(k * 2.3)
        o.append(towel(xx, yy, "#ffffff", r, 1.15) if kind == "towel" else shirt(xx, yy - 6, "#ffffff", r, 1.0))
    if sock_on and count > 0:
        o.append(sock(10, -22 - count * 30 + 4, "#e8302a", 70, 0.9))
    o.append('</g>')
    return "".join(o)


def frame(t):
    ctx = Ctx()
    ctx.defs.append(f'<clipPath id="drumclip"><circle cx="0" cy="{PORT[1]-FLOOR}" r="{PR-4}"/></clipPath>')
    g = grumpo_state(t)
    n = nibbo_state(t)
    L = [wall(t)]
    # broken machines
    L.append(washer(WX - 330, t, working=False))
    L.append(washer(WX + 330, t, working=False))
    # working machine
    dx, dy, rot = machine_motion(t)
    door = 0.0
    if T_DOOR_O <= t < T_DOOR_C:
        door = seg(t, T_DOOR_O, T_DOOR_O + 0.2) * (1 - seg(t, T_DOOR_C - 0.15, T_DOOR_C))
    if t >= T_OPEN:
        door = seg(t, T_OPEN, T_OPEN + 0.2)
    started = t >= T_D1 + 0.1
    water = seg(t, T_D1 + 0.1, T_D1 + 0.8) if started else 0.0
    if t >= T_STOP:
        water = 1 - seg(t, T_STOP, T_STOP + 0.4)
    nin = n_in_drum(t)
    if t >= T_REACH1:
        nin = 1 if t < T_SOCK2_0 else 0
    pk = pinkness(t)
    ang = drum_ang(t) if started else 0.0
    if t >= T_REACH1:
        contents = drum_contents(t, 0, pk, ang, water)
        if t < T_SOCK2_0:
            contents += sock(0, PORT[1] - FLOOR + 40, "#ffffff", 30, 0.75)
    else:
        contents = drum_contents(t, nin, pk, ang, water)
    dial_ang = -math.pi / 2 + sum(1.1 for d in D_TIMES[:3] if t >= d)
    if t >= T_D4:
        dial_ang += (t - T_D4) * 25 if t < T_STOP else (T_STOP - T_D4) * 25
    glow = 0.0
    for d in D_TIMES:
        if d <= t < d + 0.4:
            glow = seg(t, d, d + 0.4)
    L.append(shadow(WX, FLOOR + 6, 170, 1.0 + dy / 200))
    L.append(washer(WX, t, True, dx, dy, rot, door, contents, dial_ang, glow))
    # suds puffs when going wild
    if T_D3 <= t < T_STOP + 0.3:
        lv = 1.0 if t >= T_D4 else 0.4
        for k in range(5):
            q = ((t - T_D3) * 1.6 + k / 5) % 1
            x = WX + dx + (-140 if k % 2 else 140) + (-60 if k % 2 else 60) * q
            y = FLOOR - 300 + dy - 120 * q + 30 * k
            L.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{(14+10*(k%3))*lv*(0.6+q):.0f}" fill="#ffffff" stroke="#bfe6f0" stroke-width="3" opacity="{(1-q)*0.9:.2f}"/>')
    if T_D2 <= t < T_STOP:
        L.append(speed_lines(WX + dx - 170, FLOOR - 200 + dy, 0, 0.35 + 0.4 * (t >= T_D3)))
        L.append(speed_lines(WX + dx + 170, FLOOR - 200 + dy, 180, 0.35 + 0.4 * (t >= T_D3)))

    # pink laundry spilled on the floor
    if t >= T_POUR0:
        q = seg(t, T_POUR0, T_POUR1)
        items = [("shirt", 400, -20), ("towel", 470, 10), ("shirt", 520, -30), ("towel", 610, 15), ("shirt", 660, 25)]
        for k, (kind, x, r) in enumerate(items):
            pk_ = seg(q, k * 0.15, k * 0.15 + 0.4)
            if pk_ <= 0:
                continue
            yy = lerp(PORT[1] + 20, FLOOR - 30 - (k % 2) * 26, ein(pk_))
            xx = lerp(PORT[0] - 60, x, pk_)
            L.append(towel(xx, yy, PINK, r, 1.0) if kind == "towel" else shirt(xx, yy, PINK, r, 1.0))

    # Nibbo's scattered clothes (after the bump) until gathered
    if T_BUMP <= t < T_SEEK:
        items = [(shirt, "#3a8fd8", NX - 120, -40), (towel, "#5fd36a", NX + 100, 20)]
        for k, (f, c, x, r) in enumerate(items):
            p = seg(t, T_BUMP, T_BUMP + 0.6 + 0.1 * k)
            gather = seg(t, T_BUMP + 1.2 + 0.4 * k, T_BUMP + 1.5 + 0.4 * k)
            if gather >= 1:
                continue
            xx = lerp(WX + 170, x, p)
            yy = lerp(NY - 40, FLOOR - 26, p) - 260 * math.sin(math.pi * p)
            L.append(f(xx, yy, c, r + 400 * (1 - p), 1.0))
    # Nibbo's basket on the floor
    if T_BUMP <= t < T_LEAVE0:
        bp = seg(t, T_BUMP, T_BUMP + 0.6)
        bx = lerp(WX + 170, NX + 150, bp)
        by = lerp(NY + 10, FLOOR - 26, bp) - 200 * math.sin(math.pi * bp)
        L.append(basket(bx, by, "#3a8fd8", 0.75, 540 * eout(bp) if bp < 1 else 0))
        if t >= T_BUMP + 1.7:
            L.append(shirt(bx - 14, by - 26, "#3a8fd8", -10, 0.7) + towel(bx + 18, by - 22, "#5fd36a", 8, 0.65))

    # the red sock flight #1
    if T_BUMP <= t < T_SOCK1:
        p = seg(t, T_BUMP, T_SOCK1)
        gtop = (GX + 10, GY - GR - 22 - 6 * 30)
        x = lerp(WX + 170, gtop[0], eio(p))
        y = lerp(NY - 40, gtop[1], p) - 420 * math.sin(math.pi * p)
        L.append(sock(x, y, "#e8302a", 720 * p, 1.0))

    # ---- characters
    def draw_g():
        out = [grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "up", g["look"], g["rot"], g["sx"], g["sy"], drink=False, t=t),
               grumpo_extra(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], g["kind"], t, g["red"])]
        if g["pile"] > 0:
            hx, hy = bodypt(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], 0, -128)
            out.append(pile_svg(hx, hy, g["pile"], t, t >= T_SOCK1 and t < T_ARM[0] + 0.12, g["rot"]))
        if g["hat"]:
            hx, hy = bodypt(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], 0, -118)
            out.append(briefs(hx, hy, PINK, g["rot"], 1.6))
        return "".join(out)

    L.append(shadow(g["x"], FLOOR + 6, 120, 1.0 if g["y"] > GY - 40 else 0.5))
    L.append(shadow(n["x"], FLOOR + 6, 110, 1.0 if n["y"] > NY - 40 else 0.6))
    L.append(draw_g())
    L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"] if n["kind"] is None else "blank", rot=n["rot"], sx=n["sx"], sy=n["sy"]))
    L.append(nib_face(n["x"], n["y"], NR, n["rot"], n["sx"], n["sy"], n["kind"]))
    if n["basket"]:
        bx, by, bs, br = n["basket"]
        L.append(basket(bx, by, "#3a8fd8", bs, br))
        L.append(shirt(bx - 14, by - 26, "#3a8fd8", -10, 0.7) + towel(bx + 18, by - 22, "#5fd36a", 8, 0.65))
        if t < T_BUMP:
            L.append(sock(bx + 30, by - 40, "#e8302a", 30, 0.8))
        if t >= T_LEAVE0:
            L.append(sock(bx + 30, by - 40, "#ffffff", 30, 0.8))
    if n["card"]:
        cx_, cy_, cs = n["card"]
        L.append(icon_card(cx_, cy_, cs, 0))

    # carried items
    if g["carry"] and isinstance(g["carry"][0], int):
        k, (hx, hy) = g["carry"]
        L.append(towel(hx, hy - 10, "#ffffff", 20, 0.9) + shirt(hx + 16, hy - 30, "#ffffff", -10, 0.85))
        if k == 0:
            L.append(sock(hx - 10, hy - 50, "#e8302a", 50, 0.9))
    if g["carry"] and g["carry"][0] == "pink" and t < T_SOCK2_0:
        hx, hy = g["hR"]
        L.append(shirt(hx, hy - 60, PINK, -6, 1.9))
    # card snatched + crumpled + tossed
    if T_SNATCH <= t < T_CRUMPLE:
        hx, hy = g["hR"]
        L.append(icon_card(hx, hy - 30, 0.62, -10 * seg(t, T_SNATCH, T_CRUMPLE)))
    if T_CRUMPLE <= t < T_TOSS0:
        k = seg(t, T_CRUMPLE, T_CRUMPLE + 0.15)
        hx, hy = g["hR"]
        if k < 1:
            L.append(icon_card(hx - 20, hy - 30, 0.62 * (1 - k) + 0.1, 60 * k))
        else:
            L.append(f'<circle cx="{hx-20:.0f}" cy="{hy-20:.0f}" r="30" fill="#fffbe8" stroke="{OL}" stroke-width="5"/><path d="M{hx-36:.0f} {hy-28:.0f} l14 8 l10 -12 l8 14" fill="none" stroke="{OL}" stroke-width="3"/>')
    if T_TOSS0 <= t < T_TOSS1:
        p = seg(t, T_TOSS0, T_TOSS1)
        x = lerp(GX + 40, -200, p)
        y = lerp(GY - 150, GY - 300, p) - 120 * math.sin(math.pi * p)
        L.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="30" fill="#fffbe8" stroke="{OL}" stroke-width="5" transform="rotate({p*600:.0f} {x:.0f} {y:.0f})"/>')

    # white sock flight #2 (the twist)
    s2 = sock2_pos(t)
    if s2:
        L.append(sock(s2[0], s2[1], "#ffffff", s2[2], 1.1))
        L.append(star_twinkle(s2[0] + 30, s2[1] - 20, ((t - T_SOCK2_0) * 3) % 1))
    if t >= T_SOCK2_1 and n["hR"] and t < T_LEAVE0:
        hx, hy = n["hR"]
        L.append(sock(hx + 6, hy - 30, "#ffffff", -10, 1.1))
    if t >= T_LEAVE0 and n["hR"]:
        hx, hy = n["hR"]
        L.append(sock(hx + 6, hy - 30, "#ffffff", -10 + 20 * math.sin(t * 12), 1.1))
    # pink briefs falling onto Grumpo's head
    if T_BRIEFS0 <= t < T_BRIEFS1:
        p = seg(t, T_BRIEFS0, T_BRIEFS1)
        hx, hy = bodypt(g["x"], g["y"], GS, g["rot"], g["sx"], g["sy"], 0, -118)
        x = lerp(PORT[0], hx, p)
        y = lerp(PORT[1], hy, p) - 280 * math.sin(math.pi * p)
        L.append(briefs(x, y, PINK, 540 * p, 1.4 + 0.2 * p))

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
    L.append(impact(WX + 130, GY + 20, seg(t, T_BUMP, T_BUMP + 0.25)))
    if T_SPOT0 <= t < T_SPOT1:
        q = seg(t, T_SPOT0, T_SPOT1)
        op = math.sin(math.pi * q)
        sx_, sy_ = GX + 10, GY - GR - 22 - 6 * 30
        L.append(f'<circle cx="{sx_}" cy="{sy_}" r="900" fill="url(#spot)" opacity="{op:.2f}"/>')
        L.append(f'<circle cx="{sx_}" cy="{sy_}" r="{70+10*math.sin(t*20):.0f}" fill="none" stroke="#fff36a" stroke-width="7" opacity="{op:.2f}"/>')
        L.append(star_twinkle(sx_ + 60, sy_ - 40, q))
    L.append(symbol(n["x"] + 10, n["y"] - 170, "?", seg(t, T_SEEK, T_SEEK + 0.6), "#3a8fd8"))
    L.append(symbol(n["x"] + 10, n["y"] - 170, "!", seg(t, T_SEE, T_SEE + 0.5)))
    if T_SEE <= t < T_SEE + 0.6:
        L.append(f'<circle cx="{PORT[0]}" cy="{PORT[1]}" r="{PR+30+20*seg(t, T_SEE, T_SEE+0.6):.0f}" fill="none" stroke="#e8302a" stroke-width="8" opacity="{1-seg(t, T_SEE, T_SEE+0.6):.2f}"/>')
    L.append(impact(GX + 250, GY + 10, seg(t, T_FLICK, T_FLICK + 0.25)))
    if T_FLICK < t < T_SLIDE1:
        L.append(speed_lines(n["x"] - 130, n["y"], 0, 0.7))
    L.append(impact(WX, FLOOR - 10, seg(t, T_STOP, T_STOP + 0.3)))
    L.append(impact(g["x"], FLOOR - 20, seg(t, T_THROWN1, T_THROWN1 + 0.3)))
    L.append(symbol(g["x"] - 120, g["y"] - 150, "!", seg(t, T_PINK, T_PINK + 0.6)))
    if T_POINT <= t < T_SOCK2_0 + 0.3:
        L.append(f'<rect x="{POSTER[0]-160}" y="{POSTER[1]-70}" width="320" height="140" rx="20" fill="none" stroke="#fff36a" stroke-width="{8+3*math.sin(t*20):.1f}"/>')
    L.append(symbol(g["x"] + 20, g["y"] - 190, "?", seg(t, T_GASP, T_GASP + 0.6), "#3a8fd8"))
    if T_SOCK2_1 <= t < T_LEAVE0 + 0.5:
        L.append(star_twinkle(NX + 50, NY - 260, seg(t, T_SOCK2_1, T_SOCK2_1 + 0.6)))
        L.append(star_twinkle(NX - 40, NY - 220, seg(t, T_SOCK2_1 + 0.2, T_SOCK2_1 + 0.8)))

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{defs()}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g>'
           f'<rect width="{W}" height="{H}" fill="url(#vig)"/></svg>')
    layers = [hook_title(t + 0.12, "Nibbo tried to warn", "GRUMPO 3 TIMES")]
    lv = level(t)
    if lv > 0:
        bump = D_TIMES[lv - 1]
        layers.append(counter(t, D_VALS[lv - 1], "SPIN", lv, 4, bump_t=bump))
    return overlay(svg, *layers)


def build_sfx():
    sfx(0.0, "whoosh", 0.6, 1.0)
    for k in range(3):
        sfx(0.05 + k * 0.18, "tiptoe", 0.4, 1.2)
    sfx(T_BUMP, "bonk", 0.9, 0.9)
    sfx(T_BUMP + 0.02, "boing", 0.6, 1.2)
    sfx(T_BUMP + 0.1, "whoosh", 0.5, 1.4)
    sfx(T_BUMP + 0.55, "thud", 0.5, 1.3)
    sfx(T_BUMP + 0.6, "flutter", 0.4, 1.2)
    sfx(T_SOCK1, "plop", 0.6, 1.5)
    sfx(T_SOCK1 + 0.02, "suspense", 0.5, 1.0)
    sfx(T_DOOR_O, "click", 0.6, 1.0)
    for ta in T_ARM:
        sfx(ta + 0.15, "whoosh", 0.4, 1.5)
        sfx(ta + 0.3, "flutter", 0.4, 1.1)
    sfx(T_DOOR_C - 0.1, "strain", 0.5, 1.2)
    sfx(T_DOOR_C, "lock_click", 0.8, 1.0)
    sfx(T_SEEK, "blip", 0.4, 1.2)
    sfx(T_SEE, "gasp", 0.7, 1.4)
    sfx(T_SEE + 0.05, "alert", 0.5, 1.0)
    for k in range(4):
        sfx(T_W1_0 + k * 0.175, "hop", 0.4, 1.4)
    sfx(T_WAG0, "squeak", 0.4, 1.6)
    sfx(T_WAG0 + 0.25, "laugh", 0.4, 0.8)
    for d in D_TIMES:
        sfx(d, "dial", 0.8, 1.0)
        sfx(d + 0.05, "ding", 0.35, 1.5)
    sfx(T_D1 + 0.1, "spin_up", 0.5, 0.8)
    k = T_D1 + 0.2
    while k < T_STOP - 0.3:
        lv = level(k)
        sfx(k, "washer", 0.35 + 0.1 * lv, 0.8 + 0.15 * lv)
        k += 1.3
    sfx(T_W2_0, "pop", 0.5, 1.3)
    sfx(T_SNATCH, "zip", 0.6, 1.2)
    sfx(T_CRUMPLE, "crunch", 0.7, 1.4)
    sfx(T_TOSS0, "whoosh", 0.5, 1.4)
    sfx(T_D2 + 0.1, "spin_up", 0.5, 1.0)
    sfx(T_W3_0, "squeak_slide", 0.4, 1.4)
    sfx(T_W3_0 + 0.3, "strain", 0.6, 1.5)
    sfx(T_FLICK, "boing", 0.8, 1.2)
    sfx(T_FLICK + 0.02, "zoom", 0.5, 1.4)
    sfx(T_SLIDE1, "thud", 0.5, 1.4)
    sfx(T_D3 + 0.1, "spin_up", 0.6, 1.2)
    sfx(T_D3 + 0.3, "rumble", 0.5, 1.2)
    sfx(T_LEAN, "cool", 0.5, 1.0)
    sfx(T_D4 + 0.05, "spin_up", 0.8, 1.5)
    sfx(T_D4 + 0.1, "rumble", 0.8, 1.0)
    sfx(T_D4 + 0.05, "boing", 0.8, 0.9)
    sfx(T_D4 + 0.1, "gasp", 0.5, 0.9)
    k = T_LAUNCH1
    while k < T_STOP - 0.1:
        sfx(k, "thunk", 0.55, 0.9)
        k += 0.42
    sfx(T_LAUNCH1 + 0.1, "cheer", 0.5, 0.9)
    sfx(T_D4 + 1.0, "rumble", 0.7, 1.1)
    sfx(T_STOP, "ding", 0.9, 1.0)
    sfx(T_STOP + 0.02, "thud", 0.8, 0.8)
    sfx(T_STOP + 0.05, "whoosh", 0.6, 1.0)
    sfx(T_THROWN1, "squish", 0.8, 0.8)
    sfx(T_THROWN1 + 0.05, "thud", 0.7, 1.0)
    sfx(T_OPEN, "click", 0.6, 1.0)
    sfx(T_REACH0 + 0.2, "rustle", 0.5, 1.0)
    sfx(T_PINK, "gasp", 0.9, 0.85)
    sfx(T_PINK + 0.05, "alert", 0.6, 0.9)
    for k in range(5):
        sfx(T_POUR0 + k * 0.12, "flutter", 0.35, 1.0 + 0.1 * k)
    sfx(T_ANGRY, "grumble", 0.8, 0.85)
    sfx(T_POINT, "ding", 0.5, 1.2)
    sfx(T_SOCK2_0, "boing", 0.7, 1.3)
    sfx(T_SOCK2_0 + 0.1, "shine", 0.7, 1.2)
    sfx(T_SOCK2_1, "pop", 0.6, 1.3)
    sfx(T_SOCK2_1 + 0.1, "cheer", 0.5, 1.5)
    sfx(T_GASP, "gasp", 0.6, 1.1)
    sfx(T_BRIEFS0, "whoosh", 0.4, 1.3)
    sfx(T_BRIEFS1, "plop", 0.7, 1.0)
    sfx(T_BRIEFS1 + 0.15, "blip_down", 0.6, 0.9)
    for k in range(5):
        sfx(T_LEAVE0 + k * 0.27, "hop", 0.35, 1.5)
    sfx(T_LEAVE1 - 0.2, "deflate", 0.4, 0.8)
