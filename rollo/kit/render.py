"""Rollo Racing renderer – pastel cute style (reference: Cihan's race_ornek.mp4).
render(r, meta, out_mp4, stills=None)  r = course.run(...) result
meta: dict(fmt='classic'|'country', theme=<name>, names=[...], colors=[(r,g,b)], flags=[code|None], header='Pick your color!')
"""
import cairo, math, random, subprocess, os
import course as C
import worlds as WD

W, H = 1080, 1920
FPS = C.FPS
Z = 1.3
VW, VH = W / Z, H / Z
FONT = "Lilita One"
HDR = 75          # header pushed down below YouTube's top buttons


def hx(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


OUT = hx("#2a2340")

THEMES = {
    "sky":    dict(bg=["#a6dcfb", "#c7c8f5", "#efcfe6", "#fbdcc6"], rod="#7867ad", peg="#ffcf3a", spin="#f0605d", bump="#ff7eb6", pad="#38c9a0"),
    "mint":   dict(bg=["#bff3e0", "#c9eef7", "#d9e4fb", "#efe0fb"], rod="#4f8f8a", peg="#ff9f43", spin="#7a5cf0", bump="#ff6f91", pad="#5ab0ff"),
    "candy":  dict(bg=["#ffd6e8", "#ffe3f1", "#fff0d9", "#e8f7d9"], rod="#c45c9c", peg="#6fd3ff", spin="#ffb703", bump="#8c6cf2", pad="#46c779"),
    "lemon":  dict(bg=["#fff6c7", "#ffe6b5", "#ffd6c9", "#f6cde3"], rod="#a7663b", peg="#46a3ff", spin="#ff5d73", bump="#9b6bff", pad="#2ec4b6"),
    "lilac":  dict(bg=["#e4d9ff", "#d6e2ff", "#d4f1ff", "#dff7ea"], rod="#5b5ea6", peg="#ffd23f", spin="#ff7f50", bump="#ff6fb5", pad="#3dd6a0"),
    "sunset": dict(bg=["#ffd9c2", "#ffc9c9", "#f3c4e4", "#d9c8f7"], rod="#6b4a8f", peg="#fff06a", spin="#ff5a5f", bump="#44c2ff", pad="#56d68c"),
}

CLASSIC = [("PINK", "#ff5fa8"), ("PURPLE", "#9b5cf6"), ("RED", "#ef3b3b"), ("GREEN", "#3cc24a"),
           ("CYAN", "#2fc6df"), ("YELLOW", "#ffd23f"), ("ORANGE", "#ff8c2a"), ("BLUE", "#3b7bf6")]

# country: name, text color, flag spec
COUNTRIES = {
    "USA": ("#d92b3a", "usa"), "BRAZIL": ("#1f9e48", "brazil"), "JAPAN": ("#e0283a", "japan"),
    "GERMANY": ("#e0a400", "h:#1b1b1b,#dd2a2a,#ffce00"), "FRANCE": ("#2d55c8", "v:#2d55c8,#ffffff,#e53b3b"),
    "ITALY": ("#1f9e48", "v:#1f9e48,#ffffff,#e53b3b"), "MEXICO": ("#1b7f4a", "mexico"),
    "TURKEY": ("#e30a17", "turkey"), "INDIA": ("#ff8f1f", "india"), "SPAIN": ("#d6202b", "h3:#d6202b,#ffc400,#d6202b"),
    "ARGENTINA": ("#58a8e8", "argentina"), "CANADA": ("#e0283a", "canada"),
    "UKRAINE": ("#2b6fd6", "h:#2b6fd6,#ffd500"), "NIGERIA": ("#16924a", "v:#16924a,#ffffff,#16924a"),
    "SWEDEN": ("#2b6fd6", "sweden"),
}


def lerpc(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def text_c(ctx, s, x, y, size, fill, stroke=OUT, sw=12, grad=None, shadow=True):
    ctx.select_font_face(FONT); ctx.set_font_size(size)
    e = ctx.text_extents(s)
    if e.width > W - 80:                       # never overflow the screen
        size *= (W - 80) / e.width; ctx.set_font_size(size); e = ctx.text_extents(s)
    x0 = x - e.width / 2 - e.x_bearing; y0 = y - e.height / 2 - e.y_bearing
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if shadow:
        ctx.move_to(x0 + 3, y0 + 7); ctx.text_path(s)
        ctx.set_source_rgba(*stroke, 0.9); ctx.set_line_width(sw); ctx.stroke_preserve(); ctx.fill()
    ctx.move_to(x0, y0); ctx.text_path(s)
    ctx.set_source_rgb(*stroke); ctx.set_line_width(sw); ctx.stroke_preserve()
    if grad:
        g = cairo.LinearGradient(0, y - e.height / 2, 0, y + e.height / 2)
        g.add_color_stop_rgb(0, *grad[0]); g.add_color_stop_rgb(1, *grad[1]); ctx.set_source(g)
    else:
        ctx.set_source_rgb(*fill)
    ctx.fill()


def rod(ctx, a, b, col, w=22):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgb(*OUT); ctx.set_line_width(w + 8); ctx.move_to(*a); ctx.line_to(*b); ctx.stroke()
    ctx.set_source_rgb(*col); ctx.set_line_width(w); ctx.move_to(*a); ctx.line_to(*b); ctx.stroke()
    dx, dy = b[0] - a[0], b[1] - a[1]; n = math.hypot(dx, dy) or 1
    ox, oy = dy / n * w * 0.22, -dx / n * w * 0.22
    if oy > 0:
        ox, oy = -ox, -oy
    ctx.set_source_rgba(1, 1, 1, 0.22); ctx.set_line_width(w * 0.28)
    ctx.move_to(a[0] + ox, a[1] + oy); ctx.line_to(b[0] + ox, b[1] + oy); ctx.stroke()


# ---------- flags ----------
def draw_flag(ctx, spec, x, y, r):
    ctx.save(); ctx.arc(x, y, r, 0, 7); ctx.clip()
    x0, y0, d = x - r, y - r, 2 * r

    def rect(c, a, b, w, h):
        ctx.set_source_rgb(*hx(c)); ctx.rectangle(a, b, w, h); ctx.fill()

    def circ(c, a, b, rr):
        ctx.set_source_rgb(*hx(c)); ctx.arc(a, b, rr, 0, 7); ctx.fill()
    if spec.startswith(("h:", "v:", "h3:")):
        kind, cols = spec.split(":"); cols = cols.split(",")
        if kind == "h3":
            rect(cols[0], x0, y0, d, d); rect(cols[1], x0, y0 + d * .25, d, d * .5)
        else:
            n = len(cols)
            for i, c in enumerate(cols):
                if kind == "h":
                    rect(c, x0, y0 + d * i / n, d, d / n + 1)
                else:
                    rect(c, x0 + d * i / n, y0, d / n + 1, d)
    elif spec == "usa":
        for i in range(9):
            rect("#d92b3a" if i % 2 == 0 else "#ffffff", x0, y0 + d * i / 9, d, d / 9 + 1)
        rect("#2a3f8f", x0, y0, d * .5, d * .5)
        for i in range(3):
            for j in range(3):
                circ("#ffffff", x0 + d * (.1 + .15 * i), y0 + d * (.1 + .15 * j), r * .05)
    elif spec == "brazil":
        rect("#1f9e48", x0, y0, d, d)
        ctx.set_source_rgb(*hx("#ffd400")); ctx.move_to(x, y - r * .78); ctx.line_to(x + r * .9, y)
        ctx.line_to(x, y + r * .78); ctx.line_to(x - r * .9, y); ctx.close_path(); ctx.fill()
        circ("#22408f", x, y, r * .42)
    elif spec == "japan":
        rect("#ffffff", x0, y0, d, d); circ("#e0283a", x, y, r * .5)
    elif spec == "mexico":
        for i, c in enumerate(["#1b7f4a", "#ffffff", "#d62b2b"]):
            rect(c, x0 + d * i / 3, y0, d / 3 + 1, d)
        circ("#9b6a2f", x, y + r * .02, r * .2); circ("#3a8f3a", x, y + r * .2, r * .08)
    elif spec == "turkey":
        rect("#e30a17", x0, y0, d, d)
        circ("#ffffff", x - r * .18, y, r * .45); circ("#e30a17", x - r * .06, y, r * .36)
        ctx.save(); ctx.translate(x + r * .38, y); ctx.set_source_rgb(1, 1, 1); ctx.move_to(r * .16, 0)
        for k in range(1, 10):
            a = k * math.pi / 5; rr = r * .16 if k % 2 == 0 else r * .065
            ctx.line_to(rr * math.cos(a), rr * math.sin(a))
        ctx.close_path(); ctx.fill(); ctx.restore()
    elif spec == "india":
        for i, c in enumerate(["#ff9933", "#ffffff", "#138808"]):
            rect(c, x0, y0 + d * i / 3, d, d / 3 + 1)
        ctx.set_source_rgb(*hx("#1a2a8a")); ctx.set_line_width(r * .06); ctx.arc(x, y, r * .2, 0, 7); ctx.stroke()
    elif spec == "argentina":
        for i, c in enumerate(["#74acdf", "#ffffff", "#74acdf"]):
            rect(c, x0, y0 + d * i / 3, d, d / 3 + 1)
        circ("#f6b40e", x, y, r * .16)
    elif spec == "canada":
        rect("#ffffff", x0, y0, d, d); rect("#e0283a", x0, y0, d * .25, d); rect("#e0283a", x0 + d * .75, y0, d * .25, d)
        ctx.set_source_rgb(*hx("#e0283a")); ctx.move_to(x, y - r * .4)
        for (px, py) in [(.12, -.15), (.3, -.2), (.22, .02), (.32, .1), (.08, .12), (.05, .35), (-.05, .35),
                         (-.08, .12), (-.32, .1), (-.22, .02), (-.3, -.2), (-.12, -.15)]:
            ctx.line_to(x + px * r, y + py * r)
        ctx.close_path(); ctx.fill()
    elif spec == "sweden":
        rect("#2b6fd6", x0, y0, d, d); rect("#ffd500", x0, y - r * .14, d, r * .28); rect("#ffd500", x - r * .35, y0, r * .28, d)
    ctx.restore()


def marble(ctx, x, y, c, vx=0, vy=0, happy=False, rad=C.RAD, face=True, flag=None):
    ctx.set_source_rgb(*OUT); ctx.arc(x, y, rad + 3, 0, 7); ctx.fill()
    if flag:
        draw_flag(ctx, flag, x, y, rad)
        g = cairo.RadialGradient(x - rad * .35, y - rad * .4, rad * .1, x, y, rad)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.35); g.add_color_stop_rgba(0.6, 1, 1, 1, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.22)
        ctx.set_source(g); ctx.arc(x, y, rad, 0, 7); ctx.fill()
    else:
        g = cairo.RadialGradient(x - rad * .35, y - rad * .4, rad * .1, x, y, rad)
        g.add_color_stop_rgb(0, *lerpc(c, (1, 1, 1), 0.45)); g.add_color_stop_rgb(0.6, *c); g.add_color_stop_rgb(1, *lerpc(c, (0, 0, 0), 0.22))
        ctx.set_source(g); ctx.arc(x, y, rad, 0, 7); ctx.fill()
    ctx.save(); ctx.translate(x - rad * .42, y - rad * .5); ctx.rotate(-0.6); ctx.scale(1, 0.55)
    ctx.set_source_rgba(1, 1, 1, 0.7); ctx.arc(0, 0, rad * .24, 0, 7); ctx.fill(); ctx.restore()
    if not face:
        return
    s = rad / 34
    n = math.hypot(vx, vy)
    lx, ly = (vx / n * 4 * s, vy / n * 3 * s) if n > 30 else (0, 0)
    for ex in (-11 * s, 11 * s):
        if happy:
            if flag:
                ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(8 * s); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                ctx.arc(x + ex, y - 2 * s, 6 * s, math.pi * 1.1, math.pi * 1.9); ctx.stroke()
            ctx.set_source_rgb(*OUT); ctx.set_line_width(4 * s); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.arc(x + ex, y - 2 * s, 6 * s, math.pi * 1.1, math.pi * 1.9); ctx.stroke()
        else:
            if flag:
                ctx.save(); ctx.translate(x + ex + lx, y - 3 * s + ly); ctx.scale(1, 1.25)
                ctx.set_source_rgb(1, 1, 1); ctx.arc(0, 0, 8.5 * s, 0, 7); ctx.fill(); ctx.restore()
            ctx.save(); ctx.translate(x + ex + lx, y - 3 * s + ly); ctx.scale(1, 1.3)
            ctx.set_source_rgb(*OUT); ctx.arc(0, 0, 5.5 * s, 0, 7); ctx.fill(); ctx.restore()
            ctx.set_source_rgb(1, 1, 1); ctx.arc(x + ex + lx + 1.8 * s, y - 6 * s + ly, 1.9 * s, 0, 7); ctx.fill()
    if happy:
        ctx.set_source_rgb(*OUT); ctx.set_line_width(4 * s)
        ctx.arc(x, y + 6 * s, 9 * s, 0.25 * math.pi, 0.75 * math.pi); ctx.stroke()
        if not flag:
            ctx.set_source_rgba(1, 0.4, 0.5, 0.45)
            for ex in (-20 * s, 20 * s):
                ctx.arc(x + ex, y + 8 * s, 5 * s, 0, 7); ctx.fill()


def crown(ctx, x, y, s=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    pts = [(-24, 14), (-28, -12), (-12, 2), (0, -18), (12, 2), (28, -12), (24, 14)]
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path(); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgb(*OUT); ctx.set_line_width(8); ctx.stroke_preserve()
    ctx.set_source_rgb(*hx("#ffd23f")); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.5); ctx.rectangle(-20, 6, 40, 4); ctx.fill()
    ctx.restore()


def rrect(ctx, x, y, w, h, r_):
    ctx.new_sub_path()
    ctx.arc(x + w - r_, y + r_, r_, -math.pi / 2, 0); ctx.arc(x + w - r_, y + h - r_, r_, 0, math.pi / 2)
    ctx.arc(x + r_, y + h - r_, r_, math.pi / 2, math.pi); ctx.arc(x + r_, y + r_, r_, math.pi, 1.5 * math.pi)
    ctx.close_path()


def eob(x):
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def render(r, meta, out_mp4, stills=None, crf=21):
    wd = WD.make(meta["world"], meta.get("palette"))
    bump_hits = [h[0] for h in r["hits"] if h[1] == "bumper" and h[2] > 0.45]
    names, cols, flags = meta["names"], meta["colors"], meta["flags"]
    n = len(names)
    frames, finish = r["frames"], r["finish"]
    cr = r["course"]
    done = sorted(x for x in finish if x is not None)
    first_t = done[0]; winner = finish.index(first_t)
    WN = names[winner]; WC = cols[winner]
    NF = len(frames)

    # camera
    cams = []
    cx, cy = 700 - VW / 2, 300 - 0.55 * VH
    bottom = cr.floor_y + 30 - 0.95 * VH
    for i, f in enumerate(frames):
        t = i / FPS; bs = f["b"]
        if t < C.GO_T + 0.2:
            tx, ty = 700 - VW / 2, 300 - 0.55 * VH
        elif t >= first_t:
            wb = bs[winner]; tx, ty = wb[0] - VW / 2, bottom
        else:
            unf = [b for k, b in enumerate(bs) if finish[k] is None or finish[k] > t]
            lead = max(unf, key=lambda b: b[1]); tx, ty = lead[0] - VW / 2, lead[1] - 0.55 * VH
        tx = max(0, min(C.WW - VW, tx)); ty = min(bottom, ty)
        k = 1 if i == 0 else 0.07
        cx += (tx - cx) * k; cy += (ty - cy) * k
        cams.append((cx, cy))

    rng = random.Random(3)
    conf = [(rng.uniform(0, W), rng.uniform(-300, 0), rng.uniform(-120, 120), rng.uniform(200, 600),
             rng.choice(cols), rng.uniform(0, 6), rng.uniform(-9, 9)) for _ in range(220)]

    def ranking(i):
        t = i / FPS; f = frames[i]; key = []
        for k in range(n):
            if finish[k] is not None and finish[k] <= t:
                key.append((0, finish[k], k))
            else:
                key.append((1, -f["b"][k][1], k))
        return [k for _, _, k in sorted(key)]

    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    slot = {k: 0.0 for k in range(n)}; trails = {k: [] for k in range(n)}
    BAR_X0, BAR_W = 70, 940; SLOT_DX = (BAR_W - 100) / (n - 1)
    only = None; proc = None
    if stills is not None:
        only = {int(s * FPS): s for s in stills}
    else:
        tmp = out_mp4 + ".tmp.mp4"
        proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
                                 "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf),
                                 "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    outs = []
    for i in range(NF):
        t = i / FPS; f = frames[i]; bs = f["b"]; camx, camy = cams[i]
        rank = ranking(i)
        for pos, k in enumerate(rank):
            tx = BAR_X0 + 50 + pos * SLOT_DX
            slot[k] = tx if i == 0 else slot[k] + (tx - slot[k]) * 0.2
        for k in range(n):
            trails[k].append(bs[k][:2]); trails[k] = trails[k][-7:]
        if only is not None and i not in only:
            continue
        prev = frames[max(0, i - 1)]["b"]
        p = (camy + VH / 2) / cr.floor_y
        wd.background(ctx, W, H, camx, camy, Z, p, t)
        shake = 0.0
        for ht in bump_hits:
            if 0 <= t - ht < 0.18:
                shake = max(shake, 7 * (1 - (t - ht) / 0.18))
        ctx.save()
        if shake:
            ctx.translate(shake * math.sin(t * 90), shake * math.cos(t * 77))
        ctx.scale(Z, Z); ctx.translate(-camx, -camy)
        vt, vb, vl, vr = camy - 120, camy + VH + 120, camx - 120, camx + VW + 120
        wd.under(ctx, camx, camy, VW, VH, t)
        fy = cr.finish_y
        if vt < fy + 300 and vb > fy - 60:
            wd.finish(ctx, fy, C.L, C.R)
        for (a, b, kind) in cr.rods:
            if max(a[1], b[1]) < vt or min(a[1], b[1]) > vb:
                continue
            wd.rod(ctx, a, b, kind)
        if t < C.GO_T:
            rod(ctx, cr.gate[0], cr.gate[1], (1, 1, 1))
        for (x, y, rr, kind) in cr.pegs:
            if vt < y < vb and vl < x < vr:
                wd.peg(ctx, x, y, rr, kind, t)
        for kd, (kx, ky, ka) in zip(cr.kin, f["k"]):
            if ky < vt - 300 or ky > vb + 300:
                continue
            ca, sa = math.cos(ka), math.sin(ka)
            for (a, b, thk) in kd["segs"]:
                pa = (kx + a[0] * ca - a[1] * sa, ky + a[0] * sa + a[1] * ca)
                pb = (kx + b[0] * ca - b[1] * sa, ky + b[0] * sa + b[1] * ca)
                if kd["kind"] == "spin":
                    wd.spinner(ctx, pa, pb)
                else:
                    wd.rod(ctx, pa, pb, "pad")
            if kd["kind"] == "spin":
                ctx.set_source_rgb(*OUT); ctx.arc(kx, ky, 17, 0, 7); ctx.fill()
                ctx.set_source_rgb(1, 1, 1); ctx.arc(kx, ky, 12, 0, 7); ctx.fill()
        for k in range(n):
            tr = trails[k]
            for j, (x, y) in enumerate(tr[:-1]):
                a = (j + 1) / len(tr)
                ctx.set_source_rgba(*cols[k], 0.18 * a); ctx.arc(x, y, C.RAD * (0.5 + 0.4 * a), 0, 7); ctx.fill()
        lead_k = rank[0]
        for k in range(n):
            x, y, _ = bs[k]
            vx, vy = (x - prev[k][0]) * FPS, (y - prev[k][1]) * FPS
            marble(ctx, x, y, cols[k], vx, vy, k == winner and t >= first_t, flag=flags[k])
            if k == lead_k and t > C.GO_T + 0.3:
                crown(ctx, x, y - C.RAD - 22, 0.9)
        ctx.restore()

        if C.GO_T <= t < C.GO_T + 0.9:
            q = (t - C.GO_T) / 0.9
            ctx.push_group()
            text_c(ctx, "GO!", 540, 800, 230 * (0.8 + 0.4 * q), hx("#5fd068"), sw=14, shadow=False)
            ctx.pop_group_to_source(); ctx.paint_with_alpha(0.85 * (1 - q ** 2))
        if t >= first_t:
            ct = t - first_t
            for (x0, y0, vx, vy, c, r0, vr) in conf:
                x = x0 + vx * ct + 30 * math.sin(ct * 3 + r0); y = y0 + vy * ct + 120 * ct * ct
                if y > H + 20:
                    continue
                ctx.save(); ctx.translate(x, y); ctx.rotate(r0 + vr * ct)
                ctx.set_source_rgb(*c); ctx.rectangle(-8, -3.5, 16, 7); ctx.fill(); ctx.restore()
        wd.overlay(ctx, W, H, t)
        if meta.get("slow") and meta["slow"][0] <= t <= meta["slow"][1]:
            sa, sb = meta["slow"]; q = min(1, (t - sa) / 0.25, (sb - t) / 0.25)
            g = cairo.RadialGradient(W / 2, H / 2, H * 0.32, W / 2, H / 2, H * 0.75)
            g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.45 * q)
            ctx.set_source(g); ctx.paint()
        # header (pushed down HDR px, WHO WINS ~10% smaller than v1)
        text_c(ctx, meta["header"], 540, 192 + HDR, 58, (1, 1, 1), sw=11)
        text_c(ctx, "WHO WINS?", 540, 292 + HDR, 135, None, sw=15, grad=(hx("#ffe35a"), hx("#ff9420")))
        rrect(ctx, BAR_X0, 430 + HDR, BAR_W, 82, 41); ctx.set_source_rgba(*hx("#3b3552"), 0.88); ctx.fill()
        for k in range(n):
            marble(ctx, slot[k], 471 + HDR, cols[k], rad=19, face=False, flag=flags[k])
        for m in range(3):
            text_c(ctx, str(m + 1), BAR_X0 + 50 + m * SLOT_DX, 536 + HDR, 34, (1, 1, 1), sw=8, shadow=False)
        if meta["world"] == "football" and first_t <= t < first_t + 1.1:
            q = (t - first_t) / 1.1
            ctx.push_group()
            ctx.save(); ctx.translate(540, 1150); ctx.rotate(-0.08); sc = max(0.01, eob(min(1, q * 3)))
            ctx.scale(sc, sc); text_c(ctx, "GOAL!", 0, 0, 230, hx("#ffd23f"), sw=18); ctx.restore()
            ctx.pop_group_to_source(); ctx.paint_with_alpha(1 if q < 0.7 else (1 - q) / 0.3)
        if t >= first_t:
            q = min(1, (t - first_t) / 0.45); s = max(0.01, eob(q))
            ctx.save(); ctx.translate(540, 760); ctx.scale(s, s)
            text_c(ctx, f"{WN} WINS!", 0, 0, 132, WC, sw=16); ctx.restore()
            if t >= first_t + 1.4:
                q2 = min(1, (t - first_t - 1.4) / 0.35)
                ctx.push_group(); text_c(ctx, meta["ask"].format(WN), 540, 900, 64, (1, 1, 1), sw=11)
                ctx.pop_group_to_source(); ctx.paint_with_alpha(q2)
        if only is not None:
            pth = f"{out_mp4}.still_{only[i]:.1f}.png"; surf.write_to_png(pth); outs.append(pth)
        else:
            proc.stdin.write(bytes(surf.get_data()))
    if proc:
        proc.stdin.close(); rc = proc.wait()
        if rc != 0:
            raise RuntimeError("ffmpeg failed")
        os.replace(out_mp4 + ".tmp.mp4", out_mp4)
    return dict(winner=WN, first_t=first_t, dur=NF / FPS, stills=outs)
