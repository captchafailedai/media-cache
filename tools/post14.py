"""Post 14 (new look): "One of us broke the blue vase." — whodunit video with a hidden clue on the culprit."""
import math
import sys

from PIL import Image, ImageDraw

import cf_audio as A
import cf_style2 as S
from cf_style2 import (CX, COLORS, INK2, SUN, WHITE, OUT, canvas, comp, place_center, scaled, with_alpha,
                       prog, clamp01, ease_out_back, ease_out_cubic, ease_in_out_cubic, mascot_cached,
                       render_video, stills, font, fit_size, text_sprite, place_text)

NAME = "captcha_failed_14"
DUR = 11.0
BGC = COLORS["purple"]
BG_IMG = S.base(BGC)

CELL, GAP = 236, 16
GRID = 3 * CELL + 2 * GAP
GX, GY = CX - GRID // 2, 830
M_SIZE = 196
CULPRIT = 8
SUSPECTS = {1: "flat", 2: "whistle", 3: "look", 4: "side", 5: "shock", 6: "laugh", 7: "lookR", 8: "normal", 9: "love"}
VASE = (126, 192, 255)
T_TIMER0, T_TIMER1 = 5.0, 8.0
T_REVEAL = 8.0


def cell_xy(n):
    r, c = divmod(n - 1, 3)
    return GX + c * (CELL + GAP), GY + r * (CELL + GAP)


CARD = S.chunky(CELL - 10, CELL - 12, radius=26, border=6, off=(8, 10))


def badge(n, fill=INK2, ink=WHITE):
    S2 = 4
    d = 58
    img = Image.new("RGBA", (d * S2, d * S2), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    dr.ellipse((0, 0, d * S2 - 1, d * S2 - 1), fill=fill + (255,))
    dr.text((d * S2 / 2, d * S2 / 2 + 2 * S2), str(n), font=font(34 * S2, 800), fill=ink + (255,), anchor="mm")
    return img.resize((d, d), Image.LANCZOS)


BADGES = {n: badge(n) for n in range(1, 10)}
BADGE_HOT = badge(CULPRIT, fill=SUN, ink=INK2)


def shard_sprite(scale=1.0):
    S2 = 4
    w, h = int(40 * scale), int(34 * scale)
    img = Image.new("RGBA", (w * S2, h * S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(0.08, 0.95), (0.42, 0.05), (0.95, 0.62)]
    poly = [(x * w * S2, y * h * S2) for x, y in pts]
    d.polygon(poly, fill=VASE + (255,), outline=INK2 + (255,))
    d.line([(0.3 * w * S2, 0.7 * h * S2), (0.62 * w * S2, 0.48 * h * S2)], fill=(255, 255, 255, 255), width=3 * S2)
    d.line(poly + [poly[0]], fill=INK2 + (255,), width=2 * S2)
    return img.resize((w, h), Image.LANCZOS)


SHARD = shard_sprite()


def mascot_state(n, t):
    st = SUSPECTS[n]
    if n == 3:  # nervous glancing
        st = "look" if int(t / 0.6) % 2 == 0 else "lookR"
    if n == CULPRIT and t >= T_REVEAL + 0.5:
        st = "whistle"  # caught
    return st


def draw_grid(fr, t):
    for n in range(1, 10):
        pc = 1.0  # everything is in place on frame 1 (it doubles as the cover) …
        x, y = cell_xy(n)
        s = 1 + 0.07 * math.sin(math.pi * prog(t, 0.04 * (n - 1), 0.3 + 0.04 * (n - 1)))  # … with a quick ripple
        reveal = prog(t, T_REVEAL, T_REVEAL + 0.3)
        hot = n == CULPRIT
        if hot and reveal > 0:
            s *= 1 + 0.12 * ease_out_back(reveal)
        cx, cy = x + CELL / 2, y + CELL / 2
        card = CARD
        if hot and reveal > 0:
            glow = S.chunky(CELL - 10, CELL - 12, fill=SUN, radius=26, border=6, off=(8, 10))
            card = glow
        sc = scaled(card, s)
        comp(fr, with_alpha(sc, clamp01(pc * 2)), cx - sc.width / 2 + 4 * s, cy - sc.height / 2 + 5 * s)
        bob = 5 * math.sin(2 * math.pi * 0.9 * t + n * 1.3)
        if n == 2:
            bob += 3 * math.sin(2 * math.pi * 6 * t)  # jittery whistler
        m = mascot_cached(mascot_state(n, t), M_SIZE)
        ms = scaled(m, s)
        mx, my = cx - ms.width / 2, cy - ms.height / 2 + 8 * s + bob
        comp(fr, with_alpha(ms, clamp01(pc * 2)), mx, my)
        if n == 2 and t > 1.0:  # sweat on the whistler
            sp = scaled(S.SWEAT_SPR, 0.45 * s)
            comp(fr, sp, mx + ms.width * 0.78 - sp.width / 2, my + ms.height * 0.22 + 6 * math.sin(t * 3))
        if hot:  # the clue: a shard of blue vase on its head
            pulse = 1 + 0.35 * math.sin(math.pi * prog(t, T_REVEAL + 0.6, T_REVEAL + 1.0)) if t > T_REVEAL else 1
            sh = scaled(SHARD, s * pulse)
            comp(fr, sh, mx + ms.width * 0.6 - sh.width / 2, my + ms.height * 0.14 - sh.height / 2)
        b = BADGE_HOT if hot and reveal > 0 else BADGES[n]
        place_center(fr, b, x + 18, y + 18, alpha=clamp01(pc * 2), scale=s)
    # dim everyone else at the reveal
    dim = prog(t, T_REVEAL, T_REVEAL + 0.3)
    if dim > 0:
        ov = Image.new("RGBA", fr.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for n in range(1, 10):
            if n == CULPRIT:
                continue
            x, y = cell_xy(n)
            d.rounded_rectangle((x - 6, y - 6, x + CELL + 4, y + CELL + 4), radius=28, fill=BGC + (int(185 * dim),))
        fr.alpha_composite(ov)


def hook_layer():
    img = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
    S.loud(img, "One of us broke", CX, 560, 104)
    S.marker(img, "the blue vase.", CX, 690, 100, fill=VASE)
    return img


def sub_layer():
    img = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
    s = "Who did it? Comment the number."
    ImageDraw.Draw(img).text((CX, 790), s, font=font(fit_size(s, 46, 700), 700), fill=WHITE + (255,), anchor="ms")
    return img


def reveal_layer():
    img = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
    S.loud(img, "It was #8.", CX, 600, 120)
    s = "Too calm. And check its head."
    S.marker(img, s, CX, 740, fit_size(s, 52, 800, 820), tilt=-1.5)
    return img


HOOK = hook_layer()
SUB = sub_layer()
REVEAL = reveal_layer()


def draw_timer(fr, t):
    p = prog(t, T_TIMER0, T_TIMER0 + 0.25)
    if p <= 0 or t >= T_REVEAL:
        return
    a = p * (1 - prog(t, T_REVEAL - 0.15, T_REVEAL))
    d = ImageDraw.Draw(fr)
    left = 1 - prog(t, T_TIMER0, T_TIMER1)
    x0, x1, y = CX - 300, CX + 300, 772
    label = f"LOCK IN YOUR GUESS · {max(1, math.ceil(T_TIMER1 - t))}"
    d.text((CX, y - 12), label, font=font(34, 800), fill=WHITE + (int(255 * a),), anchor="ms")
    d.rounded_rectangle((x0, y + 4, x1, y + 26), radius=11, fill=S.shade(BGC, -0.35) + (int(255 * a),))
    if left > 0.01:
        d.rounded_rectangle((x0, y + 4, x0 + (x1 - x0) * left, y + 26), radius=11, fill=SUN + (int(255 * a),))


def draw_arrow(fr, t):
    p = prog(t, T_REVEAL + 0.6, T_REVEAL + 0.85)
    if p <= 0:
        return
    x, y = cell_xy(CULPRIT)
    tip = (x + CELL * 0.62, y + 20)
    start = (tip[0] + 150, tip[1] - 120)
    end = (tip[0] + 26, tip[1] - 14)
    cur = (start[0] + (end[0] - start[0]) * ease_out_cubic(p), start[1] + (end[1] - start[1]) * ease_out_cubic(p))
    d = ImageDraw.Draw(fr)
    d.line((start, cur), fill=INK2 + (255,), width=18)
    d.line((start, cur), fill=SUN + (255,), width=10)
    if p > 0.9:
        ang = math.atan2(end[1] - start[1], end[0] - start[0])
        head = [(cur[0], cur[1]),
                (cur[0] - 34 * math.cos(ang - 0.5), cur[1] - 34 * math.sin(ang - 0.5)),
                (cur[0] - 34 * math.cos(ang + 0.5), cur[1] - 34 * math.sin(ang + 0.5))]
        d.polygon(head, fill=SUN + (255,), outline=INK2 + (255,))


def draw_frame(t):
    fr = BG_IMG.copy()
    out = prog(t, T_REVEAL, T_REVEAL + 0.12)
    if out < 1:
        comp(fr, with_alpha(HOOK, 1 - out), 0, 0)
        sub_a = (1 - prog(t, T_TIMER0 - 0.1, T_TIMER0 + 0.1)) * (1 - out)
        if sub_a > 0:
            comp(fr, with_alpha(SUB, sub_a), 0, 0)
    draw_timer(fr, t)
    draw_grid(fr, t)
    swap = prog(t, T_REVEAL + 0.1, T_REVEAL + 0.35)
    if swap > 0:
        sc = 0.9 + 0.1 * ease_out_back(swap)
        lay = scaled(REVEAL, sc)
        comp(fr, with_alpha(lay, swap), CX - CX * sc, 650 - 650 * sc)  # scale about (CX, 650)
    draw_arrow(fr, t)
    return fr.convert("RGB")


def soundtrack(path):
    ev = [(0.12 + 0.05 * k, A.sfx_pop()) for k in range(9)]
    ev += [(T_TIMER0, A.sfx_whoosh(0.35, 0.18))] + [(T_TIMER0 + k, A.sfx_tick(0.35)) for k in range(3)]
    ev += [(T_REVEAL, A.sfx_thud(0.9)), (T_REVEAL + 0.25, A.sfx_thud(0.9)), (T_REVEAL + 0.6, A.sfx_ding(1568, 0.3)),
           (T_REVEAL + 0.55, A.sfx_whistle(0.18))]
    curve = [(0, 1), (T_REVEAL - 0.05, 1), (T_REVEAL + 0.02, 0), (T_REVEAL + 1.9, 0), (T_REVEAL + 2.2, 0.8), (DUR, 0.8)]
    A.write_wav(path, A.mix(DUR, "sneaky", ev, bed_curve=curve))


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        print(stills(NAME, draw_frame, sys.argv[2:]))
    else:
        silent = render_video(NAME, draw_frame, DUR)
        wav = f"{OUT}/{NAME}.wav"
        soundtrack(wav)
        print(A.mux(silent, wav, f"{OUT}/{NAME}.mp4"))
