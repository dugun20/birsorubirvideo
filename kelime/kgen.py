"""@ingilizcekodla kelime videosu üretici (Kelime #2 ve sonrası).
Kullanım:
  python3 kgen.py prep <no>          # audio/v<no>/tr.mp3 + en.mp3 -> parçalar
  python3 kgen.py frames <no> t1 t2  # kontrol kareleri -> check.png
  python3 kgen.py build <no>         # out/kelime-<no>.mp4 + kapak + açıklama
"""
import sys, os, subprocess, math, json, re, wave
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import (W, H, FPS, WHITE, MUTED, LIGHT, FB, FM, GREEN, text_img, pill, paste, emoji, hstack, font,
                    ease_out, ease_in_out, back_out, prog, clamp, check_icon)

HERE = os.path.dirname(os.path.abspath(__file__))
CYAN = (56, 189, 248); YEL = (250, 204, 21); ORANGE = (255, 124, 9); BGC = (12, 14, 34)
WORDS = json.load(open(os.path.join(HERE, 'data', 'words.json'), encoding='utf-8'))
OUT = os.path.join(HERE, 'out'); os.makedirs(OUT, exist_ok=True)
GAP = 0.1


def tr_upper(s):
    return s.replace('i', 'İ').replace('ı', 'I').upper()

def tr_cap(s):
    return (tr_upper(s[0]) if s[0] in 'iı' else s[0].upper()) + s[1:]

def is_emo(tok):
    return bool(tok) and not tok[0].isalnum() and ord(tok[0]) > 0x2000


# ---------------- ses hazırlama ----------------
def run(cmd): subprocess.run(cmd, check=True)

def silences(path, d=0.25, n=-38):
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', f'silencedetect=n={n}dB:d={d}', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    st = [float(v) for v in re.findall(r'silence_start: ([0-9.]+)', err)]
    en = [float(v) for v in re.findall(r'silence_end: ([0-9.]+)', err)]
    return list(zip(st, en))

def split(path, parts):
    """En uzun parts-1 sessizlikten böler, parça sınırlarını döndürür."""
    dur = E.duration(path)
    gaps = sorted([(e - s, s, e) for s, e in silences(path) if s > 0.05 and e < dur - 0.05], reverse=True)[:parts - 1]
    gaps = sorted(gaps, key=lambda g: g[1])
    if len(gaps) < parts - 1 or min(g[0] for g in gaps) < 0.7:
        raise SystemExit(f'{path}: {parts} parçaya temiz bölünemedi, boşluklar: {[(round(g[0],2)) for g in gaps]}')
    cuts = [0.0] + [x for g in gaps for x in (g[1], g[2])] + [dur]
    return [(cuts[i], cuts[i + 1]) for i in range(0, len(cuts), 2)]

CLEAN = ('silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,'
         'areverse,atempo=1.1,silenceremove=stop_periods=-1:stop_duration=0.22:stop_threshold=-38dB:stop_silence=0.16')

def prep(no):
    d = os.path.join(HERE, 'audio', f'v{no}')
    for src, names in [('tr.mp3', ['hook', 'mean', 'story', 'trans']), ('en.mp3', ['word', 'sent'])]:
        p = os.path.join(d, src)
        for (a, b), nm in zip(split(p, len(names)), names):
            run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{max(0, a - 0.02):.3f}', '-to', f'{b + 0.02:.3f}', '-i', p,
                 '-af', CLEAN, '-ar', '44100', '-ac', '1', os.path.join(d, nm + '.wav')])
            print(no, nm, round(E.duration(os.path.join(d, nm + '.wav')), 2))


# ---------------- görsel yardımcılar ----------------
def brow(parts, maxw=1000):
    """Ortak taban çizgisine hizalı satır. parts: (metin, boyut, renk[, font]) ya da ('@emoji', boyut)."""
    items = []; base = 0; caph = 0
    for p in parts:
        if p[0].startswith('@'):
            items.append(('e', p[0][1:], p[1]))
        else:
            f = font(p[3] if len(p) > 3 else FB, p[1]); asc, desc = f.getmetrics()
            base = max(base, asc); caph = max(caph, f.getbbox('H')[3] - f.getbbox('H')[1])
            items.append(('t', p[0], f, p[2], asc, desc))
    gap = 22; ims = []
    for it in items:
        if it[0] == 'e':
            ims.append(('e', emoji(it[1], it[2])))
        else:
            _, txt, f, col, asc, desc = it
            w = int(f.getlength(txt)) + 8
            im = Image.new('RGBA', (w, base + desc + 8), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((4, base + 4), txt, font=f, fill=col, anchor='ls')
            ims.append(('t', im))
    hgt = max([im.height for k, im in ims if k == 't'] + [base + 30])
    tw = sum(im.width for _, im in ims) + gap * (len(ims) - 1)
    out = Image.new('RGBA', (tw, max(hgt, max(im.height for _, im in ims) + 20)), (0, 0, 0, 0))
    x = 0; cy = base + 4 - caph / 2   # büyük harf yüksekliğinin ortası
    for k, im in ims:
        y = 0 if k == 't' else int(cy - im.height / 2)
        out.alpha_composite(im, (x, max(0, y))); x += im.width + gap
    bb = out.getbbox(); out = out.crop(bb) if bb else out
    if out.width > maxw:
        s = maxw / out.width; out = out.resize((maxw, max(1, int(out.height * s))), Image.LANCZOS)
    return out

def line(txt, size, color, fnt=FB, maxw=1000):
    toks = txt.split(' ')
    if is_emo(toks[-1]):
        return brow([(' '.join(toks[:-1]), size, color, fnt), ('@' + toks[-1], int(size * 0.95))], maxw)
    return brow([(txt, size, color, fnt)], maxw)

def make_bg():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    g1 = np.exp(-(((x - 200) / 650) ** 2 + ((y - 350) / 700) ** 2))
    g2 = np.exp(-(((x - 900) / 650) ** 2 + ((y - 1600) / 700) ** 2))
    base = np.array(BGC, np.float32)
    im = base + np.array((40, 30, 110), np.float32) * g1[..., None] * 0.6 + np.array((10, 70, 110), np.float32) * g2[..., None] * 0.5
    im = Image.fromarray(im.clip(0, 255).astype(np.uint8), 'RGB')
    d = ImageDraw.Draw(im)
    for yy in range(40, H, 64):
        for xx in range(32, W, 64): d.ellipse((xx - 2, yy - 2, xx + 2, yy + 2), fill=(30, 32, 66))
    return im.convert('RGBA')

def rounded(im, r):
    m = Image.new('L', (im.width * 2, im.height * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, m.width - 1, m.height - 1), r * 2, fill=255)
    out = im.convert('RGBA'); out.putalpha(m.resize(im.size, Image.LANCZOS)); return out

def _logo():
    src = Image.open(os.path.join(HERE, 'profil', 'profil-ingilizcekodla.png')).convert('RGB').resize((420, 420), Image.LANCZOS)
    m = Image.new('L', (840, 840), 0); ImageDraw.Draw(m).ellipse((0, 0, 839, 839), fill=255)
    out = src.convert('RGBA'); out.putalpha(m.resize((420, 420), Image.LANCZOS))
    ring = Image.new('RGBA', (440, 440), (0, 0, 0, 0))
    r2 = Image.new('RGBA', (880, 880), (0, 0, 0, 0)); ImageDraw.Draw(r2).ellipse((0, 0, 879, 879), fill=YEL)
    ring.alpha_composite(r2.resize((440, 440), Image.LANCZOS)); ring.alpha_composite(out, (10, 10))
    return ring

BG = make_bg(); LOGO_C = _logo()
HANDLE = text_img('@ingilizcekodla', 52, LIGHT, FM)
HEADER = pill(brow([('@🧠', 52), ('BUGÜNÜN KELİMESİ', 46, WHITE)]), (88, 60, 220), pad=(40, 20))
ASK = pill(brow([('Nasıl unutmayacaksın?', 56, WHITE), ('@🤔', 60)]), (30, 34, 72), pad=(40, 24))
CODE = pill(brow([('@🧠', 70), ('BEYNİNE KODLA', 78, BGC)]), YEL, pad=(46, 26))
EX_TAG = pill(text_img('ÖRNEK CÜMLE', 40, BGC), CYAN, pad=(30, 14))
OUT1 = brow([('Her gün', 72, WHITE), ('3 yeni kelime', 72, YEL)])
OUT2 = brow([('beynine kodla', 84, WHITE), ('@🧠', 84)])
OUT3 = text_img('ve unutma!', 84, YEL)
FOL = pill(text_img('Takip Et', 72, WHITE), ORANGE, pad=(80, 30))
FOLD = pill(brow([('Takip Edildi', 72, WHITE)]), GREEN, pad=(64, 30))
FOLD = pill(hstack([check_icon(64, WHITE), text_img('Takip Edildi', 72, WHITE)], 14), GREEN, pad=(64, 30))
HAND = emoji('👆', 130)
IMGSZ = 860


class Video:
    def __init__(self, no):
        self.no = no; w = self.w = WORDS[str(no)]
        d = os.path.join(HERE, 'audio', f'v{no}')
        A = lambda n: os.path.join(d, n + '.wav')
        F = lambda n: os.path.join(HERE, 'audio', 'fixed', n + '.wav')
        order = [('hook', A('hook')), ('word', A('word')), ('mean', A('mean')), ('ask', F('ask')), ('story', A('story')),
                 ('word2', A('word')), ('sent', A('sent')), ('trans', A('trans')), ('outro', F('outro')), ('takip', F('takip'))]
        self.clips = []; t = 0.15; T = {}
        for k, p in order:
            T[k] = t; self.clips.append((p, t)); t += E.duration(p) + GAP
        self.END = t - GAP + 0.08; self.T = T
        seg = lambda p, n: E.segment_starts(p, n)
        sm = seg(A('mean'), 2); ss = seg(A('story'), 4); st = seg(A('trans'), 2)
        sa = seg(F('ask'), 2); so = seg(F('outro'), 2); sh = seg(A('hook'), 2)
        self.HOOK2_T = T['hook'] + sh[1]
        self.T_TR1 = T['word'] - 0.3
        self.MEAN_T = T['mean'] + sm[1] - 0.05
        self.ASK_T = T['ask']; self.CODE_T = T['ask'] + sa[1]
        self.IMG_T = T['story'] + 0.35; self.SUB1_T = T['story'] + ss[1]; self.SUB2_T = T['story'] + ss[2]; self.PP_T = T['story'] + ss[3]
        self.TRN_T = T['trans'] + st[1]
        self.OUT_T = T['outro'] - 0.1; self.OUT2_T = T['outro'] + so[1]
        self.FOL_T = T['takip'] - 0.25; self.CLICK_T = T['takip'] + 0.55
        self.COVER = self.SUB1_T + 1.2
        # --- görseller
        W_ = w['word'].upper()
        self.TAG = pill(brow([('SIFIRDAN İNGİLİZCE', 38, WHITE), ('·', 38, YEL), (f'KELİME #{no}', 38, YEL)]), (30, 34, 72), pad=(30, 14))
        self.HS = [line(w['hs'][0], 96, WHITE), line(w['hs'][1], 96, YEL)]
        self.WORD = brow([(W_, 210, WHITE)])
        self.WORD_S = brow([(W_, 120, WHITE)])
        self.PRON = pill(brow([('@🔊', 44), (f'okunuşu: "{w["pron"]}"', 46, LIGHT, FM)]), (30, 34, 72), pad=(30, 16))
        self.MEAN = brow([('=', 90, MUTED), (w['mean'], 110, YEL), ('@' + w['me'], 96)])
        self.EQ = brow([(W_, 96, WHITE), ('≈', 96, YEL), (w['key'], 96, YEL), ('@' + w['ke'], 90)])
        self.SUB1 = pill(brow([(w['sub1'], 46, WHITE, FM)], 940), (0, 0, 0, 170), pad=(34, 20), radius=26)
        self.SUB2 = pill(brow([(f'{tr_cap(w["mean"])} deyince', 50, WHITE), ('@➡️', 46), (w['key'], 54, YEL), ('@' + w['ke'], 52)], 940),
                         (0, 0, 0, 170), pad=(34, 20), radius=26)
        self.PP = brow([(w['frag'] + '...', 100, YEL), (W_ + '!', 120, WHITE)])
        self.EX = []
        for ln in w['sent']:
            parts = [(tok, 80, YEL if tok.lower().strip('.?!') == w['hl'].lower().strip('.?!') else WHITE) for tok in ln.split(' ')]
            self.EX.append(brow(parts))
        self.TRN = brow([(w['trans'], 56, LIGHT, FM)])
        pic = Image.open(os.path.join(HERE, 'img', f'{no}.jpg')).convert('RGB').resize((IMGSZ, IMGSZ), Image.LANCZOS)
        self.PIC = pill(Image.new('RGBA', (IMGSZ, IMGSZ), (0, 0, 0, 0)), YEL, pad=(8, 8), radius=54)
        self.PIC.alpha_composite(rounded(pic, 48), (8, 8))

    def frame(self, t):
        T = self.T; im = BG.copy()
        # hook
        if t < self.T_TR1 + 0.4:
            ho = 1 - ease_in_out(prog(t, self.T_TR1 - 0.1, 0.3))
            p1 = back_out(prog(t, T['hook'] + 0.05, 0.4)); p2 = back_out(prog(t, max(T['hook'] + 0.5, self.HOOK2_T - 0.1), 0.4))
            paste(im, self.HS[0], W / 2, 860, scale=max(0.01, p1) * ho, alpha=clamp(p1) * ho)
            paste(im, self.HS[1], W / 2, 1010, scale=max(0.01, p2) * ho, alpha=clamp(p2) * ho)
            pq = back_out(prog(t, T['hook'] + 0.9, 0.4))
            if pq > 0:
                paste(im, emoji('❓', 150), W / 2, 1230, scale=max(0.01, pq) * ho, alpha=clamp(pq) * ho, rot=8 * math.sin(t * 6))
        # logo -> etiket
        TAG = self.TAG; LS, LE = 0.9, 0.55; TAG_X = W / 2 + 52; lx_end = TAG_X - TAG.width / 2 - 52
        pin = back_out(prog(t, 0.0, 0.35)); mv = ease_in_out(prog(t, LS, LE))
        lx = W / 2 + (lx_end - W / 2) * mv; ly = 500 + (300 - 500) * mv
        lsc = (0.68 + (0.25 - 0.68) * mv) * max(0.01, pin)
        if t < self.OUT_T:
            paste(im, LOGO_C, lx, ly, scale=lsc, alpha=clamp(prog(t, 0.0, 0.2)))
        paste(im, TAG, TAG_X, 300, alpha=ease_out(prog(t, LS + LE - 0.15, 0.35)))
        # sahne 1-2: kelime
        if t < T['story'] + 0.4:
            a = 1 - prog(t, T['story'] - 0.1, 0.4)
            ph = ease_out(prog(t, self.T_TR1, 0.5))
            paste(im, HEADER, W / 2, 400 - 40 * (1 - ph), alpha=ph * a)
            up = ease_in_out(prog(t, self.MEAN_T - 0.35, 0.5))
            wy = 860 - 260 * up
            ws = back_out(prog(t, T['word'] - 0.25, 0.4)) * (1 - 0.18 * up)
            if ws > 0.01:
                paste(im, self.WORD, W / 2, wy, scale=ws, alpha=a)
            paste(im, self.PRON, W / 2, wy + 175 - 30 * up, alpha=ease_out(prog(t, T['word'] + 0.1, 0.35)) * a)
            p = ease_out(prog(t, self.MEAN_T, 0.4))
            paste(im, self.MEAN, W / 2, 1000 + 40 * (1 - p), scale=0.6 + 0.4 * back_out(prog(t, self.MEAN_T, 0.4)), alpha=p * a)
            p = ease_out(prog(t, self.ASK_T, 0.4))
            paste(im, ASK, W / 2, 1250 + 40 * (1 - p), alpha=p * a)
            p = prog(t, self.CODE_T, 0.45)
            if p > 0:
                paste(im, CODE, W / 2, 1480, scale=0.4 + 0.6 * back_out(p), alpha=ease_out(p) * a, rot=-4 * (1 - ease_out(p)))
        # sahne 3: kodlama
        if T['story'] - 0.1 <= t < T['sent'] + 0.4:
            a = ease_out(prog(t, T['story'] - 0.1, 0.35)) * (1 - prog(t, T['sent'] - 0.1, 0.4))
            p = back_out(prog(t, T['story'], 0.45))
            paste(im, self.EQ, W / 2, 430, scale=0.5 + 0.5 * p if p > 0 else 0.01, alpha=a)
            p = prog(t, self.IMG_T, 0.55)
            if p > 0:
                zoom = 1 + 0.06 * clamp((t - self.IMG_T) / 8.0)
                paste(im, self.PIC, W / 2, 975, scale=(0.55 + 0.45 * back_out(p, 1.4)) * zoom * 0.98, alpha=ease_out(p) * a)
            s1 = ease_out(prog(t, self.SUB1_T, 0.3)) * (1 - prog(t, self.SUB2_T - 0.15, 0.25))
            paste(im, self.SUB1, W / 2, 1500, alpha=s1 * a)
            s2 = ease_out(prog(t, self.SUB2_T, 0.3)) * (1 - prog(t, self.PP_T - 0.15, 0.25))
            paste(im, self.SUB2, W / 2, 1500, alpha=s2 * a)
            p = prog(t, self.PP_T, 0.4)
            if p > 0:
                beat = 1 + 0.10 * math.sin(clamp((t - T['word2']) / 0.5) * math.pi) if t >= T['word2'] else 1
                paste(im, self.PP, W / 2, 1520, scale=(0.5 + 0.5 * back_out(p)) * beat, alpha=ease_out(p) * a)
        # sahne 4: örnek cümle + kapanış
        if t >= T['sent'] - 0.1:
            a = ease_out(prog(t, T['sent'] - 0.1, 0.35)) * (1 - ease_in_out(prog(t, self.OUT_T - 0.15, 0.3)))
            by = 770
            paste(im, self.WORD_S, W / 2, by - 130, alpha=a)
            paste(im, EX_TAG, W / 2, by, alpha=a)
            for i, part in enumerate(self.EX):
                pp = ease_out(prog(t, T['sent'] + i * 0.45, 0.35))
                paste(im, part, W / 2, by + 150 + i * 120 + 30 * (1 - pp), alpha=pp * a)
            pp = ease_out(prog(t, self.TRN_T, 0.35))
            paste(im, self.TRN, W / 2, by + 430 + 30 * (1 - pp), alpha=pp * a)
            pl = prog(t, self.OUT_T, 0.45)
            if pl > 0:
                paste(im, LOGO_C, W / 2, 640, scale=0.4 + 0.6 * back_out(pl), alpha=ease_out(pl))
                ph = ease_out(prog(t, self.OUT_T + 0.2, 0.35))
                paste(im, HANDLE, W / 2, 910 + 30 * (1 - ph), alpha=ph)
            p = ease_out(prog(t, self.OUT_T + 0.15, 0.4))
            paste(im, OUT1, W / 2, 1060 + 40 * (1 - p), alpha=p)
            p2 = ease_out(prog(t, self.OUT2_T, 0.35))
            paste(im, OUT2, W / 2, 1170 + 40 * (1 - p2), alpha=p2)
            p3 = prog(t, self.OUT2_T + 0.7, 0.35)
            paste(im, OUT3, W / 2, 1280, scale=0.6 + 0.4 * back_out(p3), alpha=ease_out(p3))
            pf = prog(t, self.FOL_T, 0.4)
            if pf > 0:
                C = self.CLICK_T; btn = FOLD if t >= C else FOL
                press = 1 - 0.08 * math.sin(clamp((t - C + 0.12) / 0.24) * math.pi) if C - 0.12 <= t < C + 0.12 else 1
                paste(im, btn, W / 2, 1450, scale=(0.5 + 0.5 * back_out(pf)) * press, alpha=ease_out(pf))
                hp = ease_out(prog(t, self.FOL_T + 0.35, 0.45))
                if hp > 0:
                    hy = 1600 + 140 * (1 - hp) - (25 * math.sin(clamp((t - C + 0.25) / 0.5) * math.pi) if t > C - 0.25 else 0)
                    paste(im, HAND, W / 2 + 120, hy, alpha=hp * (1 - prog(t, C + 0.35, 0.3)))
        return im.convert('RGB')

    def sfx(self, path):
        T = self.T; sr = 44100; n = int(self.END * sr); buf = np.zeros(n, np.float32)
        def add(t, sig):
            i = int(t * sr); j = min(n, i + len(sig)); buf[i:j] += sig[:j - i]
        def pop(f0=520, f1=900, d=0.12, v=0.18):
            tt = np.arange(int(d * sr)) / sr; f = f0 + (f1 - f0) * tt / d
            return (np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 28) * v).astype(np.float32)
        def whoosh(d=0.35, v=0.10):
            k = int(d * sr); noise = np.random.default_rng(1).standard_normal(k).astype(np.float32)
            return np.convolve(noise, np.ones(30) / 30, 'same') * np.sin(np.linspace(0, np.pi, k)) ** 2 * v * 3
        def ding(f=1320, d=0.6, v=0.12):
            tt = np.arange(int(d * sr)) / sr
            return ((np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * f * 2 * tt)) * np.exp(-tt * 6) * v).astype(np.float32)
        add(T['hook'], whoosh()); add(T['word'] - 0.27, pop()); add(self.MEAN_T, pop(440, 700)); add(self.CODE_T, ding())
        add(T['story'] - 0.15, whoosh()); add(self.IMG_T, pop(380, 760, 0.16, 0.2)); add(T['word2'] - 0.02, ding(1568, 0.5, 0.1))
        add(T['sent'] - 0.15, whoosh()); add(self.CLICK_T, pop(900, 1400, 0.08, 0.2))
        with wave.open(path, 'wb') as wv:
            wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(sr)
            wv.writeframes((np.clip(buf, -1, 1) * 32767).astype(np.int16).tobytes())

    def caption(self):
        w = self.w
        return (f'{w["word"].capitalize()} = {w["mean"]} {w["me"]}\n'
                f'{tr_cap(w["mean"])} deyince aklına {w["key"].replace("İ", "i").replace("I", "ı").lower()} gelsin! {w["ke"]}\n'
                f'Sen de "{w["word"]}" ile bir cümle kur, yorumlara yaz 👇')

    def build(self):
        no = self.no; mp4 = os.path.join(OUT, f'kelime-{no}.mp4'); vid = os.path.join(OUT, f'.v{no}.mp4')
        pr = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                               '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', vid],
                              stdin=subprocess.PIPE)
        for k in range(int(self.END * FPS)):
            pr.stdin.write(self.frame(k / FPS).tobytes())
        pr.stdin.close(); pr.wait()
        sx = os.path.join(OUT, f'.sfx{no}.wav'); self.sfx(sx)
        inputs = []; filt = []
        for i, (p, t) in enumerate(self.clips):
            inputs += ['-i', p]; ms = int(t * 1000)
            filt.append(f'[{i + 1}:a]aresample=44100,adelay={ms}|{ms}[a{i}]')
        inputs += ['-i', sx]; k = len(self.clips) + 1
        filt.append(f'[{k}:a]aresample=44100[sx]')
        mix = ''.join(f'[a{i}]' for i in range(len(self.clips))) + '[sx]'
        filt.append(f'{mix}amix=inputs={k}:normalize=0,loudnorm=I=-15:TP=-1.5,apad[aout]')
        run(['ffmpeg', '-v', 'error', '-y', '-i', vid] + inputs + ['-filter_complex', ';'.join(filt), '-map', '0:v', '-map', '[aout]',
             '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', mp4])
        os.remove(vid); os.remove(sx)
        self.frame(self.COVER).save(os.path.join(OUT, f'kelime-{no}.cover.jpg'), quality=90)
        info = {'no': no, 'word': self.w['word'], 'file': f'kelime/out/kelime-{no}.mp4', 'cover_ms': int(self.COVER * 1000),
                'caption': self.caption(), 'dur': round(self.END, 2)}
        json.dump(info, open(os.path.join(OUT, f'kelime-{no}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(json.dumps(info, ensure_ascii=False))


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'prep':
        for n in sys.argv[2:]: prep(int(n))
    elif cmd == 'frames':
        v = Video(int(sys.argv[2])); ts = [float(x) for x in sys.argv[3:]]
        sheet = Image.new('RGB', (360 * len(ts), 640))
        for i, t in enumerate(ts): sheet.paste(v.frame(t).resize((360, 640)), (i * 360, 0))
        sheet.save(os.path.join(HERE, 'check.png'))
        print({k: round(x, 2) for k, x in v.T.items()}, 'END', round(v.END, 2), 'COVER', round(v.COVER, 2))
    elif cmd == 'build':
        for n in sys.argv[2:]: Video(int(n)).build()
