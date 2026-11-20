"""Grumpo & Nibbo — Episode 2: The Wi-Fi Password (indoor living room, 60 fps)."""
import math, random, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow

W, H, FPS, DUR = 1080, 1920, 60, 27.0
FLOOR = 1560
NR = 112
NG = FLOOR - NR
GX, GY, GS = 900, 1292, 0.92     # grumpo seated
LAMP_X = 470
TABLE_X = 660
ROUTER_HOME = (660, 1300)

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


# ---------------------------------------------------------------- props
def room(t):
    o = []
    o.append(f'<rect x="-600" y="-600" width="2600" height="{FLOOR+600}" fill="#cfe8e2"/>')
    for x in range(-600, 2000, 64):
        o.append(f'<rect x="{x}" y="-600" width="22" height="{FLOOR+600}" fill="#c3dfd8"/>')
    # window
    o.append(f'<g><rect x="690" y="430" width="340" height="420" rx="10" fill="#ffffff" stroke="{OL}" stroke-width="6"/>'
             '<rect x="710" y="450" width="300" height="380" fill="#7cc3f2"/>'
             '<circle cx="950" cy="520" r="34" fill="#fff6c8"/>'
             '<g fill="#fff"><circle cx="770" cy="600" r="26"/><circle cx="800" cy="585" r="32"/><circle cx="835" cy="602" r="22"/></g>'
             '<path d="M710 760 Q 780 700 860 745 Q 930 700 1010 750 V830 H710Z" fill="#8ccf7e"/>'
             f'<path d="M860 450 V830 M710 640 H1010" stroke="#ffffff" stroke-width="12"/>'
             f'<rect x="710" y="450" width="300" height="380" fill="none" stroke="{OL}" stroke-width="5"/></g>')
    # curtains
    sway = 6 * math.sin(t * 1.3)
    for side, x0 in (("l", 640), ("r", 1000)):
        d = -1 if side == "l" else 1
        o.append(f'<path d="M{x0} 400 h90 q{sway*d:.1f} 220 {-10*d:.1f} 470 h-80 q{-8*d:.1f} -240 0 -470z" fill="#f28b9c" stroke="{OL}" stroke-width="5"/>'
                 f'<path d="M{x0+30} 410 q6 220 -4 450" fill="none" stroke="#d96c80" stroke-width="5"/>')
    o.append(f'<rect x="620" y="388" width="480" height="18" rx="9" fill="#a0703f" stroke="{OL}" stroke-width="5"/>')
    # picture frame
    o.append(f'<rect x="120" y="560" width="230" height="170" rx="8" fill="#ffd36a" stroke="{OL}" stroke-width="6"/>'
             '<rect x="140" y="580" width="190" height="130" fill="#bfe6ff"/>'
             '<path d="M140 710 L200 630 L245 680 L280 640 L330 710Z" fill="#7cc65c"/>'
             '<circle cx="300" cy="610" r="14" fill="#fff6c8"/>'
             f'<rect x="140" y="580" width="190" height="130" fill="none" stroke="{OL}" stroke-width="4"/>')
    # baseboard + floor
    o.append(f'<rect x="-600" y="{FLOOR-34}" width="2600" height="34" fill="#ffffff" stroke="{OL}" stroke-width="5"/>')
    o.append(f'<rect x="-600" y="{FLOOR}" width="2600" height="900" fill="#d39a63"/>')
    for k, y in enumerate(range(FLOOR + 50, FLOOR + 900, 70)):
        o.append(f'<line x1="-600" y1="{y}" x2="2000" y2="{y}" stroke="#b97f4c" stroke-width="5"/>')
        off = (k * 170) % 340
        for x in range(-600 + off, 2000, 340):
            o.append(f'<line x1="{x}" y1="{y-70}" x2="{x}" y2="{y}" stroke="#b97f4c" stroke-width="4"/>')
    o.append(f'<line x1="-600" y1="{FLOOR}" x2="2000" y2="{FLOOR}" stroke="{OL}" stroke-width="6"/>')
    # rug
    o.append(f'<rect x="360" y="{FLOOR+6}" width="760" height="40" rx="20" fill="#5a7fd6" stroke="{OL}" stroke-width="5"/>'
             f'<path d="M400 {FLOOR+26} h680" stroke="#ffd36a" stroke-width="6" stroke-dasharray="26 18"/>')
    # plant
    o.append(f'<path d="M60 {FLOOR-120} q-50 -90 -10 -170 q30 60 18 160z M80 {FLOOR-120} q10 -120 70 -190 q10 100 -50 190z M70 {FLOOR-120} q-80 -40 -110 -110 q80 10 110 100z" fill="#5aa957" stroke="{OL}" stroke-width="5"/>'
             f'<path d="M20 {FLOOR-130} h120 l-16 130 h-88z" fill="#e0794f" stroke="{OL}" stroke-width="6"/>')
    return "".join(o)


def lamp(shade_on=True, bulb_glow=0.0):
    x = LAMP_X
    o = [f'<ellipse cx="{x}" cy="{FLOOR-6}" rx="60" ry="14" fill="#5b5b6a" stroke="{OL}" stroke-width="5"/>',
         f'<rect x="{x-7}" y="1110" width="14" height="{FLOOR-1116}" fill="#8b8b9a" stroke="{OL}" stroke-width="4"/>',
         f'<circle cx="{x}" cy="1100" r="22" fill="#fff6c8" stroke="{OL}" stroke-width="4"/>']
    if bulb_glow > 0:
        o.append(f'<circle cx="{x}" cy="1100" r="70" fill="#fff6a8" opacity="{0.35*bulb_glow:.2f}"/>')
    if shade_on:
        o.append(shade_svg(x, 1100))
    return "".join(o)


def shade_svg(x, y, rot=0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<path d="M-56 -78 H56 L96 18 H-96Z" fill="#ffe08a" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<path d="M-96 18 H96" stroke="#e0a83a" stroke-width="10"/>'
            + "".join(f'<line x1="{-90+k*20}" y1="24" x2="{-90+k*20}" y2="38" stroke="#e0a83a" stroke-width="5" stroke-linecap="round"/>' for k in range(10)) +
            '<path d="M-40 -66 L-62 6" stroke="#fff6c8" stroke-width="8" opacity="0.7"/></g>')


def table():
    x = TABLE_X
    return (f'<g stroke="{OL}" stroke-width="5"><rect x="{x-70}" y="1340" width="16" height="{FLOOR-1340}" fill="#a0703f"/>'
            f'<rect x="{x+54}" y="1340" width="16" height="{FLOOR-1340}" fill="#a0703f"/>'
            f'<rect x="{x-90}" y="1326" width="180" height="22" rx="6" fill="#c08a52"/></g>')


def router(x, y, rot=0, flipped=False, t=0.0, s=1.0, locked=True):
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">']
    if not flipped:
        o.append(f'<path d="M-40 -30 L-56 -110 M40 -30 L56 -110" stroke="{OL}" stroke-width="12" stroke-linecap="round"/>'
                 f'<path d="M-40 -30 L-56 -110 M40 -30 L56 -110" stroke="#ececf2" stroke-width="6" stroke-linecap="round"/>'
                 f'<rect x="-62" y="-30" width="124" height="56" rx="14" fill="#f4f5f8" stroke="{OL}" stroke-width="6"/>')
        for k in range(4):
            on = math.sin(t * 9 + k * 1.7) > -0.2
            o.append(f'<circle cx="{-36 + k*16}" cy="10" r="5" fill="{"#3ce07a" if on else "#2a6a46"}"/>')
        if locked:
            o.append(f'<g transform="translate(36 -2)"><rect x="-11" y="-2" width="22" height="18" rx="4" fill="#ffcc2e" stroke="{OL}" stroke-width="3"/>'
                     f'<path d="M-6 -2 v-6 a6 6 0 0 1 12 0 v6" fill="none" stroke="{OL}" stroke-width="3"/></g>')
    else:
        o.append(f'<rect x="-62" y="-26" width="124" height="52" rx="14" fill="#dcdde4" stroke="{OL}" stroke-width="6"/>'
                 '<rect x="-40" y="-20" width="80" height="40" rx="4" fill="#ffffff" stroke="#8a8a96" stroke-width="2"/>')
        o.append(qr(-34, -16, 32))
        o.append(wifi_icon(18, 6, 0.4, 3, "#2a2a33"))
        o.append(f'<path d="M-56 -110 L-40 -26 M56 -110 L40 -26" stroke="{OL}" stroke-width="12" stroke-linecap="round" transform="rotate(180)"/>'
                 f'<path d="M-56 -110 L-40 -26 M56 -110 L40 -26" stroke="#ececf2" stroke-width="6" stroke-linecap="round" transform="rotate(180)"/>')
    o.append('</g>')
    return "".join(o)


_rq = random.Random(42)
QR_BITS = [[_rq.random() > 0.5 for _ in range(9)] for _ in range(9)]


def qr(x, y, size):
    c = size / 9
    o = [f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="#fff"/>']
    for i in range(9):
        for j in range(9):
            fin = (i < 3 and j < 3) or (i < 3 and j > 5) or (i > 5 and j < 3)
            if fin:
                continue
            if QR_BITS[i][j]:
                o.append(f'<rect x="{x+j*c:.2f}" y="{y+i*c:.2f}" width="{c+0.2:.2f}" height="{c+0.2:.2f}" fill="#111"/>')
    for (fi, fj) in ((0, 0), (0, 6), (6, 0)):
        o.append(f'<rect x="{x+fj*c:.2f}" y="{y+fi*c:.2f}" width="{3*c:.2f}" height="{3*c:.2f}" fill="#111"/>'
                 f'<rect x="{x+(fj+0.5)*c:.2f}" y="{y+(fi+0.5)*c:.2f}" width="{2*c:.2f}" height="{2*c:.2f}" fill="#fff"/>'
                 f'<rect x="{x+(fj+1)*c:.2f}" y="{y+(fi+1)*c:.2f}" width="{c:.2f}" height="{c:.2f}" fill="#111"/>')
    return "".join(o)


def wifi_icon(x, y, s, bars, col="#2a2a33", dim="#c9ccd6"):
    o = [f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.2f})">']
    for k, r in enumerate((14, 30, 46)):
        c = col if bars > k else dim
        o.append(f'<path d="M{-r*0.78:.1f} {-r*0.62:.1f} A{r} {r} 0 0 1 {r*0.78:.1f} {-r*0.62:.1f}" fill="none" stroke="{c}" stroke-width="9" stroke-linecap="round"/>')
    o.append(f'<circle cx="0" cy="2" r="6" fill="{col if bars > 0 else dim}"/></g>')
    return "".join(o)


def phone(x, y, rot, screen, s=1.0, t=0.0, bars=0, dots=0, scan=0.0):
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">',
         f'<rect x="-34" y="-58" width="68" height="116" rx="12" fill="#22222b" stroke="{OL}" stroke-width="5"/>',
         '<rect x="-27" y="-48" width="54" height="94" rx="6" fill="#f4f7ff"/>']
    if screen == "nowifi":
        o.append(wifi_icon(0, 6, 0.55, 0))
        o.append('<path d="M-12 -24 L12 0 M12 -24 L-12 0" stroke="#e8303a" stroke-width="6" stroke-linecap="round"/>')
    elif screen == "bars":
        o.append(wifi_icon(0, 10, 0.6, bars, "#2a9a4a"))
    elif screen == "play":
        o.append('<rect x="-27" y="-30" width="54" height="40" fill="#1f2a44"/>'
                 f'<path d="M-6 -20 L10 -10 L-6 0Z" fill="#ff4d5e"/>'
                 f'<rect x="-22" y="16" width="{44*((t*0.2)%1):.1f}" height="4" fill="#ff4d5e"/><rect x="-22" y="16" width="44" height="4" fill="none" stroke="#c9ccd6" stroke-width="1"/>')
    elif screen == "dots":
        for k in range(6):
            fill = "#22222b" if k < dots else "#c9ccd6"
            o.append(f'<circle cx="{-20 + k*8}" cy="-28" r="3" fill="{fill}"/>')
        for i in range(3):
            for j in range(3):
                o.append(f'<rect x="{-20 + j*14}" y="{-14 + i*14}" width="11" height="11" rx="3" fill="#d6dbea"/>')
    elif screen == "spinner":
        a = t * 400
        o.append(f'<g transform="translate(0 -2) rotate({a:.1f})"><circle r="14" fill="none" stroke="#c9ccd6" stroke-width="5"/>'
                 '<path d="M0 -14 A14 14 0 0 1 14 0" fill="none" stroke="#3a7ad6" stroke-width="5" stroke-linecap="round"/></g>')
    elif screen == "ok":
        o.append(wifi_icon(0, 0, 0.6, 3, "#2a9a4a"))
        o.append('<circle cx="14" cy="18" r="10" fill="#2ac06a"/><path d="M9 18 l4 4 l8 -9" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>')
    elif screen == "scan":
        o.append('<rect x="-20" y="-30" width="40" height="40" fill="none" stroke="#3a7ad6" stroke-width="3" stroke-dasharray="8 6"/>')
        yy = -30 + 40 * (0.5 + 0.5 * math.sin(scan * 12))
        o.append(f'<line x1="-22" y1="{yy:.1f}" x2="22" y2="{yy:.1f}" stroke="#ff4d5e" stroke-width="3"/>')
    o.append('<rect x="-10" y="-54" width="20" height="4" rx="2" fill="#3a3a44"/></g>')
    return "".join(o)


def arm(x0, y0, x1, y1, col="#3d2a12", w=10):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + 30
    return f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>'


def chair_back():
    return (f'<path d="M760 1420 V1150 Q760 1070 840 1070 H960 Q1040 1070 1040 1150 V1420Z" fill="#e26a4a" stroke="{OL}" stroke-width="7"/>'
            f'<path d="M790 1400 V1160 Q790 1100 850 1100" fill="none" stroke="#f08a6a" stroke-width="12" stroke-linecap="round"/>')


def chair_front():
    return (f'<g stroke="{OL}" stroke-width="7"><rect x="770" y="1385" width="260" height="70" rx="22" fill="#f07d5a"/>'
            f'<rect x="730" y="1255" width="70" height="210" rx="28" fill="#e26a4a"/><rect x="1000" y="1255" width="70" height="210" rx="28" fill="#e26a4a"/>'
            f'<rect x="760" y="1455" width="20" height="{FLOOR-1455}" fill="#7a4a2a"/><rect x="1020" y="1455" width="20" height="{FLOOR-1455}" fill="#7a4a2a"/></g>'
            f'<path d="M745 1280 V1440 M1015 1280 V1440" stroke="#f08a6a" stroke-width="10" stroke-linecap="round"/>')


def eyes_twitch(x, y, p):
    if p <= 0:
        return ""
    return f'<path d="M{x-60} {y-40} l12 -10 l8 10 l12 -10" fill="none" stroke="#221c2e" stroke-width="5" opacity="{p:.2f}"/>'


# ---------------------------------------------------------------- camera
CK = [(0.0, (440, 1340, 1.85)), (1.5, (690, 1235, 1.3)), (8.4, (690, 1235, 1.3)), (8.9, (960, 1230, 1.28)),
      (10.3, (960, 1230, 1.28)), (10.8, (690, 1235, 1.3)), (16.7, (690, 1235, 1.3)), (17.15, (650, 1420, 1.9)),
      (18.6, (650, 1420, 1.9)), (19.1, (690, 1235, 1.3)), (27.0, (690, 1235, 1.3))]
SHAKES = [(11.1, 8, 0.2), (11.25, 10, 0.25), (15.3, 14, 0.3), (16.65, 12, 0.3), (25.9, 10, 0.3)]


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
def frame(t):
    ctx = Ctx()
    L = [room(t)]

    # lamp (shade taken at 6.6)
    L.append(lamp(shade_on=t < 6.55, bulb_glow=1.0 if t >= 6.55 else 0.0))
    L.append(table())

    # ---------------- router position / state
    r = dict(x=ROUTER_HOME[0], y=ROUTER_HOME[1], rot=0, flipped=False, layer="table", s=1.0)
    if 4.6 <= t < 12.2:
        p = eio(seg(t, 4.6, 5.0))
        r["x"], r["y"] = lerp(660, 830, p), lerp(1300, 1250, p)
        r["layer"] = "behind" if p > 0.6 else "table"
    elif 12.2 <= t < 15.3:
        r["layer"] = "carried"
    elif 15.3 <= t < 16.65:
        p = seg(t, 15.3, 16.65)
        r["x"] = lerp(560, 650, p)
        r["y"] = lerp(1380, FLOOR - 28, p) - 620 * math.sin(math.pi * p)
        r["rot"] = 900 * p
        r["layer"] = "front"
        r["flipped"] = p > 0.5
    elif t >= 16.65:
        r["x"], r["y"], r["rot"], r["flipped"], r["layer"] = 650, FLOOR - 28, 0, True, "front"
        if t >= 19.2:
            r["layer"] = "front"

    # ---------------- NIBBO state
    n = dict(x=380, y=NG, ex="nervous", rot=0, sx=1, sy=1, vis=True, phone=None, shade=False, layer="front")
    n_phone_screen, n_bars = "nowifi", 0
    if t < 1.5:
        n["ex"] = "nervous"
    elif t < 2.4:
        n["ex"] = "wow" if t > 1.7 else "nervous"
    elif t < 4.6:
        p = seg(t, 2.4, 4.4)
        n["x"] = lerp(380, 545, p)
        n["y"] = NG - abs(math.sin(t * 11)) * 10 * (p < 1)
        n["ex"] = "happy"
        n_phone_screen = "bars"
        n_bars = 0 + (t >= 3.0) + (t >= 3.6) + (t >= 4.2)
    elif t < 6.0:
        n["x"] = 545
        n_phone_screen, n_bars = "bars", (3 if t < 5.0 else 0)
        n["ex"] = "wow" if t < 5.3 else "nervous"
        if t >= 5.0:
            q = seg(t, 5.0, 5.3)
            n["sy"], n["sx"] = 1 - 0.1 * q, 1 + 0.05 * q
    elif t < 7.0:
        p = seg(t, 6.0, 6.5)
        n["x"] = lerp(545, LAMP_X + 120, eio(p))
        n["ex"] = "happy"
        n_phone_screen = None
        n["shade"] = t >= 6.9
        if 6.55 <= t < 6.9:
            n["shade_lift"] = seg(t, 6.55, 6.9)
    elif t < 8.6:
        n["shade"] = True
        n_phone_screen = None
        if t < 8.0:
            p = seg(t, 7.0, 8.0)
            n["x"] = lerp(LAMP_X + 120, 1180, p)
            n["y"] = NG - abs(math.sin(t * 13)) * 8
            n["layer"] = "front"
            n["ex"] = "happy"
        else:
            p = seg(t, 8.0, 8.6)
            n["x"] = lerp(1180, 1010, eio(p))
            n["y"] = lerp(NG, 1150, eout(p))
            n["layer"] = "behindchair"
            n["ex"] = "happy"
    elif t < 11.25:
        n["shade"] = t < 10.8
        n_phone_screen = None
        n["layer"] = "behindchair"
        n["x"], n["y"] = 1010, 1150
        n["ex"] = "happy"
        if 9.55 <= t < 10.25:
            n["ex"] = "joy"   # frozen 'lamp' pose, eyes shut
            n["y"] = 1150
        if t >= 10.25:
            lean = eio(seg(t, 10.25, 10.8))
            n["x"], n["y"], n["rot"] = lerp(1010, 960, lean), lerp(1150, 1120, lean), -25 * lean
            n["ex"] = "wow" if t > 10.7 else "happy"
        if t >= 10.8:
            fall = ein(seg(t, 10.8, 11.25))
            n["x"], n["y"], n["rot"] = lerp(960, 1080, fall), lerp(1120, 1420, fall), -25 + 140 * fall
            n["ex"] = "wow"
    elif t < 12.2:
        n["vis"] = False
    elif t < 15.3:
        n["layer"] = "front"
        n_phone_screen = None
        if t < 12.45:
            p = eout(seg(t, 12.2, 12.45))
            n["x"], n["y"] = 1110, lerp(1420, NG - 60, p)
            n["ex"] = "joy"
        elif t < 13.4:
            p = seg(t, 12.45, 13.4)
            n["x"] = lerp(1110, -160, ein(p) * 0.4 + p * 0.6)
            n["y"] = NG - abs(math.sin(t * 18)) * 22
            n["ex"] = "joy"
        elif t < 14.2:
            n["vis"] = False
        else:
            # loop: re-enters from right, now CHASING grumpo
            p = seg(t, 14.2, 15.3)
            n["x"] = lerp(1350, 760, p)
            n["y"] = NG - abs(math.sin(t * 18)) * 22
            n["ex"] = "joy"
    elif t < 16.65:
        k = t - 15.3
        n["x"], n["y"] = 740 + 60 * min(k, 0.3), NG
        sq = max(0, 1 - k / 0.3)
        n["sx"], n["sy"] = 1 + 0.3 * sq, 1 - 0.3 * sq
        n["ex"] = "dizzy" if k < 1.0 else "wow"
    elif t < 19.2:
        n["x"], n["y"] = 500, NG
        if t < 17.0:
            n["x"] = lerp(780, 500, eio(seg(t, 16.65, 17.0)))
        n["ex"] = "wow" if t < 18.5 else "joy"
        n_phone_screen = "scan" if 17.6 <= t < 18.5 else ("ok" if t >= 18.5 else "nowifi")
    elif t < 21.0:
        k = t - 19.2
        n["x"] = 500 + 30 * math.sin(k * 6)
        n["y"] = NG - abs(math.sin(k * 7)) * 120
        n["rot"] = 15 * math.sin(k * 7)
        n["ex"] = "joy"
        n_phone_screen = "ok"
    else:
        n["x"], n["y"] = 470, NG
        n["ex"] = "joy" if math.sin(t * 6) > -0.3 else "happy"
        n_phone_screen = "play"
        n["sy"] = 1 + 0.03 * math.sin(t * 12)

    # ---------------- GRUMPO state
    g = dict(x=GX, y=GY, ex="smug", look=(0.4, 0.6), sx=1, sy=1, rot=0, seated=True, phone="play", dots=0, red=0.0, shade=None)
    if t < 1.5:
        g["y"] = GY - 6 * abs(math.sin(t * 20))   # laughing
    if 3.8 <= t < 4.6:
        g["ex"], g["look"] = "suspicious", (-1, 0.2)
    if 4.6 <= t < 5.2:
        g["ex"], g["look"] = "smug", (-1, 0.2)
    if 5.2 <= t < 9.2:
        g["ex"], g["look"] = "grumpy", (0.5, 0.7)
        g["phone"] = "dots"
        g["dots"] = int(cl((t - 5.4) / 0.35, 0, 6)) % 7
    if 9.2 <= t < 10.25:
        g["phone"] = "dots"
        g["dots"] = 4
        g["ex"] = "suspicious"
        g["look"] = (1, -0.6) if t >= 9.55 else (0.6, 0.2)
    if 10.25 <= t < 11.1:
        g["ex"], g["look"], g["phone"], g["dots"] = "grumpy", (0.5, 0.7), "dots", 5
    if 11.1 <= t < 12.2:
        g["shade"] = 1.0 if t < 11.95 else max(0, 1 - (t - 11.95) / 0.1)
        g["ex"] = "angry"
        g["phone"] = None
    if 12.2 <= t < 12.6:
        g["ex"], g["look"] = "shock", (-1, 0)
        g["phone"] = None
    if 12.6 <= t < 14.2:
        g["seated"] = False
        g["phone"] = None
        g["ex"] = "angry"
        p = seg(t, 12.6, 14.0)
        g["x"] = lerp(GX, -260, ein(p) * 0.3 + p * 0.7)
        g["y"] = lerp(GY, FLOOR - 120, min(1, p * 4)) - abs(math.sin(t * 16)) * 26
    if 14.2 <= t < 15.3:
        g["seated"] = False
        g["phone"] = None
        p = seg(t, 14.2, 15.0)
        g["x"] = lerp(1250, 620, p)
        g["y"] = FLOOR - 120 - abs(math.sin(t * 16)) * 26 * (p < 1)
        g["ex"] = "angry" if t < 14.9 else "suspicious"
        g["look"] = (-1, 0) if t < 14.9 else (1, 0)
    if 15.3 <= t < 16.65:
        g["seated"] = False
        g["phone"] = None
        k = t - 15.3
        g["x"], g["y"] = 620 - 60 * min(k, 0.3), FLOOR - 120
        sq = max(0, 1 - k / 0.3)
        g["sx"], g["sy"] = 1 + 0.25 * sq, 1 - 0.25 * sq
        g["ex"] = "shock"
        g["look"] = (0, -1)
    if 16.65 <= t < 21.0:
        g["seated"] = False
        g["phone"] = None
        g["x"] = lerp(560, 820, eio(seg(t, 16.65, 17.0))) if t < 17.0 else 820
        g["y"] = FLOOR - 120
        g["ex"] = "shock" if t < 18.5 else "shock"
        g["look"] = (-1, 0.8) if t < 18.5 else (-1, 0.2)
        if 17.2 <= t < 17.7:
            g["x"] = lerp(820, 760, eio(seg(t, 17.2, 17.5)))
        if t >= 18.5:
            g["x"] = 760
    if 21.0 <= t < 25.6:
        g["seated"] = False
        g["x"], g["y"] = 800, FLOOR - 120
        g["phone"] = "spinner"
        g["ex"] = "grumpy" if t < 22.5 else "angry"
        g["look"] = (0.4, 0.7) if t < 23.6 else (-1, 0.3)
        if 22.5 <= t < 23.6:
            g["x"] += 8 * math.sin(t * 60)   # shaking the phone
        if t >= 24.4:
            g["red"] = 0.0
    if t >= 25.6:
        g["seated"] = False
        g["phone"] = None
        p = ein(seg(t, 25.6, 25.95))
        g["x"], g["y"] = 800 + 40 * p, lerp(FLOOR - 120, FLOOR - 92, p)
        g["rot"] = 85 * p
        g["ex"] = "grumpy"
        if t >= 25.95:
            k = t - 25.95
            sq = max(0, 1 - k / 0.3)
            g["sx"], g["sy"] = 1 + 0.15 * sq, 1 - 0.15 * sq

    # ---------------- draw: behind-chair layer
    def draw_nibbo():
        o = []
        if not n["vis"]:
            return ""
        if n["layer"] == "front" and n["y"] > NG - 200:
            o.append(shadow(n["x"], FLOOR + 4, 110, 1 - (NG - n["y"]) / 400))
        o.append(bloop(ctx, n["x"], n["y"], NR, n["ex"], rot=n["rot"], sx=n["sx"], sy=n["sy"]))
        if n.get("shade"):
            o.append(shade_svg(n["x"], n["y"] - 70, n["rot"], 1.05))
        if "shade_lift" in n:
            p = n["shade_lift"]
            o.append(shade_svg(lerp(LAMP_X, n["x"], p), lerp(1100, n["y"] - 70, p) - 120 * math.sin(math.pi * p), 0, 1.0))
        if n_phone_screen:
            px, py = n["x"] + 125, n["y"] - 20
            if 2.4 <= t < 6.0:
                py = n["y"] - 120
            if 17.0 <= t < 19.2:
                px, py = n["x"] + 120, n["y"] + 10
            if t >= 21.0:
                px, py = n["x"] + 110, n["y"] - 10
            o.append(arm(n["x"] + NR * 0.85, n["y"] + 20, px - 20, py + 30))
            o.append(phone(px, py, -8 if t < 21 else -15, n_phone_screen, 1.0, t, n_bars, scan=t))
        if n["layer"] == "front" and 12.45 <= t < 13.4:
            o.append(router(n["x"] - 80, n["y"] - 70, -20, t=t, s=0.85))
            o.append(speed_lines(n["x"] + 90, n["y"], 180, 0.8))
        if 14.2 <= t < 15.3:
            o.append(speed_lines(n["x"] + 90, n["y"], 180, 0.8))
        return "".join(o)

    def draw_grumpo():
        o = []
        if not g["seated"]:
            o.append(shadow(g["x"], FLOOR + 4, 120))
        o.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"], False, 0, None, 0, t))
        if g["phone"]:
            px, py = g["x"] + 150, g["y"] - 40
            if g["phone"] == "spinner" and 22.5 <= t < 23.6:
                py += 14 * math.sin(t * 50)
            o.append(arm(g["x"] + 100, g["y"] + 30, px - 20, py + 30, "#221c2e", 11))
            o.append(phone(px, py, 8, g["phone"], 1.0, t, dots=g["dots"]))
        if g["shade"]:
            o.append(f'<g opacity="{g["shade"]:.2f}">' + shade_svg(g["x"], g["y"] - 40, 8, 1.15) + '</g>')
        if 12.6 <= t < 14.2:
            o.append(speed_lines(g["x"] + 100, g["y"], 180, 0.8))
            o.append(f'<path d="M{g["x"]-30:.0f} {g["y"]-150:.0f} q10 -30 0 -50 M{g["x"]+30:.0f} {g["y"]-150:.0f} q-10 -30 0 -50" stroke="#e8303a" stroke-width="7" fill="none" stroke-linecap="round"/>')
        return "".join(o)

    # order
    if n["layer"] == "behindchair":
        L.append(draw_nibbo())
    if r["layer"] == "behind":
        L.append(router(r["x"], r["y"], r["rot"], t=t))
    L.append(chair_back())
    if g["seated"]:
        L.append(draw_grumpo())
    L.append(chair_front())
    if r["layer"] == "table":
        L.append(router(r["x"], r["y"], r["rot"], t=t))
    if not g["seated"]:
        L.append(draw_grumpo())
    if n["layer"] == "front":
        L.append(draw_nibbo())
    if r["layer"] == "front":
        L.append(router(r["x"], r["y"], r["rot"], r["flipped"], t, 1.0))

    # ---------- effects
    L.append(symbol(380, 1170, "!", seg(t, 1.7, 2.3)))
    L.append(symbol(GX - 20, 1060, "?", seg(t, 9.55, 10.25), "#3a7ad6"))
    L.append(symbol(GX - 20, 1060, "!", seg(t, 3.8, 4.4)))
    L.append(impact(1060, 1300, seg(t, 11.1, 11.35)))
    L.append(impact(690, NG, seg(t, 15.3, 15.55)))
    L.append(impact(650, FLOOR - 40, seg(t, 16.65, 16.9), "#f1e3c4"))
    if 16.0 <= t < 16.7:
        L.append(f'<g opacity="0.0"></g>')
    # dust clouds during chase
    for t0, x0 in ((12.6, 900), (12.5, 1110)):
        p = seg(t, t0, t0 + 0.6)
        if 0 < p < 1:
            for k in range(4):
                L.append(f'<circle cx="{x0 + 40*k - 60 + 60*p:.0f}" cy="{FLOOR - 20 - 30*p:.0f}" r="{24 + 30*p:.0f}" fill="#f2ead8" stroke="#c8b898" stroke-width="4" opacity="{1-p:.2f}"/>')
    # wifi waves from router toward nibbo's phone (hot-cold)
    if 3.0 <= t < 5.0:
        for k in range(3):
            pp = ((t * 1.6) + k / 3) % 1
            rr = 30 + 200 * pp
            L.append(f'<path d="M{660 - rr*0.8:.0f} {1230 - rr*0.4:.0f} A{rr:.0f} {rr:.0f} 0 0 0 {660 - rr*0.8:.0f} {1230 + rr*0.4:.0f}" fill="none" stroke="#3ce07a" stroke-width="6" opacity="{(1-pp)*0.8:.2f}"/>')
    # scan beam to QR
    if 17.6 <= t < 18.5:
        L.append(f'<path d="M620 {NG+10} L630 {FLOOR-40} L670 {FLOOR-40}Z" fill="#ff4d5e" opacity="{0.25 + 0.15*math.sin(t*30):.2f}"/>')
    # 'connected' sparkles
    if 18.5 <= t < 19.4:
        p = seg(t, 18.5, 19.4)
        for k in range(6):
            a = k * 1.05
            L.append(star_twinkle(620 + 120 * math.cos(a) * p, NG - 40 + 100 * math.sin(a) * p, p))
    # buffering cloud over grumpo + nibbo's streaming waves
    if t >= 23.6 and t < 25.6:
        p = seg(t, 23.6, 24.2)
        a = t * 300
        L.append(f'<g transform="translate(800 {FLOOR-330}) scale({0.6 + 0.6*p:.2f}) rotate({a:.1f})"><circle r="40" fill="none" stroke="#c9ccd6" stroke-width="12"/>'
                 '<path d="M0 -40 A40 40 0 0 1 40 0" fill="none" stroke="#3a7ad6" stroke-width="12" stroke-linecap="round"/></g>')
    if t >= 21.0:
        for k in range(3):
            pp = ((t * 1.4) + k / 3) % 1
            rr = 20 + 140 * pp
            L.append(f'<path d="M{580 + rr*0.7:.0f} {NG - 120 - rr*0.5:.0f} A{rr:.0f} {rr:.0f} 0 0 1 {580 + rr*0.7:.0f} {NG - 120 + rr*0.5:.0f}" fill="none" stroke="#3ce07a" stroke-width="5" opacity="{(1-pp)*0.7:.2f}"/>')
    L.append(impact(840, FLOOR - 40, seg(t, 25.95, 26.25), "#f1e3c4"))

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs>{DEFS2}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g></svg>')


def build_sfx():
    sfx(0.05, "error_beep", 0.9)
    sfx(0.2, "laugh", 0.6, 1.1)
    sfx(1.7, "alert", 0.7)
    sfx(1.75, "lock_click", 0.7)
    for k in range(10):
        sfx(2.4 + k * 0.2, "tiptoe", 0.5, 1.0 + 0.1 * (k % 2))
    for i, tt in enumerate((3.0, 3.6, 4.2)):
        sfx(tt, "blip", 0.8, 1.0 + 0.2 * i)
    sfx(3.8, "suspense", 0.6)
    sfx(4.6, "whoosh", 0.7, 1.3)
    sfx(5.0, "blip_down", 0.9)
    sfx(5.15, "gulp", 0.6, 1.2)
    for k in range(6):
        sfx(5.45 + k * 0.35, "typing", 0.5, 1.0 + 0.05 * k)
    sfx(6.55, "pop", 0.8, 1.2)
    sfx(6.9, "boing", 0.4, 1.6)
    sfx(7.0, "sneak", 0.6)
    sfx(8.1, "squeak", 0.5, 1.1)
    sfx(9.55, "alert", 0.6, 0.85)
    sfx(9.6, "whoosh", 0.4, 1.5)
    sfx(10.3, "creak", 0.6, 1.2)
    sfx(10.8, "slide_down", 0.6, 1.4)
    sfx(11.1, "thunk", 0.9, 1.1)
    sfx(11.25, "thud", 0.9)
    sfx(11.4, "grumble", 0.6, 1.2)
    sfx(11.95, "pop", 0.7, 0.9)
    sfx(12.2, "zip", 0.8)
    sfx(12.45, "whoosh", 0.7)
    for k in range(9):
        sfx(12.5 + k * 0.17, "tiptoe", 0.6, 0.7 + 0.05 * (k % 3))
    sfx(12.6, "zip", 0.7, 0.8)
    sfx(14.2, "whoosh", 0.7, 1.1)
    for k in range(6):
        sfx(14.25 + k * 0.17, "tiptoe", 0.6, 0.75)
    sfx(14.9, "suspense", 0.4, 1.3)
    sfx(15.3, "bonk", 1.1)
    sfx(15.32, "boing", 0.7, 0.9)
    sfx(15.35, "slide_up", 0.6, 1.0)
    sfx(16.0, "slide_down", 0.6, 1.2)
    sfx(16.65, "thud", 1.0, 1.1)
    sfx(16.75, "zoom", 0.6)
    sfx(17.1, "ding", 0.5, 0.8)
    sfx(17.6, "scan", 0.8)
    sfx(18.5, "ding", 0.9, 1.3)
    sfx(18.55, "cool", 0.6)
    sfx(19.2, "boing", 0.6, 1.3); sfx(19.65, "boing", 0.6, 1.45); sfx(20.1, "boing", 0.6, 1.6)
    sfx(19.3, "cheer", 0.5, 1.2)
    sfx(21.0, "laugh", 0.6, 1.25)
    sfx(21.2, "blip_down", 0.5, 0.8)
    sfx(22.5, "shaker", 0.8, 0.8)
    sfx(23.6, "error_beep", 0.8, 0.9)
    sfx(24.0, "laugh", 0.5, 1.35)
    sfx(24.6, "grumble", 0.7)
    sfx(25.6, "slide_down", 0.5, 1.6)
    sfx(25.95, "thud", 1.0, 0.9)
    sfx(26.2, "laugh", 0.6, 1.3)
