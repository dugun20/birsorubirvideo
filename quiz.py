"""Hızlı Bilgi Yarışması videosu: 10 soru, her biri 3 saniye, sonra doğru cevap yeşil yanar.
Kullanım: python3 quiz.py <quiz.json> <out.mp4>
quiz.json: {"no": 8, "questions": [{"q": "...", "options": ["..", "..", ".."], "answer": 1}, ...]}
"""
import json, sys, math, os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw
import engine as E
from engine import (W, H, FPS, BG, CARD, BORDER, ORANGE, WHITE, RED, GREEN, MUTED, FB, FM, A,
                    font, clamp, ease_out, ease_in_out, back_out, prog, emoji, logo, paste, text_img,
                    hstack, pill, check_icon, card_base, duration, BGIMG)

Q_LEN, REVEAL = 3.0, 1.3


def wrap(txt, size, maxw, fnt=FB):
    words, lines, cur = txt.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if font(fnt, size).getlength(t) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur)
    return lines


def text_block(txt, size, color, maxw, fnt=FB, gap=10):
    lines = [text_img(l, size, color, fnt) for l in wrap(txt, size, maxw, fnt)]
    w = max(l.width for l in lines); h = sum(l.height for l in lines) + gap * (len(lines) - 1)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); y = 0
    for l in lines: im.alpha_composite(l, ((w - l.width) // 2, y)); y += l.height + gap
    return im


class QuizVideo:
    def __init__(self, data):
        self.d = data; self.qs = data['questions']
        self.T_INTRO = 0.3
        self.Q0 = self.T_INTRO + duration(A('audio', 'quiz_intro.mp3')) + 0.3
        self.slot = Q_LEN + REVEAL
        self.QEND = self.Q0 + self.slot * len(self.qs)
        self.SCORE_T = self.QEND
        self.OUTRO = self.QEND + 0.2
        self.T5 = self.OUTRO + 0.2
        self.TAP = self.OUTRO + 3.6
        self.DUR = round(self.T5 + duration(A('audio', 'quiz_outro.mp3')) + 0.1, 2)
        tag = pill(text_img(f"SORU #{data['no']}", 40, WHITE), ORANGE, pad=(30, 14))
        lvl = pill(text_img('HIZLI YARIŞMA', 34, ORANGE), None, pad=(26, 14), outline=ORANGE, ow=3)
        self.HEADER = hstack([tag, lvl], gap=20)
        self.HOOK1 = text_img(f'{len(data["questions"])} soru', 110, WHITE)
        self.HOOK2 = hstack([text_img('3 saniye', 110, ORANGE), emoji('⏱️', 100)], gap=16)
        self.HOOK3 = text_img('Kaçını bileceksin?', 70, WHITE)
        self.qimgs = [text_block(q['q'], 68, WHITE, 820) for q in self.qs]
        # outro (engine.Video.outro ile aynı düzen)
        self.FOLLOW = pill(text_img('Takip Et', 64, WHITE), ORANGE, pad=(70, 22))
        self.FOLLOWED = pill(hstack([text_img('Takip Edildi', 60, WHITE), check_icon(62, WHITE)], gap=12), GREEN, pad=(56, 24))
        self.HANDLE = text_img('@birsorubirvideo', 58, WHITE)
        self.SHARE = pill(hstack([text_img('Kaç tane bildin? Yorumlara yaz', 46, WHITE), emoji('\U0001F447', 52)], gap=12),
                          CARD + (255,), pad=(30, 16), outline=ORANGE, ow=3)
        self.NEXT = hstack([text_img('Her gün yeni bir soru', 54, WHITE), emoji('\U0001F449', 60)], gap=14)
        self.HAND = emoji('\U0001F446', 190)
        self._opt = {}

    def option(self, i, txt, state, w=780, h=118):
        key = (i, txt, state)
        if key in self._opt: return self._opt[key]
        S = 2; im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        fill, outline, tcol = (30, 41, 78), BORDER, WHITE
        if state == 'right': fill, outline = (22, 101, 52), GREEN
        if state == 'dim': fill, tcol = (22, 30, 58), (110, 120, 155)
        d.rounded_rectangle((0, 0, w * S - 1, h * S - 1), 30 * S, fill=fill, outline=outline, width=4 * S)
        im = im.resize((w, h), Image.LANCZOS)
        badge = pill(text_img('ABC'[i], 44, WHITE if state != 'dim' else tcol), ORANGE if state != 'dim' else (50, 60, 95), pad=(22, 6), radius=18)
        im.alpha_composite(badge, (24, (h - badge.height) // 2))
        t = text_img(txt, 54, tcol)
        im.alpha_composite(t, (24 + badge.width + 26, (h - t.height) // 2))
        if state == 'right':
            c = check_icon(64, WHITE); im.alpha_composite(c, (w - 90, (h - 64) // 2))
        self._opt[key] = im
        return im

    def question(self, base, t, k):
        s = self.Q0 + k * self.slot
        if t < s - 0.05 or t >= s + self.slot: return
        q = self.qs[k]; local = t - s
        pin = ease_out(prog(t, s, 0.3))
        ch = 900
        card = card_base(940, ch)
        # ilerleme
        paste(card, text_img(f'{k + 1}/{len(self.qs)}', 46, ORANGE), 940 / 2, 70)
        S = 2; bar = Image.new('RGBA', (760 * S, 16 * S), (0, 0, 0, 0)); bd = ImageDraw.Draw(bar)
        bd.rounded_rectangle((0, 0, 760 * S - 1, 16 * S - 1), 8 * S, fill=(40, 52, 92))
        frac = clamp(1 - local / Q_LEN) if local < Q_LEN else 0
        if frac > 0:
            col = RED if local > Q_LEN - 1 else ORANGE
            bd.rounded_rectangle((0, 0, max(16, int(760 * frac)) * S - 1, 16 * S - 1), 8 * S, fill=col)
        paste(card, bar.resize((760, 16), Image.LANCZOS), 940 / 2, 130)
        qi = self.qimgs[k]
        paste(card, qi, 940 / 2, 175 + qi.height / 2)
        oy = 175 + qi.height + 60
        for i, o in enumerate(q['options']):
            po = prog(t, s + 0.12 + 0.08 * i, 0.3)
            if po <= 0: continue
            state = 'normal'
            if local >= Q_LEN: state = 'right' if i == q['answer'] else 'dim'
            pulse = 1.0
            if state == 'right':
                pr = prog(t, s + Q_LEN, 0.3); pulse = 1 + 0.06 * math.sin(math.pi * pr)
            paste(card, self.option(i, o, state), 940 / 2, oy + 59 + i * 138, (0.8 + 0.2 * back_out(po)) * pulse, clamp(po * 3))
        pout = ease_in_out(prog(t, s + self.slot - 0.2, 0.2))
        paste(base, card, W / 2 - 300 * pout, 1010, 0.9 + 0.1 * pin, pin * (1 - pout))

    def frame(self, t):
        base = BGIMG.convert('RGBA')
        out_p = ease_in_out(prog(t, self.OUTRO - 0.3, 0.3))
        if t < self.OUTRO + 0.1:
            li = prog(t, 0.0, 0.5); lm = ease_in_out(prog(t, self.Q0 - 0.6, 0.5))
            paste(base, logo(300 + (78 - 300) * lm), W / 2 - 300 * lm, 560 + (330 - 560) * lm - 600 * out_p,
                  0.2 + 0.8 * back_out(li), clamp(li * 2) * (1 - out_p))
            ha = ease_out(prog(t, self.Q0 - 0.4, 0.4)) * (1 - out_p)
            if ha > 0: paste(base, self.HEADER, W / 2 + 50, 330 - 600 * out_p, 1.0, ha)
        hin = prog(t, 0.35, 0.3); hout = ease_in_out(prog(t, self.Q0 - 0.5, 0.35))
        if hin > 0 and hout < 1:
            paste(base, self.HOOK1, W / 2, 900, 0.6 + 0.4 * back_out(hin), clamp(hin * 2.5) * (1 - hout))
            h2 = prog(t, 1.2, 0.3); paste(base, self.HOOK2, W / 2, 1060, 0.6 + 0.4 * back_out(h2), clamp(h2 * 2.5) * (1 - hout))
            h3 = prog(t, 3.4, 0.3); paste(base, self.HOOK3, W / 2, 1210, 0.6 + 0.4 * back_out(h3), clamp(h3 * 2.5) * (1 - hout))
        for k in range(len(self.qs)): self.question(base, t, k)
        E.Video.outro(self, base, t)
        return base.convert('RGB')

    def render_audio(self, out_wav):
        SR = 44100; N = int(SR * self.DUR); voice = np.zeros(N, np.float32); sfx = np.zeros(N, np.float32)
        rng = np.random.default_rng(3)
        def load(p):
            raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
            return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
        def put(buf, sig, t, g=1.0):
            i = int(t * SR); j = min(N, i + len(sig))
            if j > i: buf[i:j] += sig[:j - i] * g
        tt = lambda d: np.arange(int(SR * d)) / SR
        def pop(f0=700, f1=1100, d=0.09):
            x = tt(d); f = f0 + (f1 - f0) * x / d; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 38)
        def tick(f=2200, d=0.05):
            x = tt(d); return (np.sin(2 * np.pi * f * x) + 0.4 * rng.standard_normal(len(x))) * np.exp(-x * 90)
        def bell(fr, d=0.8):
            x = tt(d); return sum(np.sin(2 * np.pi * f * x) / (k + 1) for k, f in enumerate(fr)) * np.exp(-x * 5)
        def click(): x = tt(0.03); return rng.standard_normal(len(x)) * np.exp(-x * 220)
        put(voice, load(A('audio', 'quiz_intro.mp3')), self.T_INTRO)
        put(voice, load(A('audio', 'quiz_outro.mp3')), self.T5)
        for k in range(len(self.qs)):
            s = self.Q0 + k * self.slot
            put(sfx, pop(600, 1000), s, 0.35)
            for j in range(3): put(sfx, tick(2600 if j == 2 else 2000), s + 0.5 + j, 0.35)
            put(sfx, bell((1046.5, 1568, 2093), 0.8), s + Q_LEN, 0.25)
        put(sfx, pop(500, 900, 0.12), self.OUTRO, 0.35)
        put(sfx, click(), self.TAP - 0.1, 0.5); put(sfx, bell((1046.5, 1568), 0.9), self.TAP, 0.25)
        mix = voice + sfx * 0.9; pk = np.abs(mix).max()
        if pk > 0.98: mix *= 0.98 / pk
        pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
        with wave.open(out_wav, 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.repeat(pcm[:, None], 2, 1).tobytes())

    def build(self, out):
        vid, wav = out + '.video.mp4', out + '.mix.wav'
        n = int(round(self.DUR * FPS))
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                              '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', vid], stdin=subprocess.PIPE)
        for i in range(n): p.stdin.write(self.frame(i / FPS).tobytes())
        p.stdin.close(); assert p.wait() == 0
        self.render_audio(wav)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                        '-af', 'loudnorm=I=-15:TP=-1.5:LRA=11', '-ar', '44100', '-c:a', 'aac', '-b:a', '192k', '-shortest',
                        '-movflags', '+faststart', out + '.part.mp4'], check=True)
        os.replace(out + '.part.mp4', out); os.remove(vid); os.remove(wav)


if __name__ == '__main__':
    data = json.load(open(sys.argv[1], encoding='utf-8'))
    QuizVideo(data).build(sys.argv[2])
