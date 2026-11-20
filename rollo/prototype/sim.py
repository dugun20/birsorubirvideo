import pymunk, random, math, json, sys

W = 1080
FPS = 60
SUB = 6
R = 30
COLORS = [("RED", "#ff4a4a"), ("ORANGE", "#ff9a2e"), ("YELLOW", "#ffd93b"), ("GREEN", "#4cd964"),
          ("CYAN", "#3fd6e8"), ("BLUE", "#3b7bff"), ("PURPLE", "#a35cff"), ("PINK", "#ff6fc4")]
FINISH = 6650


def build(seed):
    rnd = random.Random(seed)
    sp = pymunk.Space()
    sp.gravity = (0, 1500)
    sb = sp.static_body
    statics = []  # for drawing: ('seg',a,b,r) ('peg',c,r)

    def seg(a, b, r=10, fr=0.5, el=0.45, draw=True):
        s = pymunk.Segment(sb, a, b, r); s.friction = fr; s.elasticity = el; s.collision_type = 2
        sp.add(s)
        if draw: statics.append(("seg", a, b, r))
        return s

    def peg(c, r=14, el=0.6):
        s = pymunk.Circle(sb, r, c); s.friction = 0.3; s.elasticity = el; s.collision_type = 3
        sp.add(s); statics.append(("peg", c, r))

    # side walls
    seg((40, 0), (40, 7200), 14); seg((1040, 0), (1040, 7200), 14)
    # start box funnel
    seg((40, 260), (420, 470), 12); seg((1040, 260), (660, 470), 12)
    gate = seg((400, 480), (680, 480), 10, draw=False)
    # A: plinko
    rows = 11
    for i in range(rows):
        y = 680 + i * 125
        off = 0 if i % 2 == 0 else 60
        for k in range(9):
            x = 120 + off + k * 120
            if 70 < x < 1010:
                peg((x, y), 13)
    # bumpers between A and B
    # B: zigzag ramps
    y0 = 2150
    for i in range(5):
        y = y0 + i * 300
        if i % 2 == 0:
            seg((40, y), (880, y + 150), 12, fr=0.25, el=0.3)
        else:
            seg((1040, y), (200, y + 150), 12, fr=0.25, el=0.3)
    # C: spinners + pegs
    spinners = []
    for j, (cx, cy, w) in enumerate([(330, 3800, 2.2), (750, 4150, -2.6), (330, 4500, 2.9), (750, 4850, -2.0)]):
        body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        body.position = (cx, cy); body.angular_velocity = w
        sh = pymunk.Segment(body, (-200, 0), (200, 0), 14); sh.elasticity = 0.7; sh.friction = 0.4; sh.collision_type = 4
        sp.add(body, sh)
        spinners.append(body)
        peg((cx, cy), 22)
    for (x, y) in [(750, 3800), (330, 4150), (750, 4500), (330, 4850), (540, 3980), (540, 4330), (540, 4680)]:
        peg((x, y), 18, el=0.8)
    # D: funnel
    seg((40, 5150), (480, 5520), 12, fr=0.2); seg((1040, 5150), (600, 5520), 12, fr=0.2)
    # E: final bumpers and short ramps
    for (x, y) in [(300, 5750), (540, 5850), (780, 5750), (420, 6050), (660, 6050), (540, 6250)]:
        peg((x, y), 26, el=0.9)
    seg((40, 6380), (300, 6450), 12, fr=0.2); seg((1040, 6380), (780, 6450), 12, fr=0.2)
    # finish basin
    seg((40, 7000), (1040, 7000), 14)

    balls = []
    order = list(range(8)); rnd.shuffle(order)
    for n, ci in enumerate(order):
        b = pymunk.Body(1, pymunk.moment_for_circle(1, 0, R))
        b.position = (180 + (n % 4) * 230 + rnd.uniform(-20, 20), 120 + (n // 4) * 70 + rnd.uniform(-5, 5))
        s = pymunk.Circle(b, R); s.elasticity = 0.55; s.friction = 0.5; s.collision_type = 1
        sp.add(b, s)
        balls.append((ci, b))
    return sp, gate, balls, spinners, statics


def run(seed, maxt=70):
    sp, gate, balls, spinners, statics = build(seed)
    hits = []
    cur = {"f": 0}

    def post(arb, space, data):
        if arb.is_first_contact:
            ke = arb.total_ke
            if ke > 2e5:
                ball = arb.shapes[0]
                p = arb.contact_point_set.points[0].point_a if arb.contact_point_set.points else ball.body.position
                hits.append((cur["f"], arb.shapes[1].collision_type, min(1.0, ke / 3e6), float(p.y)))
    for ct in (2, 3, 4):
        sp.on_collision(1, ct, post_solve=post) if hasattr(sp, "on_collision") else None
    frames = []
    finish = {}
    gate_open = 60
    for f in range(int(maxt * FPS)):
        cur["f"] = f
        if f == gate_open:
            sp.remove(gate)
        for _ in range(SUB):
            sp.step(1 / FPS / SUB)
        rec = []
        for ci, b in balls:
            x, y = b.position
            # unstick: tiny nudge if ball nearly stopped after gate
            if f > gate_open + 30 and b.velocity.length < 8 and ci not in finish:
                b.apply_impulse_at_local_point((random.Random(f * 31 + ci).uniform(-120, 120), -60))
            rec.append((ci, round(x, 1), round(y, 1), round(b.angle, 3)))
            if y > FINISH and ci not in finish:
                finish[ci] = f
        frames.append({"b": rec, "s": [round(s.angle, 3) for s in spinners]})
        if len(finish) == 8 or (finish and f > max(finish.values()) + 0 and len(finish) >= 8):
            break
        if finish and f > min(finish.values()) + int(4 * FPS):
            break
    return frames, finish, hits, statics


def score(frames, finish):
    if not finish:
        return -1, 0, 0
    lead = None; changes = 0
    for fr in frames[90:]:
        ci = max(fr["b"], key=lambda r: r[2])[0]
        if ci != lead:
            changes += 1; lead = ci
    win_f = min(finish.values())
    return changes, win_f / FPS, len(finish)


if __name__ == "__main__":
    best = None
    for seed in range(int(sys.argv[1]), int(sys.argv[2])):
        frames, finish, hits, statics = run(seed)
        ch, wt, nf = score(frames, finish)
        print(seed, "changes", ch, "win_t", round(wt, 1), "finished", nf, "hits", len(hits), flush=True)
