"""@birsorubirvideo bulmaca videosu render motoru (1080x1920, 30 fps)."""
import math, os, subprocess, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
A = lambda *p: os.path.join(HERE, 'assets', *p)
W, H, FPS = 1080, 1920, 30
BG = (11, 18, 36); CARD = (21, 30, 58); BORDER = (38, 50, 92)
ORANGE = (255, 124, 9); WHITE = (255, 255, 255); RED = (239, 68, 68); GREEN = (34, 197, 94)
MUTED = (150, 162, 200); LIGHT = (205, 214, 240)
FB, FM, FE = A('fonts', 'Poppins-Bold.ttf'), A('fonts', 'Poppins-Medium.ttf'), A('fonts', 'NotoColorEmoji.ttf')

_fc = {}
def font(path, size):
    if (path, size) not in _fc: _fc[(path, size)] = ImageFont.truetype(path, size)
    return _fc[(path, size)]

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in_out(x): x = clamp(x); return 3 * x * x - 2 * x * x * x
def back_out(x, s=1.9): x = clamp(x) - 1; return x * x * ((s + 1) * x + s) + 1
def prog(t, start, dur): return clamp((t - start) / dur)

_emo = {}
def emoji(ch, size):
    if (ch, size) not in _emo:
        im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((80, 80), ch, font=font(FE, 109), embedded_color=True, anchor='mm')
        im = im.crop(im.getbbox()); s = size / max(im.size)
        _emo[(ch, size)] = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    return _emo[(ch, size)]

LOGO = Image.open(A('logo.png')).convert('RGBA')
_lc = {}
def logo(h):
    h = int(h)
    if h not in _lc: _lc[h] = LOGO.resize((max(1, int(LOGO.width * h / LOGO.height)), h), Image.LANCZOS)
    return _lc[h]

def make_bg():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.exp(-(((x - W / 2) / 700) ** 2 + ((y - 820) / 900) ** 2))
    base = np.array(BG, np.float32); glow = np.array((30, 44, 92), np.float32)
    im = Image.fromarray((base + (glow - base) * g[..., None] * 0.55).clip(0, 255).astype(np.uint8), 'RGB')
    d = ImageDraw.Draw(im)
    for yy in range(40, H, 60):
        for xx in range(30, W, 60): d.ellipse((xx - 2, yy - 2, xx + 2, yy + 2), fill=(26, 36, 70))
    return im
BGIMG = make_bg()

def paste(base, im, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    if alpha <= 0.01 or scale <= 0.01: return
    if scale != 1.0: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1.0:
        im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * alpha)))
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def text_img(txt, size, color, fnt=FB):
    f = font(fnt, size); bb = f.getbbox(txt)
    im = Image.new('RGBA', (bb[2] - bb[0] + 8, bb[3] - bb[1] + 8), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4 - bb[0], 4 - bb[1]), txt, font=f, fill=color)
    return im

def hstack(parts, gap=18):
    w = sum(p.width for p in parts) + gap * (len(parts) - 1); h = max(p.height for p in parts)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); x = 0
    for p in parts: im.alpha_composite(p, (x, (h - p.height) // 2)); x += p.width + gap
    return im

def pill(content, fill, pad=(34, 18), radius=None, outline=None, ow=0):
    w, h = content.width + pad[0] * 2, content.height + pad[1] * 2
    r = radius if radius is not None else h // 2; S = 2
    big = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    ImageDraw.Draw(big).rounded_rectangle((0, 0, w * S - 1, h * S - 1), r * S, fill=fill, outline=outline, width=ow * S)
    im = big.resize((w, h), Image.LANCZOS); im.alpha_composite(content, (pad[0], pad[1]))
    return im

def check_icon(size, color):
    S = 4; im = Image.new('RGBA', (size * S, size * S), (0, 0, 0, 0))
    ImageDraw.Draw(im).line([(x * size * S, y * size * S) for x, y in [(0.18, 0.52), (0.42, 0.75), (0.84, 0.28)]],
                            fill=color, width=int(size * 0.16 * S), joint='curve')
    return im.resize((size, size), Image.LANCZOS)

def card_base(w, h):
    S = 2; big = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))
    ImageDraw.Draw(big).rounded_rectangle((0, 0, w * S - 1, h * S - 1), 44 * S, fill=CARD + (235,), outline=BORDER, width=3 * S)
    return big.resize((w, h), Image.LANCZOS)

# ---------------- audio timing ----------------
def duration(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())

def segment_starts(path, n):
    """Konuşmayı en uzun n-1 sessizlikten bölüp her parçanın başlangıç zamanını verir."""
    dur = duration(path)
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'silencedetect=n=-35dB:d=0.1', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    st = [float(v) for v in re.findall(r'silence_start: ([0-9.]+)', err)]
    en = [float(v) for v in re.findall(r'silence_end: ([0-9.]+)', err)]
    gaps = [(e - s, s, e) for s, e in zip(st, en) if s > 0.05 and e < dur - 0.05]
    if len(gaps) < n - 1:
        return [dur * i / n for i in range(n)]
    best = sorted(sorted(gaps, reverse=True)[:n - 1], key=lambda g: g[1])
    return [0.0] + [g[2] for g in best]

# ---------------- puzzle cards ----------------
class Puzzle:
    def __init__(self, p, cues, t2, cd_end):
        self.p, self.cues, self.T2, self.CD_END = p, cues, t2, cd_end
        if p['type'] == 'meyve': self._init_meyve()
        elif p['type'] == 'dizi': self._init_dizi()
        elif p['type'] == 'kare': self._init_kare()
        elif p['type'] == 'ucgen': self._init_ucgen()
        elif p['type'] == 'piramit': self._init_piramit()
        else: self._init_farkli()

    def glow(self, t):
        return 0.5 + 0.5 * math.sin((t - self.CD_END) * math.pi * 2 * 1.3 - math.pi / 2) if t > self.CD_END else 0.0

    # meyveli denklem
    def _init_meyve(self):
        def tok(s):
            if len(s) == 1 and ord(s) > 0x2500 and s not in '−×': return emoji(s, 112)
            if s.isdigit() or s == '?': return text_img(s, 100, ORANGE)
            return text_img(s, 96, WHITE)
        self.rows = [hstack([tok(s) for s in r['tokens']]) for r in self.p['rows']]
        self.cw, self.rh = 940, 168; self.ch = self.rh * 4 + 70

    def _card_meyve(self, t):
        S = 2; big = Image.new('RGBA', (self.cw * S, self.ch * S), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
        d.rounded_rectangle((0, 0, self.cw * S - 1, self.ch * S - 1), 44 * S, fill=CARD + (235,), outline=BORDER, width=3 * S)
        p4 = ease_out(prog(t, self.T2 + self.cues[3], 0.4)); g = self.glow(t)
        if p4 > 0:
            y0 = 35 + self.rh * 3 + 6
            d.rounded_rectangle((28 * S, y0 * S, (self.cw - 28) * S, (y0 + self.rh - 12) * S), 30 * S,
                                fill=(255, 124, 9, int((28 + 60 * g) * p4)), outline=(255, 124, 9, int(255 * p4)),
                                width=int((4 + 4 * g) * S))
        card = big.resize((self.cw, self.ch), Image.LANCZOS)
        for i, row in enumerate(self.rows):
            pr = prog(t, self.T2 + self.cues[i], 0.38)
            if pr > 0: paste(card, row, self.cw / 2, 35 + self.rh * i + self.rh / 2, 0.55 + 0.45 * back_out(pr), clamp(pr * 2.5))
        return card

    # sayı dizisi
    def _init_dizi(self):
        self.tw, self.th, self.gap, self.top = 250, 200, 36, 150
        self.cw = 940; self.ch = self.top + self.th * 2 + self.gap + 44
        self.title = text_img('Sıradaki sayı ne?', 52, MUTED, FM)
        self.tiles = [self._tile(s) for s in self.p['seq']]

    def _tile(self, txt, glow=0.0):
        S = 2; im = Image.new('RGBA', (self.tw * S, self.th * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        if txt == '?':
            d.rounded_rectangle((0, 0, self.tw * S - 1, self.th * S - 1), 34 * S, fill=(255, 124, 9, int(30 + 70 * glow)),
                                outline=ORANGE, width=int((5 + 4 * glow) * S))
        else:
            d.rounded_rectangle((0, 0, self.tw * S - 1, self.th * S - 1), 34 * S, fill=(30, 41, 78), outline=BORDER, width=3 * S)
        im = im.resize((self.tw, self.th), Image.LANCZOS)
        size = 116 if len(txt) <= 3 else 92
        paste(im, text_img(txt, size, ORANGE if txt == '?' else WHITE), self.tw / 2, self.th / 2 - 4)
        return im

    def _card_dizi(self, t):
        card = card_base(self.cw, self.ch)
        pt = prog(t, self.T2, 0.4)
        if pt > 0: paste(card, self.title, self.cw / 2, 80, 1.0, clamp(pt * 2))
        xs = [self.cw / 2 - self.tw - self.gap, self.cw / 2, self.cw / 2 + self.tw + self.gap]
        for i in range(6):
            pr = prog(t, self.T2 + 0.05 + 0.09 * i, 0.38)
            if pr <= 0: continue
            im = self.tiles[i]
            if i == 5 and t > self.CD_END: im = self._tile('?', self.glow(t))
            q = prog(t, self.T2 + self.cues[i + 1] - 0.05, 0.5)
            pulse = 0.24 * math.sin(math.pi * q) if 0 < q < 1 else 0.0
            cx = xs[i % 3]; cy = self.top + self.th / 2 + (i // 3) * (self.th + self.gap)
            paste(card, im, cx, cy, (0.5 + 0.5 * back_out(pr)) * (1 + pulse), clamp(pr * 2.5))
        return card

    # kare / dikdörtgen sayma
    def _init_kare(self):
        n, m = self.p['rows_n'], self.p['cols_n']
        self.step = 560 / max(n, m); self.gw, self.gh = self.step * m, self.step * n
        self.cw, self.top = 940, 150; self.ch = int(self.top + self.gh + 70)
        self.title = text_img(f"Toplam kaç {self.p['word']} var?", 52, MUTED, FM)

    def _grid(self, t):
        n, m = self.p['rows_n'], self.p['cols_n']; S, pad, lw = 2, 12, 10
        w, h = int(self.gw + pad * 2), int(self.gh + pad * 2)
        im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        lines = [('h', 0), ('h', n), ('v', 0), ('v', m)] + [('h', i) for i in range(1, n)] + [('v', j) for j in range(1, m)]
        for k, (o, i) in enumerate(lines):
            pr = ease_in_out(prog(t, self.T2 + 0.05 + 0.08 * k, 0.45))
            if pr <= 0: continue
            col = WHITE if (o == 'h' and i in (0, n)) or (o == 'v' and i in (0, m)) else LIGHT
            if o == 'h':
                y = pad + i * self.step; d.line((pad * S, y * S, (pad + self.gw * pr) * S, y * S), fill=col, width=lw * S)
            else:
                x = pad + i * self.step; d.line((x * S, pad * S, x * S, (pad + self.gh * pr) * S), fill=col, width=lw * S)
        if t > self.T2 + 0.05 + 0.08 * len(lines) + 0.45:
            for i in range(n + 1):
                for j in range(m + 1):
                    x, y = pad + j * self.step, pad + i * self.step
                    edge = i in (0, n) or j in (0, m)
                    d.rectangle(((x - lw / 2) * S, (y - lw / 2) * S, (x + lw / 2) * S, (y + lw / 2) * S), fill=WHITE if edge else LIGHT)
        return im.resize((w, h), Image.LANCZOS)

    def _card_kare(self, t):
        card = card_base(self.cw, self.ch)
        pt = prog(t, self.T2, 0.4)
        if pt > 0: paste(card, self.title, self.cw / 2, 80, 1.0, clamp(pt * 2))
        q = prog(t, self.T2 + self.cues[1] - 0.05, 0.6)
        pulse = 0.12 * math.sin(math.pi * q) if 0 < q < 1 else 0.0
        if t > self.CD_END: pulse = 0.03 * self.glow(t)
        paste(card, self._grid(t), self.cw / 2, self.top + self.gh / 2 + 10, 1 + pulse)
        return card


    # üçgen sayma
    def _init_ucgen(self):
        self.cw, self.top = 940, 150
        self.tw_, self.th_ = 720, 600
        self.ch = int(self.top + self.th_ + 80)
        self.title = text_img('Toplam kaç üçgen var?', 52, MUTED, FM)

    def _tri(self, t):
        n, hcount = self.p['cevians'], self.p['horiz']
        S, pad, lw = 2, 16, 10
        w, h = self.tw_ + pad * 2, self.th_ + pad * 2
        im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        ax, ay = pad + self.tw_ / 2, pad
        bl, br, by = pad, pad + self.tw_, pad + self.th_
        lines = [((ax, ay), (bl, by), WHITE), ((ax, ay), (br, by), WHITE), ((bl, by), (br, by), WHITE)]
        for i in range(1, n + 1):
            bx = bl + self.tw_ * i / (n + 1)
            lines.append(((ax, ay), (bx, by), LIGHT))
        for k in range(1, hcount + 1):
            f = k / (hcount + 1)
            yy = ay + (by - ay) * f
            lines.append(((ax - self.tw_ / 2 * f, yy), (ax + self.tw_ / 2 * f, yy), LIGHT))
        for k, (p0, p1, col) in enumerate(lines):
            pr = ease_in_out(prog(t, self.T2 + 0.05 + 0.1 * k, 0.45))
            if pr <= 0: continue
            x1 = p0[0] + (p1[0] - p0[0]) * pr; y1 = p0[1] + (p1[1] - p0[1]) * pr
            d.line((p0[0] * S, p0[1] * S, x1 * S, y1 * S), fill=col, width=lw * S)
            r = lw / 2
            for (x, y) in (p0, (x1, y1)):
                d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=col)
        return im.resize((w, h), Image.LANCZOS)

    def _card_ucgen(self, t):
        card = card_base(self.cw, self.ch)
        pt = prog(t, self.T2, 0.4)
        if pt > 0: paste(card, self.title, self.cw / 2, 80, 1.0, clamp(pt * 2))
        q = prog(t, self.T2 + self.cues[1] - 0.05, 0.6)
        pulse = 0.12 * math.sin(math.pi * q) if 0 < q < 1 else 0.0
        if t > self.CD_END: pulse = 0.03 * self.glow(t)
        paste(card, self._tri(t), self.cw / 2, self.top + self.th_ / 2 + 16, 1 + pulse)
        return card

    # sayı piramidi
    def _init_piramit(self):
        self.bw, self.bh, self.bg = 180, 120, 14
        self.cw, self.top = 940, 150
        self.ch = self.top + 4 * self.bh + 3 * self.bg + 60
        self.title = text_img('Her kutu = alttaki 2 kutunun toplamı', 44, MUTED, FM)

    def _cell(self, txt, glow=0.0):
        S = 2; w, h = self.bw, self.bh
        im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        if txt == '?':
            d.rounded_rectangle((0, 0, w * S - 1, h * S - 1), 26 * S, fill=(255, 124, 9, int(30 + 70 * glow)),
                                outline=ORANGE, width=int((5 + 4 * glow) * S))
        elif txt == '':
            d.rounded_rectangle((0, 0, w * S - 1, h * S - 1), 26 * S, fill=(24, 33, 64), outline=BORDER, width=3 * S)
        else:
            d.rounded_rectangle((0, 0, w * S - 1, h * S - 1), 26 * S, fill=(30, 41, 78), outline=BORDER, width=3 * S)
        im = im.resize((w, h), Image.LANCZOS)
        if txt:
            paste(im, text_img(txt, 84 if len(txt) <= 2 else 70, ORANGE if txt == '?' else WHITE), w / 2, h / 2 - 3)
        return im

    def _card_piramit(self, t):
        card = card_base(self.cw, self.ch)
        pt = prog(t, self.T2, 0.4)
        if pt > 0: paste(card, self.title, self.cw / 2, 80, 1.0, clamp(pt * 2))
        rows = self.p['rows']
        q = prog(t, self.T2 + self.cues[1] - 0.05, 0.6)
        for ri, row in enumerate(rows):
            y = self.top + (3 - ri) * (self.bh + self.bg) + self.bh / 2
            n = len(row); total = n * self.bw + (n - 1) * self.bg
            for ci, txt in enumerate(row):
                pr = prog(t, self.T2 + 0.05 + 0.18 * ri + 0.05 * ci, 0.38)
                if pr <= 0: continue
                x = self.cw / 2 - total / 2 + self.bw / 2 + ci * (self.bw + self.bg)
                g = self.glow(t) if (txt == '?' and t > self.CD_END) else 0.0
                pulse = 0.22 * math.sin(math.pi * q) if (txt == '?' and 0 < q < 1) else 0.0
                paste(card, self._cell(txt, g), x, y, (0.5 + 0.5 * back_out(pr)) * (1 + pulse), clamp(pr * 2.5))
        return card

    # farklı olanı bul
    def _init_farkli(self):
        self.cs = 82
        rows, cols = self.p['rows_n'], self.p['cols_n']
        self.cw, self.top = 940, 150
        self.gw, self.gh = cols * self.cs, rows * self.cs
        self.ch = int(self.top + 60 + self.gh + 50)
        self.title = text_img('Farklı olanı bul!', 52, MUTED, FM)
        self.emo = {}

    def _card_farkli(self, t):
        card = card_base(self.cw, self.ch)
        pt = prog(t, self.T2, 0.4)
        if pt > 0: paste(card, self.title, self.cw / 2, 80, 1.0, clamp(pt * 2))
        rows, cols = self.p['rows_n'], self.p['cols_n']
        x0 = self.cw / 2 - self.gw / 2 + 30; y0 = self.top + 60
        pa = prog(t, self.T2 + 0.05, 0.4)
        if pa > 0:
            for j in range(cols):
                paste(card, text_img(str(j + 1), 40, ORANGE), x0 + j * self.cs + self.cs / 2, y0 - 34, 1.0, clamp(pa * 2))
            for i in range(rows):
                paste(card, text_img('ABCDEFGH'[i], 38, ORANGE), x0 - 42, y0 + i * self.cs + self.cs / 2, 1.0, clamp(pa * 2))
        q = prog(t, self.T2 + self.cues[1] - 0.05, 0.6)
        pulse = 0.08 * math.sin(math.pi * q) if 0 < q < 1 else 0.0
        for i in range(rows):
            for j in range(cols):
                pr = prog(t, self.T2 + 0.1 + 0.035 * (i * cols + j) / 2, 0.3)
                if pr <= 0: continue
                ch = self.p['grid'][i][j]
                paste(card, emoji(ch, 66), x0 + j * self.cs + self.cs / 2, y0 + i * self.cs + self.cs / 2,
                      (0.5 + 0.5 * back_out(pr)) * (1 + pulse), clamp(pr * 2.5))
        return card

    def card(self, t):
        return {'meyve': self._card_meyve, 'dizi': self._card_dizi, 'kare': self._card_kare, 'ucgen': self._card_ucgen,
                'piramit': self._card_piramit, 'farkli': self._card_farkli}[self.p['type']](t)

# ---------------- video ----------------
class Video:
    def __init__(self, p, q_audio):
        self.p = p
        qd = duration(q_audio)
        self.cues = segment_starts(q_audio, p['segments'])
        self.T1, self.T2 = 0.3, 2.3
        self.T3 = self.T2 + qd + 0.35
        self.CD_LEN = 10 if p['type'] == 'farkli' else 5
        self.CD_START = self.T3 + 0.4; self.CD_END = self.CD_START + self.CD_LEN
        self.T6 = self.CD_END + 0.25
        self.BUBBLE_T, self.LABEL_T = self.T6 + 0.95, self.T6 + 2.05
        self.OUTRO = self.T6 + duration(A('audio', 's6.mp3')) + 0.45
        self.T5 = self.OUTRO + 0.3
        self.TAP = self.OUTRO + 2.4
        self.DUR = round(self.T5 + duration(A('audio', 's5.mp3')) + 0.05, 2)
        self.q_audio = q_audio
        self.puz = Puzzle(p, self.cues, self.T2, self.CD_END)
        tag = pill(text_img(f"SORU #{p['no']}", 40, WHITE), ORANGE, pad=(30, 14))
        lvl = pill(text_img(p['level'], 34, ORANGE), None, pad=(26, 14), outline=ORANGE, ow=3)
        self.HEADER = hstack([tag, lvl], gap=20)
        self.HOOK1 = text_img('Bu soruyu', 104, WHITE)
        self.HOOK2 = hstack([text_img('çözebilir misin', 104, WHITE), text_img('?', 120, ORANGE)], gap=4)
        self.CDLABEL = hstack([text_img('Cevabını yoruma yaz', 50, WHITE), emoji('\U0001F4AC', 58)], gap=16)
        self.FOLLOWLABEL = hstack([text_img('Takip etmeyi unutma', 50, WHITE), emoji('\U0001F447', 58)], gap=16)
        self.TAKIP_T = self.CD_START + 0.9
        self.TAKIP_END = self.TAKIP_T + duration(A('audio', 'takip.mp3'))
        self.STAMP = pill(text_img('SÜRE DOLDU!', 76, WHITE), RED, pad=(44, 18), radius=22)
        self.LABEL = hstack([text_img('Cevabını yorumlara yaz', 56, WHITE), emoji('\U0001F447', 62)], gap=14)
        self.FOLLOW = pill(text_img('Takip Et', 64, WHITE), ORANGE, pad=(70, 22))
        self.FOLLOWED = pill(hstack([text_img('Takip Edildi', 60, WHITE), check_icon(62, WHITE)], gap=12), GREEN, pad=(56, 24))
        self.HANDLE = text_img('@birsorubirvideo', 58, WHITE)
        self.SHARE = pill(hstack([text_img('Bu soruyu bir arkadaşına gönder', 46, WHITE), emoji('✈️', 52)], gap=12),
                          CARD + (255,), pad=(30, 16), outline=ORANGE, ow=3)
        self.NEXT = hstack([text_img('Bir sonraki soru daha zor', 54, WHITE), emoji('\U0001F449', 60)], gap=14)
        self.HAND = emoji('\U0001F446', 190)

    def countdown(self, base, t, cy):
        if t < self.CD_START - 0.3 or t > self.CD_END + 0.15: return
        pin = ease_out(prog(t, self.CD_START - 0.3, 0.3)); pout = ease_in_out(prog(t, self.CD_END, 0.15))
        alpha = pin * (1 - pout); remain = clamp(self.CD_END - t, 0, self.CD_LEN)
        n = max(1, math.ceil(remain - 1e-6)) if t < self.CD_END else 1
        col = RED if t >= self.CD_END - 2.0 else ORANGE
        S, R = 2, 150; size = R * 2 + 40
        big = Image.new('RGBA', (size * S, size * S), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
        box = (20 * S, 20 * S, (size - 20) * S, (size - 20) * S)
        d.ellipse(box, fill=CARD + (240,), outline=BORDER, width=16 * S)
        if remain > 0: d.arc(box, -90, -90 + 360 * remain / self.CD_LEN, fill=col, width=16 * S)
        im = big.resize((size, size), Image.LANCZOS)
        within = (t - self.CD_START) % 1.0 if self.CD_START <= t < self.CD_END else 1.0
        pulse = 1.0 + 0.18 * (1 - ease_out(within / 0.25)) if within < 0.25 else 1.0
        paste(im, text_img(str(n), 150, col), size / 2, size / 2 - 4, pulse)
        paste(base, im, W / 2, cy, 0.7 + 0.3 * back_out(pin), alpha)
        f_in = ease_in_out(prog(t, self.TAKIP_T, 0.25)); f_out = ease_in_out(prog(t, self.TAKIP_END - 0.1, 0.25))
        fw = f_in * (1 - f_out)
        if fw < 1: paste(base, self.CDLABEL, W / 2, cy + 225, 1.0, alpha * (1 - fw))
        if fw > 0: paste(base, self.FOLLOWLABEL, W / 2, cy + 225, 0.9 + 0.1 * back_out(f_in), alpha * fw)

    def bubble(self, t):
        w, h, S = 560, 150, 2
        big = Image.new('RGBA', ((w + 40) * S, (h + 50) * S), (0, 0, 0, 0)); d = ImageDraw.Draw(big)
        d.rounded_rectangle((0, 0, w * S, h * S), 46 * S, fill=WHITE)
        d.polygon([(70 * S, (h - 4) * S), (60 * S, (h + 40) * S), (120 * S, (h - 4) * S)], fill=WHITE)
        d.ellipse((30 * S, 35 * S, 110 * S, 115 * S), fill=ORANGE)
        im = big.resize((w + 40, h + 50), Image.LANCZOS)
        paste(im, emoji('\U0001F914', 60), 70, 75); dd = ImageDraw.Draw(im)
        for k in range(3):
            ph = (t * 2.6 - k * 0.22) % 1.0; lift = math.sin(ph * math.pi) * 14 if ph < 0.5 else 0
            cx = 200 + k * 70
            dd.ellipse((cx - 17, 75 - 17 - lift * 2, cx + 17, 75 + 17 - lift * 2), fill=(90, 100, 135, 255 if ph < 0.5 else 140))
        dd.rounded_rectangle((420, 58, 520, 92), 17, fill=(225, 229, 240))
        return im

    def timesup(self, base, t):
        if t < self.CD_END: return
        pr = prog(t, self.CD_END, 0.28); sc = 1.9 - 0.9 * ease_out(pr)
        if pr >= 1: sc = 1.0 + 0.04 * math.sin(clamp((t - self.CD_END - 0.28) / 0.25) * math.pi)
        paste(base, self.STAMP, W / 2, 1150, sc, clamp(pr * 3), -4)
        pb = prog(t, self.BUBBLE_T, 0.4)
        if pb > 0: paste(base, self.bubble(t), W / 2 + 10, 1345, 0.5 + 0.5 * back_out(pb), clamp(pb * 2.5))
        pl = prog(t, self.LABEL_T, 0.35)
        if pl > 0:
            bob = math.sin((t - self.LABEL_T) * math.pi * 2 * 1.4) * 6 if pl >= 1 else 0
            paste(base, self.LABEL, W / 2, 1500 + bob, 0.6 + 0.4 * back_out(pl), clamp(pl * 2.5))

    def outro(self, base, t):
        O, TAP = self.OUTRO, self.TAP
        pp = ease_out(prog(t, O, 0.5))
        if pp <= 0: return
        paste(base, logo(260), W / 2, 590, 0.3 + 0.7 * back_out(prog(t, O, 0.55)), clamp(pp * 2), (1 - back_out(prog(t, O, 0.55))) * 90)
        paste(base, self.HANDLE, W / 2, 790, 1.0, clamp(prog(t, O + 0.2, 0.3)))
        ps = prog(t, O + 0.3, 0.35); paste(base, self.SHARE, W / 2, 925, 0.6 + 0.4 * back_out(ps), clamp(ps * 2.5))
        pn = prog(t, O + 0.6, 0.35); paste(base, self.NEXT, W / 2, 1055, 0.7 + 0.3 * back_out(pn), clamp(pn * 2.5))
        pb = prog(t, O + 0.8, 0.35); by = 1210
        if t < TAP:
            paste(base, self.FOLLOW, W / 2, by, (0.6 + 0.4 * back_out(pb)) * (0.92 if t > TAP - 0.12 else 1.0), clamp(pb * 2.5))
        else:
            pg = prog(t, TAP, 0.3); paste(base, self.FOLLOWED, W / 2, by, 0.92 + 0.08 * back_out(pg))
            if pg < 1:
                g = Image.new('RGBA', (700, 400), (0, 0, 0, 0)); r = 40 + 260 * ease_out(pg)
                ImageDraw.Draw(g).ellipse((350 - r, 200 - r * 0.45, 350 + r, 200 + r * 0.45), outline=GREEN + (int(220 * (1 - pg)),), width=8)
                paste(base, g, W / 2, by)
        ph = ease_in_out(prog(t, O + 1.0, 0.9))
        if ph > 0:
            sx, sy, tx, ty = W + 120, H + 150, W / 2 + 70, by + 120
            hx, hy = sx + (tx - sx) * ph, sy + (ty - sy) * ph
            if t >= TAP - 0.12: hy += math.sin(clamp((t - (TAP - 0.12)) / 0.3) * math.pi) * 22
            lv = ease_in_out(prog(t, TAP + 0.4, 0.5)); hx += 300 * lv; hy += 500 * lv
            paste(base, self.HAND, hx, hy, 0.9 if TAP - 0.12 <= t <= TAP + 0.1 else 1.0)

    def frame(self, t):
        base = BGIMG.convert('RGBA')
        out_p = ease_in_out(prog(t, self.OUTRO - 0.3, 0.3))
        shrink = ease_in_out(prog(t, self.CD_START - 0.45, 0.5))
        # soru sırasında başlık + kart ekranın ortasında (kapak/ızgara için), geri sayımda yukarı çıkar
        ch = self.puz.ch
        top = 960 - (120 + ch) / 2
        hy = (top + 40) + (330 - (top + 40)) * shrink
        cy = (top + 120 + ch / 2) + (740 - (top + 120 + ch / 2)) * shrink
        li = prog(t, 0.0, 0.5); lm = ease_in_out(prog(t, 0.9, 0.5))
        if t < self.OUTRO + 0.1:
            paste(base, logo(320 + (78 - 320) * lm), W / 2 - 235 * lm, 690 + (hy - 690) * lm - 600 * out_p,
                  0.2 + 0.8 * back_out(li), clamp(li * 2) * (1 - out_p), (1 - back_out(li)) * -120)
        ha = ease_out(prog(t, 1.1, 0.4)) * (1 - out_p)
        if ha > 0: paste(base, self.HEADER, W / 2 + 40, hy - 600 * out_p, 1.0, ha)
        hin = prog(t, 0.15, 0.35); hout = ease_in_out(prog(t, 2.05, 0.35))
        if hin > 0 and hout < 1:
            y = 1180 - 180 * ease_in_out(prog(t, 0.9, 0.5)) - 120 * hout
            paste(base, self.HOOK1, W / 2, y - 70, 0.6 + 0.4 * back_out(hin), clamp(hin * 2.5) * (1 - hout))
            h2 = prog(t, 0.5, 0.35)
            paste(base, self.HOOK2, W / 2, y + 70, 0.6 + 0.4 * back_out(h2), clamp(h2 * 2.5) * (1 - hout))
        if t >= self.T2 - 0.3 and out_p < 1:
            pc = ease_out(prog(t, self.T2 - 0.3, 0.4))
            card = self.puz.card(t)
            paste(base, card, W / 2, cy + 60 * (1 - pc) - 900 * out_p,
                  (1.0 - 0.2 * shrink) * (0.92 + 0.08 * pc), pc * (1 - out_p))
        self.countdown(base, t, 1290)
        if out_p < 1:
            tmp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); self.timesup(tmp, t)
            if out_p > 0:
                tmp = tmp.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, -900 * out_p))
                tmp.putalpha(tmp.getchannel('A').point(lambda v: int(v * (1 - out_p))))
            base.alpha_composite(tmp)
        self.outro(base, t)
        return base.convert('RGB')

    def render_video(self, out):
        n = int(round(self.DUR * FPS)); tmp = out + '.part.mp4'
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                              '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                              '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
        for i in range(n): p.stdin.write(self.frame(i / FPS).tobytes())
        p.stdin.close()
        if p.wait() != 0: raise RuntimeError('ffmpeg render failed')
        os.replace(tmp, out)

    # ---------- audio ----------
    def render_audio(self, out_wav):
        import wave
        SR = 44100; N = int(SR * self.DUR); voice = np.zeros(N, np.float32); sfx = np.zeros(N, np.float32)
        rng = np.random.default_rng(7)
        def load(path):
            raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'],
                                 capture_output=True, check=True).stdout
            return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
        def put(buf, sig, t, gain=1.0):
            i = int(t * SR); j = min(N, i + len(sig))
            if j > i: buf[i:j] += sig[:j - i] * gain
        tt = lambda d: np.arange(int(SR * d)) / SR
        def pop(f0=700, f1=1100, d=0.09):
            x = tt(d); f = f0 + (f1 - f0) * x / d
            return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 38)
        def tick(f=2200, d=0.05):
            x = tt(d); return (np.sin(2 * np.pi * f * x) + 0.4 * rng.standard_normal(len(x))) * np.exp(-x * 90)
        def bell(freqs, d=0.9):
            x = tt(d); return sum(np.sin(2 * np.pi * f * x) / (k + 1) for k, f in enumerate(freqs)) * np.exp(-x * 5)
        def buzz(f=220, d=0.5):
            x = tt(d); s = np.sign(np.sin(2 * np.pi * f * x)) * 0.5 + np.sin(2 * np.pi * f * 1.5 * x) * 0.3
            return s * np.minimum(1, x / 0.01) * np.exp(-x * 7)
        def whoosh(d=0.4):
            x = tt(d); n = rng.standard_normal(len(x)); out = np.zeros_like(n); y = 0.0
            for i in range(len(n)):
                a = 0.02 + 0.25 * (i / len(n)); y += a * (n[i] - y); out[i] = y
            return out * np.sin(np.pi * x / d) ** 2 * 2.2
        def click(): x = tt(0.03); return rng.standard_normal(len(x)) * np.exp(-x * 220)

        for path, t in [(A('audio', 's1.mp3'), self.T1), (self.q_audio, self.T2), (A('audio', 's3_10.mp3' if self.CD_LEN == 10 else 's3a.wav'), self.T3),
                        (A('audio', 'takip.mp3'), self.TAKIP_T),
                        (A('audio', 's6.mp3'), self.T6), (A('audio', 's5.mp3'), self.T5)]:
            put(voice, load(path), t)
        put(sfx, whoosh(0.45), 0.0, 0.35); put(sfx, pop(), 0.15, 0.35); put(sfx, pop(800, 1300), 0.5, 0.35)
        put(sfx, whoosh(0.4), 1.95, 0.3)
        typ = self.p['type']
        if typ == 'meyve':
            for i in range(4): put(sfx, pop(650 + 80 * i, 1050 + 80 * i), self.T2 + self.cues[i], 0.4)
            put(sfx, bell((987.8, 1480), 0.5), self.T2 + self.cues[3] + 0.05, 0.12)
        elif typ == 'dizi':
            for i in range(6): put(sfx, pop(600 + 70 * i, 1000 + 70 * i, 0.07), self.T2 + 0.05 + 0.09 * i, 0.22)
            for i in range(6): put(sfx, tick(1400 + 120 * i, 0.06), self.T2 + self.cues[i + 1] - 0.05, 0.3)
        elif typ == 'kare':
            nl = self.p['rows_n'] + self.p['cols_n'] + 2
            for k in range(nl): put(sfx, tick(1300 + 90 * k, 0.05), self.T2 + 0.05 + 0.08 * k, 0.22)
            put(sfx, pop(500, 900, 0.12), self.T2 + self.cues[1], 0.35)
        elif typ == 'ucgen':
            nl = 3 + self.p['cevians'] + self.p['horiz']
            for k in range(nl): put(sfx, tick(1300 + 90 * k, 0.05), self.T2 + 0.05 + 0.1 * k, 0.22)
            put(sfx, pop(500, 900, 0.12), self.T2 + self.cues[1], 0.35)
        elif typ == 'piramit':
            for ri in range(4): put(sfx, pop(600 + 90 * ri, 1000 + 90 * ri, 0.07), self.T2 + 0.05 + 0.18 * ri, 0.3)
            put(sfx, pop(500, 900, 0.12), self.T2 + self.cues[1], 0.35)
        else:
            for k in range(0, self.p['rows_n'] * self.p['cols_n'], 6):
                put(sfx, pop(700 + 15 * k, 1100 + 15 * k, 0.05), self.T2 + 0.1 + 0.035 * k / 2, 0.18)
            put(sfx, pop(500, 900, 0.12), self.T2 + self.cues[1], 0.35)
        put(sfx, whoosh(0.35), self.CD_START - 0.45, 0.25)
        for k in range(self.CD_LEN): put(sfx, tick(2600 if k >= self.CD_LEN - 2 else 2000), self.CD_START + k, 0.45)
        put(sfx, buzz(), self.CD_END, 0.25); put(sfx, click(), self.CD_END, 0.6)
        put(sfx, pop(500, 900, 0.12), self.BUBBLE_T, 0.35); put(sfx, pop(), self.LABEL_T, 0.3)
        O = self.OUTRO
        put(sfx, whoosh(0.4), O - 0.3, 0.3); put(sfx, pop(500, 900, 0.12), O, 0.35)
        for dt in (0.3, 0.6, 0.8): put(sfx, pop(), O + dt, 0.3)
        put(sfx, click(), self.TAP - 0.1, 0.5); put(sfx, bell((1046.5, 1568), 0.9), self.TAP, 0.25)
        mix = voice + sfx * 0.9; peak = np.abs(mix).max()
        if peak > 0.98: mix *= 0.98 / peak
        pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
        with wave.open(out_wav, 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.repeat(pcm[:, None], 2, 1).tobytes())

    def build(self, out_mp4):
        vid, wav = out_mp4 + '.video.mp4', out_mp4 + '.mix.wav'
        self.render_video(vid); self.render_audio(wav); tmp = out_mp4 + '.part.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                        '-af', 'loudnorm=I=-15:TP=-1.5:LRA=11', '-ar', '44100', '-c:a', 'aac', '-b:a', '192k',
                        '-shortest', '-movflags', '+faststart', tmp], check=True)
        os.replace(tmp, out_mp4); os.remove(vid); os.remove(wav)
