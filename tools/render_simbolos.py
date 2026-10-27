"""Renderiza os símbolos da home (constelação e livro de magia) em PNG com transparência.

    python tools/render_simbolos.py static/assets/site/simbolos   (precisa de numpy, scipy e Pillow; não roda no build)

As coordenadas (0–1) são as mesmas das partículas em tools/home_js.py, então a imagem
encaixa exatamente onde as partículas se juntam.
"""
import math, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter

OUT = sys.argv[1]
S = 1200
rng = random.Random(7)
nrng = np.random.default_rng(7)

ORANGE = np.array([1.0, .55, .25])
GOLD = np.array([1.0, .78, .45])
WHITE = np.array([1.0, .95, .88])


def light():
    return np.zeros((S, S, 3), np.float32)


def add_blob(L, x, y, r, color, k):
    """Brilho gaussiano somado à camada de luz."""
    x0, x1 = int(max(0, x - 4 * r)), int(min(S, x + 4 * r + 1))
    y0, y1 = int(max(0, y - 4 * r)), int(min(S, y + 4 * r + 1))
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    g = np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * r * r)) * k
    L[y0:y1, x0:x1] += g[..., None] * color


def add_mask(L, mask, color, k, blur=0):
    m = np.asarray(mask, np.float32) / 255
    if blur:
        m = gaussian_filter(m, blur)
    L += (m * k)[..., None] * color


def star4(L, x, y, r, color, k):
    """Faísca de 4 pontas: dois traços finos + núcleo."""
    m = Image.new('L', (S, S))
    d = ImageDraw.Draw(m)
    w = max(1, r * .08)
    d.polygon([(x, y - r), (x + w, y), (x, y + r), (x - w, y)], fill=255)
    d.polygon([(x - r, y), (x, y - w), (x + r, y), (x, y + w)], fill=255)
    add_mask(L, m, color, k, blur=.8)
    add_blob(L, x, y, r * .18, WHITE, k)
    add_blob(L, x, y, r * .5, color, k * .35)


def to_rgba(L, base=None):
    """Luz (somada sobre o preto) vira cor + alfa; a base sólida fica por baixo."""
    L = 1 - np.exp(-L * 1.25)  # tonemap suave: não estoura
    a = np.clip(L.max(axis=2), 0, 1)
    rgb = np.where(a[..., None] > 1e-4, L / np.maximum(a[..., None], 1e-4), 0)
    img = Image.fromarray(np.dstack([np.clip(rgb * 255, 0, 255), a * 255]).astype(np.uint8), 'RGBA')
    if base is not None:
        base = base.copy()
        base.alpha_composite(img)
        return base
    return img


def dust(L, n, cx, cy, sx, sy, k=1.0, big=.04):
    for _ in range(n):
        x = cx + nrng.normal() * sx
        y = cy + nrng.normal() * sy
        if not (0 < x < S and 0 < y < S):
            continue
        b = nrng.uniform(.25, 1) * k
        c = GOLD if nrng.random() < .55 else ORANGE
        if nrng.random() < big:
            add_blob(L, x, y, nrng.uniform(3, 6), c, b * .9)
            add_blob(L, x, y, 1.6, WHITE, b)
        else:
            add_blob(L, x, y, nrng.uniform(.8, 1.8), c, b * 1.4)


# ------------------------------------------------------------------ constelação
def constellation():
    ST = [[.08, .58], [.28, .44], [.46, .12], [.64, .44], [.56, .78], [.36, .7], [.9, .3], [.82, .72]]
    ED = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 1], [3, 6], [4, 7]]
    BIG = {1, 2, 3, 6}
    P = [(x * S, y * S) for x, y in ST]
    L = light()
    # névoa e poeira de estrelas em volta dos aglomerados (como na referência)
    for (x, y), sx, sy in [((.16, .6), .09, .07), ((.5, .5), .2, .16), ((.86, .5), .08, .14), ((.42, .2), .08, .07)]:
        add_blob(L, x * S, y * S, sx * S * 1.2, ORANGE, .05)
        dust(L, 420, x * S, y * S, sx * S, sy * S, .55)
    dust(L, 500, S * .5, S * .48, S * .32, S * .24, .35)
    # linhas: halo largo + fio fino brilhante
    for blur, width, col, k in [(6, 10, ORANGE, .22), (1.2, 3, GOLD, .9), (.6, 2, WHITE, .4)]:
        m = Image.new('L', (S, S))
        d = ImageDraw.Draw(m)
        for a, b in ED:
            d.line([P[a], P[b]], fill=255, width=width)
        add_mask(L, m, col, k, blur)
    # estrelas: halo amplo, brilho médio e núcleo quase branco
    for i, (x, y) in enumerate(P):
        s = 1.35 if i in BIG else 1
        add_blob(L, x, y, 70 * s, ORANGE, .28)
        add_blob(L, x, y, 26 * s, ORANGE, .85)
        add_blob(L, x, y, 13 * s, GOLD, 1.3)
        add_blob(L, x, y, 6.5 * s, WHITE, 2.2)
    for x, y, r in [(.46, .12, 70), (.9, .3, 46), (.28, .44, 40), (.64, .44, 52)]:
        star4(L, x * S, y * S, r, GOLD, .7)
    return to_rgba(L)


# ------------------------------------------------------------------ livro de magia
def bez(c, t):
    u = 1 - t
    return (u ** 3 * c[0] + 3 * u * u * t * c[2] + 3 * u * t * t * c[4] + t ** 3 * c[6],
            u ** 3 * c[1] + 3 * u * u * t * c[3] + 3 * u * t * t * c[5] + t ** 3 * c[7])


def curve(c, n=60):
    return [(bez(c, i / n)[0] * S, bez(c, i / n)[1] * S) for i in range(n + 1)]


def mirror(c):
    return [1 - v if i % 2 == 0 else v for i, v in enumerate(c)]


# --- livro (versão 2): perspectiva baixa, páginas douradas iluminadas a partir da lombada
TOP = [.5, .7, .42, .6, .24, .57, .05, .63]
EDGE = [.05, .63, .045, .69, .045, .75, .05, .8]
BOT = [.05, .8, .22, .77, .4, .79, .5, .87]


def book():
    yy, xx = np.mgrid[0:S, 0:S] / S
    base = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    db = ImageDraw.Draw(base)
    lower = [-.01, .85, .2, .84, .38, .88, .5, .935]
    upper = [.5, .9, .38, .83, .2, .81, .0, .82]
    cover = curve(lower) + list(reversed(curve(mirror(lower)))) + list(reversed(curve(mirror(upper)))) + curve(upper)
    db.polygon(cover, fill=(58, 22, 36, 255))
    db.line(curve(lower) + list(reversed(curve(mirror(lower)))), fill=(196, 120, 64, 255), width=3)
    pages = []
    for d in (1, -1):
        X = (lambda c: c) if d == 1 else mirror
        page = curve(X(TOP)) + curve(X(EDGE), 10) + curve(X(BOT)) + [(.5 * S, .7 * S)]
        pages.append(page)
        for j in range(5, 0, -1):  # bloco de páginas
            off = j * .0055 * S
            v = 120 + j * 14
            db.polygon([(x, y + off) for x, y in page], fill=(v + 90, v + 25, v - 50, 255))
    # papel com degradê: claro e dourado na lombada, âmbar nas bordas
    m = Image.new('L', (S, S))
    dm = ImageDraw.Draw(m)
    for p in pages:
        dm.polygon(p, fill=255)
    pm = np.asarray(m, np.float32) / 255
    t = np.clip(np.abs(xx - .5) / .45, 0, 1)
    near, far = np.array([255, 238, 200]), np.array([214, 140, 72])
    col = near * (1 - t[..., None] ** 1.2) + far * t[..., None] ** 1.2
    col *= (1 - .25 * np.exp(-((xx - .5) / .012) ** 2))[..., None]  # sombra da lombada
    arr = np.asarray(base, np.float32).copy()
    arr[..., :3] = arr[..., :3] * (1 - pm[..., None]) + col * pm[..., None]
    arr[..., 3] = np.maximum(arr[..., 3], pm * 255)
    base = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')
    db = ImageDraw.Draw(base)
    for d in (1, -1):
        X = (lambda c: c) if d == 1 else mirror
        for o in np.arange(.035, .17, .026):
            db.line(curve(X([.45, .71 + o, .38, .62 + o, .24, .6 + o, .1, .65 + o]), 40)[4:-4], fill=(170, 104, 58, 46), width=3)
        db.line(curve(X(TOP)), fill=(255, 240, 210, 255), width=3)

    L = light()
    add_blob(L, .5 * S, .66 * S, 210, ORANGE, .55)
    add_blob(L, .5 * S, .64 * S, 95, GOLD, 1.1)
    add_blob(L, .5 * S, .66 * S, 34, WHITE, 1.8)
    for k in range(11):  # feixes de luz
        mm = Image.new('L', (S, S))
        d = ImageDraw.Draw(mm)
        ang = math.radians(-90 + (k - 5) * 8 + rng.uniform(-3, 3))
        ln = rng.uniform(.3, .55) * S
        x0, y0 = .5 * S, .66 * S
        d.line([(x0, y0), (x0 + math.cos(ang) * ln, y0 + math.sin(ang) * ln)], fill=255, width=rng.randint(8, 20))
        add_mask(L, mm, GOLD, .14, blur=16)
    for _ in range(4200):  # redemoinho de faíscas, denso perto das páginas
        t = nrng.random() ** 1.5
        y = (.66 - t * .62) * S
        w = (.03 + t * .36) * S
        x = .5 * S + math.sin(t * 10 + nrng.random() * 6.28) * w * .5 + nrng.normal() * w * .32
        b = nrng.uniform(.3, 1) * (1.2 - t * .7)
        add_blob(L, x, y, nrng.uniform(.8, 2.2), GOLD if nrng.random() < .6 else ORANGE, b * 1.3)
    for _ in range(50):
        t = nrng.random()
        add_blob(L, (.5 + nrng.normal() * (.05 + t * .2)) * S, (.64 - t * .55) * S, nrng.uniform(4, 9), GOLD, .5)
    # páginas soltas, translúcidas e com borda iluminada
    for cx, cy, a, sz in [(.3, .24, -25, .06), (.72, .2, 22, .055), (.78, .44, 35, .042), (.2, .42, -40, .038), (.6, .1, 10, .032)]:
        mm = Image.new('L', (S, S))
        d = ImageDraw.Draw(mm)
        r = math.radians(a)
        w, h = sz * S, sz * S * .75
        pts = [(-w / 2, -h / 2), (w / 2, -h / 2 + h * .15), (w / 2, h / 2), (-w / 2, h / 2 - h * .1)]
        pts = [(cx * S + x * math.cos(r) - y * math.sin(r), cy * S + x * math.sin(r) + y * math.cos(r)) for x, y in pts]
        d.polygon(pts, fill=90)
        d.line(pts + [pts[0]], fill=255, width=2)
        add_mask(L, mm, WHITE, .6, blur=.8)
        add_mask(L, mm, ORANGE, .6, blur=12)
    for x, y, r in [(.5, .26, 64), (.35, .14, 36), (.66, .1, 42), (.62, .38, 30), (.37, .36, 28), (.86, .3, 30), (.13, .26, 26)]:
        star4(L, x * S, y * S, r, GOLD, .85)
    glow = pm * np.exp(-((xx - .5) / .2) ** 2) * np.exp(-((yy - .7) / .1) ** 2)
    L += (glow * .6)[..., None] * GOLD
    return to_rgba(L, base)


def fade_edges(im, bottom=True):
    """Apaga as bordas da imagem aos poucos, para não aparecer o recorte quadrado no site."""
    yy, xx = np.mgrid[0:S, 0:S] / S
    e = np.minimum.reduce([xx, 1 - xx, yy] + ([1 - yy] if bottom else []))
    k = np.clip(e / .09, 0, 1)
    k = k * k * (3 - 2 * k)
    arr = np.asarray(im, np.float32).copy()
    arr[..., 3] *= k
    return Image.fromarray(arr.astype(np.uint8), 'RGBA')


for name, fn in [('universo', constellation), ('livro', book)]:
    im = fade_edges(fn(), bottom=name != 'livro')
    im = im.resize((800, 800), Image.LANCZOS)
    im.convert('RGBA').save(f'{OUT}/{name}.webp', 'WEBP', quality=88, method=6)
    print(name, 'ok')
