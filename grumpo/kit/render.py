import sys, os, subprocess, importlib
from multiprocessing import Pool

mod = importlib.import_module(sys.argv[1])
outdir = sys.argv[2]
os.makedirs(outdir, exist_ok=True)
N = int(mod.DUR * mod.FPS)


def work(i):
    p = f"{outdir}/f{i:05d}.png"
    if os.path.exists(p):
        return
    svg = mod.frame(i / mod.FPS)
    sp = f"{outdir}/tmp{i}.svg"
    open(sp, "w").write(svg)
    subprocess.run(["rsvg-convert", "-w", str(mod.W), "-h", str(mod.H), sp, "-o", p], check=True)
    os.remove(sp)


if __name__ == "__main__":
    with Pool(2) as pl:
        for k, _ in enumerate(pl.imap_unordered(work, range(N), chunksize=8)):
            if k % 150 == 0:
                print(k, flush=True)
    print("done")
