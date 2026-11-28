"""Grumpo & Nibbo — Episode 22: The Thermostat War (attic room, one escalating gag, 60 fps).

A small attic room: a wall air-conditioner and, under it, ONE thermostat panel (digital display, red UP / blue DOWN
buttons). Grumpo (big, always hot) wants it COLD, Nibbo (small, always chilly) wants it WARM. Every turn of the war
swings the room further to an extreme:
  0. Grumpo, sweating, taps DOWN 24 -> 18: cool breeze, eyes-closed bliss. Nibbo shivers, teeth chattering.
  1. Nibbo hop-presses UP 3 times -> 30: warm glow, Nibbo beams, Grumpo starts to sweat.
  2. Grumpo machine-gun mashes DOWN -> 0: a blizzard INSIDE the room. Snow piles up, Nibbo gets a snow cap,
     turns blue and chatters; Grumpo smug.
  3. Nibbo shakes the snow off, hops on Grumpo's head, springs to the panel and holds UP -> 45: the snow melts into
     a puddle, the air shimmers. Grumpo MELTS into a droopy blob; Nibbo puts on sunglasses and sunbathes.
  4. Melted Grumpo stretches up the wall like goo and splats DOWN -> -30: deep freeze. Grumpo snaps back round,
     smug with a frost cap; Nibbo is frozen in an ice cube mid-sunbathe (sunglasses on).
  5. The cube wiggles, slides across the iced floor and bowls Grumpo over; it shatters, Nibbo is out. Button war:
     UP-DOWN-UP-DOWN, the AC flickers hot/cold. They grab the panel and tug — it RIPS off the wall on its wire.
The AC rattles, swells... one giant cold BLAST: both are frozen together in one big ice block, still holding the
panel. The dangling display settles on a cheerful 24 (where it started) and the AC switches off. Only their eyes
move: to the display... then to each other.
Ending: both lose. Structure: E (one chain gag escalating). No counter overlay (in-scene digits only).
"""
import math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow
from hook import overlay, hook_title

W, H, FPS, DUR = 1080, 1920, 60, 23.0
GS = 0.92
GR = 130 * GS
NR = 112
FLOOR = 1700
GY = FLOOR - GR
NY = FLOOR - NR
INK = "#1a0a2e"
GFILL = "#9466e0"
NB, NS = "#ffd23c", "#3d2a12"

PX, PY = 540, 1305          # thermostat panel centre (on the wall)
UPB = (540, 1322)           # UP button
DNB = (540, 1372)           # DOWN button
ACX, ACY = 540, 1085        # air conditioner centre

# ---- times
T_GP = [0.40, 0.62, 0.84]           # grumpo taps DOWN
T_NP = [2.27, 2.64, 3.01]           # nibbo hop-presses UP (apex)
T_MASH0, T_MASH1 = 3.6, 4.4
T_SNOW0 = 4.2
T_SHAKE0, T_SHAKE1 = 6.25, 6.6
T_HOPG0, T_HOPG1 = 6.68, 7.0        # nibbo hops onto grumpo's head
T_SPR0, T_SPR1 = 7.06, 7.36         # springs to the panel
T_HOLD1 = 8.2                       # display reaches 45
T_DROP0, T_DROP1 = 8.4, 8.75
T_SHADES = 8.95
T_MELT0, T_MELT1 = 8.3, 9.6
T_GOO0, T_GOO1 = 10.0, 10.7
T_DOWN1 = 11.6                      # display reaches -30
T_SNAP = 11.65
T_CUBE0, T_CUBE1 = 11.72, 12.0
T_WIG0, T_WIG1 = 13.55, 14.0
T_SLIDE0, T_IMP = 14.0, 14.55
T_NOTICE = 14.12
T_CRACK = 14.6
T_SHAT = 14.78
T_GSPIN1 = 15.15
T_GBACK0, T_GBACK1 = 15.3, 15.62
T_NCL0, T_NCL1 = 15.15, 15.5
T_WAR0, T_WAR1 = 15.8, 16.9
T_GRAB = 17.0
T_RIP = 17.6
T_ACSH0 = 18.0
T_LOOK = 18.45
T_BLAST = 19.15
T_ICE1 = 19.38
T_ICICLE = 20.15
T_DISP24 = 20.9
T_ACOFF = 21.15
T_EYE1 = 21.4
T_EYE2 = 22.0
WAR_DT = 0.137

GX_F = 430          # grumpo x after goo-stretch
NX_L = 760          # nibbo lounging x

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


def ramp(t, a, b, c, d):
    """0 -> 1 over [a,b], stays 1, 1 -> 0 over [c,d]."""
    return min(eio(seg(t, a, b)), 1 - eio(seg(t, c, d)))


def wob(t, t0, d=0.5, a=0.2, f=3.0):
    k = t - t0
    if 0 <= k < d:
        v = a * math.sin(2 * math.pi * f * k / d) * (1 - k / d)
        return 1 + v, 1 - v
    return 1.0, 1.0


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


def h01(i, k=0):
    """deterministic hash -> 0..1"""
    v = math.sin(i * 127.1 + k * 311.7) * 43758.5453
    return v - math.floor(v)


# ---------------------------------------------------------------- temperature
def setpoint(t):
    if t < T_GP[0]:
        return 24
    if t < T_NP[0]:
        return 24 - 2 * sum(1 for x in T_GP if t >= x)
    if t < T_MASH0:
        return 18 + 4 * sum(1 for x in T_NP if t >= x)
    if t < T_SPR1:
        return int(30 - 2 * math.floor(15 * seg(t, T_MASH0, T_MASH1)))
    if t < T_GOO1:
        return int(round(45 * eio(seg(t, T_SPR1, T_HOLD1))))
    if t < T_WAR0:
        return int(round(lerp(45, -30, eio(seg(t, T_GOO1, T_DOWN1)))))
    if t < T_WAR1:
        i = int((t - T_WAR0) / WAR_DT)
        return 45 if i % 2 == 0 else -30
    if t < T_RIP:
        return -30 if int(t * 7) % 2 else 45
    if t < T_BLAST:
        return int(h01(int(t * 14)) * 198) - 99
    return 24


def ac_mode(t):
    """(+1 hot / -1 cold / 0 off, strength 0..1)"""
    if t >= T_ACOFF:
        return 0, 0.0
    if T_RIP <= t < T_BLAST:
        return (1 if int(t * 9) % 2 else -1), 0.6 + 0.4 * seg(t, T_ACSH0, T_BLAST)
    if t >= T_BLAST:
        return -1, 1 - seg(t, T_BLAST + 0.6, T_ACOFF)
    v = setpoint(t)
    if v == 24:
        return 0, 0.0
    return (1 if v > 24 else -1), cl(0.3 + abs(v - 24) / 30, 0, 1)


def cold(t):
    c = 0.3 * ramp(t, 0.6, 1.2, 2.4, 3.0)
    c = max(c, 0.9 * ramp(t, T_MASH0 + 0.3, T_SNOW0 + 0.5, 7.5, 8.3))
    c = max(c, 1.0 * ramp(t, T_GOO1 + 0.5, T_SNAP + 0.3, 30, 31))
    return c


def hot(t):
    h = 0.3 * ramp(t, 2.9, 3.4, T_MASH0, T_MASH0 + 0.5)
    h = max(h, ramp(t, 7.6, 8.4, T_GOO1 + 0.5, T_SNAP + 0.15))
    return h


def snow_pile(t):
    return min(eio(seg(t, 4.5, 6.3)), 1 - eio(seg(t, 8.15, 8.8)))


def puddle(t):
    return eio(seg(t, 8.25, 8.9)) * 0.75 + 0.25 * eio(seg(t, 8.8, 10.4))


def ice_floor(t):
    return eio(seg(t, T_SNAP, T_SNAP + 0.5))


def frost(t):
    return eio(seg(t, T_SNAP - 0.05, T_SNAP + 0.6))


# ---------------------------------------------------------------- environment
def room(t):
    o = []
    # back wall
    o.append(f'<rect x="-900" y="-400" width="2900" height="{FLOOR+400}" fill="#f1dcb4"/>')
    for x in range(-900, 2000, 96):
        o.append(f'<rect x="{x}" y="-400" width="40" height="{FLOOR+400}" fill="#ead0a2"/>')
        o.append(f'<circle cx="{x+68}" cy="{1180 + (x % 192)}" r="6" fill="#e2c592"/>')
    # attic slopes (with beams)
    lp = "M-900 600 L420 600 L-260 1520 L-900 1520Z"
    rp = "M660 600 L2000 600 L2000 1520 L1340 1520Z"
    for d, sky in ((lp, False), (rp, True)):
        o.append(f'<path d="{d}" fill="#c99a63" stroke="{OL}" stroke-width="7" stroke-linejoin="round"/>')
    o.append('<path d="M330 720 L-120 1330 M240 600 L-200 1200" stroke="#b5864f" stroke-width="16"/>')
    o.append('<path d="M760 740 L1180 1310 M860 600 L1260 1150" stroke="#b5864f" stroke-width="16"/>')
    o.append(f'<path d="M420 600 L-260 1520 M660 600 L1340 1520" stroke="{OL}" stroke-width="8"/>')
    o.append('<path d="M432 610 L-244 1520" stroke="#dcb27c" stroke-width="10"/><path d="M648 610 L1324 1520" stroke="#dcb27c" stroke-width="10"/>')
    # skylight in the right slope
    o.append(skylight(t))
    # skirting + floor
    o.append(f'<rect x="-900" y="{FLOOR-34}" width="2900" height="40" fill="#e9e1d2" stroke="{OL}" stroke-width="5"/>')
    o.append(f'<rect x="-900" y="{FLOOR}" width="2900" height="900" fill="#c88a52"/>')
    for r, y in enumerate(range(FLOOR, FLOOR + 900, 62)):
        o.append(f'<path d="M-900 {y} H2000" stroke="#a86d3c" stroke-width="5"/>')
        off = (r * 173) % 260
        for x in range(-900 + off, 2000, 260):
            o.append(f'<path d="M{x} {y} v62" stroke="#a86d3c" stroke-width="5"/>')
        o.append(f'<path d="M-900 {y+10} H2000" stroke="#d99d64" stroke-width="4" opacity="0.6"/>')
    o.append(f'<path d="M-900 {FLOOR} H2000" stroke="{OL}" stroke-width="7"/>')
    # rug
    o.append(f'<ellipse cx="560" cy="{FLOOR+70}" rx="430" ry="56" fill="#c44a4a" stroke="{OL}" stroke-width="6"/>'
             f'<ellipse cx="560" cy="{FLOOR+70}" rx="380" ry="40" fill="none" stroke="#f2c14a" stroke-width="7" stroke-dasharray="26 16"/>')
    # props: little desk fan (left) and plant (right)
    o.append(fan(150, t) + plant(965))
    # wall picture frame (icon: thermometer)
    o.append(f'<g transform="translate(250 1230)"><rect x="-58" y="-70" width="116" height="140" rx="8" fill="#8a5a3a" stroke="{OL}" stroke-width="6"/>'
             f'<rect x="-44" y="-56" width="88" height="112" fill="#bfe6f5"/>'
             f'<path d="M-44 30 Q -10 0 10 18 Q 26 6 44 22 V56 H-44Z" fill="#7cc65c"/><circle cx="20" cy="-26" r="14" fill="#ffd23a"/></g>')
    return "".join(o)


def skylight(t):
    c = cold(t)
    h = hot(t)
    o = ['<g transform="translate(880 1040) skewX(36)">']
    o.append(f'<rect x="-60" y="-80" width="150" height="150" rx="8" fill="#d7ecf8" stroke="{OL}" stroke-width="7"/>')
    o.append('<rect x="-48" y="-68" width="126" height="126" fill="#76c0f2"/>')
    o.append(f'<circle cx="40" cy="-30" r="18" fill="#fff6c8" opacity="{0.8:.2f}"/>')
    o.append('<path d="M-48 30 Q -20 14 0 26 Q 30 10 78 24 V58 H-48Z" fill="#ffffff" opacity="0.85"/>')
    o.append(f'<path d="M15 -68 V58 M-48 -5 H78" stroke="#d7ecf8" stroke-width="9"/>')
    if c > 0.5:
        o.append(f'<rect x="-48" y="-68" width="126" height="126" fill="#ffffff" opacity="{0.55*seg(c,0.5,1):.2f}"/>')
    o.append('</g>')
    return "".join(o)


def fan(x, t):
    y = FLOOR - 40
    spin = t * 1400
    o = [f'<rect x="{x-60}" y="{y}" width="120" height="40" rx="8" fill="#6a8fb0" stroke="{OL}" stroke-width="5"/>',
         f'<rect x="{x-10}" y="{y-120}" width="20" height="124" fill="#c8d3de" stroke="{OL}" stroke-width="5"/>',
         f'<circle cx="{x}" cy="{y-170}" r="70" fill="#e6eef5" stroke="{OL}" stroke-width="6"/>']
    o.append(f'<g transform="translate({x} {y-170}) rotate({spin%360:.1f})">' + "".join(
        f'<ellipse cx="0" cy="-34" rx="18" ry="32" fill="#7fc4ef" stroke="{OL}" stroke-width="3" transform="rotate({a})"/>' for a in (0, 120, 240)) + '</g>')
    o.append(f'<circle cx="{x}" cy="{y-170}" r="12" fill="#6a8fb0" stroke="{OL}" stroke-width="4"/>')
    o.append(f'<g stroke="{OL}" stroke-width="2.5" opacity="0.6" fill="none"><circle cx="{x}" cy="{y-170}" r="48"/><circle cx="{x}" cy="{y-170}" r="26"/>'
             f'<path d="M{x-70} {y-170} H{x+70} M{x} {y-240} V{y-100}"/></g>')
    return "".join(o)


def plant(x):
    o = [f'<path d="M{x-50} {FLOOR-110} h100 l-14 110 h-72z" fill="#d8693a" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>',
         f'<rect x="{x-56}" y="{FLOOR-124}" width="112" height="22" rx="6" fill="#e8814e" stroke="{OL}" stroke-width="5"/>']
    for k, (a, L) in enumerate([(-55, 220), (-20, 280), (10, 300), (40, 250), (70, 200)]):
        r = math.radians(a - 90)
        ex, ey = x + L * math.cos(r), FLOOR - 120 + L * math.sin(r)
        o.append(f'<path d="M{x} {FLOOR-120} Q {(x+ex)/2+16} {(FLOOR-120+ey)/2} {ex:.0f} {ey:.0f}" fill="none" stroke="#2f7a3a" stroke-width="7"/>')
        o.append(f'<g transform="translate({ex:.0f} {ey:.0f}) rotate({a})"><path d="M0 0 C -50 -18 -50 -90 0 -116 C 50 -90 50 -18 0 0Z" fill="{"#4fae56" if k % 2 else "#3f9a4a"}" stroke="{OL}" stroke-width="5"/>'
                 f'<path d="M0 -10 V-100" stroke="#2f7a3a" stroke-width="4"/></g>')
    return "".join(o)


def ac_unit(t):
    mode, st = ac_mode(t)
    sh = 0.0
    sc = 1.0
    if T_ACSH0 <= t < T_BLAST:
        q = seg(t, T_ACSH0, T_BLAST)
        sh = 3 + 10 * q
        sc = 1 + 0.07 * eio(q)
    if T_BLAST <= t < T_BLAST + 0.25:
        q = seg(t, T_BLAST, T_BLAST + 0.25)
        sc = 1.07 - 0.12 * math.sin(math.pi * q)
    dx = sh * math.sin(t * 91)
    dy = sh * 0.6 * math.cos(t * 77)
    flap = 0.0
    if mode != 0:
        flap = 18 + 10 * st
    if T_ACSH0 <= t < T_BLAST:
        flap = 18 + 24 * abs(math.sin(t * 30))
    if t >= T_ACOFF:
        flap = max(0, 28 * (1 - seg(t, T_ACOFF, T_ACOFF + 0.4)))
    led = "#9aa4ae"
    if mode < 0:
        led = "#3ab0ff"
    elif mode > 0:
        led = "#ff6a2a"
    if t >= T_ACOFF:
        led = "#9aa4ae"
    o = [f'<g transform="translate({ACX+dx:.1f} {ACY+dy:.1f}) scale({sc:.3f})">']
    o.append(f'<rect x="-222" y="-58" width="444" height="124" rx="26" fill="#f7f8fa" stroke="{OL}" stroke-width="7"/>')
    o.append('<rect x="-206" y="-46" width="412" height="20" rx="8" fill="#e3e8ee"/>')
    o.append(f'<path d="M-200 32 H200" stroke="#c9d1da" stroke-width="5"/>')
    o.append(f'<rect x="-196" y="38" width="392" height="22" rx="8" fill="#2c3440"/>')
    # flaps
    for k in range(5):
        fx = -160 + k * 80
        o.append(f'<g transform="translate({fx} 50) rotate({flap:.1f})"><rect x="-34" y="-5" width="68" height="10" rx="4" fill="#dfe5ec" stroke="{OL}" stroke-width="3"/></g>')
    # snowflake / sun icon + led
    o.append(f'<circle cx="170" cy="-8" r="9" fill="{led}" stroke="{OL}" stroke-width="3"/>')
    if mode > 0 and t < T_ACOFF:
        o.append(f'<circle cx="170" cy="-8" r="20" fill="{led}" opacity="{0.25+0.2*math.sin(t*12):.2f}"/>')
    elif mode < 0 and t < T_ACOFF:
        o.append(f'<circle cx="170" cy="-8" r="20" fill="{led}" opacity="{0.25+0.2*math.sin(t*12):.2f}"/>')
    o.append(f'<g stroke="#9fb0c2" stroke-width="5" stroke-linecap="round"><path d="M-170 -10 h36 M-152 -28 v36 M-165 -23 l26 26 M-165 3 l26 -26"/></g>')
    # icicles under the AC in deep freeze
    fr = frost(t)
    if fr > 0:
        for k in range(9):
            ix = -190 + k * 48
            L = (30 + 40 * h01(k, 3)) * fr
            if t >= T_ICICLE and k == 4:
                continue
            o.append(f'<path d="M{ix-11} 64 L{ix+11} 64 L{ix} {64+L:.0f}Z" fill="#dff4ff" stroke="#6aa8d8" stroke-width="3" stroke-linejoin="round"/>')
        o.append(f'<path d="M-222 -40 Q -120 -78 0 -62 Q 120 -78 222 -40 L222 -50 Q 150 -84 0 -70 Q -150 -84 -222 -50Z" fill="#ffffff" stroke="#8fc3e8" stroke-width="3" opacity="{fr:.2f}"/>')
    o.append('</g>')
    return "".join(o)


def airflow(t):
    mode, st = ac_mode(t)
    if mode == 0 or st <= 0:
        return ""
    if t >= T_BLAST:
        st *= 0.6
    col = "#5ec8ff" if mode < 0 else "#ff8a3a"
    col2 = "#d8f4ff" if mode < 0 else "#ffe0a0"
    o = []
    for k in range(6):
        x0 = 360 + k * 72
        spread = (k - 2.5) * 70
        d = (f"M{x0} 1150 C {x0 + spread*0.3:.0f} 1260, {x0 + spread*0.9 - 30:.0f} 1340, {x0 + spread*1.3:.0f} 1480 "
             f"S {x0 + spread*1.6 + 20:.0f} 1600, {x0 + spread*1.9:.0f} 1690")
        off = -(t * 520 + k * 47) % 200
        o.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{14*st+4:.1f}" stroke-linecap="round" stroke-dasharray="70 130" stroke-dashoffset="{off:.1f}" opacity="{0.55*st+0.15:.2f}"/>')
        o.append(f'<path d="{d}" fill="none" stroke="{col2}" stroke-width="{5*st+2:.1f}" stroke-linecap="round" stroke-dasharray="40 160" stroke-dashoffset="{off-15:.1f}" opacity="{0.7*st:.2f}"/>')
    return "".join(o)


def heat_shimmer(t):
    h = hot(t)
    if h < 0.5:
        return ""
    q = seg(h, 0.5, 1.0)
    o = [f'<g opacity="{0.55*q:.2f}">']
    for k in range(9):
        x = 180 + k * 90 + 20 * math.sin(k * 2.1)
        y0 = 1680 - ((t * 260 + k * 133) % 520)
        o.append(f'<path d="M{x:.0f} {y0:.0f} q 18 -30 0 -60 q -18 -30 0 -60 q 18 -30 0 -60" fill="none" stroke="#fff4c0" stroke-width="7" stroke-linecap="round"/>')
    o.append('</g>')
    o.append(f'<circle cx="540" cy="1150" r="520" fill="url(#hotglow)" opacity="{0.7*q:.2f}"/>')
    return "".join(o)


def snowfall(t):
    c = cold(t)
    if c < 0.5 or (T_SPR1 + 1.0 < t < T_GOO1 + 0.3):
        if not (t >= T_BLAST):
            return ""
    dens = seg(c, 0.5, 0.9)
    if t >= T_BLAST:
        dens = max(dens, 1 - 0.6 * seg(t, T_BLAST + 0.5, T_BLAST + 2.0))
    wind = 0.0
    if T_SNOW0 <= t < 6.5:
        wind = 1.0
    o = []
    N = 70
    for i in range(N):
        if h01(i, 1) > dens:
            continue
        sp = 140 + 160 * h01(i, 2)
        x = 120 + ((h01(i, 3) * 880 + t * (40 + 220 * wind) + 30 * math.sin(t * 2 + i)) % 880)
        y = 1000 + ((h01(i, 4) * 720 + t * sp) % 720)
        r = 5 + 8 * h01(i, 5)
        o.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#ffffff" stroke="#9ccbe8" stroke-width="2"/>')
    return "".join(o)


def floor_snow(t):
    s = snow_pile(t)
    o = []
    if s > 0.01:
        hgt = 70 * s
        d = f"M120 {FLOOR+8} Q 200 {FLOOR-hgt*0.6:.0f} 300 {FLOOR-hgt*0.4:.0f} Q 420 {FLOOR-hgt:.0f} 560 {FLOOR-hgt*0.5:.0f} Q 700 {FLOOR-hgt*1.1:.0f} 820 {FLOOR-hgt*0.5:.0f} Q 920 {FLOOR-hgt*0.7:.0f} 990 {FLOOR+8}Z"
        o.append(f'<path d="{d}" fill="#ffffff" stroke="#8fbfe0" stroke-width="5" stroke-linejoin="round"/>')
        o.append(f'<path d="M300 {FLOOR-hgt*0.25:.0f} Q 420 {FLOOR-hgt*0.75:.0f} 540 {FLOOR-hgt*0.35:.0f}" fill="none" stroke="#e2f2fc" stroke-width="10" stroke-linecap="round"/>')
    p = puddle(t)
    fr = ice_floor(t)
    if p > 0.01:
        rx = 460 * p
        fill = mix_hex("#6ec6f0", "#dff4ff", fr)
        o.append(f'<ellipse cx="560" cy="{FLOOR+46}" rx="{rx:.0f}" ry="{50*p+6:.0f}" fill="{fill}" stroke="{mix_hex("#3a86c0", "#7ab8e0", fr)}" stroke-width="5" opacity="0.92"/>')
        o.append(f'<ellipse cx="{560-rx*0.3:.0f}" cy="{FLOOR+34}" rx="{rx*0.35:.0f}" ry="{10*p:.0f}" fill="#ffffff" opacity="{0.45+0.4*fr:.2f}"/>')
        if fr > 0:
            o.append(f'<path d="M{560-rx*0.6:.0f} {FLOOR+60} l70 -30 M{560+rx*0.2:.0f} {FLOOR+66} l90 -40 M{560+rx*0.55:.0f} {FLOOR+56} l40 -18" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="{fr:.2f}"/>')
        # ripples while hot
        if hot(t) > 0.5 and fr == 0:
            for k in range(2):
                q = ((t * 0.8 + k * 0.5) % 1)
                o.append(f'<ellipse cx="{430 + 260*k}" cy="{FLOOR+46}" rx="{20+70*q:.0f}" ry="{4+12*q:.0f}" fill="none" stroke="#ffffff" stroke-width="4" opacity="{0.8*(1-q):.2f}"/>')
    return "".join(o)


def wall_frost(t):
    fr = frost(t)
    if fr <= 0:
        return ""
    o = [f'<g opacity="{fr:.2f}">']
    # frost crusts on slope edges and around the panel
    o.append('<path d="M420 600 L-260 1520 L-200 1520 Q -150 1400 -90 1420 Q -40 1300 20 1310 Q 60 1190 130 1200 Q 170 1080 240 1090 Q 290 960 350 970 Q 390 840 440 860Z" fill="#ffffff" opacity="0.8"/>')
    o.append('<path d="M660 600 L1340 1520 L1280 1520 Q 1230 1400 1170 1420 Q 1120 1300 1060 1310 Q 1020 1190 950 1200 Q 910 1080 840 1090 Q 790 960 730 970 Q 690 840 640 860Z" fill="#ffffff" opacity="0.8"/>')
    o.append(f'<path d="M-900 {FLOOR-34} H2000 V{FLOOR-60} Q 1500 {FLOOR-90} 1200 {FLOOR-62} Q 900 {FLOOR-96} 600 {FLOOR-60} Q 300 {FLOOR-92} 0 {FLOOR-62} Q -500 {FLOOR-90} -900 {FLOOR-60}Z" fill="#ffffff" stroke="#9fd0ee" stroke-width="4"/>')
    o.append('</g>')
    return "".join(o)


# ---------------------------------------------------------------- thermostat
def panel_svg(x, y, rot, t, up_p=0.0, dn_p=0.0, frosted=0.0):
    v = setpoint(t)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">']
    o.append(f'<rect x="-76" y="-102" width="152" height="204" rx="22" fill="#f4f1ea" stroke="{OL}" stroke-width="7"/>')
    o.append('<rect x="-66" y="-92" width="132" height="14" rx="6" fill="#ffffff" opacity="0.8"/>')
    # display
    if v < 24:
        dcol, bg = "#bfeaff", "#0f3550"
    elif v > 24:
        dcol, bg = "#ffd0a0", "#4a1a0a"
    else:
        dcol, bg = "#c8ffb0", "#163a1a"
    glitch = T_RIP <= t < T_BLAST
    off = T_BLAST <= t < T_DISP24 - 0.3
    flick = T_DISP24 - 0.3 <= t < T_DISP24
    o.append(f'<rect x="-60" y="-74" width="120" height="66" rx="10" fill="{"#1a1a20" if off else bg}" stroke="{OL}" stroke-width="5"/>')
    if not off and not (flick and int(t * 30) % 2):
        txt = f"{v}°"
        if glitch and int(t * 20) % 3 == 0:
            txt = "88°"
        size = 46 if len(txt) <= 3 else 40
        o.append(f'<text x="0" y="-24" font-family="DejaVu Sans Mono" font-weight="bold" font-size="{size}" text-anchor="middle" fill="{dcol}">{txt}</text>')
        if t >= T_DISP24:
            q = seg(t, T_DISP24, T_DISP24 + 0.5)
            if q < 1:
                o.append(f'<rect x="-60" y="-74" width="120" height="66" rx="10" fill="#c8ffb0" opacity="{0.6*(1-q):.2f}"/>')
    o.append('<rect x="-52" y="-68" width="40" height="10" rx="4" fill="#ffffff" opacity="0.18"/>')
    # buttons
    for (by, col, dark, p, up) in ((17, "#ff5a4a", "#a8231a", up_p, True), (67, "#3aa0ff", "#1a4fa0", dn_p, False)):
        dy = 4 * p
        o.append(f'<circle cx="0" cy="{by+4}" r="25" fill="{dark}" stroke="{OL}" stroke-width="5"/>')
        o.append(f'<circle cx="0" cy="{by+dy:.1f}" r="25" fill="{col}" stroke="{OL}" stroke-width="5"/>')
        if up:
            o.append(f'<path d="M-12 {by+6+dy:.1f} L0 {by-10+dy:.1f} L12 {by+6+dy:.1f}Z" fill="#ffffff" stroke="#ffffff" stroke-width="3" stroke-linejoin="round"/>')
        else:
            o.append(f'<path d="M-12 {by-6+dy:.1f} L0 {by+10+dy:.1f} L12 {by-6+dy:.1f}Z" fill="#ffffff" stroke="#ffffff" stroke-width="3" stroke-linejoin="round"/>')
    # tiny sun / snowflake icons beside buttons
    o.append(f'<circle cx="-50" cy="17" r="8" fill="#ffb02a" stroke="{OL}" stroke-width="3"/>')
    o.append(f'<g stroke="#3aa0ff" stroke-width="4" stroke-linecap="round"><path d="M-58 67 h16 M-50 59 v16 M-56 61 l12 12 M-56 73 l12 -12"/></g>')
    if frosted > 0:
        o.append(f'<path d="M-76 -80 Q -76 -102 -54 -102 H54 Q 76 -102 76 -80 V-70 Q 40 -84 0 -76 Q -40 -86 -76 -70Z" fill="#ffffff" stroke="#9fd0ee" stroke-width="3" opacity="{frosted:.2f}"/>')
    o.append('</g>')
    return "".join(o)


def press_amt(t, times, d=0.12):
    for x in times:
        if x - 0.02 <= t < x + d:
            return math.sin(math.pi * seg(t, x - 0.02, x + d))
    return 0.0


def war_presses(t):
    """(up_p, dn_p) during the button war."""
    if not (T_WAR0 <= t < T_WAR1):
        return 0.0, 0.0
    i = int((t - T_WAR0) / WAR_DT)
    f = ((t - T_WAR0) % WAR_DT) / WAR_DT
    p = math.sin(math.pi * cl(f / 0.7))
    return (p, 0.0) if i % 2 == 0 else (0.0, p)


def panel_state(t):
    """returns x, y, rot, up_p, dn_p, wire (bool)."""
    up = press_amt(t, T_NP)
    dn = press_amt(t, T_GP)
    if T_MASH0 <= t < T_MASH1:
        dn = abs(math.sin((t - T_MASH0) * math.pi * 19))
    if T_SPR1 <= t < T_HOLD1 + 0.15:
        up = 1.0
    if T_GOO1 <= t < T_DOWN1 + 0.1:
        dn = 1.0
    wu, wd = war_presses(t)
    up, dn = max(up, wu), max(dn, wd)
    if t < T_GRAB:
        return PX, PY, 0.0, up, dn, False
    if t < T_RIP:
        q = seg(t, T_GRAB, T_RIP)
        j = 3 * q * math.sin(t * 70)
        return PX + j, PY + 6 * q, j * 0.6, 0, 0, False
    # ripped off: held between them
    q = seg(t, T_RIP, T_RIP + 0.3)
    tug = 0.0
    if t < T_LOOK:
        tug = 28 * math.sin((t - T_RIP) * 9) * (1 - seg(t, T_LOOK - 0.3, T_LOOK))
    x = PX + tug
    y = lerp(PY, 1468, eout(q))
    rot = lerp(0, -8, q) + tug * 0.25
    return x, y, rot, 0, 0, True


def wire(t, px, py):
    """coiled wire from the hole in the wall to the panel's back/top."""
    x0, y0 = PX, PY
    x1, y1 = px, py - 90
    n = 14
    pts = []
    for i in range(n + 1):
        f = i / n
        x = lerp(x0, x1, f) + 14 * math.sin(f * math.pi * 10)
        y = lerp(y0, y1, f) + 40 * math.sin(math.pi * f)
        pts.append(f"{x:.1f} {y:.1f}")
    d = "M" + " L".join(pts)
    return (f'<rect x="{PX-50}" y="{PY-60}" width="100" height="120" rx="12" fill="#5a4a3a" stroke="{OL}" stroke-width="6"/>'
            f'<rect x="{PX-36}" y="{PY-46}" width="72" height="92" rx="8" fill="#2a2018"/>'
            f'<path d="{d}" fill="none" stroke="{OL}" stroke-width="13" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="#e8463a" stroke-width="6" stroke-linejoin="round"/>')


# ---------------------------------------------------------------- faces / extras
def g_extra(x, y, s, rot, sx, sy, kind, t, red=0.0, look=(0, 0)):
    ink = mix_hex(INK, "#3a0505", red)
    base = mix_hex("#9466e0", "#ff6a52", red)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s*sx:.3f} {s*sy:.3f})">']
    cover = f'<ellipse cx="-38" cy="16" rx="25" ry="27" fill="{base}"/><ellipse cx="38" cy="16" rx="25" ry="27" fill="{base}"/>'
    if kind == "bliss":
        o.append(cover + f'<path d="M-56 18 q18 -16 36 0 M20 18 q18 -16 36 0" fill="none" stroke="{ink}" stroke-width="9" stroke-linecap="round"/>'
                 f'<path d="M-72 -26 Q -46 -36 -18 -30 M72 -26 Q 46 -36 18 -30" fill="none" stroke="{ink}" stroke-width="14" stroke-linecap="round"/>'
                 f'<path d="M-34 62 Q 0 96 34 62" fill="#4a0a14" stroke="{ink}" stroke-width="9" stroke-linejoin="round"/>'
                 '<ellipse cx="-70" cy="52" rx="16" ry="9" fill="#ff7fa0" opacity="0.5"/><ellipse cx="70" cy="52" rx="16" ry="9" fill="#ff7fa0" opacity="0.5"/>')
    elif kind == "melt":
        lx, ly = look
        o.append(cover + f'<ellipse cx="-38" cy="22" rx="18" ry="16" fill="#fff" stroke="#221c2e" stroke-width="3"/><ellipse cx="38" cy="22" rx="18" ry="16" fill="#fff" stroke="#221c2e" stroke-width="3"/>'
                 f'<circle cx="{-36+lx*6:.1f}" cy="{28+ly*4:.1f}" r="8" fill="{ink}"/><circle cx="{40+lx*6:.1f}" cy="{28+ly*4:.1f}" r="8" fill="{ink}"/>'
                 f'<path d="M-60 20 h44 v-14 h-44z M16 20 h44 v-14 h-44z" fill="{base}"/>'
                 f'<path d="M-58 18 h40 M18 18 h40" stroke="{ink}" stroke-width="6" stroke-linecap="round"/>'
                 f'<path d="M-72 -6 Q -46 -20 -18 -10 M72 -6 Q 46 -20 18 -10" fill="none" stroke="{ink}" stroke-width="13" stroke-linecap="round"/>'
                 f'<path d="M-30 74 q10 -8 20 0 t20 0 t20 0" fill="none" stroke="{ink}" stroke-width="8" stroke-linecap="round"/>'
                 f'<path d="M8 80 q4 26 -4 40 q-10 -10 4 -40z" fill="#ff8fa8" stroke="{ink}" stroke-width="4"/>')
    elif kind == "strain":
        o.append(f'<path d="M-78 -36 L -20 -10 M78 -36 L 20 -10" fill="none" stroke="{ink}" stroke-width="18" stroke-linecap="round"/>'
                 f'<path d="M-40 60 h80 v30 h-80z" fill="#fff" stroke="{ink}" stroke-width="8" stroke-linejoin="round"/><path d="M-40 75 h80" stroke="{ink}" stroke-width="4"/>'
                 '<path d="M100 -40 q12 18 0 28 q-12 -10 0 -28z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3"/>')
    elif kind == "dizzy":
        o.append(cover + f'<path d="M-52 2 l28 28 M-24 2 l-28 28 M24 2 l28 28 M52 2 l-28 28" stroke="{ink}" stroke-width="9" stroke-linecap="round"/>'
                 f'<path d="M-24 74 q12 -10 24 0 t24 0" fill="none" stroke="{ink}" stroke-width="8" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


def n_face(x, y, r, rot, sx, sy, kind, t, look=(0, 0)):
    f = r / 48 * 1.05
    d = "#2a1a10"
    lx, ly = look
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx*f:.3f} {sy*f:.3f})">']
    eyes = (f'<ellipse cx="{-14+lx*4:.1f}" cy="{-4+ly*3:.1f}" rx="6" ry="8" fill="{d}"/><ellipse cx="{14+lx*4:.1f}" cy="{-4+ly*3:.1f}" rx="6" ry="8" fill="{d}"/>'
            f'<circle cx="{-12+lx*4:.1f}" cy="{-7+ly*3:.1f}" r="2.2" fill="#fff"/><circle cx="{16+lx*4:.1f}" cy="{-7+ly*3:.1f}" r="2.2" fill="#fff"/>')
    blush = ('<ellipse cx="-28" cy="10" rx="8" ry="4.5" fill="#ff7fa0" opacity="0.55"/>'
             '<ellipse cx="28" cy="10" rx="8" ry="4.5" fill="#ff7fa0" opacity="0.55"/>')
    if kind == "chatter":
        o.append(f'<path d="M-21 -6 q7 6 14 0 M7 -6 q7 6 14 0" fill="none" stroke="{d}" stroke-width="4.5" stroke-linecap="round"/>'
                 f'<path d="M-24 -18 l12 5 M24 -18 l-12 5" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>')
        g = 2 * abs(math.sin(t * 60))
        o.append(f'<rect x="-14" y="{8-g:.1f}" width="28" height="{12+2*g:.1f}" rx="3" fill="#ffffff" stroke="{d}" stroke-width="3.5"/>'
                 f'<path d="M-14 {14:.1f} h28 M-5 {8-g:.1f} v{12+2*g:.1f} M5 {8-g:.1f} v{12+2*g:.1f}" stroke="{d}" stroke-width="2.5"/>')
    elif kind == "frown":
        o.append(eyes + blush + f'<path d="M-24 -20 l14 6 M24 -20 l-14 6" stroke="{d}" stroke-width="4" stroke-linecap="round"/>'
                 f'<path d="M-8 16 q8 -5 16 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    elif kind == "uhoh":
        o.append(eyes + blush + f'<path d="M-24 -18 l12 -5 M24 -18 l-12 -5" stroke="{d}" stroke-width="3.5" stroke-linecap="round"/>'
                 f'<ellipse cx="0" cy="15" rx="6" ry="8" fill="#7a2a1a" stroke="{d}" stroke-width="3.5"/>')
    elif kind == "smug":
        o.append(blush + f'<path d="M-21 -4 h14 M7 -4 h14" stroke="{d}" stroke-width="5" stroke-linecap="round"/>'
                 f'<path d="M-21 -10 q7 -4 14 0 M7 -10 q7 -4 14 0" fill="none" stroke="{d}" stroke-width="3" stroke-linecap="round"/>'
                 f'<path d="M-8 12 q10 6 18 -4" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    elif kind == "dizzy":
        o.append(f'<path d="M-20 -10 l12 12 M-8 -10 l-12 12 M8 -10 l12 12 M20 -10 l-12 12" stroke="{d}" stroke-width="4.5" stroke-linecap="round"/>'
                 f'<path d="M-10 14 q5 -6 10 0 t10 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    o.append('</g>')
    return "".join(o)


def tint_circle(ctx, x, y, r, rot, sx, sy, col, op):
    if op <= 0.01:
        return ""
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx:.3f} {sy:.3f})">'
            f'<circle r="{r-3:.1f}" fill="{col}" opacity="{op:.2f}"/></g>')


def snow_cap(x, y, r, rot, sx, sy, amt, big=False):
    if amt <= 0.01:
        return ""
    k = amt
    h = (0.55 if big else 0.75) * r * k
    w = r * (0.75 + 0.2 * k)
    top = -r * 0.96
    d = (f"M{-w:.0f} {top + r*0.35:.0f} Q {-w*0.9:.0f} {top - h*0.4:.0f} {-w*0.4:.0f} {top - h*0.6:.0f} "
         f"Q {-w*0.1:.0f} {top - h*1.25:.0f} {w*0.3:.0f} {top - h*0.8:.0f} Q {w*0.95:.0f} {top - h*0.6:.0f} {w:.0f} {top + r*0.35:.0f} "
         f"Q {w*0.5:.0f} {top + r*0.15:.0f} {w*0.2:.0f} {top + r*0.32:.0f} Q 0 {top + r*0.12:.0f} {-w*0.35:.0f} {top + r*0.3:.0f} Q {-w*0.7:.0f} {top + r*0.15:.0f} {-w:.0f} {top + r*0.35:.0f}Z")
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx:.3f} {sy:.3f})">'
            f'<path d="{d}" fill="#ffffff" stroke="#7fb4d8" stroke-width="6" stroke-linejoin="round"/>'
            f'<ellipse cx="{-w*0.35:.0f}" cy="{top - h*0.35:.0f}" rx="{w*0.22:.0f}" ry="{h*0.15+3:.0f}" fill="#e6f5ff"/></g>')


def sweat(x, y, s, t, amt):
    if amt <= 0.02:
        return ""
    o = []
    n = int(2 + 4 * amt)
    for k in range(n):
        ph = (t * (1.3 + 0.2 * k) + k * 0.37) % 1
        side = -1 if k % 2 == 0 else 1
        a = math.radians(-90 + side * (35 + 12 * k))
        r0 = 130 * s
        dist = r0 + 90 * ph * amt
        px = x + dist * math.cos(a)
        py = y + dist * math.sin(a) + 120 * ph * ph
        o.append(f'<path d="M{px:.0f} {py-16:.0f} q12 18 0 26 q-12 -8 0 -26z" fill="#bfefff" stroke="#3a6a8a" stroke-width="3" opacity="{(1-ph)*min(1,amt*1.5):.2f}"/>')
    return "".join(o)


def ice_cube(cx, cy, w, h, grow, crack=0.0, rot=0.0):
    if grow <= 0:
        return ""
    s = eback(cl(grow), 2.2)
    o = [f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.1f}) scale({s:.3f})">']
    o.append(f'<rect x="{-w/2:.0f}" y="{-h/2:.0f}" width="{w:.0f}" height="{h:.0f}" rx="28" fill="#bfe8ff" fill-opacity="0.45" stroke="#5aa8e0" stroke-width="7"/>')
    o.append(f'<rect x="{-w/2+14:.0f}" y="{-h/2+14:.0f}" width="{w-28:.0f}" height="{h-28:.0f}" rx="20" fill="none" stroke="#ffffff" stroke-width="4" opacity="0.6"/>')
    o.append(f'<path d="M{-w/2+30:.0f} {-h/2+40:.0f} l40 -16 M{-w/2+26:.0f} {-h/2+70:.0f} l24 -10 M{w/2-40:.0f} {h/2-40:.0f} l-30 12" stroke="#ffffff" stroke-width="9" stroke-linecap="round" opacity="0.8"/>')
    if crack > 0:
        L = crack
        o.append(f'<path d="M{-w*0.45*L:.0f} {-h*0.05:.0f} L{-w*0.2*L:.0f} {-h*0.18*L:.0f} L0 {h*0.05:.0f} L{w*0.18*L:.0f} {-h*0.25*L:.0f} L{w*0.45*L:.0f} {h*0.1*L:.0f} '
                 f'M0 {h*0.05:.0f} L{-w*0.05:.0f} {h*0.4*L:.0f} M{w*0.18*L:.0f} {-h*0.25*L:.0f} L{w*0.1:.0f} {-h*0.45*L:.0f}" fill="none" stroke="#ffffff" stroke-width="6" stroke-linejoin="round"/>')
    o.append('</g>')
    return "".join(o)


def shards(cx, cy, p):
    if p <= 0 or p >= 1:
        return ""
    o = []
    for k in range(12):
        a = math.radians(-170 + k * 30 + 10 * h01(k, 7))
        v = 260 + 200 * h01(k, 8)
        x = cx + v * p * math.cos(a)
        y = cy + v * p * math.sin(a) + 900 * p * p
        rr = 18 + 16 * h01(k, 9)
        rt = p * 720 * (h01(k, 6) - 0.5)
        o.append(f'<g transform="translate({x:.0f} {y:.0f}) rotate({rt:.0f})"><path d="M{-rr:.0f} 0 L0 {-rr*0.8:.0f} L{rr:.0f} {rr*0.2:.0f} L{-rr*0.2:.0f} {rr*0.7:.0f}Z" '
                 f'fill="#d6f1ff" stroke="#5aa8e0" stroke-width="4" opacity="{1-p:.2f}"/></g>')
    return "".join(o)


def bolt_sparks(x, y, p):
    if p <= 0 or p >= 1:
        return ""
    o = []
    for k in range(7):
        a = math.radians(-180 + k * 30)
        L = 30 + 60 * p
        o.append(f'<path d="M{x+20*math.cos(a):.0f} {y+20*math.sin(a):.0f} l{L*math.cos(a):.0f} {L*math.sin(a):.0f}" stroke="#fff36a" stroke-width="7" stroke-linecap="round" opacity="{1-p:.2f}"/>')
    o.append(f'<circle cx="{x}" cy="{y}" r="{24*(1-p):.0f}" fill="#fff6a8" opacity="{1-p:.2f}"/>')
    return "".join(o)


# ---------------------------------------------------------------- grumpo
def grumpo_state(t):
    g = dict(x=355.0, y=GY, sx=1.0, sy=1.0, rot=0.0, ex="angry", kind=None, red=0.0, look=(1, -0.6),
             rh=None, lh=None, crossed=False, sweat=0.0, cap=0.0, blue=0.0)
    # base: hot, pressing DOWN
    if t < 1.0:
        g["sweat"] = 0.7 * (1 - seg(t, 0.8, 1.0))
        g["red"] = 0.15
        reach = eout(seg(t, 0.0, 0.3)) * (1 - seg(t, 0.92, 1.05))
        if reach > 0:
            push = 10 * press_amt(t, T_GP)
            g["rh"] = (lerp(430, DNB[0] - 18 + push, reach), lerp(GY + 30, DNB[1] + 6, reach))
        sx, sy = squash(t, T_GP[0], 0.15, 0.05)
        g["sx"], g["sy"] = sx, sy
    elif t < 2.25:
        g["ex"], g["kind"] = "none", "bliss"
        g["rot"] = -5 * math.sin(math.pi * seg(t, 1.0, 2.25))
        g["sx"] = 1 + 0.03 * math.sin(t * 6)
        g["sy"] = 1 - 0.03 * math.sin(t * 6)
    elif t < 3.0:
        g["ex"] = "suspicious" if t < 2.7 else "shock"
        g["look"] = (1, 0)
    elif t < T_MASH0:
        g["ex"] = "angry"
        g["look"] = (1, -0.4)
        g["sweat"] = 0.6 * seg(t, 3.0, 3.3)
        g["red"] = 0.25 * seg(t, 3.0, 3.4)
    elif t < T_MASH1 + 0.15:
        g["ex"] = "angry"
        g["x"] = lerp(355, 370, seg(t, T_MASH0, T_MASH0 + 0.1))
        g["red"] = 0.3
        g["sweat"] = 0.5
        m = abs(math.sin((t - T_MASH0) * math.pi * 19))
        g["rh"] = (DNB[0] - 30 + 16 * m, DNB[1] + 8 + 6 * m)
        g["rot"] = 3 * math.sin(t * 60)
    elif t < T_HOPG1:
        g["x"] = 370
        q = seg(t, T_MASH1 + 0.15, T_MASH1 + 0.5)
        g["red"] = 0.3 * (1 - q)
        if t < 5.3:
            g["ex"] = "smug"
            g["crossed"] = True
        else:
            g["ex"], g["kind"] = "none", "bliss"
            g["crossed"] = True
            g["rot"] = -4
        if t > 6.3:
            g["ex"], g["kind"], g["crossed"] = "suspicious", None, True
            g["look"] = (1, -0.6)
    elif t < T_SPR1 + 0.6:
        g["x"] = 370
        sx, sy = squash(t, T_HOPG1, 0.4, 0.35)
        g["sx"], g["sy"] = sx, sy
        g["ex"] = "shock"
        g["look"] = (0, -1) if t < T_SPR0 else (1, -1)
    elif t < T_MELT0:
        g["x"] = 370
        g["ex"] = "angry"
        g["look"] = (1, -0.8)
        g["sweat"] = 0.6 * seg(t, 7.8, 8.2)
        g["red"] = 0.2 * seg(t, 7.8, 8.2)
    elif t < T_GOO0:
        q = eio(seg(t, T_MELT0, T_MELT1))
        g["x"] = 370
        g["sx"] = lerp(1, 1.34, q) + 0.03 * math.sin(t * 5)
        g["sy"] = lerp(1, 0.62, q) - 0.03 * math.sin(t * 5)
        g["ex"], g["kind"] = ("none", "melt") if q > 0.3 else ("shock", None)
        g["look"] = (0.4, 0.6) if t < 9.6 else (1, -0.5)
        g["sweat"] = 1.0
        g["red"] = 0.3
    elif t < T_DOWN1:
        q = eio(seg(t, T_GOO0, T_GOO1))
        g["x"] = lerp(370, GX_F, q)
        g["sx"] = lerp(1.34, 0.8, q)
        g["sy"] = lerp(0.62, 1.42, q)
        g["rot"] = lerp(0, 14, q)
        g["ex"], g["kind"] = ("none", "melt") if q < 0.5 else ("none", "strain")
        g["sweat"] = 0.8
        g["red"] = 0.3 * (1 - seg(t, T_GOO1 + 0.3, T_DOWN1))
        if q > 0.4:
            k = seg(q, 0.4, 1.0)
            g["rh"] = (lerp(GX_F + 60, DNB[0] - 6, k), lerp(GY - 30, DNB[1], k))
    elif t < T_NOTICE:
        g["x"] = GX_F
        # snap back to round with a wobble
        q = seg(t, T_DOWN1, T_SNAP + 0.1)
        sx0, sy0 = lerp(0.8, 1.0, eout(q)), lerp(1.42, 1.0, eout(q))
        wx, wy = wob(t, T_SNAP + 0.05, 0.6, 0.18, 2.0)
        g["sx"], g["sy"] = sx0 * wx, sy0 * wy
        g["rot"] = lerp(14, 0, eout(q))
        if t < T_SNAP + 0.5:
            g["ex"], g["kind"] = "none", "bliss"
        else:
            g["ex"] = "smug"
            g["crossed"] = True
            g["rot"] = -5
            g["look"] = (1, 0.2)
        g["cap"] = eio(seg(t, T_SNAP + 0.3, T_SNAP + 1.0))
    elif t < T_IMP:
        g["x"] = GX_F
        g["ex"] = "shock"
        g["look"] = (1, 0.3)
        g["cap"] = 1.0
        g["rh"] = (GX_F + 150, GY - 40)
    elif t < T_GSPIN1:
        q = eout(seg(t, T_IMP, T_GSPIN1))
        g["x"] = lerp(GX_F, 255, q)
        g["rot"] = -560 * q
        g["ex"], g["kind"] = "none", "dizzy"
        g["cap"] = 1.0 - seg(t, T_IMP, T_IMP + 0.2)
    elif t < T_GBACK0:
        g["x"] = 255
        g["ex"], g["kind"] = "none", "dizzy"
        g["rot"] = 8 * math.sin(t * 20)
    elif t < T_GBACK1:
        q = eio(seg(t, T_GBACK0, T_GBACK1))
        g["x"] = lerp(255, 390, q)
        g["ex"] = "angry"
        g["rot"] = 10 * (1 - q)
    elif t < T_GRAB:
        g["x"] = 390
        g["ex"] = "angry"
        g["look"] = (1, -0.6)
        g["red"] = 0.25
        up, dn = war_presses(t)
        if T_WAR0 - 0.15 <= t < T_WAR1:
            g["rh"] = (DNB[0] - 26 + 12 * dn, DNB[1] + 8 + 4 * dn)
        g["rot"] = 4 * math.sin(t * 40) if T_WAR0 <= t < T_WAR1 else 0
    elif t < T_RIP:
        q = seg(t, T_GRAB, T_RIP)
        g["x"] = lerp(390, 370, q)
        g["rot"] = -10 * q
        g["ex"], g["kind"] = "none", "strain"
        g["red"] = 0.35
        px, py, _, _, _, _ = panel_state(t)
        g["rh"] = (px - 72, py + 20)
    else:
        q = seg(t, T_RIP, T_RIP + 0.35)
        g["x"] = lerp(370, 360, eout(q))
        g["rot"] = lerp(-10, 0, q)
        px, py, prot, _, _, _ = panel_state(t)
        g["rh"] = (px - 70, py + 8)
        if t < T_LOOK:
            g["ex"], g["kind"] = "none", "strain"
            g["red"] = 0.3
            g["x"] += 0.5 * (px - PX)
        else:
            g["ex"] = "shock"
            g["look"] = (0.3, -1)
            if t >= T_EYE1:
                g["look"] = (0.9, 0.7)
            if t >= T_EYE2:
                g["look"] = (1, 0)
        if t >= T_BLAST:
            g["blue"] = 0.35 * seg(t, T_BLAST, T_ICE1)
    # cold blue tint while freezing earlier
    if T_SNAP <= t < T_IMP:
        g["blue"] = 0.0
    g["y"] = FLOOR - GR * g["sy"]
    return g


# ---------------------------------------------------------------- nibbo
def nibbo_state(t):
    n = dict(x=730.0, y=NY, sx=1.0, sy=1.0, rot=0.0, ex="happy", face=None, look=(0, 0),
             lh=None, rh=None, cap=0.0, blue=0.0, cube=0.0, crack=0.0, shades=False)
    if t < 1.0:
        n["ex"] = "nervous" if t < 0.5 else "uhoh"
        n["face"] = "uhoh" if t >= 0.5 else None
        if n["face"]:
            n["ex"] = "none"
        n["look"] = (-1, -0.5)
        n["blue"] = 0.2 * seg(t, 0.6, 1.0)
    elif t < 2.05:
        n["ex"], n["face"] = "none", "chatter"
        n["x"] = 730 + 4 * math.sin(t * 95)
        n["blue"] = 0.3
    elif t < 3.25:
        # hop-presses
        n["ex"], n["face"] = "none", "frown"
        n["look"] = (-1, -1)
        n["blue"] = 0.3 * (1 - seg(t, 2.8, 3.2))
        n["x"] = lerp(730, 670, eio(seg(t, 2.05, 2.15)))
        for ap in T_NP:
            if ap - 0.18 <= t < ap + 0.18:
                q = seg(t, ap - 0.18, ap + 0.18)
                n["y"] = NY - 205 * 4 * q * (1 - q)
                n["sy"] = 1.06
                n["sx"] = 0.95
                n["lh"] = (lerp(n["x"] - 70, UPB[0] + 20, min(1, q * 2.2)), lerp(n["y"], UPB[1] + 4, min(1, q * 2.2)))
        for ap in T_NP:
            sx, sy = squash(t, ap + 0.18, 0.15, 0.15)
            if sx != 1:
                n["sx"], n["sy"] = sx, sy
        if t > 3.1:
            n["ex"], n["face"] = "joy", None
    elif t < T_MASH0:
        n["x"] = 670
        n["ex"] = "joy"
        n["rot"] = 4 * math.sin(t * 8)
    elif t < T_SHAKE0:
        n["x"] = 670 + (5 * math.sin(t * 90) if t > T_SNOW0 + 0.3 else 0)
        if t < T_SNOW0 + 0.3:
            n["ex"] = "wow"
        else:
            n["ex"], n["face"] = "none", "chatter"
        n["blue"] = 0.55 * seg(t, T_SNOW0, T_SNOW0 + 0.8)
        n["cap"] = eio(seg(t, 4.5, 6.0))
    elif t < T_HOPG0:
        q = seg(t, T_SHAKE0, T_SHAKE1)
        n["x"] = 670
        n["rot"] = 22 * math.sin(q * math.pi * 6) * (1 - q)
        n["sx"] = 1 + 0.08 * math.sin(q * math.pi * 12)
        n["ex"], n["face"] = "none", "frown"
        n["look"] = (-1, -0.5)
        n["blue"] = 0.55 * (1 - q * 0.5)
        n["cap"] = 1 - eio(seg(t, T_SHAKE0, T_SHAKE0 + 0.12))
    elif t < T_HOPG1:
        q = seg(t, T_HOPG0, T_HOPG1)
        p = arc(eio(q), (670, NY), (370, GY - GR - NR + 26), 170)
        n["x"], n["y"] = p
        n["rot"] = -200 * q
        n["ex"], n["face"] = "none", "frown"
        n["blue"] = 0.25
    elif t < T_SPR0:
        n["x"], n["y"] = 370, GY - GR * 0.65 - NR + 26
        n["sx"], n["sy"] = 1.25, 0.72
        n["ex"], n["face"] = "none", "frown"
    elif t < T_SPR1:
        q = seg(t, T_SPR0, T_SPR1)
        p = arc(eout(q), (370, GY - GR - NR + 20), (700, 1345), 110)
        n["x"], n["y"] = p
        n["sx"], n["sy"] = 0.9, 1.12
        n["ex"], n["face"] = "none", "frown"
        n["look"] = (-1, -0.3)
    elif t < T_DROP0:
        n["x"], n["y"] = 700, 1345 + 3 * math.sin(t * 9)
        sx, sy = squash(t, T_SPR1, 0.2, 0.15)
        n["sx"], n["sy"] = sx, sy
        n["lh"] = (UPB[0] + 14, UPB[1] + 2)
        n["rh"] = (PX + 66, PY + 60)
        n["ex"], n["face"] = ("none", "frown") if t < 7.9 else ("joy", None)
        n["look"] = (-1, -0.3)
    elif t < T_DROP1:
        q = seg(t, T_DROP0, T_DROP1)
        n["x"], n["y"] = arc(q, (700, 1345), (NX_L, NY), -40)
        n["y"] = lerp(1345, NY, ein(q))
        n["ex"] = "joy"
    elif t < T_SNAP:
        n["x"] = NX_L
        sx, sy = squash(t, T_DROP1, 0.25, 0.2)
        n["sx"], n["sy"] = sx, sy
        if t < T_SHADES:
            n["ex"] = "joy"
        else:
            q = seg(t, T_SHADES, T_SHADES + 0.3)
            n["ex"] = "cool"
            n["rot"] = -16 * eio(q)
            n["sy"] = 1 - 0.05 * eio(q)
            n["sx"] = 1 + 0.03 * eio(q)
            n["rot"] += 2 * math.sin(t * 2.5)
    elif t < T_SLIDE0:
        n["x"] = NX_L
        n["ex"] = "cool"
        n["rot"] = -16
        n["sy"], n["sx"] = 0.95, 1.03
        n["blue"] = 0.5 * seg(t, T_CUBE0, T_CUBE1)
        n["cube"] = seg(t, T_CUBE0, T_CUBE1)
        if T_WIG0 <= t:
            n["rot"] = -16 + 7 * math.sin(t * 45)
    elif t < T_SHAT:
        q = ein(seg(t, T_SLIDE0, T_IMP))
        cxp = NX_L - 100 * q if t < T_IMP else NX_L - 100 - 6 * seg(t, T_IMP, T_IMP + 0.05)
        n["x"] = cxp
        n["ex"] = "cool"
        n["rot"] = -16 + 4 * math.sin(t * 45)
        n["sy"], n["sx"] = 0.95, 1.03
        n["blue"] = 0.5
        n["cube"] = 1.0
        n["crack"] = seg(t, T_CRACK, T_SHAT)
    elif t < T_NCL0:
        q = seg(t, T_SHAT, T_SHAT + 0.3)
        n["x"] = NX_L - 100
        n["y"] = NY - 60 * math.sin(math.pi * q)
        sx, sy = squash(t, T_SHAT + 0.3, 0.2, 0.2)
        n["sx"], n["sy"] = sx, sy
        n["ex"], n["face"] = "none", "dizzy"
        n["blue"] = 0.4 * (1 - seg(t, T_SHAT, T_SHAT + 0.3))
        n["rot"] = 8 * math.sin(t * 20)
    elif t < T_NCL1:
        q = seg(t, T_NCL0, T_NCL1)
        n["x"], n["y"] = arc(eout(q), (NX_L - 100, NY), (700, 1345), 80)
        n["ex"], n["face"] = "none", "frown"
    elif t < T_GRAB:
        n["x"], n["y"] = 700, 1345 + 3 * math.sin(t * 9)
        n["ex"], n["face"] = "none", "frown"
        n["look"] = (-1, -0.3)
        up, dn = war_presses(t)
        n["lh"] = (UPB[0] + 24 - 10 * up, UPB[1] + 2)
        n["rh"] = (PX + 66, PY + 60)
        n["rot"] = 4 * math.sin(t * 40) if T_WAR0 <= t < T_WAR1 else 0
    elif t < T_RIP:
        q = seg(t, T_GRAB, T_RIP)
        n["x"], n["y"] = 700 + 10 * q, 1345
        n["rot"] = 12 * q
        n["ex"], n["face"] = "none", "frown"
        px, py, _, _, _, _ = panel_state(t)
        n["lh"] = (px + 72, py + 10)
        n["rh"] = (px + 72, py + 50)
    else:
        q = seg(t, T_RIP, T_RIP + 0.35)
        n["x"] = lerp(710, 740, eout(q))
        n["y"] = lerp(1345, NY, ein(q))
        sx, sy = squash(t, T_RIP + 0.35, 0.2, 0.2)
        n["sx"], n["sy"] = sx, sy
        px, py, _, _, _, _ = panel_state(t)
        n["lh"] = (px + 70, py + 8)
        if t < T_LOOK:
            n["ex"], n["face"] = "none", "frown"
            n["look"] = (-1, 0)
            n["x"] += 0.5 * (px - PX)
        else:
            n["ex"], n["face"] = "none", "uhoh"
            n["look"] = (-0.4, -1)
            if t >= T_EYE1:
                n["look"] = (-1, 0.7)
            if t >= T_EYE2:
                n["look"] = (-1, 0)
        if t >= T_BLAST:
            n["blue"] = 0.35 * seg(t, T_BLAST, T_ICE1)
    return n


# ---------------------------------------------------------------- camera
CK = [(0.0, (480, 1330, 1.85)), (0.9, (490, 1330, 1.78)), (1.9, (560, 1335, 1.66)), (2.3, (570, 1320, 1.66)),
      (3.3, (560, 1330, 1.66)), (3.65, (490, 1330, 1.85)), (4.4, (500, 1330, 1.8)), (4.9, (550, 1335, 1.64)),
      (6.2, (570, 1335, 1.66)), (6.7, (520, 1300, 1.62)), (7.1, (500, 1290, 1.66)), (7.5, (535, 1300, 1.74)),
      (8.2, (560, 1310, 1.72)), (8.8, (530, 1335, 1.64)), (9.7, (520, 1350, 1.68)), (10.2, (500, 1340, 1.74)),
      (10.8, (500, 1310, 1.82)), (11.5, (520, 1315, 1.78)), (12.1, (590, 1335, 1.6)), (13.5, (595, 1335, 1.64)),
      (14.3, (590, 1335, 1.64)), (14.7, (520, 1335, 1.62)), (15.2, (470, 1335, 1.6)), (15.8, (530, 1310, 1.78)),
      (16.9, (540, 1310, 1.82)), (17.6, (540, 1325, 1.72)), (18.3, (540, 1320, 1.66)), (18.9, (540, 1295, 1.62)),
      (19.3, (540, 1320, 1.6)), (20.3, (540, 1355, 1.66)), (22.0, (550, 1365, 1.72)), (DUR, (550, 1370, 1.76))]
SHAKES = [(T_GP[0], 4, 0.15), (T_MASH0, 7, 0.8), (T_HOPG1, 8, 0.3), (T_SPR1, 6, 0.25), (T_GOO1, 6, 0.25),
          (T_SNAP, 8, 0.35), (T_IMP, 10, 0.35), (T_SHAT, 6, 0.25), (T_RIP, 10, 0.35), (T_ACSH0, 4, 1.15),
          (T_BLAST, 16, 0.6), (T_ICICLE + 0.25, 4, 0.2)]


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
    o = []
    gx, gy = g["x"], g["y"]
    o.append(shadow(gx, FLOOR + 6, 120 * g["sx"]))
    o.append(grumpo(ctx, gx, gy, GS, g["ex"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"], False, 0, None, 0, t))
    if g["kind"]:
        o.append(g_extra(gx, gy, GS, g["rot"], g["sx"], g["sy"], g["kind"], t, g["red"], g["look"]))
    o.append(tint_circle(ctx, gx, gy, GR, g["rot"], g["sx"], g["sy"], "#7ad0ff", g["blue"]))
    o.append(snow_cap(gx, gy, GR, g["rot"], g["sx"], g["sy"], g["cap"], big=True))
    ink = mix_hex(INK, "#3a0505", g["red"])
    gfill = mix_hex(GFILL, "#ff6a52", g["red"])
    shR = (gx + 96 * GS * g["sx"], gy + 26 * GS * g["sy"])
    shL = (gx - 96 * GS * g["sx"], gy + 26 * GS * g["sy"])
    if g["crossed"]:
        o.append(f'<g transform="translate({gx:.1f} {gy:.1f}) rotate({g["rot"]:.1f}) scale({g["sx"]:.3f} {g["sy"]:.3f})">'
                 f'<path d="M-92 50 Q -30 96 46 66" fill="none" stroke="{ink}" stroke-width="13" stroke-linecap="round"/>'
                 f'<path d="M92 50 Q 30 96 -46 66" fill="none" stroke="{ink}" stroke-width="13" stroke-linecap="round"/>'
                 f'<circle cx="46" cy="66" r="15" fill="{gfill}" stroke="{OL}" stroke-width="5"/><circle cx="-46" cy="66" r="15" fill="{gfill}" stroke="{OL}" stroke-width="5"/></g>')
    if g["rh"] is not None:
        hx, hy = g["rh"]
        o.append(arm(shR[0], shR[1], hx, hy, ink, 13, 10) + hand(hx, hy, gfill, OL, 16))
    return "".join(o)


def draw_nibbo(ctx, n, t):
    o = []
    nx, ny = n["x"], n["y"]
    if ny > NY - 250:
        o.append(shadow(nx, FLOOR + 6, 100 * (1 - (NY - ny) / 400)))
    o.append(nibbo(ctx, nx, ny, NR, n["ex"], rot=n["rot"], sx=n["sx"], sy=n["sy"]))
    if n["face"]:
        o.append(n_face(nx, ny, NR, n["rot"], n["sx"], n["sy"], n["face"], t, n["look"]))
    o.append(tint_circle(ctx, nx, ny, NR, n["rot"], n["sx"], n["sy"], "#6ac8ff", n["blue"]))
    o.append(snow_cap(nx, ny, NR, n["rot"], n["sx"], n["sy"], n["cap"]))
    for key, sxk in (("lh", -1), ("rh", 1)):
        if n[key] is not None:
            hx, hy = n[key]
            sh = (nx + sxk * 76 * n["sx"], ny + 8)
            o.append(arm(sh[0], sh[1], hx, hy, NS, 10, 8) + hand(hx, hy, NB, NS, 13))
    return "".join(o)


def frame(t):
    ctx = Ctx()
    g = grumpo_state(t)
    n = nibbo_state(t)
    L = [room(t)]
    L.append(wall_frost(t))
    L.append(ac_unit(t))
    px, py, prot, up_p, dn_p, ripped = panel_state(t)
    if ripped:
        L.append(wire(t, px, py))
    else:
        L.append(panel_svg(px, py, prot, t, up_p, dn_p, frost(t) if t < T_WAR0 else 0))
    L.append(heat_shimmer(t))
    L.append(floor_snow(t))

    # ice cube around Nibbo (behind/around)
    cube_cx, cube_cy = n["x"], FLOOR - 128
    L.append(draw_grumpo(ctx, g, t))
    L.append(draw_nibbo(ctx, n, t))
    if n["cube"] > 0 and t < T_SHAT:
        L.append(ice_cube(cube_cx, cube_cy, 290, 260, n["cube"], n["crack"], -2))
    if T_SHAT <= t < T_SHAT + 0.9:
        L.append(shards(cube_cx, cube_cy, seg(t, T_SHAT, T_SHAT + 0.9)))
        # sunglasses flying off
        q = seg(t, T_SHAT, T_SHAT + 0.9)
        sxp, syp = arc(q, (cube_cx, cube_cy - 20), (cube_cx + 420, FLOOR - 10), 260)
        L.append(f'<g transform="translate({sxp:.0f} {syp:.0f}) rotate({q*900:.0f})"><rect x="-30" y="-10" width="26" height="16" rx="6" fill="#111"/><rect x="4" y="-10" width="26" height="16" rx="6" fill="#111"/><path d="M-4 -4 h8" stroke="#111" stroke-width="4"/></g>')
    if ripped:
        L.append(panel_svg(px, py, prot, t, 0, 0))
        # hands over the panel edges
        L.append(hand(px - 70, py + 8, mix_hex(GFILL, "#ff6a52", g["red"]), OL, 16) + hand(px + 70, py + 8, NB, NS, 13))
    if T_GRAB <= t < T_RIP:
        L.append(panel_svg(px, py, prot, t, 0, 0))
        L.append(hand(px - 72, py + 20, mix_hex(GFILL, "#ff6a52", g["red"]), OL, 16) + hand(px + 72, py + 10, NB, NS, 13) + hand(px + 72, py + 50, NB, NS, 13))

    # airflow + snow (in front)
    L.append(airflow(t))
    L.append(snowfall(t))
    L.append(sweat(g["x"], g["y"], GS * max(g["sx"], g["sy"]), t, g["sweat"]))

    # snow shaken off Nibbo
    if T_SHAKE0 <= t < T_SHAKE0 + 0.6:
        q = seg(t, T_SHAKE0, T_SHAKE0 + 0.6)
        for k in range(10):
            a = math.radians(-160 + k * 16)
            v = 220 + 120 * h01(k, 12)
            x = 670 + v * q * math.cos(a)
            y = NY - 90 + v * q * math.sin(a) + 500 * q * q
            L.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{16-8*q:.0f}" fill="#ffffff" stroke="#8fbfe0" stroke-width="3" opacity="{1-q:.2f}"/>')

    # final big ice block
    if t >= T_BLAST:
        q = seg(t, T_BLAST, T_ICE1)
        top = lerp(FLOOR, 1365, eout(q))
        L.append(f'<rect x="170" y="{top:.0f}" width="740" height="{FLOOR+14-top:.0f}" rx="34" fill="#bfe8ff" fill-opacity="0.42" stroke="#5aa8e0" stroke-width="8"/>')
        if q >= 1:
            L.append(f'<rect x="186" y="1381" width="708" height="317" rx="26" fill="none" stroke="#ffffff" stroke-width="5" opacity="0.6"/>'
                     '<path d="M215 1420 l60 -24 M210 1460 l30 -12 M860 1650 l-50 20 M840 1610 l-24 10" stroke="#ffffff" stroke-width="10" stroke-linecap="round" opacity="0.8"/>'
                     '<path d="M170 1400 Q 300 1340 540 1352 Q 780 1340 910 1400 L910 1380 Q 780 1326 540 1338 Q 300 1326 170 1380Z" fill="#ffffff" stroke="#8fc3e8" stroke-width="4"/>')
        # falling icicle
        if T_ICICLE - 0.35 <= t < T_ICICLE + 0.4:
            k = seg(t, T_ICICLE - 0.35, T_ICICLE)
            iy = lerp(ACY + 70, 1330, ein(k))
            if t < T_ICICLE:
                L.append(f'<path d="M{ACX-11} {iy:.0f} L{ACX+11} {iy:.0f} L{ACX} {iy+56:.0f}Z" fill="#dff4ff" stroke="#6aa8d8" stroke-width="3"/>')
            else:
                b = seg(t, T_ICICLE, T_ICICLE + 0.4)
                bx, by = arc(b, (ACX, 1330), (ACX + 90, 1350), 70)
                L.append(f'<g transform="translate({bx:.0f} {by:.0f}) rotate({b*400:.0f})"><path d="M-11 -20 L11 -20 L0 36Z" fill="#dff4ff" stroke="#6aa8d8" stroke-width="3" opacity="{1-b:.2f}"/></g>')
        if t < T_ICE1:
            L.append(f'<rect x="-400" y="{top:.0f}" width="1900" height="40" fill="#ffffff" opacity="0.5"/>')

    # ---- effects
    for x in T_GP:
        L.append(impact(DNB[0] - 30, DNB[1], seg(t, x, x + 0.16), "#bfeaff"))
    for x in T_NP:
        L.append(impact(UPB[0] + 30, UPB[1] - 10, seg(t, x, x + 0.16), "#ffd0a0"))
    if T_MASH0 <= t < T_MASH1:
        L.append(speed_lines(DNB[0] - 50, DNB[1] + 20, 200, 0.9))
        L.append(impact(DNB[0] - 20, DNB[1], ((t - T_MASH0) * 6) % 1, "#bfeaff"))
    L.append(impact(370, GY - GR, seg(t, T_HOPG1, T_HOPG1 + 0.22), "#ffffff"))
    L.append(impact(UPB[0] + 40, UPB[1], seg(t, T_SPR1, T_SPR1 + 0.22), "#ffd0a0"))
    if T_GOO1 <= t < T_GOO1 + 0.3:
        q = seg(t, T_GOO1, T_GOO1 + 0.3)
        L.append(impact(DNB[0] - 10, DNB[1], q, "#bfeaff"))
    if T_HOLD1 - 0.8 <= t < T_HOLD1:
        L.append(symbol(PX + 140, PY - 150, "!", seg(t, T_HOLD1 - 0.8, T_HOLD1 + 0.1), "#ff6a2a"))
    L.append(symbol(g["x"] + 60, g["y"] - 230, "!", seg(t, 2.7, 3.3)))
    L.append(symbol(n["x"] + 10, n["y"] - 190, "!", seg(t, T_MASH0 + 0.1, T_MASH0 + 0.7), "#3a7ad6"))
    L.append(symbol(g["x"] + 40, g["y"] - 220, "!", seg(t, T_NOTICE, T_NOTICE + 0.45)))
    L.append(impact(GX_F + 125, GY, seg(t, T_IMP, T_IMP + 0.25), "#ffffff"))
    if T_IMP <= t < T_GSPIN1:
        L.append(speed_lines(g["x"] + 150, g["y"], 180, 1.0))
    if T_GBACK0 <= t < T_GBACK1:
        L.append(speed_lines(g["x"] - 150, g["y"], 0, 1.0))
    if T_WAR0 <= t < T_WAR1:
        i = int((t - T_WAR0) / WAR_DT)
        f = ((t - T_WAR0) % WAR_DT) / WAR_DT
        L.append(impact(UPB[0] + 30 if i % 2 == 0 else DNB[0] - 30, UPB[1] if i % 2 == 0 else DNB[1], f, "#ffd0a0" if i % 2 == 0 else "#bfeaff"))
    L.append(bolt_sparks(PX, PY, seg(t, T_RIP, T_RIP + 0.4)))
    if T_RIP + 0.2 <= t < T_BLAST and int(t * 8) % 3 == 0:
        L.append(bolt_sparks(PX + 10, PY - 20, ((t * 8) % 1)))
    L.append(symbol(ACX + 260, ACY - 30, "!", seg(t, T_LOOK - 0.1, T_LOOK + 0.6)))
    if T_ACSH0 <= t < T_BLAST:
        for k in range(3):
            q = ((t - T_ACSH0) * 1.5 + k / 3) % 1
            col = "#7ad0ff" if k % 2 else "#ffb070"
            L.append(f'<circle cx="{ACX - 160 + k*160:.0f}" cy="{ACY + 70 + 40*q:.0f}" r="{12+30*q:.0f}" fill="{col}" opacity="{0.6*(1-q):.2f}"/>')
        for k, dx in enumerate((-250, 250)):
            w = 8 * math.sin(t * 40 + k)
            L.append(f'<path d="M{ACX+dx:.0f} {ACY-30:.0f} q{w:.0f} 14 0 28 q{-w:.0f} 14 0 28" fill="none" stroke="{OL}" stroke-width="6" stroke-linecap="round"/>')
    if T_BLAST <= t < T_BLAST + 0.6:
        q = seg(t, T_BLAST, T_BLAST + 0.6)
        L.append(f'<path d="M{ACX-200} {ACY+60} L{ACX+200} {ACY+60} L{ACX+560} 1760 L{ACX-560} 1760Z" fill="#dff4ff" opacity="{0.85*(1-q):.2f}"/>')
        for k in range(14):
            a = math.radians(20 + k * 10)
            L1 = 300 + 700 * q
            L.append(f'<path d="M{ACX} {ACY+60} l{L1*math.cos(a):.0f} {L1*math.sin(a):.0f}" stroke="#ffffff" stroke-width="10" stroke-linecap="round" opacity="{0.9*(1-q):.2f}"/>')
    if T_DISP24 <= t < T_DISP24 + 0.7:
        L.append(star_twinkle(px + 90, py - 110, seg(t, T_DISP24, T_DISP24 + 0.7)))

    # ---- global temperature tint
    c, h = cold(t), hot(t)
    if t >= T_BLAST:
        c = 1.0
    tint = ""
    if c > 0.01:
        tint += f'<rect x="-900" y="-400" width="2900" height="3000" fill="#7cc8ff" opacity="{0.2*c:.3f}"/>'
    if h > 0.01:
        tint += f'<rect x="-900" y="-400" width="2900" height="3000" fill="#ff9a3a" opacity="{0.2*h:.3f}"/>'
    L.append(tint)

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    flash = ""
    if T_BLAST <= t < T_BLAST + 0.4:
        flash = f'<rect width="{W}" height="{H}" fill="#ffffff" opacity="{0.9*(1-seg(t, T_BLAST, T_BLAST+0.4)):.2f}"/>'
    frost_vig = ""
    fv = max(frost(t) * 0.8, 1.0 if t >= T_BLAST else 0)
    if fv > 0:
        frost_vig = f'<rect width="{W}" height="{H}" fill="url(#frostvig)" opacity="{fv:.2f}"/>'
    defs = (DEFS2 + "".join(ctx.defs)
            + '<radialGradient id="vig" cx="0.5" cy="0.55" r="0.78"><stop offset="0.6" stop-color="#1a0f20" stop-opacity="0"/><stop offset="1" stop-color="#1a0f20" stop-opacity="0.35"/></radialGradient>'
            + '<radialGradient id="hotglow"><stop offset="0" stop-color="#ffd27a" stop-opacity="0.6"/><stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>'
            + '<radialGradient id="frostvig" cx="0.5" cy="0.6" r="0.75"><stop offset="0.62" stop-color="#ffffff" stop-opacity="0"/><stop offset="1" stop-color="#e8f7ff" stop-opacity="0.75"/></radialGradient>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{defs}</defs><g transform="{tr}">{"".join(L)}</g>'
           f'{frost_vig}<rect width="{W}" height="{H}" fill="url(#vig)"/>{flash}</svg>')
    return overlay(svg, hook_title(t + 0.12, "Too hot? Too cold?", "THERMOSTAT WAR"))


def build_sfx():
    # opening: grumpo taps DOWN
    sfx(0.0, "whoosh", 0.5, 1.2)
    sfx(0.05, "pant", 0.4, 1.0)
    for x in T_GP:
        sfx(x, "beep", 0.9, 0.9)
        sfx(x, "tap", 0.5, 1.0)
    sfx(0.95, "ac_hum", 0.5, 1.1)
    sfx(1.0, "wind", 0.35, 1.3)
    sfx(1.05, "cool", 0.5, 1.0)
    sfx(1.2, "chatter", 0.8, 1.0)
    sfx(1.9, "chatter", 0.6, 1.05)
    # nibbo hop-presses UP
    for x in T_NP:
        sfx(x - 0.18, "hop", 0.5, 1.2)
        sfx(x, "beep", 0.9, 1.25)
        sfx(x + 0.18, "plop", 0.4, 1.3)
    sfx(3.05, "ac_hum", 0.5, 0.9)
    sfx(3.15, "cheer", 0.25, 1.5)
    sfx(2.75, "gasp", 0.5, 1.0)
    sfx(3.3, "grumble", 0.6, 0.9)
    # mash
    k = 0
    tt = T_MASH0
    while tt < T_MASH1:
        sfx(tt, "beep", 0.55, 0.85 - 0.01 * k)
        sfx(tt, "tap", 0.35, 1.1)
        tt += 1 / 19
        k += 1
    sfx(T_MASH0 + 0.1, "gasp", 0.6, 1.3)
    sfx(T_SNOW0, "wind", 0.9, 0.9)
    sfx(T_SNOW0 + 1.2, "wind", 0.8, 0.85)
    sfx(T_SNOW0 + 0.1, "freeze", 0.4, 1.2)
    sfx(T_SNOW0 + 0.5, "chatter", 0.9, 1.0)
    sfx(T_SNOW0 + 1.4, "chatter", 0.9, 0.95)
    sfx(5.35, "cool", 0.5, 0.9)
    # shake off + hop on head + spring
    sfx(T_SHAKE0, "shaker", 0.6, 1.4)
    sfx(T_SHAKE0 + 0.05, "poof", 0.6, 1.2)
    sfx(T_HOPG0, "boing", 0.6, 1.2)
    sfx(T_HOPG1, "squish", 0.8, 0.8)
    sfx(T_HOPG1 + 0.02, "bonk", 0.6, 0.9)
    sfx(T_SPR0, "boing", 0.9, 0.9)
    sfx(T_SPR1, "slap", 0.7, 1.2)
    sfx(T_SPR1 + 0.02, "beep", 0.9, 1.3)
    for i in range(10):
        sfx(T_SPR1 + 0.1 + i * 0.08, "beep", 0.45, 1.3 + 0.03 * i)
    sfx(7.9, "rise", 0.5, 1.0)
    sfx(8.15, "sizzle", 0.7, 1.0)
    sfx(8.3, "splash_small", 0.6, 1.0)
    sfx(8.45, "pour", 0.4, 1.1)
    # drop + shades
    sfx(T_DROP1, "plop", 0.6, 1.1)
    sfx(T_SHADES, "cool", 0.8, 1.0)
    sfx(T_SHADES + 0.4, "laugh", 0.3, 1.5)
    # melt
    sfx(T_MELT0 + 0.2, "deflate", 0.7, 0.8)
    sfx(T_MELT0 + 0.7, "squish", 0.5, 0.7)
    sfx(9.1, "pant", 0.6, 0.85)
    sfx(9.3, "drip", 0.6, 1.0)
    sfx(9.75, "drip", 0.5, 1.2)
    sfx(10.0, "stretch", 0.8, 0.9)
    sfx(10.4, "strain", 0.6, 0.9)
    sfx(T_GOO1, "splat", 0.8, 1.1)
    sfx(T_GOO1 + 0.02, "beep", 0.9, 0.8)
    for i in range(8):
        sfx(T_GOO1 + 0.1 + i * 0.1, "beep", 0.45, 0.8 - 0.02 * i)
    sfx(T_DOWN1 - 0.15, "wind", 0.9, 0.8)
    sfx(T_SNAP - 0.05, "freeze", 1.0, 1.0)
    sfx(T_SNAP + 0.05, "boing", 0.8, 0.8)
    sfx(T_CUBE0, "freeze", 0.7, 1.3)
    sfx(T_CUBE1, "clank", 0.4, 1.8)
    sfx(12.4, "cool", 0.5, 0.85)
    sfx(12.6, "wind", 0.5, 0.9)
    # cube wiggle + slide + impact
    sfx(T_WIG0, "shaker", 0.5, 0.9)
    sfx(T_SLIDE0, "squeak_slide", 0.7, 0.8)
    sfx(T_SLIDE0 + 0.05, "drag", 0.5, 1.3)
    sfx(T_NOTICE, "gasp", 0.7, 0.85)
    sfx(T_IMP, "bonk", 1.0, 0.8)
    sfx(T_IMP + 0.02, "clank", 0.6, 1.4)
    sfx(T_IMP + 0.05, "squeak_slide", 0.7, 1.2)
    sfx(T_IMP + 0.1, "whoosh", 0.6, 1.3)
    sfx(T_CRACK, "snap", 0.6, 1.4)
    sfx(T_SHAT, "ice_shatter", 1.0, 1.0)
    sfx(T_SHAT + 0.3, "boing", 0.5, 1.4)
    sfx(T_GSPIN1, "thud", 0.6, 1.0)
    sfx(T_NCL0, "hop", 0.5, 1.2)
    sfx(T_GBACK0, "zoom", 0.7, 1.2)
    # button war
    for i in range(int((T_WAR1 - T_WAR0) / WAR_DT) + 1):
        tt = T_WAR0 + i * WAR_DT
        if tt < T_WAR1:
            sfx(tt, "beep", 0.7, 1.3 if i % 2 == 0 else 0.8)
            sfx(tt, "tap", 0.4, 1.0)
    sfx(T_WAR0 + 0.2, "grumble", 0.6, 0.85)
    sfx(T_WAR0 + 0.3, "ac_hum", 0.5, 1.4)
    # grab + rip
    sfx(T_GRAB, "strain", 0.8, 0.9)
    sfx(T_GRAB + 0.1, "creak", 0.6, 1.2)
    sfx(T_RIP, "rip", 0.9, 0.8)
    sfx(T_RIP + 0.02, "zap", 0.9, 1.0)
    sfx(T_RIP + 0.05, "boing", 0.5, 1.6)
    sfx(T_RIP + 0.3, "thud", 0.6, 1.1)
    sfx(T_RIP + 0.4, "zap", 0.5, 1.3)
    sfx(T_RIP + 0.8, "zap", 0.4, 1.1)
    sfx(T_RIP + 0.2, "strain", 0.5, 1.1)
    # AC freaks out
    sfx(T_ACSH0, "pipe_rattle", 0.9, 1.0)
    sfx(T_ACSH0 + 0.5, "pipe_rattle", 0.9, 0.9)
    sfx(T_ACSH0 + 0.1, "rumble", 0.7, 1.0)
    sfx(T_LOOK, "gasp", 0.8, 1.0)
    sfx(T_LOOK + 0.05, "gasp", 0.6, 1.4)
    sfx(T_BLAST - 0.35, "inhale", 0.7, 0.8)
    sfx(T_BLAST, "blast", 1.0, 1.0)
    sfx(T_BLAST + 0.05, "freeze", 1.0, 0.85)
    sfx(T_BLAST + 0.12, "clank", 0.5, 0.7)
    sfx(T_ICE1, "freeze", 0.5, 1.4)
    sfx(T_BLAST + 0.4, "wind", 0.6, 0.8)
    sfx(T_ICICLE, "tink", 1.0, 1.0)
    sfx(T_ICICLE + 0.15, "tink", 0.6, 1.3)
    sfx(T_DISP24 - 0.3, "blip", 0.4, 1.2)
    sfx(T_DISP24, "ding", 0.9, 1.0)
    sfx(T_DISP24 + 0.05, "shine", 0.5, 1.2)
    sfx(T_ACOFF, "power_off", 0.6, 0.7)
    sfx(T_EYE1, "slide_down", 0.35, 1.4)
    sfx(T_EYE2, "slide_up", 0.35, 1.2)
    sfx(T_EYE2 + 0.25, "chatter", 0.6, 0.95)
