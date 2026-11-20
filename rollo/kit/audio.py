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


THUD_GAIN = 1 / 0.2805   # level-matched to the approved test mix


def build(r, out_wav):
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
    lp = lr = ls = -1
    for (t, k, s, x, y) in hits:
        if t < go:
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
            if t - lr < 0.14 or s < 0.25:
                continue
            lr = t; add(t, thud(), 0.05 + 0.08 * s, pan * 0.5, (LT, RT))
    add(go - 0.01, GO, 0.6)
    fin = sorted(x for x in finish if x is not None)
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
