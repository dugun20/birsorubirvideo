"""Build a Grumpo & Nibbo episode end to end.

usage:
  python3 kit/build.py preview episodes/epNN_slug.py t1 t2 t3 ...   -> out/preview-NN.png (contact sheet of given times)
  python3 kit/build.py full    episodes/epNN_slug.py NN             -> out/grumpo-NN.mp4 + out/check-NN.png

An episode module must define: W, H, FPS, DUR, frame(t)->svg string, build_sfx() filling EV list (list of dicts t/name/gain/pitch).
"""
import sys, os, json, subprocess, importlib.util, shutil, tempfile
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)


def load(path):
    path = os.path.abspath(path)
    sys.path.insert(0, os.path.dirname(path))
    spec = importlib.util.spec_from_file_location("episode", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


EP = None
TMP = None


def _init(path, tmp):
    global EP, TMP
    EP = load(path)
    TMP = tmp


def _work(i):
    p = f"{TMP}/f{i:05d}.png"
    if os.path.exists(p):
        return
    sp = f"{TMP}/s{i}.svg"
    open(sp, "w").write(EP.frame(i / EP.FPS))
    subprocess.run(["rsvg-convert", "-w", str(EP.W), "-h", str(EP.H), sp, "-o", p], check=True)
    os.remove(sp)


def preview(path, times, tag):
    ep = load(path)
    tmp = tempfile.mkdtemp()
    for k, t in enumerate(times):
        open(f"{tmp}/s.svg", "w").write(ep.frame(t))
        subprocess.run(["rsvg-convert", "-w", "270", "-h", "480", f"{tmp}/s.svg", "-o", f"{tmp}/p{k:03d}.png"], check=True)
    cols = min(6, len(times))
    rows = (len(times) + cols - 1) // cols
    out = os.path.join(ROOT, "out", f"preview-{tag}.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{tmp}/p%03d.png", "-vf", f"tile={cols}x{rows}", "-frames:v", "1", out], check=True)
    print(out)


def full(path, no):
    ep = load(path)
    ep.EV.clear()
    ep.build_sfx()
    tmp = tempfile.mkdtemp()
    ev = f"{tmp}/ev.json"
    json.dump(ep.EV, open(ev, "w"))
    wav = f"{tmp}/sfx.wav"
    subprocess.run([sys.executable, os.path.join(HERE, "sfx.py"), ev, wav, str(ep.DUR)], check=True)
    n = int(round(ep.DUR * ep.FPS))
    with Pool(os.cpu_count() or 2, initializer=_init, initargs=(path, tmp)) as pl:
        for k, _ in enumerate(pl.imap_unordered(_work, range(n), chunksize=8)):
            if k % 300 == 0:
                print("frames", k, "/", n, flush=True)
    out = os.path.join(ROOT, "out", f"grumpo-{no}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(ep.FPS), "-i", f"{tmp}/f%05d.png", "-i", wav,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-r", str(ep.FPS),
                    "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], check=True)
    chk = os.path.join(ROOT, "out", f"check-{no}.png")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, "-vf", f"fps={min(1.0, 12.0/ep.DUR):.4f},scale=216:-1,tile=6x2",
                    "-frames:v", "1", chk], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print(out, os.path.getsize(out), "bytes")
    print(chk)


if __name__ == "__main__":
    mode, path = sys.argv[1], sys.argv[2]
    if mode == "preview":
        tag = os.path.basename(path).split("_")[0]
        preview(path, [float(x) for x in sys.argv[3:]], tag)
    else:
        full(path, sys.argv[3])
