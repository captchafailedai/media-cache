"""Shared look, sprites and rendering for Captcha Failed posts (1080x1920, 30 fps)."""
import io
import math
import os
import subprocess

import cairosvg
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
FONT_PATH = "/home/claude/fonts/Bricolage.ttf"
OUT = "/home/claude/tiktok"

BG = (35, 37, 94)
DOT = (52, 54, 107)
WHITE = (246, 245, 255)
LAV = (185, 187, 230)
SUN = (255, 207, 92)
SUN_DARK = (214, 160, 40)
SHADOW = (20, 21, 58)
CARD = (250, 250, 252)
CARD_BORDER = (214, 216, 226)
INK = (43, 44, 60)
MUTED = (104, 106, 136)
TRACK = (226, 227, 238)
RED = (210, 44, 52)
SWEAT = (140, 205, 255)

CX = 520          # content centre, left of TikTok's right-hand buttons
SAFE_W = 860      # widest text line
MX, MY, M_SIZE = 257, 990, 520  # mascot placement

# ----------------------------------------------------------------- timing

def clamp01(x):
    return max(0.0, min(1.0, x))


def prog(t, a, b):
    return clamp01((t - a) / (b - a))


def ease_out_cubic(p):
    return 1 - (1 - p) ** 3


def ease_in_out_cubic(p):
    return 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


def ease_out_back(p, s=1.70158):
    p -= 1
    return 1 + (s + 1) * p ** 3 + s * p ** 2


def lerp(a, b, p):
    return a + (b - a) * p


def lerp_pt(a, b, p):
    return (lerp(a[0], b[0], p), lerp(a[1], b[1], p))


def lerp_color(a, b, p):
    return tuple(int(round(lerp(x, y, p))) for x, y in zip(a, b))


def fade_window(t, t_in, t_out, d_in=0.25, d_out=0.15):
    """Alpha for something that fades in at t_in and out at t_out."""
    return ease_out_cubic(prog(t, t_in, t_in + d_in)) * (1 - prog(t, t_out, t_out + d_out))


# ------------------------------------------------------------------ text

_fonts = {}


def font(size, wght=800):
    key = (int(size), wght)
    if key not in _fonts:
        f = ImageFont.truetype(FONT_PATH, int(size))
        vals = []
        for a in f.get_variation_axes():
            name = a.get("name")
            name = (name.decode("utf-8", "ignore") if isinstance(name, bytes) else (name or "")).lower()
            if "optical" in name:
                vals.append(max(a["minimum"], min(a["maximum"], size * 0.75)))
            elif "weight" in name:
                vals.append(wght)
            elif "width" in name:
                vals.append(100)
            else:
                vals.append(a["default"])
        f.set_variation_by_axes(vals)
        _fonts[key] = f
    return _fonts[key]


def fit_size(text, size, wght, max_w=SAFE_W):
    while size > 20 and font(size, wght).getlength(text) > max_w:
        size -= 2
    return size


PAD = 16


def text_sprite(text, size, wght, fill, max_w=None):
    if max_w:
        size = fit_size(text, size, wght, max_w)
    f = font(size, wght)
    asc, desc = f.getmetrics()
    w = int(math.ceil(f.getlength(text))) + 2 * PAD
    h = asc + desc + 2 * PAD
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((PAD, PAD + asc), text, font=f, fill=fill + (255,), anchor="ls")
    return img, PAD + asc


def wrap(text, size, wght, max_w):
    f = font(size, wght)
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if f.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------- compositing

def with_alpha(spr, a):
    if a >= 0.999:
        return spr
    s = spr.copy()
    s.putalpha(s.getchannel("A").point(lambda v: int(v * a)))
    return s


def comp(frame, spr, x, y):
    x, y = int(round(x)), int(round(y))
    sx0, sy0 = max(0, -x), max(0, -y)
    dx0, dy0 = max(0, x), max(0, y)
    w = min(spr.width - sx0, frame.width - dx0)
    h = min(spr.height - sy0, frame.height - dy0)
    if w <= 0 or h <= 0:
        return
    if sx0 or sy0 or w != spr.width or h != spr.height:
        spr = spr.crop((sx0, sy0, sx0 + w, sy0 + h))
    frame.alpha_composite(spr, (dx0, dy0))


def scaled(spr, s):
    if abs(s - 1) < 1e-3:
        return spr
    return spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.LANCZOS)


def place_text(frame, item, cx, baseline, alpha=1.0, scale=1.0):
    if alpha <= 0.003:
        return
    spr, bl = item
    s = with_alpha(scaled(spr, scale), alpha)
    comp(frame, s, cx - s.width / 2, baseline - bl * scale)


def place_center(frame, spr, cx, cy, alpha=1.0, scale=1.0, shadow=None):
    """Composite a sprite centred on (cx, cy); shadow=(dx, dy) adds a hard drop shadow."""
    if alpha <= 0.003:
        return
    s = scaled(spr, scale)
    if shadow:
        sh = with_alpha(silhouette(s, SHADOW), alpha)
        comp(frame, sh, cx - s.width / 2 + shadow[0] * scale, cy - s.height / 2 + shadow[1] * scale)
    comp(frame, with_alpha(s, alpha), cx - s.width / 2, cy - s.height / 2)


def silhouette(spr, color):
    sh = Image.new("RGBA", spr.size, color + (0,))
    sh.putalpha(spr.getchannel("A"))
    return sh


def partial_polyline(pts, p):
    segs = list(zip(pts[:-1], pts[1:]))
    lens = [math.dist(a, b) for a, b in segs]
    target = sum(lens) * p
    out = [pts[0]]
    for (a, b), L in zip(segs, lens):
        if target >= L:
            out.append(b)
            target -= L
        else:
            out.append(lerp_pt(a, b, target / L))
            break
    return out


def round_line(d, pts, color, width):
    d.line(pts, fill=color, width=int(width), joint="curve")
    r = width / 2
    for px, py in (pts[0], pts[-1]):
        d.ellipse((px - r, py - r, px + r, py + r), fill=color)


# ---------------------------------------------------------------- assets

def make_base():
    S = 2
    img = Image.new("RGBA", (W * S, H * S), BG + (255,))
    d = ImageDraw.Draw(img)
    r = 2.2 * S
    for y in range(22, H, 44):
        for x in range(22, W, 44):
            d.ellipse((x * S - r, y * S - r, x * S + r, y * S + r), fill=DOT + (255,))
    return img.resize((W, H), Image.LANCZOS)


BASE = make_base()

_BODY = (
    '<g transform="translate(14 16)" fill="#14153A">'
    '<rect x="90" y="100" width="420" height="330" rx="150" ry="150"/>'
    '<path d="M170 390C170 450 140 495 100 520C170 520 240 490 275 420Z"/></g>'
    '<g fill="#FFCF5C"><rect x="90" y="100" width="420" height="330" rx="150" ry="150"/>'
    '<path d="M170 390C170 450 140 495 100 520C170 520 240 490 275 420Z"/></g>'
    '<path d="M118 214Q136 147 205 128" fill="none" stroke="#FFFFFF" stroke-opacity="0.5" '
    'stroke-width="16" stroke-linecap="round"/>'
)
_CHEEKS = (
    '<ellipse cx="196" cy="296" rx="26" ry="15" fill="#FF8FA3" fill-opacity="0.85"/>'
    '<ellipse cx="404" cy="296" rx="26" ry="15" fill="#FF8FA3" fill-opacity="0.85"/>'
)
_INK = "#23255E"


def _eyes(dx=0, dy=0, r=None):
    if r:  # round "shocked" eyes
        return (f'<circle cx="{240+dx}" cy="{244+dy}" r="{r}" fill="{_INK}"/>'
                f'<circle cx="{360+dx}" cy="{244+dy}" r="{r}" fill="{_INK}"/>'
                f'<circle cx="{249+dx}" cy="{234+dy}" r="8" fill="#FFFFFF"/>'
                f'<circle cx="{369+dx}" cy="{234+dy}" r="8" fill="#FFFFFF"/>')
    return (f'<ellipse cx="{240+dx}" cy="{246+dy}" rx="24" ry="34" fill="{_INK}"/>'
            f'<ellipse cx="{360+dx}" cy="{246+dy}" rx="24" ry="34" fill="{_INK}"/>'
            f'<circle cx="{249+dx}" cy="{232+dy}" r="8" fill="#FFFFFF"/>'
            f'<circle cx="{369+dx}" cy="{232+dy}" r="8" fill="#FFFFFF"/>')


def _stroke(d, w=12):
    return f'<path d="{d}" fill="none" stroke="{_INK}" stroke-width="{w}" stroke-linecap="round"/>'


_SMILE = _stroke("M272 300Q300 326 328 300")
_FACES = {
    "normal": _CHEEKS + _eyes() + _SMILE,
    "look": _CHEEKS + _eyes(-9, -7) + _SMILE,
    "lookR": _CHEEKS + _eyes(9, -7) + _SMILE,
    "proud": _CHEEKS + _stroke("M214 254Q240 222 266 254", 13) + _stroke("M334 254Q360 222 386 254", 13)
    + f'<path d="M264 294Q300 350 336 294Z" fill="{_INK}"/>',
    "shock": _CHEEKS + _eyes(r=27) + f'<ellipse cx="300" cy="318" rx="15" ry="19" fill="{_INK}"/>',
    "flat": _CHEEKS + _stroke("M216 250H264", 13) + _stroke("M336 250H384", 13) + _stroke("M282 308H318"),
    "whistle": _CHEEKS + _eyes(9, -9) + f'<circle cx="308" cy="312" r="10" fill="{_INK}"/>',
}


def mascot(state="normal", size=M_SIZE):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">'
           f'<g transform="rotate(-6 300 300)">{_BODY}{_FACES[state]}</g></svg>')
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert("RGBA")


_mascots = {}


def mascot_cached(state, size=M_SIZE):
    if (state, size) not in _mascots:
        _mascots[(state, size)] = mascot(state, size)
    return _mascots[(state, size)]


def draw_mascot(frame, t, state, enter=(0.4, 1.1), hop=None, x=MX, y=MY, size=M_SIZE):
    """Mascot that slides up on enter, bobs gently, and can hop=(t0, t1). Returns its top-left y."""
    pm = prog(t, *enter)
    if pm <= 0:
        return None
    off = 560 * (1 - ease_out_back(pm))
    bob = 6 * math.sin(2 * math.pi * t / 2.2) if t > enter[1] else 0
    h = -44 * math.sin(math.pi * prog(t, *hop)) if hop else 0
    my = y + off + bob + h
    comp(frame, mascot_cached(state, size), x, my)
    return my


def sweat_sprite():
    S = 4
    w, h = 44, 64
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, r = 22 * S, 42 * S, 19 * S
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=SWEAT + (255,))
    d.polygon([(22 * S, 2 * S), (cx - 0.88 * r, cy - 0.475 * r), (cx + 0.88 * r, cy - 0.475 * r)], fill=SWEAT + (255,))
    d.ellipse((12 * S, 36 * S, 20 * S, 47 * S), fill=(255, 255, 255, 210))
    return img.resize((w, h), Image.LANCZOS)


SWEAT_SPR = sweat_sprite()


def draw_sweat(frame, t, my, t_in, t_out):
    pw = prog(t, t_in, t_in + 0.2)
    fade = 1 - prog(t, t_out, t_out + 0.2)
    if my is None or pw <= 0 or fade <= 0:
        return
    s = max(0.01, ease_out_back(pw))
    slide = 26 * ease_in_out_cubic(prog(t, t_in + 0.2, t_in + 1.5))
    spr = with_alpha(scaled(SWEAT_SPR, s), fade)
    comp(frame, spr, MX + 404 - spr.width / 2, my + 104 + slide - spr.height / 2)


def draw_sweat_at(frame, t, mx, my, size, t_in, t_out=None):
    """Sweat drop for a mascot drawn at (mx, my) with any size."""
    pw = prog(t, t_in, t_in + 0.2)
    fade = 1 - prog(t, t_out, t_out + 0.2) if t_out is not None else 1.0
    if my is None or pw <= 0 or fade <= 0:
        return
    k = size / M_SIZE
    s = max(0.01, ease_out_back(pw)) * k
    slide = 26 * k * ease_in_out_cubic(prog(t, t_in + 0.2, t_in + 1.5))
    spr = with_alpha(scaled(SWEAT_SPR, s), fade)
    comp(frame, spr, mx + 404 * k - spr.width / 2, my + 104 * k + slide - spr.height / 2)

def card(w, h, radius=26, fill=CARD, border=CARD_BORDER, border_w=2):
    S = 2
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((0, 0, w * S - 1, h * S - 1), radius=radius * S, fill=fill + (255,),
                                          outline=(border + (255,)) if border else None,
                                          width=border_w * S if border else 0)
    return img.resize((w, h), Image.LANCZOS)


def chat_bubble(text, size=60, wght=600, max_w=820, label="HUMAN"):
    """A human's message: white bubble with a tail at the bottom right and a small label above."""
    lines = wrap(text, size, wght, max_w - 88)
    f = font(size, wght)
    lh = int(size * 1.18)
    tw = max(f.getlength(s) for s in lines)
    bw, bh = int(tw + 88), int(lh * len(lines) + 56)
    S = 2
    lab = font(30, 700)
    lab_h = 48
    img = Image.new("RGBA", ((bw + 10) * S, (bh + lab_h + 40) * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    top = lab_h * S
    d.rounded_rectangle((0, top, bw * S, top + bh * S), radius=36 * S, fill=(255, 255, 255, 255))
    tx, ty = (bw - 70) * S, top + bh * S - 2
    d.polygon([(tx, ty - 30 * S), (tx + 64 * S, ty + 30 * S), (tx - 20 * S, ty)], fill=(255, 255, 255, 255))
    if label:
        d.text(((bw - 24) * S, 34 * S), label, font=font(30 * S, 700), fill=LAV + (255,), anchor="rs")
    asc = font(size * S, wght).getmetrics()[0]
    for i, s in enumerate(lines):
        d.text((44 * S, top + 28 * S + i * lh * S + asc), s, font=font(size * S, wght), fill=INK + (255,), anchor="ls")
    return img.resize((img.width // S, img.height // S), Image.LANCZOS)


def check_badge(d=64, fill=SUN, ink=BG):
    S = 4
    img = Image.new("RGBA", (d * S, d * S), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.ellipse((0, 0, d * S - 1, d * S - 1), fill=fill + (255,))
    pts = [(0.27 * d * S, 0.52 * d * S), (0.44 * d * S, 0.68 * d * S), (0.74 * d * S, 0.34 * d * S)]
    round_line(dr, pts, ink + (255,), 0.12 * d * S)
    return img.resize((d, d), Image.LANCZOS)


# ------------------------------------------------------------------ render

ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS)]


def render_video(name, draw_frame, duration, scene_len=3.0):
    """Encode one file per scene, join with the concat demuxer, return the silent mp4 path."""
    files = []
    t0, k = 0.0, 0
    while t0 < duration - 1e-6:
        t1 = min(duration, t0 + scene_len)
        part = os.path.join(OUT, f"{name}_s{k}.mp4")
        tmp = part[:-4] + ".tmp.mp4"
        n = int(round((t1 - t0) * FPS))
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"] + ENC + [tmp]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(n):
            p.stdin.write(draw_frame(t0 + i / FPS).tobytes())
        p.stdin.close()
        if p.wait() != 0:
            raise SystemExit(f"ffmpeg failed on {part}")
        os.replace(tmp, part)
        files.append(part)
        t0, k = t1, k + 1
    lst = os.path.join(OUT, f"{name}_scenes.txt")
    with open(lst, "w") as fh:
        fh.writelines(f"file '{f}'\n" for f in files)
    silent = os.path.join(OUT, f"{name}_silent.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", silent], check=True)
    return silent


def stills(name, draw_frame, times):
    paths = []
    for ts in times:
        p = os.path.join(OUT, f"{name}_still_{ts}.png")
        draw_frame(float(ts)).save(p)
        paths.append(p)
    return paths


def save_slide(img, path):
    """Write a photo-post slide. TikTok photo posts only accept JPEG or WebP, never PNG."""
    if not path.endswith(".jpg"):
        raise ValueError("slides must be saved as .jpg")
    img.convert("RGB").save(path, "JPEG", quality=95, subsampling=0, optimize=True)
    return path
