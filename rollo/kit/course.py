"""Rollo Racing – procedural course builder + physics sim (pymunk).

A course = start V-gate + 3..6 parts from PARTS (random order) + finish.
World: x 40..1360 (walls), y grows downward. Marble radius 34.
Clearance rule (no traps): any gap a marble can enter is either >= 80 px or < 20 px.
"""
import math, random
import pymunk

WW = 1400
L, R = 40, 1360
WIN_L, WIN_R = L + 11, R - 11          # inner wall faces
RAD = 34
FPS = 60
SUB = 4
GO_T = 1.6
GAP = 170                               # vertical breathing room between parts


class Course:
    def __init__(self, space):
        self.space = space
        self.rods = []        # (a, b, kind)  kind: rod|pad
        self.pegs = []        # (x, y, r, kind) kind: peg|bumper
        self.kin = []         # kinematic: dict(body, segs=[(a,b,thick)], kind, motion)
        self.parts = []       # (name, y0, y1)
        self.st = space.static_body

    def rod(self, a, b, kind="rod", e=0.3, f=0.6, th=11):
        s = pymunk.Segment(self.st, a, b, th)
        s.elasticity = e if kind == "rod" else 1.05
        s.friction = f; s.collision_type = 4 if kind == "rod" else 6
        self.space.add(s); self.rods.append((a, b, kind))

    def peg(self, x, y, r=18, kind="peg"):
        c = pymunk.Circle(self.st, r, (x, y))
        c.elasticity = 0.6 if kind == "peg" else 0.92
        c.friction = 0.15
        c.collision_type = 3 if kind == "peg" else 2
        self.space.add(c); self.pegs.append((x, y, r, kind))

    def kinematic(self, pos, segs, kind, motion):
        b = pymunk.Body(body_type=pymunk.Body.KINEMATIC); b.position = pos
        shapes = []
        for (a, c, th) in segs:
            s = pymunk.Segment(b, a, c, th); s.elasticity = 0.5; s.friction = 0.5; s.collision_type = 5
            shapes.append(s)
        self.space.add(b, *shapes)
        if motion.get("w"):
            b.angular_velocity = motion["w"]
        self.kin.append(dict(body=b, segs=segs, kind=kind, motion=motion, base=pos))
        return b


# ---------------- parts ----------------
def p_plinko(c, y, rng):
    rows = rng.randint(6, 9)
    for row in range(rows):
        xs = range(150, 1151, 200) if row % 2 == 0 else range(250, 1251, 200)
        for x in xs:
            c.peg(x, y + 60 + row * 120)
    return 60 + rows * 120


def p_ramps(c, y, rng):
    """connector: 2 rolling ramps between parts (slows marbles, gives the rolling look)"""
    return p_zigzag(c, y, rng, n=2)


def p_zigzag(c, y, rng, n=None):
    n = n or rng.randint(3, 5)
    first_left = rng.random() < 0.5
    for i in range(n):
        left = (i % 2 == 0) == first_left
        if left:
            c.rod((L, y + i * 360), (1150, y + i * 360 + 230))
        else:
            c.rod((R, y + i * 360), (250, y + i * 360 + 230))
    return (n - 1) * 360 + 330


def p_spinners(c, y, rng):
    n = rng.randint(2, 4)
    sp = rng.uniform(1.8, 2.6)
    for i in range(n):
        x = 430 if i % 2 == 0 else 970
        yy = y + 220 + i * 250
        w = sp * (1 if i % 2 == 0 else -1) * rng.uniform(0.85, 1.15)
        c.kinematic((x, yy), [((-200, 0), (200, 0), 13)], "spin", dict(w=w))
        c.peg(970 if i % 2 == 0 else 430, yy - 30)
    return 220 + (n - 1) * 250 + 260


def p_windmill(c, y, rng):
    yy = y + 260
    w = rng.choice([-1, 1]) * rng.uniform(1.4, 2.0)
    arm = 175
    c.kinematic((700, yy), [((-arm, 0), (arm, 0), 13), ((0, -arm), (0, arm), 13)], "spin", dict(w=w))
    for x in (250, 1150):
        c.peg(x, yy - 60); c.peg(x, yy + 90)
    return 520


def p_funnel(c, y, rng):
    gap = 200
    cx = rng.choice([560, 700, 840])
    c.rod((L, y), (cx - gap / 2, y + 340))
    c.rod((R, y), (cx + gap / 2, y + 340))
    c.rod((cx - gap / 2, y + 340), (cx - gap / 2, y + 430))
    c.rod((cx + gap / 2, y + 340), (cx + gap / 2, y + 430))
    return 470


def p_bumpers(c, y, rng):
    layouts = [
        [(330, 120), (1070, 120), (700, 330), (300, 560), (1100, 560), (700, 780)],
        [(500, 140), (900, 140), (280, 380), (700, 400), (1120, 380), (500, 640), (900, 640)],
        [(700, 140), (400, 360), (1000, 360), (700, 580), (300, 800), (1100, 800)],
    ]
    lay = rng.choice(layouts)
    for (x, dy) in lay:
        c.peg(x, y + dy, 52, "bumper")
    return max(d for _, d in lay) + 170


def p_scatter(c, y, rng):
    pts = []
    tries = 0
    while len(pts) < 14 and tries < 2000:
        tries += 1
        x = rng.uniform(200, 1200); yy = rng.uniform(60, 700)
        if all(math.hypot(x - a, yy - b) > 200 for a, b in pts):
            pts.append((x, yy))
    for x, yy in pts:
        c.peg(x, y + yy)
    return 780


def p_sliders(c, y, rng):
    n = rng.randint(2, 3)
    for i in range(n):
        yy = y + 160 + i * 260
        amp = rng.uniform(260, 380); w = rng.uniform(1.2, 1.9); ph = rng.uniform(0, 6.28)
        c.kinematic((700, yy), [((-150, 0), (150, 0), 13)], "slide", dict(amp=amp, sw=w, ph=ph))
    return 160 + (n - 1) * 260 + 220


def p_pads(c, y, rng):
    # bouncy trampoline pads, alternating tilt
    n = rng.randint(3, 4)
    for i in range(n):
        yy = y + 120 + i * 230
        if i % 2 == 0:
            c.rod((260, yy), (560, yy + 70), "pad"); c.rod((840, yy + 70), (1140, yy), "pad")
        else:
            c.rod((560, yy), (840, yy + 40), "pad")
    return 120 + (n - 1) * 230 + 220


def p_split(c, y, rng):
    c.rod((700, y + 40), (700, y + 640))
    for row in range(4):
        yy = y + 120 + row * 140
        xs = [260, 560] if row % 2 == 0 else [410]
        for x in xs:
            c.peg(x, yy); c.peg(1400 - x, yy)
    return 700


PARTS = {
    "plinko": p_plinko, "zigzag": p_zigzag, "spinners": p_spinners, "windmill": p_windmill,
    "funnel": p_funnel, "bumpers": p_bumpers, "scatter": p_scatter, "sliders": p_sliders,
    "pads": p_pads, "split": p_split,
}


def build(space, parts, layout_seed):
    rng = random.Random(layout_seed)
    c = Course(space)
    # start V + gate
    c.rod((300, 80), (575, 430)); c.rod((1100, 80), (825, 430))
    gate = pymunk.Segment(c.st, (575, 430), (825, 430), 11)
    gate.elasticity = 0.1; gate.friction = 0.8
    space.add(gate)
    y = 620
    seq = []
    for i, name in enumerate(parts):
        seq.append(name)
        if name != "zigzag" and i < len(parts) - 1 and parts[i + 1] != "zigzag":
            seq.append("ramps")
    seq.append("ramps")
    for name in seq:
        h = (p_ramps if name == "ramps" else PARTS[name])(c, y, rng)
        c.parts.append((name, y, y + h))
        y += h + GAP
    finish_y = y + 120
    floor_y = finish_y + 300
    c.rod((L, -600), (L, floor_y)); c.rod((R, -600), (R, floor_y))
    c.rod((L, floor_y), (R, floor_y))
    c.finish_y, c.floor_y = finish_y, floor_y
    return c, gate


def run(parts, layout_seed, seed, n_balls=8, max_t=45):
    rnd = random.Random(seed)
    space = pymunk.Space(); space.gravity = (0, 2600)
    c, gate = build(space, parts, layout_seed)
    spots = [(612 + 58 * k, 380 - 70 * r) for r in range(3) for k in range(4)]
    rnd.shuffle(spots)
    balls = []
    for i in range(n_balls):
        b = pymunk.Body(1, pymunk.moment_for_circle(1, 0, RAD))
        x, yy = spots[i]
        b.position = (x + rnd.uniform(-5, 5), yy - 120)
        s = pymunk.Circle(b, RAD); s.elasticity = 0.45; s.friction = 0.7; s.collision_type = 1
        space.add(b, s); balls.append(b)
    hits = []; ct = [0.0]
    KIND = {2: "bumper", 3: "peg", 4: "rod", 5: "spin", 6: "pad", 1: "ball"}

    def on_hit(arb, sp, data):
        imp = arb.total_impulse.length
        if imp > 150:
            p = arb.contact_point_set.points
            px, py = (p[0].point_a.x, p[0].point_a.y) if p else (700, 0)
            k = KIND.get(arb.shapes[1].collision_type, "rod")
            hits.append((round(ct[0], 3), k, min(1.0, imp / 1200), round(px, 1), round(py, 1)))
    for t2 in (1, 2, 3, 4, 5, 6):
        space.on_collision(1, t2, post_solve=on_hit)

    frames, finish = [], [None] * n_balls
    slow = [0.0] * n_balls
    dt = 1.0 / (FPS * SUB); t = 0.0; opened = False
    while t < max_t:
        for _ in range(SUB):
            if not opened and t >= GO_T:
                space.remove(gate); opened = True
            for k in c.kin:
                m = k["motion"]
                if "amp" in m:
                    k["body"].velocity = (m["amp"] * m["sw"] * math.cos(m["sw"] * t + m["ph"]), 0)
                    if t == 0:
                        k["body"].position = (k["base"][0] + m["amp"] * math.sin(m["ph"]), k["base"][1])
            space.step(dt); t += dt; ct[0] = t
            for i, b in enumerate(balls):
                if opened and finish[i] is None and b.velocity.length < 40:
                    slow[i] += dt
                    if slow[i] > 0.5:
                        b.apply_impulse_at_local_point((rnd.choice([-1, 1]) * rnd.uniform(180, 260), -120)); slow[i] = 0
                else:
                    slow[i] = 0
                if finish[i] is None and b.position.y > c.finish_y:
                    finish[i] = t
        frames.append({"b": [(b.position.x, b.position.y, b.angle) for b in balls],
                       "k": [(k["body"].position.x, k["body"].position.y, k["body"].angle) for k in c.kin]})
        done = [f for f in finish if f is not None]
        if done and t > min(done) + 4.5:
            break
    return dict(frames=frames, finish=finish, hits=hits, course=c)


def score(r):
    """Return (ok, info) – race quality check."""
    f = r["finish"]
    done = sorted(x for x in f if x is not None)
    if len(done) < 4:
        return False, "few finishers"
    first = done[0]
    if not (15.0 <= first <= 26.0):
        return False, f"winner time {first:.1f}"
    gap = done[1] - done[0]
    ch, prev = 0, None
    for fm in r["frames"][150:int(first * FPS)]:
        ys = [b[1] for b in fm["b"]]; l = ys.index(max(ys))
        if prev is not None and l != prev:
            ch += 1
        prev = l
    ok = gap < 1.3 and ch >= 5
    return ok, dict(first=round(first, 2), gap=round(gap, 2), changes=ch, n_fin=len(done))
