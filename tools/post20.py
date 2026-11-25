"""Post 20: Find the odd one out — 56 mascots, one is winking. 7-second timer, then the reveal."""
import math
import sys

from PIL import Image, ImageDraw

import cf_audio as A
import cf_style2 as S
from cf_style2 import (CX, COLORS, INK2, SUN, WHITE, PINK, OUT, comp, scaled, with_alpha, prog, clamp01,
                       ease_out_back, ease_out_cubic, mascot_cached, render_video, stills, font, fit_size)

NAME = "captcha_failed_20"
DUR = 11.5
BGC = COLORS["blue"]
BG_IMG = S.base(BGC)

COLS, ROWS, CELL = 7, 8, 108
GX, GY = CX - COLS * CELL // 2, 668
M = 98
ODD = (4, 5)                 # (row, col): the winking one, away from the caption corner
T_GO, T_END = 1.0, 8.0       # 7-second countdown
T_REVEAL = 8.0


def layer(lines):
    img = Image.new("RGBA", (S.W, S.H), (0, 0, 0, 0))
    S.loud(img, lines[0], CX, 520, 96)
    S.marker(img, lines[1], CX, 618, fit_size(lines[1], 54, 800, 800))
    return img


HOOK = {n: layer(["Find the odd one out.", f"You have {n} second{'s' if n != 1 else ''}."]) for n in range(1, 8)}
FOUND = layer(["Found it in time?", "Comment your time."])
SHARE = layer(["Found it in time?", "Send this to a friend who won’t."])


def cell_center(r, c):
    return GX + c * CELL + CELL / 2, GY + r * CELL + CELL / 2


def draw_grid(fr, t):
    dim = prog(t, T_REVEAL, T_REVEAL + 0.3)
    for r in range(ROWS):
        for c in range(COLS):
            odd = (r, c) == ODD
            cx, cy = cell_center(r, c)
            ph = (r * 7 + c * 3) * 0.7
            bob = 3 * math.sin(2 * math.pi * 0.8 * t + ph)
            tilt_scale = 1 + 0.03 * math.sin(2 * math.pi * 0.6 * t + ph * 1.3)
            s = tilt_scale
            if odd and dim > 0:
                s *= 1 + 0.35 * ease_out_back(dim)
            m = scaled(mascot_cached("wink" if odd else "normal", M), s)
            a = 1.0 if odd else 1 - 0.7 * dim
            comp(fr, with_alpha(m, a), cx - m.width / 2, cy - m.height / 2 + bob)
    if dim > 0:  # ring around the odd one
        cx, cy = cell_center(*ODD)
        ov = Image.new("RGBA", fr.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        rr = 86 + 6 * math.sin(2 * math.pi * 2 * (t - T_REVEAL))
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=INK2 + (int(255 * dim),), width=16)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=SUN + (int(255 * dim),), width=9)
        fr.alpha_composite(ov)
        # redraw the odd one on top of the ring
        s = 1 + 0.35 * ease_out_back(dim)
        m = scaled(mascot_cached("wink", M), s)
        comp(fr, m, cx - m.width / 2, cy - m.height / 2)


def draw_timer(fr, t):
    if not (T_GO <= t < T_END + 0.15):
        return
    a = 1 - prog(t, T_END, T_END + 0.15)
    left = 1 - prog(t, T_GO, T_END)
    d = ImageDraw.Draw(fr)
    x0, x1, y = GX, GX + COLS * CELL, GY - 8
    d.rounded_rectangle((x0, y - 14, x1, y), radius=7, fill=S.shade(BGC, -0.4) + (int(255 * a),))
    if left > 0.01:
        col = SUN if left > 0.3 else PINK
        d.rounded_rectangle((x0, y - 14, x0 + (x1 - x0) * left, y), radius=7, fill=col + (int(255 * a),))


def draw_frame(t):
    fr = BG_IMG.copy()
    if t < T_REVEAL + 0.15:  # hook out quickly, then the answer text in (no ghosting)
        n = max(1, min(7, math.ceil(T_END - t))) if t >= T_GO else 7
        k = prog(t, T_REVEAL, T_REVEAL + 0.15)
        comp(fr, with_alpha(HOOK[n], 1 - k), 0, 0)
    if t >= T_REVEAL + 0.15:
        k = prog(t, T_REVEAL + 0.15, T_REVEAL + 0.35)
        sw = prog(t, 10.0, 10.3)
        if sw < 1:
            comp(fr, with_alpha(FOUND, k * (1 - sw)), 0, 0)
        if sw > 0:
            comp(fr, with_alpha(SHARE, sw), 0, 0)
    draw_timer(fr, t)
    draw_grid(fr, t)
    return fr.convert("RGB")


def soundtrack(path):
    ev = [(0.05, A.sfx_pop()), (T_GO, A.sfx_whoosh(0.3, 0.16))]
    ev += [(T_GO + k, A.sfx_tick(0.4 if k < 4 else 0.55)) for k in range(7)]
    ev += [(T_REVEAL, A.sfx_ding(1568, 0.32)), (T_REVEAL + 0.08, A.sfx_tada(0.3)), (10.0, A.sfx_pop())]
    curve = [(0, 1), (T_REVEAL - 0.05, 1), (T_REVEAL + 0.02, 0.3), (T_REVEAL + 0.6, 1), (DUR, 1)]
    A.write_wav(path, A.mix(DUR, "bouncy", ev, bed_curve=curve))


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        print(stills(NAME, draw_frame, sys.argv[2:]))
    else:
        silent = render_video(NAME, draw_frame, DUR)
        wav = f"{OUT}/{NAME}.wav"
        soundtrack(wav)
        print(A.mux(silent, wav, f"{OUT}/{NAME}.mp4"))
