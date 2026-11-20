import json, numpy as np, wave, random
from sim import FPS
SR = 48000
ev = json.load(open("events.json"))
N = ev["N"]; Z = ev["Z"]; cam = ev["cam"]; WIN = ev["win_f"]
VH = 1920 / Z
out = np.zeros(int((N / FPS + 0.5) * SR))
rnd = np.random.default_rng(3)

def add(t, sig, g=1.0):
    i = int(t * SR)
    if i >= len(out): return
    n = min(len(sig), len(out) - i)
    out[i:i+n] += sig[:n] * g

def env(n, dec):
    return np.exp(-np.arange(n) / (dec * SR))

def tone(f, dur, dec, harm=(1, 0.3, 0.12)):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(a * np.sin(2*np.pi*f*(k+1)*t) for k, a in enumerate(harm))
    att = np.minimum(1, np.arange(n) / (0.002*SR))
    return s * env(n, dec) * att

def noise(dur, dec, lp=0.3):
    n = int(dur * SR); x = rnd.standard_normal(n)
    y = np.zeros(n); a = lp; acc = 0
    for i in range(n):
        acc += a * (x[i] - acc); y[i] = acc
    return y * env(n, dec)

PENTA = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5, 1174.7, 1318.5]
thud = noise(0.12, 0.03, 0.08) * 2.2 + tone(150, 0.12, 0.04, (1,))
clack = noise(0.08, 0.015, 0.6) * 1.4 + tone(900, 0.08, 0.02, (1, 0.5))
last = -10
for f, ct, inten, y in ev["hits"]:
    if f >= N or f < 60: continue
    cy = cam[f][1]
    if not (cy - 40 < y < cy + VH + 40): continue
    if f - last < 2: continue
    last = f
    t = f / FPS
    g = 0.12 + 0.35 * inten
    if ct == 3:
        add(t, tone(random.Random(int(y)).choice(PENTA), 0.35, 0.09), g)
    elif ct == 2:
        add(t, thud, g * 0.9)
    else:
        add(t, clack, g * 1.2)
# hook pop at start
pop = tone(300, 0.15, 0.04, (1,)) * np.linspace(1, 0, int(0.15*SR))
n = int(0.15*SR); tt = np.arange(n)/SR
add(0.02, np.sin(2*np.pi*(250 + 900*tt)*tt) * env(n, 0.05), 0.5)
# gate + go whoosh
add(1.0, clack, 0.9)
n = int(0.5*SR); w = noise(0.5, 0.25, 0.15); w *= np.minimum(1, np.arange(n)/(0.1*SR))
add(1.0, w, 1.2)
add(1.0, tone(523.25, 0.4, 0.15), 0.25); add(1.08, tone(783.99, 0.5, 0.2), 0.25)
# finish: bell + confetti pops + ta-da chime
tw = WIN / FPS
for k, fq in enumerate([523.25, 659.25, 783.99, 1046.5]):
    add(tw + k * 0.07, tone(fq, 1.2, 0.35, (1, 0.4, 0.2, 0.1)), 0.28)
for k in range(9):
    add(tw + 0.05 + k * 0.045 + rnd.uniform(0, 0.02), noise(0.06, 0.012, 0.7), 0.6)
add(tw + 1.4, tone(880, 0.2, 0.06, (1, 0.2)), 0.25); add(tw + 1.47, tone(1318.5, 0.25, 0.08, (1, 0.2)), 0.25)
# light ambient rolling hiss proportional to motion (subtle)
out /= max(1e-6, np.abs(out).max()) / 0.89
pcm = (out * 32767).astype(np.int16)
with wave.open("sfx.wav", "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes(pcm.tobytes())
print("ok", len(out)/SR)
