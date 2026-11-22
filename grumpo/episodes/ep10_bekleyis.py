"""Grumpo & Nibbo — Episode 10: The 13-Year Wait (living room, game launch, 60 fps).

Grumpo has waited 13 years for the big new game: calendar pages rip by (YEAR 2013 -> 2026), a
cobweb grows on him. Doorbell! The game arrives, he leaps, slams the disc in, the download crawls
to 99% ... Nibbo strolls in and unplugs the console to charge his phone. Power off, back to 0%.
They wait together, 100%! Grumpo jumps for joy -> the screen flips to UPDATE 0%. Grumpo falls
flat, the controller bonks his face, the calendar rips to 2027 and the spider starts a new web.
(No game logos or characters are shown; only the generic "new game" box with a sunset palm.)
"""
import math, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow
from hook import overlay, hook_title, counter

W, H, FPS, DUR = 1080, 1920, 60, 23.8
FLOOR = 1700
NR = 112
NG = FLOOR - NR
GS = 0.92
GR = 120
GX_SEAT, GY_SEAT = 830, 1430
GY_FLOOR = FLOOR - GR

TV = (210, 1170, 340, 290)        # x, y, w, h
CAB = (180, 1470, 400, 230)
CONSOLE = (390, 1560)
SOCKET = (760, 1626)
CAL = (615, 1135, 170, 175)

TEARS = [0.45 + k * 0.4 for k in range(13)]   # 2013 -> 2026
T_BELL = 5.85
T_SLIDE0, T_SLIDE1 = 5.95, 6.45
T_LEAP0, T_LEAP1 = 6.5, 7.05
T_LID = 7.15
T_CASE0, T_CASE1 = 7.3, 7.6
T_INSERT0, T_INSERT1 = 7.7, 8.05
T_TVON = 8.2
DL0, DL1 = 8.4, 12.15
N_IN0, N_IN1 = 10.0, 11.4
T_UNPLUG = 12.25
T_TVOFF = 12.3
T_REPLUG = 14.0
T_TVON2 = 14.2
DL2_0, DL2_1 = 14.6, 17.5
T_DONE = 17.55
T_JUMP0, T_JUMP1 = 17.8, 18.6
T_UPDATE = 18.85
T_FALL0, T_FALL1 = 19.7, 20.3
T_PADBONK = 20.7
T_TEAR_END = 21.6
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


def arm(x0, y0, x1, y1, col, w=11, sag=26):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag
    return f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


# ---------------------------------------------------------------- state helpers
def year_at(t):
    y = 2013 + sum(1 for tt in TEARS if t >= tt)
    if t >= T_TEAR_END:
        y += 1
    return y


def last_tear(t):
    lt = None
    for tt in TEARS + [T_TEAR_END]:
        if t >= tt:
            lt = tt
    return lt


def download(t):
    """returns (mode, pct). mode: idle/off/dl/done/update"""
    if t < T_TVON:
        return "idle", 0
    if t < T_TVOFF:
        x = seg(t, DL0, DL1)
        return "dl", int(99 * (1 - (1 - x) ** 1.6))
    if t < T_TVON2:
        return "off", 0
    if t < T_DONE:
        return "dl", int(99 * eio(seg(t, DL2_0, DL2_1)))
    if t < T_UPDATE:
        return "done", 100
    return "update", 0


# ---------------------------------------------------------------- props
def room(t):
    o = [f'<rect x="-700" y="-700" width="2600" height="{FLOOR+700}" fill="#efe1f6"/>']
    for x in range(-700, 2000, 70):
        o.append(f'<rect x="{x}" y="-700" width="26" height="{FLOOR+700}" fill="#e6d4f0"/>')
    # wall shelf with plant + picture
    o.append('<g transform="translate(-40 110)">')
    o.append(f'<rect x="830" y="1080" width="210" height="16" rx="6" fill="#b98552" stroke="{OL}" stroke-width="5"/>'
             f'<path d="M870 1080 q-30 -60 0 -110 q20 40 10 110z M890 1080 q10 -80 50 -120 q6 70 -40 120z" fill="#5aa957" stroke="{OL}" stroke-width="4"/>'
             f'<path d="M850 1080 h70 l-10 -46 h-50z" fill="#e0794f" stroke="{OL}" stroke-width="5"/>'
             f'<rect x="950" y="1000" width="70" height="80" rx="6" fill="#ffd36a" stroke="{OL}" stroke-width="5"/>'
             '<rect x="960" y="1010" width="50" height="60" fill="#bfe6ff"/><circle cx="985" cy="1035" r="10" fill="#fff6c8"/></g>')
    # baseboard + floor
    o.append(f'<rect x="-700" y="{FLOOR-34}" width="2600" height="34" fill="#ffffff" stroke="{OL}" stroke-width="5"/>')
    o.append(f'<rect x="-700" y="{FLOOR}" width="2600" height="900" fill="#c99462"/>')
    for k, y in enumerate(range(FLOOR + 50, FLOOR + 900, 70)):
        o.append(f'<line x1="-700" y1="{y}" x2="2000" y2="{y}" stroke="#b27b4b" stroke-width="5"/>')
        off = (k * 170) % 340
        for x in range(-700 + off, 2000, 340):
            o.append(f'<line x1="{x}" y1="{y-70}" x2="{x}" y2="{y}" stroke="#b27b4b" stroke-width="4"/>')
    o.append(f'<line x1="-700" y1="{FLOOR}" x2="2000" y2="{FLOOR}" stroke="{OL}" stroke-width="6"/>')
    o.append(f'<rect x="300" y="{FLOOR+12}" width="760" height="40" rx="20" fill="#3fb3a8" stroke="{OL}" stroke-width="5"/>'
             f'<path d="M340 {FLOOR+32} h680" stroke="#ffe08a" stroke-width="6" stroke-dasharray="22 16"/>')
    return "".join(o)


def socket(plugged):
    x, y = SOCKET
    o = [f'<rect x="{x-26}" y="{y-30}" width="52" height="60" rx="10" fill="#ffffff" stroke="{OL}" stroke-width="5"/>',
         f'<circle cx="{x-9}" cy="{y-4}" r="4" fill="{OL}"/><circle cx="{x+9}" cy="{y-4}" r="4" fill="{OL}"/>']
    return "".join(o)


def plug(x, y, rot=0, col="#2b2b33"):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">'
            f'<rect x="-16" y="-20" width="32" height="34" rx="8" fill="{col}" stroke="{OL}" stroke-width="4"/>'
            f'<path d="M-7 -20 v-10 M7 -20 v-10" stroke="#c9ccd6" stroke-width="5" stroke-linecap="round"/></g>')


def cord(x0, y0, x1, y1, col="#2b2b33"):
    my = max(y0, y1) + 40
    return (f'<path d="M{x0:.1f} {y0:.1f} C {x0+60:.1f} {my:.1f}, {x1-60:.1f} {my:.1f}, {x1:.1f} {y1:.1f}" fill="none" stroke="{OL}" stroke-width="11" stroke-linecap="round"/>'
            f'<path d="M{x0:.1f} {y0:.1f} C {x0+60:.1f} {my:.1f}, {x1-60:.1f} {my:.1f}, {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="6" stroke-linecap="round"/>')


def cabinet():
    x, y, w, h = CAB
    return (f'<g stroke="{OL}" stroke-width="6"><rect x="{x}" y="{y}" width="{w}" height="{h-14}" rx="10" fill="#b98552"/>'
            f'<rect x="{x+20}" y="{y+40}" width="{w-40}" height="{h-80}" rx="8" fill="#8a5d34"/></g>'
            f'<rect x="{x+14}" y="{y+8}" width="{w-28}" height="12" rx="6" fill="#d8a46a"/>')


def console(on, t):
    x, y = CONSOLE
    led = "#3ce07a" if on else "#5a5a66"
    o = [f'<rect x="{x-110}" y="{y-34}" width="220" height="68" rx="16" fill="#f4f5f8" stroke="{OL}" stroke-width="6"/>',
         f'<rect x="{x-80}" y="{y-6}" width="110" height="10" rx="5" fill="#2b2b33"/>',
         f'<circle cx="{x+70}" cy="{y}" r="9" fill="{led}" stroke="{OL}" stroke-width="3"/>']
    if on:
        o.append(f'<circle cx="{x+70}" cy="{y}" r="20" fill="#3ce07a" opacity="{0.25 + 0.15*math.sin(t*6):.2f}"/>')
    return "".join(o)


def case_svg(x, y, rot=0, s=1.0):
    gid = "caseg"
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            f'<rect x="-46" y="-60" width="92" height="120" rx="8" fill="#1f6fd6" stroke="{OL}" stroke-width="6"/>'
            f'<rect x="-38" y="-46" width="76" height="98" rx="4" fill="url(#{gid})"/>'
            '<circle cx="12" cy="0" r="16" fill="#ffe36a"/>'
            '<path d="M-38 30 Q 0 16 38 30 V52 H-38Z" fill="#3a1f5a"/>'
            '<path d="M-18 50 Q -16 10 -8 -14" stroke="#3a1f5a" stroke-width="5" fill="none"/>'
            '<path d="M-8 -14 q-22 -4 -28 8 M-8 -14 q-16 -14 -32 -6 M-8 -14 q8 -16 26 -12 M-8 -14 q20 -2 24 12" stroke="#3a1f5a" stroke-width="6" fill="none" stroke-linecap="round"/>'
            '<rect x="-46" y="-60" width="92" height="14" rx="6" fill="#0f4fa8"/></g>')


CASE_DEF = ('<linearGradient id="caseg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ff5fa8"/>'
            '<stop offset="0.55" stop-color="#ff9a4a"/><stop offset="1" stop-color="#ffd86a"/></linearGradient>'
            '<linearGradient id="tvsun" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3a1f7a"/>'
            '<stop offset="0.6" stop-color="#ff5fa8"/><stop offset="1" stop-color="#ffb04a"/></linearGradient>')


def package(x, y, lid=0.0, rot=0):
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">',
         f'<rect x="-80" y="-70" width="160" height="70" rx="6" fill="#d9a066" stroke="{OL}" stroke-width="6"/>',
         '<rect x="-14" y="-70" width="28" height="70" fill="#f2d39a"/>',
         f'<path d="M-50 -40 h26 M-50 -28 h18" stroke="#9a6a3a" stroke-width="5" stroke-linecap="round"/>']
    a = -130 * lid
    o.append(f'<g transform="translate(-80 -70) rotate({a:.1f})"><rect x="0" y="-10" width="80" height="12" rx="4" fill="#e8b47a" stroke="{OL}" stroke-width="5"/></g>')
    o.append(f'<g transform="translate(80 -70) rotate({-a:.1f})"><rect x="-80" y="-10" width="80" height="12" rx="4" fill="#e8b47a" stroke="{OL}" stroke-width="5"/></g>')
    o.append('</g>')
    return "".join(o)


def tv(t):
    x, y, w, h = TV
    mode, pct = download(t)
    o = [f'<rect x="{x+w/2-50}" y="{y+h}" width="100" height="14" fill="#2b2b33" stroke="{OL}" stroke-width="5"/>',
         f'<rect x="{x-14}" y="{y-14}" width="{w+28}" height="{h+28}" rx="18" fill="#2b2b33" stroke="{OL}" stroke-width="7"/>']
    sx, sy, sw, shh = x, y, w, h
    if mode == "idle":
        o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{shh}" rx="6" fill="#1a1a24"/>')
        # hourglass waiting icon
        cx, cy = sx + sw / 2, sy + shh / 2
        a = (t * 90) % 180 if t < 6.0 else 0
        o.append(f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({a:.1f})">'
                 '<path d="M-34 -50 H34 L4 0 L34 50 H-34 L-4 0Z" fill="#3a3a4c" stroke="#8a8aa8" stroke-width="6" stroke-linejoin="round"/>'
                 '<path d="M-20 -40 H20 L2 -8Z" fill="#ffcf5a"/><path d="M-22 44 H22 L0 26Z" fill="#ffcf5a"/></g>')
    elif mode == "off":
        k = t - T_TVOFF
        if k < 0.25:
            p = k / 0.25
            o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{shh}" rx="6" fill="#0c0c12"/>')
            o.append(f'<rect x="{sx + sw*0.5*p:.1f}" y="{sy + shh/2 - 6*(1-p):.1f}" width="{sw*(1-p):.1f}" height="{max(2, 12*(1-p)):.1f}" fill="#ffffff"/>')
        else:
            o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{shh}" rx="6" fill="#0c0c12"/>'
                     f'<path d="M{sx+30} {sy+30} L{sx+90} {sy+20} L{sx+60} {sy+90}Z" fill="#ffffff" opacity="0.08"/>')
    else:
        o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{shh}" rx="6" fill="url(#tvsun)"/>')
        cx = sx + sw / 2
        o.append(f'<circle cx="{cx+60:.1f}" cy="{sy+120}" r="40" fill="#ffe36a" opacity="0.95"/>'
                 f'<path d="M{sx} {sy+190} Q {cx} {sy+165} {sx+sw} {sy+190} V{sy+shh} H{sx}Z" fill="#2a1450"/>'
                 f'<path d="M{sx+70} {sy+200} Q {sx+74} {sy+130} {sx+92} {sy+86}" stroke="#2a1450" stroke-width="8" fill="none"/>'
                 f'<path d="M{sx+92} {sy+86} q-36 -6 -48 12 M{sx+92} {sy+86} q-26 -24 -52 -10 M{sx+92} {sy+86} q14 -26 42 -20 M{sx+92} {sy+86} q32 -2 38 22" '
                 'stroke="#2a1450" stroke-width="10" fill="none" stroke-linecap="round"/>')
        # bar panel
        by = sy + shh - 58
        o.append(f'<rect x="{sx+16}" y="{by-8}" width="{sw-32}" height="50" rx="10" fill="#14141e" opacity="0.85"/>')
        bw = sw - 64
        fill = bw * pct / 100
        col = "#3ce07a" if mode != "update" else "#ffb02a"
        if mode == "update":
            # rotating update arrows
            a = t * 260
            o.append(f'<g transform="translate({cx:.1f} {sy+95}) rotate({a:.1f})">'
                     '<path d="M-34 -8 A34 34 0 0 1 26 -22" fill="none" stroke="#ffffff" stroke-width="12" stroke-linecap="round"/>'
                     '<path d="M34 8 A34 34 0 0 1 -26 22" fill="none" stroke="#ffffff" stroke-width="12" stroke-linecap="round"/>'
                     '<path d="M18 -40 L34 -18 L8 -12Z" fill="#ffffff"/><path d="M-18 40 L-34 18 L-8 12Z" fill="#ffffff"/></g>')
            blink = 0.6 + 0.4 * math.sin(t * 10)
            o.append(f'<rect x="{sx+32}" y="{by+4}" width="{bw}" height="16" rx="8" fill="#3a3a4c" opacity="{blink:.2f}"/>')
        else:
            o.append(f'<rect x="{sx+32}" y="{by+4}" width="{bw}" height="16" rx="8" fill="#3a3a4c"/>'
                     f'<rect x="{sx+32}" y="{by+4}" width="{fill:.1f}" height="16" rx="8" fill="{col}"/>')
        if mode == "done":
            k = t - T_DONE
            for i in range(10):
                a = i * 0.63
                rr = 30 + 160 * min(1, k * 1.6)
                px = cx + rr * math.cos(a)
                py = sy + 100 + rr * math.sin(a) * 0.6
                if sx < px < sx + sw and sy < py < sy + shh:
                    c = ["#ffe36a", "#3ce07a", "#ff5fa8", "#4ac0ff"][i % 4]
                    o.append(f'<rect x="{px-6:.1f}" y="{py-6:.1f}" width="12" height="12" fill="{c}" transform="rotate({i*30 + k*300:.0f} {px:.1f} {py:.1f})"/>')
    # screen glare
    o.append(f'<path d="M{x+16} {y+16} L{x+80} {y+16} L{x+16} {y+80}Z" fill="#ffffff" opacity="0.12"/>')
    return "".join(o)


def calendar(t):
    x, y, w, h = CAL
    yr = year_at(t)
    o = [f'<circle cx="{x+w/2}" cy="{y-18}" r="7" fill="{OL}"/>',
         f'<path d="M{x+w/2} {y-18} L{x+30} {y+8} M{x+w/2} {y-18} L{x+w-30} {y+8}" stroke="{OL}" stroke-width="4"/>',
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#ffffff" stroke="{OL}" stroke-width="6"/>',
         f'<rect x="{x}" y="{y}" width="{w}" height="52" rx="10" fill="#e8454a" stroke="{OL}" stroke-width="6"/>',
         f'<text x="{x+w/2}" y="{y+42}" font-family="Fredoka" font-weight="700" font-size="38" text-anchor="middle" fill="#ffffff">{yr}</text>']
    for i in range(3):
        for j in range(5):
            o.append(f'<rect x="{x+16+j*29}" y="{y+68+i*30}" width="20" height="20" rx="4" fill="#e6e8f0"/>')
    # circled release day on the final year
    if yr >= 2026:
        o.append(f'<circle cx="{x+16+3*29+10}" cy="{y+68+2*30+10}" r="18" fill="none" stroke="#e8454a" stroke-width="5"/>')
    # flying torn page
    lt = last_tear(t)
    if lt is not None and t - lt < 0.55:
        k = (t - lt) / 0.55
        px = x + w / 2 + 260 * k
        py = y + h / 2 - 220 * k + 300 * k * k
        prev = yr - 1
        o.append(f'<g transform="translate({px:.1f} {py:.1f}) rotate({300*k:.1f})" opacity="{1-k:.2f}">'
                 f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="10" fill="#ffffff" stroke="{OL}" stroke-width="6"/>'
                 f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="52" rx="10" fill="#e8454a" stroke="{OL}" stroke-width="6"/>'
                 f'<text x="0" y="{-h/2+42}" font-family="Fredoka" font-weight="700" font-size="38" text-anchor="middle" fill="#ffffff">{prev}</text></g>')
    return "".join(o)


def couch_back():
    return ('<g transform="translate(-30 0)">' + f'<path d="M690 1560 V1380 Q690 1310 760 1310 H980 Q1050 1310 1050 1380 V1560Z" fill="#5a7fd6" stroke="{OL}" stroke-width="7"/>'
            f'<path d="M720 1540 V1390 Q720 1340 770 1340" fill="none" stroke="#7a9ae6" stroke-width="12" stroke-linecap="round"/></g>')


def couch_front():
    return ('<g transform="translate(-30 0)">' + f'<g stroke="{OL}" stroke-width="7"><rect x="700" y="1520" width="340" height="80" rx="24" fill="#6a8fe6"/>'
            f'<rect x="650" y="1440" width="80" height="190" rx="30" fill="#5a7fd6"/><rect x="1010" y="1440" width="80" height="190" rx="30" fill="#5a7fd6"/>'
            f'<rect x="700" y="1600" width="24" height="{FLOOR-1600}" fill="#7a4a2a"/><rect x="1010" y="1600" width="24" height="{FLOOR-1600}" fill="#7a4a2a"/></g>'
            f'<path d="M665 1465 V1610 M1025 1465 V1610" stroke="#7a9ae6" stroke-width="10" stroke-linecap="round"/></g>')


def cobweb(cx, cy, r, op, ang0=200, ang1=340):
    if op <= 0.02:
        return ""
    o = [f'<g opacity="{op:.2f}" stroke="#ffffff" stroke-width="3" fill="none">']
    spokes = 6
    pts = []
    for k in range(spokes):
        a = math.radians(lerp(ang0, ang1, k / (spokes - 1)))
        ex, ey = cx + r * math.cos(a), cy + r * math.sin(a)
        o.append(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}"/>')
        pts.append(a)
    for ring in (0.3, 0.55, 0.8):
        d = []
        for k, a in enumerate(pts):
            px, py = cx + r * ring * math.cos(a), cy + r * ring * math.sin(a)
            d.append(("M" if k == 0 else "L") + f"{px:.1f} {py:.1f}")
        o.append(f'<path d="{" ".join(d)}"/>')
    o.append('</g>')
    return "".join(o)


def spider(x, top, y, op=1.0):
    if op <= 0.02:
        return ""
    return (f'<g opacity="{op:.2f}"><line x1="{x}" y1="{top}" x2="{x}" y2="{y-14}" stroke="#ffffff" stroke-width="2.5"/>'
            f'<g stroke="{OL}" stroke-width="4" stroke-linecap="round">'
            f'<path d="M{x-12} {y-4} l-14 -10 M{x-12} {y+2} l-16 0 M{x-12} {y+8} l-14 10 M{x+12} {y-4} l14 -10 M{x+12} {y+2} l16 0 M{x+12} {y+8} l14 10"/></g>'
            f'<circle cx="{x}" cy="{y}" r="15" fill="#3a2a4a" stroke="{OL}" stroke-width="4"/>'
            f'<circle cx="{x-5}" cy="{y-3}" r="4" fill="#fff"/><circle cx="{x+5}" cy="{y-3}" r="4" fill="#fff"/>'
            f'<circle cx="{x-5}" cy="{y-2}" r="2" fill="{OL}"/><circle cx="{x+5}" cy="{y-2}" r="2" fill="{OL}"/></g>')


def pad(x, y, rot=0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<path d="M-52 -18 Q -40 -30 -16 -26 H16 Q 40 -30 52 -18 Q 66 20 48 30 Q 34 36 22 12 H-22 Q -34 36 -48 30 Q -66 20 -52 -18Z" fill="#2b2b33" stroke="{OL}" stroke-width="5"/>'
            '<path d="M-36 -8 h16 M-28 -16 v16" stroke="#c9ccd6" stroke-width="5" stroke-linecap="round"/>'
            '<circle cx="26" cy="-14" r="5" fill="#ff5f6e"/><circle cx="36" cy="-4" r="5" fill="#3ce07a"/><circle cx="16" cy="-4" r="5" fill="#4ac0ff"/></g>')


def phone(x, y, rot, charged, s=1.0):
    col = "#3ce07a" if charged else "#e8303a"
    lvl = 34 if charged else 6
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<rect x="-30" y="-52" width="60" height="104" rx="11" fill="#22222b" stroke="{OL}" stroke-width="5"/>'
            '<rect x="-23" y="-43" width="46" height="84" rx="5" fill="#f4f7ff"/>'
            f'<rect x="-14" y="-14" width="28" height="44" rx="5" fill="none" stroke="#2a2a33" stroke-width="4"/><rect x="-5" y="-20" width="10" height="6" rx="2" fill="#2a2a33"/>'
            f'<rect x="-9" y="{26-lvl}" width="18" height="{lvl}" rx="2" fill="{col}"/></g>')


# ---------------------------------------------------------------- camera
CK = [(0.0, (600, 1320, 1.55)), (5.7, (600, 1320, 1.55)), (6.2, (640, 1330, 1.6)), (8.0, (600, 1320, 1.55)),
      (12.25, (600, 1320, 1.55)), (12.6, (660, 1390, 1.68)), (13.8, (680, 1390, 1.68)), (14.3, (600, 1320, 1.55)),
      (18.75, (600, 1320, 1.55)), (19.1, (480, 1370, 1.75)), (19.65, (480, 1370, 1.75)), (20.1, (620, 1330, 1.55)),
      (DUR, (620, 1330, 1.55))]
SHAKES = [(7.05, 10, 0.25), (12.3, 8, 0.3), (20.3, 14, 0.35), (T_PADBONK, 8, 0.25)]


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


# ---------------------------------------------------------------- characters
def grumpo_state(t):
    g = dict(x=GX_SEAT, y=GY_SEAT, ex="grumpy", look=(-1, 0.15), rot=0, sx=1, sy=1, red=0.0,
             layer="couch", pad=("lap",), vis=True)
    if t < T_LEAP0:
        g["sy"] = 1 + 0.012 * math.sin(t * 3)
        if 2.6 <= t < 4.2:
            g["ex"] = "suspicious"
        if t >= 4.2:
            g["ex"], g["look"] = "grumpy", (0.2, -0.8)   # glances up at spider
        if t >= 5.0:
            g["look"] = (-1, 0.15)
        if t >= T_BELL:
            g["ex"], g["look"] = "shock", (1, 0.4)
        if t >= T_SLIDE0:
            g["look"] = (1 - 2 * seg(t, T_SLIDE0, T_SLIDE1), 0.6)
        if T_BELL <= t < T_BELL + 0.3:
            k = (t - T_BELL) / 0.3
            g["y"] -= 30 * math.sin(math.pi * k)
    elif t < T_LEAP1:
        p = seg(t, T_LEAP0, T_LEAP1)
        g["x"] = lerp(GX_SEAT, 560, p)
        g["y"] = lerp(GY_SEAT, GY_FLOOR, p) - 300 * math.sin(math.pi * p)
        g["rot"] = -360 * eio(p)
        g["ex"], g["layer"], g["look"] = "smug", "front", (-1, 0.5)
        g["pad"] = ("fly", p)
    elif t < T_TVON:
        g["x"], g["y"], g["layer"], g["ex"] = 560, GY_FLOOR, "front", "smug"
        k = t - T_LEAP1
        if k < 0.2:
            q = math.sin(math.pi * k / 0.2)
            g["sx"], g["sy"] = 1 + 0.15 * q, 1 - 0.18 * q
        g["look"] = (-0.6, 0.8) if t < T_CASE1 else (-1, 0.3)
        g["pad"] = ("floor",)
    elif t < T_TVOFF:
        g["x"], g["layer"] = 560, "front"
        g["y"] = GY_FLOOR - abs(math.sin(t * 7)) * 10
        g["ex"], g["look"] = "smug", (-1, -0.3)
        g["pad"] = ("hold",)
    elif t < T_TVON2:
        g["x"], g["y"], g["layer"] = 560, GY_FLOOR, "front"
        g["pad"] = ("hold",)
        if t < 12.95:
            g["ex"], g["look"] = "shock", (-1, -0.3)
        elif t < 13.25:
            g["ex"], g["look"] = "shock", (1, 0.2)
        else:
            g["ex"], g["look"] = "angry", (1, 0.2)
            g["red"] = 0.55 * eio(seg(t, 13.25, 13.7)) * (1 - seg(t, 14.05, 14.4))
            g["sx"] = 1 + 0.03 * math.sin(t * 40)
    elif t < T_DONE:
        g["x"], g["y"], g["layer"] = 560, GY_FLOOR, "front"
        g["pad"] = ("hold",)
        g["red"] = 0.55 * (1 - seg(t, 14.05, 14.4))
        g["ex"], g["look"] = ("grumpy", (-1, -0.2)) if t < 15.2 else ("suspicious", (-1, -0.3))
        g["sy"] = 1 + 0.015 * math.sin(t * 4)
    elif t < T_JUMP1:
        g["x"], g["layer"] = 560, "front"
        g["pad"] = ("up",)
        g["ex"], g["look"] = "smug", (-0.5, -1)
        if t >= T_JUMP0:
            p = seg(t, T_JUMP0, T_JUMP1)
            g["y"] = GY_FLOOR - 170 * math.sin(math.pi * p)
        else:
            g["y"] = GY_FLOOR
            k = seg(t, T_DONE, T_JUMP0)
            g["sy"], g["sx"] = 1 - 0.12 * math.sin(math.pi * k), 1 + 0.08 * math.sin(math.pi * k)
    elif t < T_FALL0:
        g["x"], g["y"], g["layer"] = 560, GY_FLOOR, "front"
        g["pad"] = ("up",)
        g["ex"], g["look"] = ("smug", (-0.5, -1)) if t < T_UPDATE + 0.15 else ("shock", (-1, -0.2))
        if t >= T_UPDATE + 0.15:
            g["sx"] = 1 + 0.02 * math.sin(t * 50)
    elif t < T_FALL1:
        p = ein(seg(t, T_FALL0, T_FALL1))
        g["x"], g["layer"] = lerp(560, 640, p), "front"
        g["y"] = lerp(GY_FLOOR, FLOOR - 98, p)
        g["rot"] = 90 * p
        g["ex"], g["look"] = "shock", (-1, -0.2)
        g["pad"] = ("drop", seg(t, T_FALL0, T_PADBONK))
    else:
        g["x"], g["y"], g["rot"], g["layer"] = 640, FLOOR - 98, 90, "front"
        k = t - T_FALL1
        if k < 0.25:
            q = math.sin(math.pi * k / 0.25)
            g["sy"], g["sx"] = 1 - 0.18 * q, 1 + 0.12 * q
        g["ex"] = "shock" if t < T_PADBONK + 0.3 else "grumpy"
        g["look"] = (0, -1)
        g["pad"] = ("drop", seg(t, T_FALL0, T_PADBONK)) if t < T_PADBONK else ("face", t - T_PADBONK)
    return g


def nibbo_state(t):
    n = dict(x=1300, y=NG, ex="happy", rot=0, sx=1, sy=1, vis=False, phone=None)
    if t < N_IN0:
        return n
    n["vis"] = True
    if t < N_IN1:
        p = seg(t, N_IN0, N_IN1)
        n["x"] = lerp(1250, 850, p)
        n["y"] = NG - abs(math.sin(t * 12)) * 14
        n["phone"] = ("hand", False)
    elif t < T_UNPLUG:
        n["x"] = 850
        k = seg(t, 11.6, 12.0)
        n["sy"], n["sx"] = 1 - 0.1 * k, 1 + 0.05 * k
        n["ex"] = "happy"
        n["phone"] = ("hand", False)
    elif t < 13.3:
        n["x"] = 850
        n["ex"] = "joy" if t > 12.45 else "happy"
        n["phone"] = ("charging", t > 12.45)
        n["y"] = NG - (abs(math.sin(t * 10)) * 10 if t > 12.5 else 0)
    elif t < T_TVON2:
        n["x"] = 850
        n["ex"] = "uhoh"
        n["phone"] = ("charging", True) if t < T_REPLUG - 0.15 else ("hand", True)
        n["sx"] = 1 + 0.02 * math.sin(t * 45)
    elif t < 15.0:
        p = eio(seg(t, T_TVON2, 14.9))
        n["x"] = lerp(850, 790, p)
        n["ex"] = "nervous"
        n["phone"] = ("hand", True)
    elif t < T_DONE:
        n["x"] = 800
        n["ex"] = "happy"
        n["rot"] = 4 * math.sin(t * 2.4)
        n["phone"] = None
    elif t < T_UPDATE:
        n["x"] = 800
        n["ex"] = "joy"
        p = seg(t, T_JUMP0 - 0.1, T_JUMP1 - 0.1)
        n["y"] = NG - 140 * math.sin(math.pi * p)
    elif t < T_FALL1 + 0.3:
        n["x"] = 800
        n["ex"] = "wow" if t < T_FALL0 else "uhoh"
    else:
        p = eio(seg(t, T_FALL1 + 0.3, T_FALL1 + 0.8))
        n["x"] = lerp(800, 830, p)
        n["ex"] = "nervous" if t < 22.8 else "happy"
        n["rot"] = -8 * math.sin(t * 6) * (t < 22.8)
    return n


def grumpo_pad(g, t):
    """controller + arms for grumpo"""
    kind = g["pad"][0]
    x, y = g["x"], g["y"]
    col = "#4a2a7a"
    if kind == "lap":
        px, py = x - 70, y + 70
        return arm(x - 100, y + 20, px - 30, py, col) + arm(x - 40, y + 60, px + 30, py, col, sag=10) + pad(px, py, -8, 0.95)
    if kind == "fly":
        p = g["pad"][1]
        px, py = x - 40, y - 160 - 60 * math.sin(math.pi * p)
        return pad(px, py, 720 * p, 0.95)
    if kind == "floor":
        return pad(700, FLOOR - 40, 12, 0.95)
    if kind == "hold":
        px, py = x - 130, y + 20
        return arm(x - 100, y - 10, px + 30, py, col) + pad(px, py, -14, 0.95)
    if kind == "up":
        px, py = x - 40, y - 190
        return arm(x - 80, y - 60, px - 20, py + 10, col, sag=-10) + arm(x + 10, y - 100, px + 30, py + 10, col, sag=-10) + pad(px, py, 0, 0.95)
    if kind == "drop":
        p = g["pad"][1]
        px = lerp(520, 580, p)
        py = lerp(GY_FLOOR - 190, FLOOR - 230, p) - 260 * math.sin(math.pi * min(1, p * 1.1)) * (1 - p)
        if p >= 1:
            py = FLOOR - 150
        return pad(px, py, 540 * p, 0.95)
    if kind == "face":
        k = g["pad"][1]
        bounce = abs(math.sin(min(k, 0.5) * 12)) * 30 * max(0, 1 - k * 2)
        return pad(620, FLOOR - 160 - bounce, 80, 0.95)
    return ""


# ---------------------------------------------------------------- frame
def frame(t):
    ctx = Ctx()
    L = [room(t), calendar(t), cabinet(), console(T_TVON <= t < T_TVOFF or t >= T_TVON2, t), tv(t), socket(True)]

    # cords: console -> socket (unplugged between UNPLUG and REPLUG)
    plugged_console = not (T_UNPLUG <= t < T_REPLUG)
    cx0, cy0 = CONSOLE[0] + 110, CONSOLE[1]
    if plugged_console:
        L.append(cord(cx0, cy0, SOCKET[0], SOCKET[1] + 26))
        L.append(plug(SOCKET[0], SOCKET[1] + 6, 0))
    else:
        k = t - T_UNPLUG
        hop = 40 * math.sin(math.pi * min(1, k / 0.35)) if k < 0.35 else 0
        ex_, ey_ = SOCKET[0] - 40, FLOOR - 20 - hop
        L.append(cord(cx0, cy0, ex_, ey_ + 18))
        L.append(plug(ex_, ey_, -70 + 20 * math.sin(k * 3)))

    n = nibbo_state(t)
    g = grumpo_state(t)

    # cobweb + spider (montage) on couch corner
    web_op = seg(t, 1.2, 5.0) * (1 - seg(t, T_LEAP0, T_LEAP0 + 0.25))
    sp_y = lerp(1060, 1290, eio(seg(t, 3.4, 4.4))) if t < T_LEAP0 else lerp(1290, 1060, seg(t, T_LEAP0, T_LEAP0 + 0.4))
    sp_op = 1.0 if 3.4 <= t < T_LEAP0 + 0.4 else 0.0

    L.append(couch_back())
    L.append(cobweb(1010, 1320, 190 * (0.4 + 0.6 * seg(t, 1.2, 4.0)), web_op, 150, 250))
    if g["layer"] == "couch":
        L.append(shadow(g["x"], 1525, 130))
        L.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"],
                        False, 0, None, 0, t))
        L.append(grumpo_pad(g, t))
    L.append(couch_front())
    L.append(spider(955, 1000, sp_y, sp_op))

    # package
    if T_SLIDE0 <= t:
        if t < T_SLIDE1:
            p = eout(seg(t, T_SLIDE0, T_SLIDE1))
            bx = lerp(1250, 470, p)
            L.append(speed_lines(bx + 110, FLOOR - 40, 180, 1 - p))
        else:
            bx = 470
        if t < T_INSERT1 + 1.5:
            op = 1 - seg(t, T_INSERT1 + 1.0, T_INSERT1 + 1.5)
            L.append(f'<g opacity="{op:.2f}">' + shadow(bx, FLOOR + 2, 90) + package(bx, FLOOR, eback(seg(t, T_LID, T_LID + 0.3))) + '</g>')
    # game case
    if t >= T_LID:
        if t < T_CASE1:
            p = eout(seg(t, T_LID, T_CASE1))
            cx_, cy_ = 470, lerp(FLOOR - 60, FLOOR - 300, p)
            L.append(case_svg(cx_, cy_, 0, 0.6 + 0.4 * p))
            L.append(star_twinkle(cx_ - 70, cy_ - 50, seg(t, T_LID + 0.1, T_CASE1)))
            L.append(star_twinkle(cx_ + 70, cy_ - 20, seg(t, T_LID + 0.2, T_CASE1)))
        elif t < T_INSERT1:
            p = ein(seg(t, T_INSERT0, T_INSERT1))
            cx_ = lerp(470, CONSOLE[0] - 25, p)
            cy_ = lerp(FLOOR - 300, CONSOLE[1], p) - 60 * math.sin(math.pi * p)
            L.append(case_svg(cx_, cy_, -90 * p, 1 - 0.55 * p))
        elif t < T_INSERT1 + 0.12:
            L.append(case_svg(CONSOLE[0] - 25, CONSOLE[1], -90, 0.45))

    # nibbo (front of couch)
    if n["vis"]:
        L.append(shadow(n["x"], FLOOR + 2, 110))
        L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"], rot=n["rot"], sx=n["sx"], sy=n["sy"]))
        if n["phone"]:
            kind, charged = n["phone"]
            if kind == "hand":
                L.append(arm(n["x"] - 60, n["y"] + 20, n["x"] - 110, n["y"] + 10, "#3d2a12"))
                L.append(phone(n["x"] - 120, n["y"] - 10, -10, charged, 0.9))
            else:  # charging: phone on floor next to socket, cable to socket
                L.append(cord(SOCKET[0] - 36, FLOOR - 40, SOCKET[0], SOCKET[1] + 26, "#f4f5f8"))
                L.append(plug(SOCKET[0], SOCKET[1] + 6, 0, "#f4f5f8"))
                L.append(phone(SOCKET[0] - 36, FLOOR - 40, 90, charged, 0.8))
                if charged:
                    L.append(f'<path d="M{SOCKET[0]-48} {FLOOR-110} l10 -14 l-4 12 l10 -2 l-12 16 l4 -12z" fill="#ffe36a" stroke="{OL}" stroke-width="2"/>')
            if kind == "charging":
                L.append(arm(n["x"] - 60, n["y"] + 20, SOCKET[0] + 30, SOCKET[1] + 10, "#3d2a12"))

    # grumpo (floor layer)
    if g["layer"] == "front":
        if g["rot"] < 45:
            L.append(shadow(g["x"], FLOOR + 2, 120))
        L.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"],
                        False, 0, None, 0, t))
        L.append(grumpo_pad(g, t))

    # FX
    L.append(symbol(GX_SEAT, GY_SEAT - 200, "!", seg(t, T_BELL, T_BELL + 0.2) * (1 - seg(t, T_LEAP0, T_LEAP0 + 0.1)), "#ffcc2e"))
    if T_BELL <= t < T_BELL + 0.7:   # doorbell rings from the right
        k = (t - T_BELL) / 0.7
        for i in range(3):
            rr = 40 + 50 * i + 60 * k
            L.append(f'<path d="M{960 - rr*0.3:.0f} {1450 - rr:.0f} A{rr:.0f} {rr:.0f} 0 0 1 {960 - rr*0.3:.0f} {1450 + rr:.0f}" fill="none" stroke="#ffcc2e" stroke-width="7" opacity="{(1-k)*0.8:.2f}"/>')
    L.append(impact(560, FLOOR - 10, seg(t, T_LEAP1, T_LEAP1 + 0.3), "#f1e3c4"))
    L.append(impact(SOCKET[0], SOCKET[1], seg(t, T_UNPLUG, T_UNPLUG + 0.25), "#fff6a8"))
    L.append(symbol(560, GY_FLOOR - 210, "!", seg(t, 12.95, 13.1) * (1 - seg(t, 13.9, 14.1)), "#e8303a"))
    L.append(symbol(850, NG - 190, "?", seg(t, 13.3, 13.45) * (1 - seg(t, 14.0, 14.2)), "#3a7ad6"))
    if T_DONE <= t < T_UPDATE:
        for k in range(6):
            a = k * 1.05 + 0.3
            p = seg(t, T_DONE, T_DONE + 0.6)
            L.append(star_twinkle(560 + 170 * math.cos(a) * p, GY_FLOOR - 60 + 120 * math.sin(a) * p, p))
    L.append(symbol(560, GY_FLOOR - 250, "!", seg(t, T_UPDATE + 0.15, T_UPDATE + 0.3) * (1 - seg(t, T_FALL0, T_FALL0 + 0.1)), "#e8303a"))
    L.append(impact(640, FLOOR - 40, seg(t, T_FALL1, T_FALL1 + 0.3), "#f1e3c4"))
    L.append(impact(620, FLOOR - 170, seg(t, T_PADBONK, T_PADBONK + 0.25), "#fff6a8"))
    # dizzy stars after bonk
    if t >= T_PADBONK + 0.2:
        for k in range(3):
            a = t * 4 + k * 2.09
            L.append(star_twinkle(640 + 120 * math.cos(a), FLOOR - 250 + 26 * math.sin(a), 0.55))
    # new web + spider at the end
    if t >= T_TEAR_END:
        q = seg(t, T_TEAR_END + 0.3, 23.2)
        L.append(cobweb(470, FLOOR - 4, 230 * (0.3 + 0.7 * q), q * 0.9, 270, 360))
        L.append(spider(700, 1040, lerp(1040, FLOOR - 230, eio(seg(t, 21.9, 22.8))), 1.0))

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{CASE_DEF}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g></svg>')

    # ---- screen overlays: hook + counter
    layers = [hook_title(t + 0.12, "Waiting for GTA 6", "13 YEARS!")]
    if t < T_SLIDE0:
        layers.append(counter(t, str(year_at(t)), "YEAR", bump_t=last_tear(t)))
    elif T_TVON <= t < T_UPDATE:
        mode, pct = download(t)
        bt = None
        if T_TVOFF <= t < T_TVOFF + 0.4:
            bt = T_TVOFF
        elif T_DONE <= t:
            bt = T_DONE
        layers.append(counter(t, f"{pct}%", "DOWNLOAD", bump_t=bt))
    elif T_UPDATE <= t < T_TEAR_END:
        layers.append(counter(t, "0%", "UPDATE", bump_t=T_UPDATE))
    elif t >= T_TEAR_END:
        layers.append(counter(t, str(year_at(t)), "YEAR", bump_t=T_TEAR_END))
    return overlay(svg, *layers)


def build_sfx():
    sfx(0.05, "grumble", 0.6, 0.9)
    for k, tt in enumerate(TEARS):
        sfx(tt, "flap", 0.7, 0.9 + 0.04 * k)
        sfx(tt + 0.02, "tap", 0.35, 1.0 + 0.05 * k)
    sfx(2.6, "creak", 0.4, 1.3)
    sfx(3.4, "boing", 0.35, 1.8)
    sfx(4.2, "gulp", 0.4, 1.1)
    sfx(T_BELL, "ding", 0.9, 1.0); sfx(T_BELL + 0.25, "ding", 0.9, 0.8)
    sfx(T_BELL + 0.05, "gasp", 0.7)
    sfx(T_SLIDE0, "squeak_slide", 0.7)
    sfx(T_LEAP0, "whoosh", 0.9, 1.1)
    sfx(T_LEAP0 + 0.05, "rise", 0.5, 1.2)
    sfx(T_LEAP1, "thud", 0.9)
    sfx(T_LID, "pop", 0.8, 1.1)
    sfx(T_LID + 0.15, "cool", 0.7, 1.1)
    sfx(T_INSERT0, "whoosh", 0.6, 1.4)
    sfx(T_INSERT1, "click", 0.9)
    sfx(T_INSERT1 + 0.05, "whirr", 0.6)
    sfx(T_TVON, "blip", 0.8, 1.2)
    # download ticks speeding then slowing
    k = 0
    tt = DL0
    while tt < DL1:
        sfx(tt, "blip", 0.25, 1.4 + 0.02 * k)
        k += 1
        tt += 0.22 + 0.25 * seg(tt, DL0 + 2.5, DL1)
    for i in range(8):
        sfx(N_IN0 + i * 0.18, "tiptoe", 0.5, 1.1 + 0.1 * (i % 2))
    sfx(11.6, "suspense", 0.5, 1.2)
    sfx(T_UNPLUG, "cork_pop", 0.9, 1.1)
    sfx(T_TVOFF, "blip_down", 0.9, 0.7)
    sfx(12.45, "ding", 0.5, 1.5)
    sfx(12.5, "laugh", 0.5, 1.3)
    sfx(12.95, "error_beep", 0.7, 0.8)
    sfx(13.3, "grumble", 0.9, 0.9)
    sfx(13.35, "gulp", 0.6, 1.3)
    sfx(T_REPLUG - 0.15, "zip", 0.6, 1.3)
    sfx(T_REPLUG, "pop", 0.8, 0.9)
    sfx(T_TVON2, "blip", 0.8, 1.2)
    sfx(14.4, "tiptoe", 0.5, 1.2); sfx(14.6, "tiptoe", 0.5, 1.1)
    for i in range(10):
        sfx(DL2_0 + i * 0.29, "typing", 0.35, 1.0 + 0.04 * i)
    sfx(T_DONE, "ding", 1.0, 1.3)
    sfx(T_DONE + 0.05, "cheer", 0.7, 1.1)
    sfx(T_JUMP0, "boing", 0.7, 1.2)
    sfx(T_JUMP0 + 0.1, "laugh", 0.6, 1.3)
    sfx(T_JUMP1, "thud", 0.6, 1.2)
    sfx(T_UPDATE, "alert", 0.8, 0.9)
    sfx(T_UPDATE + 0.15, "error_beep", 0.9, 0.7)
    sfx(T_UPDATE + 0.3, "zoom", 0.5)
    sfx(T_FALL0, "slide_down", 0.8, 1.0)
    sfx(T_FALL1, "thud", 1.0, 0.85)
    sfx(T_PADBONK, "bonk", 1.0, 1.1)
    sfx(T_PADBONK + 0.25, "boing", 0.4, 1.5)
    sfx(T_TEAR_END, "flap", 0.8, 0.85)
    sfx(T_TEAR_END + 0.05, "tap", 0.4, 0.8)
    sfx(21.9, "boing", 0.4, 1.9)
    sfx(22.9, "grumble", 0.8, 0.85)
    sfx(23.1, "laugh", 0.4, 1.4)
