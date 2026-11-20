import cairo, math, random, subprocess, sys, json, numpy as np
from multiprocessing import Pool
from sim import run, FPS, FINISH, COLORS, R

W, H = 1080, 1920
OL = (0x22/255, 0x1c/255, 0x2e/255)
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 2
OUT = sys.argv[2] if len(sys.argv) > 2 else "race.mp4"

frames, finish, hits, statics = run(SEED)
WIN_F = min(finish.values())
WINNER = min(finish, key=finish.get)
END_F = min(len(frames) - 1, WIN_F + int(3.6 * FPS))
N = END_F + 1


def hexc(h, a=1):
    h = h.lstrip("#"); return (int(h[0:2], 16)/255, int(h[2:4], 16)/255, int(h[4:6], 16)/255, a)


def shade(c, k):
    return tuple(max(0, min(1, v * k)) for v in c[:3])

# camera: zoomed, follows leader (x and y), holds on finish after win
Z = 1.55
VW, VH = W / Z, H / Z
cam = []
cx, cy = 540 - VW / 2, -330.0
for f in range(N):
    fr = frames[f]["b"]
    racing = [r for r in fr if r[2] < FINISH + 200]
    lead = max((racing or fr), key=lambda r: r[2])
    tx = lead[1] - VW / 2
    ty = lead[2] - VH * 0.52
    if f >= WIN_F - 20:
        w = [r for r in fr if r[0] == WINNER][0]
        tx = w[1] - VW / 2
        ty = FINISH - VH * 0.48
    if f < 70:
        tx, ty = 540 - VW / 2, -330
    tx = max(20, min(1060 - VW, tx))
    ty = max(-330, min(7040 - VH, ty))
    k = 0.09
    cx += (tx - cx) * k
    cy += (ty - cy) * k
    cam.append((cx, cy))

# ranks per frame
def ranking(f):
    fr = frames[f]["b"]
    fin = {ci: ff for ci, ff in finish.items() if ff <= f}
    def key(r):
        ci = r[0]
        if ci in fin: return (0, fin[ci])
        return (1, -r[2])
    return [r[0] for r in sorted(fr, key=key)]

# confetti particles
rnd = random.Random(7)
CONF = [(rnd.uniform(-1, 1), rnd.uniform(-1.6, -0.4), rnd.choice(COLORS)[1], rnd.uniform(0, 6.28), rnd.uniform(14, 26)) for _ in range(140)]


def text(ctx, s, x, y, size, fill, stroke=14, weight=cairo.FONT_WEIGHT_BOLD, align="c"):
    ctx.select_font_face("Fredoka", cairo.FONT_SLANT_NORMAL, weight)
    ctx.set_font_size(size)
    ext = ctx.text_extents(s)
    tx = x - ext.width / 2 - ext.x_bearing if align == "c" else x
    ctx.move_to(tx, y)
    ctx.text_path(s)
    if stroke:
        ctx.set_source_rgb(*OL); ctx.set_line_width(stroke); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
    if isinstance(fill, cairo.Pattern):
        ctx.set_source(fill)
    else:
        ctx.set_source_rgba(*fill)
    ctx.fill()
    return ext


def draw_bg(ctx, cy):
    # depth gradient
    g = cairo.LinearGradient(0, 0, 0, H)
    t0 = cy / 7000; t1 = (cy + H) / 7000
    def col(t):
        stops = [(0, (0.62, 0.86, 1.0)), (0.35, (0.72, 0.78, 1.0)), (0.7, (0.95, 0.80, 0.95)), (1, (1.0, 0.86, 0.70))]
        for i in range(len(stops) - 1):
            a, ca = stops[i]; b, cb = stops[i + 1]
            if a <= t <= b:
                u = (t - a) / (b - a); return tuple(ca[j] + (cb[j] - ca[j]) * u for j in range(3))
        return stops[-1][1]
    g.add_color_stop_rgb(0, *col(t0)); g.add_color_stop_rgb(1, *col(t1))
    ctx.set_source(g); ctx.paint()
    # parallax dots
    ctx.set_source_rgba(1, 1, 1, 0.22)
    for i in range(40):
        x = (i * 263) % W
        yy = ((i * 977) % 7000) - cy * 0.5
        yy %= 2400
        ctx.arc(x, yy - 200, 18 + (i % 5) * 9, 0, 6.283); ctx.fill()


def draw_track(ctx, cam_xy, sangles):
    camx, cy = cam_xy
    ctx.save(); ctx.scale(Z, Z); ctx.translate(-camx, -cy)
    # finish checker
    sq = 45
    for i in range(0, 24):
        for j in range(2):
            x = 40 + i * sq
            if x > 1040: break
            ctx.rectangle(x, FINISH - sq + j * sq, sq, sq)
            ctx.set_source_rgb(*( (0.13, 0.11, 0.18) if (i + j) % 2 else (1, 1, 1)))
            ctx.fill()
    for kind, *a in statics:
        if kind == "seg":
            (x1, y1), (x2, y2), r = a
            if max(y1, y2) < cy - 60 or min(y1, y2) > cy + VH + 60: continue
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(x1, y1); ctx.line_to(x2, y2)
            ctx.set_source_rgb(*OL); ctx.set_line_width(2 * r + 10); ctx.stroke()
            ctx.move_to(x1, y1); ctx.line_to(x2, y2)
            ctx.set_source_rgb(0.42, 0.36, 0.62); ctx.set_line_width(2 * r); ctx.stroke()
            ctx.move_to(x1, y1 - r * 0.4); ctx.line_to(x2, y2 - r * 0.4)
            ctx.set_source_rgba(1, 1, 1, 0.25); ctx.set_line_width(r * 0.6); ctx.stroke()
        else:
            (x, y), r = a
            if y < cy - 60 or y > cy + VH + 60: continue
            ctx.arc(x, y, r + 5, 0, 6.283); ctx.set_source_rgb(*OL); ctx.fill()
            ctx.arc(x, y, r, 0, 6.283); ctx.set_source_rgb(1.0, 0.78, 0.25); ctx.fill()
            ctx.arc(x - r * 0.3, y - r * 0.3, r * 0.35, 0, 6.283); ctx.set_source_rgba(1, 1, 1, 0.6); ctx.fill()
    for (cx, cyy, _), ang in zip([(330, 3800, 0), (750, 4150, 0), (330, 4500, 0), (750, 4850, 0)], sangles):
        if cyy < cy - 300 or cyy > cy + VH + 300: continue
        ctx.save(); ctx.translate(cx, cyy); ctx.rotate(ang)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(-200, 0); ctx.line_to(200, 0); ctx.set_source_rgb(*OL); ctx.set_line_width(38); ctx.stroke()
        ctx.move_to(-200, 0); ctx.line_to(200, 0); ctx.set_source_rgb(1.0, 0.42, 0.42); ctx.set_line_width(28); ctx.stroke()
        ctx.restore()
        ctx.arc(cx, cyy, 27, 0, 6.283); ctx.set_source_rgb(*OL); ctx.fill()
        ctx.arc(cx, cyy, 21, 0, 6.283); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    ctx.restore()


def draw_ball(ctx, x, y, color, vx, vy, happy=False, crown=False, t=0):
    c = hexc(color)
    ctx.arc(x + 4, y + R + 2, 0, 0, 1)
    ctx.arc(x, y, R + 5, 0, 6.283); ctx.set_source_rgb(*OL); ctx.fill()
    ctx.arc(x, y, R, 0, 6.283); ctx.set_source_rgb(*c[:3]); ctx.fill()
    # two-tone shade
    ctx.save(); ctx.arc(x, y, R, 0, 6.283); ctx.clip()
    ctx.arc(x + R * 0.35, y + R * 0.45, R * 1.0, 0, 6.283); ctx.set_source_rgb(*shade(c, 0.82)); ctx.fill()
    ctx.restore()
    ctx.arc(x - R * 0.42, y - R * 0.45, R * 0.22, 0, 6.283); ctx.set_source_rgba(1, 1, 1, 0.75); ctx.fill()
    # eyes look toward velocity
    sp = math.hypot(vx, vy) + 1e-6
    lx, ly = vx / sp * 5, vy / sp * 5
    for ex in (-10, 10):
        if happy:
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.arc(x + ex, y - 1, 6, math.pi * 1.1, math.pi * 1.9); ctx.set_source_rgb(*OL); ctx.set_line_width(4.5); ctx.stroke()
        else:
            ctx.arc(x + ex + lx, y - 3 + ly, 6.5, 0, 6.283); ctx.set_source_rgb(*OL); ctx.fill()
            ctx.arc(x + ex + lx - 2, y - 5 + ly, 2.2, 0, 6.283); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    if happy:
        ctx.arc(x, y + 8, 9, 0.15, math.pi - 0.15); ctx.set_source_rgb(*OL); ctx.fill()
    ctx.arc(x - 18, y + 9, 5, 0, 6.283); ctx.set_source_rgba(1, 0.45, 0.55, 0.45); ctx.fill()
    ctx.arc(x + 18, y + 9, 5, 0, 6.283); ctx.fill()
    if crown:
        bob = math.sin(t * 8) * 3
        cyy = y - R - 30 + bob
        ctx.move_to(x - 22, cyy + 18); ctx.line_to(x - 24, cyy - 6); ctx.line_to(x - 11, cyy + 5); ctx.line_to(x, cyy - 12)
        ctx.line_to(x + 11, cyy + 5); ctx.line_to(x + 24, cyy - 6); ctx.line_to(x + 22, cyy + 18); ctx.close_path()
        ctx.set_source_rgb(*OL); ctx.set_line_width(9); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.stroke_preserve()
        ctx.set_source_rgb(1.0, 0.82, 0.1); ctx.fill()


def hud(ctx, f, t, rank):
    # hook title
    pop = min(1, t / 0.3)
    s = 1 + 1.70158 * ((pop - 1) ** 3) + 2.70158 * ((pop - 1) ** 3) * 0 if pop < 1 else 1
    s = max(0.01, 1 + 2.7 * (pop - 1) ** 3 + 1.7 * (pop - 1) ** 2)
    ctx.save(); ctx.translate(540, 350); ctx.rotate(math.sin(t * 2.2) * 0.025 if t > 0.3 else 0); ctx.scale(s, s)
    text(ctx, "Pick your color!", 0, -120, 72, (1, 1, 1, 1), 16)
    g = cairo.LinearGradient(0, -130, 0, 10)
    g.add_color_stop_rgb(0, 1, 0.95, 0.48); g.add_color_stop_rgb(0.55, 1, 0.76, 0.1); g.add_color_stop_rgb(1, 1, 0.54, 0)
    text(ctx, "WHO WINS?", 0, 10, 160, g, 26)
    ctx.restore()
    # standings bar
    y = 480
    ctx.save()
    ctx.set_source_rgba(*OL, 0.78)
    x0, x1 = 70, 1010
    rr = 46
    ctx.new_sub_path(); ctx.arc(x0 + rr, y + rr, rr, math.pi / 2, 3 * math.pi / 2); ctx.arc(x1 - rr, y + rr, rr, -math.pi / 2, math.pi / 2); ctx.close_path(); ctx.fill()
    for i, ci in enumerate(rank):
        cx = 130 + i * 117
        col = hexc(COLORS[ci][1])
        ctx.arc(cx, y + rr, 30 if i == 0 else 24, 0, 6.283); ctx.set_source_rgb(1, 1, 1); ctx.fill()
        ctx.arc(cx, y + rr, 24 if i == 0 else 19, 0, 6.283); ctx.set_source_rgb(*col[:3]); ctx.fill()
        if i < 3:
            text(ctx, str(i + 1), cx, y + rr + 62, 34, (1, 1, 1, 1), 9)
    ctx.restore()
    if 60 <= f < 105:
        p = (f - 60) / 45
        sc = 1 + 0.6 * p; a = 1 - p
        ctx.save(); ctx.translate(540, 900); ctx.scale(sc, sc)
        text(ctx, "GO!", 0, 60, 230, (0.37, 0.83, 0.42, a), 28 * a)
        ctx.restore()


def winner_fx(ctx, f, t):
    dt = (f - WIN_F) / FPS
    if dt < 0: return
    if dt < 0.15:
        ctx.set_source_rgba(1, 1, 1, 0.6 * (1 - dt / 0.15)); ctx.paint()
    name, col = COLORS[WINNER]
    for (vx, vy, cc, a0, sz) in CONF:
        x = 540 + vx * 900 * dt
        y = 1150 + vy * 1500 * dt + 1400 * dt * dt
        ctx.save(); ctx.translate(x, y); ctx.rotate(a0 + dt * 8)
        ctx.rectangle(-sz / 2, -sz / 4, sz, sz / 2); ctx.set_source_rgba(*hexc(cc)[:3], 1); ctx.fill(); ctx.restore()
    p = min(1, dt / 0.35)
    s = max(0.01, 1 + 2.7 * (p - 1) ** 3 + 1.7 * (p - 1) ** 2)
    ctx.save(); ctx.translate(540, 760); ctx.scale(s, s); ctx.rotate(math.sin(t * 3) * 0.03)
    text(ctx, f"{name} WINS!", 0, 0, 150 if len(name) < 6 else 130, hexc(col), 26)
    ctx.restore()
    if dt > 1.4:
        a = min(1, (dt - 1.4) / 0.3)
        text(ctx, f"Did you pick {name}?", 540, 880, 70, (1, 1, 1, a), 16 * a)


def render(f):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    t = f / FPS
    camx, cy = cam[f]
    draw_bg(ctx, max(0, cy))
    draw_track(ctx, cam[f], frames[f]["s"])
    rank = ranking(f)
    leader = rank[0]
    ctx.save(); ctx.scale(Z, Z); ctx.translate(-camx, -cy)
    pf = frames[max(0, f - 1)]["b"]; pv = {r[0]: r for r in pf}
    # gate (closed) before open
    if f < 60:
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(400, 480); ctx.line_to(680, 480); ctx.set_source_rgb(*OL); ctx.set_line_width(30); ctx.stroke()
        ctx.move_to(400, 480); ctx.line_to(680, 480); ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(20); ctx.stroke()
    for ci, x, y, a in sorted(frames[f]["b"], key=lambda r: r[0] == leader):
        if y < cy - 80 or y > cy + VH + 80: continue
        p = pv[ci]; vx, vy = x - p[1], y - p[2]
        # trail
        if math.hypot(vx, vy) > 9:
            for k in range(1, 5):
                q = frames[max(0, f - k * 2)]["b"]; qq = [r for r in q if r[0] == ci][0]
                ctx.arc(qq[1], qq[2], R * (1 - k * 0.15), 0, 6.283); ctx.set_source_rgba(*hexc(COLORS[ci][1])[:3], 0.18 - k * 0.03); ctx.fill()
        happy = ci == WINNER and f >= WIN_F
        draw_ball(ctx, x, y, COLORS[ci][1], vx, vy, happy=happy, crown=(ci == leader and f > 90), t=t)
    ctx.restore()
    hud(ctx, f, t, rank)
    winner_fx(ctx, f, t)
    # fade out last 0.25s? keep
    buf = surf.get_data()
    arr = np.ndarray((H, W, 4), np.uint8, buf)
    return arr[:, :, :3].tobytes()


if __name__ == "__main__":
    mode = sys.argv[3] if len(sys.argv) > 3 else "full"
    if mode == "preview":
        import PIL.Image as Im
        ts = [0.5, 1.2, 4, 9, 14, 18, 22, WIN_F / FPS + 0.3, WIN_F / FPS + 2.0]
        ims = []
        for tt in ts:
            f = min(N - 1, int(tt * FPS))
            a = np.frombuffer(render(f), np.uint8).reshape(H, W, 3)[:, :, ::-1]
            ims.append(Im.fromarray(a.copy()).resize((270, 480)))
        sheet = Im.new("RGB", (270 * len(ims), 480))
        for i, im in enumerate(ims): sheet.paste(im, (i * 270, 0))
        sheet.save("preview.png"); print("preview.png", N / FPS, COLORS[WINNER][0])
    else:
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
                              "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
        with Pool(2) as pool:
            for i, b in enumerate(pool.imap(render, range(N), chunksize=8)):
                p.stdin.write(b)
                if i % 300 == 0: print("frame", i, "/", N, flush=True)
        p.stdin.close(); p.wait()
        json.dump({"hits": hits, "cam": cam, "Z": Z, "N": N, "win_f": WIN_F, "finish": finish}, open("events.json", "w"))
        print("video.mp4", N / FPS)
