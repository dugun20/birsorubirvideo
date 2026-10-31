"""Bulmaca üreticileri. Her üretici cevabı kodla hesaplar ve doğrular."""
import random

ONES = ['', 'bir', 'iki', 'üç', 'dört', 'beş', 'altı', 'yedi', 'sekiz', 'dokuz']
TENS = ['', 'on', 'yirmi', 'otuz', 'kırk', 'elli', 'altmış', 'yetmiş', 'seksen', 'doksan']


def tr(n):
    """Sayıyı Türkçe yazıya çevirir (0-9999), seslendirme metni için."""
    if n == 0:
        return 'sıfır'
    parts = []
    th, n = divmod(n, 1000)
    if th:
        parts.append('bin' if th == 1 else tr(th) + ' bin')
    h, n = divmod(n, 100)
    if h:
        parts.append('yüz' if h == 1 else ONES[h] + ' yüz')
    t, o = divmod(n, 10)
    if t:
        parts.append(TENS[t])
    if o:
        parts.append(ONES[o])
    return ' '.join(parts)


FRUITS = [('\U0001F34E', 'elma'), ('\U0001F34C', 'muz'), ('\U0001F965', 'hindistan cevizi'),
          ('\U0001F347', 'üzüm'), ('\U0001F34A', 'portakal'), ('\U0001F353', 'çilek'),
          ('\U0001F352', 'kiraz'), ('\U0001F34D', 'ananas'), ('\U0001F95D', 'kivi'),
          ('\U0001F351', 'şeftali'), ('\U0001F349', 'karpuz'), ('\U0001F34B', 'limon')]


def meyve(rng):
    (ea, na), (eb, nb), (ec, nc) = rng.sample(FRUITS, 3)
    a = rng.randint(3, 12)
    b = rng.randint(3, 9)
    c = rng.randint(1, b - 1)
    if len({a, b, c}) < 3:
        return meyve(rng)
    vals = {'A': a, 'B': b, 'C': c}
    em = {'A': ea, 'B': eb, 'C': ec}
    nm = {'A': na, 'B': nb, 'C': nc}
    # son satır: X + Y × Z (işlem önceliği tuzağı)
    while True:
        x, y, z = rng.sample(['A', 'B', 'C'], 3)
        correct = vals[x] + vals[y] * vals[z]
        trap = (vals[x] + vals[y]) * vals[z]
        if correct != trap:
            break
    rows = [
        {'tokens': [em['A'], '+', em['A'], '+', em['A'], '=', str(3 * a)]},
        {'tokens': [em['B'], '+', em['B'], '+', em['A'], '=', str(2 * b + a)]},
        {'tokens': [em['B'], '−', em['C'], '=', str(b - c)]},
        {'tokens': [em[x], '+', em[y], '×', em[z], '=', '?']},
    ]
    # doğrulama: satırlardan değerleri geri çöz
    a2 = (3 * a) // 3
    b2 = ((2 * b + a) - a2) // 2
    c2 = b2 - (b - c)
    sol = {'A': a2, 'B': b2, 'C': c2}
    assert sol == vals and sol[x] + sol[y] * sol[z] == correct
    tts = (f"{na} artı {na} artı {na}, {tr(3 * a)} ediyor... "
           f"{nb} artı {nb} artı {na}, {tr(2 * b + a)} ediyor... "
           f"{nb} eksi {nc}, {tr(b - c)} ediyor... "
           f"Peki, {nm[x]} artı {nm[y]} çarpı {nm[z]}, kaç eder?")
    key = f"meyve:{na},{nb},{nc}:{a},{b},{c}:{x}{y}{z}"
    return dict(type='meyve', rows=rows, answer=correct, trap=trap, tts=tts[0].upper() + tts[1:],
                segments=4, level='ORTA', key=key)


def dizi(rng):
    kind = rng.choice(['x2m1', 'x2p1', 'artan_fark', 'geometrik', 'kare', 'fib', 'nn1'])
    if kind == 'x2m1':
        s = [rng.randint(2, 6)]
        f = lambda v: v * 2 - 1
        level = 'ZOR'
    elif kind == 'x2p1':
        s = [rng.randint(1, 4)]
        f = lambda v: v * 2 + 1
        level = 'ZOR'
    elif kind == 'geometrik':
        r = rng.choice([2, 3])
        s = [rng.randint(1, 3)]
        f = lambda v: v * r
        level = 'ORTA'
    if kind in ('x2m1', 'x2p1', 'geometrik'):
        while len(s) < 6:
            s.append(f(s[-1]))
    elif kind == 'artan_fark':
        d0, step = rng.randint(1, 3), rng.randint(1, 3)
        s = [rng.randint(1, 9)]
        for i in range(5):
            s.append(s[-1] + d0 + step * i)
        level = 'ORTA'
    elif kind == 'kare':
        k = rng.randint(1, 5)
        s = [(k + i) ** 2 for i in range(6)]
        level = 'ORTA'
    elif kind == 'fib':
        s = [rng.randint(1, 3), rng.randint(2, 5)]
        while len(s) < 6:
            s.append(s[-1] + s[-2])
        level = 'ZOR'
    else:  # n(n+1)
        k = rng.randint(1, 4)
        s = [(k + i) * (k + i + 1) for i in range(6)]
        level = 'ZOR'
    if s[-1] > 999 or len(set(s)) < 6:
        return dizi(rng)
    shown, answer = s[:5], s[5]
    nums = '... '.join(tr(v) for v in shown)
    tts = f"Bu sayılar, belli bir kurala göre ilerliyor... {nums}... Peki, soru işaretinin yerine hangi sayı gelmeli?"
    return dict(type='dizi', seq=[str(v) for v in shown] + ['?'], answer=answer, kind=kind,
                tts=tts, segments=7, level=level, key='dizi:' + ','.join(map(str, s)))


def kare(rng):
    n = rng.randint(2, 6)
    m = rng.randint(n, 6)
    rect = rng.random() < 0.4 and n * m <= 16
    if not rect and n * m < 9:
        return kare(rng)
    if rect:
        answer = (n * (n + 1) // 2) * (m * (m + 1) // 2)
        # kaba kuvvet doğrulama
        cnt = sum(1 for r1 in range(n + 1) for r2 in range(r1 + 1, n + 1)
                  for c1 in range(m + 1) for c2 in range(c1 + 1, m + 1))
        word = 'dikdörtgen'
    else:
        answer = sum((n - k + 1) * (m - k + 1) for k in range(1, min(n, m) + 1))
        cnt = sum(1 for r in range(n) for c in range(m) for k in range(1, min(n, m) + 1)
                  if r + k <= n and c + k <= m)
        word = 'kare'
    assert cnt == answer
    level = 'ZOR' if answer >= 20 else 'ORTA'
    tts = f"Bu şekilde, toplam kaç tane {word} var?... Dikkatli say... İlk aklına gelen cevap, yanlış olabilir!"
    return dict(type='kare', rows_n=n, cols_n=m, word=word, answer=answer, tts=tts, segments=3,
                level=level, key=f'kare:{n}x{m}:{word}')


def ucgen(rng):
    n = rng.randint(1, 5)          # tepeden tabana inen iç çizgi sayısı
    h = rng.randint(0, 3)          # yatay iç çizgi sayısı
    from math import comb
    answer = comb(n + 2, 2) * (h + 1)
    # kaba kuvvet doğrulama: tepe çizgilerinden 2'si + yatay tabanlardan 1'i
    cnt = sum(1 for i in range(n + 2) for j in range(i + 1, n + 2) for k in range(h + 1))
    assert cnt == answer
    if answer < 6:
        return ucgen(rng)
    level = 'ZOR' if answer >= 15 else 'ORTA'
    tts = "Bu şekilde, toplam kaç tane üçgen var?... Dikkatli say... İlk aklına gelen cevap, yanlış olabilir!"
    return dict(type='ucgen', cevians=n, horiz=h, answer=answer, tts=tts, segments=3, level=level,
                key=f'ucgen:{n}:{h}')


def piramit(rng):
    base = [rng.randint(1, 9) for _ in range(4)]
    rows = [base]
    while len(rows[-1]) > 1:
        r = rows[-1]
        rows.append([r[i] + r[i + 1] for i in range(len(r) - 1)])
    top = rows[-1][0]
    assert top == base[0] + 3 * base[1] + 3 * base[2] + base[3]
    variant = rng.choice(['tepe', 'taban'])
    shown = [[str(v) if i == 0 else '' for v in r] for i, r in enumerate(rows)]
    if variant == 'tepe':
        shown[-1][0] = '?'
        answer = top
        level = 'ORTA'
        tts = ("Her kutu, altındaki iki kutunun toplamına eşit... "
               "Peki, en tepedeki kutuya hangi sayı gelmeli?")
    else:
        idx = rng.choice([1, 2])
        answer = base[idx]
        shown[0][idx] = '?'
        shown[-1][0] = str(top)
        level = 'ZOR'
        # doğrulama: bilinmeyeni tepeden geri çöz
        coef = [1, 3, 3, 1]
        rest = sum(coef[i] * base[i] for i in range(4) if i != idx)
        assert (top - rest) % coef[idx] == 0 and (top - rest) // coef[idx] == answer
        tts = ("Her kutu, altındaki iki kutunun toplamına eşit... "
               f"En tepedeki sayı {tr(top)}. Peki, soru işaretinin yerine hangi sayı gelmeli?")
    return dict(type='piramit', rows=shown, answer=answer, tts=tts, segments=2, level=level,
                key='piramit:' + variant + ':' + ','.join(map(str, base)))


ODD_PAIRS = [('\U0001F600', '\U0001F603'), ('\U0001F642', '\U0001F643'), ('\U0001F552', '\U0001F553'),
             ('\U0001F316', '\U0001F317'), ('\U0001F41F', '\U0001F420'), ('\U0001F604', '\U0001F601'),
             ('\U0001F40C', '\U0001F41B'), ('\U0001F34F', '\U0001F350'), ('\U0001F31D', '\U0001F31E'),
             ('\U0001F42D', '\U0001F439')]
ROW_LETTERS = 'ABCDEFG'


def farkli(rng):
    a, b = rng.choice(ODD_PAIRS)
    if rng.random() < 0.5:
        a, b = b, a
    rows, cols = 7, 6
    r, c = rng.randrange(rows), rng.randrange(cols)
    answer = f'{ROW_LETTERS[r]}{c + 1}'
    grid = [[b if (i, j) == (r, c) else a for j in range(cols)] for i in range(rows)]
    assert sum(row.count(b) for row in grid) == 1
    tts = "Bu tablodaki emojilerden biri, diğerlerinden farklı... Onu bulabilir misin? Konumunu yorumlara yaz!"
    return dict(type='farkli', grid=grid, rows_n=rows, cols_n=cols, answer=answer, tts=tts, segments=2,
                level='ORTA', key=f'farkli:{a}{b}:{answer}')


GENERATORS = {'meyve': meyve, 'dizi': dizi, 'kare': kare, 'ucgen': ucgen, 'piramit': piramit, 'farkli': farkli}
ORDER = ['meyve', 'dizi', 'kare', 'piramit', 'ucgen', 'farkli']

CAPTION_L1 = {
    'meyve': ['Çoğu kişi bu soruda yanılıyor \U0001F440', 'İlk bakışta kolay görünüyor ama çoğu kişi yanılıyor \U0001F440',
              'Dikkatli bakmayan bu soruda yanılıyor \U0001F440'],
    'dizi': ['Sayıların gizli bir kuralı var \U0001F440', 'Bu dizinin kuralını bulan çok az \U0001F440',
             'Bu soruda çoğu kişi takılıyor \U0001F440'],
    'kare': ['İlk bakışta kolay görünüyor ama çoğu kişi yanılıyor \U0001F440', 'Herkes farklı bir sayı buluyor \U0001F440',
             'Dikkatli saymayan yanılıyor \U0001F440'],
    'ucgen': ['Herkes farklı bir sayı buluyor \U0001F440', 'Dikkatli saymayan yanılıyor \U0001F440',
              'İlk bakışta kolay görünüyor ama çoğu kişi yanılıyor \U0001F440'],
    'piramit': ['Bu piramidin kuralı basit ama çoğu kişi yanılıyor \U0001F440', 'Bu soruda çoğu kişi takılıyor \U0001F440'],
    'farkli': ['Gözüne güveniyor musun? \U0001F440', 'Farklı olanı ilk 5 saniyede bulan çok az \U0001F440'],
}


def caption(p, rng):
    l1 = rng.choice(CAPTION_L1[p['type']])
    l2 = {'kare': '\U0001F914 Sen kaç tane saydın?', 'ucgen': '\U0001F914 Sen kaç tane saydın?',
          'farkli': '\U0001F914 Sen buldun mu?'}.get(p['type'], '\U0001F914 Sen kaç buldun?')
    l3 = ('\U0001F447 Konumunu yorumlara yaz (örneğin B3), bakalım kaç kişi bulacak. \U0001F9E0' if p['type'] == 'farkli'
          else '\U0001F447 Cevabını yorumlara yaz, bakalım kaç kişi doğru bilecek. \U0001F9E0')
    return f'{l1}\n{l2}\n{l3}'


def make(no, history_keys, seed=None, ptype=None):
    rng = random.Random(seed if seed is not None else no * 7919 + 13)
    ptype = ptype or ORDER[(no - 1) % len(ORDER)]
    p = None
    for t in [ptype] + [x for x in ORDER if x != ptype]:
        for _ in range(500):
            cand = GENERATORS[t](rng)
            if cand['key'] not in history_keys:
                p = cand
                break
        if p:
            break
    if p is None:
        raise RuntimeError('yeni bulmaca bulunamadı')
    p['no'] = no
    p['caption'] = caption(p, rng)
    return p
