"""Grumpo & Nibbo — Episode 1: The Pool (v2 quality, 60 fps, 30 s)."""
import math, random, json, sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import *
from still_v2 import pool, ring2, GROUND, POOL_X0, POOL_X1, WATER, POOL_BOT

W, H, FPS, DUR = 1080, 1920, 60, 30.0
NR = 112                 # nibbo radius
NG = GROUND - 26 - NR    # nibbo center on ground (grass top ~1224)
GX = 1120
GS = 0.92
SIGN_X, SIGN_Y = 560, GROUND - 380
BUSH_X = 330
TR_X = 470               # trampoline
TOWER_X = 1700
PLAT_Y = 380

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


def ballistic(p0, v, g, tau):
    return p0[0] + v[0] * tau, p0[1] + v[1] * tau + 0.5 * g * tau * tau


# ------------------------------------------------------------ timings
G1_START, G1_HIT = 2.6, 4.3
G1_HOPS = [(330, 480), (480, 620)]
G1_APEX = (880, 800)
G1_V = (-900, -2300)
G1_RETURN, G1_CRASH = 6.9, 7.45
G2_WALK0, G2_DIVE, G2_SWIM1 = 8.6, 9.5, 11.4
G2_POUR0, G2_POUR1, G2_LAUNCH = 11.8, 12.4, 12.75
G2_P0 = (1290, 1520)
G2_V = (-700, -2000)
G2_G = 2600
G3_DRAG0, G3_DRAG1 = 15.0, 16.0
G3_BOUNCES = [16.35, 16.9, 17.55]
G3_UMB0, G3_UMB_HIT = 17.75, 18.4
G3_SIGN_HIT = 19.0
G3_SLIDE1 = 20.15
F_DASH, F_CLIMB0, F_CLIMB1 = 21.35, 22.2, 23.0
F_BOARD, F_JUMP, F_SPLASH = 23.0, 23.7, 24.8
F_GLAND = 26.0
F_RLAND, F_NLAND = 25.9, 26.25

rnd = random.Random(21)
LEAVES = [(rnd.uniform(-1, 1), rnd.uniform(-900, -400), rnd.uniform(-500, 500), rnd.uniform(0, 360)) for _ in range(18)]
RAIN = [(rnd.uniform(250, 1750), rnd.uniform(-700, 300), rnd.uniform(9, 20), rnd.uniform(0, 0.5)) for _ in range(80)]
SPRAY = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(30)]


# ------------------------------------------------------------ camera
C0 = (760, 1080, 1.0)
CAMKEYS = [
    (0.0, (1120, 1130, 1.3)), (1.7, C0),
    (9.4, C0), (10.0, (900, 1190, 1.0)), (12.9, (900, 1190, 1.0)), (13.6, C0),
    (21.5, C0), (22.4, (1450, 840, 0.85)), (23.5, (1450, 820, 0.85)), (24.15, (1280, 700, 0.8)),
    (24.8, (1080, 1100, 0.85)), (25.6, (1040, 1200, 0.88)), (26.6, (1040, 1250, 0.9)),
    (27.0, (1120, 1470, 1.45)), (28.2, (1120, 1470, 1.45)), (28.7, (860, 1280, 0.9)), (30.0, (860, 1280, 0.9)),
]
SHAKES = [(G1_HIT, 8, 0.2), (G1_CRASH, 12, 0.3), (G2_LAUNCH, 8, 0.25), (G3_UMB_HIT, 8, 0.2),
          (G3_SIGN_HIT, 14, 0.3), (G3_SLIDE1, 6, 0.2), (F_SPLASH, 30, 0.6), (F_GLAND, 22, 0.4), (F_NLAND, 6, 0.2)]


def camera(t):
    k0 = CAMKEYS[0]
    for i in range(1, len(CAMKEYS)):
        k1 = CAMKEYS[i]
        if t <= k1[0]:
            p = eio(seg(t, k0[0], k1[0]))
            a, b = k0[1], k1[1]
            cx, cy, z = lerp(a[0], b[0], p), lerp(a[1], b[1], p), lerp(a[2], b[2], p)
            break
        k0 = k1
    else:
        cx, cy, z = CAMKEYS[-1][1]
    amp = 0
    for t0, a, d in SHAKES:
        if t0 <= t < t0 + d:
            amp = max(amp, a * (1 - (t - t0) / d))
    if 27.2 <= t < 28.2:
        amp = max(amp, 3)
    return cx + amp * math.sin(t * 93), cy + amp * math.cos(t * 79), z


# ------------------------------------------------------------ props
def trampoline(x, dip=0.0):
    y = GROUND - 26
    return (f'<g stroke="{OL}" stroke-width="6" stroke-linecap="round"><line x1="{x-110}" y1="{y-70}" x2="{x-130}" y2="{y}"/><line x1="{x+110}" y1="{y-70}" x2="{x+130}" y2="{y}"/>'
            f'<line x1="{x-40}" y1="{y-70}" x2="{x-50}" y2="{y}"/><line x1="{x+40}" y1="{y-70}" x2="{x+50}" y2="{y}"/></g>'
            f'<path d="M{x-120} {y-78} Q {x} {y-78+dip*2} {x+120} {y-78}" fill="none" stroke="#2a2a33" stroke-width="16"/>'
            f'<rect x="{x-136}" y="{y-92}" width="272" height="22" rx="11" fill="#3ac0ff" stroke="{OL}" stroke-width="6"/>'
            f'<path d="M{x-110} {y-82} h220" stroke="#9be3ff" stroke-width="5" stroke-linecap="round"/>')


def tower():
    x = TOWER_X
    o = [f'<g stroke="{OL}" stroke-width="6">',
         f'<rect x="{x-80}" y="{PLAT_Y}" width="22" height="{GROUND-PLAT_Y}" fill="#e8ecf1"/><rect x="{x+58}" y="{PLAT_Y}" width="22" height="{GROUND-PLAT_Y}" fill="#e8ecf1"/>']
    for y in range(PLAT_Y + 60, GROUND - 20, 70):
        o.append(f'<rect x="{x-58}" y="{y}" width="116" height="12" rx="4" fill="#cfd6de"/>')
    o.append(f'<rect x="{x-130}" y="{PLAT_Y-26}" width="240" height="30" rx="6" fill="#3a8fd0"/>')
    o.append('</g>')
    o.append(f'<path d="M{x-120} {PLAT_Y-26} v-60 M{x+100} {PLAT_Y-26} v-60 M{x-120} {PLAT_Y-80} h220" fill="none" stroke="{OL}" stroke-width="14" stroke-linecap="round"/>'
             f'<path d="M{x-120} {PLAT_Y-26} v-60 M{x+100} {PLAT_Y-26} v-60 M{x-120} {PLAT_Y-80} h220" fill="none" stroke="#dfe6ee" stroke-width="7" stroke-linecap="round"/>')
    return "".join(o)


def board(dip=0.0):
    x0, x1, y = TOWER_X - 130, 1470, PLAT_Y - 14
    return (f'<path d="M{x0} {y} Q {lerp(x0, x1, 0.6):.0f} {y + dip*0.4:.0f} {x1} {y + dip:.0f}" fill="none" stroke="{OL}" stroke-width="26" stroke-linecap="round"/>'
            f'<path d="M{x0} {y} Q {lerp(x0, x1, 0.6):.0f} {y + dip*0.4:.0f} {x1} {y + dip:.0f}" fill="none" stroke="#ffffff" stroke-width="15" stroke-linecap="round"/>')


def umbrella(x, y, open_p, squash=0.0):
    if open_p <= 0:
        return ""
    w = 200 * open_p
    h = (120 - squash * 50) * open_p
    segs = []
    n = 6
    for k in range(n):
        xa = x - w + 2 * w * k / n
        xb = x - w + 2 * w * (k + 1) / n
        col = "#ff4d5e" if k % 2 == 0 else "#ffffff"
        segs.append(f'<path d="M{x} {y-h:.1f} L{xa:.1f} {y:.1f} Q {(xa+xb)/2:.1f} {y-14:.1f} {xb:.1f} {y:.1f}Z" fill="{col}"/>')
    return (f'<line x1="{x}" y1="{y-h:.1f}" x2="{x+20}" y2="{y+150}" stroke="{OL}" stroke-width="9"/><line x1="{x}" y1="{y-h:.1f}" x2="{x+20}" y2="{y+150}" stroke="#d9c49a" stroke-width="4"/>'
            + "".join(segs) +
            f'<path d="M{x-w:.1f} {y:.1f} Q {x:.1f} {y-h*2+10:.1f} {x+w:.1f} {y:.1f}" fill="none" stroke="{OL}" stroke-width="0"/>'
            f'<path d="M{x} {y-h:.1f} L{x-w:.1f} {y:.1f} ' + " ".join(f"Q {x - w + 2*w*(k+0.5)/n:.1f} {y-14:.1f} {x - w + 2*w*(k+1)/n:.1f} {y:.1f}" for k in range(n)) + f' Z" fill="none" stroke="{OL}" stroke-width="6" stroke-linejoin="round"/>'
            f'<circle cx="{x}" cy="{y-h-6:.1f}" r="9" fill="#ff4d5e" stroke="{OL}" stroke-width="4"/>')


def snorkel_mask(x, y, r, rot=0, tube_top=None):
    s = r / 112
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">',
         f'<path d="M{-r:.1f} {-20*s:.1f} Q 0 {-40*s:.1f} {r:.1f} {-20*s:.1f}" fill="none" stroke="#2a6fd6" stroke-width="{12*s:.1f}"/>',
         f'<rect x="{-70*s:.1f}" y="{-58*s:.1f}" width="{140*s:.1f}" height="{70*s:.1f}" rx="{30*s:.1f}" fill="#bfefff" fill-opacity="0.55" stroke="{OL}" stroke-width="{6*s:.1f}"/>',
         f'<rect x="{-60*s:.1f}" y="{-50*s:.1f}" width="{40*s:.1f}" height="{12*s:.1f}" rx="5" fill="#fff" opacity="0.8"/></g>']
    if tube_top is not None:
        tx = x + 70 * s
        o.append(f'<path d="M{tx-20*s:.1f} {y+10*s:.1f} Q {tx+10*s:.1f} {y+10*s:.1f} {tx+10*s:.1f} {y-30*s:.1f} L{tx+10*s:.1f} {tube_top:.1f}" fill="none" stroke="{OL}" stroke-width="{24*s:.1f}" stroke-linecap="round"/>'
                 f'<path d="M{tx-20*s:.1f} {y+10*s:.1f} Q {tx+10*s:.1f} {y+10*s:.1f} {tx+10*s:.1f} {y-30*s:.1f} L{tx+10*s:.1f} {tube_top:.1f}" fill="none" stroke="#ff8a1e" stroke-width="{14*s:.1f}" stroke-linecap="round"/>')
    return "".join(o)


def cup(x, y, rot=0, full=1.0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})"><path d="M-20 -30 h40 l-8 60 h-24z" fill="#fff3a8" stroke="{OL}" stroke-width="6"/>'
            + (f'<path d="M-17 {-10 + 20*(1-full):.1f} h34" stroke="#ffb02a" stroke-width="{max(1, 18*full):.1f}" opacity="0.7"/>' if full > 0.05 else "") +
            '<path d="M6 -30 L22 -70" stroke="#ff5a6e" stroke-width="7" stroke-linecap="round"/><circle cx="-12" cy="-34" r="9" fill="#7be08a" stroke="#221c2e" stroke-width="3"/></g>')


def glasses_sprite(x, y, rot=0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})"><rect x="-80" y="-18" width="66" height="38" rx="14" fill="#1a1a22"/><rect x="14" y="-18" width="66" height="38" rx="14" fill="#1a1a22"/>'
            '<path d="M-14 -2 h28" stroke="#1a1a22" stroke-width="8"/><path d="M-66 -10 h20 M28 -10 h20" stroke="#5a5a70" stroke-width="5" stroke-linecap="round"/></g>')


def dust(x, y, p, s=1.0):
    if p <= 0 or p >= 1:
        return ""
    o = []
    for k in range(5):
        a = math.radians(160 + k * 12)
        d = 40 + 160 * p
        o.append(f'<circle cx="{x + d*math.cos(a)*s:.1f}" cy="{y + d*math.sin(a)*0.3 - 30*p:.1f}" r="{(26 + 30*p)*s:.1f}" fill="#f2ead8" stroke="#c8b898" stroke-width="4" opacity="{1-p:.2f}"/>')
    return "".join(o)


def drip_drops(x, y, t, n=5, spread=110):
    o = []
    for k in range(n):
        p = (t * 1.3 + k / n) % 1
        dx = (k - n / 2) * spread / n
        o.append(f'<path d="M{x+dx:.1f} {y + p*140:.1f} q8 14 0 20 q-8 -6 0 -20z" fill="#9be6ff" stroke="#2a86cf" stroke-width="3" opacity="{1-p:.2f}"/>')
    return "".join(o)


# ------------------------------------------------------------ frame
def frame(t):
    ctx = Ctx()
    L = [sky(-200, 2400), sun(1180, 420)]
    for (cx0, cy0, s) in [(500, 520, 1.1), (1250, 700, 0.8), (-50, 760, 0.9), (1900, 460, 1.0), (900, 260, 0.7)]:
        L.append(cloud((cx0 + t * 10 * s + 400) % 2800 - 400, cy0, s))
    L.append(hills(-200, 2400, GROUND))
    L.append(ground_strip(-200, 2400, GROUND))
    L.append(underground(t))

    # water level
    wl = WATER
    if t >= F_SPLASH:
        wl = lerp(WATER, POOL_BOT - 40, eout(seg(t, F_SPLASH, F_SPLASH + 0.5)))
    L.append(tower())
    L.append(pool(t, wl))

    # ---------------- sign (with wobble on impact)
    sp = eback(seg(t, 0.45, 0.8)) if t >= 0.45 else 0
    wob = 0
    if G3_SIGN_HIT <= t < G3_SIGN_HIT + 0.8:
        k = t - G3_SIGN_HIT
        wob = 9 * math.sin(k * 30) * (1 - k / 0.8)
    icon = bloop(ctx, 0, 0, 52, "happy")
    if sp > 0:
        L.append(f'<g transform="rotate({wob:.1f} {SIGN_X} {GROUND-26})">{sign2(SIGN_X, GROUND - 26, icon, top=SIGN_Y, s=sp)}</g>')
    L.append(tufts([520, 600, 250, 1650, 1820, 90], GROUND))

    # ---------------- NIBBO behind bush (peeks)
    behind = []
    if t < G1_START:
        p = eback(seg(t, 1.55, 1.85))
        hide = eio(seg(t, 2.15, 2.4))
        y = lerp(1110, 1020, p) + 140 * hide
        behind.append(bloop(ctx, 300, y, NR, "happy", rot=-8 * p))
    if G1_CRASH + 0.2 <= t < G2_WALK0:
        p = eback(seg(t, 7.75, 8.05))
        hide = eio(seg(t, 8.35, 8.55))
        y = lerp(1130, 1030, p) + 140 * hide
        behind.append(bloop(ctx, 330, y, NR, "dizzy"))
        if p > 0.5 and hide < 0.5:
            for k in range(3):
                a = t * 6 + k * 2.1
                behind.append(star_twinkle(330 + 70 * math.cos(a), 900 + 18 * math.sin(a), 0.5))
    L += behind
    # bush shake + crash
    bshake = 0
    if G1_CRASH <= t < G1_CRASH + 0.5:
        bshake = 14 * math.sin((t - G1_CRASH) * 50) * (1 - (t - G1_CRASH) / 0.5)
    L.append(f'<g transform="translate({bshake:.1f} 0)">{bush_big(BUSH_X, GROUND - 26, 0.95)}</g>')
    if G1_CRASH <= t < G1_CRASH + 1.2:
        tau = t - G1_CRASH
        for (dx, vy, vx, r0) in LEAVES:
            x, y = BUSH_X + dx * 120 + vx * tau, 1040 + vy * tau + 900 * tau * tau
            if y < GROUND:
                L.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({r0 + tau*400:.1f})"><path d="M-30 0 Q 0 -26 30 0 Q 0 26 -30 0Z" fill="#6dbb5f" stroke="{OL}" stroke-width="4"/><path d="M-22 0 H22" stroke="#4f9e4c" stroke-width="3"/></g>')

    # ---------------- trampoline
    tr_x = None
    dip = 0
    if G3_DRAG0 <= t < 30:
        tr_x = lerp(-250, TR_X, eout(seg(t, G3_DRAG0, G3_DRAG1)))
        for b in G3_BOUNCES:
            if b <= t < b + 0.25:
                dip = 40 * math.sin(math.pi * (t - b) / 0.25)
        L.append(trampoline(tr_x, dip))

    # ---------------- RING + GRUMPO state
    g = dict(x=GX, y=wl - 112 + 5 * math.sin(t * 2.2), expr="grumpy", look=(-0.6, 0), glasses="up", sip=0.0, drink=True,
             rot=0, sx=1, sy=1, red=0.0, steam=0.0)
    ring_xy = (GX, wl + 6 + 5 * math.sin(t * 2.2), 1.0, 0)
    gt = g
    if 0.9 <= t < 1.5:
        gt["sip"] = math.sin(seg(t, 0.9, 1.5) * math.pi)
    if 1.6 <= t < 2.5:
        gt["look"], gt["expr"] = (-1, -0.2), "suspicious"
    # gag1
    if 2.8 <= t < G1_HIT:
        gt["look"] = (-1, -0.6)
        gt["expr"] = "suspicious" if t < 3.7 else "smug"
    if 3.75 <= t < G1_HIT + 0.55:
        # header jump
        p = seg(t, 3.75, G1_HIT)
        q = seg(t, G1_HIT, G1_HIT + 0.55)
        if t < G1_HIT:
            gt["x"] = lerp(GX, 1000, eout(p))
            gt["y"] = lerp(wl - 112, 990, eout(p))
            gt["rot"] = -18 * p
        else:
            gt["x"] = lerp(1000, GX, eio(q))
            gt["y"] = lerp(990, wl - 112, ein(q) if q < 1 else 1)
            gt["rot"] = -18 * (1 - q)
        gt["expr"] = "angry"
        gt["look"] = (-1, -0.8)
        gt["glasses"] = "up"
    if G1_HIT + 0.55 <= t < 8.5:
        gt["expr"] = "smug"
        gt["look"] = (-0.5, -0.4)
        if 5.6 <= t < 6.3:
            gt["sip"] = math.sin(seg(t, 5.6, 6.3) * math.pi)
        if t >= G1_RETURN:
            gt["look"] = (-1, -0.3)
    # gag2
    if G2_WALK0 <= t < G2_SWIM1:
        gt["look"] = (-0.2, 0.3)
        gt["glasses"] = "down" if t > 8.9 else "up"
        gt["expr"] = "smug"
    pour_svg = ""
    if G2_SWIM1 <= t < G2_LAUNCH + 1.4:
        gt["glasses"] = "down"
        if t < G2_POUR0:
            gt["expr"], gt["look"] = "suspicious", (1, 1)
        elif t < G2_LAUNCH:
            gt["expr"], gt["look"] = "smug", (1, 1)
            gt["drink"] = False
            p = eio(seg(t, G2_POUR0, G2_POUR0 + 0.25))
            cxp, cyp = lerp(1282, 1300, p), lerp(1133, 1170, p)
            rot = lerp(0, 125, p)
            full = 1 - seg(t, G2_POUR0 + 0.2, G2_POUR1)
            pour_svg += (f'<path d="M{gt["x"]+105:.1f} {gt["y"]+30:.1f} Q {gt["x"]+170:.1f} {gt["y"]+60:.1f} {cxp-10:.1f} {cyp+20:.1f}" fill="none" stroke="#221c2e" stroke-width="12" stroke-linecap="round"/>')
            pour_svg += cup(cxp, cyp, rot, full)
            if G2_POUR0 + 0.2 <= t < G2_POUR1 + 0.1:
                pour_svg += f'<path d="M{cxp+26:.1f} {cyp+8:.1f} Q {cxp+30:.1f} {cyp+40:.1f} 1296 {WATER-36}" fill="none" stroke="#ffb02a" stroke-width="10" stroke-linecap="round" opacity="0.85"/>'
        else:
            gt["expr"], gt["look"] = "smug", (-1, -0.4)
            if t < G2_LAUNCH + 1.0:
                gt["y"] -= 8 * abs(math.sin(t * 22))
    if G2_LAUNCH + 1.4 <= t < G3_UMB0:
        gt["expr"], gt["look"] = "smug", (-0.6, 0)
        gt["glasses"] = "down" if t < 15.5 else "up"
    # gag3
    umb = None
    if 16.3 <= t < 21.0:
        gt["look"] = (-1, -0.4)
        gt["expr"] = "suspicious" if t < G3_UMB0 else "smug"
        if t >= 17.2 and t < G3_UMB0:
            gt["expr"] = "shock"
        if G3_UMB0 <= t < 19.6:
            op = eback(seg(t, G3_UMB0, G3_UMB0 + 0.2))
            sq = 0
            if G3_UMB_HIT <= t < G3_UMB_HIT + 0.3:
                sq = math.sin(math.pi * (t - G3_UMB_HIT) / 0.3)
            close = seg(t, 19.3, 19.6)
            umb = (gt["x"] + 10, gt["y"] - 150 + 40 * sq, op * (1 - close), sq)
            gt["drink"] = False
        if 19.6 <= t < 20.6:
            gt["y"] -= 8 * abs(math.sin(t * 22))
    # finale
    if 21.0 <= t < F_SPLASH:
        gt["look"] = (-1, -0.2) if t < 22.2 else (1, -1)
        gt["expr"] = "smug" if t < 23.4 else ("suspicious" if t < 23.85 else "shock")
        if 22.4 <= t < 23.2:
            gt["sip"] = math.sin(seg(t, 22.4, 23.2) * math.pi)
        if t >= 24.25:
            gt["glasses"] = "none"
    if t >= F_SPLASH:
        gt["glasses"], gt["drink"] = "none", False
        tau = t - F_SPLASH
        if t < F_GLAND:
            # up with column then down into empty pool
            up = seg(t, F_SPLASH, F_SPLASH + 0.5)
            dn = seg(t, F_SPLASH + 0.5, F_GLAND)
            gt["y"] = lerp(WATER - 112, 330, eout(up)) if dn == 0 else lerp(330, POOL_BOT - 118, ein(dn))
            gt["rot"] = -360 * eio(seg(t, F_SPLASH, F_GLAND))
            gt["expr"] = "shock"
        else:
            k = t - F_GLAND
            sq = max(0, 1 - k / 0.3)
            gt["sx"], gt["sy"] = 1 + 0.25 * sq * math.cos(k * 30), 1 - 0.25 * sq * math.cos(k * 30)
            gt["y"] = POOL_BOT - 118 + 120 * (1 - gt["sy"])
            gt["expr"] = "shock" if k < 0.6 else "angry"
            gt["red"] = eio(seg(t, F_GLAND + 0.6, F_GLAND + 1.4))
            gt["steam"] = seg(t, 27.2, 27.5)
            gt["look"] = (-1, -0.5) if t > 28.5 else (0, 0)
            if gt["red"] > 0.3:
                gt["x"] += 4 * math.sin(t * 70) * gt["red"]
        # ring flies to grass
        if t < F_RLAND:
            p = seg(t, F_SPLASH, F_RLAND)
            ring_xy = (lerp(GX, 380, p), lerp(WATER, GROUND - 40, p) - 900 * math.sin(math.pi * p), 1.0, 540 * p)
        else:
            k = t - F_RLAND
            ring_xy = (380, GROUND - 40, 1.0, 6 * math.sin(k * 25) * max(0, 1 - k / 0.5))

    # ---------------- NIBBO main (front layer) — computed, drawn later in proper order
    N = []          # svg pieces drawn before ring/grumpo
    NF = []         # drawn after grumpo (front)
    # gag1: beach ball bounce
    if G1_START <= t < G1_HIT + 1.2:
        tau = t - G1_START
        sx = sy = 1
        if tau < 0.7:
            k = int(tau / 0.35)
            p = (tau - 0.35 * k) / 0.35
            xa, xb = G1_HOPS[k]
            x, y = lerp(xa, xb, p), NG - 170 * math.sin(math.pi * p)
            if p < 0.15:
                sy, sx = lerp(0.75, 1, p / 0.15), lerp(1.2, 1, p / 0.15)
            NF.append(shadow(x, GROUND - 22, 110, 1 - 0.4 * math.sin(math.pi * p)))
            NF.append(bloop(ctx, x, y, NR, "joy", rot=p * 140 + k * 140, sx=sx, sy=sy, paint="beach"))
        elif t < G1_HIT:
            p = seg(t, G1_START + 0.7, G1_HIT)
            x = lerp(620, G1_APEX[0], p)
            y = lerp(NG, G1_APEX[1], math.sin(p * math.pi / 2))
            if p < 0.1:
                sy, sx = lerp(0.72, 1, p / 0.1), lerp(1.25, 1, p / 0.1)
            NF.append(bloop(ctx, x, y, NR, "happy" if p < 0.75 else "wow", rot=280 + p * 120, sx=sx, sy=sy, paint="beach"))
        else:
            k = t - G1_HIT
            x, y = ballistic(G1_APEX, G1_V, 1800, k)
            if y > -200:
                NF.append(speed_lines(x, y, -110, 0.9))
                NF.append(bloop(ctx, x, y, NR, "dizzy", rot=-1100 * k, paint="beach", sx=1.2 if k < 0.06 else 1, sy=0.8 if k < 0.06 else 1))
        NF.append(impact(G1_APEX[0] + 60, G1_APEX[1] + 90, seg(t, G1_HIT, G1_HIT + 0.25)))
    NF.append(star_twinkle(G1_APEX[0] - 900 * 0.5 + 80, 60, seg(t, 4.85, 5.4)))
    # return fall into bush
    if G1_RETURN <= t < G1_CRASH + 0.05:
        p = ein(seg(t, G1_RETURN, G1_CRASH))
        NF.append(bloop(ctx, lerp(560, BUSH_X, p), lerp(-150, 1080, p), NR, "wow", rot=720 * p, paint="beach"))
    NF.append(impact(BUSH_X, 1080, seg(t, G1_CRASH, G1_CRASH + 0.3), "#c8f0b0"))

    # gag2: snorkel
    if G2_WALK0 <= t < G2_DIVE + 0.3:
        if t < G2_DIVE:
            p = seg(t, G2_WALK0, G2_DIVE - 0.15)
            x = lerp(250, 640, p)
            y = NG - abs(math.sin(t * 11)) * 14 * (p < 1)
            N.append(shadow(x, GROUND - 22, 110))
            N.append(bloop(ctx, x, y, NR, "happy", rot=4 * math.sin(t * 11)))
            N.append(snorkel_mask(x, y - 10, NR, tube_top=y - 170))
        else:
            p = seg(t, G2_DIVE, G2_DIVE + 0.3)
            x = lerp(640, 790, p)
            y = lerp(NG, 1450, p) - 160 * math.sin(math.pi * p)
            N.append(bloop(ctx, x, y, NR, "joy", rot=90 * p))
            N.append(snorkel_mask(x, y - 10, NR, rot=90 * p))
    UW = []  # underwater nibbo (drawn clipped inside pool, before ring)
    if G2_DIVE + 0.3 <= t < G2_LAUNCH:
        p = eio(seg(t, G2_DIVE + 0.3, G2_SWIM1))
        x = lerp(790, G2_P0[0], p)
        y = lerp(1450, G2_P0[1], p) + 12 * math.sin(t * 3)
        sx = sy = 1
        ex = "happy"
        if t >= G2_POUR1:
            q = seg(t, G2_POUR1, G2_LAUNCH)
            sx, sy, ex = 1 + 0.25 * q + 0.03 * math.sin(t * 40), 1 + 0.2 * q, "wow"
        UW.append(bloop(ctx, x, y, NR, ex, sx=sx, sy=sy, rot=3 * math.sin(t * 3)))
        UW.append(snorkel_mask(x, y - 10, NR, tube_top=WATER - 40))
        for k in range(4):
            bp = ((t - G2_DIVE) * 0.9 + k * 0.25) % 1
            UW.append(f'<circle cx="{x - 40 + 12*math.sin(bp*8+k):.1f}" cy="{y - 120 - bp*(y-WATER-140):.1f}" r="{6+k*2}" fill="none" stroke="#e8fbff" stroke-width="4" opacity="{1-bp:.2f}"/>')
    if G2_LAUNCH <= t < 15.4:
        tau = t - G2_LAUNCH
        a, b, c = G2_G / 2, G2_V[1], G2_P0[1] - NG
        tl = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
        if tau < tl:
            x, y = ballistic(G2_P0, G2_V, G2_G, tau)
            NF.append(bloop(ctx, x, y, NR, "wow", rot=-400 * tau, sx=1.15, sy=1.1))
            NF.append(snorkel_mask(x, y - 10, NR, rot=-400 * tau))
            # spit fountain
            for k, (a1, a2) in enumerate(SPRAY[:14]):
                pp = ((tau * 3 + k / 14) % 1)
                NF.append(f'<circle cx="{x + 60 + pp*160 + a1*20:.1f}" cy="{y + 20 - pp*90 + pp*pp*200:.1f}" r="{10 - 6*pp:.1f}" fill="#ffb02a" opacity="{0.9*(1-pp):.2f}"/>')
            if y > WATER - 200 and tau < 0.3:
                NF.append(impact(G2_P0[0], WATER - 10, tau / 0.3, "#c8f4ff"))
        else:
            x = G2_P0[0] + G2_V[0] * tl
            k = tau - tl
            sq = max(0, 1 - k / 0.25)
            out = seg(t, 14.9, 15.3)
            xx = lerp(x, -200, out)
            yy = NG - 150 * math.sin(math.pi * out)
            NF.append(shadow(xx, GROUND - 22, 110))
            NF.append(bloop(ctx, xx, yy + 112 * 0.25 * sq, NR, "dizzy", sx=1 + 0.25 * sq, sy=1 - 0.25 * sq))
            NF.append(drip_drops(xx, yy - 40, t, 4, 120))

    # gag3: drag, bounce, umbrella, sign
    if G3_DRAG0 <= t < 16.35:
        if t < G3_DRAG1 + 0.1:
            x = tr_x - 230
            N.append(shadow(x, GROUND - 22, 110))
            N.append(bloop(ctx, x, NG + 4 * math.sin(t * 20), NR, "nervous", rot=-10))
        else:
            p = seg(t, G3_DRAG1 + 0.1, 16.35)
            x = lerp(TR_X - 230, TR_X, p)
            y = lerp(NG, GROUND - 26 - 92 - NR, p) - 160 * math.sin(math.pi * p)
            N.append(bloop(ctx, x, y, NR, "joy", rot=200 * p))
    if 16.35 <= t < G3_UMB_HIT:
        top = GROUND - 26 - 92 - NR
        bh = [220, 420]
        if t < G3_BOUNCES[2]:
            i = 0 if t < G3_BOUNCES[1] else 1
            t0, t1 = G3_BOUNCES[i], G3_BOUNCES[i + 1]
            p = seg(t, t0, t1)
            y = top - bh[i] * math.sin(math.pi * p) + 30 * max(0, 1 - p / 0.12) * (p < 0.12)
            sx = 1.2 if p < 0.08 else 1
            sy = 0.8 if p < 0.08 else 1
            N.append(shadow(TR_X, GROUND - 22, 110, 1 - 0.003 * (top - y + 200) / 2))
            N.append(bloop(ctx, TR_X, y, NR, "joy", sx=sx, sy=sy))
        else:
            p = seg(t, G3_BOUNCES[2], G3_UMB_HIT)
            hx, hy = gt["x"] - 30, gt["y"] - 150 - 120 - NR + 10
            x = lerp(TR_X, hx, p)
            y = lerp(top, hy, p) - 620 * math.sin(math.pi * p)
            NF.append(bloop(ctx, x, y, NR, "joy" if p < 0.6 else "wow", rot=360 * p))
    if G3_UMB_HIT <= t < G3_SIGN_HIT:
        p = seg(t, G3_UMB_HIT, G3_SIGN_HIT)
        hx, hy = GX - 30, WATER - 112 - 150 - 120 - NR + 10
        x = lerp(hx, SIGN_X + 70, p)
        y = lerp(hy, SIGN_Y, p) - 260 * math.sin(math.pi * p)
        NF.append(speed_lines(x, y, 180, 0.8))
        NF.append(bloop(ctx, x, y, NR, "wow", rot=-700 * p))
    if G3_SIGN_HIT <= t < 21.6:
        if t < G3_SLIDE1:
            p = seg(t, G3_SIGN_HIT + 0.25, G3_SLIDE1)
            y = lerp(SIGN_Y, NG, ein(p))
            flat = 1 - 0.5 * seg(t, G3_SLIDE1 - 0.3, G3_SLIDE1)
            NF.append(bloop(ctx, SIGN_X + 40, y, NR, "dizzy", sx=0.55 + 0.45 * (1 - flat), sy=1.2 - 0.2 * (1 - flat)))
        else:
            k = t - G3_SLIDE1
            sq = max(0, 1 - k / 0.25)
            x = SIGN_X + 40
            if t >= F_DASH:
                q = seg(t, F_DASH, F_DASH + 0.25)
                x = lerp(SIGN_X + 40, 1100, ein(q))
                NF.append(speed_lines(x, NG, 0, 0.9 * (1 - q)))
            ex = "dizzy" if t < 20.9 else ("wow" if t < 21.15 else "joy")
            NF.append(shadow(x, GROUND - 22, 110))
            NF.append(bloop(ctx, x, NG + NR * 0.25 * sq, NR, ex, sx=1 + 0.25 * sq, sy=1 - 0.25 * sq))
            if 20.25 <= t < 20.9:
                for k2 in range(3):
                    a = t * 6 + k2 * 2.1
                    NF.append(star_twinkle(x + 70 * math.cos(a), NG - 130 + 18 * math.sin(a), 0.5))
        NF.append(impact(SIGN_X + 40, SIGN_Y, seg(t, G3_SIGN_HIT, G3_SIGN_HIT + 0.25)))
        NF.append(dust(SIGN_X + 60, NG + 80, seg(t, F_DASH, F_DASH + 0.6), 1.2))
    NF.append(symbol(SIGN_X + 40, NG - 190, "!", seg(t, 20.95, 21.45), "#ffb020"))

    # finale: climb, board, jump
    if F_CLIMB0 <= t < F_SPLASH:
        if t < F_CLIMB1:
            p = seg(t, F_CLIMB0, F_CLIMB1)
            y = lerp(NG, PLAT_Y - 26 - NR, eio(p)) + 8 * math.sin(t * 40)
            NF.append(bloop(ctx, TOWER_X, y, NR, "happy", rot=6 * math.sin(t * 40)))
        elif t < F_JUMP:
            p = eio(seg(t, F_BOARD, 23.4))
            x = lerp(TOWER_X - 30, 1500, p)
            b = 0
            if t >= 23.4:
                q = seg(t, 23.4, F_JUMP)
                b = 40 * math.sin(math.pi * q * 2) * (1 - q * 0.5)
            yb = PLAT_Y - 14 - 13 - NR + b * ((x - (TOWER_X - 130)) / (1470 - TOWER_X + 130))
            NF.append(bloop(ctx, x, yb, NR, "joy" if t > 23.4 else "happy", sy=1 - 0.1 * (b > 20)))
        else:
            p = seg(t, F_JUMP, F_SPLASH)
            x = lerp(1500, GX, p)
            y0, y2 = PLAT_Y - 27 - NR, WATER - 60
            ctrl = -380
            y = (1 - p) ** 2 * y0 + 2 * p * (1 - p) * ctrl + p * p * y2
            cb = seg(t, 24.05, 24.25)
            NF.append(bloop(ctx, x, y, NR * (1 - 0.12 * cb), "joy" if cb > 0 else "happy", rot=500 * p * cb))
            if p > 0.55:
                NF.append(speed_lines(x, y, 100, 0.8))
    NF.append(symbol(TOWER_X, 120, "!", 0) )
    # splash & after
    if t >= F_SPLASH:
        tau = t - F_SPLASH
        # column
        if tau < 1.0:
            hh = 1050 * math.sin(min(1, tau / 0.45) * math.pi / 2) * (1 - seg(t, F_SPLASH + 0.5, F_SPLASH + 1.0))
            wdt = 300 + 260 * tau
            NF.append(f'<path d="M{GX-wdt:.0f} {WATER} Q {GX-wdt*0.4:.0f} {WATER-hh*0.9:.0f} {GX-60:.0f} {WATER-hh:.0f} Q {GX:.0f} {WATER-hh-60:.0f} {GX+60:.0f} {WATER-hh:.0f} Q {GX+wdt*0.4:.0f} {WATER-hh*0.9:.0f} {GX+wdt:.0f} {WATER}Z" fill="#8fe0ff" stroke="#2a86cf" stroke-width="7" opacity="{1-0.5*seg(t, F_SPLASH+0.5, F_SPLASH+1.0):.2f}"/>')
        # rain
        if tau < 1.8:
            for (x0, y0, r, dl) in RAIN:
                k = tau - 0.3 - dl
                if k < 0:
                    continue
                y = y0 + 300 + 1800 * k * k + 400 * k
                if y < GROUND + 10:
                    NF.append(f'<path d="M{x0:.0f} {y:.0f} q{r*0.6:.1f} {r:.1f} 0 {r*1.5:.1f} q{-r*0.6:.1f} {-r*0.5:.1f} 0 {-r*1.5:.1f}z" fill="#9be6ff" stroke="#2a86cf" stroke-width="3"/>')
        # nibbo launched to ring
        if t < F_NLAND:
            p = seg(t, F_SPLASH + 0.15, F_NLAND)
            if p > 0:
                x = lerp(GX, 380, p)
                y = lerp(WATER - 400, GROUND - 40 - 82, p) - 650 * math.sin(math.pi * p)
                NF.append(bloop(ctx, x, y, NR, "joy", rot=720 * p))
        NF.append(impact(GX, WATER - 40, seg(t, F_SPLASH, F_SPLASH + 0.35), "#e8fbff"))

    # glasses + cup flights
    if 24.25 <= t < 26.4:
        p = seg(t, 24.25, 26.4)
        x = lerp(GX, 380, p)
        y = lerp(WATER - 190, GROUND - 40 - 82 - 10, p) - 700 * math.sin(math.pi * p)
        NF.append(glasses_sprite(x, y, 720 * p, 0.6))
    if F_SPLASH <= t < 26.5:
        p = seg(t, F_SPLASH, 26.5)
        x = lerp(GX + 160, 380 + 120, p)
        y = lerp(WATER - 180, GROUND - 40 - 110, p) - 760 * math.sin(math.pi * p)
        NF.append(cup(x, y, 900 * p, 1))

    # ---------------- draw order
    L += N
    # underwater layer clipped
    if UW:
        ctx.defs.append(f'<clipPath id="uwc"><rect x="{POOL_X0+26}" y="{WATER-60}" width="{POOL_X1-POOL_X0-52}" height="{POOL_BOT-WATER+60}"/></clipPath>')
        L.append(f'<g clip-path="url(#uwc)">' + "".join(UW) + '</g>')
        L.append(f'<path d="M{POOL_X0+26} {WATER} ' + " ".join(f"L{x} {WATER + 7*math.sin(x/45 + t*3.5):.1f}" for x in range(POOL_X0 + 26, POOL_X1 - 25, 16)) +
                 f' L{POOL_X1-26} {POOL_BOT} L{POOL_X0+26} {POOL_BOT}Z" fill="#3aa0e0" opacity="0.28"/>')
    # ring
    if t < F_SPLASH or t >= F_SPLASH:
        rx, ry, rs, rr = ring_xy
        if not (F_SPLASH <= t < F_SPLASH + 0.12):
            L.append(ring2(rx, ry, rs, rr))
    # nibbo sitting in ring (after landing)
    if t >= F_NLAND:
        k = t - F_NLAND
        sq = max(0, 1 - k / 0.25)
        sx_, sy_ = 380, GROUND - 40 - 82 + 6 * math.sin(t * 2)
        ex = "joy" if t < 26.4 else "cool"
        L.append(bloop(ctx, sx_, sy_ + 20 * sq, NR, ex, sx=1 + 0.2 * sq, sy=1 - 0.2 * sq))
        if t >= 26.5:
            s2 = math.sin(seg(t, 28.75, 29.6) * math.pi) if t >= 28.75 else 0
            L.append(f'<path d="M{sx_+100:.0f} {sy_+30:.0f} Q {sx_+150:.0f} {sy_+20:.0f} {sx_+140 - 50*s2:.0f} {sy_-10 + 20*s2:.0f}" fill="none" stroke="#3d2a12" stroke-width="10" stroke-linecap="round"/>')
            L.append(cup(sx_ + 140 - 60 * s2, sy_ - 40 + 30 * s2, -20 * s2, 1 - 0.5 * seg(t, 28.9, 29.6), 0.9))
        L.append(drip_drops(sx_, sy_ - 40, t, 3, 140) if t < 27.5 else "")
    # grumpo
    if umb:
        L.append(umbrella(umb[0], umb[1], umb[2], umb[3]))
    L.append(grumpo(ctx, gt["x"], gt["y"], GS, gt["expr"], gt["red"], gt["glasses"], gt["look"], gt["rot"], gt["sx"], gt["sy"],
                    gt["drink"], gt["sip"], None, gt["steam"], t))
    if t >= F_GLAND:
        L.append(drip_drops(gt["x"], gt["y"] - 30, t, 6, 200))
        L.append(f'<ellipse cx="{GX}" cy="{POOL_BOT-8}" rx="{170*seg(t, F_GLAND, F_GLAND+0.4):.0f}" ry="14" fill="#5cc4f2" stroke="#2a86cf" stroke-width="4" opacity="0.9"/>')
    L.append(pour_svg)
    if umb and G3_UMB_HIT <= t < G3_UMB_HIT + 0.3:
        L.append(impact(umb[0], umb[1] - 120, seg(t, G3_UMB_HIT, G3_UMB_HIT + 0.3)))
    L.append(symbol(GX, 900, "!", seg(t, G2_SWIM1, G2_SWIM1 + 0.6)))
    L.append(symbol(GX, 900, "!", seg(t, 17.2, 17.8)))
    L.append(symbol(GX, 880, "!", seg(t, 23.85, 24.5)))
    L += NF

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<defs>{DEFS2}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g></svg>')


# ------------------------------------------------------------ sound
def build_sfx():
    sfx(0.45, "pop"); sfx(0.5, "ding", 0.5)
    sfx(0.9, "slurp", 0.8)
    sfx(1.55, "squeak", 0.6)
    sfx(2.15, "zip", 0.4, 1.3)
    sfx(G1_START, "boing", 0.7, 1.1); sfx(G1_START + 0.35, "boing", 0.7, 1.25); sfx(G1_START + 0.7, "boing", 0.8, 0.9)
    sfx(3.0, "suspense", 0.6)
    sfx(3.75, "slide_up", 0.6, 1.2)
    sfx(G1_HIT, "bonk", 1.1); sfx(G1_HIT + 0.02, "slide_up", 0.7, 1.1)
    sfx(G1_HIT + 0.5, "plop", 0.7, 0.7)
    sfx(4.85, "ding", 0.8, 1.5)
    sfx(5.6, "slurp", 0.8)
    sfx(G1_RETURN, "slide_down", 0.8)
    sfx(G1_CRASH, "crash_bush", 1.0); sfx(G1_CRASH + 0.02, "thud", 0.8)
    sfx(7.75, "squeak", 0.5, 0.9)
    for k in range(8):
        sfx(G2_WALK0 + k * 0.11, "tiptoe", 0.55, 1.0 + 0.1 * (k % 2))
    sfx(8.9, "click", 0.8); sfx(8.92, "cool", 0.5)
    sfx(G2_DIVE, "hop", 0.6); sfx(G2_DIVE + 0.3, "splash_small", 0.9)
    sfx(G2_DIVE + 0.4, "sneak", 0.6)
    sfx(10.2, "bubbles", 0.6)
    sfx(G2_SWIM1, "alert", 0.7)
    sfx(G2_POUR0 + 0.15, "pour", 0.9)
    sfx(G2_POUR1, "gulp", 0.9, 0.8)
    sfx(G2_LAUNCH, "splash_small", 1.0, 0.9); sfx(G2_LAUNCH + 0.02, "spit", 0.9)
    sfx(G2_LAUNCH + 0.05, "slide_up", 0.6, 0.9)
    sfx(13.0, "laugh", 0.8)
    a, b, c = G2_G / 2, G2_V[1], G2_P0[1] - NG
    tl = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
    sfx(G2_LAUNCH + tl, "thud", 1.0)
    sfx(14.9, "hop", 0.4, 1.3)
    sfx(G3_DRAG0, "drag", 0.8)
    sfx(G3_DRAG1 + 0.1, "hop", 0.5)
    for i, b in enumerate(G3_BOUNCES):
        sfx(b, "boing", 0.8 + 0.1 * i, 1.0 - 0.12 * i)
    sfx(17.2, "alert", 0.7, 0.9)
    sfx(G3_UMB0, "umbrella", 1.0)
    sfx(G3_UMB_HIT, "boing", 1.0, 0.7)
    sfx(G3_UMB_HIT + 0.05, "whoosh", 0.7)
    sfx(G3_SIGN_HIT, "splat", 1.0, 1.3); sfx(G3_SIGN_HIT + 0.01, "clank", 0.8, 0.8)
    sfx(G3_SIGN_HIT + 0.3, "squeak_slide", 0.8)
    sfx(G3_SLIDE1, "thud", 0.8, 1.2)
    sfx(19.6, "laugh", 0.8)
    sfx(20.95, "ding", 0.8, 1.2)
    sfx(F_DASH, "zip", 0.9, 0.8)
    sfx(21.5, "whoosh", 0.6, 0.7)
    for k in range(10):
        sfx(F_CLIMB0 + k * 0.08, "tiptoe", 0.5, 1.2 + 0.05 * k)
    sfx(23.4, "boing", 0.6, 1.4); sfx(23.55, "boing", 0.6, 1.5)
    sfx(F_JUMP, "slide_up", 0.7, 0.8)
    sfx(23.85, "alert", 0.8, 0.85); sfx(23.9, "gasp", 0.8)
    sfx(24.1, "slide_down", 0.9)
    sfx(F_SPLASH, "splash", 1.4); sfx(F_SPLASH + 0.02, "thud", 0.9, 0.6)
    sfx(F_SPLASH + 0.6, "splash", 0.5, 1.3)
    sfx(F_RLAND, "boing", 0.6, 1.3)
    sfx(F_GLAND, "thud", 1.2, 0.8); sfx(F_GLAND + 0.05, "splash_small", 0.6, 1.2)
    sfx(F_NLAND, "boing", 0.7, 1.5)
    sfx(26.4, "click", 0.8); sfx(26.42, "cool", 0.6)
    sfx(26.6, "grumble", 1.0)
    sfx(26.95, "zoom", 0.7)
    sfx(27.2, "steam", 0.9)
    sfx(28.2, "zoom", 0.5, 1.3)
    sfx(28.75, "slurp", 0.9)


if __name__ == "__main__":
    build_sfx()
    json.dump(EV, open(sys.argv[1] if len(sys.argv) > 1 else "events_v2.json", "w"))
    print(len(EV), "events")
