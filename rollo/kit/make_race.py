"""Rollo Racing – one-command race maker.
  python3 make_race.py run NN      -> out/rollo-NN.mp4, out/check-NN.png, out/rollo-NN.json (title/desc/tags/comment)
  python3 make_race.py log NN      -> append out/rollo-NN.json summary to log/races.json (call after the queue row is added)
Variety rules: theme differs from last 2 races, part set never repeats one of the last 15, winner differs from
last 2 winners, format alternates (classic ~65%, country ~35%, never 3 country in a row).
"""
import sys, os, json, random, subprocess, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import course as C, render as RD, audio as AU

ROOT = os.path.join(HERE, "..")
OUTD = os.path.join(ROOT, "out"); LOG = os.path.join(ROOT, "log", "races.json")
os.makedirs(OUTD, exist_ok=True)


def load_log():
    return json.load(open(LOG)) if os.path.exists(LOG) else []


def plan(nn, log, rng):
    last = log[-15:]
    themes = [t for t in RD.THEMES if t not in [x["theme"] for x in log[-2:]]]
    theme = rng.choice(themes)
    fmts = [x["fmt"] for x in log[-2:]]
    fmt = "country" if (rng.random() < 0.35 and fmts != ["country", "country"]) else "classic"
    fmt = os.environ.get("FORCE_FMT", fmt)
    if fmt == "classic":
        names = [n for n, _ in RD.CLASSIC]; cols = [RD.hx(c) for _, c in RD.CLASSIC]; flags = [None] * 8
        header, ask = "Pick your color!", "Did you pick {}?"
    else:
        pick = rng.sample(list(RD.COUNTRIES), 8)
        names = pick; cols = [RD.hx(RD.COUNTRIES[p][0]) for p in pick]; flags = [RD.COUNTRIES[p][1] for p in pick]
        header, ask = "Pick your country!", "Did you pick {}?"
    used = [tuple(sorted(x["parts"])) for x in last]
    names_all = list(C.PARTS)
    while True:
        k = rng.choice([4, 4, 5])
        parts = rng.sample(names_all, k)
        if tuple(sorted(parts)) not in used:
            break
    return dict(nn=nn, theme=theme, fmt=fmt, names=names, colors=cols, flags=flags, header=header, ask=ask, parts=parts)


def find_race(p, log, rng):
    bad_winners = [x["winner"] for x in log[-2:]]
    for attempt in range(6):
        layout = rng.randrange(10 ** 6)
        best = None
        for seed in range(30):
            r = C.run(p["parts"], layout, seed)
            ok, info = C.score(r)
            if not ok:
                continue
            f = r["finish"]; first = min(x for x in f if x is not None)
            w = p["names"][f.index(first)]
            if w in bad_winners:
                continue
            sc = info["changes"] - 4 * info["gap"]
            if best is None or sc > best[0]:
                best = (sc, layout, seed, info, w, r)
            if info["changes"] >= 8 and info["gap"] < 0.8:
                break
        if best:
            return best
        # this part set is hard – swap one part and retry
        p["parts"][rng.randrange(len(p["parts"]))] = rng.choice([x for x in C.PARTS if x not in p["parts"]])
    raise RuntimeError("no good race found")


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
    tag = f"rollo-{nn:02d}"
    mp4 = os.path.join(OUTD, tag + ".mp4")
    meta = dict(theme=p["theme"], names=p["names"], colors=p["colors"], flags=p["flags"], header=p["header"], ask=p["ask"])
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
    AU.build(r, wav)
    tmp = mp4 + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", vid, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, mp4); os.remove(vid); os.remove(wav)
    tpl, title, desc, tags, comment = texts(p, rng, log)
    out = dict(nn=nn, file=f"rollo/out/{tag}.mp4", title=title, title_tpl=tpl, description=desc, tags=tags, comment=comment,
               theme=p["theme"], fmt=p["fmt"], parts=p["parts"], names=p["names"], winner=w, layout=layout, seed=seed,
               first=info["first"], gap=info["gap"], changes=info["changes"], dur=round(res["dur"], 1),
               mb=round(os.path.getsize(mp4) / 1e6, 1),
               summary=f"{p['fmt']} race, theme {p['theme']}, parts {'+'.join(p['parts'])}; {w} wins by {info['gap']}s")
    json.dump(out, open(os.path.join(OUTD, tag + ".json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out, ensure_ascii=False, indent=1))


def add_log(nn):
    d = json.load(open(os.path.join(OUTD, f"rollo-{nn:02d}.json")))
    log = load_log()
    log.append({k: d[k] for k in ("nn", "title", "title_tpl", "theme", "fmt", "parts", "winner", "layout", "seed", "first", "gap")})
    json.dump(log, open(LOG, "w"), indent=1, ensure_ascii=False)
    print("logged", nn, "total", len(log))


if __name__ == "__main__":
    cmd, nn = sys.argv[1], int(sys.argv[2])
    run(nn) if cmd == "run" else add_log(nn)
