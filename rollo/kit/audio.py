"""Rollo Racing sound – APPROVED by Cihan (20 Nov 2026), don't change without asking:
- pegs / bumpers / trampoline pads: the peg note from his sample race_ornek.mp4, re-pitched to C-major pentatonic by x position
- spinners / sliders: sample's spinner hit;  GO + win: sample's sounds
- ramp landings: short soft 110 Hz thud (60 ms) + light reverb, quiet, max 1 per 0.14 s ("ses_marimba" landing sound)
- no music
"""
import os, wave, numpy as np
import course as C

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.join(HERE, "..", "assets", "sfx")


def load(name):
    w = wave.open(os.path.join(SFX, name)); x = np.frombuffer(w.readframes(w.getnframes()), np.int16) / 32768
    return x / np.abs(x).max()


PEG, SPIN, GO, WIN = load("peg_787hz.wav"), load("spin_900hz.wav"), load("go.wav"), load("win.wav")
PEG_F = 787.0
SCALE = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5, 1174.66, 1318.5]


def repitch(s, ratio):
    n = int(len(s) / ratio)
    return np.interp(np.arange(n) * ratio, np.arange(len(s)), s)


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def thud():
    n = int(SR * 0.06); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 110 * t) * env(n, 0.003, 0.018)


def puf():
    """very soft cushioned landing: short low-passed air puff + faint 240 Hz body (no boomy 'tok')"""
    n = int(SR * 0.05); t = np.arange(n) / SR
    noise = np.random.default_rng(int(1e6 * t.sum()) % 997).normal(0, 1, n)
    lp = np.convolve(noise, np.ones(12) / 12, mode="same")
    return (0.7 * lp / (np.abs(lp).max() + 1e-9) + 0.35 * np.sin(2 * np.pi * 240 * t)) * env(n, 0.002, 0.012)


def beep(f, d, bright=0.0):
    n = int(SR * d); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) + bright * np.sin(6 * np.pi * f * t)
    return s * np.minimum(1, t / 0.004) * np.minimum(1, (d - t) / 0.04)


def start_signal():
    """race start: 2 short countdown beeps while the marbles fill the box, then a bright GO chord"""
    out = np.zeros(int(SR * 1.3))
    for i, t0 in enumerate((0.0, 0.42)):
        b = beep(880, 0.13); k = int(t0 * SR); out[k:k + len(b)] += b * 0.5
    g = beep(1760, 0.45, 0.25) + 0.6 * beep(1318.5, 0.45); k = int(0.84 * SR)
    g *= np.exp(-np.arange(len(g)) / SR / 0.28)
    out[k:k + len(g)] += g[:len(out) - k] * 0.8
    return out


LAND = "puf"     # "puf" | "thud" | "none"


THUD_GAIN = 1 / 0.2805   # level-matched to the approved test mix


def whistle(d=0.55):
    """referee whistle (football world GO)"""
    n = int(SR * d); t = np.arange(n) / SR
    f = 2900 + 180 * np.sign(np.sin(2 * np.pi * 28 * t))          # pea trill
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.25 * np.random.default_rng(1).normal(0, 1, n)
    env_ = np.minimum(1, t / 0.01) * np.minimum(1, (d - t) / 0.06)
    return s * env_ * 0.5


def crowd(d=2.2):
    """soft stadium cheer (football world goal)"""
    rng = np.random.default_rng(2)
    n = int(SR * d); t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    k = np.ones(18) / 18; lo = np.convolve(x, k, mode="same"); band = lo - np.convolve(lo, np.ones(160) / 160, mode="same")
    env_ = np.minimum(1, t / 0.25) * np.exp(-np.maximum(0, t - 0.6) / 0.7)
    return band / np.abs(band).max() * env_


def build(r, out_wav, world="pastel"):
    hits, finish = r["hits"], r["finish"]
    dur = len(r["frames"]) / C.FPS + 0.8
    L = np.zeros(int(SR * dur)); R = np.zeros_like(L); LT = np.zeros_like(L); RT = np.zeros_like(L)

    def add(t, s, v, pan=0.0, tgt=None):
        A, B = tgt or (L, R)
        i = int(t * SR)
        if i >= len(A):
            return
        m = min(len(s), len(A) - i)
        A[i:i + m] += s[:m] * v * np.sqrt((1 - pan) / 2); B[i:i + m] += s[:m] * v * np.sqrt((1 + pan) / 2)
    go = C.GO_T
    lp = lr = ls = lb = -1
    for (t, k, s, x, y) in hits:
        if t < go and k in ("rod", "peg") and y < 700:    # marbles landing in the start box: bright pentatonic clinks
            if t - lb < 0.035:
                continue
            lb = t
            idx = max(0, min(7, int((x - 500) / 400 * 7 + 0.5)))
            add(t, repitch(PEG, SCALE[idx] / PEG_F), 0.05 + 0.08 * s, (x - 700) / 1400)
            continue
        if t < go and k == "ball":     # marbles settling in the start box – soft ticks so the intro isn't silent
            if t - lb < 0.05:
                continue
            lb = t
            add(t, repitch(PEG, (SCALE[5] + 200 * ((x * 7) % 3)) / PEG_F), 0.03 + 0.05 * s, (x - 700) / 1400)
            continue
        pan = max(-0.6, min(0.6, (x - 700) / 700))
        if k in ("peg", "bumper", "pad"):
            if t - lp < 0.07:
                continue
            lp = t
            idx = max(0, min(7, int((x - C.L) / (C.R - C.L) * 7 + 0.5)))
            f = SCALE[idx] * (0.5 if k == "bumper" else 1)
            add(t, repitch(PEG, f / PEG_F), (0.05 + 0.06 * s) * (1.3 if k != "peg" else 1), pan)
        elif k == "spin":
            if t - ls < 0.12:
                continue
            ls = t; add(t, SPIN, 0.10 + 0.08 * s, pan)
        elif k == "rod":
            if t - lr < 0.14 or s < (0.12 if t < go else 0.25):
                continue
            lr = t
            if LAND != "none":
                add(t, puf() if LAND == "puf" else thud(), (0.03 + 0.05 * s) if LAND == "puf" else (0.05 + 0.08 * s),
                    pan * 0.5, (LT, RT))
    fin = sorted(x for x in finish if x is not None)
    add(go - 0.84, start_signal(), 0.45)
    if world == "football":
        add(go - 0.02, whistle(), 0.3)
        add(fin[0] - 0.05, crowd(), 0.22)
        add(fin[0] - 0.05, WIN, 0.35)
    else:
        add(fin[0] - 0.05, WIN, 0.45)
    for ft in fin[1:]:
        add(ft, repitch(PEG, SCALE[5] / PEG_F), 0.08)
    rng = np.random.default_rng(5)
    irn = int(SR * 0.9); ir = rng.normal(0, 1, irn) * np.exp(-np.arange(irn) / SR / 0.25); ir /= np.abs(ir).sum() / 6

    def rev(v):
        nf = 1 << int(np.ceil(np.log2(len(v) + irn)))
        return np.fft.irfft(np.fft.rfft(v, nf) * np.fft.rfft(ir, nf), nf)[:len(v)]
    LT = LT + 0.22 * rev(LT); RT = RT + 0.22 * rev(RT)
    pk = max(np.abs(L).max(), np.abs(R).max())
    L = L + LT * THUD_GAIN * pk; R = R + RT * THUD_GAIN * pk
    st = np.stack([L, R], 1); st = st / np.abs(st).max() * 0.7
    o = wave.open(out_wav, "wb"); o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
    o.writeframes((st * 32767).astype(np.int16).tobytes()); o.close()
