"""Loud look (v2): saturated backgrounds, huge text with hard shadows, chunky outlined cards,
and a more expressive mascot. Builds on cf_lib; everything stays inside the TikTok safe band."""
from PIL import Image, ImageDraw

import cf_lib as L
from cf_lib import *  # noqa: F401,F403

COLORS = {
    "blue": (38, 84, 240),
    "magenta": (222, 40, 124),
    "purple": (118, 62, 236),
    "teal": (0, 142, 128),
    "green": (26, 150, 76),
    "red": (222, 52, 52),
    "navy": BG,
}
CYCLE = ["blue", "magenta", "purple", "teal", "red", "green"]
INK2 = (20, 21, 48)          # outlines and hard shadows
PINK = (255, 92, 170)

# ------------------------------------------------------------------ extra mascot faces

_H = "#FF4D6D"


def _heart(cx, cy, s=1.0):
    return (f'<path transform="translate({cx} {cy}) scale({s})" fill="{_H}" '
            'd="M0 18C-26 0 -34 -14 -34 -24C-34 -38 -22 -46 -12 -46C-4 -46 0 -40 0 -36'
            'C0 -40 4 -46 12 -46C22 -46 34 -38 34 -24C34 -14 26 0 0 18Z"/>')


_LID = "#FFCF5C"  # eyelids in body colour
L._FACES.update({
    "laugh": L._CHEEKS + L._stroke("M212 252Q240 214 268 252", 14) + L._stroke("M332 252Q360 214 388 252", 14)
    + f'<path d="M262 292Q300 360 338 292Z" fill="{L._INK}"/>'
    + '<path d="M282 330Q300 346 318 330Q310 318 300 318Q290 318 282 330Z" fill="#FF8FA3"/>',
    "love": L._CHEEKS + _heart(240, 262, 1.15) + _heart(360, 262, 1.15) + L._SMILE,
    "side": L._CHEEKS + L._eyes(14, 0)
    + f'<rect x="200" y="196" width="90" height="44" fill="{_LID}"/><rect x="320" y="196" width="90" height="44" fill="{_LID}"/>'
    + L._stroke("M214 240H286", 10) + L._stroke("M334 240H406", 10) + L._stroke("M288 314H326"),
    "smug": L._CHEEKS + L._eyes(0, 4)
    + f'<rect x="200" y="196" width="90" height="50" fill="{_LID}"/><rect x="320" y="196" width="90" height="50" fill="{_LID}"/>'
    + L._stroke("M212 246H288", 10) + L._stroke("M332 246H408", 10) + L._stroke("M272 304Q304 324 334 296"),
})


# ------------------------------------------------------------------ backgrounds & text

def shade(c, k):
    """k < 0 darkens, k > 0 lightens."""
    if k < 0:
        return tuple(int(v * (1 + k)) for v in c)
    return tuple(int(v + (255 - v) * k) for v in c)


_bases = {}


def base(color):
    """Dotted background in any colour (cached)."""
    if color not in _bases:
        S = 2
        img = Image.new("RGBA", (W * S, H * S), color + (255,))
        d = ImageDraw.Draw(img)
        dot = shade(color, -0.16)
        r = 2.6 * S
        for y in range(22, H, 44):
            for x in range(22, W, 44):
                d.ellipse((x * S - r, y * S - r, x * S + r, y * S + r), fill=dot + (255,))
        _bases[color] = img.resize((W, H), Image.LANCZOS)
    return _bases[color]


def loud(img, text, cx, baseline, size, color=WHITE, max_w=SAFE_W, shadow=INK2, off=(6, 8), wght=800, anchor="ms"):
    """Big text with a hard offset shadow. Returns the size actually used."""
    size = fit_size(text, size, wght, max_w)
    d = ImageDraw.Draw(img)
    f = font(size, wght)
    d.text((cx + off[0], baseline + off[1]), text, font=f, fill=shadow + (255,), anchor=anchor)
    d.text((cx, baseline), text, font=f, fill=color + (255,), anchor=anchor)
    return size


def marker(img, text, cx, baseline, size, fill=SUN, ink=INK2, tilt=-2.5, wght=800, pad=(26, 14)):
    """Text on a highlighter block, slightly tilted, centred on cx."""
    f = font(size, wght)
    w = f.getlength(text)
    asc, desc = f.getmetrics()
    S = 2
    bw, bh = int(w + 2 * pad[0]), int(asc * 0.78 + desc * 0.4 + 2 * pad[1])
    blk = Image.new("RGBA", (bw * S, bh * S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blk)
    bd.rounded_rectangle((6 * S, 8 * S, bw * S - 1, bh * S - 1), radius=12 * S, fill=INK2 + (255,))
    bd.rounded_rectangle((0, 0, bw * S - 6 * S, bh * S - 8 * S), radius=12 * S, fill=fill + (255,))
    bd.text(((bw - 6) * S / 2, (bh - 8) * S / 2 + asc * 0.39 * S), text, font=font(size * S, wght), fill=ink + (255,), anchor="ms")
    blk = blk.resize((bw, bh), Image.LANCZOS).rotate(tilt, resample=Image.BICUBIC, expand=True)
    comp(img, blk, cx - blk.width / 2, baseline - bh * 0.72 - (blk.height - bh) / 2)


def chunky(w, h, fill=CARD, radius=30, border=7, off=(10, 12)):
    """White card with a thick dark outline and a hard offset shadow (neo-brutalist)."""
    S = 2
    img = Image.new("RGBA", ((w + off[0]) * S, (h + off[1]) * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((off[0] * S, off[1] * S, (w + off[0]) * S - 1, (h + off[1]) * S - 1), radius=radius * S, fill=INK2 + (255,))
    d.rounded_rectangle((0, 0, w * S - 1, h * S - 1), radius=radius * S, fill=INK2 + (255,))
    b = border * S
    d.rounded_rectangle((b, b, w * S - 1 - b, h * S - 1 - b), radius=(radius - border) * S, fill=fill + (255,))
    return img.resize((w + off[0], h + off[1]), Image.LANCZOS)


def label(img, text, cx, baseline, size=30, color=WHITE, wght=800, spacing=3):
    """Small caps label with letter spacing, centred."""
    f = font(size, wght)
    total = sum(f.getlength(ch) for ch in text) + spacing * (len(text) - 1)
    x = cx - total / 2
    d = ImageDraw.Draw(img)
    for ch in text:
        d.text((x, baseline), ch, font=f, fill=color + (255,), anchor="ls")
        x += f.getlength(ch) + spacing


def put_mascot2(img, state, size, cx, top):
    m = mascot_cached(state, size)
    comp(img, m, cx - size / 2, top)


# ------------------------------------------------------------------ props for the Black Friday week

def is_dark(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2] < 70


_base_orig = base


def base(color):  # noqa: F811 — dark backgrounds get lighter dots instead of darker ones
    if not is_dark(color):
        return _base_orig(color)
    key = ("dark",) + color
    if key not in _bases:
        S2 = 2
        img = Image.new("RGBA", (W * S2, H * S2), color + (255,))
        d = ImageDraw.Draw(img)
        dot = shade(color, 0.10)
        r = 2.6 * S2
        for y in range(22, H, 44):
            for x in range(22, W, 44):
                d.ellipse((x * S2 - r, y * S2 - r, x * S2 + r, y * S2 + r), fill=dot + (255,))
        _bases[key] = img.resize((W, H), Image.LANCZOS)
    return _bases[key]


def burst(text, r=110, fill=SUN, ink=INK2, angle=-12, points=14, lines=None, size=None):
    """Starburst sticker with a hard shadow; returns an RGBA sprite."""
    import math as _m
    S2 = 3
    R = r * S2
    sz = int(R * 2 + 30 * S2)
    img = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = sz / 2

    def star(dx, dy):
        pts = []
        for k in range(points * 2):
            rr = R if k % 2 == 0 else R * 0.8
            a = _m.pi * k / points
            pts.append((c + dx + rr * _m.cos(a), c + dy + rr * _m.sin(a)))
        return pts
    d.polygon(star(8 * S2, 10 * S2), fill=INK2 + (255,))
    d.polygon(star(0, 0), fill=fill + (255,), outline=INK2 + (255,))
    d.line(star(0, 0) + [star(0, 0)[0]], fill=INK2 + (255,), width=5 * S2)
    rows = lines or [text]
    fs = size or min(fit_size(t, int(r * 0.62), 800, r * 1.35) for t in rows)
    lh = fs * 1.0
    y0 = c - (len(rows) - 1) * lh * S2 / 2
    for k, t in enumerate(rows):
        d.text((c, y0 + k * lh * S2), t, font=font(fs * S2, 800), fill=ink + (255,), anchor="mm")
    img = img.rotate(angle, resample=Image.BICUBIC)
    return img.resize((sz // S2, sz // S2), Image.LANCZOS)


def price_tag(text, w=300, h=130, fill=SUN, ink=INK2, angle=-8):
    """Shop price tag (pointed left end, punched hole) with a hard shadow; returns an RGBA sprite."""
    S2 = 3
    W2, H2 = (w + 40) * S2, (h + 40) * S2
    img = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def shape(dx, dy):
        x0, y0, x1, y1 = (10 + dx) * S2, (10 + dy) * S2, (10 + w + dx) * S2, (10 + h + dy) * S2
        n = h * 0.45 * S2
        return [(x0, (y0 + y1) / 2), (x0 + n, y0), (x1, y0), (x1, y1), (x0 + n, y1)]
    d.polygon(shape(8, 10), fill=INK2 + (255,))
    pts = shape(0, 0)
    d.polygon(pts, fill=fill + (255,))
    d.line(pts + [pts[0]], fill=INK2 + (255,), width=5 * S2, joint="curve")
    hx, hy = (10 + h * 0.3) * S2, (10 + h / 2) * S2
    d.ellipse((hx - 11 * S2, hy - 11 * S2, hx + 11 * S2, hy + 11 * S2), fill=(0, 0, 0, 0), outline=INK2 + (255,), width=4 * S2)
    fs = fit_size(text, int(h * 0.62), 800, w - h * 0.55 - 24)
    d.text(((10 + h * 0.45 + (w - h * 0.45) / 2) * S2, (10 + h / 2) * S2), text, font=font(fs * S2, 800), fill=ink + (255,), anchor="mm")
    img = img.rotate(angle, resample=Image.BICUBIC, expand=True)
    return img.resize((img.width // S2, img.height // S2), Image.LANCZOS)


def coffee_icon(size=160):
    """Small coffee cup on a saucer with steam (drawn, no photos)."""
    S2 = 4
    u = size * S2 / 160
    img = Image.new("RGBA", (int(160 * u), int(160 * u)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    import math as _m
    for k, x in enumerate((64, 84, 104)):  # steam: smooth wiggles
        pts = [(x * u + 6 * u * _m.sin(j / 3 + k), (50 - j * 1.8) * u) for j in range(24)]
        d.line(pts, fill=(255, 255, 255, 235), width=int(5 * u), joint="curve")
    d.ellipse((14 * u, 120 * u, 150 * u, 150 * u), fill=INK2 + (255,))
    d.ellipse((14 * u, 114 * u, 150 * u, 144 * u), fill=(244, 244, 250, 255), outline=INK2 + (255,), width=int(4 * u))
    cup = [(34 * u, 62 * u), (130 * u, 62 * u), (118 * u, 128 * u), (46 * u, 128 * u)]
    d.polygon(cup, fill=(255, 255, 255, 255))
    d.line(cup + [cup[0]], fill=INK2 + (255,), width=int(5 * u), joint="curve")
    d.rectangle((42 * u, 82 * u, 124 * u, 96 * u), fill=(214, 48, 64, 255))
    for x in range(50, 120, 16):
        d.ellipse((x * u, 86 * u, (x + 6) * u, 92 * u), fill=(255, 255, 255, 255))
    d.ellipse((36 * u, 56 * u, 128 * u, 70 * u), fill=(106, 64, 40, 255), outline=INK2 + (255,), width=int(4 * u))
    return img.resize((size, size), Image.LANCZOS)
