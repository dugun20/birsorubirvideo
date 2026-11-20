"""Rollo Racing – one-command race maker.
  python3 make_race.py run NN      -> out/rollo-NN.mp4, out/check-NN.png, out/rollo-NN.json (title/desc/tags/comment)
  python3 make_race.py log NN      -> append out/rollo-NN.json summary to log/races.json (call after the queue row is added)
Variety rules: theme differs from last 2 races, part set never repeats one of the last 15, winner differs from
last 2 winners, format alternates (classic ~65%, country ~35%, never 3 country in a row).
"""
import sys, os, json, random, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import course as C, render as RD, audio as AU, worlds as WD

ROOT = os.path.join(HERE, "..")
OUTD = os.path.join(ROOT, "out"); LOG = os.path.join(ROOT, "log", "races.json")
os.makedirs(OUTD, exist_ok=True)


def load_log():
    return json.load(open(LOG)) if os.path.exists(LOG) else []


def plan(nn, log, rng):
    last = log[-15:]
    fmts = [x["fmt"] for x in log[-2:]]
    fmt = "country" if (rng.random() < 0.35 and fmts != ["country", "country"]) else "classic"
    fmt = os.environ.get("FORCE_FMT", fmt)
    recent_worlds = [x.get("world", "pastel") for x in log[-2:]]
    if fmt == "country":
        world = "football" if (rng.random() < 0.8 and "football" not in recent_worlds[-1:]) else \
            rng.choice([w for w in WD.WORLDS if w not in recent_worlds and w != "football"])
    else:
        world = rng.choice([w for w in WD.WORLDS if w not in recent_worlds and w != "football"])
    world = os.environ.get("FORCE_WORLD", world)
    palette = rng.choice([pname for pname in WD.PASTELS if pname not in [x.get("palette") for x in log[-3:]]]) if world == "pastel" else None
    theme = world + (":" + palette if palette else "")
    start = rng.choice(["v", "shelf"])
    if fmt == "classic":
        names = [n for n, _ in RD.CLASSIC]; cols = [RD.hx(c) for _, c in RD.CLASSIC]; flags = [None] * 8
        header, ask = "Pick your color!", "Did you pick {}?"
    else:
        while True:
            pick = rng.sample(list(RD.COUNTRIES), 8)
            if not ({"ITALY", "MEXICO"} <= set(pick)):      # near-identical flags on a small marble
                break
        names = pick; cols = [RD.hx(RD.COUNTRIES[p][0]) for p in pick]; flags = [RD.COUNTRIES[p][1] for p in pick]
        header, ask = "Pick your country!", "Did you pick {}?"
    used = [tuple(sorted(x["parts"])) for x in last]
    names_all = list(C.PARTS)
    while True:
        k = rng.choice([8, 8, 9])
        weights = {n: (0.12 if n == "zigzag" else 1.0) for n in names_all}
        parts = []
        while len(parts) < k:
            n = rng.choices(names_all, [weights[x] for x in names_all])[0]
            if n not in parts:
                parts.append(n)
        if tuple(sorted(parts)) not in used:
            break
    return dict(nn=nn, theme=theme, world=world, palette=palette, start=start, fmt=fmt, names=names, colors=cols, flags=flags,
                header=header, ask=ask, parts=parts)


def find_race(p, log, rng, tmin=11.0, tmax=19.0):
    """Adapt the course length to the target race time, then pick the most exciting seed."""
    bad_winners = [x["winner"] for x in log[-2:]]
    action = [x for x in C.PARTS if x != "zigzag"]
    for attempt in range(10):
        layout = rng.randrange(10 ** 6)
        firsts, cands = [], []
        for seed in range(14):
            r = C.run(p["parts"], layout, seed, start=p["start"], connectors=False)
            f = [x for x in r["finish"] if x is not None]
            if f:
                firsts.append(min(f))
            ok, info = C.score(r, tmin, tmax)
            if not ok:
                continue
            w = p["names"][r["finish"].index(min(f))]
            if w in bad_winners:
                continue
            cands.append((info["changes"] - 4 * info["gap"], layout, seed, info, w, r))
        if cands:
            return max(cands, key=lambda c: c[0])
        med = sorted(firsts)[len(firsts) // 2] if firsts else 0
        if med and med < tmin:            # too fast -> longer course
            p["parts"].insert(rng.randrange(1, len(p["parts"]) + 1),
                              rng.choice([x for x in action if x not in p["parts"]] or action))
        elif med > tmax and len(p["parts"]) > 3:
            p["parts"].pop(rng.randrange(len(p["parts"])))
        print(f"  attempt {attempt}: median winner {med:.1f}s -> parts {p['parts']}", file=sys.stderr)
    raise RuntimeError("no good race found")


def slowmo(r, info, factor=2.5):
    """Photo-finish slow motion: last ~1.2 s before the winner crosses plays at 1/factor speed
    (only when the finish is close). Frames are interpolated; hit/finish times are remapped."""
    fps = C.FPS
    first = info["first"]
    if info["gap"] > 0.8:
        return r, None
    a, b = first - 1.2, first + 0.35
    ia, ib = int(a * fps), int(b * fps)
    fr = r["frames"]
    if ia < 1 or ib >= len(fr):
        return r, None
    out = fr[:ia]
    n_new = int((ib - ia) * factor)
    for j in range(n_new):
        x = ia + j / factor; i0 = int(x); w = x - i0; i1 = min(i0 + 1, len(fr) - 1)
        f0, f1 = fr[i0], fr[i1]
        out.append({"b": [tuple(p0[k] + (p1[k] - p0[k]) * w for k in range(3)) for p0, p1 in zip(f0["b"], f1["b"])],
                    "k": [tuple(p0[k] + (p1[k] - p0[k]) * w for k in range(3)) for p0, p1 in zip(f0["k"], f1["k"])]})
    out += fr[ib:]

    def tm(t):
        if t <= a:
            return t
        if t <= b:
            return a + (t - a) * factor
        return t + (b - a) * (factor - 1)
    r2 = dict(r)
    r2["frames"] = out
    r2["finish"] = [tm(x) if x is not None else None for x in r["finish"]]
    r2["hits"] = [(tm(h[0]),) + tuple(h[1:]) for h in r["hits"]]
    return r2, (tm(a), tm(b))


TITLES_CLASSIC = [
    "Pick Your Color! WHO WINS? 🏆 Marble Race #{nn}",
    "Which Color Wins This Marble Race? 🏁 #{nn}",
    "Only 1 Marble Can Win! Pick Your Color 🏆 #{nn}",
    "Satisfying Marble Race – Who Wins? 🔴🟢🔵 #{nn}",
    "Pick a Marble Before the Race Starts! 🏁 #{nn}",
    "Can Your Color Win? Marble Race #{nn} 🏆",
]
TITLES_COUNTRY = [
    "Country Marble Race! Pick Your Country 🌍 #{nn}",
    "Which Country Wins? 🌍 Marble Race #{nn}",
    "Pick Your Country! WHO WINS? 🏆 #{nn}",
    "Country Ball Race – Who Wins? 🌍 #{nn}",
]


def texts(p, rng, log):
    used = [x.get("title_tpl") for x in log[-4:]]
    pool = TITLES_CLASSIC if p["fmt"] == "classic" else TITLES_COUNTRY
    tpl = rng.choice([t for t in pool if t not in used] or pool)
    title = tpl.format(nn=p["nn"])
    if p["fmt"] == "classic":
        desc = ("Pick your color before the race starts! 🏁\n8 marbles, 1 winner. Which one did you choose? 👇\n"
                "Comment your color and subscribe for new races every day! 🏆\n\n#marblerace #whowins #shorts")
        comment = "Which color did you pick? 👇"
        extra = "color race, pick your color"
    else:
        desc = ("Pick your country before the race starts! 🌍\n8 countries, 1 winner. Which one did you choose? 👇\n"
                "Comment your country and subscribe for new races every day! 🏆\n\n#marblerace #countryballs #shorts")
        comment = "Which country did you pick? 🌍👇"
        extra = "country race, country marble race, countryballs, " + ", ".join(n.lower() for n in p["names"][:4])
    tags = ("marble race, marble racing, who wins, rollo racing, marble run, satisfying, oddly satisfying, ball race, "
            "marble race shorts, race simulation, guess who wins, satisfying video, " + extra)
    return tpl, title, desc, tags, comment


def run(nn):
    log = load_log()
    rng = random.Random(int(time.time()) ^ (nn * 7919))
    p = plan(nn, log, rng)
    sc, layout, seed, info, w, r = find_race(p, log, rng)
    r, slow = r, None   # slow-motion disabled: Cihan saw it as an unnatural slowdown
    if slow:
        info = dict(info, first=round(min(x for x in r["finish"] if x is not None), 2))
    tag = f"rollo-{nn:02d}"
    mp4 = os.path.join(OUTD, tag + ".mp4")
    meta = dict(slow=slow, world=p["world"], palette=p["palette"], names=p["names"], colors=p["colors"], flags=p["flags"], header=p["header"], ask=p["ask"])
    # check sheet stills first
    ft = info["first"]
    stills = [0.8, 2.0, ft * 0.3, ft * 0.5, ft * 0.7, ft * 0.9, ft + 0.6, ft + 3.0]
    res = RD.render(r, meta, os.path.join(OUTD, tag), stills=stills)
    from PIL import Image
    ims = [Image.open(x).convert("RGB").resize((360, 640)) for x in res["stills"]]
    sheet = Image.new("RGB", (360 * 4, 640 * 2))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 4) * 360, (i // 4) * 640))
    sheet.save(os.path.join(OUTD, f"check-{nn:02d}.png"))
    for x in res["stills"]:
        os.remove(x)
    vid = os.path.join(OUTD, tag + ".video.mp4")
    RD.render(r, meta, vid)
    wav = os.path.join(OUTD, tag + ".wav")
    AU.build(r, wav, p["world"])
    tmp = mp4 + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, mp4); os.remove(vid); os.remove(wav)
    tpl, title, desc, tags, comment = texts(p, rng, log)
    out = dict(nn=nn, file=f"rollo/out/{tag}.mp4", title=title, title_tpl=tpl, description=desc, tags=tags, comment=comment,
               theme=p["theme"], world=p["world"], palette=p["palette"], start=p["start"], fmt=p["fmt"], parts=p["parts"], names=p["names"], winner=w, layout=layout, seed=seed,
               first=info["first"], gap=info["gap"], changes=info["changes"], dur=round(res["dur"], 1),
               mb=round(os.path.getsize(mp4) / 1e6, 1),
               summary=f"{p['fmt']} race, world {p['theme']}, start {p['start']}, parts {'+'.join(p['parts'])}; {w} wins by {info['gap']}s")
    json.dump(out, open(os.path.join(OUTD, tag + ".json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out, ensure_ascii=False, indent=1))


def add_log(nn):
    d = json.load(open(os.path.join(OUTD, f"rollo-{nn:02d}.json")))
    log = load_log()
    log.append({k: d.get(k) for k in ("nn", "title", "title_tpl", "theme", "world", "palette", "start", "fmt", "parts", "winner",
                                      "layout", "seed", "first", "gap")})
    json.dump(log, open(LOG, "w"), indent=1, ensure_ascii=False)
    print("logged", nn, "total", len(log))


if __name__ == "__main__":
    cmd, nn = sys.argv[1], int(sys.argv[2])
    run(nn) if cmd == "run" else add_log(nn)
