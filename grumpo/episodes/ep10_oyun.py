"""Grumpo & Nibbo — Episode 10: Grumpo Just Wants to Play (living room, 4 blocked tries, 60 fps).

Grumpo slams the new game in and hits PLAY. Nibbo keeps blocking him, each trick bigger:
TRY 1  Nibbo flicks the TV off/on with a remote from behind the couch -> Grumpo yanks the remote.
TRY 2  Nibbo jumps in front of the TV holding his drawing -> Grumpo's cushion throw knocks him away.
TRY 3  Nibbo tugs the controller cable -> tug of war, Grumpo yanks, Nibbo flies off screen.
TRY 4  "No disc!" Nibbo has it -> Grumpo shakes him upside down, the disc (and junk) falls out.
Final: Grumpo finally plays ... sees sad Nibbo, sighs, tosses him the 2nd controller: split screen, both play.
(No game logos/characters — generic sunset/palm title screen and two little cars.)
"""
import math, random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit"))
from chars2 import *
from env2 import OL, DEFS2, shadow
from hook import overlay, hook_title, counter
import ep10_bekleyis as B

W, H, FPS, DUR = 1080, 1920, 60, 22.0
FLOOR = B.FLOOR
NR, GS, GR = 112, 0.92, 120
NG = FLOOR - NR
GX, GY = 830, 1430          # seat
GYF = FLOOR - GR             # grumpo on floor
CONSOLE = B.CONSOLE
TVX, TVY, TVW, TVH = B.TV

EV = []


def sfx(t, name, gain=1.0, pitch=1.0):
    EV.append({"t": round(t, 3), "name": name, "gain": gain, "pitch": pitch})


cl, seg, eio, eout, ein, eback, arm = B.cl, B.seg, B.eio, B.eout, B.ein, B.eback, B.arm

# ---------------------------------------------------------------- timeline
T_SLAM = 0.75
T_TVON = 0.95
T_SIT0, T_SIT1 = 1.05, 1.5
TRY = [1.7, 5.0, 8.6, 12.6]
T_GAMEON = 16.4
# try 1
FLICK = [2.05, 2.5, 2.7, 2.9, 3.05, 3.2, 3.35]          # alternating off/on, starts with OFF
T_SPOT = 3.75
T_YANK0, T_YANK1 = 4.0, 4.35
T_NDUCK = 4.6
T_TV1 = 4.5
# try 2
T_START2 = 5.15
T_NJUMP0, T_NJUMP1 = 5.35, 5.85
T_CUSH0, T_CUSH1 = 6.75, 7.15
T_KNOCK1 = 7.75
# try 3
T_TUG0 = 9.1
T_GRAB = 9.9
T_YANKBACK = 11.3
T_NFLY1 = 11.95
T_BACKSEAT = 12.35
# try 4
T_NODISC = 12.9
T_CHASE0, T_CHASE1 = 13.5, 14.2
T_SHAKE0, T_SHAKE1 = 14.4, 15.4
T_INSERT = 15.9
# final
T_SAD = 16.7
T_PULL2 = 17.35
T_TOSS0, T_TOSS1 = 17.6, 18.05
T_SITN = 18.4

KNOCK_X = -260


def tv_mode(t):
    if t < T_TVON:
        return "off"
    if t < TRY[1]:
        if t >= FLICK[0] and t < T_TV1:
            k = sum(1 for f in FLICK if t >= f)
            return "off" if k % 2 == 1 else "title"
        return "title"
    if t < T_START2:
        return "title"
    if t < TRY[3]:
        return "game"
    if t < T_INSERT:
        return "nodisc" if t >= T_NODISC else "game"
    if t < T_GAMEON:
        return "title"
    if t < T_TOSS1:
        return "game"
    return "split"


# ---------------------------------------------------------------- props
def car(x, y, col, s=1.0, rot=0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<rect x="-30" y="-14" width="60" height="22" rx="8" fill="{col}" stroke="{OL}" stroke-width="4"/>'
            f'<path d="M-16 -14 Q -10 -30 8 -30 Q 20 -30 24 -14Z" fill="{col}" stroke="{OL}" stroke-width="4"/>'
            '<path d="M-8 -16 Q -4 -26 6 -26 Q 14 -26 17 -16Z" fill="#bfe6ff"/>'
            f'<circle cx="-16" cy="10" r="8" fill="#2b2b33" stroke="{OL}" stroke-width="3"/><circle cx="16" cy="10" r="8" fill="#2b2b33" stroke="{OL}" stroke-width="3"/></g>')


def road_view(x, y, w, h, t, cars):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#tvsun)"/>',
         f'<circle cx="{x+w*0.7:.1f}" cy="{y+h*0.38:.1f}" r="{h*0.13:.1f}" fill="#ffe36a"/>',
         f'<path d="M{x} {y+h*0.62:.1f} H{x+w} V{y+h} H{x}Z" fill="#3a3a4c"/>']
    for k in range(6):
        px = x + ((k * w / 5 - t * 260) % (w + 60)) - 30
        if x <= px <= x + w - 30:
            o.append(f'<rect x="{px:.1f}" y="{y+h*0.8:.1f}" width="30" height="6" fill="#ffe36a"/>')
    # palms passing
    for k in range(3):
        px = x + ((k * w / 2.2 - t * 120) % (w + 80)) - 40
        if x + 8 <= px <= x + w - 8:
            o.append(f'<path d="M{px:.1f} {y+h*0.62:.1f} Q {px+2:.1f} {y+h*0.4:.1f} {px+8:.1f} {y+h*0.3:.1f}" stroke="#2a1450" stroke-width="5" fill="none"/>'
                     f'<path d="M{px+8:.1f} {y+h*0.3:.1f} q-16 -2 -22 8 M{px+8:.1f} {y+h*0.3:.1f} q8 -12 20 -8 M{px+8:.1f} {y+h*0.3:.1f} q14 2 16 12" stroke="#2a1450" stroke-width="6" fill="none" stroke-linecap="round"/>')
    for (cx, col) in cars:
        bob = 2 * math.sin(t * 20 + cx)
        o.append(car(x + cx * w, y + h * 0.74 + bob, col, h / 220))
    return "".join(o)


def tv(t):
    x, y, w, h = TVX, TVY, TVW, TVH
    mode = tv_mode(t)
    o = [f'<rect x="{x+w/2-50}" y="{y+h}" width="100" height="14" fill="#2b2b33" stroke="{OL}" stroke-width="5"/>',
         f'<rect x="{x-14}" y="{y-14}" width="{w+28}" height="{h+28}" rx="18" fill="#2b2b33" stroke="{OL}" stroke-width="7"/>']
    if mode == "off":
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#0c0c12"/>')
    elif mode == "title":
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="url(#tvsun)"/>'
                 f'<circle cx="{x+w*0.68:.1f}" cy="{y+110}" r="44" fill="#ffe36a"/>'
                 f'<path d="M{x} {y+200} Q {x+w/2} {y+175} {x+w} {y+200} V{y+h} H{x}Z" fill="#2a1450"/>'
                 f'<path d="M{x+70} {y+210} Q {x+74} {y+140} {x+92} {y+96}" stroke="#2a1450" stroke-width="8" fill="none"/>'
                 f'<path d="M{x+92} {y+96} q-36 -6 -48 12 M{x+92} {y+96} q-26 -24 -52 -10 M{x+92} {y+96} q14 -26 42 -20 M{x+92} {y+96} q32 -2 38 22" stroke="#2a1450" stroke-width="10" fill="none" stroke-linecap="round"/>')
        pulse = 1 + 0.12 * math.sin(t * 9)
        o.append(f'<g transform="translate({x+w/2:.1f} {y+h-62}) scale({pulse:.3f})"><circle r="34" fill="#ffffff" stroke="{OL}" stroke-width="5"/>'
                 '<path d="M-10 -16 L18 0 L-10 16Z" fill="#e8454a"/></g>')
    elif mode == "game":
        o.append(f'<g clip-path="url(#tvclip)">{road_view(x, y, w, h, t, [(0.35, "#9466e0")])}</g>')
    elif mode == "split":
        o.append(f'<g clip-path="url(#tvclip)">{road_view(x, y, w, h/2, t, [(0.4, "#9466e0")])}'
                 f'{road_view(x, y + h/2, w, h/2, t * 1.1, [(0.55, "#ffd23c")])}</g>'
                 f'<line x1="{x}" y1="{y+h/2}" x2="{x+w}" y2="{y+h/2}" stroke="#ffffff" stroke-width="5"/>')
    elif mode == "nodisc":
        blink = 0.6 + 0.4 * math.sin(t * 14)
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#14141e"/>'
                 f'<g transform="translate({x+w/2:.1f} {y+h/2:.1f})" opacity="{blink:.2f}"><circle r="70" fill="#c9ccd6" stroke="#ffffff" stroke-width="6"/>'
                 '<circle r="16" fill="#14141e"/><path d="M-80 -80 L80 80" stroke="#e8303a" stroke-width="16" stroke-linecap="round"/></g>')
    o.append(f'<path d="M{x+16} {y+16} L{x+80} {y+16} L{x+16} {y+80}Z" fill="#ffffff" opacity="0.12"/>')
    return "".join(o)


TV_DEF = f'<clipPath id="tvclip"><rect x="{TVX}" y="{TVY}" width="{TVW}" height="{TVH}" rx="6"/></clipPath>'


def remote(x, y, rot=0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<rect x="-16" y="-44" width="32" height="88" rx="10" fill="#2b2b33" stroke="{OL}" stroke-width="4"/>'
            '<circle cx="0" cy="-28" r="7" fill="#e8303a"/><rect x="-9" y="-10" width="7" height="7" rx="2" fill="#c9ccd6"/>'
            '<rect x="2" y="-10" width="7" height="7" rx="2" fill="#c9ccd6"/><rect x="-9" y="4" width="7" height="7" rx="2" fill="#c9ccd6"/>'
            '<rect x="2" y="4" width="7" height="7" rx="2" fill="#c9ccd6"/></g>')


def drawing(x, y, rot=0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<rect x="-150" y="-110" width="300" height="220" rx="8" fill="#ffffff" stroke="{OL}" stroke-width="6"/>'
            '<path d="M-40 -10 C -40 -60 30 -60 30 -10 C 30 -60 100 -60 100 -10 C 100 30 30 70 30 80 C 30 70 -40 30 -40 -10Z" fill="#ff5f6e" stroke="#c8303a" stroke-width="5"/>'
            '<circle cx="-90" cy="20" r="44" fill="#ffd23c" stroke="#3d2a12" stroke-width="5"/>'
            '<circle cx="-104" cy="10" r="6" fill="#3d2a12"/><circle cx="-76" cy="10" r="6" fill="#3d2a12"/>'
            '<path d="M-108 34 Q -90 50 -72 34" stroke="#3d2a12" stroke-width="5" fill="none" stroke-linecap="round"/>'
            '<path d="M-130 -80 l12 12 M-118 -80 l-12 12 M110 70 l14 -6 M60 -90 l6 14" stroke="#3a7ad6" stroke-width="5" stroke-linecap="round"/></g>')


def cushion(x, y, rot=0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<path d="M-62 -44 Q 0 -56 62 -44 Q 74 0 62 44 Q 0 56 -62 44 Q -74 0 -62 -44Z" fill="#ff8fb4" stroke="{OL}" stroke-width="6"/>'
            '<circle r="7" fill="#e86a94"/><path d="M-40 -30 Q 0 -36 30 -30" stroke="#ffc2d6" stroke-width="7" fill="none" stroke-linecap="round"/></g>')


def disc(x, y, rot=0, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.2f})">'
            f'<circle r="44" fill="#dfe5ec" stroke="{OL}" stroke-width="5"/>'
            '<path d="M-30 -20 A36 36 0 0 1 10 -34" stroke="#ffffff" stroke-width="8" fill="none"/>'
            '<path d="M20 28 A36 36 0 0 1 -14 36" stroke="#ff9ad0" stroke-width="6" fill="none"/>'
            f'<circle r="12" fill="#efe1f6" stroke="{OL}" stroke-width="4"/></g>')


def junk(kind, x, y, rot):
    if kind == "disc":
        return disc(x, y, rot, 0.9)
    if kind == "cookie":
        return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})"><circle r="26" fill="#d9a066" stroke="{OL}" stroke-width="4"/>'
                '<circle cx="-8" cy="-6" r="4" fill="#5a2a12"/><circle cx="9" cy="3" r="4" fill="#5a2a12"/><circle cx="-2" cy="11" r="3" fill="#5a2a12"/></g>')
    if kind == "sock":
        return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})"><path d="M-12 -30 H12 V10 Q 12 26 28 26 Q 34 36 20 38 H-6 Q -12 30 -12 10Z" fill="#4ac0ff" stroke="{OL}" stroke-width="4"/>'
                '<path d="M-12 -22 H12" stroke="#ffffff" stroke-width="6"/></g>')
    if kind == "duck":
        return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})"><ellipse cx="0" cy="6" rx="28" ry="18" fill="#ffd23c" stroke="{OL}" stroke-width="4"/>'
                f'<circle cx="-14" cy="-12" r="14" fill="#ffd23c" stroke="{OL}" stroke-width="4"/><path d="M-30 -12 l-12 4 l12 4z" fill="#ff9a2a" stroke="{OL}" stroke-width="3"/>'
                '<circle cx="-16" cy="-15" r="3" fill="#221c2e"/></g>')
    return ""


JUNK = [("cookie", 0.0, -90, 40), ("sock", 0.12, 70, 60), ("duck", 0.24, -40, 90), ("disc", 0.4, 20, 0)]


def cable(x0, y0, x1, y1, sag=60, taut=0.0, wob=0.0):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + sag * (1 - taut) + wob
    return (f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="{OL}" stroke-width="10" stroke-linecap="round"/>'
            f'<path d="M{x0:.1f} {y0:.1f} Q {mx:.1f} {my:.1f} {x1:.1f} {y1:.1f}" fill="none" stroke="#2b2b33" stroke-width="5" stroke-linecap="round"/>')


# ---------------------------------------------------------------- camera
CK = [(0.0, (560, 1420, 1.95)), (0.9, (560, 1420, 1.95)), (1.4, (610, 1320, 1.55)),
      (3.6, (640, 1320, 1.55)), (3.8, (760, 1380, 1.75)), (4.4, (760, 1380, 1.75)), (4.8, (600, 1320, 1.55)), (5.4, (570, 1330, 1.55)), (7.9, (570, 1330, 1.55)),
      (8.6, (600, 1320, 1.55)), (9.3, (560, 1340, 1.5)), (12.2, (560, 1340, 1.5)), (12.6, (600, 1320, 1.55)),
      (12.9, (460, 1320, 1.7)), (13.3, (640, 1320, 1.55)), (16.0, (640, 1320, 1.55)), (16.6, (600, 1320, 1.55)), (17.0, (760, 1380, 1.7)),
      (17.8, (760, 1380, 1.7)), (18.3, (650, 1320, 1.36)), (DUR, (650, 1330, 1.4))]
SHAKES = [(T_SLAM, 10, 0.25), (T_YANK1, 6, 0.2), (T_KNOCK1 - 0.55, 12, 0.3), (T_YANKBACK, 12, 0.3), (T_NFLY1, 16, 0.35),
          (T_SHAKE0, 6, 1.0), (T_INSERT, 6, 0.2)]


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
def g_state(t):
    g = dict(x=GX, y=GY, ex="smug", look=(-1, -0.1), rot=0, sx=1, sy=1, red=0.0, layer="couch",
             hold="pad", seated=True)
    if t < T_SIT0:
        g.update(x=560, y=GYF, layer="front", seated=False, hold="case" if t < T_SLAM else "none", look=(-1, 0.3))
        if t < T_SLAM:
            k = seg(t, 0.35, T_SLAM)
            g["sy"], g["sx"] = 1 + 0.08 * math.sin(math.pi * k), 1 - 0.05 * math.sin(math.pi * k)
    elif t < T_SIT1:
        p = seg(t, T_SIT0, T_SIT1)
        g.update(x=lerp(560, GX, p), y=lerp(GYF, GY, p) - 200 * math.sin(math.pi * p), layer="front",
                 rot=-30 * math.sin(math.pi * p), hold="none")
    elif t < TRY[1]:
        if FLICK[0] <= t < T_SPOT:
            g["ex"] = "angry" if t > 2.6 else "suspicious"
            g["red"] = 0.35 * seg(t, 2.8, 3.4)
            g["sx"] = 1 + 0.02 * math.sin(t * 40) * (t > 2.8)
        if T_SPOT <= t < T_YANK0:
            g["ex"], g["look"], g["red"] = "angry", (1, 0.1), 0.35
        if T_YANK0 <= t < T_YANK1:
            g["ex"], g["look"], g["red"] = "angry", (1, 0.1), 0.35 * (1 - seg(t, T_YANK0, T_YANK1))
            g["hold"] = "yank"
        if t >= T_YANK1:
            g["ex"], g["look"], g["hold"] = "smug", (-1, -0.1), "pad+remote"
    elif t < TRY[2]:
        g["hold"] = "pad"
        if T_NJUMP1 <= t < T_CUSH0:
            g["ex"], g["look"] = "angry", (-1, -0.2)
            g["red"] = 0.4 * seg(t, 5.9, 6.4)
        if T_CUSH0 - 0.3 <= t < T_CUSH1:
            g["hold"] = "throw"
            g["ex"] = "angry"
            g["red"] = 0.4 * (1 - seg(t, T_CUSH0, T_CUSH1))
            g["rot"] = -12 * math.sin(math.pi * seg(t, T_CUSH0 - 0.3, T_CUSH1))
        if t >= T_KNOCK1 - 0.4:
            g["ex"] = "smug"
    elif t < TRY[3]:
        if t < T_TUG0 + 0.25:
            g["hold"] = "pad"
        elif t < T_GRAB:
            p = seg(t, T_TUG0 + 0.3, T_GRAB)
            g.update(ex="shock" if t < 9.5 else "angry", look=(-1, 0.1), hold="none",
                     x=lerp(GX, 640, eio(p)), y=lerp(GY, GYF, p) - 160 * math.sin(math.pi * p), layer="front",
                     seated=False)
        elif t < T_YANKBACK:
            k = t - T_GRAB
            g.update(x=640 + 18 * math.sin(k * 9), y=GYF, layer="front", seated=False, ex="angry", look=(-1, 0.1),
                     hold="tug", red=0.3, rot=8 * math.sin(k * 9))
            g["sx"] = 1 + 0.04 * math.sin(k * 18)
        elif t < T_BACKSEAT:
            p = seg(t, T_YANKBACK + 0.4, T_BACKSEAT)
            g.update(layer="front", seated=False, hold="pad", ex="smug", look=(-1, -0.1),
                     x=lerp(700, GX, eio(p)), y=lerp(GYF, GY, p) - 120 * math.sin(math.pi * p))
            if t < T_YANKBACK + 0.4:
                g.update(x=700, y=GYF, rot=14 * math.sin(math.pi * seg(t, T_YANKBACK, T_YANKBACK + 0.4)))
        else:
            g["hold"] = "pad"
    elif t < T_GAMEON:
        g["hold"] = "pad"
        if T_NODISC <= t < T_CHASE0:
            g["ex"], g["look"] = ("shock", (-1, -0.2)) if t < 13.25 else ("angry", (1, 0.1))
        elif T_CHASE0 <= t < T_SHAKE0:
            p = seg(t, T_CHASE0, T_CHASE1)
            g.update(layer="front", seated=False, ex="angry", look=(1, 0), hold="none",
                     x=lerp(GX, 680, eio(p)), y=lerp(GY, GYF, p) - 150 * math.sin(math.pi * p))
        elif t < T_SHAKE1 + 0.2:
            g.update(layer="front", seated=False, x=680, y=GYF, ex="angry", look=(1, -0.6), hold="shake",
                     red=0.25)
            g["y"] += 8 * math.sin(t * 40) * (t < T_SHAKE1)
        elif t < T_INSERT:
            p = seg(t, T_SHAKE1 + 0.2, T_INSERT)
            g.update(layer="front", seated=False, ex="smug", look=(-1, 0.4), hold="disc",
                     x=lerp(680, 520, eio(p)), y=GYF - 90 * math.sin(math.pi * p))
        else:
            p = seg(t, T_INSERT, T_GAMEON)
            g.update(layer="front", seated=False, ex="smug", look=(-1, -0.1), hold="none",
                     x=lerp(520, GX, eio(p)), y=lerp(GYF, GY, p) - 140 * math.sin(math.pi * p))
    else:
        g["hold"] = "pad"
        if t < T_SAD:
            g["ex"] = "smug"
        elif t < T_PULL2:
            g["ex"], g["look"] = ("grumpy", (1, 0.4)) if t > 16.95 else ("smug", (-1, 0))
        elif t < T_TOSS1:
            g["ex"], g["look"], g["hold"] = "smug", (1, 0.4), "toss"
        else:
            g["ex"], g["look"] = "smug", (-1, -0.1)
            g["x"] = lerp(GX, 750, eio(seg(t, T_TOSS1, T_SITN)))
            g["y"] = GY - abs(math.sin(t * 8)) * 6
    return g


def n_state(t):
    n = dict(x=1300, y=NG, ex="happy", rot=0, sx=1, sy=1, vis=False, layer="front", hold=None)
    if t < 1.9:
        return n
    if t < T_NDUCK + 0.3:
        # peeking from behind the couch's right arm with the remote
        up = eout(seg(t, 1.9, 2.1)) * (1 - seg(t, T_NDUCK, T_NDUCK + 0.3))
        n.update(vis=True, layer="behind", x=1015, y=lerp(1600, 1380, up), hold="remote" if t < T_YANK0 + 0.1 else None)
        n["ex"] = "happy" if t < T_SPOT else ("uhoh" if t < T_YANK1 else "wow")
        n["rot"] = -10 * up
        return n
    if t < T_NJUMP0:
        return n
    if t < T_KNOCK1:
        if t < T_NJUMP1:
            p = seg(t, T_NJUMP0, T_NJUMP1)
            n.update(vis=True, x=lerp(1150, 400, p), y=lerp(NG, NG - 40, p) - 380 * math.sin(math.pi * p),
                     rot=-360 * p, ex="joy", hold="drawing")
        elif t < T_CUSH1:
            n.update(vis=True, x=400, y=NG - 40 + 8 * math.sin(t * 9), ex="joy", hold="drawing")
        else:
            p = seg(t, T_CUSH1, T_KNOCK1)
            n.update(vis=True, x=lerp(400, KNOCK_X, p), y=NG - 40 - 300 * math.sin(math.pi * p), rot=-540 * p,
                     ex="dizzy", hold=None, sx=1.15 - 0.15 * p, sy=0.85 + 0.15 * p)
        return n
    if t < T_TUG0 - 0.4:
        return n
    if t < T_YANKBACK:
        # tugging the cable from the left side (behind cabinet edge)
        p = eout(seg(t, T_TUG0 - 0.4, T_TUG0))
        k = max(0, t - T_GRAB)
        n.update(vis=True, x=lerp(-120, 300, p) - 14 * math.sin(k * 9), y=NG, ex="joy" if t < T_GRAB else "nervous",
                 hold="cable", rot=-10 * math.sin(k * 9))
        n["sx"] = 1 + 0.05 * math.sin(k * 18)
        return n
    if t < T_NFLY1 + 0.1:
        p = seg(t, T_YANKBACK, T_NFLY1)
        n.update(vis=True, x=lerp(300, 1300, p), y=NG - 520 * math.sin(math.pi * p), rot=720 * p, ex="dizzy",
                 hold=None)
        return n
    if t < T_NODISC + 0.3:
        return n
    if t < T_CHASE1:
        p = eout(seg(t, T_NODISC + 0.3, 13.4))
        n.update(vis=True, x=lerp(1150, 860, p), y=NG - abs(math.sin(t * 10)) * 14, ex="joy", hold="disc")
        return n
    if t < T_SHAKE1 + 0.2:
        # upside down, held by grumpo, shaken
        n.update(vis=True, x=860, y=NG - 160 + 26 * math.sin(t * 40) * (t < T_SHAKE1), rot=180, ex="dizzy", hold=None)
        if t < T_SHAKE0:
            p = seg(t, T_CHASE1, T_SHAKE0)
            n.update(y=lerp(NG, NG - 160, p), rot=180 * eio(p), ex="uhoh")
        return n
    if t < T_SAD:
        p = seg(t, T_SHAKE1 + 0.2, T_SHAKE1 + 0.55)
        n.update(vis=True, x=860, y=lerp(NG - 160, NG, ein(p)), rot=lerp(180, 360, p) % 360, ex="dizzy")
        if t > T_SHAKE1 + 0.55:
            k = t - T_SHAKE1 - 0.55
            if k < 0.2:
                q = math.sin(math.pi * k / 0.2)
                n["sx"], n["sy"] = 1 + 0.2 * q, 1 - 0.2 * q
        return n
    if t < T_TOSS1:
        n.update(vis=True, x=lerp(860, 950, eio(seg(t, T_GAMEON, T_SAD))), y=NG, ex="nervous", hold="catch" if t > T_TOSS0 else None)
        n["sy"] = 1 - 0.04 * math.sin(t * 7)
        if t > T_TOSS1 - 0.1:
            n["ex"] = "joy"
        return n
    if t < T_SITN:
        p = seg(t, T_TOSS1, T_SITN)
        n.update(vis=True, x=lerp(950, 960, p), y=lerp(NG, 1430, p) - 120 * math.sin(math.pi * p), ex="joy",
                 hold="pad", layer="couch")
        return n
    n.update(vis=True, x=960, y=1430 - abs(math.sin(t * 9 + 1)) * 8, ex="joy", hold="pad", layer="couch")
    return n


def g_hands(g, t):
    x, y = g["x"], g["y"]
    col = "#4a2a7a"
    h = g["hold"]
    o = []
    if h in ("pad", "pad+remote", "toss"):
        px, py = x - 70, y + 70
        o.append(arm(x - 100, y + 20, px - 30, py, col) + arm(x - 40, y + 60, px + 30, py, col, sag=10) + B.pad(px, py, -8, 0.95))
        if h == "pad+remote":
            o.append(remote(x + 110, y + 70, 70, 0.9))
        if h == "toss":
            p = seg(t, T_TOSS0, T_TOSS1)
            if t < T_TOSS0:
                q = seg(t, T_PULL2, T_TOSS0)
                o.append(arm(x + 60, y, x + 120, y - 60 * q, col) + B.pad(x + 130, y - 60 * q, 0, 0.9))
            elif p < 1:
                o.append(B.pad(lerp(x + 130, 840, p), lerp(y - 60, NG - 30, p) - 160 * math.sin(math.pi * p), 540 * p, 0.9))
    elif h == "case":
        o.append(arm(x - 90, y, x - 150, y - 40, col) + B.case_svg(x - 165, y - 60, -10, 0.8))
    elif h == "yank":
        p = seg(t, T_YANK0, T_YANK1)
        rx = lerp(1000, x + 110, eio(p))
        ry = lerp(1400, y + 70, eio(p))
        o.append(arm(x + 90, y, rx, ry, col, w=12, sag=-20 * (1 - p)) + remote(rx, ry, 70 * p, 0.9))
        o.append(arm(x - 100, y + 20, x - 100, y + 70, col) + B.pad(x - 70, y + 70, -8, 0.95))
    elif h == "throw":
        p = seg(t, T_CUSH0 - 0.3, T_CUSH0)
        o.append(arm(x - 60, y - 40, x - 60 - 40 * p, y - 140 + 40 * p, col, sag=-10))
        if t < T_CUSH0:
            o.append(cushion(x - 80 - 40 * p, y - 160 + 40 * p, -20, 0.9))
    elif h == "tug":
        px, py = x - 150, y + 10
        o.append(arm(x - 90, y, px + 20, py, col) + arm(x - 60, y + 40, px + 30, py + 10, col, sag=10) + B.pad(px, py, -20, 0.95))
    elif h == "shake":
        o.append(arm(x + 80, y - 60, 860, NG - 30, col, w=12, sag=-30))
    elif h == "disc":
        o.append(arm(x - 90, y - 10, x - 140, y - 60, col) + disc(x - 160, y - 80, t * 400, 0.9))
    return "".join(o)


def n_hands(n, t):
    x, y = n["x"], n["y"]
    col = "#3d2a12"
    h = n["hold"]
    if h == "remote":
        return arm(x - 70, y + 10, x - 110, y - 20, col) + remote(x - 120, y - 40, -30, 0.85)
    if h == "drawing":
        return arm(x - 80, y + 30, x - 40, y - 40, col) + arm(x + 80, y + 30, x + 40, y - 40, col) + drawing(x, y - 150, 6 * math.sin(t * 5), 0.95)
    if h == "cable":
        return arm(x + 80, y + 10, x + 140, y + 20, col)
    if h == "disc":
        return arm(x - 80, y, x - 130, y - 50, col) + disc(x - 140, y - 80, t * 600, 0.85)
    if h == "catch":
        p = seg(t, T_TOSS1 - 0.08, T_TOSS1)
        return arm(x - 80, y + 10, x - 110, y - 20, col) + (B.pad(x - 110, y - 30, 10, 0.9) if p >= 1 else "")
    if h == "pad":
        px, py = x - 30, y + 70
        return arm(x - 80, y + 20, px - 30, py, col) + arm(x + 40, y + 50, px + 30, py, col, sag=10) + B.pad(px, py, 8, 0.9)
    return ""


# ---------------------------------------------------------------- frame
def frame(t):
    ctx = Ctx()
    L = [B.room(t), B.cabinet(), B.console(t >= T_TVON, t), tv(t), B.socket(True)]
    L.append(B.cord(CONSOLE[0] + 110, CONSOLE[1], B.SOCKET[0], B.SOCKET[1] + 26))
    L.append(B.plug(B.SOCKET[0], B.SOCKET[1] + 6, 0))

    g = g_state(t)
    n = n_state(t)

    # controller cable: console -> grumpo's pad
    pad_pos = None
    if g["hold"] in ("pad", "pad+remote", "toss", "yank"):
        pad_pos = (g["x"] - 70, g["y"] + 70)
    elif g["hold"] == "tug":
        pad_pos = (g["x"] - 150, g["y"] + 10)
    if TRY[2] <= t < T_BACKSEAT + 0.2:
        cx0, cy0 = CONSOLE[0] - 60, CONSOLE[1] + 10
        if t < T_TUG0:
            L.append(cable(cx0, cy0, g["x"] - 70, g["y"] + 70, 90))
        elif t < T_GRAB:
            # pad flies out of grumpo's hands toward nibbo
            p = eout(seg(t, T_TUG0, T_TUG0 + 0.45))
            px = lerp(GX - 70, 440, p)
            py = lerp(GY + 70, FLOOR - 60, p) - 140 * math.sin(math.pi * p)
            L.append(cable(n["x"] + 140, n["y"] + 20, px, py, 40, 0.3))
            L.append(B.pad(px, py, 600 * p, 0.95))
        elif t < T_YANKBACK:
            k = t - T_GRAB
            L.append(cable(n["x"] + 140, n["y"] + 20, g["x"] - 150, g["y"] + 10, 30, 1.0, 10 * math.sin(k * 30)))
    # couch + grumpo seated
    L.append(B.couch_back())
    if n["vis"] and n["layer"] == "behind":
        L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"], rot=n["rot"], sx=n["sx"], sy=n["sy"]))
        L.append(n_hands(n, t))
    if g["layer"] == "couch":
        L.append(shadow(g["x"], 1525, 130))
        L.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"],
                        False, 0, None, 0, t))
        L.append(g_hands(g, t))
    if n["vis"] and n["layer"] == "couch":
        L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"], rot=n["rot"], sx=n["sx"], sy=n["sy"]))
        L.append(n_hands(n, t))
    L.append(B.couch_front())

    # thrown cushion
    if T_CUSH0 <= t < T_KNOCK1 + 0.6:
        p = seg(t, T_CUSH0, T_CUSH1)
        if t < T_CUSH1:
            L.append(cushion(lerp(GX - 120, 470, p), lerp(GY - 120, NG - 220, p) - 120 * math.sin(math.pi * p), -720 * p, 0.9))
        else:
            q = seg(t, T_CUSH1, T_KNOCK1 + 0.6)
            L.append(cushion(lerp(470, 560, q), lerp(NG - 220, FLOOR - 50, ein(q)), 200 * q, 0.9))
    # drawing falling after knock
    if T_CUSH1 <= t < TRY[2] + 1.0:
        q = seg(t, T_CUSH1, T_CUSH1 + 1.2)
        sway = 40 * math.sin(q * 9)
        L.append(drawing(400 + sway, lerp(NG - 190, FLOOR - 20, eio(q)), 20 * math.sin(q * 9) + 80 * q, 0.95 - 0.35 * q))

    # nibbo front
    if n["vis"] and n["layer"] == "front":
        if abs(n["rot"]) < 30 or n["rot"] % 360 < 30:
            L.append(shadow(n["x"], FLOOR + 2, 110))
        L.append(nibbo(ctx, n["x"], n["y"], NR, n["ex"], rot=n["rot"], sx=n["sx"], sy=n["sy"]))
        L.append(n_hands(n, t))
    # grumpo front
    if g["layer"] == "front":
        L.append(shadow(g["x"], FLOOR + 2, 120))
        L.append(grumpo(ctx, g["x"], g["y"], GS, g["ex"], g["red"], "none", g["look"], g["rot"], g["sx"], g["sy"],
                        False, 0, None, 0, t))
        L.append(g_hands(g, t))

    # case slam into console
    if 0.35 <= t < T_SLAM + 0.1 and g["hold"] != "case":
        pass
    if T_SLAM - 0.25 <= t < T_SLAM:
        p = ein(seg(t, T_SLAM - 0.25, T_SLAM))
        L.append(B.case_svg(lerp(395, CONSOLE[0] - 25, p), lerp(1480, CONSOLE[1], p), -90 * p, 0.8 - 0.35 * p))
    # junk falling out of nibbo while shaken
    if T_SHAKE0 + 0.1 <= t < T_INSERT + 0.4:
        for kind, d, vx, rot0 in JUNK:
            t0 = T_SHAKE0 + 0.15 + d * 1.6
            if t < t0:
                continue
            if kind == "disc" and t >= T_SHAKE1 + 0.2:
                continue
            k = t - t0
            fy = min(FLOOR - 30, NG - 230 + 0.5 * 4200 * k * k)
            fx = 860 + vx * min(k, 0.4)
            L.append(junk(kind, fx, fy, rot0 + (300 * k if fy < FLOOR - 30 else 0)))
    if t >= T_INSERT - 0.15 and t < T_INSERT:
        p = seg(t, T_INSERT - 0.15, T_INSERT)
        L.append(disc(lerp(360, CONSOLE[0] - 25, p), lerp(1460, CONSOLE[1], p), 0, 0.9 - 0.4 * p))

    # FX
    L.append(impact(CONSOLE[0] - 20, CONSOLE[1], seg(t, T_SLAM, T_SLAM + 0.25), "#fff6a8"))
    for f in FLICK[:5]:
        if f <= t < f + 0.12:
            L.append(f'<path d="M1000 1360 L{TVX+TVW} {TVY+TVH/2}" stroke="#ff5f6e" stroke-width="5" stroke-dasharray="10 12" opacity="0.6"/>')
    L.append(symbol(GX, GY - 210, "!", seg(t, T_SPOT, T_SPOT + 0.15) * (1 - seg(t, T_YANK0, T_YANK0 + 0.1)), "#e8303a"))
    L.append(impact(420, NG - 150, seg(t, T_CUSH1, T_CUSH1 + 0.3), "#fff6a8"))
    L.append(symbol(640, GYF - 210, "!", seg(t, T_TUG0 + 0.05, T_TUG0 + 0.2) * (1 - seg(t, 9.7, 9.8)), "#e8303a"))
    if T_NFLY1 <= t < T_NFLY1 + 0.4:
        L.append(impact(1000, 1200, seg(t, T_NFLY1, T_NFLY1 + 0.4), "#ffe8a8"))
    L.append(symbol(GX, GY - 210, "?", seg(t, T_NODISC, T_NODISC + 0.15) * (1 - seg(t, 13.25, 13.35)), "#3a7ad6"))
    if T_SHAKE0 <= t < T_SHAKE1:
        L.append(speed_lines(860, NG - 160, 90, 0.7))
        L.append(speed_lines(860, NG - 160, 270, 0.7))
    L.append(impact(CONSOLE[0] - 20, CONSOLE[1], seg(t, T_INSERT, T_INSERT + 0.25), "#fff6a8"))
    if t >= T_TOSS1:
        for k in range(5):
            a = t * 2 + k * 1.26
            L.append(star_twinkle(860 + 260 * math.cos(a), 1230 + 60 * math.sin(a), 0.55 + 0.3 * math.sin(t * 6 + k)))
    if T_SAD <= t < T_PULL2:
        L.append(f'<path d="M{922} {NG+8} q-6 14 0 22 q6 -8 0 -22z" fill="#9adfff" stroke="#3a6a8a" stroke-width="2"/>')

    cx, cy, z = camera(t)
    tr = f"translate(540 960) scale({z:.4f}) translate({-cx:.1f} {-cy:.1f})"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
           f'<defs>{DEFS2}{B.CASE_DEF}{TV_DEF}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g></svg>')

    layers = [hook_title(t + 0.12, "Grumpo just wants to", "PLAY GTA 6!")]
    if TRY[0] <= t < T_GAMEON:
        i = sum(1 for x in TRY if t >= x)
        layers.append(counter(t, f"{i}/4", "TRY", i - 1, 4, bump_t=TRY[i - 1]))
    elif t >= T_GAMEON:
        layers.append(counter(t, "ON!", "GAME", 4 if t < T_TOSS1 else 4, 4, bump_t=T_GAMEON if t < T_TOSS1 else T_TOSS1))
    return overlay(svg, *layers)


def build_sfx():
    sfx(0.0, "whoosh", 0.8, 1.2)
    sfx(0.1, "laugh", 0.5, 0.8)
    sfx(T_SLAM - 0.1, "zip", 0.6, 1.3)
    sfx(T_SLAM, "click", 1.0)
    sfx(T_SLAM + 0.05, "whirr", 0.6)
    sfx(T_TVON, "ding", 0.7, 1.4)
    sfx(T_SIT0, "boing", 0.5, 1.1)
    sfx(T_SIT1, "thud", 0.5, 1.3)
    for i, f in enumerate(FLICK):
        sfx(f, "click", 0.7, 1.1)
        sfx(f + 0.01, "blip_down" if i % 2 == 0 else "blip", 0.5, 1.2)
    sfx(2.2, "laugh", 0.5, 1.4)
    sfx(2.9, "grumble", 0.7, 1.0)
    sfx(T_SPOT, "alert", 0.6)
    sfx(T_SPOT + 0.05, "gulp", 0.5, 1.3)
    sfx(T_YANK0, "zip", 0.9)
    sfx(T_YANK1, "pop", 0.6, 1.2)
    sfx(T_YANK1 + 0.1, "cool", 0.5)
    sfx(TRY[1], "ding", 0.4, 1.6)
    sfx(T_START2, "click", 0.8)
    sfx(T_START2 + 0.05, "rise", 0.5, 1.1)
    sfx(T_NJUMP0, "boing", 0.8, 1.0)
    sfx(T_NJUMP0 + 0.05, "whoosh", 0.7)
    sfx(T_NJUMP1, "laugh", 0.6, 1.3)
    sfx(T_NJUMP1 + 0.3, "flap", 0.5, 1.2)
    sfx(6.0, "grumble", 0.8, 0.9)
    sfx(T_CUSH0, "whoosh", 0.9, 0.9)
    sfx(T_CUSH1, "bonk", 1.0, 1.1)
    sfx(T_CUSH1 + 0.05, "squeak", 0.6, 1.3)
    sfx(T_CUSH1 + 0.1, "slide_up", 0.5, 1.2)
    sfx(7.9, "flap", 0.4, 0.9)
    sfx(TRY[2], "ding", 0.4, 1.6)
    sfx(8.9, "click", 0.6); sfx(9.0, "click", 0.6, 1.1)
    sfx(T_TUG0, "zip", 1.0, 0.9)
    sfx(T_TUG0 + 0.05, "gasp", 0.7)
    sfx(T_GRAB, "thud", 0.7)
    sfx(T_GRAB + 0.1, "strain", 0.8)
    for k in range(5):
        sfx(T_GRAB + 0.2 + k * 0.25, "creak", 0.5, 1.0 + 0.1 * k)
    sfx(T_YANKBACK, "whoosh", 1.0, 1.1)
    sfx(T_YANKBACK + 0.05, "boing", 0.8, 0.8)
    sfx(T_NFLY1, "crash_bush", 0.9)
    sfx(T_NFLY1 + 0.05, "clatter", 0.7)
    sfx(TRY[3], "ding", 0.4, 1.6)
    sfx(12.7, "click", 0.7)
    sfx(T_NODISC, "error_beep", 0.9)
    sfx(13.1, "gasp", 0.6, 0.9)
    sfx(13.3, "laugh", 0.6, 1.4)
    sfx(T_CHASE0, "whoosh", 0.8)
    sfx(T_CHASE1, "thud", 0.6)
    sfx(T_SHAKE0, "shaker", 0.9, 0.9)
    sfx(T_SHAKE0 + 0.5, "shaker", 0.7, 1.0)
    for kind, d, vx, rot0 in JUNK:
        t0 = T_SHAKE0 + 0.15 + d * 1.6
        sfx(t0 + 0.32, "plop" if kind != "disc" else "tap", 0.6, 1.0 + d)
    sfx(T_SHAKE1 + 0.55, "thud", 0.7, 1.2)
    sfx(T_INSERT, "click", 1.0)
    sfx(T_INSERT + 0.05, "whirr", 0.6)
    sfx(T_GAMEON, "cheer", 0.6, 1.0)
    sfx(T_GAMEON + 0.05, "ding", 0.8, 1.2)
    sfx(T_SAD, "gulp", 0.4, 1.4)
    sfx(17.0, "grumble", 0.5, 1.2)
    sfx(T_PULL2, "pop", 0.6, 1.1)
    sfx(T_TOSS0, "whoosh", 0.6, 1.3)
    sfx(T_TOSS1, "tap", 0.8, 1.2)
    sfx(T_TOSS1 + 0.05, "laugh", 0.7, 1.3)
    sfx(T_TOSS1 + 0.1, "cheer", 0.6, 1.2)
    sfx(T_SITN, "boing", 0.5, 1.3)
    for k in range(10):
        sfx(18.6 + k * 0.33, "click", 0.35, 1.0 + 0.1 * (k % 3))
    sfx(19.0, "zoom", 0.4, 1.2)
    sfx(20.4, "zoom", 0.4, 1.0)
    sfx(21.3, "laugh", 0.5, 1.2)
