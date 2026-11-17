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
