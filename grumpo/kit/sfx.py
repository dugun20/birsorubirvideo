"""Cartoon SFX synthesizer + mixer. Usage: python3 sfx.py events.json out.wav duration"""
import json, sys
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100
rng = np.random.default_rng(3)


def T(d):
    return np.arange(int(SR * d)) / SR


def env(n, a=0.005, r=None, curve=3.0):
    t = np.arange(n) / SR
    d = n / SR
    e = np.minimum(1, t / max(a, 1e-4))
    rr = (1 - t / d) ** curve
    return e * rr


def sweep(f0, f1, d, kind="exp", wave="sine"):
    t = T(d)
    if kind == "exp":
        f = f0 * (f1 / f0) ** (t / d)
    else:
        f = f0 + (f1 - f0) * t / d
    ph = 2 * np.pi * np.cumsum(f) / SR
    if wave == "sine":
        return np.sin(ph)
    if wave == "tri":
        return 2 / np.pi * np.arcsin(np.sin(ph))
    if wave == "sq":
        return np.tanh(4 * np.sin(ph))
    if wave == "saw":
        return 2 * ((ph / (2 * np.pi)) % 1) - 1


def noise(d):
    return rng.standard_normal(int(SR * d))


def filt(x, lo=None, hi=None, order=2):
    if lo and hi:
        sos = butter(order, [lo, hi], "bandpass", fs=SR, output="sos")
    elif lo:
        sos = butter(order, lo, "highpass", fs=SR, output="sos")
    else:
        sos = butter(order, hi, "lowpass", fs=SR, output="sos")
    return sosfilt(sos, x)


def norm(x, peak=0.9):
    m = np.max(np.abs(x)) + 1e-9
    return x / m * peak


def cat(*xs):
    return np.concatenate(xs)


# ------------------------------------------------------------------ sounds
def s_pop():
    d = 0.09
    return norm(sweep(900, 250, d) * env(int(SR * d), 0.001, curve=2) + 0.3 * filt(noise(d), 1500, 6000) * env(int(SR * d), 0.001, curve=8))


def s_ding():
    t = T(0.9)
    x = sum(a * np.sin(2 * np.pi * f * t) for f, a in [(1568, 1), (3136, 0.4), (4700, 0.2), (2350, 0.3)])
    return norm(x * np.exp(-t * 5) * np.minimum(1, t / 0.003)) * 0.8


def s_slurp():
    d = 0.6
    t = T(d)
    n = filt(noise(d), 600, 3500)
    am = 0.5 + 0.5 * np.sin(2 * np.pi * 14 * t) ** 2
    f = filt(noise(d), 200, 900) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * t))
    x = (n * am + 0.6 * f) * env(len(t), 0.05, curve=0.8)
    end = s_pop() * 0.0
    return norm(x) * 0.7


def s_squeak():
    d = 0.16
    return norm(sweep(1400, 2600, d, wave="tri") * env(int(SR * d), 0.01, curve=1.5)) * 0.6


def s_tiptoe():
    d = 0.07
    x = sweep(1300, 700, d, wave="tri") * env(int(SR * d), 0.001, curve=4)
    x += 0.4 * filt(noise(d), 2000, 7000) * env(int(SR * d), 0.0005, curve=10)
    return norm(x) * 0.6


def s_suspense():
    d = 0.5
    t = T(d)
    x = sum(np.sin(2 * np.pi * f * t) for f in (220, 233, 330)) * np.exp(-t * 3) * np.minimum(1, t / 0.005)
    x += 0.5 * sweep(110, 108, d, wave="saw") * np.exp(-t * 4)
    return norm(filt(x, hi=2500)) * 0.7


def s_whistle_tune():
    notes = [(1175, 0.14), (1568, 0.14), (1319, 0.14), (1568, 0.22)]
    out = []
    for f, d in notes:
        t = T(d)
        vib = 1 + 0.01 * np.sin(2 * np.pi * 6 * t)
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        x = np.sin(ph) + 0.15 * filt(noise(d), 1000, 3000)
        out.append(x * env(len(t), 0.02, curve=0.5))
    return norm(cat(*out)) * 0.5


def s_whoosh():
    d = 0.32
    n = noise(d)
    t = T(d)
    out = np.zeros_like(n)
    for i, (lo, hi) in enumerate([(300, 900), (600, 1800), (1200, 3600)]):
        w = np.exp(-((t - d * (0.3 + 0.15 * i)) / (d * 0.22)) ** 2)
        out += filt(n, lo, hi) * w
    return norm(out) * 0.75


def s_thunk():
    d = 0.22
    t = T(d)
    x = np.sin(2 * np.pi * np.cumsum(180 * np.exp(-t * 12) + 70) / SR) * np.exp(-t * 18)
    x += 0.5 * filt(noise(d), 200, 1500) * np.exp(-t * 40)
    return norm(x)


def s_rise():
    d = 0.4
    return norm(sweep(300, 900, d, wave="tri") * env(int(SR * d), 0.05, curve=0.7)) * 0.5


def s_gulp():
    a = sweep(500, 260, 0.12, wave="sine") * env(int(SR * 0.12), 0.005, curve=1)
    gap = np.zeros(int(SR * 0.04))
    b = sweep(420, 180, 0.16, wave="sine") * env(int(SR * 0.16), 0.005, curve=1.5)
    return norm(cat(a, gap, b)) * 0.8


def s_bonk():
    d = 0.35
    t = T(d)
    hit = filt(noise(0.05), 300, 4000) * env(int(SR * 0.05), 0.0005, curve=6)
    body = sweep(620, 260, d, wave="tri") * np.exp(-t * 9)
    body2 = sweep(930, 390, d) * np.exp(-t * 12) * 0.5
    x = body + body2
    x[: len(hit)] += hit * 1.2
    return norm(x)


def s_slide_up():
    d = 0.7
    t = T(d)
    f = 400 * (2000 / 400) ** (t / d)
    vib = 1 + 0.02 * np.sin(2 * np.pi * 7 * t)
    x = np.sin(2 * np.pi * np.cumsum(f * vib) / SR) + 0.1 * filt(noise(d), 800, 4000)
    return norm(x * env(len(t), 0.02, curve=0.6)) * 0.55


def s_slide_down():
    return s_slide_up()[::-1].copy() * 1.0


def s_click():
    d = 0.05
    x = filt(noise(d), 2000, 9000) * env(int(SR * d), 0.0005, curve=12)
    x2 = np.zeros(int(SR * 0.06))
    return norm(cat(x, x2, x * 0.7))


def s_cool():
    t = T(0.5)
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 6) for f in (2093, 2637, 3136))
    sh = filt(noise(0.5), 4000, 12000) * np.exp(-t * 8) * 0.4
    return norm(x * np.minimum(1, t / 0.002) + sh) * 0.6


def s_boing():
    d = 0.45
    t = T(d)
    f = 180 + 260 * np.exp(-t * 6) * (1 + 0.35 * np.sin(2 * np.pi * 22 * t))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    x += 0.4 * np.sin(2 * np.pi * np.cumsum(2 * f) / SR)
    return norm(x * np.exp(-t * 6) * np.minimum(1, t / 0.003)) * 0.8


def s_zip():
    d = 0.25
    return norm(sweep(2200, 500, d, wave="tri") * env(int(SR * d), 0.003, curve=1.2) + 0.2 * filt(noise(d), 3000, 8000) * env(int(SR * d), 0.003, curve=3)) * 0.6


def s_clank():
    d = 0.5
    t = T(d)
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, a, k in [(523, 1, 8), (1247, 0.7, 10), (1873, 0.5, 14), (2970, 0.3, 18)])
    x += filt(noise(d), 1000, 6000) * np.exp(-t * 60) * 0.8
    return norm(x * np.minimum(1, t / 0.0005)) * 0.8


def s_hop():
    d = 0.12
    return norm(sweep(350, 900, d, wave="sine") * env(int(SR * d), 0.003, curve=1.5)) * 0.6


def s_plop():
    d = 0.18
    t = T(d)
    x = sweep(260, 1100, d, wave="sine") * np.exp(-t * 14) * np.minimum(1, t / 0.002)
    x += 0.3 * filt(noise(d), 800, 3000) * np.exp(-t * 30)
    return norm(x) * 0.85


def s_pipe_rattle():
    d = 1.4
    t = T(d)
    x = np.zeros(len(t))
    for k in range(18):
        st = int(rng.uniform(0, d - 0.08) * SR)
        n = int(0.06 * SR)
        tt = np.arange(n) / SR
        f = rng.uniform(300, 700)
        x[st:st + n] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 50) * rng.uniform(0.4, 1)
    x += filt(noise(d), 100, 400) * 0.25
    return norm(x * env(len(t), 0.05, curve=0.5)) * 0.6


def s_bubbles():
    d = 1.0
    x = np.zeros(int(SR * d))
    for k in range(9):
        st = int(rng.uniform(0, d - 0.08) * SR)
        b = s_plop() * rng.uniform(0.3, 0.8)
        b = b[: len(x) - st]
        x[st:st + len(b)] += b
    return norm(x) * 0.6


def s_alert():
    a = sweep(880, 880, 0.08, wave="sq") * env(int(SR * 0.08), 0.002, curve=0.5)
    b = sweep(1320, 1320, 0.14, wave="sq") * env(int(SR * 0.14), 0.002, curve=1)
    return norm(filt(cat(a, b), hi=4000)) * 0.45


def s_squish():
    d = 0.25
    t = T(d)
    x = filt(noise(d), 200, 1200) * np.exp(-t * 10) * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * t))
    x += sweep(300, 160, d) * np.exp(-t * 12) * 0.6
    return norm(x) * 0.7


def s_rumble():
    d = 2.2
    t = T(d)
    x = filt(noise(d), 30, 160, order=3) * (0.7 + 0.3 * np.sin(2 * np.pi * 7 * t))
    x += 0.4 * filt(noise(d), 160, 500) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t))
    return norm(x * env(len(t), 0.4, curve=0.6))


def s_laugh():
    out = []
    for i in range(5):
        d = 0.11
        t = T(d)
        f = 210 - i * 8
        x = sweep(f * 1.3, f, d, wave="saw")
        x = filt(x, 300, 1800)
        out.append(x * env(len(t), 0.01, curve=1.2))
        out.append(np.zeros(int(SR * 0.05)))
    return norm(cat(*out)) * 0.7


def s_cork_pop():
    d = 0.14
    t = T(d)
    x = filt(noise(0.02), 500, 5000)
    body = sweep(700, 1500, d) * np.exp(-t * 25)
    body[: len(x)] += x * 1.5
    return norm(body) * 0.85


def s_thud():
    d = 0.35
    t = T(d)
    x = np.sin(2 * np.pi * np.cumsum(55 + 90 * np.exp(-t * 20)) / SR) * np.exp(-t * 9)
    x += 0.5 * filt(noise(d), 80, 600) * np.exp(-t * 25)
    return norm(x)


def s_gasp():
    d = 0.35
    t = T(d)
    x = filt(noise(d), 700, 2600) * env(len(t), 0.02, curve=1.5)
    x += 0.4 * sweep(500, 800, d, wave="saw") * env(len(t), 0.02, curve=2)
    return norm(filt(x, hi=3500)) * 0.6


def s_cheer():
    d = 1.4
    x = np.zeros(int(SR * d))
    for k in range(26):
        st = int(rng.uniform(0, d - 0.3) * SR)
        dd = rng.uniform(0.12, 0.28)
        f0 = rng.uniform(700, 1300)
        y = sweep(f0, f0 * rng.uniform(1.2, 1.7), dd, wave="tri") * env(int(SR * dd), 0.01, curve=1)
        y = y[: len(x) - st]
        x[st:st + len(y)] += y * rng.uniform(0.3, 0.8)
    return norm(x * env(len(x), 0.05, curve=0.7)) * 0.6


def s_splash():
    d = 1.6
    t = T(d)
    x = filt(noise(d), 300, 6000) * np.exp(-t * 3.2) * np.minimum(1, t / 0.01)
    x += 1.2 * filt(noise(d), 60, 300) * np.exp(-t * 6)
    drops = np.zeros(len(t))
    for k in range(20):
        st = int(rng.uniform(0.15, 1.2) * SR)
        b = s_plop() * rng.uniform(0.15, 0.45)
        b = b[: len(t) - st]
        drops[st:st + len(b)] += b
    return norm(x + drops)


def s_grumble():
    d = 1.1
    t = T(d)
    f = 95 + 15 * np.sin(2 * np.pi * 3 * t)
    x = sweep(1, 1, d)  # placeholder
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
    x = filt(saw, 80, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t))
    x += 0.3 * filt(noise(d), 100, 500)
    return norm(x * env(len(t), 0.05, curve=0.6)) * 0.9


def s_zoom():
    d = 0.3
    n = filt(noise(d), 500, 5000)
    t = T(d)
    return norm(n * (t / d) ** 2 * np.minimum(1, (d - t) / 0.02)) * 0.6


def s_steam():
    d = 1.6
    t = T(d)
    x = filt(noise(d), 2500, 10000) * env(len(t), 0.05, curve=0.8)
    w = np.sin(2 * np.pi * np.cumsum(1900 + 300 * np.sin(2 * np.pi * 4 * t)) / SR) * 0.35 * env(len(t), 0.2, curve=1)
    return norm(x + w) * 0.7


def s_balloon():
    d = 0.5
    t = T(d)
    f = 520 + 160 * np.sin(2 * np.pi * 3 * t) + 60 * np.sin(2 * np.pi * 23 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 17 * t) ** 2)
    return norm(filt(x, 300, 3000) * env(len(t), 0.05, curve=1)) * 0.5


def s_shaker():
    d = 0.75
    x = np.zeros(int(SR * d))
    for k in range(14):
        st = int(k * 0.05 * SR)
        n = int(0.04 * SR)
        y = filt(noise(0.04), 3000, 10000) * env(n, 0.002, curve=3)
        x[st:st + n] += y * (0.6 + 0.4 * (k % 2))
    return norm(x) * 0.7


def s_inhale():
    d = 0.28
    t = T(d)
    x = filt(noise(d), 800, 3000) * (t / d) ** 1.5
    x += 0.5 * sweep(300, 520, d, wave="saw") * (t / d) ** 2
    return norm(filt(x, hi=3500) * np.minimum(1, (d - t) / 0.02)) * 0.6


def s_achoo():
    a = s_inhale()[: int(SR * 0.12)] * 0.5
    d = 0.45
    t = T(d)
    burst = filt(noise(d), 500, 5000) * np.exp(-t * 7) * np.minimum(1, t / 0.004)
    vox = sweep(620, 260, d, wave="saw") * np.exp(-t * 6)
    vox = filt(vox, 200, 2500)
    return norm(cat(a, burst + 0.7 * vox)) * 0.95


def s_dig():
    d = 1.6
    x = np.zeros(int(SR * d))
    for k in range(30):
        st = int(rng.uniform(0, d - 0.06) * SR)
        n = int(rng.uniform(0.03, 0.06) * SR)
        y = filt(rng.standard_normal(n), 300, 2500) * env(n, 0.002, curve=2)
        x[st:st + n] += y * rng.uniform(0.4, 1)
    return norm(x * env(len(x), 0.05, curve=0.4)) * 0.6


def s_creak():
    d = 0.6
    t = T(d)
    f = 140 + 60 * (t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sign(np.sin(ph)) * (np.sin(2 * np.pi * 35 * t) > 0)
    return norm(filt(x, 200, 2500) * env(len(t), 0.05, curve=0.6)) * 0.5


def s_splat():
    d = 0.7
    t = T(d)
    x = filt(noise(d), 150, 2500) * np.exp(-t * 7) * np.minimum(1, t / 0.003)
    x += 0.8 * np.sin(2 * np.pi * np.cumsum(90 + 200 * np.exp(-t * 25)) / SR) * np.exp(-t * 10)
    sq = filt(noise(d), 1000, 4000) * np.exp(-((t - 0.15) / 0.08) ** 2) * 0.5
    return norm(x + sq)


def s_munch():
    d = 1.4
    x = np.zeros(int(SR * d))
    for k in range(10):
        st = int((k * 0.13 + rng.uniform(0, 0.03)) * SR)
        n = int(0.07 * SR)
        y = filt(noise(0.07), 600, 3500) * env(n, 0.003, curve=2) + 0.5 * sweep(260, 180, 0.07) * env(n, 0.003, curve=2)
        x[st:st + n] += y[: len(x) - st]
    return norm(x) * 0.6


def s_crash_bush():
    d = 0.8
    t = T(d)
    x = filt(noise(d), 1500, 8000) * np.exp(-t * 6) * (0.6 + 0.4 * np.sin(2 * np.pi * 37 * t) ** 2)
    x += 0.6 * filt(noise(d), 200, 900) * np.exp(-t * 10)
    return norm(x * np.minimum(1, t / 0.003)) * 0.9


def s_splash_small():
    d = 0.6
    t = T(d)
    x = filt(noise(d), 400, 5000) * np.exp(-t * 7) * np.minimum(1, t / 0.005)
    x += 0.6 * filt(noise(d), 80, 400) * np.exp(-t * 12)
    return norm(x) * 0.85


def s_sneak():
    notes = [196, 0, 233, 0, 262, 0, 233, 0, 196, 0, 175, 0, 196, 0, 0, 0]
    out = []
    for f in notes:
        d = 0.13
        tt = T(d)
        if f:
            y = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt * 28)
        else:
            y = np.zeros(len(tt))
        out.append(y)
    return norm(cat(*out)) * 0.55


def s_pour():
    d = 0.75
    t = T(d)
    x = np.zeros(len(t))
    for k in range(16):
        st = int(k * 0.045 * SR)
        n = int(0.06 * SR)
        f0 = 380 + 30 * (k % 4)
        y = sweep(f0, f0 * 1.6, 0.06) * env(n, 0.003, curve=2)
        x[st:st + n] += y[: len(x) - st]
    x += 0.3 * filt(noise(d), 600, 3000) * env(len(t), 0.05, curve=0.5)
    return norm(x) * 0.7


def s_spit():
    d = 0.5
    t = T(d)
    x = filt(noise(d), 600, 5000) * np.exp(-t * 6) * np.minimum(1, t / 0.004)
    x += 0.5 * sweep(500, 200, d, wave="saw") * np.exp(-t * 8)
    return norm(filt(x, hi=6000)) * 0.85


def s_drag():
    d = 1.0
    t = T(d)
    x = filt(noise(d), 200, 1500) * (0.6 + 0.4 * np.sin(2 * np.pi * 13 * t) ** 2)
    return norm(x * env(len(t), 0.05, curve=0.5)) * 0.6


def s_umbrella():
    a = s_whoosh()[: int(SR * 0.18)] * 0.7
    d = 0.12
    t = T(d)
    p = filt(noise(d), 800, 6000) * np.exp(-t * 40) + 0.6 * sweep(300, 120, d) * np.exp(-t * 30)
    return norm(cat(a, p))


def s_squeak_slide():
    d = 0.9
    t = T(d)
    f = 1500 - 700 * (t / d) + 120 * np.sin(2 * np.pi * 9 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t) ** 2)
    return norm(filt(x, 600, 4000) * env(len(t), 0.03, curve=0.6)) * 0.5


def s_error_beep():
    a = sweep(420, 420, 0.14, wave="sq") * env(int(SR * 0.14), 0.003, curve=0.6)
    b = sweep(300, 300, 0.22, wave="sq") * env(int(SR * 0.22), 0.003, curve=1.2)
    return norm(filt(cat(a, np.zeros(int(SR * 0.04)), b), hi=3000)) * 0.5


def s_blip():
    d = 0.09
    return norm(sweep(900, 1400, d, wave="sq") * env(int(SR * d), 0.002, curve=1.5)) * 0.35


def s_blip_down():
    out = [sweep(f, f * 0.8, 0.08, wave="sq") * env(int(SR * 0.08), 0.002, curve=1.5) for f in (1200, 900, 600)]
    return norm(filt(cat(*out), hi=4000)) * 0.4


def s_lock_click():
    d = 0.12
    t = T(d)
    x = filt(noise(d), 2000, 8000) * np.exp(-t * 80) + 0.5 * np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 60)
    return norm(cat(x, np.zeros(int(SR * 0.05)), x * 0.7)) * 0.6


def s_typing():
    d = 0.04
    t = T(d)
    x = filt(noise(d), 1500, 7000) * np.exp(-t * 120)
    return norm(cat(x, np.zeros(int(SR * 0.07)), x * 0.8, np.zeros(int(SR * 0.06)), x * 0.9)) * 0.45


def s_scan():
    d = 0.8
    t = T(d)
    f = 1200 + 300 * np.sin(2 * np.pi * 5 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + 0.2 * filt(noise(d), 3000, 8000)
    return norm(x * env(len(t), 0.03, curve=0.4)) * 0.35


def s_sizzle():
    d = 1.0
    t = T(d)
    x = filt(noise(d), 2500, 9000) * (0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 3.3 * t)))
    for k in range(40):
        st = int(rng.uniform(0, d - 0.01) * SR)
        n = int(0.006 * SR)
        x[st:st + n] += rng.uniform(1.5, 3.0) * filt(noise(0.006), 3000, 10000)[:n]
    return norm(x * env(len(t), 0.05, curve=0.7)) * 0.45


def s_flap():
    """pancake flip: airy 'fwup' with a soft flap."""
    d = 0.22
    t = T(d)
    x = filt(noise(d), 500, 2500) * np.sin(np.pi * t / d) ** 2
    x += 0.5 * sweep(180, 420, d) * np.exp(-t * 14)
    return norm(x) * 0.6


def s_pancake():
    """soft 'thwap' of a pancake landing."""
    d = 0.2
    t = T(d)
    x = filt(noise(d), 250, 1800) * np.exp(-t * 28) * np.minimum(1, t / 0.001)
    x += 0.7 * np.sin(2 * np.pi * np.cumsum(140 + 160 * np.exp(-t * 40)) / SR) * np.exp(-t * 22)
    return norm(x) * 0.75


def s_strain():
    """effort grunt-like low wobble (no voice)."""
    d = 0.9
    t = T(d)
    f = 95 + 15 * np.sin(2 * np.pi * 9 * t)
    x = filt(np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)), 80, 900)
    return norm(x * env(len(t), 0.08, curve=0.8)) * 0.5


def s_wobble():
    """tall stack swaying: rubbery wah."""
    d = 1.2
    t = T(d)
    f = 220 + 90 * np.sin(2 * np.pi * 2.2 * t)
    x = sweep(1, 1, d)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 2.2 * t))
    return norm(filt(x, 150, 1500) * env(len(t), 0.05, curve=0.8)) * 0.45


def s_whirr():
    """vending machine spiral motor: buzzy rising-falling whirr."""
    d = 0.9
    t = T(d)
    f = 110 + 25 * np.sin(np.pi * t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.tanh(3 * np.sin(ph)) + 0.4 * np.sin(3 * ph) + 0.15 * filt(noise(d), 800, 3000)
    x *= 0.75 + 0.25 * np.sin(2 * np.pi * 14 * t)
    return norm(filt(x, 70, 2500) * env(len(t), 0.04, curve=0.5)) * 0.45


def s_coin():
    """metallic coin clink."""
    d = 0.5
    t = T(d)
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, a, k in [(2900, 1, 9), (4300, 0.6, 12), (6100, 0.35, 16), (1900, 0.3, 14)])
    x += 0.4 * filt(noise(d), 4000, 10000) * np.exp(-t * 90)
    return norm(x) * 0.5


def s_tap():
    """knuckle tap on glass."""
    d = 0.08
    t = T(d)
    x = np.sin(2 * np.pi * 1300 * t) * np.exp(-t * 70) + 0.6 * filt(noise(d), 1500, 6000) * np.exp(-t * 120)
    return norm(x) * 0.5


def s_clatter():
    """a few cans/bags tumbling down."""
    d = 0.7
    out = np.zeros(int(SR * d))
    for k in range(7):
        st = int((k * 0.085 + rng.uniform(0, 0.03)) * SR)
        n = int(0.12 * SR)
        tt = np.arange(n) / SR
        f = rng.uniform(500, 1400)
        h = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 35) + 0.7 * filt(noise(0.12), 800, 5000)[:n] * np.exp(-tt * 60)
        out[st:st + n] += h[: len(out) - st] * rng.uniform(0.6, 1.0)
    return norm(out) * 0.7


def s_vacuum():
    """robot vacuum hum (whiny motor + air)."""
    d = 1.6
    t = T(d)
    f = 520 + 30 * np.sin(2 * np.pi * 3 * t)
    x = 0.5 * sweep(1, 1, d) * 0 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 + 0.6 * filt(noise(d), 1500, 6000)
    return norm(x * env(len(t), 0.15, curve=0.6)) * 0.35


def s_suck():
    """quick suction 'shloop'."""
    d = 0.22
    t = T(d)
    x = filt(noise(d), 800, 5000) * np.sin(np.pi * t / d) + 0.7 * sweep(300, 1400, d) * env(len(t), 0.01, curve=1.2)
    return norm(x) * 0.55


def s_robot_beep():
    """happy little robot chirp: 3 rising notes."""
    out = [sweep(f, f * 1.05, 0.07, wave="sq") * env(int(SR * 0.07), 0.002, curve=1.2) for f in (880, 1175, 1568)]
    gap = np.zeros(int(SR * 0.025))
    return norm(filt(cat(out[0], gap, out[1], gap, out[2]), hi=5000)) * 0.4


def s_twang():
    """plucked rubber band / stretched wishbone: low wobbly decaying tone."""
    d = 0.7
    t = T(d)
    f = 150 * (1 + 0.5 * np.exp(-t * 18)) * (1 + 0.04 * np.sin(2 * np.pi * 11 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (2 * ((ph / (2 * np.pi)) % 1) - 1) * 0.6 + np.sin(ph * 2) * 0.4
    x = filt(x, hi=1800) * env(len(t), 0.002, curve=2.2)
    return norm(x) * 0.8


def s_snap():
    """dry bone crack: sharp noise burst + low knock."""
    d = 0.32
    n = filt(noise(d), lo=1500) * env(int(SR * d), 0.0008, curve=14)
    k = sweep(220, 70, d) * env(int(SR * d), 0.001, curve=6)
    c = filt(noise(0.05), lo=3000) * env(int(SR * 0.05), 0.0005, curve=4)
    c = np.pad(c, (int(SR * 0.03), len(n) - len(c) - int(SR * 0.03)))
    return norm(n * 0.9 + k * 0.7 + c * 0.6) * 0.95


def s_stretch():
    """rubbery creak while something stretches."""
    d = 0.8
    t = T(d)
    f = 90 + 70 * t / d
    ph = 2 * np.pi * np.cumsum(f) / SR
    am = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 9 * t))
    x = filt((2 * ((ph / (2 * np.pi)) % 1) - 1), 120, 1400) * am * env(len(t), 0.05, curve=1.0)
    return norm(x) * 0.6


def s_alarm_ring():
    """old bell alarm clock ringing (1.2 s, hammer ~22 Hz)."""
    d = 1.2
    t = T(d)
    x = sum(a * np.sin(2 * np.pi * f * t) for f, a in [(2100, 1), (2630, 0.6), (4200, 0.3), (5300, 0.2)])
    ham = (np.sin(2 * np.pi * 22 * t) > 0).astype(float)
    ham = filt(ham, hi=200)
    x = x * (0.35 + 0.65 * np.abs(ham)) + 0.15 * filt(noise(d), 3000, 8000)
    return norm(x * env(len(t), 0.005, curve=0.4)) * 0.7


def s_honk():
    """air horn blast."""
    d = 0.9
    t = T(d)
    x = sum(np.tanh(3 * np.sin(2 * np.pi * f * t)) for f in (415, 523, 622))
    x = filt(x, 200, 5000) * env(len(t), 0.01, curve=0.6)
    return norm(x) * 0.85


def s_gong():
    """soft gong 'dong'."""
    d = 2.0
    t = T(d)
    x = sum(a * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 3 * t)) for f, a in [(110, 1), (167, 0.6), (233, 0.4), (391, 0.25)])
    return norm(x * np.exp(-t * 1.6) * np.minimum(1, t / 0.01)) * 0.8


def s_snore():
    """one snore: rough inhale + whistle exhale."""
    d1, d2 = 0.6, 0.5
    a = filt(noise(d1), 80, 600) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 28 * T(d1)))) * env(int(SR * d1), 0.2, curve=1.2)
    b = 0.5 * sweep(900, 1300, d2, wave="sine") * env(int(SR * d2), 0.05, curve=1.5) + 0.2 * filt(noise(d2), 1500, 4000) * env(int(SR * d2), 0.05, curve=2)
    return norm(cat(a, b)) * 0.55


def s_chicken():
    """rubber chicken squawk."""
    d = 0.45
    t = T(d)
    f = 700 + 500 * np.sin(np.pi * t / d) + 60 * np.sin(2 * np.pi * 30 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.tanh(2.5 * np.sin(ph)) + 0.3 * filt(noise(d), 1500, 5000)
    return norm(filt(x, 300, 6000) * env(len(t), 0.02, curve=0.8)) * 0.75


def s_seat_clack():
    """spring-loaded cinema seat snapping up: short creak + hard wooden clack + rattle."""
    d = 0.32
    t = T(d)
    cr = filt(noise(0.06), 900, 3000) * np.sin(2 * np.pi * 34 * T(0.06)) ** 2
    hit = np.sin(2 * np.pi * np.cumsum(420 * np.exp(-t * 30) + 160) / SR) * np.exp(-t * 28)
    hit += 0.8 * filt(noise(d), 1200, 7000) * np.exp(-t * 70)
    rat = 0.25 * filt(noise(d), 2500, 8000) * np.exp(-t * 14) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 26 * t)))
    return norm(cat(cr * 0.5, hit + rat))


def s_popcorn():
    """a shower of popcorn puffs: light dry patter."""
    d = 0.9
    out = np.zeros(int(SR * d))
    for k in range(22):
        st = int(rng.uniform(0, d - 0.05) * SR)
        n = int(0.025 * SR)
        y = filt(noise(0.025), 1800, 9000) * env(n, 0.0008, curve=6) * rng.uniform(0.3, 1.0)
        out[st:st + n] += y[: len(out) - st]
    return norm(out * env(len(out), 0.02, curve=1.2)) * 0.7


def s_rain():
    """3 s of steady rain: soft hiss + random droplet ticks (layer back to back for a bed)."""
    d = 3.0
    t = T(d)
    x = 0.5 * filt(noise(d), 1200, 9000) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.7 * t))
    x += 0.25 * filt(noise(d), 200, 900)
    n = int(0.012 * SR)
    for k in range(160):
        st = int(rng.uniform(0, d - 0.02) * SR)
        f = rng.uniform(1800, 4200)
        y = np.sin(2 * np.pi * f * np.arange(n) / SR) * env(n, 0.0005, curve=5) * rng.uniform(0.1, 0.35)
        x[st:st + n] += y
    e = np.minimum(1, np.minimum(t / 0.05, (d - t) / 0.05))
    return norm(x * e) * 0.6


def s_wind():
    """a gust of wind: swelling band-passed whoosh with a whistle."""
    d = 1.4
    t = T(d)
    sw = np.sin(np.pi * t / d) ** 1.5
    x = filt(noise(d), 300, 2500) * sw
    x += 0.25 * sweep(700, 1100, d, kind="lin") * sw * (0.6 + 0.4 * np.sin(2 * np.pi * 5 * t))
    return norm(x) * 0.8


def s_bus_horn():
    """big low two-note bus horn."""
    d = 0.7
    t = T(d)
    x = sum(np.tanh(2.5 * np.sin(2 * np.pi * f * t)) for f in (196, 247))
    x = filt(x, 120, 3000) * env(len(t), 0.02, curve=0.4)
    return norm(x) * 0.8


def s_engine():
    """bus driving past: low diesel rumble swelling then fading, slight pitch drop."""
    d = 2.6
    t = T(d)
    f = 55 - 12 * (t / d)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.tanh(2 * np.sin(ph)) + 0.5 * np.tanh(2 * np.sin(2 * ph))
    x = filt(x, 40, 900) + 0.35 * filt(noise(d), 80, 600)
    sw = np.exp(-((t - 1.0) / 0.7) ** 2)
    return norm(x * sw) * 0.85


def s_wave():
    """huge water crash: low boom + roaring noise + dripping tail."""
    d = 2.2
    t = T(d)
    x = 1.2 * filt(noise(d), 40, 260) * np.exp(-t * 3.0) * np.minimum(1, t / 0.03)
    x += filt(noise(d), 300, 7000) * np.exp(-t * 2.2) * np.minimum(1, t / 0.06)
    drops = np.zeros(len(t))
    for k in range(30):
        st = int(rng.uniform(0.3, 1.9) * SR)
        b = s_plop() * rng.uniform(0.1, 0.4)
        b = b[: len(t) - st]
        drops[st:st + len(b)] += b
    return norm(x + drops)


def s_stream():
    """water gushing off an umbrella edge onto someone (1.1 s)."""
    d = 1.1
    t = T(d)
    x = filt(noise(d), 500, 4500) * (0.75 + 0.25 * np.sin(2 * np.pi * 17 * t))
    x += 0.4 * filt(noise(d), 120, 400)
    return norm(x * env(len(t), 0.04, curve=0.5)) * 0.75


def s_tweet():
    """small bird chirp (2 quick upward whistles)."""
    out = []
    for f0 in (2600, 3100):
        d = 0.09
        out.append(sweep(f0, f0 * 1.5, d) * env(int(SR * d), 0.005, curve=1.5))
        out.append(np.zeros(int(SR * 0.05)))
    return norm(cat(*out)) * 0.5


def s_keys():
    """keyring jingle (several small metallic clinks)."""
    d = 0.45
    out = np.zeros(int(SR * d))
    for k, (st, f) in enumerate([(0.0, 3300), (0.05, 4100), (0.11, 2800), (0.18, 3700), (0.27, 4500)]):
        dd = 0.18
        t = T(dd)
        x = sum(a * np.sin(2 * np.pi * f * m * t) for m, a in [(1, 1), (1.51, 0.5), (2.3, 0.25)]) * np.exp(-t * 28)
        i = int(st * SR)
        out[i:i + len(x)] += x[: len(out) - i] * (1 - 0.12 * k)
    out += 0.15 * filt(noise(d), 5000, 12000) * np.exp(-T(d) * 20)
    return norm(out) * 0.5


def s_tink():
    """single tiny metal tink (keys hitting shaft wall)."""
    d = 0.35
    t = T(d)
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, a, k in [(3600, 1, 14), (5400, 0.5, 20), (7900, 0.25, 30)])
    return norm(x) * 0.45


def s_lift_door():
    """elevator door slide: soft mechanical rumble with a clunk at the end (0.55 s)."""
    d = 0.55
    t = T(d)
    x = filt(noise(d), 150, 900) * (0.6 + 0.4 * np.sin(np.pi * t / d))
    x += 0.4 * np.sin(2 * np.pi * np.cumsum(90 + 30 * t / d) / SR)
    x *= env(len(t), 0.05, curve=0.6)
    tail = int(0.47 * SR)
    k = T(d - 0.47)
    x[tail:] += 0.9 * np.sin(2 * np.pi * 140 * k) * np.exp(-k * 40)
    return norm(x) * 0.6


def s_lift_hum():
    """elevator motor hum while travelling (1.0 s)."""
    d = 1.0
    t = T(d)
    f = 70 + 40 * np.minimum(1, t / 0.3)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.2 * filt(noise(d), 200, 1200)
    x *= np.minimum(1, t / 0.1) * np.minimum(1, (d - t) / 0.2)
    return norm(filt(x, 50, 1800)) * 0.4


def s_deflate():
    """balloon letting air out (raspberry whistle, 0.8 s)."""
    d = 0.8
    t = T(d)
    f = 700 - 450 * t / d + 120 * np.sin(2 * np.pi * 9 * t)
    x = np.tanh(3 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * (0.6 + 0.4 * np.sin(2 * np.pi * 37 * t))
    x += 0.3 * filt(noise(d), 1000, 5000)
    return norm(filt(x, 200, 6000) * env(len(t), 0.02, curve=0.7)) * 0.55


def s_pant():
    """quick tired panting (4 breaths, 0.9 s)."""
    d = 0.9
    out = np.zeros(int(SR * d))
    for k in range(4):
        dd = 0.13
        t = T(dd)
        x = filt(noise(dd), 600 + 300 * (k % 2), 3000) * np.sin(np.pi * t / dd) ** 2
        i = int(k * 0.22 * SR)
        out[i:i + len(x)] += x[: len(out) - i]
    return norm(out) * 0.45


def s_surf():
    """gentle beach wave washing in and out (2.8 s ambience)."""
    d = 2.8
    t = T(d)
    sw = np.sin(np.pi * np.minimum(1, t / 1.1)) ** 2 * np.exp(-np.maximum(0, t - 1.1) * 1.4)
    x = filt(noise(d), 200, 3500) * sw + 0.5 * filt(noise(d), 60, 300) * sw
    x *= np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.5)
    return norm(x) * 0.5


def s_ffwd():
    """cartoon time-lapse fast-forward: chirpy rising warble (1.5 s)."""
    d = 1.5
    t = T(d)
    f = 500 * (2.2 ** (t / d)) * (1 + 0.18 * np.sign(np.sin(2 * np.pi * 16 * t)))
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = 0.6 * np.tanh(2 * np.sin(ph)) + 0.25 * filt(noise(d), 2000, 7000) * (0.5 + 0.5 * np.sin(2 * np.pi * 16 * t))
    x *= np.minimum(1, t / 0.08) * np.minimum(1, (d - t) / 0.15)
    return norm(filt(x, 200, 8000)) * 0.4


def s_coconut():
    """hollow coconut knock on a head: woody 'tok' with resonance."""
    d = 0.4
    t = T(d)
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, a, k in [(420, 1, 22), (980, 0.55, 30), (1650, 0.3, 45)])
    x += 0.5 * filt(noise(d), 1200, 5000) * np.exp(-t * 160)
    return norm(x) * 0.85


def s_crab():
    """tiny pincer clicks (3 quick snips)."""
    d = 0.35
    out = np.zeros(int(SR * d))
    for k in range(3):
        n = int(0.03 * SR)
        tt = np.arange(n) / SR
        h = np.sin(2 * np.pi * 3200 * tt) * np.exp(-tt * 260) + 0.6 * filt(noise(0.03), 3000, 9000)[:n] * np.exp(-tt * 300)
        i = int(k * 0.1 * SR)
        out[i:i + n] += h[: len(out) - i]
    return norm(out) * 0.4


def s_rustle():
    """palm fronds rustling/whipping (0.6 s)."""
    d = 0.6
    t = T(d)
    x = filt(noise(d), 1500, 9000) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 13 * t))) * env(len(t), 0.02, curve=1.5)
    return norm(x) * 0.55


def s_crunch():
    """loud crisp celery crunch: sharp noisy snap + a few crackly fragments."""
    d = 0.45
    t = T(d)
    x = filt(noise(d), 1800, 9000) * np.exp(-t * 30) * np.minimum(1, t / 0.001)
    for k in range(5):
        st = int((0.04 + k * 0.05 + rng.uniform(0, 0.02)) * SR)
        n = int(0.025 * SR)
        y = filt(noise(0.025), 2500, 10000)[:n] * np.exp(-np.arange(n) / SR * 200)
        x[st:st + n] += 0.6 * y[: len(x) - st]
    x += 0.5 * sweep(300, 120, d) * np.exp(-t * 25)
    return norm(x) * 0.9


def s_fridge_hum():
    """small fridge compressor hum (1.2 s): low buzzy 50 Hz-ish drone."""
    d = 1.2
    t = T(d)
    x = sweep(58, 58, d, wave="saw") * 0.5 + 0.3 * np.sin(2 * np.pi * 116 * t)
    x = filt(x, hi=600) * env(len(t), 0.15, curve=0.6)
    return norm(x) * 0.35


def s_shine():
    """fridge light / treasure glow: airy shimmering rise (0.9 s)."""
    d = 0.9
    t = T(d)
    x = np.zeros(len(t))
    for k, f in enumerate((1320, 1760, 2090, 2640, 3520)):
        st = k * 0.09
        e = np.clip((t - st) / 0.01, 0, 1) * np.exp(-np.clip(t - st, 0, None) * 5)
        x += np.sin(2 * np.pi * f * t) * e
    x += 0.25 * filt(noise(d), 4000, 12000) * env(len(t), 0.2, curve=1.5)
    return norm(x) * 0.5


def s_can():
    """empty tin can clink."""
    d = 0.3
    t = T(d)
    x = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * dk) for f, dk in ((1850, 18), (2730, 25), (4100, 35)))
    x += 0.5 * filt(noise(d), 3000, 9000) * np.exp(-t * 120)
    return norm(x) * 0.6


def s_cabin_hum():
    """airplane cabin: steady jet-engine air roar, 2.4 s with soft edges (overlap copies every ~2 s)."""
    d = 2.4
    t = T(d)
    x = filt(noise(d), 60, 700) + 0.25 * filt(noise(d), 700, 2200)
    x += 0.15 * np.sin(2 * np.pi * 118 * t) + 0.08 * np.sin(2 * np.pi * 236 * t)
    e = np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4)
    return norm(x * e) * 0.35


def s_plane_chime():
    """cabin PA chime: soft two-tone 'bing-bong'."""
    def tone(f, d):
        t = T(d)
        y = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) + 0.1 * np.sin(2 * np.pi * 3 * f * t)
        return y * np.exp(-t * 3.2) * np.minimum(1, t / 0.004)
    a = tone(1175, 1.2)
    b = tone(880, 1.4)
    x = np.zeros(int(SR * 1.9))
    x[:len(a)] += a
    st = int(0.42 * SR)
    x[st:st + len(b)] += b[: len(x) - st]
    return norm(x) * 0.75


def s_buckle():
    """seatbelt buckle unlatching: metallic double click + strap slither."""
    d = 0.35
    t = T(d)
    c1 = filt(noise(0.02), 2500, 9000) * env(int(0.02 * SR), 0.001, curve=2)
    ring = sum(np.sin(2 * np.pi * f * T(0.12)) * np.exp(-T(0.12) * 40) for f in (2900, 4300))
    x = np.zeros(len(t))
    x[:len(c1)] += c1
    st = int(0.06 * SR)
    x[st:st + len(ring)] += ring * 0.6
    sl = filt(noise(0.15), 1500, 6000) * env(int(0.15 * SR), 0.02, curve=1.5) * 0.3
    st = int(0.18 * SR)
    x[st:st + len(sl)] += sl
    return norm(x) * 0.7


def s_sneeze_build():
    """'ah... ah...' wordless pre-sneeze: two rising breathy hums."""
    out = []
    for k, (f0, f1, d) in enumerate([(240, 330, 0.32), (300, 470, 0.42)]):
        t = T(d)
        v = filt(sweep(f0, f1, d, wave="saw"), 250, 2200) * (t / d) ** 0.6
        br = filt(noise(d), 900, 3500) * (t / d) ** 1.4 * 0.6
        x = (v + br) * np.minimum(1, (d - t) / 0.03)
        out.append(x)
        out.append(np.zeros(int(SR * 0.08)))
    return norm(cat(*out)) * 0.55


def s_mff():
    """muffled sneeze behind a hand: low 'mfff' thump + cheek puff."""
    d = 0.4
    t = T(d)
    burst = filt(noise(d), 120, 700) * np.exp(-t * 9) * np.minimum(1, t / 0.006)
    thump = np.sin(2 * np.pi * np.cumsum(140 * np.exp(-t * 6) + 60) / SR) * np.exp(-t * 10)
    vox = filt(sweep(300, 160, d, wave="saw"), 100, 600) * np.exp(-t * 8) * 0.6
    return norm(burst + thump + vox) * 0.85


def s_big_achoo():
    """the huge final sneeze: long inhale tail + roaring blast + rumble."""
    a = s_inhale() * 0.5
    d = 1.1
    t = T(d)
    burst = filt(noise(d), 300, 6000) * np.exp(-t * 3.2) * np.minimum(1, t / 0.004)
    vox = filt(sweep(700, 180, d, wave="saw"), 150, 2600) * np.exp(-t * 3.5)
    rum = filt(noise(d), 30, 200) * np.exp(-t * 2.5) * 1.6
    return norm(cat(a, burst + 0.8 * vox + rum)) * 1.0


def s_book_thud():
    """hardcover book landing: papery slap + low knock."""
    d = 0.18
    t = T(d)
    slap = filt(noise(d), 400, 3000) * np.exp(-t * 55)
    knock = np.sin(2 * np.pi * np.cumsum(220 * np.exp(-t * 18) + 90) / SR) * np.exp(-t * 26)
    return norm(slap + knock) * 0.75


def s_flutter():
    """pages fluttering (fast rustly flaps)."""
    d = 0.6
    t = T(d)
    am = 0.5 + 0.5 * np.sin(2 * np.pi * 24 * t) ** 2
    x = filt(noise(d), 1500, 7000) * am * np.sin(np.pi * t / d)
    return norm(x) * 0.5


def s_tick():
    """quiet library clock tick-tock."""
    d = 0.55
    x = np.zeros(int(SR * d))
    for k, f in enumerate((2600, 2100)):
        tt = T(0.04)
        h = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 160) + 0.4 * filt(noise(0.04), 2000, 8000) * np.exp(-tt * 200)
        st = int(k * 0.5 * SR)
        x[st:st + len(h)] += h[: len(x) - st]
    return norm(x) * 0.4


def s_poof():
    """soft dust puff."""
    d = 0.35
    t = T(d)
    x = filt(noise(d), 300, 2000) * np.exp(-t * 9) * np.minimum(1, t / 0.01)
    return norm(x) * 0.5


def s_buzz():
    """mosquito whine (1.2 s, wobbling pitch)."""
    d = 1.2
    t = T(d)
    f = 620 + 60 * np.sin(2 * np.pi * 3.3 * t) + 25 * np.sin(2 * np.pi * 11 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.tanh(3 * np.sin(ph)) + 0.35 * np.sin(2 * ph)
    am = 0.6 + 0.4 * np.sin(2 * np.pi * 5 * t)
    x = filt(x, 400, 5000) * am * np.minimum(1, t / 0.08) * np.minimum(1, (d - t) / 0.15)
    return norm(x) * 0.45


def s_slap():
    """sharp cartoon slap."""
    d = 0.22
    t = T(d)
    x = filt(noise(d), 900, 7000) * np.exp(-t * 45) + 0.6 * np.sin(2 * np.pi * 180 * t) * np.exp(-t * 30)
    return norm(x) * 0.95


def s_crackle():
    """campfire crackle bed (2 s)."""
    d = 2.0
    x = 0.25 * filt(noise(d), 80, 600) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * T(d)))
    r = np.random.default_rng(11)
    for _ in range(26):
        st = int(r.uniform(0, d - 0.03) * SR)
        tt = T(r.uniform(0.004, 0.02))
        nz = filt(rng.standard_normal(len(tt)), 1500, 8000)
        x[st:st + len(tt)] += r.uniform(0.4, 1.0) * nz * np.exp(-tt * 300)
    return norm(x) * 0.5


def s_blow():
    """puffed-cheek blowing."""
    d = 0.5
    t = T(d)
    x = filt(noise(d), 500, 3000) * np.sin(np.pi * t / d) ** 0.6
    return norm(x) * 0.6


def s_washer():
    """washing machine churn (1.5 s)."""
    d = 1.5
    t = T(d)
    x = filt(noise(d), 120, 900) * (0.55 + 0.45 * np.sin(2 * np.pi * 1.6 * t) ** 2)
    x += 0.5 * np.sin(2 * np.pi * 55 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 1.6 * t))
    return norm(x * np.minimum(1, t / 0.1) * np.minimum(1, (d - t) / 0.1)) * 0.55


def s_spin_up():
    """motor winding up."""
    d = 0.9
    x = sweep(120, 900, d, wave="saw") * 0.5 + 0.4 * filt(noise(d), 300, 3000)
    return norm(filt(x, 80, 4000) * env(int(SR * d), 0.05, curve=0.8)) * 0.7


def s_dial():
    """ratchet dial clicks."""
    d = 0.35
    x = np.zeros(int(SR * d))
    for k in range(6):
        tt = T(0.02)
        st = int(k * 0.055 * SR)
        h = filt(noise(0.02), 2000, 9000) * np.exp(-tt * 260)
        x[st:st + len(h)] += h[: len(x) - st]
    return norm(x) * 0.6


def s_rip():
    """cardboard / paper tearing: crackly noise with jittery amplitude (0.45 s)."""
    d = 0.45
    n = int(SR * d)
    x = filt(noise(d), 700, 7000)
    jit = np.repeat(rng.uniform(0.2, 1.0, n // 300 + 1), 300)[:n]
    e = np.minimum(1, np.arange(n) / (0.03 * SR)) * (1 - np.arange(n) / n) ** 0.6
    return norm(x * jit * e) * 0.8


def s_cart_rattle():
    """shopping cart rolling fast: rattly wire clatter + wheel rumble (0.8 s)."""
    d = 0.8
    n = int(SR * d)
    tt = np.arange(n) / SR
    rattle = filt(noise(d), 2000, 7000) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 23 * tt)))
    rumble = filt(noise(d), 60, 300) * 1.5
    e = np.minimum(1, tt / 0.05) * np.minimum(1, (d - tt) / 0.2)
    return norm((rattle * 0.6 + rumble) * e) * 0.7


def s_metal_crash():
    """cart crashing into a display: metallic clangs + clatter tail (1.0 s)."""
    d = 1.0
    out = np.zeros(int(SR * d))
    for k in range(9):
        st = int((k * 0.07 + rng.uniform(0, 0.04)) * SR)
        m = int(0.3 * SR)
        tt = np.arange(m) / SR
        f = rng.uniform(300, 1800)
        h = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 2.76 * tt)) * np.exp(-tt * (12 + 4 * k))
        h += 0.8 * filt(noise(0.3), 1000, 8000)[:m] * np.exp(-tt * 40)
        out[st:st + m] += h[: len(out) - st] * (1.0 if k == 0 else rng.uniform(0.4, 0.8))
    boom = filt(noise(0.25), 40, 200) * np.exp(-T(0.25) * 14) * 3
    out[: len(boom)] += boom
    return norm(out) * 0.85


def s_tube():
    """hollow cardboard tube 'tok' on a head."""
    d = 0.25
    tt = T(d)
    x = np.sin(2 * np.pi * 420 * tt) * np.exp(-tt * 30) + 0.6 * np.sin(2 * np.pi * 630 * tt) * np.exp(-tt * 45)
    x += 0.4 * filt(noise(d), 800, 3000) * np.exp(-tt * 80)
    return norm(x) * 0.7


def s_clack():
    """wooden chopsticks clacking together: bright dry double click."""
    d = 0.12
    out = np.zeros(int(SR * d))
    for st_t, f in ((0.0, 2400), (0.035, 2900)):
        tt = T(0.05)
        h = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 140) + 0.5 * filt(noise(0.05), 2500, 9000) * np.exp(-tt * 200)
        st = int(st_t * SR)
        out[st:st + len(h)] += h[: len(out) - st]
    return norm(out) * 0.7


def s_purr():
    """cat purring: low rumbly amplitude-modulated noise (1.2 s)."""
    d = 1.2
    tt = T(d)
    x = filt(noise(d), 40, 260) * (0.55 + 0.45 * np.sin(2 * np.pi * 24 * tt)) * (0.7 + 0.3 * np.sin(2 * np.pi * 1.6 * tt))
    e = np.minimum(1, tt / 0.1) * np.minimum(1, (d - tt) / 0.2)
    return norm(x * e) * 0.6


def s_plate_spin():
    """a plate spinning down on a counter: accelerating ceramic rattle (1.0 s)."""
    d = 1.0
    out = np.zeros(int(SR * d))
    tk = 0.0
    gap = 0.12
    while tk < d - 0.05:
        tt = T(0.04)
        h = np.sin(2 * np.pi * 3100 * tt) * np.exp(-tt * 160) + 0.4 * filt(noise(0.04), 3000, 9000) * np.exp(-tt * 220)
        st = int(tk * SR)
        out[st:st + len(h)] += h[: len(out) - st] * (0.4 + 0.6 * tk / d)
        tk += gap
        gap = max(0.018, gap * 0.82)
    return norm(out) * 0.6


def s_belt():
    """sushi conveyor hum (2 s, loopable bed)."""
    d = 2.0
    tt = T(d)
    x = 0.5 * np.sin(2 * np.pi * 95 * tt) + 0.3 * np.sin(2 * np.pi * 190 * tt) + 0.4 * filt(noise(d), 100, 600)
    x *= 0.8 + 0.2 * np.sin(2 * np.pi * 3 * tt)
    e = np.minimum(1, tt / 0.2) * np.minimum(1, (d - tt) / 0.2)
    return norm(x * e) * 0.3


def s_zap():
    """short electric zap / spark crackle (plug going in, energy blip)."""
    d = 0.22
    tt = T(d)
    buzz = np.sign(np.sin(2 * np.pi * 120 * tt)) * 0.4 + filt(noise(d), 1500, 7000)
    gate = (rng.random(len(tt)) > 0.55).astype(float)
    gate = filt(gate, hi=400)
    x = buzz * (0.4 + gate) * np.exp(-tt * 14)
    return norm(x) * 0.55


def s_power_off():
    """phone dying: descending sine 'pwoo' + tiny click at the end."""
    a = sweep(900, 110, 0.55, wave="tri") * env(int(SR * 0.55), 0.005, curve=0.8)
    c = filt(noise(0.03), 2000, 8000) * np.exp(-T(0.03) * 120)
    return norm(cat(a, np.zeros(int(SR * 0.04)), c * 0.6)) * 0.6


def s_shutter():
    """phone camera shutter: two quick clicks with a soft swish."""
    k = filt(noise(0.025), 1500, 9000) * np.exp(-T(0.025) * 160)
    sw = filt(noise(0.06), 800, 4000) * env(int(SR * 0.06), 0.01, curve=2)
    return norm(cat(k, sw * 0.4, k * 0.8)) * 0.7


def s_charge_ok():
    """'charging connected' chime: two quick rising soft notes."""
    out = []
    for f in (880, 1320):
        d = 0.12
        out.append((np.sin(2 * np.pi * f * T(d)) + 0.3 * np.sin(4 * np.pi * f * T(d))) * env(int(SR * d), 0.004, curve=2))
    return norm(cat(*out)) * 0.45


def s_beep():
    """thermostat button beep: short clean square-ish tone."""
    d = 0.07
    x = np.tanh(2.5 * np.sin(2 * np.pi * 1900 * T(d))) * env(int(SR * d), 0.002, curve=1.5)
    return norm(filt(x, 300, 6000)) * 0.4


def s_chatter():
    """teeth chattering from cold: fast irregular tiny clicks (0.9 s)."""
    d = 0.9
    x = np.zeros(int(SR * d))
    r = np.random.default_rng(21)
    tt = 0.0
    while tt < d - 0.03:
        st = int(tt * SR)
        k = filt(r.standard_normal(int(SR * 0.012)), 1800, 6000) * np.exp(-T(0.012) * 400)
        x[st:st + len(k)] += k * r.uniform(0.6, 1.0)
        tt += r.uniform(0.035, 0.055)
    return norm(x) * 0.5


def s_freeze():
    """things freezing over: rising glassy shimmer + crystalline crackle (0.9 s)."""
    d = 0.9
    t = T(d)
    sh = sum(a * np.sin(2 * np.pi * f * t * (1 + 0.6 * t / d)) for f, a in [(1800, 0.5), (2700, 0.35), (4100, 0.2)])
    sh *= np.minimum(1, t / 0.25) * (1 - t / d) ** 1.2
    cr = np.zeros(len(t))
    r = np.random.default_rng(5)
    for _ in range(30):
        st = int(r.uniform(0, d - 0.02) * SR)
        k = filt(r.standard_normal(int(SR * 0.008)), 3000, 9000) * np.exp(-T(0.008) * 500)
        cr[st:st + len(k)] += k * r.uniform(0.3, 1.0)
    return norm(sh * 0.6 + cr) * 0.6


def s_ice_shatter():
    """ice block cracking and shattering: crack + tinkly shards."""
    c = filt(noise(0.12), lo=1200) * env(int(SR * 0.12), 0.0006, curve=10)
    d = 0.7
    t = T(d)
    tk = np.zeros(len(t))
    r = np.random.default_rng(8)
    for _ in range(14):
        st = int(r.uniform(0.02, 0.5) * SR)
        f = r.uniform(2500, 6500)
        tt = T(0.15)
        k = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 30)
        tk[st:st + len(k)] += k[: len(tk) - st] * r.uniform(0.3, 0.8)
    return norm(np.concatenate([c, np.zeros(len(t) - len(c))]) + tk * 0.5) * 0.8


def s_ac_hum():
    """air conditioner running: airy fan hiss + low motor hum (2 s, loopable bed)."""
    d = 2.0
    t = T(d)
    x = 0.6 * filt(noise(d), 200, 1800) + 0.35 * np.sin(2 * np.pi * 100 * t) + 0.15 * np.sin(2 * np.pi * 200 * t)
    e = np.minimum(1, t / 0.15) * np.minimum(1, (d - t) / 0.15)
    return norm(x * e) * 0.35


def s_blast():
    """huge cold air blast: big low whoomp + roaring noise burst."""
    d = 1.3
    t = T(d)
    lo = sweep(90, 35, d) * np.exp(-t * 3)
    nz = filt(noise(d), 150, 3000) * np.minimum(1, t / 0.02) * np.exp(-t * 2.2)
    return norm(lo * 0.9 + nz) * 0.95


def s_drip():
    """single water drip 'plink'."""
    d = 0.25
    x = sweep(900, 1700, d) * np.exp(-T(d) * 22)
    return norm(x) * 0.45


SOUNDS = {k[2:]: v for k, v in globals().items() if k.startswith("s_")}


def repitch(x, p):
    if abs(p - 1) < 1e-3:
        return x
    n = int(len(x) / p)
    return np.interp(np.arange(n) * p, np.arange(len(x)), x)


def main():
    ev = json.load(open(sys.argv[1]))
    dur = float(sys.argv[3])
    mix = np.zeros(int(SR * (dur + 2)))
    cache = {}
    for e in ev:
        name = e["name"]
        if name not in cache:
            cache[name] = SOUNDS[name]()
        x = repitch(cache[name], e.get("pitch", 1.0)) * e.get("gain", 1.0)
        st = int(e["t"] * SR)
        mix[st:st + len(x)] += x[: len(mix) - st]
    mix = mix[: int(SR * dur)]
    mix = np.tanh(mix * 1.1) * 0.9
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.89
    # gentle fade out last 0.4s
    n = int(0.4 * SR)
    mix[-n:] *= np.linspace(1, 0, n)
    st = np.stack([mix, mix], 1)
    wavfile.write(sys.argv[2], SR, (st * 32767).astype(np.int16))
    print("ok", len(ev))


if __name__ == "__main__":
    main()
