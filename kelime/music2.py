"""Alternatif arka plan müzikleri (kodla üretilmiş, özgün, sözsüz).
Kullanım: python3 music2.py <stil: marimba|lofi> <çıktı.wav>"""
import numpy as np, wave, sys

SR = 44100
rng = np.random.default_rng(11)
style = sys.argv[1]; out = sys.argv[2]

def hz(m): return 440 * 2 ** ((m - 69) / 12)

def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR); y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc; y[i] = acc
    return y

def reverb(x, secs=1.6, mix=0.25):
    n = int(secs * SR); t = np.arange(n) / SR
    ir = rng.normal(0, 1, n) * np.exp(-t * 3.5); ir[0] = 0
    ir = lowpass(ir, 3500); ir /= np.sqrt(np.sum(ir ** 2))
    N = 1 << int(np.ceil(np.log2(len(x) + n)))
    wet = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[:len(x)]
    return (1 - mix) * x + mix * wet * 0.6

def marimba(f, vel):
    d = 1.2; t = np.arange(int(d * SR)) / SR
    return vel * (np.sin(2*np.pi*f*t) * np.exp(-t*5) + 0.25*np.sin(2*np.pi*4*f*t)*np.exp(-t*30)
                  + 0.08*np.sin(2*np.pi*10*f*t)*np.exp(-t*60)) * (1 - np.exp(-t*800))

def pad(freqs, d, vel):
    t = np.arange(int(d * SR)) / SR; x = np.zeros_like(t)
    for f in freqs:
        for det in (-0.12, 0.12):
            x += np.sin(2*np.pi*(f*(1+det/100*6))*t) + 0.3*np.sin(2*np.pi*2*f*t)
    env = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.6)
    return vel * x * env / len(freqs)

def keys(f, d, vel):  # yumuşak rhodes
    t = np.arange(int(d * SR)) / SR
    mod = np.sin(2*np.pi*f*t) * 1.2 * np.exp(-t*3)
    return vel * np.sin(2*np.pi*f*t + mod) * np.exp(-t*1.4) * (1 - np.exp(-t*200))

def kick(vel=0.5):
    t = np.arange(int(0.35 * SR)) / SR
    f = 55 + 70 * np.exp(-t * 30)
    return vel * np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t * 9)

def snare(vel=0.18):
    t = np.arange(int(0.25 * SR)) / SR
    return vel * lowpass(rng.normal(0, 1, len(t)), 3000) * np.exp(-t * 18)

def hat(vel=0.05):
    t = np.arange(int(0.06 * SR)) / SR
    n = rng.normal(0, 1, len(t)); n = n - lowpass(n, 6000)
    return vel * n * np.exp(-t * 70)

def add(buf, x, s):
    i = int(s * SR); j = min(len(buf), i + len(x)); buf[i:j] += x[:j - i]

if style == "marimba":
    BPM = 100; B = 60 / BPM; bars = 16
    chords = [[53, 57, 60], [52, 55, 60], [50, 53, 57], [46, 50, 53]]  # F C/E Dm Bb
    bass = [41, 40, 38, 34]
    # 2 ölçülük oyuncaklı melodi (8'likler, None = sus)
    mel = [[72, None, 69, 72, 74, None, 72, None], [72, None, 67, 69, 67, None, None, None],
           [69, None, 65, 69, 70, None, 69, None], [67, None, 65, 67, 65, None, None, None]]
    total = bars * 4 * B; n = int(total * SR); L = np.zeros(n + 3 * SR); R = np.zeros_like(L)
    for b in range(bars):
        ci = b % 4; t0 = b * 4 * B
        p = pad([hz(m) for m in chords[ci]], 4 * B + 0.3, 0.10); add(L, p, t0); add(R, p, t0)
        for k in range(4):  # marimba bas + akor vuruşu
            add(L, marimba(hz(bass[ci] + 12), 0.22 if k % 2 == 0 else 0.12), t0 + k * B)
            add(R, marimba(hz(bass[ci] + 12), 0.18 if k % 2 == 0 else 0.10), t0 + k * B)
        for s, m in enumerate(mel[ci]):
            if m is None or b < 0: continue
            x = marimba(hz(m), 0.20 if b % 8 < 4 else 0.17)
            add(L, x * 0.6, t0 + s * B / 2); add(R, x, t0 + s * B / 2)
        for s in range(8):  # çok hafif hat
            add(L, hat(0.02), t0 + s * B / 2); add(R, hat(0.025), t0 + s * B / 2)
else:  # lofi
    BPM = 80; B = 60 / BPM; bars = 12
    chords = [[60, 64, 67, 71], [57, 60, 64, 67], [62, 65, 69, 72], [55, 59, 62, 65]]  # Cmaj7 Am7 Dm7 G7
    bass = [36, 33, 38, 31]
    total = bars * 4 * B; n = int(total * SR); L = np.zeros(n + 3 * SR); R = np.zeros_like(L)
    for b in range(bars):
        ci = b % 4; t0 = b * 4 * B
        for k, m in enumerate(chords[ci]):
            for hit in (0, 2.5):
                x = keys(hz(m), 2.2, 0.10); add(L, x, t0 + hit * B + k * 0.015); add(R, x * 0.8, t0 + hit * B + k * 0.02)
        xb = keys(hz(bass[ci]), 3.5, 0.28); add(L, xb, t0); add(R, xb, t0)
        for k in range(4):
            if k in (0, 2): add(L, kick(0.35), t0 + k * B); add(R, kick(0.35), t0 + k * B)
            if k in (1, 3): add(L, snare(0.10), t0 + k * B + 0.02); add(R, snare(0.10), t0 + k * B + 0.02)
        for s in range(8):
            sw = 0.05 if s % 2 else 0  # swing
            add(L, hat(0.03), t0 + s * B / 2 + sw); add(R, hat(0.035), t0 + s * B / 2 + sw)
    L = lowpass(L, 5000); R = lowpass(R, 5000)
    vinyl = rng.normal(0, 0.004, len(L)); L += vinyl; R += vinyl

L = reverb(L); R = reverb(R)
tail_L, tail_R = L[n:].copy(), R[n:].copy(); L, R = L[:n], R[:n]
L[:len(tail_L)] += tail_L; R[:len(tail_R)] += tail_R
st = np.stack([L, R], 1); st /= np.max(np.abs(st)) / 0.8
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print(style, round(total, 1), "sn")
