"""High-quality flat environment kit (v2 look). World units = px at 1080 wide."""
import math, random

OL = "#221c2e"

DEFS2 = """
<linearGradient id="sky2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3f93ea"/><stop offset="0.55" stop-color="#78bdf5"/><stop offset="1" stop-color="#cdeeff"/></linearGradient>
<radialGradient id="sunglow" cx="0.5" cy="0.5" r="0.5"><stop offset="0.3" stop-color="#fffbe0" stop-opacity="0.95"/><stop offset="0.55" stop-color="#fff3b0" stop-opacity="0.35"/><stop offset="1" stop-color="#fff3b0" stop-opacity="0"/></radialGradient>
<linearGradient id="dirt2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a06c43"/><stop offset="1" stop-color="#7a4d2e"/></linearGradient>
<linearGradient id="water2" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5cc4f2" stop-opacity="0.92"/><stop offset="1" stop-color="#2b86cf" stop-opacity="0.96"/></linearGradient>
<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cdeeff" stop-opacity="0"/><stop offset="1" stop-color="#cdeeff" stop-opacity="0.55"/></linearGradient>
<radialGradient id="shadow"><stop offset="0" stop-color="#1a1028" stop-opacity="0.32"/><stop offset="1" stop-color="#1a1028" stop-opacity="0"/></radialGradient>
"""


def sky(x0, x1):
    return f'<rect x="{x0-600}" y="-800" width="{x1-x0+1200}" height="3200" fill="url(#sky2)"/>'


def sun(x, y):
    return (f'<circle cx="{x}" cy="{y}" r="190" fill="url(#sunglow)"/>'
            f'<circle cx="{x}" cy="{y}" r="70" fill="#fff6c8"/><circle cx="{x}" cy="{y}" r="56" fill="#fffbe6"/>')


def cloud(x, y, s=1.0):
    puffs = [(-70, 10, 42), (-25, -18, 56), (30, -28, 62), (82, -2, 46), (115, 18, 32), (-100, 24, 28)]
    base = "".join(f'<circle cx="{x+dx*s:.1f}" cy="{y+dy*s:.1f}" r="{r*s:.1f}" fill="#ffffff"/>' for dx, dy, r in puffs)
    shade = f'<rect x="{x-128*s:.1f}" y="{y+18*s:.1f}" width="{272*s:.1f}" height="{34*s:.1f}" rx="{17*s:.1f}" fill="#e3f1fb"/>'
    hl = f'<circle cx="{x+20*s:.1f}" cy="{y-40*s:.1f}" r="{22*s:.1f}" fill="#ffffff"/>'
    return f'<g opacity="0.97">{shade}{base}{hl}</g>'


def tree(x, y, s=1.0, far=False):
    if far:
        c1, c2, tr = "#8fc89a", "#a3d4ab", "#9a8a7a"
        return (f'<rect x="{x-6*s:.1f}" y="{y-40*s:.1f}" width="{12*s:.1f}" height="{44*s:.1f}" fill="{tr}"/>'
                f'<circle cx="{x:.1f}" cy="{y-70*s:.1f}" r="{44*s:.1f}" fill="{c1}"/><circle cx="{x-30*s:.1f}" cy="{y-50*s:.1f}" r="{30*s:.1f}" fill="{c1}"/>'
                f'<circle cx="{x+32*s:.1f}" cy="{y-52*s:.1f}" r="{28*s:.1f}" fill="{c1}"/><circle cx="{x-10*s:.1f}" cy="{y-86*s:.1f}" r="{18*s:.1f}" fill="{c2}"/>')
    return (f'<rect x="{x-9*s:.1f}" y="{y-60*s:.1f}" width="{18*s:.1f}" height="{64*s:.1f}" rx="4" fill="#8a5a3a" stroke="{OL}" stroke-width="5"/>'
            f'<g stroke="{OL}" stroke-width="5"><circle cx="{x-36*s:.1f}" cy="{y-70*s:.1f}" r="{38*s:.1f}" fill="#5aa957"/><circle cx="{x+38*s:.1f}" cy="{y-72*s:.1f}" r="{36*s:.1f}" fill="#5aa957"/>'
            f'<circle cx="{x:.1f}" cy="{y-104*s:.1f}" r="{52*s:.1f}" fill="#5aa957"/></g>'
            f'<circle cx="{x-36*s:.1f}" cy="{y-70*s:.1f}" r="{35.5*s:.1f}" fill="#5aa957"/><circle cx="{x+38*s:.1f}" cy="{y-72*s:.1f}" r="{33.5*s:.1f}" fill="#5aa957"/>'
            f'<circle cx="{x-14*s:.1f}" cy="{y-120*s:.1f}" r="{22*s:.1f}" fill="#79c46d"/><circle cx="{x-46*s:.1f}" cy="{y-80*s:.1f}" r="{13*s:.1f}" fill="#79c46d"/>')


def hills(x0, x1, ground):
    o = []
    # far range
    o.append(f'<path d="M{x0-600} {ground-260} ' + " ".join(
        f"Q {x + 160} {ground - 420 - 60*math.sin(x/300)} {x + 320} {ground - 260 - 30*math.cos(x/170)}" for x in range(x0 - 600, x1 + 600, 320)) +
        f' V{ground+60} H{x0-600}Z" fill="#a8d9b4"/>')
    for k, x in enumerate(range(x0 - 400, x1 + 400, 230)):
        o.append(tree(x + 60 * math.sin(k * 1.7), ground - 175 + 15 * math.cos(k), 0.8, far=True))
    o.append(f'<rect x="{x0-600}" y="{ground-480}" width="{x1-x0+1200}" height="300" fill="url(#haze)"/>')
    # mid hill
    o.append(f'<path d="M{x0-600} {ground-140} ' + " ".join(
        f"Q {x + 220} {ground - 250 - 40*math.sin(x/260)} {x + 440} {ground - 150}" for x in range(x0 - 600, x1 + 600, 440)) +
        f' V{ground+40} H{x0-600}Z" fill="#8ccc7f"/>')
    # near hill band
    o.append(f'<path d="M{x0-600} {ground-50} ' + " ".join(
        f"Q {x + 260} {ground - 110} {x + 520} {ground - 60}" for x in range(x0 - 600, x1 + 600, 520)) +
        f' V{ground+20} H{x0-600}Z" fill="#74bd67"/>')
    return "".join(o)


def ground_strip(x0, x1, ground, gaps=()):
    """grass top + sand + dirt from ground down."""
    o = [f'<rect x="{x0-600}" y="{ground}" width="{x1-x0+1200}" height="1400" fill="url(#dirt2)"/>']
    rnd = random.Random(5)
    for k in range(int((x1 - x0 + 1200) / 70)):
        x = x0 - 600 + k * 70 + rnd.uniform(-20, 20)
        y = ground + 80 + rnd.uniform(0, 900)
        o.append(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{rnd.uniform(7,16):.0f}" ry="{rnd.uniform(4,9):.0f}" fill="#6e4429" opacity="0.6"/>')
        if k % 3 == 0:
            o.append(f'<ellipse cx="{x+30:.0f}" cy="{y+40:.0f}" rx="5" ry="3" fill="#c8946a" opacity="0.6"/>')
    # grass + sand band
    o.append(f'<rect x="{x0-600}" y="{ground-6}" width="{x1-x0+1200}" height="22" fill="#e9d59a" stroke="{OL}" stroke-width="5"/>')
    o.append(f'<rect x="{x0-600}" y="{ground-30}" width="{x1-x0+1200}" height="26" fill="#7cc65c" stroke="{OL}" stroke-width="5"/>')
    o.append(f'<rect x="{x0-600}" y="{ground-27}" width="{x1-x0+1200}" height="8" fill="#98d672"/>')
    return "".join(o)


def tufts(xs, ground):
    o = []
    for x in xs:
        o.append(f'<path d="M{x-14} {ground-28} l6 -22 l4 18 l6 -28 l5 26 l7 -18 l2 24z" fill="#5aa947" stroke="{OL}" stroke-width="3.5" stroke-linejoin="round"/>')
    return "".join(o)


def bush_big(x, ground, s=1.0):
    pts = [(-120, -40, 80), (-40, -90, 100), (70, -70, 92), (150, -30, 66), (-170, -10, 50)]
    o = [f'<g stroke="{OL}" stroke-width="6">' + "".join(f'<circle cx="{x+dx*s:.1f}" cy="{ground+dy*s:.1f}" r="{r*s:.1f}" fill="#4f9e4c"/>' for dx, dy, r in pts) + '</g>']
    o.append("".join(f'<circle cx="{x+dx*s:.1f}" cy="{ground+dy*s:.1f}" r="{(r-3)*s:.1f}" fill="#4f9e4c"/>' for dx, dy, r in pts))
    o.append("".join(f'<circle cx="{x+dx*s:.1f}" cy="{ground+dy*s:.1f}" r="{r*s:.1f}" fill="#6dbb5f"/>' for dx, dy, r in [(-50, -140, 30), (60, -118, 24), (-130, -80, 18)]))
    o.append(f'<rect x="{x-230*s:.1f}" y="{ground-30}" width="{460*s:.1f}" height="30" fill="#4f9e4c"/>')
    return "".join(o)


def sign2(x, ground, icon_svg, top=None, s=1.0):
    top = top if top is not None else ground - 330
    return (f'<rect x="{x-11}" y="{top+80}" width="22" height="{ground-top-80+4}" rx="4" fill="#b07a45" stroke="{OL}" stroke-width="5"/>'
            f'<g transform="translate({x} {top}) scale({s:.3f})"><circle r="104" fill="#e83a2e" stroke="{OL}" stroke-width="6"/><circle r="80" fill="#ffffff" stroke="{OL}" stroke-width="4"/>'
            f'{icon_svg}<line x1="-56" y1="-56" x2="56" y2="56" stroke="#e83a2e" stroke-width="22" stroke-linecap="round"/>'
            '<ellipse cx="-50" cy="-62" rx="18" ry="8" fill="#fff" opacity="0.4" transform="rotate(-40 -50 -62)"/></g>')


def shadow(x, y, w, k=1.0):
    if k <= 0:
        return ""
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w*k:.1f}" ry="{w*0.18*k:.1f}" fill="url(#shadow)"/>'


def underground(t=0):
    """pipe + rocks for the pool world."""
    o = []
    d = "M1120 1712 V1800 a60 60 0 0 1 -60 60 H300 a60 60 0 0 0 -60 60 V2300"
    o.append(f'<path d="{d}" fill="none" stroke="{OL}" stroke-width="74"/>')
    o.append(f'<path d="{d}" fill="none" stroke="#aab4c0" stroke-width="60"/>')
    o.append('<path d="M1106 1716 V1798 M1060 1844 H300" fill="none" stroke="#dbe2ea" stroke-width="10"/>')
    for x in (520, 820):
        o.append(f'<rect x="{x}" y="1818" width="22" height="84" rx="4" fill="#8b96a4" stroke="{OL}" stroke-width="5"/>')
    for (x, y, rx, ry, c) in [(180, 1500, 46, 30, "#8d8f9c"), (1400, 1950, 60, 36, "#8d8f9c"), (640, 2050, 38, 24, "#9a9caa"), (90, 1980, 30, 20, "#9a9caa")]:
        o.append(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{c}" stroke="{OL}" stroke-width="5"/><ellipse cx="{x-rx*0.3:.0f}" cy="{y-ry*0.35:.0f}" rx="{rx*0.35:.0f}" ry="{ry*0.25:.0f}" fill="#c3c6d0"/>')
    o.append(f'<path d="M400 1290 q-20 60 10 110 q20 40 -10 80" fill="none" stroke="#6a4027" stroke-width="7" stroke-linecap="round"/>')
    o.append(f'<path d="M250 1290 q30 40 0 90" fill="none" stroke="#6a4027" stroke-width="6" stroke-linecap="round"/>')
    return "".join(o)
