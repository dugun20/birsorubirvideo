"""Grumpo & Nibbo — reusable character + scene drawing (SVG strings). Nibbo = the yellow character (function: nibbo / bloop)."""
import math

OUT = "#2a1a10"
OUTL = "#221c2e"
NOUT = "#3d2a12"


def lerp(a, b, t):
    return a + (b - a) * t


def mix_hex(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{int(round(lerp(x, y, t))):02x}" for x, y in zip(a, b))


class Ctx:
    """Per-frame id counter + defs collector."""
    def __init__(self):
        self.n = 0
        self.defs = []

    def uid(self, p="i"):
        self.n += 1
        return f"{p}{self.n}"


# ---------------------------------------------------------------- BLOOP
def bloop_face(expr, s):
    d = OUT
    g = [f'<g transform="scale({s:.3f})">']
    if expr in ("happy", "nervous", "wow", "cool", "uhoh"):
        ry = 10 if expr == "wow" else 8
        g.append(f'<ellipse cx="-14" cy="-4" rx="6" ry="{ry}" fill="{d}"/><ellipse cx="14" cy="-4" rx="6" ry="{ry}" fill="{d}"/>'
                 '<circle cx="-12" cy="-7" r="2.2" fill="#fff"/><circle cx="16" cy="-7" r="2.2" fill="#fff"/>')
    if expr == "joy":
        g.append(f'<path d="M-21 -2 q7 -10 14 0 M7 -2 q7 -10 14 0" fill="none" stroke="{d}" stroke-width="5" stroke-linecap="round"/>')
    if expr == "dizzy":
        g.append(f'<path d="M-20 -10 l12 12 M-8 -10 l-12 12 M8 -10 l12 12 M20 -10 l-12 12" stroke="{d}" stroke-width="5" stroke-linecap="round"/>')
    # mouths
    if expr in ("happy", "cool"):
        g.append(f'<path d="M-9 12 q9 9 18 0" fill="none" stroke="{d}" stroke-width="5" stroke-linecap="round"/>')
    elif expr == "joy":
        g.append(f'<path d="M-12 8 q12 18 24 0z" fill="#7a2a1a" stroke="{d}" stroke-width="4" stroke-linejoin="round"/>')
    elif expr == "nervous":
        g.append(f'<path d="M-12 14 q4 -5 8 0 t8 0 t8 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>'
                 '<path d="M26 -26 q8 13 0 18 q-8 -5 0 -18z" fill="#bfefff" stroke="#3a6a8a" stroke-width="2.5"/>')
    elif expr in ("wow", "uhoh"):
        g.append(f'<ellipse cx="0" cy="14" rx="7" ry="9" fill="#7a2a1a" stroke="{d}" stroke-width="4"/>')
    elif expr == "dizzy":
        g.append(f'<path d="M-10 14 q5 -6 10 0 t10 0" fill="none" stroke="{d}" stroke-width="4" stroke-linecap="round"/>')
    if expr not in ("dizzy",):
        g.append('<ellipse cx="-28" cy="10" rx="8" ry="4.5" fill="#ff7fa0" opacity="0.55"/>'
                 '<ellipse cx="28" cy="10" rx="8" ry="4.5" fill="#ff7fa0" opacity="0.55"/>')
    if expr == "cool":
        g.append('<rect x="-30" y="-14" width="26" height="16" rx="6" fill="#111"/><rect x="4" y="-14" width="26" height="16" rx="6" fill="#111"/>'
                 '<path d="M-4 -8 h8" stroke="#111" stroke-width="4"/><path d="M-26 -10 h8" stroke="#666" stroke-width="3"/>')
    g.append("</g>")
    return "".join(g)


def bloop(ctx, x, y, r=34, expr="happy", rot=0, sx=1, sy=1, paint=None, opacity=1, hat=None):
    s = r / 48
    out = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({sx:.3f} {sy:.3f})" opacity="{opacity:.2f}">']
    cid0 = ctx.uid("bc")
    ctx.defs.append(f'<clipPath id="{cid0}"><circle r="{r}"/></clipPath>')
    sw = min(8, max(3.5, r * 0.065))
    out.append(f'<g clip-path="url(#{cid0})"><rect x="{-r-4}" y="{-r-4}" width="{2*r+8}" height="{2*r+8}" fill="#f0a21c"/><circle cx="{-r*0.12:.1f}" cy="{-r*0.14:.1f}" r="{r}" fill="#ffd23c"/></g>')
    out.append(f'<circle r="{r}" fill="none" stroke="#3d2a12" stroke-width="{sw:.1f}"/>')
    if paint == "beach":
        cid = ctx.uid("c")
        ctx.defs.append(f'<clipPath id="{cid}"><circle r="{r - 2}"/></clipPath>')
        R = r * 1.2
        segs = []
        cols = ["#e8302a", "#ffffff", "#2a7de8", "#ffffff", "#2ac06a", "#ffffff"]
        for k, c in enumerate(cols):
            a0 = math.radians(k * 60 - 90)
            a1 = math.radians(k * 60 - 30)
            segs.append(f'<path d="M0 0 L{R*math.cos(a0):.1f} {R*math.sin(a0):.1f} L{R*math.cos(a1):.1f} {R*math.sin(a1):.1f}Z" fill="{c}" opacity="0.92"/>')
        out.append(f'<g clip-path="url(#{cid})">{"".join(segs)}<circle r="{r*0.3:.1f}" fill="url(#emoji)"/></g>')
        out.append(f'<circle r="{r}" fill="none" stroke="#8a5a08" stroke-width="{5 * r / 34:.1f}"/>')
    out.append(f'<ellipse cx="{-r*0.42:.1f}" cy="{-r*0.52:.1f}" rx="{r*0.2:.1f}" ry="{r*0.1:.1f}" fill="#fff" opacity="0.7" transform="rotate(-35 {-r*0.42:.1f} {-r*0.52:.1f})"/><circle cx="{-r*0.7:.1f}" cy="{-r*0.25:.1f}" r="{r*0.045:.1f}" fill="#fff" opacity="0.6"/>')
    out.append(bloop_face(expr, s * 1.05))
    if paint == "cupcake":
        k = r / 34
        out.append(f'<g transform="scale({k:.3f})"><path d="M-33 14 L33 14 L26 44 L-26 44Z" fill="#ff8fc0" stroke="#8a2a5a" stroke-width="5" stroke-linejoin="round"/>'
                   '<path d="M-20 14 l-3 30 M-7 14 l-1 30 M7 14 l1 30 M20 14 l3 30" stroke="#c84a8a" stroke-width="3"/>'
                   '<path d="M-36 -14 Q -40 -38 -16 -40 Q -10 -60 10 -52 Q 34 -52 32 -36 Q 42 -24 36 -14 Q 0 -6 -36 -14Z" fill="#fff4f8" stroke="#e8a8c4" stroke-width="5"/>'
                   '<circle cx="-14" cy="-30" r="3" fill="#6fd0ff"/><circle cx="8" cy="-40" r="3" fill="#7be08a"/><circle cx="18" cy="-26" r="3" fill="#ffb02a"/>'
                   '<circle cx="2" cy="-58" r="10" fill="#e8243a" stroke="#5a0a14" stroke-width="3"/><path d="M2 -66 q6 -10 14 -12" stroke="#3a7a2a" stroke-width="3" fill="none"/></g>')
    if hat == "party":
        k = r / 34
        out.append(f'<g transform="scale({k:.3f}) rotate(-14)"><path d="M-18 -28 L0 -76 L18 -28Z" fill="#3ac0ff" stroke="#123a5c" stroke-width="4" stroke-linejoin="round"/>'
                   '<path d="M-12 -42 h24 M-6 -58 h12" stroke="#ffd23a" stroke-width="5"/><circle cx="0" cy="-78" r="7" fill="#ff5a6e" stroke="#123a5c" stroke-width="3"/></g>')
    out.append("</g>")
    return "".join(out)


# ---------------------------------------------------------------- GRUMPO
def grumpo(ctx, x, y, s=1.0, expr="grumpy", red=0.0, glasses="up", look=(0, 0), rot=0,
           sx=1, sy=1, drink=True, sip=0.0, pole=None, steam=0.0, t=0.0, hat=None, frost=0.0, cherry=False):
    gid = ctx.uid("g")
    light = mix_hex("#a678e8", "#ff7a5a", red)
    dark = mix_hex("#5b2fa6", "#b4140c", red)
    ctx.defs.append(f'<radialGradient id="{gid}" cx="0.35" cy="0.3" r="0.8"><stop offset="0" stop-color="{light}"/><stop offset="1" stop-color="{dark}"/></radialGradient>')
    ink = mix_hex("#1a0a2e", "#3a0505", red)
    o = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s*sx:.3f} {s*sy:.3f})">']
    if red > 0.05:
        rg = ctx.uid("rg")
        ctx.defs.append(f'<radialGradient id="{rg}"><stop offset="0.55" stop-color="#ff2a1a" stop-opacity="{0.55*red:.2f}"/><stop offset="1" stop-color="#ff2a1a" stop-opacity="0"/></radialGradient>')
        o.append(f'<circle r="230" fill="url(#{rg})"/>')
    # pole (behind hand, in front of body handled by order below)
    pole_svg = ""
    if pole is not None:
        ang, L, op = pole[:3]
        kind = pole[3] if len(pole) > 3 else "net"
        px, py = -140, 0
        ex = px + L * math.cos(math.radians(ang))
        ey = py + L * math.sin(math.radians(ang))
        shaft = "#7fd0e8" if kind == "net" else "#cfd6de"
        if kind == "net":
            head = ('<ellipse rx="62" ry="34" fill="#ffffff" fill-opacity="0.35" stroke="#2a2a30" stroke-width="7"/>'
                    '<path d="M-50 -14 L50 14 M-50 14 L50 -14 M-30 -28 L-30 28 M0 -34 L0 34 M30 -28 L30 28" stroke="#2a2a30" stroke-width="3" opacity="0.6"/>'
                    '<ellipse rx="62" ry="34" fill="none" stroke="#ff9a2a" stroke-width="5"/>')
        else:  # fork
            head = ('<path d="M-34 14 Q -36 -8 -26 -10 L-26 -96 Q -26 -104 -18 -104 Q -10 -104 -10 -96 L-10 -12 L10 -12 L10 -96 Q 10 -104 18 -104 Q 26 -104 26 -96 L26 -10 Q 36 -8 34 14 Q 0 30 -34 14Z" fill="#dfe5ec" stroke="#2a2a30" stroke-width="6" stroke-linejoin="round"/>'
                    '<path d="M-6 -12 L-6 -100 Q 0 -108 6 -100 L6 -12Z" fill="#dfe5ec" stroke="#2a2a30" stroke-width="6"/>'
                    '<path d="M-24 4 h48" stroke="#fff" stroke-width="5" opacity="0.7"/>')
        pole_svg = (f'<g opacity="{op:.2f}"><line x1="{px}" y1="{py}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="#2a2a30" stroke-width="20" stroke-linecap="round"/>'
                    f'<line x1="{px}" y1="{py}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{shaft}" stroke-width="11" stroke-linecap="round"/>'
                    f'<g transform="translate({ex:.1f} {ey:.1f}) rotate({ang+90:.1f})">' + head + '</g>'
                    f'<path d="M-118 20 Q -140 18 {px} {py}" fill="none" stroke="{ink}" stroke-width="12" stroke-linecap="round"/>'
                    f'<circle cx="{px}" cy="{py}" r="15" fill="#9466e0" stroke="#221c2e" stroke-width="6"/></g>')
    base = mix_hex("#9466e0", "#ff6a52", red)
    shade = mix_hex("#6a41ba", "#c2281a", red)
    cid = ctx.uid("gc")
    ctx.defs.append(f'<clipPath id="{cid}"><circle r="130"/></clipPath>')
    ag = ctx.uid("ag")
    ctx.defs.append(f'<radialGradient id="{ag}"><stop offset="0.62" stop-color="{base}" stop-opacity="0.45"/><stop offset="1" stop-color="{base}" stop-opacity="0"/></radialGradient>')
    o.append(f'<circle r="190" fill="url(#{ag})"/>')
    o.append(f'<g clip-path="url(#{cid})"><rect x="-140" y="-140" width="280" height="280" fill="{shade}"/><circle cx="-16" cy="-18" r="130" fill="{base}"/></g>')
    o.append(f'<circle r="130" fill="none" stroke="#221c2e" stroke-width="8"/>')
    o.append('<ellipse cx="-60" cy="-66" rx="28" ry="13" fill="#fff" opacity="0.42" transform="rotate(-38 -60 -66)"/><circle cx="-92" cy="-30" r="6" fill="#fff" opacity="0.35"/>')
    lx, ly = look
    # eyes
    ery = 26 if expr == "shock" else 20
    erx = 22 if expr == "shock" else 18
    o.append(f'<ellipse cx="-38" cy="16" rx="{erx}" ry="{ery}" fill="#fff" stroke="#221c2e" stroke-width="3"/><ellipse cx="38" cy="16" rx="{erx}" ry="{ery}" fill="#fff" stroke="#221c2e" stroke-width="3"/>')
    pr = 7 if expr == "shock" else 10
    o.append(f'<circle cx="{-34+lx*8:.1f}" cy="{20+ly*8:.1f}" r="{pr}" fill="{ink}"/><circle cx="{34+lx*8:.1f}" cy="{20+ly*8:.1f}" r="{pr}" fill="{ink}"/>')
    if expr == "smug":  # half-lidded
        o.append(f'<path d="M-60 16 h44 v-24 h-44z M16 16 h44 v-24 h-44z" fill="{base}"/>'
                 f'<path d="M-58 14 h40 M18 14 h40" stroke="{ink}" stroke-width="6" stroke-linecap="round"/>')
    # brows
    if expr == "grumpy" or expr == "smug":
        o.append(f'<path d="M-72 -30 Q -44 -20 -16 -8 M72 -30 Q 44 -20 16 -8" fill="none" stroke="{ink}" stroke-width="17" stroke-linecap="round"/>')
    elif expr == "shock":
        o.append(f'<path d="M-72 -40 Q -40 -64 -8 -44 M8 -44 Q 40 -64 72 -40" fill="none" stroke="{ink}" stroke-width="16" stroke-linecap="round"/>')
    elif expr == "angry":
        o.append(f'<path d="M-78 -40 L -20 -6 M78 -40 L 20 -6" fill="none" stroke="{ink}" stroke-width="20" stroke-linecap="round"/>')
    elif expr == "suspicious":
        o.append(f'<path d="M-78 -18 Q -40 -8 -4 -10 M8 -36 Q 40 -50 76 -32" fill="none" stroke="{ink}" stroke-width="16" stroke-linecap="round"/>'
                 f'<path d="M-60 16 h44 v-20 h-44z" fill="{base}"/><path d="M-58 12 h40" stroke="{ink}" stroke-width="6" stroke-linecap="round"/>')
    # mouth
    if expr == "grumpy" or expr == "suspicious":
        o.append(f'<path d="M-34 76 q34 -26 68 0" fill="none" stroke="{ink}" stroke-width="10" stroke-linecap="round"/>')
    elif expr == "smug":
        o.append(f'<path d="M-30 66 q34 22 64 -10" fill="none" stroke="{ink}" stroke-width="10" stroke-linecap="round"/>')
    elif expr == "shock":
        o.append(f'<ellipse cx="0" cy="80" rx="22" ry="28" fill="#4a0a14" stroke="{ink}" stroke-width="8"/>')
    elif expr == "angry":
        o.append(f'<rect x="-44" y="58" width="88" height="40" rx="14" fill="#fff" stroke="{ink}" stroke-width="8"/>'
                 f'<path d="M-40 78 h80 M-14 60 v36 M14 60 v36" stroke="{ink}" stroke-width="4"/>')
    # glasses
    if glasses == "up":
        o.append('<g transform="translate(0 -84)"><rect x="-80" y="-18" width="66" height="38" rx="14" fill="#1a1a22"/><rect x="14" y="-18" width="66" height="38" rx="14" fill="#1a1a22"/>'
                 '<path d="M-14 -2 h28" stroke="#1a1a22" stroke-width="8"/><path d="M-66 -10 h20 M28 -10 h20" stroke="#5a5a70" stroke-width="5" stroke-linecap="round"/></g>')
    elif glasses == "down":
        o.append('<g transform="translate(0 14)"><rect x="-82" y="-20" width="70" height="42" rx="15" fill="#1a1a22"/><rect x="12" y="-20" width="70" height="42" rx="15" fill="#1a1a22"/>'
                 '<path d="M-12 -2 h24" stroke="#1a1a22" stroke-width="8"/><path d="M-68 -10 h22 M26 -10 h22" stroke="#5a5a70" stroke-width="5" stroke-linecap="round"/></g>')
    # drink arm
    if drink:
        cx, cy = lerp(176, 76, sip), lerp(-60, 30, sip)
        o.append(f'<path d="M120 30 Q {lerp(175,120,sip):.1f} {lerp(40,70,sip):.1f} {cx:.1f} {cy+40:.1f}" fill="none" stroke="{ink}" stroke-width="12" stroke-linecap="round"/>')
        o.append(f'<g transform="translate({cx:.1f} {cy:.1f})"><path d="M-20 -30 h40 l-8 60 h-24z" fill="#fff3a8" stroke="{ink}" stroke-width="6"/>'
                 f'<path d="M-16 -10 h32" stroke="#ffb02a" stroke-width="18" opacity="0.6"/>'
                 f'<path d="M6 -30 L{lerp(22,-30,sip):.1f} {lerp(-70,40,sip):.1f}" stroke="#ff5a6e" stroke-width="7" stroke-linecap="round"/></g>')
    if frost > 0:
        o.append(f'<path d="M-118 -50 Q -120 -128 0 -132 Q 120 -128 118 -50 Q 112 -10 96 -20 Q 92 30 74 20 Q 64 -6 44 0 Q 36 50 18 44 Q 8 4 -12 2 Q -20 36 -38 30 Q -46 -4 -66 2 Q -76 40 -92 30 Q -98 -16 -118 -50Z" '
                 f'fill="#fff7fb" stroke="#e8b8cc" stroke-width="6" opacity="{frost:.2f}"/>'
                 f'<g opacity="{frost:.2f}"><circle cx="-40" cy="-80" r="9" fill="#ff6fa8"/><circle cx="30" cy="-96" r="8" fill="#6fd0ff"/><circle cx="60" cy="-60" r="7" fill="#ffd23a"/><circle cx="-10" cy="-40" r="7" fill="#7be08a"/></g>')
    if hat == "party":
        o.append('<g transform="rotate(12)"><path d="M-52 -118 L0 -250 L52 -118Z" fill="#3ac0ff" stroke="#123a5c" stroke-width="7" stroke-linejoin="round"/>'
                 '<path d="M-38 -150 L36 -150 M-24 -186 L22 -186 M-12 -218 L12 -218" stroke="#ffd23a" stroke-width="12"/>'
                 '<circle cx="0" cy="-254" r="18" fill="#ff5a6e" stroke="#123a5c" stroke-width="6"/></g>')
    if cherry:
        fl = 1 + 0.15 * math.sin(t * 40)
        o.append('<path d="M0 -158 q14 -34 40 -40" fill="none" stroke="#3a7a2a" stroke-width="6" stroke-linecap="round"/>'
                 '<circle cx="0" cy="-140" r="30" fill="#e8243a" stroke="#5a0a14" stroke-width="6"/><ellipse cx="-10" cy="-152" rx="8" ry="5" fill="#fff" opacity="0.6"/>'
                 '<rect x="-9" y="-232" width="18" height="70" rx="4" fill="#fff" stroke="#123a5c" stroke-width="5"/><path d="M-9 -220 l18 12 M-9 -196 l18 12 M-9 -172 l18 12" stroke="#ff5a6e" stroke-width="5"/>'
                 f'<g transform="translate(0 -238) scale(1 {fl:.2f})"><path d="M0 -36 Q 16 -10 0 0 Q -16 -10 0 -36Z" fill="#ffb02a" stroke="#d45a0a" stroke-width="3"/><path d="M0 -20 Q 6 -8 0 -3 Q -6 -8 0 -20Z" fill="#fff3a8"/></g>')
    o.append(pole_svg)
    # steam
    if steam > 0:
        for k, (dx, ph) in enumerate([(-70, 0), (0, 0.33), (70, 0.66)]):
            p = (t * 1.6 + ph) % 1
            yy = -150 - p * 160
            rr = 22 + p * 40
            o.append(f'<circle cx="{dx + math.sin(p*6+k)*14:.1f}" cy="{yy:.1f}" r="{rr:.1f}" fill="#f4f4f4" stroke="#bbb" stroke-width="4" opacity="{steam*(1-p)*0.95:.2f}"/>')
    o.append("</g>")
    return "".join(o)


# ---------------------------------------------------------------- PROPS
def box(x, y, phase=0.0, rot=0, lid=0):
    fl = math.sin(phase * math.pi * 2) * 8
    fr = -fl
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">'
            f'<ellipse cx="-30" cy="{78+min(0,fl):.1f}" rx="16" ry="8" fill="#ffcc2e" stroke="#8a5a08" stroke-width="4"/>'
            f'<ellipse cx="30" cy="{78+min(0,fr):.1f}" rx="16" ry="8" fill="#ffcc2e" stroke="#8a5a08" stroke-width="4"/>'
            '<path d="M-62 -10 h124 v82 h-124z" fill="#c99a5b" stroke="#5a3a18" stroke-width="7"/>'
            '<path d="M-62 -10 l-20 -26 h124 l-20 26" fill="#dbb07a" stroke="#5a3a18" stroke-width="7" stroke-linejoin="round"/>'
            '<path d="M-30 30 h60" stroke="#5a3a18" stroke-width="5" opacity="0.5"/>'
            '<rect x="-40" y="2" width="80" height="18" rx="8" fill="#1a1208"/>'
            '<ellipse cx="-14" cy="11" rx="7" ry="6" fill="#fff"/><ellipse cx="14" cy="11" rx="7" ry="6" fill="#fff"/>'
            '<circle cx="-12" cy="12" r="3.5" fill="#1a1208"/><circle cx="16" cy="12" r="3.5" fill="#1a1208"/></g>')


def empty_box(x, y, rot):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">'
            '<path d="M-62 -40 h124 v82 h-124z" fill="#c99a5b" stroke="#5a3a18" stroke-width="7"/>'
            '<path d="M-62 -40 l-20 -26 h124 l-20 26" fill="#dbb07a" stroke="#5a3a18" stroke-width="7" stroke-linejoin="round"/>'
            '<rect x="-40" y="-28" width="80" height="18" rx="8" fill="#1a1208"/></g>')


def ring(x, y, rot=0, s=1):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f}) scale({s})">'
            '<ellipse rx="190" ry="54" fill="#ff5a6e" stroke="#7a1626" stroke-width="7"/>'
            '<path d="M-150 -28 a190 54 0 0 1 60 -20 M-40 -54 h80 M90 -48 a190 54 0 0 1 60 20" stroke="#fff" stroke-width="22" fill="none"/>'
            '<ellipse cx="0" cy="-6" rx="110" ry="26" fill="#3a8fd0"/></g>')


def sign(x, y, s=1.0):
    return (f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.3f})">'
            '<circle r="96" fill="#fff" stroke="#d62d20" stroke-width="22"/>'
            '<g transform="translate(0 2) scale(1.05)"><circle r="46" fill="url(#emoji)" stroke="#8a5a08" stroke-width="6"/>'
            + bloop_face("happy", 0.95) +
            '</g><line x1="-67" y1="-67" x2="67" y2="67" stroke="#d62d20" stroke-width="22" stroke-linecap="round"/>'
            '<circle r="107" fill="none" stroke="#5a0f0a" stroke-width="5"/></g>')


def star_twinkle(x, y, p):
    """p 0..1"""
    if p <= 0 or p >= 1:
        return ""
    sc = math.sin(p * math.pi) * 1.4
    pts = []
    for k in range(10):
        a = math.radians(k * 36 - 90)
        rr = 40 if k % 2 == 0 else 15
        pts.append(f"{rr*math.cos(a):.1f},{rr*math.sin(a):.1f}")
    return (f'<g transform="translate({x} {y}) rotate({p*180:.1f}) scale({sc:.2f})">'
            f'<polygon points="{" ".join(pts)}" fill="#fff6a8" stroke="#ffb020" stroke-width="5" stroke-linejoin="round"/></g>')


def symbol(x, y, ch, p, color="#d62d20"):
    """pop-in '!' or '?' bubble."""
    if p <= 0 or p >= 1:
        return ""
    sc = min(1, p * 6) * (1 + 0.25 * math.sin(min(1, p * 6) * math.pi))
    op = 1 if p < 0.8 else (1 - p) / 0.2
    return (f'<g transform="translate({x} {y}) scale({sc:.2f})" opacity="{op:.2f}">'
            f'<text x="0" y="0" font-family="DejaVu Sans" font-weight="bold" font-size="110" text-anchor="middle" '
            f'fill="{color}" stroke="#fff" stroke-width="8" paint-order="stroke">{ch}</text></g>')


def speed_lines(x, y, ang, op):
    if op <= 0:
        return ""
    o = []
    for k in range(4):
        off = (k - 1.5) * 22
        a = math.radians(ang)
        nx, ny = -math.sin(a) * off, math.cos(a) * off
        L = 70 + k % 2 * 30
        o.append(f'<line x1="{x+nx:.1f}" y1="{y+ny:.1f}" x2="{x+nx-L*math.cos(a):.1f}" y2="{y+ny-L*math.sin(a):.1f}" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity="{op:.2f}"/>')
    return "".join(o)


def impact(x, y, p, color="#fff6a8"):
    if p <= 0 or p >= 1:
        return ""
    r1 = 30 + p * 90
    pts = []
    for k in range(16):
        a = math.radians(k * 22.5)
        rr = r1 if k % 2 == 0 else r1 * 0.55
        pts.append(f"{x+rr*math.cos(a):.1f},{y+rr*math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{color}" stroke="#ff9a20" stroke-width="5" opacity="{1-p:.2f}"/>'


# Yellow character is officially named NIBBO
nibbo = bloop
