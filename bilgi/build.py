"""Ses + efekt miksajı ve çıktı: python3 build.py <slug> <no> <kapak_saniye>
videos/<slug>/raw.mp4 + vo.mp3 + meta.json -> out/bilgi-<no>.mp4, out/bilgi-<no>.cover.jpg, videos/<slug>/check.jpg"""
import sys, json, wave, subprocess, os
import numpy as np
from PIL import Image

slug, no, cover = sys.argv[1], sys.argv[2], float(sys.argv[3])
d = f'videos/{slug}'; meta = json.load(open(f'{d}/meta.json'))
sr = 44100; END = meta['END']; n = int(END * sr); buf = np.zeros(n, np.float32)
rng = np.random.default_rng(3)

def add(t, sig):
    i = int(t * sr); j = min(n, i + len(sig))
    if 0 <= i < n: buf[i:j] += sig[:j - i]
def tt(d): return np.arange(int(d * sr)) / sr
def whoosh(v=1):
    k = int(.45 * sr); r = rng.standard_normal(k).astype(np.float32)
    return np.convolve(r, np.ones(40) / 40, 'same') * np.sin(np.linspace(0, np.pi, k)) ** 2 * .36 * v
def boom(v=1):
    x = tt(1.4); return (np.sin(2 * np.pi * (55 - 20 * x) * x) * np.exp(-x * 3.5) * .25 * v).astype(np.float32)
def pop(v=1, f0=500, f1=900, dd=.1):
    x = tt(dd); f = f0 + (f1 - f0) * x / dd; return (np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-x * 30) * .15 * v).astype(np.float32)
def crunch(v=1):
    k = int(.5 * sr); r = rng.standard_normal(k).astype(np.float32) * (rng.random(k) > .97)
    return np.convolve(r, np.ones(6) / 6, 'same') * np.exp(-np.arange(k) / sr * 5) * .48 * v
def snap(v=1):
    x = tt(.25); return (rng.standard_normal(len(x)) * np.exp(-x * 25) * .3 * v).astype(np.float32)
def ding(v=1):
    x = tt(.6); return ((np.sin(2 * np.pi * 1320 * x) + .4 * np.sin(2 * np.pi * 2640 * x)) * np.exp(-x * 6) * .12 * v).astype(np.float32)
FX = {'whoosh': whoosh, 'boom': boom, 'pop': pop, 'pop_low': lambda v=1: pop(v, 300, 180, .25), 'crunch': crunch, 'snap': snap, 'ding': ding,
      'click': lambda v=1: pop(v, 900, 1400, .08)}
for t, kind, v in meta['SFX']:
    add(t, FX[kind](v))
with wave.open(f'{d}/sfx.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(buf, -1, 1) * 32767).astype(np.int16).tobytes())
os.makedirs('out', exist_ok=True); out = f'out/bilgi-{no}.mp4'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{d}/raw.mp4', '-i', f'{d}/vo.mp3', '-i', f'{d}/sfx.wav', '-filter_complex',
                '[1:a]aresample=44100[v];[2:a]aresample=44100[s];[v][s]amix=inputs=2:normalize=0,loudnorm=I=-15:TP=-1.5,apad[a]',
                '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(cover), '-i', out, '-frames:v', '1', f'out/bilgi-{no}.cover.jpg'], check=True)
# kontrol sayfası: 8 kare
ims = []
for i in range(8):
    p = f'{d}/.k{i}.png'; t = END * (i + .5) / 8
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', out, '-frames:v', '1', '-vf', 'scale=270:-2', p], check=True)
    ims.append(Image.open(p)); os.remove(p)
sh = Image.new('RGB', (270 * 4, 480 * 2))
for i, im in enumerate(ims): sh.paste(im, ((i % 4) * 270, (i // 4) * 480))
sh.save(f'{d}/check.jpg', quality=85)
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout)
print(json.dumps({'out': out, 'cover_ms': int(cover * 1000), 'dur': round(dur, 2)}))
