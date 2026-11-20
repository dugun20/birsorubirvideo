"""Ekran ustu yazi katmanlari: acilis baslik kancasi (hook) ve tirmanan sayac.

Kullanim (bolum dosyasinda):
    from hook import overlay, hook_title, counter
    def frame(t):
        svg = ... (normal sahne, kamera dahil)
        return overlay(svg, hook_title(t, "Grumpo vs Nibbo", "WI-FI WAR"),
                            counter(t, value, "TRY", 3, 5))   # sayac opsiyonel

Kurallar: yazi INGILIZCE, kisa (ust satir <= 22 karakter, ana satir <= 16 karakter),
sayilar rakamla. Katman ekran koordinatinda (kameradan bagimsiz) cizilir.
"""
import math, os, glob, shutil, subprocess

OL = "#221c2e"
FONT = "Fredoka"


def ensure_font():
    """Fredoka yoksa kit/fonts icinden ~/.fonts'a kurar (zamanlanmis temiz ortamlarda gerekli)."""
    try:
        if "Fredoka" in subprocess.run(["fc-list"], capture_output=True, text=True).stdout:
            return
    except FileNotFoundError:
        return
    dst = os.path.expanduser("~/.fonts")
    os.makedirs(dst, exist_ok=True)
    for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "*.woff")):
        shutil.copy(f, dst)
    subprocess.run(["fc-cache", "-f"], capture_output=True)


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _fit(text, size, maxw=960, k=0.66):
    w = len(text) * size * k
    return size if w <= maxw else size * maxw / w


def _ease_back(p):
    p = max(0.0, min(1.0, p))
    c = 1.70158
    return 1 + (c + 1) * (p - 1) ** 3 + c * (p - 1) ** 2


def _txt(x, y, text, size, fill, stroke_w, weight=700, extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-weight="{weight}" font-size="{size:.1f}" '
            f'text-anchor="middle" fill="{fill}" stroke="{OL}" stroke-width="{stroke_w}" stroke-linejoin="round" '
            f'paint-order="stroke" letter-spacing="3" word-spacing="14" {extra}>{_esc(text)}</text>')


_DEFS = ('<defs><linearGradient id="hookG" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#fff27a"/><stop offset="0.55" stop-color="#ffc21a"/>'
         '<stop offset="1" stop-color="#ff8a00"/></linearGradient></defs>')


def hook_title(t, top, main, y=330, pop=0.35, wobble=True):
    """Ust satir (beyaz, kucuk) + ana satir (sari-turuncu, buyuk). t=0'da patlayarak gelir, video boyunca kalir."""
    s = _ease_back(t / pop) if pop > 0 else 1
    s = max(s, 0.001)
    rot = 0
    if wobble and t > pop:
        rot = 1.6 * math.sin(t * 2.2)
    main_size = _fit(main, 150)
    top_size = _fit(top, 72, k=0.55)
    g = [_DEFS, f'<g transform="translate(540,{y}) rotate({rot:.2f}) scale({s:.3f})">',
         f'<g transform="translate(6,10)" opacity="0.35">{_txt(0, 0, main, main_size, OL, 26)}</g>',
         _txt(0, -main_size * 0.92, top, top_size, "#ffffff", 16, 600),
         _txt(0, 0, main, main_size, "url(#hookG)", 26),
         '</g>']
    return "".join(g)


def counter(t, value, label="", step=None, steps=None, y=560, bump_t=None):
    """Tirmanan sayac rozeti: 'LABEL 1,024' + opsiyonel ilerleme noktalari (step/steps).
    bump_t: deger degistigi an (o an rozet hafifce buyur)."""
    sc = 1.0
    if bump_t is not None and 0 <= t - bump_t < 0.25:
        sc = 1 + 0.25 * math.sin(math.pi * (t - bump_t) / 0.25)
    txt = f"{label} {value:,}" if isinstance(value, int) and label else (f"{value:,}" if isinstance(value, int) else str(value))
    if label and not isinstance(value, int):
        txt = f"{label} {value}"
    size = _fit(txt, 84, maxw=760)
    w = min(820, len(txt) * size * 0.6 + 90)
    out = [f'<g transform="translate(540,{y}) scale({sc:.3f})">',
           f'<rect x="{-w/2:.0f}" y="-62" width="{w:.0f}" height="112" rx="56" fill="{OL}" opacity="0.82"/>',
           _txt(0, 26, txt, size, "#ffffff", 0)]
    if steps:
        gap = 62
        x0 = -(steps - 1) * gap / 2
        for i in range(steps):
            done = i < (step or 0)
            out.append(f'<circle cx="{x0 + i*gap:.0f}" cy="92" r="20" fill="{"#5fd36a" if done else "#ffffff"}" '
                       f'stroke="{OL}" stroke-width="6"/>')
            if done:
                cx = x0 + i * gap
                out.append(f'<path d="M{cx-8:.0f},92 l6,6 l10,-12" fill="none" stroke="{OL}" stroke-width="5" '
                           f'stroke-linecap="round" stroke-linejoin="round"/>')
    out.append('</g>')
    return "".join(out)


def overlay(svg, *layers):
    """Katmanlari </svg>'den hemen once ekler (kamera transformunun disinda)."""
    add = "".join(l for l in layers if l)
    i = svg.rfind("</svg>")
    return svg[:i] + add + svg[i:]
