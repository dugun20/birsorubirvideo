"""Rollo Racing visual worlds. Each world = background + skins for rods / pegs / bumpers / spinners / pads + finish.
All bright & friendly (Cihan rejected dark/neon). Draw functions get a cairo ctx in WORLD coords unless noted.
"""
import math, random, cairo

OUT = (0x2a / 255, 0x23 / 255, 0x40 / 255)


def hx(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


def lerpc(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _stroke_line(ctx, a, b, w, col, cap=cairo.LINE_CAP_ROUND):
    ctx.set_line_cap(cap); ctx.set_source_rgb(*col); ctx.set_line_width(w)
    ctx.move_to(*a); ctx.line_to(*b); ctx.stroke()


def rod_plain(ctx, a, b, col, w=22, shine=0.22):
    _stroke_line(ctx, a, b, w + 8, OUT)
    _stroke_line(ctx, a, b, w, col)
    dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) or 1
    ox, oy = dy / n * w * 0.22, -dx / n * w * 0.22
    if oy > 0:
        ox, oy = -ox, -oy
    ctx.set_source_rgba(1, 1, 1, shine); ctx.set_line_width(w * 0.28)
    ctx.move_to(a[0] + ox, a[1] + oy); ctx.line_to(b[0] + ox, b[1] + oy); ctx.stroke()


def rod_striped(ctx, a, b, base, stripe, w=22, period=34):
    _stroke_line(ctx, a, b, w + 8, OUT)
    _stroke_line(ctx, a, b, w, base)
    dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n; px, py = -uy, ux
    ctx.save()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(w)
    ctx.move_to(*a); ctx.line_to(*b)
    # clip to rod body
    ctx.restore()
    ctx.set_source_rgb(*stripe)
    k = 0.0
    while k < n:
        c = (a[0] + ux * k, a[1] + uy * k)
        ctx.move_to(c[0] + px * w / 2 - ux * 6, c[1] + py * w / 2 - uy * 6)
        ctx.line_to(c[0] + px * w / 2 + ux * 6, c[1] + py * w / 2 + uy * 6)
        ctx.line_to(c[0] - px * w / 2 + ux * 16, c[1] - py * w / 2 + uy * 16)
        ctx.line_to(c[0] - px * w / 2 + ux * 4, c[1] - py * w / 2 + uy * 4)
        ctx.close_path(); ctx.fill()
        k += period
    ctx.set_source_rgba(1, 1, 1, 0.25); ctx.set_line_width(w * 0.25)
    ox, oy = px * w * 0.22, py * w * 0.22
    if oy > 0:
        ox, oy = -ox, -oy
    ctx.move_to(a[0] + ox, a[1] + oy); ctx.line_to(b[0] + ox, b[1] + oy); ctx.stroke()


def rod_wood(ctx, a, b, w=24):
    _stroke_line(ctx, a, b, w + 8, OUT, cairo.LINE_CAP_ROUND)
    _stroke_line(ctx, a, b, w, hx("#b9783f"))
    dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) or 1
    ux, uy = dx / n, dy / n; px, py = -uy, ux
    ctx.set_source_rgba(*hx("#7a4a22"), 0.7); ctx.set_line_width(2.5)
    for off in (-5, 3):
        ctx.move_to(a[0] + px * off, a[1] + py * off); ctx.line_to(b[0] + px * off, b[1] + py * off); ctx.stroke()
    k = 40.0
    while k < n - 20:
        c = (a[0] + ux * k, a[1] + uy * k)
        ctx.arc(c[0], c[1], 3, 0, 7); ctx.fill(); k += 130
    ox, oy = px * w * 0.25, py * w * 0.25
    if oy > 0:
        ox, oy = -ox, -oy
    ctx.set_source_rgba(1, 1, 1, 0.18); ctx.set_line_width(w * 0.22)
    ctx.move_to(a[0] + ox, a[1] + oy); ctx.line_to(b[0] + ox, b[1] + oy); ctx.stroke()


def rod_ice(ctx, a, b, w=22):
    rod_plain(ctx, a, b, hx("#9fd8f5"), w, 0.45)
    # snow cap on the upper side
    dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) or 1
    px, py = dy / n, -dx / n
    if py > 0:
        px, py = -px, -py
    ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(a[0] + px * 9, a[1] + py * 9); ctx.line_to(b[0] + px * 9, b[1] + py * 9); ctx.stroke()


# ---------------- pegs / bumpers ----------------
def peg_plain(ctx, x, y, r, col):
    ctx.set_source_rgb(*OUT); ctx.arc(x, y, r + 3.5, 0, 7); ctx.fill()
    ctx.set_source_rgb(*col); ctx.arc(x, y, r, 0, 7); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.55); ctx.arc(x - r * .35, y - r * .35, r * .3, 0, 7); ctx.fill()


def football(ctx, x, y, r, ang=0.0):
    ctx.set_source_rgb(*OUT); ctx.arc(x, y, r + 3.5, 0, 7); ctx.fill()
    ctx.set_source_rgb(1, 1, 1); ctx.arc(x, y, r, 0, 7); ctx.fill()
    ctx.save(); ctx.arc(x, y, r, 0, 7); ctx.clip()
    ctx.set_source_rgb(0.12, 0.12, 0.16)

    def pent(cx, cy, s, rot):
        ctx.move_to(cx + s * math.cos(rot), cy + s * math.sin(rot))
        for k in range(1, 5):
            a = rot + k * 2 * math.pi / 5
            ctx.line_to(cx + s * math.cos(a), cy + s * math.sin(a))
        ctx.close_path(); ctx.fill()
    pent(x, y, r * .36, ang - math.pi / 2)
    for k in range(5):
        a = ang - math.pi / 2 + k * 2 * math.pi / 5
        pent(x + math.cos(a) * r * 0.95, y + math.sin(a) * r * 0.95, r * .3, a + math.pi / 2)
    ctx.restore()
    ctx.set_source_rgba(1, 1, 1, 0.5); ctx.arc(x - r * .35, y - r * .4, r * .22, 0, 7); ctx.fill()


def candy(ctx, x, y, r, col):
    ctx.set_source_rgb(*OUT); ctx.arc(x, y, r + 3.5, 0, 7); ctx.fill()
    ctx.set_source_rgb(1, 1, 1); ctx.arc(x, y, r, 0, 7); ctx.fill()
    ctx.set_source_rgb(*col)
    for k in range(3):
        a0 = k * 2 * math.pi / 3
        ctx.move_to(x, y); ctx.arc(x, y, r, a0, a0 + math.pi / 3); ctx.close_path(); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.5); ctx.arc(x - r * .35, y - r * .35, r * .25, 0, 7); ctx.fill()


def donut(ctx, x, y, r, col):
    ctx.set_source_rgb(*OUT); ctx.arc(x, y, r + 5, 0, 7); ctx.fill()
    ctx.set_source_rgb(*hx("#e8a860")); ctx.arc(x, y, r, 0, 7); ctx.fill()
    ctx.set_source_rgb(*col)
    ctx.new_path()
    for k in range(24):
        a = k * 2 * math.pi / 24; rr = r * (0.86 + 0.06 * math.sin(k * 2.7))
        (ctx.move_to if k == 0 else ctx.line_to)(x + rr * math.cos(a), y + rr * math.sin(a))
    ctx.close_path(); ctx.fill()
    rng = random.Random(int(x * 7 + y))
    for _ in range(10):
        a = rng.uniform(0, 6.28); d = rng.uniform(r * .45, r * .75)
        ctx.set_source_rgb(*rng.choice([hx("#ffffff"), hx("#ffd23f"), hx("#3b7bf6"), hx("#3cc24a")]))
        ctx.save(); ctx.translate(x + d * math.cos(a), y + d * math.sin(a)); ctx.rotate(rng.uniform(0, 3))
        ctx.rectangle(-5, -2, 10, 4); ctx.fill(); ctx.restore()
    ctx.set_source_rgb(*OUT); ctx.arc(x, y, r * .3 + 3, 0, 7); ctx.fill()
    ctx.set_source_rgb(*hx("#fbe3ec")); ctx.arc(x, y, r * .3, 0, 7); ctx.fill()


def beachball(ctx, x, y, r):
    ctx.set_source_rgb(*OUT); ctx.arc(x, y, r + 5, 0, 7); ctx.fill()
    cols = [hx("#ff4d4d"), hx("#ffffff"), hx("#2f86f6"), hx("#ffffff"), hx("#ffd23f"), hx("#ffffff")]
    for k in range(6):
        a0 = k * math.pi / 3 - math.pi / 2
        ctx.move_to(x, y); ctx.arc(x, y, r, a0, a0 + math.pi / 3); ctx.close_path()
        ctx.set_source_rgb(*cols[k]); ctx.fill()
    ctx.set_source_rgb(1, 1, 1); ctx.arc(x, y, r * .18, 0, 7); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.45); ctx.arc(x - r * .35, y - r * .4, r * .22, 0, 7); ctx.fill()


def snowball(ctx, x, y, r):
    ctx.set_source_rgb(*OUT); ctx.arc(x, y, r + 3.5, 0, 7); ctx.fill()
    g = cairo.RadialGradient(x - r * .3, y - r * .3, r * .1, x, y, r)
    g.add_color_stop_rgb(0, 1, 1, 1); g.add_color_stop_rgb(1, *hx("#cfe8f7"))
    ctx.set_source(g); ctx.arc(x, y, r, 0, 7); ctx.fill()


def coconut(ctx, x, y, r):
    ctx.set_source_rgb(*OUT); ctx.arc(x, y, r + 3.5, 0, 7); ctx.fill()
    ctx.set_source_rgb(*hx("#8a5a33")); ctx.arc(x, y, r, 0, 7); ctx.fill()
    ctx.set_source_rgb(*hx("#5e3a1e"))
    for a in (-0.6, 0.6, 1.57):
        ctx.arc(x + r * .35 * math.cos(a - 1.57), y + r * .35 * math.sin(a - 1.57), r * .12, 0, 7); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.25); ctx.arc(x - r * .35, y - r * .35, r * .25, 0, 7); ctx.fill()


def bush(ctx, x, y, r):
    ctx.set_source_rgb(*OUT)
    for (dx, dy, rr) in [(0, 0, 1), (-.55, .1, .6), (.55, .1, .6), (0, -.5, .6)]:
        ctx.arc(x + dx * r, y + dy * r, rr * r + 5, 0, 7); ctx.fill()
    for (dx, dy, rr, c) in [(0, 0, 1, "#3fae5a"), (-.55, .1, .6, "#4cc46a"), (.55, .1, .6, "#4cc46a"), (0, -.5, .6, "#5fd47c")]:
        ctx.set_source_rgb(*hx(c)); ctx.arc(x + dx * r, y + dy * r, rr * r, 0, 7); ctx.fill()
    for (dx, dy) in [(-.3, -.1), (.35, .25), (.05, .45)]:
        ctx.set_source_rgb(*hx("#ff5d73")); ctx.arc(x + dx * r, y + dy * r, r * .1, 0, 7); ctx.fill()


# ---------------- backgrounds (screen coords) ----------------
def bg_gradient(ctx, W, H, top, bot):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *top); g.add_color_stop_rgb(1, *bot)
    ctx.set_source(g); ctx.paint()


def bokeh(ctx, W, H, camx, camy, Z, seed=3, col=(1, 1, 1), n=45, amin=0.12, amax=0.3):
    rng = random.Random(seed)
    for _ in range(n):
        bx, by, br, ba = rng.uniform(0, W), rng.uniform(0, 3000), rng.uniform(14, 48), rng.uniform(amin, amax)
        yy = (by - camy * Z * 0.35) % 3000 - 500; xx = (bx - camx * Z * 0.35) % (W + 200) - 100
        if -60 < yy < H + 60:
            ctx.set_source_rgba(*col, ba); ctx.arc(xx, yy, br, 0, 7); ctx.fill()


class World:
    name = "pastel"
    header_col = None

    def __init__(self, palette=None):
        self.pal = palette

    # world-space background details drawn under the track (optional)
    def under(self, ctx, camx, camy, VW, VH, t):
        pass

    def background(self, ctx, W, H, camx, camy, Z, p, t):
        raise NotImplementedError

    def rod(self, ctx, a, b, kind):
        raise NotImplementedError

    def peg(self, ctx, x, y, r, kind, t):
        raise NotImplementedError

    def spinner(self, ctx, a, b):
        rod_plain(ctx, a, b, self.spin_col, 24)

    def overlay(self, ctx, W, H, t):
        pass

    def finish(self, ctx, fy, L, R):
        sq = 40
        for xq in range(L, R, sq):
            for row in range(2):
                ctx.set_source_rgb(*((1, 1, 1) if ((xq - L) // sq + row) % 2 == 0 else (0.08, 0.06, 0.12)))
                ctx.rectangle(xq, fy - sq + row * sq, sq, sq); ctx.fill()


PASTELS = {
    "sky":    dict(bg=["#a6dcfb", "#c7c8f5", "#efcfe6", "#fbdcc6"], rod="#7867ad", peg="#ffcf3a", spin="#f0605d", bump="#ff7eb6", pad="#38c9a0"),
    "mint":   dict(bg=["#bff3e0", "#c9eef7", "#d9e4fb", "#efe0fb"], rod="#4f8f8a", peg="#ff9f43", spin="#7a5cf0", bump="#ff6f91", pad="#5ab0ff"),
    "lemon":  dict(bg=["#fff6c7", "#ffe6b5", "#ffd6c9", "#f6cde3"], rod="#a7663b", peg="#46a3ff", spin="#ff5d73", bump="#9b6bff", pad="#2ec4b6"),
    "lilac":  dict(bg=["#e4d9ff", "#d6e2ff", "#d4f1ff", "#dff7ea"], rod="#5b5ea6", peg="#ffd23f", spin="#ff7f50", bump="#ff6fb5", pad="#3dd6a0"),
    "sunset": dict(bg=["#ffd9c2", "#ffc9c9", "#f3c4e4", "#d9c8f7"], rod="#6b4a8f", peg="#fff06a", spin="#ff5a5f", bump="#44c2ff", pad="#56d68c"),
}


class Pastel(World):
    name = "pastel"

    def __init__(self, palette):
        th = PASTELS[palette]; self.palname = palette
        self.bg = [hx(c) for c in th["bg"]]
        self.rod_col, self.peg_col, self.spin_col, self.bump_col, self.pad_col = (hx(th[k]) for k in ("rod", "peg", "spin", "bump", "pad"))

    def bgcol(self, p):
        p = max(0, min(0.999, p)) * (len(self.bg) - 1); i = int(p)
        return lerpc(self.bg[i], self.bg[i + 1], p - i)

    def background(self, ctx, W, H, camx, camy, Z, p, t):
        bg_gradient(ctx, W, H, self.bgcol(p - 0.05), self.bgcol(p + 0.12))
        bokeh(ctx, W, H, camx, camy, Z)

    def rod(self, ctx, a, b, kind):
        rod_plain(ctx, a, b, self.pad_col if kind == "pad" else self.rod_col, 18 if kind == "pad" else 22)

    def peg(self, ctx, x, y, r, kind, t):
        if kind == "peg":
            peg_plain(ctx, x, y, r, self.peg_col)
        else:
            ctx.set_source_rgb(*OUT); ctx.arc(x, y, r + 5, 0, 7); ctx.fill()
            ctx.set_source_rgb(*self.bump_col); ctx.arc(x, y, r, 0, 7); ctx.fill()
            ctx.set_source_rgba(1, 1, 1, 0.55); ctx.set_line_width(5); ctx.arc(x, y, r * .6, 0, 7); ctx.stroke()


class Football(World):
    name = "football"
    spin_col = hx("#ffd23f")

    def background(self, ctx, W, H, camx, camy, Z, p, t):
        band = 150
        off = (camy * Z) % (2 * band)
        y = -off
        k = 0
        while y < H:
            ctx.set_source_rgb(*(hx("#5cbf4a") if k % 2 == 0 else hx("#4fae3f")))
            ctx.rectangle(0, y, W, band); ctx.fill(); y += band; k += 1
        # stadium light flares at the very top
        g = cairo.LinearGradient(0, 0, 0, 420)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.35); g.add_color_stop_rgba(1, 1, 1, 1, 0)
        ctx.set_source(g); ctx.rectangle(0, 0, W, 420); ctx.fill()

    def under(self, ctx, camx, camy, VW, VH, t):
        # pitch markings in world space
        ctx.set_source_rgba(1, 1, 1, 0.55); ctx.set_line_width(8)
        ctx.move_to(90, camy - 200); ctx.line_to(90, camy + VH + 200); ctx.stroke()
        ctx.move_to(1310, camy - 200); ctx.line_to(1310, camy + VH + 200); ctx.stroke()
        k0 = int((camy - 900) // 1800)
        for k in range(k0, k0 + 3):
            cy = k * 1800 + 900
            ctx.move_to(90, cy); ctx.line_to(1310, cy); ctx.stroke()
            ctx.arc(700, cy, 230, 0, 7); ctx.stroke()
            ctx.arc(700, cy, 10, 0, 7); ctx.fill()
            ctx.rectangle(400, cy + 600, 600, 260); ctx.stroke()

    def rod(self, ctx, a, b, kind):
        rod_plain(ctx, a, b, hx("#ffffff") if kind == "rod" else hx("#ffd23f"), 22, 0.0)

    def peg(self, ctx, x, y, r, kind, t):
        football(ctx, x, y, r, (x * 0.01 + t * (0.0 if kind == "peg" else 0.6)))

    def finish(self, ctx, fy, L, R):
        # goal: posts + crossbar + net below the line
        ctx.set_source_rgba(1, 1, 1, 0.75); ctx.set_line_width(3)
        for xq in range(L + 20, R, 36):
            ctx.move_to(xq, fy); ctx.line_to(xq + 20, fy + 260); ctx.stroke()
            ctx.move_to(xq + 36, fy); ctx.line_to(xq + 16, fy + 260); ctx.stroke()
        for yq in range(int(fy), int(fy + 260), 32):
            ctx.move_to(L, yq); ctx.line_to(R, yq); ctx.stroke()
        rod_plain(ctx, (L + 10, fy), (R - 10, fy), (1, 1, 1), 26, 0.0)

    def overlay(self, ctx, W, H, t):
        pass


class Candy(World):
    name = "candy"
    spin_col = hx("#ff5fa8")

    def background(self, ctx, W, H, camx, camy, Z, p, t):
        bg_gradient(ctx, W, H, hx("#ffe0ef"), hx("#fff3d9"))
        rng = random.Random(9)
        for _ in range(70):
            bx, by = rng.uniform(0, W), rng.uniform(0, 3000)
            yy = (by - camy * Z * 0.35) % 3000 - 500; xx = (bx - camx * Z * 0.35) % (W + 200) - 100
            if -20 < yy < H + 20:
                ctx.save(); ctx.translate(xx, yy); ctx.rotate(rng.uniform(0, 3.14))
                ctx.set_source_rgba(*rng.choice([hx("#ff7eb6"), hx("#7ad3ff"), hx("#ffd23f"), hx("#8fe39a"), hx("#b79cff")]), 0.55)
                ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(9); ctx.move_to(-10, 0); ctx.line_to(10, 0); ctx.stroke()
                ctx.restore()

    def rod(self, ctx, a, b, kind):
        if kind == "pad":
            rod_plain(ctx, a, b, hx("#8fe39a"), 18)
        else:
            rod_striped(ctx, a, b, (1, 1, 1), hx("#ff4d6d"))

    def peg(self, ctx, x, y, r, kind, t):
        rng = random.Random(int(x * 3 + y * 7))
        col = rng.choice([hx("#ff5fa8"), hx("#3b9bf6"), hx("#ffb703"), hx("#3cc24a"), hx("#9b5cf6")])
        if kind == "peg":
            candy(ctx, x, y, r, col)
        else:
            donut(ctx, x, y, r, rng.choice([hx("#ff7eb6"), hx("#b79cff"), hx("#7ad3ff")]))

    def spinner(self, ctx, a, b):
        rod_striped(ctx, a, b, (1, 1, 1), hx("#9b5cf6"), 24)


class Beach(World):
    name = "beach"
    spin_col = hx("#2f86f6")

    def background(self, ctx, W, H, camx, camy, Z, p, t):
        # sky -> sea -> sand as the race goes down
        stops = [hx("#9fe0ff"), hx("#5cc8f0"), hx("#47b9e6"), hx("#f7e2b0")]
        def col(q):
            q = max(0, min(0.999, q)) * 3; i = int(q); return lerpc(stops[i], stops[i + 1], q - i)
        bg_gradient(ctx, W, H, col(p - 0.06), col(p + 0.1))
        # gentle wave lines
        ctx.set_source_rgba(1, 1, 1, 0.35); ctx.set_line_width(6)
        off = (camy * Z * 0.5) % 260
        for k in range(10):
            yy = k * 260 - off
            ctx.move_to(0, yy)
            for xx in range(0, W + 40, 40):
                ctx.line_to(xx, yy + 10 * math.sin(xx / 60 + t * 2 + k))
            ctx.stroke()

    def rod(self, ctx, a, b, kind):
        if kind == "pad":
            rod_plain(ctx, a, b, hx("#ff8c2a"), 18)
        else:
            rod_wood(ctx, a, b)

    def peg(self, ctx, x, y, r, kind, t):
        if kind == "peg":
            peg_plain(ctx, x, y, r, hx("#ff8fa3"))
        else:
            beachball(ctx, x, y, r)

    def spinner(self, ctx, a, b):
        rod_plain(ctx, a, b, hx("#2f86f6"), 26)


class Winter(World):
    name = "winter"
    spin_col = hx("#ff5d73")

    def background(self, ctx, W, H, camx, camy, Z, p, t):
        bg_gradient(ctx, W, H, hx("#d8f0ff"), hx("#eef3ff"))
        bokeh(ctx, W, H, camx, camy, Z, seed=5, col=hx("#bfe3fa"), n=30, amin=0.25, amax=0.45)

    def overlay(self, ctx, W, H, t):
        rng = random.Random(11)
        ctx.set_source_rgba(1, 1, 1, 0.9)
        for _ in range(60):
            x0, sp, r, ph = rng.uniform(0, W), rng.uniform(60, 160), rng.uniform(3, 7), rng.uniform(0, 6.28)
            y = (rng.uniform(0, H) + sp * t) % (H + 20) - 10
            x = x0 + 18 * math.sin(t + ph)
            ctx.arc(x, y, r, 0, 7); ctx.fill()

    def rod(self, ctx, a, b, kind):
        if kind == "pad":
            rod_plain(ctx, a, b, hx("#ff8fb1"), 18)
        else:
            rod_ice(ctx, a, b)

    def peg(self, ctx, x, y, r, kind, t):
        snowball(ctx, x, y, r)
        if kind != "peg":
            ctx.set_source_rgb(*OUT)
            for ex in (-r * .3, r * .3):
                ctx.arc(x + ex, y - r * .15, r * .08, 0, 7); ctx.fill()
            ctx.set_source_rgb(*hx("#ff8c2a")); ctx.move_to(x, y); ctx.line_to(x + r * .45, y + r * .08); ctx.line_to(x, y + r * .14); ctx.fill()

    def spinner(self, ctx, a, b):
        rod_striped(ctx, a, b, (1, 1, 1), hx("#e53b3b"), 24)


class Jungle(World):
    name = "jungle"
    spin_col = hx("#8a5a33")

    def background(self, ctx, W, H, camx, camy, Z, p, t):
        bg_gradient(ctx, W, H, hx("#c9f2c2"), hx("#e8f7c8"))
        rng = random.Random(21)
        for _ in range(26):
            bx, by, s = rng.uniform(0, W), rng.uniform(0, 3000), rng.uniform(60, 130)
            yy = (by - camy * Z * 0.3) % 3000 - 500; xx = (bx - camx * Z * 0.3) % (W + 300) - 150
            if -150 < yy < H + 150:
                ctx.save(); ctx.translate(xx, yy); ctx.rotate(rng.uniform(-1, 1)); ctx.scale(1, 0.45)
                ctx.set_source_rgba(*hx("#7fcf74"), 0.35); ctx.arc(0, 0, s, 0, 7); ctx.fill(); ctx.restore()

    def rod(self, ctx, a, b, kind):
        if kind == "pad":
            rod_plain(ctx, a, b, hx("#5fd47c"), 18)
        else:
            rod_wood(ctx, a, b)

    def peg(self, ctx, x, y, r, kind, t):
        if kind == "peg":
            coconut(ctx, x, y, r)
        else:
            bush(ctx, x, y, r)

    def spinner(self, ctx, a, b):
        rod_wood(ctx, a, b, 26)


def make(name, palette=None):
    if name == "pastel":
        return Pastel(palette or "sky")
    return {"football": Football, "candy": Candy, "beach": Beach, "winter": Winter, "jungle": Jungle}[name]()


WORLDS = ["pastel", "football", "candy", "beach", "winter", "jungle"]
