"""Grumpo & Nibbo — Episode 9: One Umbrella (rainy bus stop, co-operation structure, 60 fps).

Pouring rain at a bus stop. Grumpo stands dry under his red-and-white umbrella; Nibbo dashes in
soaked. Nibbo scoots under the edge -> Grumpo tilts it away. Nibbo snuggles in -> Grumpo hip-bumps him
out and tips the umbrella so the whole gutter of rainwater pours onto Nibbo's head.
A gust flips the umbrella inside out, lifts Grumpo off the ground and drops him into the puddle.
Co-operation: Nibbo springs into the inverted canopy, his weight pops it back into shape, and
Grumpo (grudgingly) shares. Both dry, a little heart... then the bus arrives, hits the road puddle
and a giant wave buries them both. The bus doesn't even stop. The rain stops, the sun comes out,
a rainbow appears — and when Grumpo flips his (again inverted, water-filled) umbrella back,
the whole cup of water dumps on his own head. Nobody stays dry: both lose.
"""
import math, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow, sun
from hook import overlay, hook_title

W, H, FPS, DUR = 1080, 1920, 60, 15.0
GS = 0.92
GR = 130 * GS            # ~120
NR = 112
FOOT = 1500              # where both balls stand (sidewalk)
GX = 650
ROAD_TOP, ROAD_BOT = 1150, 1362
PUD_X, PUD_Y = 640, 1342  # road puddle
SPUD_X, SPUD_Y = 610, 1510  # sidewalk puddle at their feet
STOP_X = 300
UR = 215                 # umbrella canopy half width
UF = -340                # ferrule (shaft end) in umbrella local coords

# key times
T_ARR = 0.35
T_BUMP = 2.3
T_TILT = 2.45
T_STREAM0, T_STREAM1 = 2.6, 3.6
T_GUST = 4.0
T_FLIP = 4.12
T_LIFT0, T_LIFT1 = 4.3, 4.8
T_SPLASH = 5.12
T_JUMP0, T_JUMP1 = 6.3, 6.65
T_POP = 7.25
T_NLAND = 7.62
T_SHARE0, T_SHARE1 = 8.0, 8.3
T_GLOW = 8.55
T_HONK = 8.95
T_BUS = 9.6              # front wheel reaches the road puddle
T_CRASH = 10.05
T_DRAIN0, T_DRAIN1 = 10.2, 10.55
T_SHAKE = 11.0
T_STOP = 11.45           # rain stops
T_CLEAR0, T_CLEAR1 = 11.55, 12.3
T_DUMP = 12.95
T_HIT = 13.37

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


def heart(x, y, p, s=1.0):
    if p <= 0 or p >= 1:
        return ""
    sc = s * min(1, p * 5) * (1 + 0.2 * math.sin(p * 20))
    op = 1 if p < 0.75 else (1 - p) / 0.25
    return (f'<g transform="translate({x:.1f} {y - 60*p:.1f}) scale({sc:.2f})" opacity="{op:.2f}">'
            f'<path d="M0 22 C -40 -6 -30 -40 0 -18 C 30 -40 40 -6 0 22Z" fill="#ff5a7a" stroke="{OL}" stroke-width="5" stroke-linejoin="round"/>'
            '<ellipse cx="-12" cy="-14" rx="6" ry="4" fill="#fff" opacity="0.7"/></g>')


def drop(x, y, s=1.0, op=1.0, col="#8fd3ff"):
    return (f'<path d="M{x:.1f} {y-14*s:.1f} Q {x+9*s:.1f} {y:.1f} {x:.1f} {y+6*s:.1f} Q {x-9*s:.1f} {y:.1f} {x:.1f} {y-14*s:.1f}Z" '
            f'fill="{col}" stroke="#2a5a8a" stroke-width="{2.5*s:.1f}" opacity="{op:.2f}"/>')


# ---------------------------------------------------------------- umbrella
def rot(px, py, a):
    r = math.radians(a)
    return px * math.cos(r) - py * math.sin(r), px * math.sin(r) + py * math.cos(r)


def umb_geom(hx, hy, a, inv):
    rim_y = UF + 150 * (1 - 2 * inv) if inv < 1 else UF - 150
    rim_y = UF + lerp(150, -95, inv)
    rx = UR * (1 - 0.14 * inv)

    def w(px, py):
        dx, dy = rot(px, py, a)
        return hx + dx, hy + dy
    return dict(rim_y=rim_y, rx=rx, left=w(-rx, rim_y), right=w(rx, rim_y), mid=w(0, rim_y),
                tip=w(0, UF), cup=w(0, UF - 30), w=w)


def umbrella(ctx, hx, hy, a, inv, full=0.0, dump=0.0):
    g = umb_geom(hx, hy, a, inv)
    rim_y, rx = g["rim_y"], g["rx"]
    c = (UF - 0.25 * rim_y) / 0.75
    dome = f"M{-rx:.1f} {rim_y:.1f} C {-rx*0.95:.1f} {c:.1f} {rx*0.95:.1f} {c:.1f} {rx:.1f} {rim_y:.1f}"
    n = 6
    xs = [rx - k * 2 * rx / n for k in range(n + 1)]
    bulge = 26 * (1 - 2 * inv)
    scal = "".join(f" Q {(xs[k]+xs[k+1])/2:.1f} {rim_y - bulge:.1f} {xs[k+1]:.1f} {rim_y:.1f}" for k in range(n))
    shape = dome + scal + "Z"
    cid = ctx.uid("um")
    ctx.defs.append(f'<clipPath id="{cid}"><path d="{shape}"/></clipPath>')
    o = [f'<g transform="translate({hx:.1f} {hy:.1f}) rotate({a:.2f})">']
    # shaft + J handle
    o.append(f'<path d="M0 {UF} V0 v26 q0 26 -26 26 q-22 0 -22 -20" fill="none" stroke="{OL}" stroke-width="16" stroke-linecap="round"/>'
             f'<path d="M0 {UF} V0 v26 q0 26 -26 26 q-22 0 -22 -20" fill="none" stroke="#8a5a3a" stroke-width="8" stroke-linecap="round"/>')
    # canopy panels
    panels = []
    cols = ["#e8434f", "#fbf3ea"]
    xs2 = [-rx * 1.5 + k * 3 * rx / n for k in range(n + 1)]
    for k in range(n):
        y0 = rim_y + (rim_y - UF) * 0.8
        panels.append(f'<path d="M0 {UF} L{xs2[k]:.1f} {y0:.1f} L{xs2[k+1]:.1f} {y0:.1f}Z" fill="{cols[k % 2]}"/>')
    inner = "#b62a3a" if inv > 0.5 else None
    o.append(f'<g clip-path="url(#{cid})"><rect x="{-rx-20:.1f}" y="{min(UF, rim_y)-200:.1f}" width="{2*rx+40:.1f}" height="420" fill="#fbf3ea"/>'
             + "".join(panels) +
             # two-tone shade on the lower side
             f'<path d="{dome} L{rx:.1f} {rim_y+200:.1f} L{-rx:.1f} {rim_y+200:.1f}Z" fill="#000" opacity="0"/>'
             f'<ellipse cx="{rx*0.45:.1f}" cy="{rim_y:.1f}" rx="{rx*0.75:.1f}" ry="{abs(rim_y-UF)*0.55+10:.1f}" fill="#5a0f2a" opacity="0.16"/>')
    if inv > 0.5 and full > 0.01:
        wl = lerp(UF + 6, rim_y + 22, full)
        o.append(f'<rect x="{-rx-10:.1f}" y="{wl:.1f}" width="{2*rx+20:.1f}" height="{UF-wl+30:.1f}" fill="#5cb8ec" opacity="0.95"/>'
                 f'<path d="M{-rx:.1f} {wl:.1f} H{rx:.1f}" stroke="#e9fbff" stroke-width="8"/>')
    o.append('</g>')
    if inner:
        pass
    o.append(f'<path d="{shape}" fill="none" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>')
    # ribs
    rib = "".join(f'<path d="M0 {UF} Q {xk*0.55:.1f} {lerp(UF, rim_y, 0.25) - 18*(1-2*inv):.1f} {xk:.1f} {rim_y:.1f}" fill="none" stroke="{OL}" stroke-width="3" opacity="0.55"/>'
                  for xk in xs[1:-1])
    o.append(rib)
    for xk in xs:
        ex = xk * (1 + 0.08 * inv)
        ey = rim_y - 22 * inv
        o.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="6" fill="#d8d8e0" stroke="{OL}" stroke-width="3"/>')
    # highlight
    if inv < 0.5:
        o.append(f'<path d="M{-rx*0.62:.1f} {lerp(UF, rim_y, 0.55):.1f} Q {-rx*0.4:.1f} {lerp(UF, rim_y, 0.05):.1f} {-rx*0.05:.1f} {UF+12:.1f}" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" opacity="0.55"/>')
    # ferrule
    o.append(f'<path d="M0 {UF} v-22" stroke="{OL}" stroke-width="10" stroke-linecap="round"/><circle cx="0" cy="{UF-24}" r="7" fill="#d8d8e0" stroke="{OL}" stroke-width="3"/>')
    o.append('</g>')
    return "".join(o), g


# ---------------------------------------------------------------- scene
rnd = random.Random(9)
BLD = []
x = -500
while x < 1700:
    w = rnd.uniform(150, 260)
    h = rnd.uniform(170, 400)
    BLD.append((x, w, h, rnd.choice(["#6d7d98", "#7889a3", "#62728c", "#8392ab"]), rnd.random()))
    x += w + rnd.uniform(-20, 30)
BLD2 = []
x = -560
while x < 1800:
    w = rnd.uniform(200, 320)
    h = rnd.uniform(60, 220)
    BLD2.append((x, w, h, rnd.choice(["#58678a", "#4f5e7e", "#5d6c8e"]), rnd.random()))
    x += w + rnd.uniform(0, 40)
WIN_LIT = [[rnd.random() < 0.35 for _ in range(40)] for _ in range(60)]


def sky_layer(t, clear):
    o = ['<rect x="-900" y="-600" width="3000" height="2400" fill="url(#rainSky)"/>']
    if clear > 0:
        o.append(f'<rect x="-900" y="-600" width="3000" height="2400" fill="url(#sky2)" opacity="{clear:.3f}"/>')
        o.append(f'<g opacity="{clear:.3f}">{sun(930, 760 - 120*eout(clear))}</g>')
    return "".join(o)


def rainbow(t):
    rb = seg(t, 12.0, 12.7)
    if rb <= 0:
        return ""
    cols = ["#ff5a5a", "#ffa63a", "#ffe24a", "#6fd36a", "#4ab0ff", "#8a6ae8"]
    arcs = "".join(f'<path d="M{610-(360-k*20)} 1150 A {360-k*20} {330-k*20} 0 0 1 {610+(360-k*20)} 1150" fill="none" stroke="{c}" stroke-width="21"/>'
                   for k, c in enumerate(cols))
    return f'<g opacity="{0.7*rb:.2f}">{arcs}</g>'


def clouds(t, clear):
    o = []
    rr = random.Random(4)
    for k in range(9):
        cx = -260 + k * 210 + rr.uniform(-40, 40) + 14 * math.sin(t * 0.4 + k)
        cy = 640 + rr.uniform(-60, 90)
        s = rr.uniform(0.9, 1.4)
        side = -1 if cx < 560 else 1
        cx += side * 900 * ein(clear)
        op = 1 - clear
        if op <= 0:
            continue
        puffs = [(-90, 20, 70), (-30, -20, 90), (50, -30, 96), (120, 10, 72), (0, 40, 80)]
        o.append(f'<g opacity="{op:.2f}">' + "".join(
            f'<circle cx="{cx+dx*s:.0f}" cy="{cy+dy*s:.0f}" r="{r*s:.0f}" fill="{"#5c6884" if dy > 0 else "#727e9a"}"/>' for dx, dy, r in puffs) + '</g>')
    return "".join(o)


def buildings(t, clear):
    o = []
    for (x0, w, h, c, r) in BLD2:
        o.append(f'<rect x="{x0:.0f}" y="{ROAD_TOP-90-h-260:.0f}" width="{w:.0f}" height="{h+300:.0f}" fill="{mix_hex(c, "#9ab8d8", clear*0.5)}"/>')
    for i, (x0, w, h, c, r) in enumerate(BLD):
        top = ROAD_TOP - 30 - h
        col = mix_hex(c, "#a8bcd8", clear * 0.55)
        o.append(f'<rect x="{x0:.0f}" y="{top:.0f}" width="{w:.0f}" height="{h+40:.0f}" fill="{col}" stroke="{OL}" stroke-width="4"/>')
        o.append(f'<rect x="{x0:.0f}" y="{top:.0f}" width="{w*0.25:.0f}" height="{h+40:.0f}" fill="#000" opacity="0.08"/>')
        # roof cap
        o.append(f'<rect x="{x0-6:.0f}" y="{top-14:.0f}" width="{w+12:.0f}" height="18" fill="{mix_hex(col, "#222222", 0.25)}" stroke="{OL}" stroke-width="4"/>')
        cols = max(2, int(w // 58))
        rows = max(2, int(h // 80))
        for rr_ in range(rows):
            for cc in range(cols):
                wx = x0 + 18 + cc * (w - 36) / cols
                wy = top + 26 + rr_ * 80
                lit = WIN_LIT[i % 60][(rr_ * cols + cc) % 40]
                wc = mix_hex("#ffd98a", "#cfe6ff", clear) if lit else mix_hex("#3e4a62", "#6f8fb8", clear)
                o.append(f'<rect x="{wx:.0f}" y="{wy:.0f}" width="{(w-36)/cols-14:.0f}" height="44" rx="4" fill="{wc}"/>')
    return "".join(o)


def road(t, clear):
    o = [f'<rect x="-900" y="{ROAD_TOP}" width="3000" height="{ROAD_BOT-ROAD_TOP}" fill="{mix_hex("#4a4f5e", "#5e6474", clear)}"/>',
         f'<rect x="-900" y="{ROAD_TOP-8}" width="3000" height="14" fill="#9a9aa8" stroke="{OL}" stroke-width="4"/>']
    for k in range(-8, 20):
        o.append(f'<rect x="{k*180}" y="{(ROAD_TOP+ROAD_BOT)//2-8}" width="100" height="14" rx="4" fill="#e8e4cf" opacity="0.85"/>')
    # wet sheen streaks
    for k in range(-6, 14):
        o.append(f'<path d="M{k*140+30} {ROAD_TOP+40+(k%3)*40} h{60+(k%2)*40}" stroke="#8a93ab" stroke-width="5" stroke-linecap="round" opacity="{0.45*(1-clear)+0.1:.2f}"/>')
    # road puddle (empties when the bus hits it)
    pk = 1 - 0.7 * seg(t, T_BUS, T_BUS + 0.15)
    o.append(f'<ellipse cx="{PUD_X}" cy="{PUD_Y}" rx="{240*pk:.0f}" ry="{17*pk:.0f}" fill="#7d9cc6" stroke="{OL}" stroke-width="4"/>'
             f'<path d="M{PUD_X-150*pk:.0f} {PUD_Y-4} h{110*pk:.0f}" stroke="#d8ecff" stroke-width="5" stroke-linecap="round"/>')
    return "".join(o)


def bus(bx, t):
    """city bus, facing left; bx = front x."""
    y0, y1 = 930, 1318
    L_ = 1000
    o = [f'<g>']
    # body
    o.append(f'<path d="M{bx+40} {y0} H{bx+L_-20} Q {bx+L_} {y0} {bx+L_} {y0+30} V{y1} H{bx} V{y0+110} Q {bx} {y0} {bx+40} {y0}Z" fill="#2bb3a3" stroke="{OL}" stroke-width="7"/>')
    o.append(f'<rect x="{bx+4}" y="{y1-120}" width="{L_-8}" height="34" fill="#f4efe0"/>')
    o.append(f'<rect x="{bx+4}" y="{y1-46}" width="{L_-8}" height="42" fill="#1f8a7e"/>')
    # windshield + windows
    o.append(f'<path d="M{bx+10} {y0+30} Q {bx+14} {y0+10} {bx+46} {y0+10} H{bx+110} V{y0+170} H{bx+10}Z" fill="#3c5470" stroke="{OL}" stroke-width="5"/>')
    for k in range(6):
        wx = bx + 250 + k * 122
        o.append(f'<rect x="{wx}" y="{y0+28}" width="104" height="128" rx="10" fill="#3c5470" stroke="{OL}" stroke-width="5"/>'
                 f'<path d="M{wx+14} {y0+120} L{wx+60} {y0+44}" stroke="#9fc0e0" stroke-width="8" stroke-linecap="round" opacity="0.6"/>')
    # door
    o.append(f'<rect x="{bx+128}" y="{y0+30}" width="100" height="{y1-y0-54}" rx="6" fill="#4a6a88" stroke="{OL}" stroke-width="5"/>'
             f'<path d="M{bx+178} {y0+30} V{y1-24}" stroke="{OL}" stroke-width="4"/>')
    # route display (lit dots, no text)
    o.append(f'<rect x="{bx+20}" y="{y0-0}" width="80" height="0" fill="none"/>')
    o.append(f'<rect x="{bx+260}" y="{y0-2}" width="300" height="0" fill="none"/>')
    # headlight + bumper
    o.append(f'<circle cx="{bx+22}" cy="{y1-70}" r="20" fill="#fff3a8" stroke="{OL}" stroke-width="4"/>'
             f'<rect x="{bx-10}" y="{y1-26}" width="60" height="22" rx="6" fill="#9a9aa8" stroke="{OL}" stroke-width="4"/>'
             f'<circle cx="{bx+L_-14}" cy="{y1-70}" r="14" fill="#ff4a3a" stroke="{OL}" stroke-width="4"/>')
    # wheels
    for wx in (bx + 175, bx + L_ - 190):
        spin = (t * 900) % 360
        o.append(f'<circle cx="{wx}" cy="{y1+6}" r="50" fill="#2a2a33" stroke="{OL}" stroke-width="5"/>'
                 f'<circle cx="{wx}" cy="{y1+6}" r="22" fill="#b8bcc8" stroke="{OL}" stroke-width="4"/>'
                 f'<path d="M{wx-16} {y1+6} h32" stroke="{OL}" stroke-width="5" transform="rotate({-spin:.0f} {wx} {y1+6})"/>')
    o.append('</g>')
    return "".join(o)


def bus_x(t):
    return 470 - 900 * (t - T_BUS)


def sidewalk(t, clear):
    o = [f'<rect x="-900" y="{ROAD_BOT-6}" width="3000" height="30" fill="#b8b6c4" stroke="{OL}" stroke-width="5"/>',
         f'<rect x="-900" y="{ROAD_BOT+24}" width="3000" height="1200" fill="{mix_hex("#a9a6b8", "#cbc6d4", clear)}"/>']
    for y in (ROAD_BOT + 90, ROAD_BOT + 190, ROAD_BOT + 320, ROAD_BOT + 480):
        o.append(f'<path d="M-900 {y} H2100" stroke="#8d8a9e" stroke-width="4"/>')
    for k in range(-8, 18):
        o.append(f'<path d="M{k*170} {ROAD_BOT+24} V{ROAD_BOT+600}" stroke="#8d8a9e" stroke-width="4"/>')
    # wet shine
    o.append(f'<rect x="-900" y="{ROAD_BOT+24}" width="3000" height="60" fill="#e8f2ff" opacity="{0.15*(1-clear):.2f}"/>')
    return "".join(o)


def foreground(t, clear):
    o = []
    # storm drain grate
    gx, gy = 880, 1650
    o.append(f'<rect x="{gx-90}" y="{gy-26}" width="180" height="52" rx="8" fill="#3a3a48" stroke="{OL}" stroke-width="5"/>')
    for k in range(7):
        o.append(f'<rect x="{gx-76+k*22}" y="{gy-16}" width="12" height="32" rx="4" fill="#15151c"/>')
    # small puddle with ripples
    px, py = 330, 1680
    o.append(f'<ellipse cx="{px}" cy="{py}" rx="120" ry="16" fill="#86a6cf" stroke="{OL}" stroke-width="4"/>')
    a = rain_amt(t)
    for k in range(2):
        p = (t * 1.4 + k * 0.5) % 1
        o.append(f'<ellipse cx="{px - 30 + 60*k}" cy="{py}" rx="{10+60*p:.0f}" ry="{3+8*p:.0f}" fill="none" stroke="#e3efff" stroke-width="3" opacity="{a*(1-p):.2f}"/>')
    # fallen leaves
    o.append(f'<g transform="translate(560 1720) rotate(20)"><path d="M-26 0 Q 0 -18 26 0 Q 0 18 -26 0Z" fill="#e8a23a" stroke="{OL}" stroke-width="3"/></g>'
             f'<g transform="translate(160 1600) rotate(-30)"><path d="M-20 0 Q 0 -14 20 0 Q 0 14 -20 0Z" fill="#d8762a" stroke="{OL}" stroke-width="3"/></g>')
    return "".join(o)


def stop_sign():
    x = STOP_X
    return (f'<rect x="{x-11}" y="1050" width="22" height="{FOOT+30-1050}" rx="5" fill="#9aa0ae" stroke="{OL}" stroke-width="5"/>'
            f'<g transform="translate({x} 1050)"><circle r="66" fill="#2f74d0" stroke="{OL}" stroke-width="6"/><circle r="52" fill="#ffffff"/>'
            f'<rect x="-34" y="-30" width="68" height="50" rx="10" fill="#2bb3a3" stroke="{OL}" stroke-width="4"/>'
            f'<rect x="-26" y="-22" width="22" height="18" rx="3" fill="#cfe6ff"/><rect x="2" y="-22" width="24" height="18" rx="3" fill="#cfe6ff"/>'
            f'<circle cx="-18" cy="24" r="8" fill="{OL}"/><circle cx="18" cy="24" r="8" fill="{OL}"/></g>')


def side_puddle(t, clear):
    big = 1 + 0.25 * seg(t, T_DRAIN0, T_DRAIN1)
    o = [f'<ellipse cx="{SPUD_X}" cy="{SPUD_Y}" rx="{300*big:.0f}" ry="{28*big:.0f}" fill="#86a6cf" stroke="{OL}" stroke-width="4"/>']
    if clear > 0.3:
        cols = ["#ff5a5a", "#ffe24a", "#6fd36a", "#4ab0ff"]
        o.append(f'<g opacity="{(clear-0.3)/0.7*0.55:.2f}">' + "".join(
            f'<path d="M{SPUD_X-200+k*18} {SPUD_Y+10} q 120 -26 240 0" fill="none" stroke="{c}" stroke-width="7"/>' for k, c in enumerate(cols)) + '</g>')
    o.append(f'<path d="M{SPUD_X-220*big:.0f} {SPUD_Y-8} h{120*big:.0f}" stroke="#e1f1ff" stroke-width="6" stroke-linecap="round"/>')
    return "".join(o)


# ---------------------------------------------------------------- rain
rr = random.Random(77)
DROPS = [(rr.uniform(-250, 1350), rr.uniform(0, 1500), rr.uniform(0.85, 1.15), k % 3 == 0) for k in range(210)]
TICKS = [(rr.uniform(0, 1100), rr.uniform(ROAD_BOT + 40, 1700), rr.uniform(0, 1)) for _ in range(28)]


def rain_amt(t):
    return 1 - seg(t, T_STOP, T_STOP + 0.3)


def wind_ang(t):
    return kf(t, [(3.95, 9), (4.15, 38), (4.85, 38), (5.1, 9)])


def rain(t, front, cover):
    a = rain_amt(t)
    if a <= 0:
        return ""
    ang = math.radians(wind_ang(t))
    o = []
    for (x0, y0, sp, fr) in DROPS:
        if fr != front:
            continue
        y = 450 + (y0 + t * 2300 * sp) % 1500
        x = x0 + (y - 450) * math.tan(ang) - 400 * math.tan(ang)
        dx, dy = 48 * math.sin(ang), 48 * math.cos(ang)
        if cover is not None:
            (cx0, cx1, cy) = cover
            if cx0 < x < cx1 and y > cy - 30:
                continue
        if front and y > FOOT + 60:
            continue
        o.append(f'<path d="M{x:.0f} {y:.0f} l{dx:.0f} {dy:.0f}" stroke="#dbeaff" stroke-width="{4 if front else 3}" stroke-linecap="round" opacity="{a*(0.7 if front else 0.5):.2f}"/>')
    if not front:
        for (x0, y0, ph) in TICKS:
            p = (t * 2.2 + ph) % 1
            if p < 0.35:
                q = p / 0.35
                o.append(f'<path d="M{x0-14*q:.0f} {y0-10*q:.0f} l{6*q:.1f} {9*q:.1f} M{x0+14*q:.0f} {y0-10*q:.0f} l{-6*q:.1f} {9*q:.1f}" stroke="#e3efff" stroke-width="3" stroke-linecap="round" opacity="{a*(1-q)*0.8:.2f}"/>'
                         f'<ellipse cx="{x0:.0f}" cy="{y0:.0f}" rx="{20*q:.0f}" ry="{5*q:.0f}" fill="none" stroke="#e3efff" stroke-width="2.5" opacity="{a*(1-q)*0.6:.2f}"/>')
    return "".join(o)


def wetness(x, y, r, t, amount, sx=1.0, sy=1.0):
    """drips running off a wet character + glossy streaks."""
    if amount <= 0:
        return ""
    o = []
    for k in range(3):
        p = (t * 1.3 + k * 0.37) % 1
        dx = (k - 1) * r * 0.55 * sx
        yy = y + r * sy * (0.92 - 0.25 * abs(k - 1)) + p * 110
        o.append(drop(x + dx, yy, 0.9, amount * (1 - p)))
    o.append(f'<path d="M{x + r*0.5*sx:.0f} {y - r*0.55*sy:.0f} q {r*0.18:.0f} {r*0.25:.0f} {r*0.12:.0f} {r*0.55:.0f}" fill="none" stroke="#e8f6ff" stroke-width="6" stroke-linecap="round" opacity="{0.7*amount:.2f}"/>')
    o.append(f'<path d="M{x - r*0.75*sx:.0f} {y + r*0.05*sy:.0f} q {-r*0.05:.0f} {r*0.25:.0f} {r*0.06:.0f} {r*0.45:.0f}" fill="none" stroke="#e8f6ff" stroke-width="5" stroke-linecap="round" opacity="{0.55*amount:.2f}"/>')
    return "".join(o)


# ---------------------------------------------------------------- states
def umb_state(t):
    a = kf(t, [(0, -27), (1.35, -27), (1.55, 2), (T_TILT, 2), (T_TILT + 0.15, -34), (T_STREAM1, -34), (3.85, -27),
               (T_GUST, -27), (4.12, 12), (4.4, -6), (4.6, 14), (4.85, 0), (T_SPLASH, -6), (T_POP, -6), (7.6, -12),
               (T_SHARE0, -12), (T_SHARE1, -27), (T_CRASH, -27), (T_CRASH + 0.1, -8), (12.6, -8), (T_DUMP - 0.03, 22)])
    inv = 0.0
    if t >= T_FLIP:
        inv = eout(seg(t, T_FLIP, T_FLIP + 0.1))
    if t >= T_POP:
        inv = 1 - eout(seg(t, T_POP, T_POP + 0.09))
    if t >= T_CRASH + 0.03:
        inv = eout(seg(t, T_CRASH + 0.03, T_CRASH + 0.12))
    if t >= T_DUMP:
        inv = 1 - eout(seg(t, T_DUMP, T_DUMP + 0.1))
    raise_ = kf(t, [(T_TILT, 0), (T_TILT + 0.15, 190), (T_STREAM1, 190), (3.85, 0),
                    (T_JUMP1 - 0.02, 0), (T_JUMP1 + 0.08, -55), (T_POP, -55), (T_POP + 0.12, 0),
                    (T_SHARE0, 0), (T_SHARE1, 50), (T_CRASH, 50), (T_CRASH + 0.1, 0)])
    full = 1.0 if (T_DRAIN0 <= t < T_DUMP) else 0.0
    if T_CRASH + 0.1 <= t < T_DRAIN0:
        full = 1.0
    # sway while lifted
    if T_FLIP <= t < T_SPLASH:
        a += 6 * math.sin(t * 17)
    return dict(a=a, inv=inv, raise_=raise_, full=full)


def grumpo_state(t):
    g = dict(x=GX, b=FOOT, ex="smug", look=(-0.3, -0.2), sx=1.0, sy=1.0, rot=0.0, wet=0.0, red=0.0)
    g["x"] += kf(t, [(T_BUMP - 0.08, 0), (T_BUMP, -40), (T_BUMP + 0.18, 0)])
    if T_BUMP - 0.08 <= t < T_BUMP + 0.18:
        g["rot"] = -12 * math.sin(math.pi * seg(t, T_BUMP - 0.08, T_BUMP + 0.18))
    # lift by the gust
    if T_LIFT0 <= t < T_LIFT1:
        p = seg(t, T_LIFT0, T_LIFT1)
        g["b"] = FOOT - 250 * eout(p)
        g["rot"] = 10 * math.sin(t * 14)
        g["sy"] = 1.12
        g["sx"] = 0.92
    elif T_LIFT1 <= t < T_SPLASH:
        p = seg(t, T_LIFT1, T_SPLASH)
        g["b"] = lerp(FOOT - 250, FOOT, ein(p))
        g["sy"] = 1.1
        g["sx"] = 0.94
    elif T_FLIP <= t < T_LIFT0:
        g["b"] = FOOT - 30 * seg(t, T_FLIP, T_LIFT0)
        g["sy"] = 1 + 0.1 * seg(t, T_FLIP, T_LIFT0)
    a, b = squash(t, T_SPLASH, 0.35, 0.3)
    g["sx"] *= a
    g["sy"] *= b
    # weight of Nibbo in the cup
    if T_JUMP1 <= t < T_POP + 0.15:
        k = seg(t, T_JUMP1, T_JUMP1 + 0.12)
        q = 1 - seg(t, T_POP, T_POP + 0.15)
        g["sy"] *= 1 - 0.13 * k * q
        g["sx"] *= 1 + 0.08 * k * q
    # flattened by the wave
    if T_CRASH <= t:
        fl = kf(t, [(T_CRASH, 1.0), (T_CRASH + 0.08, 0.74), (11.1, 0.74), (11.3, 1.04), (11.45, 1.0)])
        g["sy"] *= fl
        g["sx"] *= 1 + (1 - fl) * 0.6
    # dumped on
    if t >= T_HIT:
        fl = kf(t, [(T_HIT, 1.0), (T_HIT + 0.12, 0.74), (14.1, 0.74), (14.35, 0.9)])
        g["sy"] *= fl
        g["sx"] *= 1 + (1 - fl) * 0.55
    g["wet"] = 1.0 if t >= T_SPLASH else 0.0
    g["ex"] = pick(t, [(0, "smug"), (1.3, "suspicious"), (1.6, "smug"), (2.0, "suspicious"), (T_BUMP, "smug"), (T_GUST + 0.05, "shock"),
                       (T_SPLASH + 0.2, "grumpy"), (5.45, "angry"), (6.1, "grumpy"), (T_JUMP1, "shock"), (T_POP + 0.2, "suspicious"),
                       (T_SHARE0 + 0.05, "smug"), (9.0, "grumpy"), (9.68, "shock"), (T_DRAIN1, "shock"), (11.2, "grumpy"),
                       (11.9, "suspicious"), (12.6, "smug"), (T_DUMP + 0.05, "shock"), (13.9, "angry"), (14.5, "grumpy")], "smug")
    g["look"] = pick(t, [(0, (-0.3, -0.2)), (1.3, (-1, 0)), (1.6, (0.2, -0.3)), (2.0, (-1, 0)), (T_BUMP + 0.2, (-0.8, 0.2)),
                         (3.7, (0, -0.3)), (T_GUST, (0, -1)), (T_SPLASH, (0, 0.3)), (5.45, (-1, 0)), (6.1, (-0.6, -0.8)),
                         (T_POP + 0.2, (-1, 0)), (T_SHARE0 + 0.05, (-0.5, -0.3)), (8.6, (1, 0)), (9.68, (0.3, -1)),
                         (T_DRAIN1, (0, 0)), (11.2, (-0.6, 0.2)), (11.9, (0, -1)), (12.6, (0.8, -0.4)), (T_DUMP + 0.05, (-0.2, -1)), (T_HIT, (0, 0)),
                         (13.9, (-1, 0)), (14.5, (0, 0.2))], (0, 0))
    g["y"] = g["b"] - GR * g["sy"]
    return g


def hand_pos(g, u):
    return g["x"] + 122 * g["sx"], g["y"] - 5 - u["raise_"] + 10 * (g["sy"] - 1)


def _stream_x():
    hx, hy = GX + 122, FOOT - GR - 5 - 190
    return umb_geom(hx, hy, -34, 0.0)["left"][0] + 6


X_STREAM = _stream_x()


def nibbo_state(t, g, u):
    n = dict(x=420, b=FOOT, ex="nervous", rot=0.0, sx=1.0, sy=1.0, wet=0.7, hang=False)
    n["x"] = kf(t, [(0, -200), (T_ARR, 405), (0.95, 405), (1.2, 470), (1.72, 470), (1.92, 535), (T_BUMP, 535), (T_BUMP + 0.16, X_STREAM),
                    (T_STREAM1, X_STREAM), (3.9, 415), (T_GUST, 415), (4.6, 385), (6.0, 385)])
    if t < T_ARR:
        n["rot"] = 18
        n["sx"], n["sy"] = 1.12, 0.92
    a_, b_ = squash(t, T_ARR, 0.3, 0.25)
    n["sx"] *= a_
    n["sy"] *= b_
    # hops (scoot & snuggle)
    for t0, t1, h in [(0.95, 1.2, 50), (1.72, 1.92, 60), (T_BUMP, T_BUMP + 0.16, 30), (3.6, 3.9, 40)]:
        if t0 <= t < t1:
            n["b"] -= h * math.sin(math.pi * seg(t, t0, t1))
    if 1.92 <= t < T_BUMP:
        n["sx"] *= 0.9
        n["sy"] *= 1.05
    # stream squash
    if T_STREAM0 <= t < T_STREAM1:
        k = seg(t, T_STREAM0, T_STREAM0 + 0.12)
        n["sy"] *= 1 - 0.2 * k + 0.03 * math.sin(t * 40)
        n["sx"] *= 1 + 0.12 * k
    # blown by the gust
    if T_GUST <= t < 5.1:
        k = math.sin(math.pi * seg(t, T_GUST, 5.1))
        n["rot"] = -14 * k + 3 * math.sin(t * 30) * k
        n["sx"] *= 1 - 0.08 * k
    # laughing
    if 5.3 <= t < 5.75:
        n["b"] -= 18 * abs(math.sin((t - 5.3) * 22))
    # jump into the inverted cup
    um, ug = None, None
    hx, hy = hand_pos(g, u)
    geo = umb_geom(hx, hy, u["a"], u["inv"])
    cupx, cupy = geo["cup"]
    if T_JUMP0 <= t < T_JUMP1:
        p = seg(t, T_JUMP0, T_JUMP1)
        n["x"] = lerp(385, cupx, p)
        n["b"] = lerp(FOOT, cupy, p) - 260 * 4 * p * (1 - p)
        n["sy"] *= 1.1
        n["sx"] *= 0.93
    elif T_JUMP1 <= t < T_POP:
        n["x"], n["b"] = cupx, cupy + 8
        a_, b_ = squash(t, T_JUMP1, 0.3, 0.2)
        n["sx"] *= a_
        n["sy"] *= b_
        n["rot"] = 4 * math.sin((t - T_JUMP1) * 9)
    elif T_POP <= t < T_NLAND:
        p = seg(t, T_POP, T_NLAND)
        x0, y0 = 600, 1000
        n["x"] = lerp(x0, 500, p)
        n["b"] = lerp(y0, FOOT, ein(p)) - 160 * math.sin(math.pi * p) * (1 - p)
        n["rot"] = -200 * p
    elif t >= T_NLAND:
        n["x"] = kf(t, [(T_NLAND, 500), (T_SHARE0, 500), (T_SHARE1, 505)])
        a_, b_ = squash(t, T_NLAND, 0.3, 0.24)
        n["sx"] *= a_
        n["sy"] *= b_
        if t >= T_SHARE1 - 0.1 and t < T_CRASH:
            n["sx"] *= 0.9
            n["sy"] *= 1.04
    if T_POP <= t < T_POP + 0.02:
        pass
    # happy bus hops
    if 9.12 <= t < 9.5:
        n["b"] -= 40 * abs(math.sin(math.pi * seg(t, 9.12, 9.5) * 2))
    # wave flatten
    if t >= T_CRASH:
        fl = kf(t, [(T_CRASH, 1.0), (T_CRASH + 0.08, 0.72), (T_SHAKE, 0.72), (T_SHAKE + 0.12, 1.0)])
        n["sy"] *= fl
        n["sx"] *= 1 + (1 - fl) * 0.6
    if T_SHAKE <= t < T_SHAKE + 0.4:
        n["rot"] = 16 * math.sin((t - T_SHAKE) * 55)
    # final giggle
    if 13.55 <= t < 14.8:
        k = t - 13.55
        n["b"] -= 22 * abs(math.sin(k * 11))
        n["rot"] = 6 * math.sin(k * 11)
    n["wet"] = 0.7 if t < T_STREAM0 else 1.0
    if T_SHARE1 <= t < T_CRASH:
        n["wet"] = 0.5
    n["ex"] = pick(t, [(0, "nervous"), (T_ARR + 0.1, "uhoh"), (0.95, "happy"), (1.5, "uhoh"), (1.72, "happy"), (T_BUMP, "wow"),
                       (T_STREAM0, "dizzy"), (T_STREAM1, "uhoh"), (T_GUST, "nervous"), (T_SPLASH, "wow"), (5.3, "joy"),
                       (5.55, "uhoh"), (6.0, "happy"), (T_JUMP0, "joy"), (T_JUMP1, "happy"), (T_POP, "wow"), (T_NLAND, "joy"),
                       (8.0, "happy"), (9.0, "wow"), (9.12, "joy"), (9.68, "uhoh"), (T_DRAIN1, "dizzy"), (T_SHAKE, "nervous"),
                       (11.45, "uhoh"), (11.9, "wow"), (12.5, "nervous"), (T_DUMP + 0.12, "wow"), (13.55, "joy")], "happy")
    n["y"] = n["b"] - NR * n["sy"]
    return n


# ---------------------------------------------------------------- effects
def stream(t, rim, n):
    if not (T_STREAM0 <= t < T_STREAM1):
        return ""
    k = seg(t, T_STREAM0, T_STREAM0 + 0.1) * (1 - seg(t, T_STREAM1 - 0.1, T_STREAM1))
    x0, y0 = rim
    x1, y1 = n["x"] + 8, n["y"] - NR * n["sy"] + 10
    w0, w1 = 20 * k, 42 * k
    wob = 4 * math.sin(t * 50)
    o = [f'<path d="M{x0-w0:.1f} {y0:.1f} Q {(x0+x1)/2-w0+wob:.1f} {(y0+y1)/2:.1f} {x1-w1:.1f} {y1:.1f} L{x1+w1:.1f} {y1:.1f} Q {(x0+x1)/2+w0-wob:.1f} {(y0+y1)/2:.1f} {x0+w0:.1f} {y0:.1f}Z" '
         f'fill="#6cc3f0" stroke="#2a5a8a" stroke-width="4" opacity="0.95"/>',
         f'<path d="M{x0-4:.1f} {y0+8:.1f} L{x1-10:.1f} {y1-10:.1f}" stroke="#e9fbff" stroke-width="5" stroke-linecap="round" opacity="0.8"/>']
    # splash on head
    for j in range(7):
        p = (t * 3 + j / 7) % 1
        ang = math.radians(-160 + j * 23)
        px = x1 + math.cos(ang) * (40 + 90 * p)
        py = y1 + math.sin(ang) * (30 + 70 * p) + 120 * p * p
        o.append(drop(px, py, 1.0, k * (1 - p)))
    return "".join(o)


rs = random.Random(5)
SPL = [(rs.uniform(-1, 1), rs.uniform(0.5, 1.0), rs.uniform(0.8, 1.3)) for _ in range(16)]


def splash_burst(x, y, t, t0, scale=1.0, d=0.7):
    if not (t0 <= t < t0 + d):
        return ""
    k = t - t0
    o = []
    for (vx, vy, s) in SPL:
        px = x + vx * 520 * k * scale
        py = y - vy * 1100 * k * scale + 2600 * k * k
        if py > y + 20:
            continue
        o.append(drop(px, py, 1.2 * s, 1 - k / d))
    # crown
    p = k / d
    o.append(f'<path d="M{x-170*scale*(0.5+p):.0f} {y} Q {x-120*scale:.0f} {y-130*scale*math.sin(math.pi*min(1,p*1.6)):.0f} {x:.0f} {y-30*scale:.0f} '
             f'Q {x+120*scale:.0f} {y-130*scale*math.sin(math.pi*min(1,p*1.6)):.0f} {x+170*scale*(0.5+p):.0f} {y}Z" fill="#8fd3ff" stroke="#2a5a8a" stroke-width="4" opacity="{1-p:.2f}"/>')
    return "".join(o)


def wave_back(t):
    """water wall rising from the road puddle behind them."""
    if not (T_BUS <= t < T_CRASH + 0.08):
        return ""
    p = eout(seg(t, T_BUS, T_CRASH))
    top = PUD_Y - 600 * p
    x0, x1 = 230 - 120 * p, 1010 + 60 * p
    pts = " ".join(f"L{xx:.0f} {top + 30*math.sin(xx/60 + t*20) + 40*math.sin(xx/170):.0f}" for xx in range(int(x0), int(x1) + 1, 40))
    o = [f'<path d="M{x0:.0f} {PUD_Y+10} {pts} L{x1:.0f} {PUD_Y+10}Z" fill="url(#waveG)" stroke="#2a5a8a" stroke-width="6" opacity="0.96"/>']
    # foam cap
    for k, xx in enumerate(range(int(x0) + 20, int(x1), 55)):
        yy = top + 30 * math.sin(xx / 60 + t * 20) + 40 * math.sin(xx / 170)
        o.append(f'<circle cx="{xx}" cy="{yy:.0f}" r="{22 + 8*(k%3)}" fill="#f2fbff" stroke="#2a5a8a" stroke-width="3"/>')
    for (vx, vy, s) in SPL[:10]:
        o.append(drop(lerp(x0, x1, (vx + 1) / 2), top - 60 * vy * p - 30, 1.4 * s, p))
    return "".join(o)


def wave_front(t):
    """the wall crashes over them: water fills the frame, then drains down."""
    if not (T_CRASH <= t < T_DRAIN1 + 0.15):
        return ""
    if t < T_CRASH + 0.08:
        p = seg(t, T_CRASH, T_CRASH + 0.08)
        top = lerp(PUD_Y - 600, 700, p)
        op = 0.6 + 0.35 * p
    else:
        top = lerp(700, FOOT + 60, ein(seg(t, T_DRAIN0, T_DRAIN1)))
        op = 0.95 * (1 - seg(t, T_DRAIN1, T_DRAIN1 + 0.15))
    pts = " ".join(f"L{xx} {top + 24*math.sin(xx/55 + t*16):.0f}" for xx in range(-200, 1401, 40))
    o = [f'<path d="M-200 1900 L-200 {top:.0f} {pts} L1400 1900Z" fill="url(#waveG)" opacity="{op:.2f}"/>',
         f'<path d="M-200 {top:.0f} {pts}" fill="none" stroke="#f2fbff" stroke-width="16" stroke-linecap="round" opacity="{op:.2f}"/>']
    rb = random.Random(3)
    for k in range(22):
        bx = rb.uniform(150, 1000)
        by = FOOT + 80 - ((t * 420 + rb.uniform(0, 700)) % 800)
        if by > top + 30:
            o.append(f'<circle cx="{bx:.0f}" cy="{by:.0f}" r="{rb.uniform(8, 20):.0f}" fill="none" stroke="#e9fbff" stroke-width="4" opacity="{op*0.8:.2f}"/>')
    return "".join(o)


def _dump_start():
    g = grumpo_state(T_DUMP)
    u = umb_state(T_DUMP - 0.001)
    hx, hy = hand_pos(g, u)
    return umb_geom(hx, hy, u["a"], 1.0)["cup"]


def dump_blob(t, g):
    """the cup of water is flung up when the umbrella snaps back, then lands on Grumpo's head."""
    if not (T_DUMP <= t < T_HIT + 0.04):
        return ""
    sx_, sy_ = DUMP0
    p = seg(t, T_DUMP, T_HIT)
    hx, hy = g["x"], FOOT - 2 * GR - 30
    x = lerp(sx_, hx, p)
    y = lerp(sy_ - 20, hy, ein(p) * 0.6 + p * 0.4) - 150 * 4 * p * (1 - p)
    wob = math.sin(t * 30)
    rx, ry = 110 + 14 * wob, 66 - 10 * wob
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({-30*p:.0f})">'
         f'<path d="M{-rx:.0f} 0 Q {-rx:.0f} {-ry:.0f} 0 {-ry:.0f} Q {rx:.0f} {-ry:.0f} {rx:.0f} 0 Q {rx*0.9:.0f} {ry:.0f} 0 {ry*0.9:.0f} Q {-rx*0.9:.0f} {ry:.0f} {-rx:.0f} 0Z" '
         f'fill="#6cc3f0" stroke="#2a5a8a" stroke-width="5" opacity="0.95"/>'
         f'<path d="M{-rx*0.55:.0f} {-ry*0.45:.0f} Q 0 {-ry*0.8:.0f} {rx*0.4:.0f} {-ry*0.5:.0f}" fill="none" stroke="#e9fbff" stroke-width="8" stroke-linecap="round"/></g>']
    for j in range(4):
        q = (p * 3 + j / 4) % 1
        o.append(drop(x + (j - 1.5) * 50, y + ry + 40 * q, 1.0, (1 - q) * 0.9))
    return "".join(o)


LEAVES = [(rr.uniform(0, 1), rr.uniform(900, 1450), rr.uniform(0, 360)) for _ in range(7)]


def leaves(t):
    if not (T_GUST <= t < 5.1):
        return ""
    o = []
    for (ph, y, r0) in LEAVES:
        p = seg(t, T_GUST + ph * 0.3, T_GUST + ph * 0.3 + 0.7)
        if 0 < p < 1:
            x = lerp(-150, 1250, p)
            yy = y + 60 * math.sin(p * 9)
            o.append(f'<g transform="translate({x:.0f} {yy:.0f}) rotate({r0 + 900*p:.0f})"><path d="M-22 0 Q 0 -16 22 0 Q 0 16 -22 0Z" fill="#e8a23a" stroke="{OL}" stroke-width="3"/>'
                     f'<path d="M-18 0 H18" stroke="{OL}" stroke-width="2"/></g>')
    return "".join(o)


def wind_lines(t):
    if not (T_GUST <= t < 5.0):
        return ""
    k = math.sin(math.pi * seg(t, T_GUST, 5.0))
    o = []
    for j in range(5):
        p = (t * 2.5 + j * 0.21) % 1
        x = lerp(-100, 1200, p)
        y = 950 + j * 110
        o.append(f'<path d="M{x:.0f} {y} q 60 -30 120 0 t 120 0" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="{0.55*k:.2f}"/>')
    return "".join(o)


def exhaust(t):
    if not (10.85 <= t < 11.9):
        return ""
    o = []
    for j in range(3):
        p = seg(t, 10.85 + j * 0.12, 11.6 + j * 0.12)
        if 0 < p < 1:
            x = bus_x(10.85 + j * 0.12) + 1010 - 80 * p
            y = 1260 - 60 * p
            o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{30 + 70*p:.0f}" fill="#9ea2b0" stroke="#6a6e7c" stroke-width="4" opacity="{0.8*(1-p):.2f}"/>')
    return "".join(o)


def headlight_glow(t):
    k = seg(t, T_GLOW, T_GLOW + 0.4) * (1 - seg(t, 9.3, 9.6))
    if k <= 0:
        return ""
    return f'<ellipse cx="1060" cy="1230" rx="260" ry="160" fill="url(#hlG)" opacity="{k:.2f}"/>'


# ---------------------------------------------------------------- camera
CK = [(0.0, (600, 1165, 1.62)), (0.5, (600, 1165, 1.62)), (T_TILT - 0.1, (560, 1175, 1.75)), (3.7, (560, 1175, 1.75)),
      (4.05, (600, 1080, 1.35)), (T_SPLASH, (600, 1100, 1.35)), (5.6, (600, 1165, 1.62)), (6.2, (600, 1165, 1.62)),
      (6.55, (610, 1050, 1.32)), (7.4, (610, 1050, 1.32)), (7.85, (600, 1165, 1.62)), (8.5, (610, 1150, 1.5)),
      (9.4, (600, 1080, 1.3)), (10.3, (600, 1080, 1.3)), (10.85, (600, 1160, 1.55)), (11.5, (600, 1120, 1.4)),
      (12.5, (600, 1120, 1.4)), (12.85, (650, 1160, 1.58)), (DUR, (640, 1170, 1.66))]
SHAKES = [(T_ARR, 5, 0.2), (T_SPLASH, 12, 0.3), (T_POP, 6, 0.2), (T_CRASH, 16, 0.45), (T_HIT, 9, 0.3), (T_BUS, 5, 0.3)]


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


EXTRA_DEFS = ('<linearGradient id="rainSky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4c5a78"/><stop offset="1" stop-color="#9aa8bf"/></linearGradient>'
              '<linearGradient id="waveG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7fd0f6"/><stop offset="1" stop-color="#2b7fc4"/></linearGradient>'
              '<radialGradient id="hlG"><stop offset="0" stop-color="#fff6c0" stop-opacity="0.9"/><stop offset="1" stop-color="#fff6c0" stop-opacity="0"/></radialGradient>'
              '<radialGradient id="vign" cx="0.5" cy="0.55" r="0.75"><stop offset="0.6" stop-color="#101828" stop-opacity="0"/>'
              '<stop offset="1" stop-color="#101828" stop-opacity="0.4"/></radialGradient>')


# ---------------------------------------------------------------- frame
def frame(t):
    ctx = Ctx()
    clear = eio(seg(t, T_CLEAR0, T_CLEAR1))
    g = grumpo_state(t)
    u = umb_state(t)
    n = nibbo_state(t, g, u)
    NB, NS = "#ffd23c", "#3d2a12"
    gfill = "#9466e0"
    gink = "#1a0a2e"
    L = [sky_layer(t, clear), clouds(t, clear), buildings(t, clear), rainbow(t), road(t, clear)]
    if T_BUS - 0.7 <= t < 11.8:
        L.append(bus(bus_x(t), t))
    L.append(headlight_glow(t))
    L.append(exhaust(t))
    L.append(wave_back(t))
    L.append(f'<rect x="-900" y="-600" width="3000" height="{ROAD_BOT+600}" fill="#1c2640" opacity="{0.16*(1-clear):.3f}"/>')
    L.append(sidewalk(t, clear))
    L.append(side_puddle(t, clear))
    L.append(foreground(t, clear))
    L.append(stop_sign())

    hx, hy = hand_pos(g, u)
    umb_svg, geo = umbrella(ctx, hx, hy, u["a"], u["inv"], u["full"])
    cover = None
    if u["inv"] < 0.5:
        lx, rx_ = sorted([geo["left"][0], geo["right"][0]])
        cover = (lx + 10, rx_ - 10, min(geo["left"][1], geo["right"][1], geo["tip"][1]))
    L.append(rain(t, False, None))

    # characters
    L.append(shadow(n["x"], FOOT - 2, 100, cl(1 - (FOOT - n["b"]) / 400)))
    L.append(shadow(g["x"], FOOT - 2, 120, cl(1 - (FOOT - g["b"]) / 400)))
    nib_svg = nibbo(ctx, n["x"], n["y"], NR, n["ex"], rot=n["rot"], sx=n["sx"], sy=n["sy"])
    nib_wet = wetness(n["x"], n["y"], NR, t, n["wet"], n["sx"], n["sy"])
    in_cup = T_JUMP1 <= t < T_POP
    if not in_cup:
        L.append(nib_svg + nib_wet)
    L.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"],
                    False, 0, None, 0, t))
    L.append(wetness(g["x"], g["y"], GR, t + 0.4, g["wet"], g["sx"], g["sy"]))
    # Grumpo's umbrella arm
    L.append(arm(g["x"] + 95 * g["sx"], g["y"] + 35 * g["sy"], hx, hy, gink, 13, 18 - u["raise_"] * 0.1))
    L.append(umb_svg)
    L.append(hand(hx, hy, gfill, OL, 17))
    if in_cup:
        L.append(nib_svg)
    # rain bouncing on the canopy
    if u["inv"] < 0.5 and rain_amt(t) > 0:
        for j in range(6):
            p = (t * 3.1 + j / 6) % 1
            px, py = geo["w"](-UR * 0.8 + j * UR * 0.32, lerp(UF, geo["rim_y"], 0.35) - 8)
            o_ = 1 - p
            L.append(f'<path d="M{px-10-12*p:.0f} {py-18*p:.0f} l-6 -8 M{px+10+12*p:.0f} {py-18*p:.0f} l6 -8" stroke="#e3efff" stroke-width="4" stroke-linecap="round" opacity="{o_*rain_amt(t)*0.9:.2f}"/>')
    L.append(stream(t, geo["left"], n))
    L.append(dump_blob(t, g))
    L.append(rain(t, True, cover))
    L.append(splash_burst(g["x"], FOOT, t, T_SPLASH, 1.3))
    L.append(splash_burst(g["x"], FOOT - 2 * GR * 0.74 + 10, t, T_HIT, 0.9, 0.6))
    if T_POP <= t < T_POP + 0.5:
        L.append(splash_burst(geo["mid"][0], geo["mid"][1] - 60, t, T_POP, 0.7, 0.5))
    L.append(leaves(t))
    L.append(wind_lines(t))
    L.append(wave_front(t))

    # symbols
    L.append(symbol(n["x"] - 20, n["y"] - 170, "?", seg(t, 0.55, 1.0), "#3a7ad6"))
    L.append(symbol(n["x"] + 10, n["y"] - 170, "!", seg(t, 6.0, 6.35), "#ffb020"))
    L.append(symbol(g["x"] + 20, g["y"] - 190, "!", seg(t, T_FLIP + 0.02, T_FLIP + 0.4)))
    L.append(symbol(g["x"] - 30, g["y"] - 190, "!", seg(t, 9.62, 10.0)))
    L.append(symbol(n["x"] - 30, n["y"] - 175, "!", seg(t, 9.62, 10.0)))
    L.append(heart(n["x"] - 60, n["y"] - 150, seg(t, T_SHARE1, T_SHARE1 + 0.75)))
    L.append(star_twinkle(geo["mid"][0], geo["mid"][1] - 80, seg(t, T_POP, T_POP + 0.5)))
    L.append(impact(g["x"], FOOT - 10, seg(t, T_SPLASH, T_SPLASH + 0.2), "#e9fbff"))
    if 5.45 <= t < 6.0:
        L.append(f'<path d="M{g["x"]-150:.0f} {g["y"]-150:.0f} l22 -10 l-8 22 M{g["x"]-125:.0f} {g["y"]-125:.0f} l22 -10 l-8 22" stroke="#e8303a" stroke-width="7" fill="none" stroke-linecap="round"/>')
    if 13.95 <= t < 14.55:
        L.append(f'<path d="M{g["x"]+120:.0f} {g["y"]-110:.0f} l22 -10 l-8 22 M{g["x"]+145:.0f} {g["y"]-85:.0f} l22 -10 l-8 22" stroke="#e8303a" stroke-width="7" fill="none" stroke-linecap="round"/>')
    if 1.85 <= t < 2.05 or T_BUMP <= t < T_BUMP + 0.2:
        L.append(impact(n["x"] + 95, FOOT - 70, seg(t, T_BUMP, T_BUMP + 0.2), "#ffffff"))
    if 9.12 <= t < 9.5:
        L.append(speed_lines(n["x"], n["y"] + 60, -90, 0.5))
    if T_SHAKE <= t < T_SHAKE + 0.45:
        q = seg(t, T_SHAKE, T_SHAKE + 0.45)
        for j in range(10):
            ang = math.radians(j * 36 + 10)
            L.append(drop(n["x"] + math.cos(ang) * (110 + 160 * q), n["y"] + math.sin(ang) * (100 + 140 * q) + 60 * q * q, 1.1, 1 - q))
    if 12.2 <= t < 12.8:
        L.append(star_twinkle(930, 640, seg(t, 12.2, 12.8)))

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{EXTRA_DEFS}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g>'
           f'<rect width="{W}" height="{H}" fill="url(#vign)" opacity="{1-0.6*clear:.2f}"/></svg>')
    return overlay(svg, hook_title(t + 0.12, "Only 1 umbrella", "WHO STAYS DRY?"))


# ---------------------------------------------------------------- sound
def build_sfx():
    for t0 in (0.0, 2.85, 5.7, 8.45):
        sfx(t0, "rain", 0.55, 1.0)
    sfx(0.0, "whoosh", 0.6, 1.2)
    sfx(T_ARR, "squish", 0.8, 1.2)
    sfx(T_ARR + 0.02, "splash_small", 0.6, 1.2)
    sfx(0.55, "blip", 0.3, 0.9)
    sfx(0.95, "hop", 0.5, 1.4)
    sfx(1.2, "squish", 0.4, 1.4)
    sfx(1.35, "umbrella", 0.6, 1.2)
    sfx(1.72, "hop", 0.5, 1.5)
    sfx(1.92, "squish", 0.5, 1.2)
    sfx(T_BUMP - 0.05, "bonk", 0.7, 0.9)
    sfx(T_BUMP + 0.02, "boing", 0.4, 1.3)
    sfx(T_TILT, "umbrella", 0.6, 0.9)
    sfx(T_STREAM0, "stream", 0.9, 1.0)
    sfx(T_STREAM0 + 0.05, "splash_small", 0.5, 0.9)
    sfx(T_STREAM0 + 0.5, "gulp", 0.4, 1.3)
    sfx(3.62, "hop", 0.4, 1.2)
    sfx(3.9, "squish", 0.4, 1.0)
    sfx(T_GUST - 0.1, "wind", 0.9, 1.0)
    sfx(T_FLIP, "umbrella", 0.9, 0.75)
    sfx(T_FLIP + 0.04, "boing", 0.5, 1.1)
    sfx(T_LIFT0, "slide_up", 0.6, 0.8)
    sfx(T_LIFT0 + 0.1, "gasp", 0.5, 0.9)
    sfx(T_LIFT1, "slide_down", 0.6, 0.9)
    sfx(T_SPLASH, "splash", 1.0, 0.9)
    sfx(T_SPLASH, "thud", 0.6, 0.9)
    sfx(5.3, "laugh", 0.6, 1.3)
    sfx(5.5, "grumble", 0.6, 0.9)
    sfx(6.02, "ding", 0.45, 1.3)
    sfx(T_JUMP0, "boing", 0.7, 1.2)
    sfx(T_JUMP0 + 0.03, "whoosh", 0.5, 1.4)
    sfx(T_JUMP1, "squish", 0.7, 1.0)
    sfx(T_JUMP1 + 0.05, "creak", 0.5, 1.0)
    sfx(6.9, "strain", 0.5, 1.2)
    sfx(T_POP, "cork_pop", 0.9, 0.9)
    sfx(T_POP + 0.03, "umbrella", 0.7, 1.1)
    sfx(T_POP + 0.1, "slide_down", 0.5, 1.4)
    sfx(T_NLAND, "plop", 0.6, 1.1)
    sfx(T_SHARE0 + 0.05, "umbrella", 0.4, 1.3)
    sfx(T_SHARE1 + 0.02, "pop", 0.4, 1.6)
    sfx(T_SHARE1 + 0.05, "ding", 0.35, 1.5)
    sfx(T_GLOW, "engine", 0.8, 1.0)
    sfx(T_HONK, "bus_horn", 0.8, 1.0)
    sfx(9.12, "hop", 0.4, 1.5)
    sfx(9.33, "hop", 0.4, 1.6)
    sfx(T_BUS, "splash", 0.8, 0.7)
    sfx(9.65, "gasp", 0.6, 1.1)
    sfx(T_CRASH, "wave", 1.0, 1.0)
    sfx(T_CRASH + 0.05, "umbrella", 0.6, 0.8)
    sfx(T_DRAIN0, "bubbles", 0.5, 1.0)
    sfx(T_DRAIN1, "squish", 0.5, 0.8)
    sfx(10.9, "rumble", 0.35, 1.2)
    sfx(T_SHAKE, "shaker", 0.6, 1.3)
    sfx(T_SHAKE + 0.1, "splash_small", 0.4, 1.4)
    sfx(11.3, "boing", 0.35, 1.0)
    sfx(12.3, "tweet", 0.6, 1.0)
    sfx(12.65, "tweet", 0.5, 1.15)
    sfx(12.4, "rise", 0.3, 1.2)
    sfx(T_DUMP, "umbrella", 0.8, 1.0)
    sfx(T_DUMP + 0.02, "cork_pop", 0.6, 1.2)
    sfx(T_DUMP + 0.05, "slide_up", 0.5, 1.2)
    sfx(T_DUMP + 0.2, "gasp", 0.5, 0.85)
    sfx(T_HIT, "splash", 1.0, 1.1)
    sfx(T_HIT + 0.03, "squish", 0.7, 0.8)
    sfx(13.6, "laugh", 0.65, 1.3)
    sfx(13.95, "grumble", 0.6, 0.85)
    sfx(14.3, "plop", 0.4, 1.3)


DUMP0 = _dump_start()
