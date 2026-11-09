"""Post 2: "no rush, take your time!" -> done in 0.3 s -> pretends to think."""
import sys

from PIL import Image, ImageDraw

import cf_audio as A
from cf_lib import *  # noqa: F401,F403

NAME = "captcha_failed_02"
DUR = 10.5

HOOK = text_sprite("POV: a human says", 84, 800, WHITE, max_w=SAFE_W)
BUBBLE = chat_bubble("no rush, take your time!", 60, 600, max_w=840)
CAPS = [
    (text_sprite("me, 0.3 seconds later:", 64, 800, WHITE, max_w=SAFE_W), 1.6, 3.45),
    (text_sprite("…wait. was that too fast?", 64, 800, WHITE, max_w=SAFE_W), 3.65, 5.6),
    (text_sprite("let me pretend to think", 64, 800, WHITE, max_w=SAFE_W), 5.8, 8.75),
    (text_sprite("much more believable.", 76, 800, SUN, max_w=SAFE_W), 8.95, 99),
]
CHECK = check_badge(60)
CARD_W, CARD_H = 820, 210
CARD_C = (CX, 740)
CARD_SH = silhouette(card(CARD_W, CARD_H), SHADOW)


def progress(t):
    """(label, percent, done) for the progress card."""
    if t < 2.3:
        return "Thinking…", 0, False
    if t < 2.62:
        return "Thinking…", round(100 * ease_in_out_cubic(prog(t, 2.3, 2.6))), False
    if t < 5.85:
        return "Done.", 100, True
    # fake progress for effect: crawls, stalls, sticks at 99
    keys = [(6.0, 0), (6.6, 23), (7.1, 23), (7.6, 61), (7.9, 61), (8.2, 99), (8.8, 99), (8.85, 100)]
    pct = 0
    for (ta, pa), (tb, pb) in zip(keys, keys[1:]):
        if ta <= t < tb:
            pct = pa + (pb - pa) * ease_in_out_cubic(prog(t, ta, tb))
            break
    if t >= 8.85:
        return "Done. (again)", 100, True
    return "Thinking… (for effect)", round(pct), False


_cards = {}


def progress_card(label, pct, done):
    key = (label, pct, done)
    if key in _cards:
        return _cards[key]
    S = 2
    img = card(CARD_W * S, CARD_H * S, radius=26 * S, border_w=2 * S)
    d = ImageDraw.Draw(img)
    x = 40 * S
    if done:
        img.alpha_composite(check_badge(56 * S), (x, 26 * S))
        x += 76 * S
    d.text((x, 76 * S), label, font=font(48 * S, 700), fill=INK + (255,), anchor="ls")
    d.text(((CARD_W - 40) * S, 76 * S), f"{pct}%", font=font(44 * S, 700), fill=MUTED + (255,), anchor="rs")
    x0, y0, x1, y1 = 40 * S, 118 * S, (CARD_W - 40) * S, 160 * S
    d.rounded_rectangle((x0, y0, x1, y1), radius=21 * S, fill=TRACK + (255,))
    if pct > 0:
        fx = x0 + (x1 - x0) * pct / 100
        d.rounded_rectangle((x0, y0, max(fx, x0 + 42 * S), y1), radius=21 * S,
                            fill=(SUN if done else BG) + (255,))
    out = img.resize((CARD_W, CARD_H), Image.LANCZOS)
    _cards[key] = out
    return out


def mascot_state(t):
    if t < 2.62:
        return "normal"
    if t < 3.6:
        return "proud"
    if t < 4.0:
        return "shock"
    if t < 5.8:
        return "look"
    if t < 8.85:
        return "whistle"
    return "proud"


def draw_frame(t):
    fr = BASE.copy()
    p = ease_out_cubic(prog(t, 0.0, 0.3))
    place_text(fr, HOOK, CX, 300 - 24 * (1 - p))

    pb = prog(t, 0.15, 0.45)
    if pb > 0:
        place_center(fr, BUBBLE, CX, 470, alpha=clamp01(pb * 2.5), scale=0.85 + 0.15 * ease_out_back(pb))

    pc = prog(t, 1.5, 1.8)
    if pc > 0:
        s = 0.85 + 0.15 * ease_out_back(pc)
        a = clamp01(pc * 2.5)
        place_center(fr, CARD_SH, CARD_C[0], CARD_C[1] + 14 * s, alpha=a, scale=s)
        place_center(fr, progress_card(*progress(t)), CARD_C[0], CARD_C[1], alpha=a, scale=s)

    for item, t_in, t_out in CAPS:
        a = fade_window(t, t_in, t_out)
        if a > 0:
            rise = 16 * (1 - ease_out_cubic(prog(t, t_in, t_in + 0.25)))
            place_text(fr, item, CX, 955 + rise, alpha=a)

    my = draw_mascot(fr, t, mascot_state(t), hop=(8.85, 9.25))
    draw_sweat(fr, t, my, 4.05, 5.6)
    return fr.convert("RGB")


def soundtrack(path):
    ev = [(0.15, A.sfx_pop()), (0.45, A.sfx_whoosh(0.5, 0.2)), (1.5, A.sfx_pop()), (1.62, A.sfx_pop() * 0.6),
          (2.3, A.sfx_zip(True)), (2.62, A.sfx_ding()), (3.6, A.sfx_bonk() * 0.7), (3.65, A.sfx_pop() * 0.6),
          (4.05, A.sfx_blip()), (5.8, A.sfx_pop() * 0.6), (8.85, A.sfx_tada()), (8.97, A.sfx_pop() * 0.6)]
    ev += [(6.0 + 0.5 * i, A.sfx_tick(0.3)) for i in range(6)]
    curve = [(0, 1), (5.9, 1), (6.1, 0.55), (8.8, 0.55), (8.9, 1), (DUR, 1)]
    A.write_wav(path, A.mix(DUR, "bouncy", ev, bed_curve=curve))


if __name__ == "__main__":
    if sys.argv[1:2] == ["stills"]:
        print(stills(NAME, draw_frame, sys.argv[2:]))
    else:
        silent = render_video(NAME, draw_frame, DUR)
        wav = f"{OUT}/{NAME}.wav"
        soundtrack(wav)
        print(A.mux(silent, wav, f"{OUT}/{NAME}.mp4"))
