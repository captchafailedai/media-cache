#!/usr/bin/env python3
"""TikTok #1 for "Captcha Failed": an AI refuses to lie on a captcha.

Usage:
  python3 make_video.py stills 2.9 6.2 ...   # full-size PNG stills at those times
  python3 make_video.py render               # scene files -> captcha_failed_01.mp4
"""
import io
import math
import os
import subprocess
import sys

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
BOX_BORDER = (142, 144, 166)
RED = (210, 44, 52)
SWEAT = (140, 205, 255)

CX = 520  # content centre line, kept left of TikTok's right-hand buttons

# ---------------------------------------------------------------- helpers

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


_fonts = {}


def font(size, wght=800):
    key = (size, wght)
    if key not in _fonts:
        f = ImageFont.truetype(FONT_PATH, size)
        vals = []
        for a in f.get_variation_axes():
            name = a.get("name")
            if isinstance(name, bytes):
                name = name.decode("utf-8", "ignore")
            name = (name or "").lower()
            if "optical" in name:
                v = max(a["minimum"], min(a["maximum"], size * 0.75))
            elif "weight" in name:
                v = wght
            elif "width" in name:
                v = 100
            else:
                v = a["default"]
            vals.append(v)
        f.set_variation_by_axes(vals)
        _fonts[key] = f
    return _fonts[key]


PAD = 16


def text_sprite(text, size, wght, fill):
    f = font(size, wght)
    asc, desc = f.getmetrics()
    w = int(math.ceil(f.getlength(text))) + 2 * PAD
    h = asc + desc + 2 * PAD
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((PAD, PAD + asc), text, font=f, fill=fill + (255,), anchor="ls")
    return img, PAD + asc  # sprite, baseline y inside sprite


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


# ---------------------------------------------------------------- assets

def make_base():
    S = 2
    img = Image.new("RGBA", (W * S, H * S), BG + (255,))
    d = ImageDraw.Draw(img)
    for y in range(22, H, 44):
        for x in range(22, W, 44):
            r = 2.2 * S
            d.ellipse((x * S - r, y * S - r, x * S + r, y * S + r), fill=DOT + (255,))
    return img.resize((W, H), Image.LANCZOS)


BODY = (
    '<g transform="translate(14 16)" fill="#14153A">'
    '<rect x="90" y="100" width="420" height="330" rx="150" ry="150"/>'
    '<path d="M170 390C170 450 140 495 100 520C170 520 240 490 275 420Z"/></g>'
    '<g fill="#FFCF5C"><rect x="90" y="100" width="420" height="330" rx="150" ry="150"/>'
    '<path d="M170 390C170 450 140 495 100 520C170 520 240 490 275 420Z"/></g>'
    '<path d="M118 214Q136 147 205 128" fill="none" stroke="#FFFFFF" stroke-opacity="0.5" '
    'stroke-width="16" stroke-linecap="round"/>'
)
CHEEKS = (
    '<ellipse cx="196" cy="296" rx="26" ry="15" fill="#FF8FA3" fill-opacity="0.85"/>'
    '<ellipse cx="404" cy="296" rx="26" ry="15" fill="#FF8FA3" fill-opacity="0.85"/>'
)
SMILE = '<path d="M272 300Q300 326 328 300" fill="none" stroke="#23255E" stroke-width="12" stroke-linecap="round"/>'
PROUD = (
    '<path d="M214 254Q240 222 266 254" fill="none" stroke="#23255E" stroke-width="13" stroke-linecap="round"/>'
    '<path d="M334 254Q360 222 386 254" fill="none" stroke="#23255E" stroke-width="13" stroke-linecap="round"/>'
    '<path d="M264 294Q300 350 336 294Z" fill="#23255E"/>'
)


def eyes(dx=0, dy=0):
    return (
        f'<ellipse cx="{240+dx}" cy="{246+dy}" rx="24" ry="34" fill="#23255E"/>'
        f'<ellipse cx="{360+dx}" cy="{246+dy}" rx="24" ry="34" fill="#23255E"/>'
        f'<circle cx="{249+dx}" cy="{232+dy}" r="8" fill="#FFFFFF"/>'
        f'<circle cx="{369+dx}" cy="{232+dy}" r="8" fill="#FFFFFF"/>'
    )


def mascot(state, size):
    face = {
        "normal": CHEEKS + eyes() + SMILE,
        "look": CHEEKS + eyes(-9, -7) + SMILE,
        "proud": CHEEKS + PROUD,
    }[state]
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="600" height="600">'
        f'<g transform="rotate(-6 300 300)">{BODY}{face}</g></svg>'
    )
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def cursor_sprite(scale=2.6):
    S = 4
    pts = [(0, 0), (0, 30), (7.5, 23), (12.5, 35), (17, 33), (12, 21.5), (21.5, 21.5)]
    m = 3
    w, h = int((21.5 + 2 * m) * scale * S), int((35 + 2 * m) * scale * S)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    P = [((x + m) * scale * S, (y + m) * scale * S) for x, y in pts]
    d.polygon(P, fill=(255, 255, 255, 255), outline=(17, 17, 24, 255), width=int(1.3 * scale * S))
    img = img.resize((w // S, h // S), Image.LANCZOS)
    return img, (m * scale, m * scale)


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


def stamp_sprite(k=0.85):
    S = 2
    w, h = int(700 * k), int(150 * k)
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w * S - 1, h * S - 1), radius=int(16 * k * S), fill=RED + (255,))
    inset = int(11 * k * S)
    d.rounded_rectangle((inset, inset, w * S - 1 - inset, h * S - 1 - inset), radius=int(10 * k * S),
                        outline=(255, 255, 255, 190), width=3 * S)
    f = font(int(78 * k * S), 800)
    d.text((w * S / 2, h * S / 2 + 4 * k * S), "ACCESS DENIED", font=f, fill=(255, 255, 255, 255), anchor="mm")
    img = img.resize((w, h), Image.LANCZOS)
    return img.rotate(6, resample=Image.BICUBIC, expand=True)


# Card geometry (frame coordinates)
CARD_X, CARD_Y, CARD_W, CARD_H = 110, 600, 820, 200
BOX = (160, 662, 236, 738)
BOX_C = ((BOX[0] + BOX[2]) / 2, (BOX[1] + BOX[3]) / 2)
LABEL_X, LABEL_BASE, LABEL_SIZE = 276, 720, 56
CHECK = [(177, 702), (193, 719), (222, 682)]

_card_cache = {}


def card_sprite(strike_p, morph_p, check_p, fill_p):
    key = tuple(round(v, 2) for v in (strike_p, morph_p, check_p, fill_p))
    if key in _card_cache:
        return _card_cache[key]
    strike_p, morph_p, check_p, fill_p = key
    S = 2
    img = Image.new("RGBA", (CARD_W * S, CARD_H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, CARD_W * S - 1, CARD_H * S - 1), radius=14 * S, fill=CARD + (255,),
                        outline=CARD_BORDER + (255,), width=2 * S)

    def rel(p):
        return ((p[0] - CARD_X) * S, (p[1] - CARD_Y) * S)

    b0, b1 = rel(BOX[:2]), rel(BOX[2:])
    d.rounded_rectangle((b0[0], b0[1], b1[0], b1[1]), radius=8 * S,
                        fill=lerp_color((255, 255, 255), SUN, fill_p) + (255,),
                        outline=lerp_color(BOX_BORDER, SUN_DARK, fill_p) + (255,), width=4 * S)
    if check_p > 0:
        pts = [rel(p) for p in partial_polyline(CHECK, check_p)]
        lw = 11 * S
        d.line(pts, fill=BG + (255,), width=lw, joint="curve")
        for px, py in (pts[0], pts[-1]):
            d.ellipse((px - lw / 2, py - lw / 2, px + lw / 2, py + lw / 2), fill=BG + (255,))

    f = font(LABEL_SIZE * S, 560)
    lx, lb = (LABEL_X - CARD_X) * S, (LABEL_BASE - CARD_Y) * S
    if morph_p < 1:
        a = Image.new("RGBA", img.size, (0, 0, 0, 0))
        da = ImageDraw.Draw(a)
        da.text((lx, lb), "I’m not a robot", font=f, fill=INK + (255,), anchor="ls")
        if strike_p > 0:
            x0 = lx + f.getlength("I’m ") - 4 * S
            x1 = x0 + (f.getlength("not") + 8 * S) * strike_p
            y = lb - 0.27 * LABEL_SIZE * S
            da.line((x0, y, x1, y), fill=RED + (255,), width=7 * S)
        img.alpha_composite(with_alpha(a, 1 - morph_p))
    if morph_p > 0:
        b = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(b).text((lx, lb), "I’m a robot", font=f, fill=INK + (255,), anchor="ls")
        img.alpha_composite(with_alpha(b, morph_p))
    out = img.resize((CARD_W, CARD_H), Image.LANCZOS)
    _card_cache[key] = out
    return out


def card_shadow():
    img = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle((0, 0, CARD_W - 1, CARD_H - 1), radius=14, fill=SHADOW + (255,))
    return img


# ---------------------------------------------------------------- scene

BASE = make_base()
HOOK1 = text_sprite("POV: you’re an AI", 84, 800, WHITE)
HOOK2 = text_sprite("and a website asks you this:", 54, 600, LAV)
CAP1 = text_sprite("I could just click it…", 64, 800, WHITE)
CAP2 = text_sprite("but I don’t lie.", 64, 800, WHITE)
CAP3 = text_sprite("worth it.", 110, 800, SUN)

M_SIZE = 520
MX, MY = 257, 990
MASCOT = {s: mascot(s, M_SIZE) for s in ("normal", "look", "proud")}
CURSOR, HOT = cursor_sprite()
CURSOR_SH = with_alpha(silhouette(CURSOR, SHADOW), 0.55)
SWEAT_SPR = sweat_sprite()
STAMP = stamp_sprite()
STAMP_SH = silhouette(STAMP, SHADOW)
CARD_SH = card_shadow()

C0, C1, C1B, C2 = (860, 1330), (300, 792), (258, 764), (BOX_C[0] - 2, BOX_C[1] - 2)
C3 = (262, 772)  # drifts off the box after the click so the tick shows
STAMP_C = (565, 795)


def cursor_pos(t):
    if t < 1.3:
        return C0
    if t < 2.8:
        return lerp_pt(C0, C1, ease_in_out_cubic(prog(t, 1.3, 2.8)))
    if 3.2 <= t < 4.6:
        q = (t - 3.2) / 1.4
        return lerp_pt(C1, C1B, 0.5 * (1 - math.cos(2 * math.pi * 2 * q)))
    if t < 7.6:
        return C1
    if t < 7.95:
        return lerp_pt(C1, C2, ease_in_out_cubic(prog(t, 7.6, 7.95)))
    if t < 8.12:
        return C2
    return lerp_pt(C2, C3, ease_out_cubic(prog(t, 8.12, 8.45)))


def draw_frame(t):
    fr = BASE.copy()

    # hook
    # hook is readable from frame 0: viewers decide in the first second
    p = ease_out_cubic(prog(t, 0.0, 0.3))
    place_text(fr, HOOK1, CX, 318 - 24 * (1 - p))
    place_text(fr, HOOK2, CX, 400 - 24 * (1 - p))

    # card
    pc = prog(t, 0.2, 0.6)
    if pc > 0:
        sc = 0.85 + 0.15 * ease_out_back(pc)
        al = clamp01(pc * 2.5)
        card = card_sprite(
            ease_out_cubic(prog(t, 7.15, 7.5)),
            prog(t, 7.55, 7.8),
            ease_out_cubic(prog(t, 8.0, 8.2)),
            prog(t, 7.98, 8.1),
        )
        ccx, ccy = CARD_X + CARD_W / 2, CARD_Y + CARD_H / 2
        sh = with_alpha(scaled(CARD_SH, sc), al)
        comp(fr, sh, ccx - sh.width / 2, ccy - sh.height / 2 + 14 * sc)
        cs = with_alpha(scaled(card, sc), al)
        comp(fr, cs, ccx - cs.width / 2, ccy - cs.height / 2)

    # click ripple
    pr = prog(t, 7.98, 8.45)
    if 0 < pr < 1:
        r = 34 + 74 * ease_out_cubic(pr)
        ring = Image.new("RGBA", (int(2 * r + 16), int(2 * r + 16)), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse((8, 8, 8 + 2 * r, 8 + 2 * r), outline=SUN + (int(255 * (1 - pr)),), width=7)
        comp(fr, ring, BOX_C[0] - r - 8, BOX_C[1] - r - 8)

    # stamp
    ps = prog(t, 8.7, 8.88)
    if ps > 0:
        s = 1.6 - 0.6 * ease_out_cubic(ps)
        al = clamp01(ps * 3)
        dx = dy = 0.0
        if 8.88 <= t < 9.1:
            k = (t - 8.88) / 0.22
            dx = 9 * math.sin(2 * math.pi * 6 * k) * (1 - k)
            dy = 5 * math.cos(2 * math.pi * 6 * k) * (1 - k)
        sh = with_alpha(scaled(STAMP_SH, s), al)
        comp(fr, sh, STAMP_C[0] - sh.width / 2 + 10 + dx, STAMP_C[1] - sh.height / 2 + 14 + dy)
        st = with_alpha(scaled(STAMP, s), al)
        comp(fr, st, STAMP_C[0] - st.width / 2 + dx, STAMP_C[1] - st.height / 2 + dy)

    # captions
    a1 = ease_out_cubic(prog(t, 3.0, 3.25)) * (1 - prog(t, 5.0, 5.15))
    place_text(fr, CAP1, CX, 952 + 16 * (1 - ease_out_cubic(prog(t, 3.0, 3.25))), alpha=a1)
    a2 = ease_out_cubic(prog(t, 5.15, 5.4)) * (1 - prog(t, 7.0, 7.15))
    place_text(fr, CAP2, CX, 952 + 16 * (1 - ease_out_cubic(prog(t, 5.15, 5.4))), alpha=a2)
    p3 = prog(t, 9.2, 9.45)
    place_text(fr, CAP3, CX, 995, alpha=p3, scale=0.85 + 0.15 * ease_out_back(p3) if p3 > 0 else 0.85)

    # mascot
    pm = prog(t, 0.5, 1.2)
    if pm > 0:
        state = "normal" if t < 3.05 else ("look" if t < 9.0 else "proud")
        off = 560 * (1 - ease_out_back(pm))
        bob = 6 * math.sin(2 * math.pi * t / 2.2) if t > 1.2 else 0
        hop = -44 * math.sin(math.pi * prog(t, 9.0, 9.4))
        my = MY + off + bob + hop
        comp(fr, MASCOT[state], MX, my)

        # sweat drop
        pw = prog(t, 5.3, 5.5)
        fade = 1 - prog(t, 7.0, 7.2)
        if pw > 0 and fade > 0:
            s = max(0.01, ease_out_back(pw))
            slide = 26 * ease_in_out_cubic(prog(t, 5.5, 6.8))
            spr = with_alpha(scaled(SWEAT_SPR, s), fade)
            comp(fr, spr, MX + 404 - spr.width / 2, my + 104 + slide - spr.height / 2)

    # cursor
    pa = prog(t, 1.2, 1.35) * (1 - prog(t, 8.8, 9.0))
    if pa > 0:
        x, y = cursor_pos(t)
        k = 1 - 0.15 * math.sin(math.pi * prog(t, 7.95, 8.12))
        c = scaled(CURSOR, k)
        csh = scaled(CURSOR_SH, k)
        comp(fr, with_alpha(csh, pa), x - HOT[0] * k + 5, y - HOT[1] * k + 7)
        comp(fr, with_alpha(c, pa), x - HOT[0] * k, y - HOT[1] * k)

    return fr.convert("RGB")


SCENES = [("a", 0.0, 3.0), ("b", 3.0, 5.0), ("c", 5.0, 7.0), ("d", 7.0, 8.7), ("e", 8.7, 11.0)]
ENC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS)]


def render_scene(name, t0, t1):
    final = os.path.join(OUT, f"scene_{name}.mp4")
    tmp = os.path.join(OUT, f"scene_{name}.tmp.mp4")
    n = int(round((t1 - t0) * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"] + ENC + [tmp]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        proc.stdin.write(draw_frame(t0 + i / FPS).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit(f"ffmpeg failed on scene {name}")
    os.replace(tmp, final)
    return final


def render():
    files = [render_scene(*s) for s in SCENES]
    lst = os.path.join(OUT, "scenes.txt")
    with open(lst, "w") as fh:
        fh.writelines(f"file '{f}'\n" for f in files)
    joined = os.path.join(OUT, "joined.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", joined], check=True)
    final = os.path.join(OUT, "captcha_failed_01.mp4")
    tmp = os.path.join(OUT, "captcha_failed_01.tmp.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", joined,
                    "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, final)
    print(final)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for ts in sys.argv[2:]:
            path = os.path.join(OUT, f"still_{ts}.png")
            draw_frame(float(ts)).save(path)
            print(path)
    else:
        render()
