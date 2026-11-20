import sys, math
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chars2 import *
from env2 import *

GROUND = 1250
POOL_X0, POOL_X1, WATER, POOL_BOT = 680, 1560, 1300, 1700


def pool(t, wl=WATER):
    o = [f'<rect x="{POOL_X0-24}" y="{GROUND-34}" width="{POOL_X1-POOL_X0+48}" height="30" rx="6" fill="#eef1f5" stroke="{OL}" stroke-width="5"/>',
         f'<rect x="{POOL_X0}" y="{GROUND-6}" width="{POOL_X1-POOL_X0}" height="{POOL_BOT-GROUND+30}" fill="#d5dde6" stroke="{OL}" stroke-width="5"/>',
         f'<rect x="{POOL_X0+26}" y="{GROUND-6}" width="{POOL_X1-POOL_X0-52}" height="{POOL_BOT-GROUND+6}" fill="#b9dcef"/>']
    for gx in range(POOL_X0 + 26, POOL_X1 - 26, 64):
        o.append(f'<line x1="{gx}" y1="{GROUND}" x2="{gx}" y2="{POOL_BOT}" stroke="#9cc7e0" stroke-width="3"/>')
    for gy in range(GROUND + 30, POOL_BOT, 64):
        o.append(f'<line x1="{POOL_X0+26}" y1="{gy}" x2="{POOL_X1-26}" y2="{gy}" stroke="#9cc7e0" stroke-width="3"/>')
    wave = " ".join(f"L{x} {wl + 7*math.sin(x/45 + t*3.5):.1f}" for x in range(POOL_X0 + 26, POOL_X1 - 25, 16))
    o.append(f'<path d="M{POOL_X0+26} {POOL_BOT} L{POOL_X0+26} {wl} {wave} L{POOL_X1-26} {POOL_BOT}Z" fill="url(#water2)"/>')
    o.append(f'<path d="M{POOL_X0+26} {wl} {wave}" fill="none" stroke="#e9fbff" stroke-width="8" stroke-linecap="round"/>')
    o.append(f'<path d="M{POOL_X0+26} {wl+16} ' + " ".join(f"L{x} {wl + 16 + 5*math.sin(x/45 + t*3.5 + 1):.1f}" for x in range(POOL_X0 + 26, POOL_X1 - 25, 16)) + '" fill="none" stroke="#8fdcfa" stroke-width="5" opacity="0.7"/>')
    for k in range(7):
        x = POOL_X0 + 90 + k * 120 + 20 * math.sin(t + k)
        y = wl + 80 + (k % 3) * 90
        o.append(f'<path d="M{x:.0f} {y:.0f} q30 -10 60 0" fill="none" stroke="#bff0ff" stroke-width="5" stroke-linecap="round" opacity="0.55"/>')
    o.append(f'<rect x="{POOL_X0+26}" y="{POOL_BOT-14}" width="{POOL_X1-POOL_X0-52}" height="14" fill="#1f6fb0" opacity="0.35"/>')
    o.append(f'<rect x="{(POOL_X0+POOL_X1)//2-40}" y="{POOL_BOT-12}" width="80" height="14" rx="5" fill="#5b6b7c" stroke="{OL}" stroke-width="4"/>')
    # ladder
    o.append(f'<g fill="none" stroke="{OL}" stroke-width="15" stroke-linecap="round"><path d="M{POOL_X0+50} {GROUND-30} v-40 q0 -34 34 -34 q34 0 34 34 v190"/><path d="M{POOL_X0+96} {GROUND-30} v-30"/></g>'
             f'<g fill="none" stroke="#dfe6ee" stroke-width="8" stroke-linecap="round"><path d="M{POOL_X0+50} {GROUND-30} v-40 q0 -34 34 -34 q34 0 34 34 v190"/><path d="M{POOL_X0+96} {GROUND-30} v-30"/></g>')
    return "".join(o)


def ring2(x, y, s=1.0, rot=0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s:.3f})">'
            f'<ellipse rx="176" ry="50" fill="#ff5d72" stroke="{OL}" stroke-width="6"/>'
            '<path d="M-150 -24 a176 50 0 0 1 56 -20 M-36 -50 h72 M94 -44 a176 50 0 0 1 56 20 M-150 24 a176 50 0 0 0 56 20 M94 44 a176 50 0 0 0 56 -20" stroke="#fff" stroke-width="20" fill="none"/>'
            f'<ellipse rx="176" ry="50" fill="none" stroke="{OL}" stroke-width="6"/>'
            f'<ellipse cy="-4" rx="100" ry="22" fill="#3a8fd0" stroke="{OL}" stroke-width="4"/>'
            '<ellipse cx="-110" cy="-22" rx="24" ry="7" fill="#fff" opacity="0.5"/></g>')


def frame(t=1.0):
    ctx = Ctx()
    L = [sky(0, 2000), sun(1180, 420), cloud(500, 520, 1.1), cloud(1250, 700, 0.8), cloud(-50, 760, 0.9),
         hills(0, 2000, GROUND), ground_strip(0, 2000, GROUND)]
    L.append(underground(t))
    L.append(pool(t))
    icon = bloop(ctx, 0, 0, 52, "happy")
    L.append(sign2(560, GROUND - 26, icon, top=GROUND - 380))
    L.append(tufts([520, 600, 250, 1650, 1720], GROUND))
    # nibbo peeking behind bush
    L.append(bloop(ctx, 300, 1020, 112, "happy", rot=-8))
    L.append(bush_big(330, GROUND - 26, 0.95))
    # grumpo on ring
    gy = WATER - 112
    L.append(ring2(1120, WATER + 6))
    L.append(grumpo(ctx, 1120, gy, 0.92, "grumpy", 0, "up", (-0.6, 0), 0, 1, 1, True, 0, None, 0, t))
    cx, cy, z = 745, 1045, 0.915
    tr = f"translate(540 960) scale({z}) translate({-cx} {-cy})"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">'
            f'<defs>{DEFS2}{"".join(ctx.defs)}</defs><g transform="{tr}">{"".join(L)}</g></svg>')


if __name__ == "__main__":
    open("v2.svg", "w").write(frame())
