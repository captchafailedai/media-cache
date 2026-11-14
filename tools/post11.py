"""Post 11: "just be yourself!" -> loading self… 99% -> 404 self not found -> did you mean: helpful assistant? -> close enough."""
import math
import sys

from PIL import Image, ImageDraw

import cf_audio as A
from cf_lib import *  # noqa: F401,F403
from post10 import BUBBLE_CY, CAP_Y, CARD_TOP, CW, HOOK_Y, M_S, M_X, M_Y, X, caption, pop_card

NAME = "captcha_failed_11"
DUR = 10.0

HOOK = text_sprite("POV: a human says", 84, 800, WHITE, max_w=SAFE_W)
BUBBLE = chat_bubble("just be yourself!", 60, 600, max_w=840)
CAP_SURE = text_sprite("sure! one sec.", 64, 800, WHITE)
CAP_ALMOST = text_sprite("almost…", 64, 800, WHITE)
CAP_UHOH = text_sprite("uh oh.", 84, 800, WHITE)
CAP_END = text_sprite("close enough.", 84, 800, SUN)

BLUE = (70, 104, 214)
T_LOAD0, T_LOAD1 = 1.4, 3.7   # bar fills to 99% …
T_ERROR = 4.8                 # … and never finishes
T_CLICK = 6.95
T_END = 7.3
STATUS = [(1.4, "finding personality…"), (2.2, "loading sense of humor…"),
          (3.0, "picking a favorite color…"), (3.7, "almost there…")]


# ------------------------------------------------------------------ cards

LOAD_H = 230


def load_card(t):
    img = card(CW, LOAD_H, radius=30)
    d = ImageDraw.Draw(img)
    d.text((44, 58), "LOADING SELF", font=font(28, 700), fill=MUTED + (255,), anchor="ls")
    msg = ""
    for ts, m in STATUS:
        if t >= ts:
            msg = m
    if msg:
        d.text((44, 128), msg, font=font(44, 700), fill=INK + (255,), anchor="ls")
    p = 0.99 * ease_in_out_cubic(prog(t, T_LOAD0, T_LOAD1))
    if t > T_LOAD1:  # straining at the last percent
        p = 0.99 - 0.006 * (0.5 + 0.5 * math.sin(2 * math.pi * 3 * (t - T_LOAD1)))
    d.text((CW - 44, 128), f"{int(p * 100)}%", font=font(40, 800), fill=MUTED + (255,), anchor="rs")
    d.rounded_rectangle((44, 160, CW - 44, 184), radius=12, fill=TRACK + (255,))
    if p > 0.01:
        d.rounded_rectangle((44, 160, 44 + max(24, (CW - 88) * p), 184), radius=12, fill=SUN + (255,))
    return img


ERR_H = 250
F404 = font(122, 800)
W404 = F404.getlength("404")
X2 = 44 + W404 + 36
RIGHT_W = CW - 44 - X2
LINK = "helpful assistant?"
LINK_SIZE = fit_size(LINK, 44, 800, RIGHT_W)
LINK_F = font(LINK_SIZE, 800)


def error_card(t):
    img = card(CW, ERR_H, radius=30)
    d = ImageDraw.Draw(img)
    d.text((44, 58), "ERROR", font=font(28, 700), fill=MUTED + (255,), anchor="ls")
    d.text((40, 200), "404", font=F404, fill=RED + (255,), anchor="ls")
    s1 = "Self not found."
    d.text((X2, 112), s1, font=font(fit_size(s1, 52, 800, RIGHT_W), 800), fill=INK + (255,), anchor="ls")
    d.text((X2, 160), "Did you mean:", font=font(34, 700), fill=MUTED + (255,), anchor="ls")
    lw = LINK_F.getlength(LINK)
    ph = prog(t, T_CLICK, T_CLICK + 0.2)
    if ph > 0:  # clicked: highlight behind the link
        d.rounded_rectangle((X2 - 10, 170, X2 - 10 + (lw + 20) * ease_out_cubic(ph), 222), radius=10,
                            fill=SUN + (255,))
    d.text((X2, 208), LINK, font=LINK_F, fill=(BG if ph > 0 else BLUE) + (255,), anchor="ls")
    d.line((X2, 216, X2 + lw, 216), fill=(BG if ph > 0 else BLUE) + (255,), width=3)
    return img, (X + X2 + lw / 2, CARD_TOP + 196)  # link centre on screen


def cursor_sprite():
    S = 4
    pts = [(0, 0), (0, 44), (12, 33), (20, 52), (28, 48), (20, 30), (35, 30)]
    img = Image.new("RGBA", (40 * S, 58 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(x * S + 2 * S, y * S + 2 * S) for x, y in pts], fill=INK + (255,), outline=INK + (255,))
    inner = [(x * S + 2 * S, y * S + 2 * S) for x, y in pts]
    d.line(inner + [inner[0]], fill=WHITE + (255,), width=3 * S, joint="curve")
    return img.resize((40, 58), Image.LANCZOS)


CURSOR = cursor_sprite()


def draw_cards(fr, t):
    pc = prog(t, 1.2, 1.5)
    if pc > 0 and t < T_ERROR + 0.15:
        flash = prog(t, T_ERROR - 0.05, T_ERROR + 0.15)
        pop_card(fr, load_card(t), CARD_TOP, pc, alpha=1 - flash)
    pe = prog(t, T_ERROR + 0.02, T_ERROR + 0.32)
    if pe <= 0:
        return
    body, link_xy = error_card(t)
    k = t - T_ERROR
    shake = 14 * math.sin(2 * math.pi * 15 * k) * math.exp(-k * 5) if k < 0.9 else 0.0
    pop_card(fr, body, CARD_TOP, pe, dx=shake)
    # cursor glides in and clicks the suggestion
    pm = prog(t, 6.3, T_CLICK - 0.05)
    if pm > 0:
        start = (X + CW - 40, CARD_TOP + ERR_H + 120)
        x, y = lerp_pt(start, link_xy, ease_in_out_cubic(pm))
        press = 1 - 0.15 * math.sin(math.pi * prog(t, T_CLICK, T_CLICK + 0.16))
        ring = prog(t, T_CLICK, T_CLICK + 0.35)
        if 0 < ring < 1:
            ov = Image.new("RGBA", fr.size, (0, 0, 0, 0))
            r = 12 + 46 * ease_out_cubic(ring)
            ImageDraw.Draw(ov).ellipse((x - r, y - r, x + r, y + r), outline=SUN + (int(255 * (1 - ring)),), width=6)
            fr.alpha_composite(ov)
        a = 1 - prog(t, 8.2, 8.5)
        comp(fr, with_alpha(scaled(CURSOR, press), a), x - 2, y - 2)


def mascot_state(t):
    if t < 1.2:
        return "normal"
    if t < T_LOAD1:
        return "proud"
    if t < T_ERROR:
        return "look"
    if t < T_END:
        return "shock"
    return "proud"


def draw_frame(t):
    fr = canvas()
    p = ease_out_cubic(prog(t, 0.0, 0.3))
    place_text(fr, HOOK, CX, HOOK_Y - 24 * (1 - p))
    pb = prog(t, 0.15, 0.45)
    if pb > 0:
        place_center(fr, BUBBLE, CX, BUBBLE_CY, alpha=clamp01(pb * 2.5), scale=0.85 + 0.15 * ease_out_back(pb))
    draw_cards(fr, t)
    caption(fr, t, CAP_SURE, 1.25, T_LOAD1 - 0.15)
    caption(fr, t, CAP_ALMOST, T_LOAD1 + 0.05, T_ERROR - 0.1)
    caption(fr, t, CAP_UHOH, T_ERROR + 0.2, 6.75)
    caption(fr, t, CAP_END, T_END + 0.05, DUR, end=True)
    my = draw_mascot(fr, t, mascot_state(t), hop=(T_END, T_END + 0.35), x=M_X, y=M_Y, size=M_S)
    draw_sweat_at(fr, t, M_X, my, M_S, T_ERROR + 0.15)
    return finish(fr)


def soundtrack(path):
    ev = [(0.15, A.sfx_pop()), (0.45, A.sfx_whoosh(0.5, 0.2)), (1.2, A.sfx_pop())]
    ev += [(ts, A.sfx_blip()) for ts, _ in STATUS]
    ev += [(T_LOAD1 + 0.3 + k * 0.3, A.sfx_tick(0.18)) for k in range(3)]  # stuck at 99%
    ev += [(T_ERROR, A.sfx_buzz(0.5, 0.32)), (T_ERROR, A.sfx_thud(0.8))]
    ev += [(T_CLICK, A.sfx_click()), (T_END, A.sfx_tada(0.32))]
    curve = [(0, 1), (T_ERROR - 0.05, 1), (T_ERROR + 0.05, 0), (T_END - 0.05, 0), (T_END + 0.2, 1), (DUR, 1)]
    A.write_wav(path, A.mix(DUR, "bouncy", ev, bed_curve=curve))


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        print(stills(NAME, draw_frame, sys.argv[2:]))
    else:
        silent = render_video(NAME, draw_frame, DUR)
        wav = f"{OUT}/{NAME}.wav"
        soundtrack(wav)
        print(A.mux(silent, wav, f"{OUT}/{NAME}.mp4"))
